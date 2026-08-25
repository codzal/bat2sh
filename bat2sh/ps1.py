"""Batch -> PowerShell translator (structured, AST-based).

Covers the same statement grammar as the bash backend: variables, control
flow (if/else, all `for` flavors), subroutines as functions, redirection,
pipes and a broad command mapping. Output targets PowerShell 7+.
"""
import re

from .parser import Parser

# ---------------------------------------------------------------- helpers

_WIN_ENV = {
    'TEMP': '$env:TMPDIR', 'TMP': '$env:TMPDIR',
    'USERPROFILE': '$HOME', 'HOMEPATH': '$HOME',
    'APPDATA': '$env:APPDATA', 'LOCALAPPDATA': '$env:LOCALAPPDATA',
    'PROGRAMFILES': '$env:ProgramFiles', 'PROGRAMDATA': '$env:ProgramData',
    'SYSTEMROOT': '$env:SystemRoot', 'WINDIR': '$env:SystemRoot',
    'COMPUTERNAME': '$env:COMPUTERNAME',
}


def _ps_inner(name):
    if name.upper() in _WIN_ENV:
        return _WIN_ENV[name.upper()]
    if name.isupper():
        return 'env:%s' % name
    return name.replace('.', '_').lower()


def _ps_name(name):
    return '${' + _ps_inner(name) + '}'


def _ps_value(text, arith=False, loop_var=None):
    if arith:
        # in set /a a doubled % is the modulo operator; only the ACTIVE
        # for-loop letter is a variable reference
        if loop_var:
            text = re.sub(re.escape('%%' + loop_var) + r'\b',
                          '$%s' % loop_var, text)
            text = re.sub(r'%%+(?![%w])', '%', text)
        else:
            text = re.sub(r'%%+', '%', text)
        text = re.sub(r'%(?!%)((?:[1-9]))',
                      lambda m: '$($args[%d])' % (int(m.group(1)) - 1), text)
        return text
    """%VAR% / !VAR! / %1 / %%a -> PowerShell variable syntax."""
    text = re.sub(r'%%([A-Za-z])\b', r'$\1', text)          # loop variables
    text = re.sub(r'[!%]([A-Za-z_][\w.]*)[!%]',
                  lambda m: '${' + _ps_inner(m.group(1)) + '}', text)
    text = re.sub(r'%(?!%)([A-Za-z_]\w*)',
                  lambda m: '${' + _ps_inner(m.group(1)) + '}', text)
    text = re.sub(r'%(?!%)([1-9])',
                  lambda m: '$($args[%d])' % (int(m.group(1)) - 1), text)
    return text.replace('%%', '%')


def _q(text):
    """Quote a literal for double-quoted PS string, keeping $ alive."""
    return '"%s"' % text.replace('"', '`"')


def _split_args(s):
    out, cur, q = [], '', None
    for ch in s:
        if q:
            cur += ch
            if ch == q:
                q = None
        elif ch in '"\'':
            q = ch
            cur += ch
        elif ch.isspace():
            if cur:
                out.append(cur)
                cur = ''
        else:
            cur += ch
    if cur:
        out.append(cur)
    return out


_CMD_MAP = {
    'dir':      'Get-ChildItem',
    'md':       'New-Item -ItemType Directory -Force -Path',
    'mkdir':    'New-Item -ItemType Directory -Force -Path',
    'rd':       'Remove-Item -Recurse -Force',
    'rmdir':    'Remove-Item -Recurse -Force',
    'del':      'Remove-Item -Force',
    'erase':    'Remove-Item -Force',
    'copy':     'Copy-Item',
    'xcopy':    'Copy-Item -Recurse',
    'robocopy': 'Copy-Item -Recurse',
    'move':     'Move-Item',
    'ren':      'Rename-Item',
    'rename':   'Rename-Item',
    'type':     'Get-Content',
    'cls':      'Clear-Host',
    'cd':       'Set-Location',
    'chdir':    'Set-Location',
    'pushd':    'Push-Location',
    'popd':     'Pop-Location',
    'where':    'Get-Command',
    'tasklist': 'Get-Process',
    'hostname': 'hostname',
    'whoami':   'whoami',
    'date':     'Get-Date',
    'tree':     'Get-ChildItem -Recurse | Select-Object FullName',
}


REG_HELPERS_PS = "\n# --- bat2sh registry emulation (JSON store; native registry when present)\n$script:BatRegStore = if ($env:BAT2SH_REG) { $env:BAT2SH_REG } else {\n    Join-Path $HOME '.config/bat2sh/registry.json' }\nfunction reg_load {\n    if (Test-Path $script:BatRegStore) {\n        Get-Content $script:BatRegStore -Raw |\n            ConvertFrom-Json -AsHashtable\n    } else { @{} }\n}\nfunction reg_save($d) {\n    $dir = Split-Path $script:BatRegStore\n    if ($dir -and -not (Test-Path $dir)) {\n        New-Item -ItemType Directory -Force -Path $dir | Out-Null\n    }\n    $d | ConvertTo-Json -Depth 5 | Set-Content $script:BatRegStore\n}\nfunction reg_add($k,$n,$v){\n    if ($IsWindows -and (Get-Command reg.exe -ErrorAction SilentlyContinue)) {\n        reg.exe add $k /v $n /d $v /f | Out-Null; return }\n    $d = reg_load\n    if (-not $d.ContainsKey($k)) { $d[$k] = @{} }\n    $d[$k][$n] = $v\n    reg_save $d\n}\nfunction reg_query($k,$n){\n    if ($IsWindows -and (Get-Command reg.exe -ErrorAction SilentlyContinue)) {\n        reg.exe query $k /v $n; return }\n    $d = reg_load\n    if (-not $d.ContainsKey($k)) { Write-Error 'key not found'; return }\n    if (-not $d[$k].ContainsKey($n)) { Write-Error 'value not found'; return }\n    $d[$k][$n]\n}\nfunction reg_del($k,$n){\n    if ($IsWindows -and (Get-Command reg.exe -ErrorAction SilentlyContinue)) {\n        reg.exe delete $k /v $n /f | Out-Null; return }\n    $d = reg_load\n    if ($d.ContainsKey($k) -and $d[$k].ContainsKey($n)) {\n        $d[$k].Remove($n) | Out-Null\n        reg_save $d\n    }\n}\n"




class PSG:
    def __init__(self):
        self.label_map = {}
        self.func_names = {}
        self.stats = {'stmts': 0, 'fallback': 0}
        self.loop_var = None
        self._need_reg = False
        self.lines = []

    # ---------------- small emitters ----------------
    def w(self, indent, text):
        self.lines.append('    ' * indent + text if text else '')

    def warn(self, indent, raw):
        self.stats['fallback'] += 1
        self.w(indent, '# BAT2SH WARNING (ps1): no translation for: %s' % raw)

    # ---------------- expressions ----------------
    def expr(self, text, arith=False):
        t = _ps_value(text, arith=arith,
                      loop_var=getattr(self, 'loop_var', None))
        # set /a style arithmetic is native in parens; keep as-is
        t = re.sub(r'\bEQU\b', '-eq', t, flags=re.I)
        t = re.sub(r'\bNEQ\b', '-ne', t, flags=re.I)
        t = re.sub(r'\bLSS\b', '-lt', t, flags=re.I)
        t = re.sub(r'\bLEQ\b', '-le', t, flags=re.I)
        t = re.sub(r'\bGTR\b', '-gt', t, flags=re.I)
        t = re.sub(r'\bGEQ\b', '-ge', t, flags=re.I)

        def _pref(m):
            name = m.group(0)
            return ('${env:%s}' % name.upper()) if name.isupper() \
                else '${%s}' % name.lower()

        t = re.sub(r'(?<![\w$.{:])([A-Za-z_]\w*)', _pref, t)
        return t

    # ---------------- commands ----------------
    def cmd(self, seg, ind):
        st = seg.strip()
        low = st.lower()
        if low.startswith('@'):
            st = st[1:].lstrip()
            low = st.lower()
        if not st:
            return
        if low.startswith(('rem ', '::')):
            self.w(ind, '# ' + st.split(' ', 1)[1])
            return
        m = re.match(r'(\S+)\s*(.*)$', st, re.S)
        cmd, args = m.group(1).lower(), m.group(2).strip()
        self.stats['stmts'] += 1

        if cmd == 'echo':
            body = args
            if low.strip() == 'echo off' or body.lower() == 'off':
                return
            if body == '.' or body == '':
                self.w(ind, 'Write-Output ""')
            else:
                self.w(ind, 'Write-Output %s' % _q(_ps_value(body)))
            return
        if cmd == 'set':
            self.cmd_set(args, ind)
            return
        if cmd == 'pause':
            self.w(ind, 'Read-Host "Press any key to continue . . ." '
                        '| Out-Null')
            return
        if cmd in ('exit',):
            mm = re.match(r'/b\s*(\d+)?$', args, re.I)
            if mm:
                code = int(mm.group(1)) if mm.group(1) else '$LASTEXITCODE'
                self.w(ind, 'exit %s' % code)
            else:
                self.w(ind, 'exit %s' % (args or '0'))
            return
        if cmd in ('setlocal', 'endlocal'):
            self.w(ind, '# %s (scoping no-op)' % cmd)
            return
        if cmd == 'color':
            self.warn(ind, st)
            return
        if cmd == 'title':
            self.w(ind, '$Host.UI.RawUI.WindowTitle = %s' % _q(_ps_value(args)))
            return

        # --- control-flow keywords reaching here are parse leftovers
        if cmd in ('goto', 'call') and args.lower().startswith(':'):
            self.warn(ind, st)
            return

        if cmd == 'sc':
            return self.cmd_sc(args, ind)
        if cmd == 'net':
            return self.cmd_net(args, ind)
        if cmd == 'reg':
            self._need_reg = True
            return self.cmd_reg(args, ind)
        if cmd == 'wmic':
            self.warn(ind, st + ' (CIM/WMI modules are Windows-only)')
            return

        mapped = _CMD_MAP.get(cmd)
        if mapped:
            argv = _ps_value(args)
            redir = ''
            mm = re.search(r'>>\s*(\S+)\s*$', argv)
            if mm:
                argv = argv[:mm.start()].strip()
                redir = ' | Add-Content %s' % _q(mm.group(1))
            else:
                mm = re.search(r'>\s*nul\s*$', argv, re.I)
                if mm:
                    argv = argv[:mm.start()].strip()
                    redir = ' | Out-Null'
                else:
                    mm = re.search(r'>\s*(\S+)\s*$', argv)
                    if mm:
                        argv = argv[:mm.start()].strip()
                        redir = ' | Set-Content %s' % _q(mm.group(1))
            self.w(ind, '%s %s%s' % (mapped, argv, redir))
            return

        # unknown: assume it exists on the Windows host running pwsh
        self.w(ind, _ps_value(st) + '  # native invocation')

    _SVC_GUARD = (
        '$svcCmd = Get-Command -Name "{verb}-Service" '
        '-ErrorAction SilentlyContinue\n'
        'if ($svcCmd) {{ {ps} }}\n'
        'elseif (Get-Command systemctl -ErrorAction SilentlyContinue) {{ '
        '{sh} }}\n'
        'else {{ Write-Warning "service management not available: {name}" }}')

    def cmd_sc(self, args, ind):
        t = _split_args(_ps_value(args))
        if len(t) < 2:
            self.warn(ind, 'sc ' + args)
            return
        verb_map = {'start': ('Start-Service', 'start'),
                    'stop': ('Stop-Service', 'stop'),
                    'query': ('Get-Service', 'status')}
        svc = t[1].lower()
        sub = t[0].lower()
        if sub == 'config':
            mm = re.search(r'start=\s*(\w+)', ' '.join(t[2:]), re.I)
            mode = (mm.group(1) if mm else '').lower()
            act = {'auto': 'enable', 'delayed-auto': 'enable',
                   'demand': 'disable'}.get(mode)
            if act:
                self.w(ind, 'if (Get-Command systemctl '
                            '-ErrorAction SilentlyContinue) { '
                            'systemctl %s %s } else { Write-Warning '
                            '"sc config not available: %s" }'
                       % (act, svc, svc))
            else:
                self.warn(ind, args)
            return
        if sub in verb_map:
            ps_verb, sys_action = verb_map[sub]
            block = self._SVC_GUARD.format(
                verb=ps_verb.split('-')[0], ps='%s -Name %s'
                % (ps_verb, _q(svc)), sh='systemctl %s %s' % (sys_action,
                                                              svc),
                name=svc)
            for ln in block.splitlines():
                self.w(ind, ln)
            return
        self.warn(ind, args)

    def cmd_net(self, args, ind):
        t = _split_args(_ps_value(args))
        if len(t) >= 2 and t[0].lower() in ('start', 'stop'):
            self.cmd_sc('%s %s' % (t[0], t[1]), ind)
            return
        if len(t) >= 1 and t[0].lower() == 'user':
            self.w(ind, 'if (Get-Command Get-LocalUser '
                        '-ErrorAction SilentlyContinue) { '
                        'Get-LocalUser | Format-Table Name,Enabled } '
                        'elseif (Test-Path /etc/passwd) { '
                        'Get-Content /etc/passwd | ForEach-Object '
                        '{ ($_ -split ":")[0] } }')
            return
        self.warn(ind, 'net ' + args)

    def cmd_reg(self, args, ind):
        self._need_reg = True
        t = _split_args(args)
        if len(t) < 2:
            self.warn(ind, 'reg ' + args)
            return
        op = t[0].lower()
        key = t[1].replace(chr(92), '/')
        name, val = '(Default)', ''
        rest, i = t[2:], 0
        while i < len(rest):
            k = rest[i].lower()
            if k == '/v' and i + 1 < len(rest):
                name = rest[i + 1]; i += 2
            elif k == '/ve':
                name = '(Default)'; i += 1
            elif k == '/d' and i + 1 < len(rest):
                val = rest[i + 1]; i += 2
            else:
                i += 1
        call = {('add',): 'reg_add',
                ('query',): 'reg_query',
                ('delete',): 'reg_del'}
        fn = None
        for verbs, fname in call.items():
            if op.startswith(verbs[0][:5]):
                fn = fname
        if not fn:
            self.warn(ind, 'reg ' + op)
            return
        argv = "'%s','%s'" % (key.replace("'", "''"),
                              name.replace("'", "''"))
        if fn == 'reg_add':
            argv += ",'%s'" % val.replace("'", "''")
        self.w(ind, '%s %s' % (fn, argv))

    def cmd_set(self, args, ind):
        mm = re.match(r'/p\s+(\w+)\s*=\s*(.*)$', args, re.I)
        if mm:
            var, prompt = mm.groups()
            self.w(ind, '$%s = Read-Host %s' % (var.lower(),
                                                _q(_ps_value(prompt))))
            return
        mm = re.match(r'/a\s+(.+)$', args, re.I)
        if mm:
            body = mm.group(1)
            assignments = re.findall(
                r'([A-Za-z_]\w*)\s*=\s*([^,]+?)(?=\s*,|'
                r'\s+[A-Za-z_]\w*\s*=|$)', body)
            if not assignments:
                self.w(ind, '$null = (%s)' % self.expr(body))
                return
            for name, rhs in assignments:
                tgt = ('$env:' + name) if name.isupper() \
                    else '$' + name.lower()
                self.w(ind, '%s = (%s)' % (tgt, self.expr(rhs.strip(), arith=True)))
            return
        mm = re.match(r'"?([A-Za-z_][\w.]*)"?=(.*)$', args, re.S)
        if mm:
            name, val = mm.groups()
            tgt = ('$env:' + name) if name.isupper() \
                else '$' + name.replace('.', '_').lower()
            val = val.strip()
            if val == '':
                self.w(ind, '%s = $null' % tgt)
            else:
                self.w(ind, '%s = %s' % (tgt, _q(_ps_value(val.strip('"')))))
            return
        self.warn(ind, 'set ' + args)

    # ---------------- structured statements ----------------
    def emit_node(self, node, ind=0):
        t = node[0]
        if t == 'comment':
            self.w(ind, '# ' + node[1] if node[1] else '')
        elif t == 'label':
            pass
        elif t == 'simple':
            parts = re.split(r'&&|\|\||&|\|', node[1])
            ops = re.findall(r'&&|\|\||&|\|', node[1])
            buf = parts[0]
            self.cmd(buf, ind)
            for op, tail in zip(ops, parts[1:]):
                if op.strip() == '&':
                    self.cmd(tail, ind)
                elif op == '&&':
                    self.w(ind, 'if ($LASTEXITCODE -eq 0) {')
                    self.cmd(tail, ind + 1)
                    self.w(ind, '}')
                elif op == '||':
                    self.w(ind, 'if ($LASTEXITCODE -ne 0) {')
                    self.cmd(tail, ind + 1)
                    self.w(ind, '}')
                else:
                    self.cmd(buf and tail or tail, ind)
        elif t == 'if':
            d = node[1]
            self.emit_if(d, ind)
        elif t == 'for':
            self.emit_for(node[1], ind)
        elif t == 'block':
            for n in node[1]:
                self.emit_node(n, ind)
        elif t in ('goto', 'goto_eof'):
            self.warn(ind, node[0] + ' ' + str(node[1] if len(node) > 1
                                              else 'eof'))
        elif t == 'call_sub':
            sub = node[1].lower()
            fname = self.func_names.get(sub.upper())
            if fname:
                args = _ps_value(node[2]).strip()
                self.w(ind, '%s %s' % (fname, args))
            else:
                self.warn(ind, 'call :' + node[1])
        elif t == 'call_ext':
            out = []
            saved = self.lines
            self.lines = []
            self.cmd(node[1], 0)
            out = self.lines
            self.lines = saved
            for ln in out:
                self.w(ind, ln)
        else:
            self.warn(ind, repr(node)[:60])

    def emit_if(self, d, ind=0):
        neg = d['neg']
        ctype, cond = d['ctype'], d['cond']

        def line(test):
            if neg:
                test = '(-not (%s))' % test
            self.w(ind, 'if (%s) {' % test)

        close = lambda: self.w(ind, '}')
        if ctype == 'exist':
            p = _ps_value(cond if isinstance(cond, str) else cond[0])
            line('Test-Path %s' % _q(p.strip('"')))
        elif ctype == 'errorlevel':
            line('$LASTEXITCODE -ge %d' % cond)
        elif ctype == 'defined':
            nm = _ps_value(cond).lstrip('$')
            line("Get-Variable -Name '%s' -ErrorAction SilentlyContinue"
                 % nm.replace('env:', ''))
        elif ctype == 'numcompare':
            opmap = {'equ': '-eq', 'neq': '-ne', 'lss': '-lt',
                     'leq': '-le', 'gtr': '-gt', 'geq': '-ge'}
            left, op, right = cond
            test = '%s %s %s' % (self.expr(left), opmap[op],
                                 self.expr(right))
            line(test)
        elif ctype == 'compare':
            left, right = cond
            line('%s -eq %s' % (_q(_ps_value(left)), _q(_ps_value(right))))
        else:
            self.w(ind, 'if ($false) {')
        for n in d['body']:
            self.emit_node(n, ind + 1)
        close()
        if d['elseb']:
            self.w(ind, 'else {')
            for n in d['elseb']:
                self.emit_node(n, ind + 1)
            close()

    def emit_for(self, d, ind=0):
        var = d['var'].lower()
        flags, inner, opts = d['flags'], d['inner'], d.get('opts', '')
        if 'l' in flags:
            nums = [self.expr(x) for x in inner.strip('()').split(',')]
            if len(nums) == 3:
                start, step, stop = nums
                cmpn = '-le' if not step.startswith('-') else '-ge'
                self.w(ind, 'for ($%s = %s; $%s %s %s; $%s += %s) {'
                       % (var, start, var, cmpn, stop, var, step))
                self.body(d['body'], ind + 1, var)
                self.w(ind, '}')
            else:
                self.warn(ind, 'for /l ' + inner)
            return
        if 'r' in flags:
            root = _ps_value(d.get('base_dir', '') or '.')
            pats = [p.strip('"\'') for p in
                    _ps_value(inner.strip('()')).split()]
            inc = ', '.join(_q(p) for p in pats)
            self.w(ind, 'Get-ChildItem -LiteralPath %s -Recurse -File '
                        '-Include %s | ForEach-Object {' % (
                            _q(root.strip('"')), inc))
            self.w(ind + 1, '$%s = $_.FullName' % var)
            self.body(d['body'], ind + 1, var)
            self.w(ind, '}')
            return
        if 'f' in flags:
            src = inner.strip()
            mm = re.match(r'"(.*)"', src)
            delim = ''
            dm = re.search(r'delims=("?)((?:"\1)|[^"\s]*)\1', opts or '',
                           re.I)
            if dm and dm.group(2):
                delim = dm.group(2)
            if mm:                                     # command source
                cmdtxt = _ps_value(mm.group(1))
                self.w(ind, '%s | ForEach-Object {' % cmdtxt)
            else:
                path = _ps_value(src.strip('"\''))
                self.w(ind, 'Get-Content %s | ForEach-Object {' %
                       _q(path.strip('"')))
            split = ("$parts = $_ -split '%s'" % re.escape(delim)) if delim \
                else "$parts = @($_)"
            self.w(ind + 1, split)
            toks = re.search(r'tokens=([\d,*]+)', opts or '', re.I)
            idx = 0
            if toks:
                spec = toks.group(1)
                letters = []
                base = ord(var)
                for el in spec.split(','):
                    if el == '*':
                        letters.append((1, True))
                    elif el.endswith('*'):
                        letters.append((int(el[:-1]), True))
                    else:
                        letters.append((int(el), False))
                for k, (tok, star) in enumerate(letters):
                    letter = chr(base + k)
                    if star:
                        self.w(ind + 1,
                               '$%s = ($parts[%d..($parts.Count-1)] '
                               '-join \'%s\')'
                               % (letter, tok - 1, delim or ' '))
                    else:
                        self.w(ind + 1,
                               '$%s = $parts[%d]' % (letter, tok - 1))
                    idx += 1
            else:
                self.w(ind + 1, '$%s = $_' % var)
            self.body(d['body'], ind + 1, var)
            self.w(ind, '}')
            return
        items = [i.strip('"\'') for i in
                 _ps_value(inner.strip('()')).split()]
        self.w(ind, 'foreach ($%s in %s) {' % (
            var, ', '.join(_q(i) for i in items)))
        self.body(d['body'], ind + 1, var)
        self.w(ind, '}')

    def body(self, nodes, ind, loop_var=None):
        saved = self.loop_var
        self.loop_var = loop_var
        for n in nodes:
            self.emit_node(n, ind)
        self.loop_var = saved


def convert(text):
    """batch text -> (ps1 script, warning count)."""
    g = PSG()
    text = _re.sub(r'\^\r?\n', '', text)
    nodes = Parser(text).parse_program()

    indexed = list(enumerate(nodes))

    def walk(ns):
        for n in ns:
            yield n
            if n[0] == 'if':
                yield from walk(n[1]['body'])
                if n[1]['elseb']:
                    yield from walk(n[1]['elseb'])
            elif n[0] == 'for':
                yield from walk(n[1]['body'])
            elif n[0] == 'block':
                yield from walk(n[1])

    all_nodes = list(walk(nodes))
    called = {n[1].upper() for n in all_nodes
              if n[0] == 'call_sub'}
    label_pos = [(i, n[1].upper()) for i, n in indexed if n[0] == 'label']
    g.label_map = dict(label_pos)
    for _i, name in label_pos:
        if name in called:
            g.func_names[name] = 'sub_' + re.sub(r'\W', '_', name).lower()

    head = ['#requires -Version 7',
            '# Converted from a Windows batch file by bat2sh (--target=ps1)',
            '']
    for pos, (li, lname) in enumerate(label_pos):
        if lname not in g.func_names:
            continue
        start = li + 1
        end = label_pos[pos + 1][0] if pos + 1 < len(label_pos) else len(nodes)
        g.lines = []
        for j in range(start, end):
            n = nodes[j]
            if n[0] in ('label', 'goto', 'goto_eof'):
                continue
            g.emit_node(n, 0)
        head.append('# subroutine: %s' % lname.title())
        head.append('function %s {' % g.func_names[lname])
        head.extend('    ' + l for l in g.lines)
        head.append('}')
        head.append('')
    g.lines = []

    if g._need_reg:
        head += REG_HELPERS_PS.splitlines()
        head.append('')

    first_sub = next((i for i, n in indexed
                      if n[0] == 'label' and n[1].upper() in called),
                     None)
    for i, n in indexed:
        if first_sub is not None and i >= first_sub:
            break                          # subroutine region starts here
        if n[0] == 'label':
            continue
        g.emit_node(n, 0)

    script = '\n'.join(head + g.lines).rstrip() + '\n'
    return script, g.stats['fallback']


import re as _re
