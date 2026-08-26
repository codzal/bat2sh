"""Static compatibility audit of batch sources."""
import re

# (id, regex, severity, message)
_RULES = [
    ('registry', re.compile(r'\breg(\.exe)?\s+(add|query|delete|export|import)\b', re.I), 'warn',
     'script touches the Windows registry; check the logic '
     '(emulated via a JSON store when run through bat2sh)'),
    ('regfile', re.compile(r'\.reg\b', re.I), 'warn',
     '.reg file referenced - manual review required'),
    ('binary', re.compile(r'"?[^"\s]+\.(exe|msi|com)\b', re.I), 'warn',
     'Windows binary launched: wrap with `wine <prog>` or replace with a '
     'Linux equivalent'),
    ('service', re.compile(r'\b(net\s+(start|stop)|sc\s+(config|start|stop)|'
                           r'vssadmin)\b', re.I), 'warn',
     'Windows service management detected - map to systemctl/service'),
    ('wmi', re.compile(r'\bwmic\b', re.I), 'info',
     'wmic has no POSIX equivalent; rewrite the query'),
]

# known single-command suggestions for binaries
_SUGGEST = {
    'notepad': 'gedit / nano',
    'calc': 'gnome-calculator / bc',
    'mspaint': 'kolourpaint / gimp',
    'taskmgr': 'htop / top',
    'explorer': 'xdg-open .',
    'msiexec': 'wine msiexec',
}


def analyze(text):
    """Yield dicts: line, col, id, severity, message, snippet."""
    out = []
    for no, raw in enumerate(text.splitlines(), 1):
        code = raw.split('::')[0].strip()
        low = code.lower()
        if low.startswith(('rem ', '@rem ')):
            continue
        for rid, rx, sev, msg in _RULES:
            m = rx.search(code)
            if not m:
                continue
            extra = ''
            if rid == 'binary':
                # the rule may swallow directories: C:\dir\tool.exe
                base = re.split(r'[\\/]', m.group(0))[-1]
                name_m = re.match(r'([\w.-]+?)\.(?:exe|msi|com)', base,
                                  re.I)
                if name_m and name_m.group(1).lower() in _SUGGEST:
                    extra = ' Suggestion: %s' % _SUGGEST[name_m.group(1)
                                                         .lower()]
                else:
                    extra = (' Suggestion: wine %s or an equivalent '
                             'utility' % base)
            out.append({'line': no, 'col': m.start() + 1, 'id': rid,
                        'severity': sev,
                        'message': msg + extra,
                        'snippet': raw.rstrip()[:120]})
    return out


def summarize(findings):
    order = {'warn': 0, 'info': 1}
    return sorted(findings, key=lambda f: (order[f['severity']], f['line']))


def migration_report(items, fmt='md'):
    """items: [(name, stats, findings)] -> markdown or html string."""
    total_stmts = sum(st.get('stmts', 0) for _n, st, _f in items) or 1
    total_fb = sum(st.get('fallback', 0) for _n, st, _f in items)
    pct = 100 * (total_stmts - total_fb) // total_stmts
    if fmt == 'html':
        rows = []
        for name, st, finds in items:
            badges = ''.join('<li>%s:%d %s</li>' % (f['id'], f['line'],
                                                    f['message'])
                             for f in finds) or '<li>clean</li>'
            rows.append(
                '<tr><td>%s</td><td>%d</td><td>%d</td>'
                '<td>%.0f%%</td><td><ul>%s</ul></td></tr>'
                % (name, st.get('stmts', 0), st.get('fallback', 0),
                   100 * (st.get('stmts', 0) - st.get('fallback', 0))
                   // max(st.get('stmts', 1)), badges))
        return ('<h1>bat2sh migration report</h1>'
                '<p>Overall translation coverage: <b>%d%%</b></p>'
                '<table border=1 cellpadding=4>'
                '<tr><th>file</th><th>statements</th><th>fallbacks</th>'
                '<th>coverage</th><th>manual attention</th></tr>%s</table>'
                % (pct, ''.join(rows)))
    lines = ['# bat2sh migration report', '',
             'Overall translation coverage: **%d%%**' % pct, '',
             '| file | stmts | fallback | coverage | attention |',
             '|---|---|---|---|---|']
    for name, st, finds in items:
        cov = (100 * (st.get('stmts', 0) - st.get('fallback', 0))
               // max(st.get('stmts', 1), 1))
        att = ('; '.join('%s:%d' % (f['id'], f['line'])
                         for f in finds)) or 'clean'
        lines.append('| %s | %d | %d | %d%% | %s |'
                     % (name, st.get('stmts', 0), st.get('fallback', 0),
                        cov, att))
    for name, st, finds in items:
        if finds:
            lines += ['', '## %s' % name]
            lines += ['- `%d`: %s' % (f['line'], f['message']) for f in finds]
    return '\n'.join(lines) + '\n'
