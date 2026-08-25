"""Minimal .bat -> PowerShell (ps1) translator (beta subset)."""
import re

_MAP = [
    ('echo', lambda a: 'Write-Output %s' % _ps(a)),
    ('rem', lambda a: '# ' + a),
    ('set ', None),
    ('if exist', None),
    ('cd', lambda a: 'Set-Location %s' % _ps(a)),
    ('md', lambda a: 'New-Item -ItemType Directory -Force -Path %s' % _ps(a)),
    ('mkdir', lambda a: 'New-Item -ItemType Directory -Force -Path %s' % _ps(a)),
    ('del', lambda a: 'Remove-Item -Force %s' % _ps(a)),
    ('copy', lambda a: 'Copy-Item %s' % _ps(a)),
    ('move', lambda a: 'Move-Item %s' % _ps(a)),
    ('ren', lambda a: 'Rename-Item %s' % _ps(a)),
    ('type', lambda a: 'Get-Content %s' % _ps(a)),
    ('cls', lambda a: 'Clear-Host'),
    ('pause', lambda a: '$null = Read-Host "Press any key to continue"'),
]


def _ps(a):
    """Convert %VAR% and windows paths inside an argument string."""
    a = re.sub(r'%([A-Za-z_]\w*)%', r'$env:\1', a)
    return a.replace('\\', '/')


def line_to_ps(line):
    """Translate one simple statement; returns ps1 text or warning comment."""
    st = line.strip()
    if not st or st.startswith('::'):
        return ('# ' + st[2:].strip()) if st else ''
    low = st.lower()
    if low.startswith('rem '):
        return '# ' + st[4:]
    if low.startswith('@'):
        st = st[1:].lstrip()
        low = st.lower()
    if low == 'echo off':
        return ''
    m = re.match(r'set\s+/?a?\s+([A-Za-z_]\w*)=(.*)$', st, re.I)
    if m:
        var, expr = m.group(1), m.group(2).strip()
        expr = re.sub(r'%([A-Za-z_]\w*)%', r'$env:\1', expr)
        prefix = '$env:' if var.isupper() else '$'
        return '%s%s = %s' % (prefix, var, expr)
    m = re.match(r'if\s+(not\s+)?exist\s+(\S+)\s+(.*)$', st, re.I)
    if m:
        neg, path, body = m.groups()
        cond = 'Test-Path "%s"' % path.strip('"')
        return 'if (%s) { %s }' % (('! ' + cond) if neg else cond,
                                   line_to_ps(body))
    for name, fn in _MAP:
        if not isinstance(name, str):
            continue
        key = name.rstrip()
        if low == key or low.startswith(key + ' ') or \
                (name.endswith(' ') and low.startswith(name)):
            argtext = st[len(key):].strip()
            return fn(argtext) if callable(fn) else fn
    return "# BAT2SH WARNING: no PowerShell mapping for: %s" % st


def convert(text):
    out = ['#requires -Version 5.1',
           '# Converted from a Windows batch file by bat2sh (--target=ps1)',
           '']
    warns = 0
    for raw in text.splitlines():
        ps = line_to_ps(raw) or ''
        if ps.startswith('# BAT2SH WARNING'):
            warns += 1
        out.append(ps)
    return '\n'.join(out) + '\n', warns
