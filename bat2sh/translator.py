import os
import re
import shlex

from .commands import WIN_COMMAND_MAP
from .parser import Parser
from .shell import (_unquote, dos_slashes, expand_vars, fix_redir,
                    split_args, split_redir, split_top_ops, unescape_caret,
                    winpath)
# JSON-backed registry emulation for `reg add/query/delete`
REG_FUNCS = """\
REG_FILE="${BAT2SH_REG:-$HOME/.config/bat2sh/registry.json}"
reg_add() { python3 -c '
import json,sys,os
p,k,n,v=sys.argv[1:5]
d=json.load(open(p)) if os.path.exists(p) else {}
d.setdefault(k,{})[n]=v
os.makedirs(os.path.dirname(p),exist_ok=True)
json.dump(d,open(p,"w"),indent=1)
' "$REG_FILE" "$1" "$2" "$3"; }
reg_query() { python3 -c '
import json,sys,os
d=json.load(open(sys.argv[1])) if os.path.exists(sys.argv[1]) else {}
v=d.get(sys.argv[2],{}).get(sys.argv[3])
print(v if v is not None else "The system cannot find the specified registry key or value.")
sys.exit(0 if v is not None else 1)
' "$REG_FILE" "$1" "$2"; }
reg_del() { python3 -c '
import json,sys,os
p=sys.argv[1]
d=json.load(open(p)) if os.path.exists(p) else {}
d.get(sys.argv[2],{}).pop(sys.argv[3],None)
json.dump(d,open(p,"w"),indent=1)
' "$REG_FILE" "$1" "$2"; }
"""


class Translator:
    def __init__(self):
        self.label_map = {}
        self.func_names = {}
        self._need_ci = False
        self._need_reg = False

        def _sub_nul(a):
            return 'cat ' + re.sub(r'\bnul\b', '/dev/null', expand_vars(a))

        self._cmd = {
            'set': self.cmd_set, 'echo': self.cmd_echo,
            'cd': self.cmd_cd, 'chdir': self.cmd_cd, 'exit': self.cmd_exit,
            'rd': self.cmd_rd, 'rmdir': self.cmd_rd, 'del': self.cmd_del,
            'erase': self.cmd_del, 'copy': self.cmd_copy,
            'move': self.cmd_move, 'ren': self.cmd_ren,
            'rename': self.cmd_ren, 'pause': self.cmd_pause,
            'dir': self.cmd_dir, 'start': self.cmd_start,
            'path': self.cmd_path, 'call': self.cmd_call_ext,
            'md': lambda a: 'mkdir -p ' + expand_vars(a),
            'mkdir': lambda a: 'mkdir -p ' + expand_vars(a),
            'type': _sub_nul,
            'cls': lambda a: 'clear',
            'title': lambda a: "printf '\\033]0;%s\\007' " + '"'
                               + expand_vars(a) + '"',
            'color': lambda a: ':',
            'ver': lambda a: 'uname -a',
            'date': lambda a: 'date ' + expand_vars(a),
            'time': lambda a: 'date +%T ' + expand_vars(a),
            'setlocal': lambda a: ':  # setlocal',
            'endlocal': lambda a: ':  # endlocal',
            'pushd': lambda a: 'pushd ' + expand_vars(a),
            'popd': lambda a: 'popd',
            'shift': lambda a: 'ARGS=("${ARGS[@]:1}")',
            'find': lambda a: 'grep ' + expand_vars(a),
            'findstr': lambda a: 'grep -E ' + expand_vars(a),
            'choice': lambda a: 'choice ' + expand_vars(a),
            'cmd': self.cmd_cmd,
        }

    # command level
    def translate_segment(self, seg, nxt=0):
        seg = seg.strip()
        if seg == '':
            return ''
        if seg.startswith('@'):
            seg = seg[1:].strip()
        seg = dos_slashes(seg)
        seg = re.sub(r'([0-9]?>>?|<<?)\s*nul\b', r'\1/dev/null', seg)
        low = seg.lower()
        if low.startswith('rem '):
            return '# ' + seg[4:].strip()
        if seg.startswith('::'):
            return '# ' + seg[2:].strip()

        m = re.match(r'(\S+)\s*(.*)$', seg, re.DOTALL)
        cmd = m.group(1)
        args = m.group(2)
        lcmd = cmd.lower()

        if lcmd == 'goto':
            tgt = seg[4:].strip().lstrip(':')
            if tgt.lower() == 'eof':
                return self._emit_eof()
            t = self.label_map.get(tgt.upper())
            if t is None:
                return ('{ echo "The system cannot find the batch label '
                        'specified - %s" >&2; PC=-1; }' % tgt)
            return 'PC=%d; return' % t

        if lcmd == 'reg':
            return self.cmd_reg(args)

        h = self._cmd.get(lcmd)
        if h is not None:
            return h(args)
        handler = WIN_COMMAND_MAP.get(lcmd)
        if handler is not None:
            return handler(args)

        return expand_vars(seg)

    def cmd_reg(self, args):
        """reg add/query/delete -> JSON-backed registry emulation."""
        self._need_reg = True
        t = split_args(expand_vars(args.strip()))
        if not t:
            return ':  # reg'
        op = t[0].lower()
        key = '"%s"' % (t[1].replace('\\', '/') if len(t) > 1 else '')
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
        if op.startswith('add'):
            return 'reg_add %s "%s" "%s"' % (key, name, val)
        if op.startswith('query'):
            return 'reg_query %s "%s"' % (key, name)
        if op.startswith('delete'):
            return 'reg_del %s "%s"' % (key, name)
        return ':  # reg %s' % op

    def cmd_cmd(self, args):
        m = re.match(r'/[ck]\s+"?(.*?)"?\s*$', args, re.IGNORECASE)
        if not m:
            return 'bash -c "%s"' % expand_vars(args)
        cmdline = m.group(1).replace('exit /b', 'exit').replace('exit /B', 'exit')
        mb = re.match(r'"?([^"]+\.(?:bat|cmd))"?\s*(.*)$',
                      cmdline.strip(), re.IGNORECASE)
        if mb:
            sh = re.sub(r'\.(bat|cmd)$', '.sh', mb.group(1),
                        flags=re.IGNORECASE)
            if '/' not in sh and not sh.startswith('.'):
                sh = './' + sh
            rest = expand_vars(mb.group(2))
            return '"%s"%s' % (sh, (' ' + rest) if rest else '')
        return 'bash -c "%s"' % expand_vars(cmdline)

    def cmd_set(self, args):
        args = args.strip()
        if args == '':
            return 'set'
        mm = re.match(r'/a\s+(.*)', args, re.IGNORECASE)
        if mm:
            expr, redir = split_redir(mm.group(1).strip())
            expanded = expand_vars(expr)
            if '!' in expanded:
                return ('# unhandled: arithmetic uses delayed/indirect expansion '
                        'of a computed variable name: set /a %s' % expr)
            line = '(( %s ))' % expanded
            if redir:
                line += ' ' + fix_redir(redir)
            return line
        mm = re.match(r'/p\s+([A-Za-z_]\w*)\s*=\s*(.*)', args, re.IGNORECASE)
        if mm:
            var = mm.group(1)
            prompt = expand_vars(mm.group(2)).strip()
            if len(prompt) >= 2 and prompt.startswith('"') and prompt.endswith('"'):
                prompt = prompt[1:-1]
            if prompt == '':
                return 'IFS= read -r %s' % var
            return 'IFS= read -r -p "%s" %s' % (prompt, var)
        mm = re.match(r'("?)([A-Za-z_][\w.]*)\s*=\s*([^"]*)\1', args)
        if mm:
            name = expand_vars(mm.group(2)).replace('.', '_')
            val = mm.group(3)
            mci = re.search(r'(!|%)([A-Za-z_][\w.]*):(%%[A-Za-z])=(%%[A-Za-z])\1',
                            val)
            if mci:
                # batch replacement is case-insensitive; bash is not
                self._need_ci = True
                target = expand_vars(mci.group(2)).replace('.', '_')
                return 'ci_replace %s %s "$%s" "$%s"' % (
                    name, target, mci.group(3)[2], mci.group(4)[2])
            if '$' in name:
                return 'printf -v "%s" \'%%s\' "%s"' % (name, dos_slashes(expand_vars(val)))
            if val.strip() == '':
                return '%s=""' % name
            return '%s="%s"' % (name, dos_slashes(expand_vars(val)))
        mc = re.match(r'"([^"=]+)=(.*)"\s*$', args)
        if mc:
            name = expand_vars(mc.group(1)).replace('.', '_')
            val = dos_slashes(expand_vars(mc.group(2)))
            return 'printf -v "%s" \'%%s\' "%s"' % (name, val)
        return expand_vars('set ' + args)

    def cmd_echo(self, args):
        a = args.strip()
        if a.lower() in ('off', 'on'):
            return ':  # echo %s' % a
        if a == '.':
            return 'echo'
        if a.startswith('.'):
            a = a[1:]
        msg, redir = split_redir(a)
        msg = expand_vars(msg)
        if msg and any(ch in msg for ch in '()&|;<>') and \
                not (msg.startswith('"') and msg.endswith('"')):
            msg = '"%s"' % msg
        if redir:
            return 'echo %s %s' % (msg, fix_redir(redir))
        return 'echo ' + msg

    def cmd_pause(self, args):
        msg, redir = split_redir(args.strip())
        r = (' ' + fix_redir(redir)) if redir else ''
        return 'read -n1 -r -p "Press any key to continue . . . " || true; echo' + r

    def cmd_cd(self, args):
        a = args.strip()
        if a == '':
            return 'pwd'
        mm = re.match(r'/d\s+(.*)', a, re.IGNORECASE)
        if mm:
            a = mm.group(1).strip()
        path, redir = split_redir(a)
        if path.strip() == '':
            return 'pwd' + (' ' + fix_redir(redir) if redir else '')
        return 'cd "%s"%s' % (winpath(path.strip()), (' ' + fix_redir(redir) if redir else ''))

    def cmd_exit(self, args):
        a = args.strip()
        mb = re.match(r'/b\s*(\d+)?\s*$', a, re.IGNORECASE)
        if mb:
            return self._emit_eof(int(mb.group(1)) if mb.group(1) else None)
        if a == '':
            return 'exit'
        return 'exit ' + expand_vars(a)

    def cmd_rd(self, args):
        a = args.strip()
        recursive = bool(re.search(r'(^|\s)/s(?=\s|$)', a, re.IGNORECASE))
        a2 = re.sub(r'(^|\s)/[sq](?=\s|$)', '', a, flags=re.IGNORECASE).strip()
        if recursive:
            return 'rm -rf "%s"' % winpath(a2)
        return 'rmdir "%s"' % winpath(a2)

    def cmd_del(self, args):
        a = args.strip()
        recursive = bool(re.search(r'(^|\s)/s(?=\s|$)', a, re.IGNORECASE))
        a2 = re.sub(r'(^|\s)/[sqf](?=\s|$)', '', a, flags=re.IGNORECASE).strip()
        if recursive:
            return 'rm -rf "%s"' % winpath(a2)
        return 'rm -f "%s"' % winpath(a2)

    def cmd_copy(self, args):
        a = args.strip()
        a = re.sub(r'(^|\s)/[yb](?=\s|$)', '', a, flags=re.IGNORECASE).strip()
        parts = split_args(a)
        if len(parts) >= 2:
            return 'cp "%s" "%s"' % (winpath(parts[0]), winpath(parts[-1]))
        if len(parts) == 1:
            return 'cp "%s" .' % winpath(parts[0])
        return 'cp ' + expand_vars(a)

    def cmd_move(self, args):
        a = args.strip()
        a = re.sub(r'(^|\s)/[y](?=\s|$)', '', a, flags=re.IGNORECASE).strip()
        parts = split_args(a)
        if len(parts) >= 2:
            return 'mv "%s" "%s"' % (winpath(parts[0]), winpath(parts[-1]))
        return 'mv ' + expand_vars(a)

    def cmd_ren(self, args):
        a = args.strip()
        parts = split_args(a)
        if len(parts) >= 2:
            src = parts[0]
            dst = parts[1]
            if '/' not in dst and '\\' not in dst:
                d = os.path.dirname(src.strip('"').strip("'"))
                if d:
                    dst = d + '/' + dst
            return 'mv "%s" "%s"' % (winpath(src), winpath(dst))
        return 'mv ' + expand_vars(a)

    def cmd_start(self, args):
        a = expand_vars(args).strip()
        if a == '':
            return ':'
        wait = bool(re.search(r'/wait\b', a, re.I))
        rest = re.sub(r'/[a-z]+\b\s*', '', a,
                      flags=re.IGNORECASE).strip()
        m = re.match(r'"([^"]*)"\s*(.*)$', rest)
        if m:
            rest = m.group(2).strip()
        if not rest:
            return ':  # start: empty title only'
        low = rest.lower()
        if low.startswith(('http://', 'https://', 'www.')) or \
                rest.endswith('.url'):
            core = 'xdg-open %s' % (rest if rest.startswith('"')
                                    else '"%s"' % rest)
        else:
            core = rest
        if wait:
            return core
        return 'nohup %s >/dev/null 2>&1 &' % core

    def cmd_dir(self, args):
        a = args.strip()
        flags = ''
        if '/b' in a.lower():
            flags += ' -1'
        if '/s' in a.lower():
            flags += ' -R'
        if '/a' in a.lower():
            flags += ' -a'
        if '/w' in a.lower():
            flags += ' -w'
        a2 = re.sub(r'/[bsaw]+', '', a, flags=re.IGNORECASE).strip()
        path, redir = split_redir(a2)
        if path.strip() == '':
            return 'ls%s%s' % (flags, (' ' + fix_redir(redir) if redir else ''))
        return 'ls%s "%s"%s' % (flags, winpath(path.strip()), (' ' + fix_redir(redir) if redir else ''))

    def cmd_path(self, args):
        a = args.strip()
        if a == '':
            return 'echo "$PATH"'
        a = expand_vars(a).replace(';', ':')
        return 'export PATH="%s"' % a

    def cmd_call_ext(self, args):
        a = args.strip()
        if re.match(r'set\b', a, re.IGNORECASE):
            return self.cmd_set(expand_vars(a[3:].strip()))
        mm = re.match(r'("?)([^" ]+)\1(.*)$', a)
        if mm:
            prog = mm.group(2)
            rest = mm.group(3)
            prog = re.sub(r'\.(bat|cmd|BAT|CMD)$', '.sh', prog)
            if '/' not in prog and not prog.startswith('.'):
                prog = './' + prog
            if not prog.endswith('.sh'):
                prog = prog + '.sh'
            return '"%s"%s' % (prog, rest)
        return expand_vars(a)

    def _emit_eof(self, code=None):
        sep = r"$'\x1f'"
        setlvl = 'ERRORLEVEL=%d; ' % int(code) if code is not None else ''
        return (setlvl +
                'if [ ${#CALL_STACK[@]} -gt 0 ]; then '
                'PC="${CALL_STACK[-1]}"; unset "CALL_STACK[-1]"; '
                'if [ ${#ARGS_STACK[@]} -gt 0 ]; then '
                'IFS=%s read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi; '
                'else PC=-1; fi; return' % sep)

    def _save_args(self):
        sep = r"$'\x1f'"
        return 'ARGS_STACK+=("$(IFS=%s; echo "${ARGS[*]}")")' % sep

    def _restore_args(self):
        sep = r"$'\x1f'"
        return ('if [ ${#ARGS_STACK[@]} -gt 0 ]; then '
                'IFS=%s read -ra ARGS <<<"${ARGS_STACK[-1]}"; '
                'unset "ARGS_STACK[-1]"; fi' % sep)

    # simple line
    def translate_simple(self, text, nxt=0):
        parts = split_top_ops(text)
        out = []
        for seg, op in parts:
            line = self.translate_segment(seg, nxt)
            if line == '':
                continue
            out.append(line)
            if op:
                out.append(op)
        while out and out[-1] in ('&&', '||', '|', ';'):
            out.pop()
        if not out:
            return []
        return [unescape_caret(' '.join(out))]

    # node emission
    def emit_node(self, node, idx, nxt):
        t = node[0]
        if t == 'comment':
            return ['# ' + node[1]] if node[1] else []
        if t == 'label':
            return []
        if t == 'simple':
            lines = self.translate_simple(node[1], nxt)
            if lines:
                last = lines[-1].strip()
                if not last.startswith('#') and not last.startswith(':'):
                    lines.append('ERRORLEVEL=$?')
            return lines
        if t == 'goto':
            tgt = self.label_map.get(node[1].upper())
            if tgt is None:
                return ['{ echo "The system cannot find the batch label '
                        'specified - %s" >&2; PC=-1; }' % node[1]]
            return ['PC=%d; return' % tgt]
        if t == 'goto_eof':
            return [self._emit_eof()]
        if t == 'call_sub':
            sub = node[1].upper()
            tgt = self.label_map.get(sub)
            if tgt is None:
                return ['{ echo "The system cannot find the batch label '
                        'specified - %s" >&2; ERRORLEVEL=1; false; }' % sub]
            args = expand_vars(node[2])
            if sub in self.func_names:
                # plain call keeps working inside loops/if-blocks
                return [self._save_args(),
                        'ARGS=()' if args.strip() == '' else 'ARGS=(%s)' % args,
                        self.func_names[sub], self._restore_args()]
            if args.strip() == '':
                return [self._save_args(), 'ARGS=()',
                        'CALL_STACK+=("%d")' % nxt, 'PC=%d; return' % tgt]
            return [self._save_args(), 'ARGS=(%s)' % args,
                    'CALL_STACK+=("%d")' % nxt, 'PC=%d; return' % tgt]
        if t == 'call_ext':
            out = self.translate_simple(node[1], nxt)
            if out:
                last = out[-1].strip()
                if not last.startswith('#') and not last.startswith(':'):
                    out.append('ERRORLEVEL=$?')
            return out
        if t == 'if':
            return self.emit_if(node[1], idx, nxt)
        if t == 'for':
            return self.emit_for(node[1], idx, nxt)
        if t == 'block':
            out = []
            for n in node[1]:
                out.extend(self.emit_node(n, idx, nxt))
            return out
        return ['# unhandled: %r' % (node,)]

    def _body_lines(self, nodes, idx=0, nxt=0):
        """Emit indented body lines; guarantee a non-empty command list."""
        out = []
        for n in nodes:
            for l in self.emit_node(n, idx, nxt):
                out.append('    ' + l)
        if not any(l.strip() and not l.strip().startswith('#') for l in out):
            out.append('    :')
        return out

    def emit_if(self, d, idx=0, nxt=0):
        neg = d['neg']
        ctype = d['ctype']
        cond = d['cond']
        if ctype == 'errorlevel':
            test = '[ "$ERRORLEVEL" -ge %d ]' % cond
            if neg:
                test = '[ "$ERRORLEVEL" -lt %d ]' % cond
        elif ctype == 'defined':
            test = '[[ -n "${%s+x}" ]]' % cond
            if neg:
                test = '[[ -z "${%s+x}" ]]' % cond
        elif ctype == 'exist':
            test = '[[ -e "%s" ]]' % winpath(expand_vars(cond))
            if neg:
                test = '[[ ! -e "%s" ]]' % winpath(expand_vars(cond))
        elif ctype == 'compare':
            left = _unquote(expand_vars(cond[0]))
            right = _unquote(expand_vars(cond[1]))
            test = '[[ "%s" == "%s" ]]' % (left, right)
            if neg:
                test = '[[ "%s" != "%s" ]]' % (left, right)
        elif ctype == 'numcompare':
            left = _unquote(expand_vars(cond[0]))
            right = _unquote(expand_vars(cond[2]))
            op = cond[1]
            if op in ('equ', 'neq'):
                eq_op = '==' if ((op == 'equ') != bool(neg)) else '!='
                test = '[[ "%s" %s "%s" ]]' % (left, eq_op, right)
            else:
                opmap = {'lss': '-lt', 'leq': '-le', 'gtr': '-gt', 'geq': '-ge'}
                test = '[ "%s" %s "%s" ]' % (left, opmap[op], right)
                if neg:
                    test = '! ' + test
        else:
            test = 'false'
        lines = ['if ' + test + '; then']
        lines += self._body_lines(d['body'], idx, nxt)
        if d['elseb']:
            lines.append('else')
            lines += self._body_lines(d['elseb'], idx, nxt)
        lines.append('fi')
        return lines

    def emit_for(self, d, idx=0, nxt=0):
        var = d['var']
        flags = d['flags']
        lines = []
        repl = lambda l: re.sub(r'%%' + re.escape(var) + r'\b', '$' + var, l)
        if 'l' in flags:
            inner2 = expand_vars(d['inner']).strip().strip('()').strip()
            parts = [p.strip() for p in inner2.split(',')]
            if len(parts) == 3:
                start, step, end = parts
                try:
                    step_num = int(step)
                except ValueError:
                    step_num = 0
                if step_num >= 0:
                    cond = '%s<=%s' % (var, end)
                else:
                    cond = '%s>=%s' % (var, end)
                lines.append('for ((%s=%s; %s; %s+=%s)); do' % (var, start, cond, var, step))
            else:
                lines.append('for %s in %s; do' % (var, expand_vars(d['inner'])))
        elif 'r' in flags:
            root = winpath(expand_vars(d.get('base_dir', '') or '.')).strip('"')
            pats = [p.strip().strip('"') for p in
                    expand_vars(d['inner']).strip('()').split()]
            name_tests = ' -o '.join('-name %s' % shlex.quote(p)
                                     for p in pats if p)
            if not name_tests:
                name_tests = '-type f'
            else:
                name_tests = '\\( %s \\) -type f' % name_tests
            lines.append("while IFS= read -r -d '' _fr; do")
            lines.append('    %s="$_fr"' % var)
            body = self._body_lines(d['body'], idx, nxt)
            for l in body:
                lines.append(re.sub(r'%%([A-Za-z])\b', r'$\1', l))
            lines.append('done < <(LC_ALL=C find "%s" %s -print0 | sort -z)'
                         % (root, name_tests))
            lines.append('ERRORLEVEL=$?')
            return lines
        elif 'f' in flags:
            inner2 = d['inner'].strip()
            opts = d.get('opts', '') or ''
            usebackq = 'usebackq' in opts.lower()
            mdq = re.match(r'"(.*)"', inner2)          # double-quoted
            msq = re.match(r"'(.*)'", inner2)          # single-quoted
            mbt = re.match(r'`(.*)`', inner2)          # backquoted

            def _cmd_src(raw):
                cmdtext = expand_vars(raw)
                parts = split_top_ops(cmdtext)
                cmdtext = unescape_caret(''.join(seg + ((' ' + op) if op else '')
                                             for seg, op in parts))
                return '< <(%s)' % dos_slashes(cmdtext)

            def _str_src(raw):
                s = expand_vars(raw)
                if not usebackq:                       # standard "str" keeps quotes live
                    return '< <(printf \'%%s\\n\' "%s")' % s
                return '< <(printf \'%%s\\n\' %s)' % shlex.quote(s)

            src = None
            if usebackq:
                if mbt:                                # `cmd`  -> command
                    src = _cmd_src(mbt.group(1))
                elif mdq:                              # "file" -> file
                    src = '< "%s"' % winpath(mdq.group(1).strip())
                elif msq:                              # 'str'  -> literal string
                    src = _str_src(msq.group(1))
            else:
                if msq:                                # 'cmd'  -> command
                    src = _cmd_src(msq.group(1))
                elif mdq:                              # "str"  -> literal string
                    src = _str_src(mdq.group(1))
            if src is None:                            # bare    -> file
                fname = inner2.strip('()').strip()
                src = '< "%s"' % winpath(fname)

            dm = re.search(r'delims=("?)([^"\s]*)\1', opts, re.IGNORECASE)
            if dm:
                # delims= (empty) disables splitting entirely
                dch = dm.group(2)
                read_split = ('IFS=%s read -ra _arr <<< "$_line" || true'
                              % (shlex.quote(dch) if dch else "''"))
                delim_class = ''
                if dch:
                    esc = (dch.replace('[', '[[]').replace('*', '[*]')
                              .replace('?', '[?]'))
                    delim_class = '[%s]*' % esc
            else:
                read_split = "IFS=$' \\t' read -ra _arr <<< \"$_line\" || true"
                delim_class = ''
            tm = re.search(r'tokens=([\d,\-*]+)', opts, re.IGNORECASE)
            tokens = tm.group(1) if tm else '1'
            elements = [p.strip() for p in tokens.split(',')]
            nums = []
            star_tok = None
            for part in elements:
                if part == '*':
                    star_tok = 1
                    continue
                mn = re.match(r'^(\d+)\*$', part)
                if mn:
                    star_tok = int(mn.group(1))
                    continue
                if '-' in part:
                    a, b = part.split('-')
                    nums += list(range(int(a) - 1, int(b)))
                elif part.isdigit():
                    nums.append(int(part) - 1)
            base = ord(var)
            per_iter = [read_split]

            def _rest_from(n):
                per_iter.append('_anchor="${_arr[%d]:-}"' % (n - 1))
                per_iter.append('_pre="${_line%%"${_anchor}"*}"')
                per_iter.append('_incl="${_line:${#_pre}}"')

            if elements == ['*']:
                per_iter[0] = 'IFS=$\' \\t\' read -r %s <<< "$_line" || true' % var
            elif star_tok is not None and not nums:
                per_iter.append('%s="${_arr[%d]}"' % (chr(base), star_tok - 1))
                _rest_from(star_tok)
                nxt = chr(base + 1)
                per_iter.append('%s="${_incl#*"${_anchor}"}"' % nxt)
                if delim_class:
                    per_iter.append('%s="${%s#%s}"' % (nxt, nxt, delim_class))
            else:
                for k, idx in enumerate(nums):
                    per_iter.append('%s="${_arr[%d]}"' % (chr(base + k), idx))
                if star_tok is not None:
                    letter = chr(base + len(nums))
                    _rest_from(max(star_tok, 1))
                    per_iter.append('%s="${_incl}"' % letter)
            sm = re.search(r'skip=(\d+)', opts, re.IGNORECASE)
            skip = int(sm.group(1)) if sm else 0

            if skip:
                lines.append('_skip=%d' % skip)
                lines.append('while IFS= read -r _line; do')
                lines.append('    if [ $_skip -gt 0 ]; then ((_skip--)); continue; fi')
            else:
                lines.append('while IFS= read -r _line; do')
            for l in per_iter:
                lines.append('    ' + l)
            body = self._body_lines(d['body'], idx, nxt)
            for l in body:
                lines.append(re.sub(r'%%([A-Za-z])\b', r'$\1', l))
            lines.append('done %s' % src)
            lines.append('ERRORLEVEL=$?')
            return lines
        else:
            lines.append('for %s in %s; do' % (var, expand_vars(d['inner'])))
        body = self._body_lines(d['body'], idx, nxt)
        for l in body:
            lines.append(repl(l))
        lines.append('done')
        lines.append('ERRORLEVEL=$?')
        return lines

    # full conversion
    @staticmethod
    def _is_debug_line(line):
        s = line.strip()
        if s.startswith('# Converted from a Windows batch file by bat2sh'):
            return True
        if re.match(r'^\s*# choice: emulate', line):
            return True
        if re.match(r'^\s*:\s+#', line):
            return True
        return False

    def convert(self, text, clean=False, shebang=None):
        text = self.join_continuations(text)
        nodes = Parser(text).parse_program()
        indexed = list(enumerate(nodes))
        self.label_map = {}
        for i, n in indexed:
            if n[0] == 'label':
                self.label_map[n[1].upper()] = i

        # call-only labels become bash functions so calls work inside
        # loops/if-blocks (a PC jump would abandon them)
        def _walk(ns):
            for n in ns:
                yield n
                if n[0] == 'if':
                    yield from _walk(n[1]['body'])
                    if n[1]['elseb']:
                        yield from _walk(n[1]['elseb'])
                elif n[0] == 'for':
                    yield from _walk(n[1]['body'])
                elif n[0] == 'block':
                    yield from _walk(n[1])

        all_nodes = list(_walk(nodes))
        called = {n[1].upper() for n in all_nodes
                  if n[0] == 'call_sub' and n[1].upper() in self.label_map}
        goto_targets = {n[1].upper() for n in all_nodes if n[0] == 'goto'}
        self.func_names = {
            name: 'sub_' + re.sub(r'\W', '_', name).lower()
            for name in sorted(called - goto_targets)
        }

        eof_stmt = self._emit_eof()
        label_pos = [(i, n[1].upper()) for i, n in indexed if n[0] == 'label']
        func_defs = []
        for pos, (li, lname) in enumerate(label_pos):
            if lname not in self.func_names:
                continue
            start = li + 1
            end = label_pos[pos + 1][0] if pos + 1 < len(label_pos) else len(nodes)
            body = []
            for j in range(start, end):
                n = nodes[j]
                if n[0] == 'label':
                    continue
                if n[0] in ('goto', 'goto_eof'):
                    body.append('return')
                    continue
                body.extend(self.emit_node(n, j, j + 1))
            body = ['return' if ln == eof_stmt else ln for ln in body]
            func_defs.append('# subroutine: %s\n%s() {\n%s\n}'
                             % (lname.title(), self.func_names[lname],
                                '\n'.join('    ' + l for l in body)))

        arms = []
        for i, n in indexed:
            nxt = i + 1
            body = self.emit_node(n, i, nxt)
            # only DEFINED pc-mode calls jump without advancing; an
            # undefined call must fall through or the arm loops forever
            is_jump = n[0] in ('goto', 'goto_eof') or (
                n[0] == 'call_sub' and n[1].upper() in self.label_map
                and n[1].upper() not in self.func_names)
            if is_jump:
                arm_body = body
            else:
                arm_body = body + ['PC=%d' % nxt]
            if not arm_body:
                arm_body = ['PC=%d' % nxt]
            arms.append('    %d)\n%s\n        ;;' % (i, '\n'.join('        ' + l for l in arm_body)))

        preamble = '''#!/usr/bin/env bash
# Converted from a Windows batch file by bat2sh.
set -o pipefail
shopt -s nocasematch   # emulate "if /i" case-insensitive compares

CALL_STACK=()
ARGS_STACK=()
ARGS=("$@")
ERRORLEVEL=0
PC=0

# cmd.exe-style diagnostics for unknown commands
command_not_found_handle() {
    printf "'%s' is not recognized as an internal or external command,\\n" "$1" >&2
    echo "operable program or batch file." >&2
    ERRORLEVEL=9009
    return 9009
}

# choice: emulate the batch CHOICE command
choice() {
    local opts="" prompt="" default="" t=""
    while [ $# -gt 0 ]; do
        case "$1" in
            /c:*) opts="${1#/c:}";;
            /m:*) prompt="${1#/m:} ";;
            /t:*) t="${1#/t:}";;
            /d:*) default="${1#/d:}";;
        esac
        shift
    done
    if [ -n "$t" ]; then
        read -n1 -r -t "$t" -p "$prompt" _ch || _ch=""
    else
        read -n1 -r -p "$prompt" _ch || _ch=""
    fi
    echo
    [ -z "$_ch" ] && [ -n "$default" ] && _ch="$default"
    if [ -t 0 ]; then
        IFS= read -r _rest || true
    fi
    local i
    for ((i=1; i<=${#opts}; i++)); do
        c="${opts:i-1:1}"
        if [ "$_ch" = "$c" ]; then ERRORLEVEL=$i; return; fi
    done
    ERRORLEVEL=255
}

dispatch() {
    case $PC in'''
        epilogue = '''
        *) PC=-1;;
    esac
}

run() {
    while [ "$PC" -ge 0 ]; do
        dispatch
    done
}

run
exit $ERRORLEVEL
'''
        extras = func_defs
        if self._need_reg:
            extras = [REG_FUNCS] + extras
        if self._need_ci:
            ci_helper = (
                '# case-insensitive replace (batch semantics):'
                '\nci_replace() {\n'
                '    local __d="$1" __s="$2" __f="$3" __r="$4" __t __u __l\n'
                '    [ -z "$__f" ] && return 0\n'
                '    __u="${__f^^}" __l="${__f,,}"\n'
                '    __t="${!__s//"$__u"/$__r}"\n'
                '    printf -v "$__d" \'%s\' "${__t//"$__l"/$__r}"\n'
                '}')
            extras = [ci_helper] + extras
        script = preamble + '\n'.join(arms) + epilogue
        if shebang:
            lines = script.split('\n')
            lines[0] = shebang if shebang.startswith('#!') \
                else '#!' + shebang
            script = '\n'.join(lines)
        if extras:
            marker = 'dispatch() {\n    case $PC in'
            head, tail = preamble.split(marker)
            script = (head + '\n' + '\n\n'.join(extras) + '\n\n'
                      + marker + '\n'.join(arms) + epilogue)
        if clean:
            script = '\n'.join(
                ln for ln in script.split('\n')
                if not self._is_debug_line(ln)
            )
            # drop the inline explanation on the shopt line
            script = re.sub(r'(shopt -s nocasematch).*', r'\1', script)
        return script

    def join_continuations(self, text):
        lines = text.split('\n')
        out = []
        buf = ''
        for line in lines:
            stripped = line.rstrip()
            if stripped.endswith('^'):
                buf += line[:stripped.rfind('^')]
                continue
            if buf:
                buf += line
                out.append(buf)
                buf = ''
            else:
                out.append(line)
        if buf:
            out.append(buf)
        return '\n'.join(out)

