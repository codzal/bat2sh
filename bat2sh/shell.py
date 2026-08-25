import re
from functools import lru_cache

_RX_REDIR_SPLIT = re.compile(r'(\d*(?:>>?|<<?))')
_RX_REDIR_OP = re.compile(r'\d*(?:>>?|<<?)')


def _unquote(s):
    """Strip one pair of surrounding double quotes, if present."""
    s = s.strip()
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        return s[1:-1]
    return s


@lru_cache(maxsize=8192)
def winpath(s):
    if not s:
        return s
    s = expand_vars(s)
    s = s.strip()
    quoted = s.startswith('"') and s.endswith('"')
    if quoted:
        s = s[1:-1]
    m = re.match(r'^([A-Za-z]):[\\/](.*)$', s)
    if m:
        s = '/mnt/' + m.group(1).lower() + '/' + m.group(2)
    s = s.replace('\\', '/')
    return s


def fix_redir(redir):
    """Expand variables and translate every file target inside a
    redirection clause (e.g. ``> build\\%PROJ%_%%n.txt 2>&1``)."""
    parts = _RX_REDIR_SPLIT.split(redir)
    out = []
    for p in parts:
        if p == '':
            continue
        if _RX_REDIR_OP.fullmatch(p):
            out.append(p)
            continue
        p = p.strip()
        if not p:
            continue
        if p.startswith('&'):
            out.append(p)
        elif p.startswith('"'):
            qe = p.find('"', 1)
            fn = p[1:qe] if qe != -1 else p[1:]
            out.append('"%s"' % winpath(fn))
        else:
            out.append('"%s"' % winpath(p))
    return ''.join(out)


def split_redir(s):
    """Split a command tail into (args, redirection) at the first top-level
    > or < so redirection is not swallowed as a path argument.

    A '>' or '<' is treated as a redirect operator only when it is preceded
    by whitespace, a file descriptor digit, '&', or another redirect char.
    This keeps literal comparisons such as '>=' or '<=' inside text (e.g. an
    ECHO message) from being mistaken for redirection.
    """
    q = False
    i = 0
    n = len(s)
    pos = None
    if '>' not in s and '<' not in s:
        return s, ''
    while i < n:
        c = s[i]
        if c == '"':
            q = not q
        elif not q and c in '<>':
            prev = s[i - 1] if i > 0 else ''
            is_redir = (prev == '' or prev.isspace() or prev.isdigit()
                        or prev in '&<>')
            if is_redir:
                # a redirect operator is never followed by '=' (that would be
                # a comparison such as '>=' or '<='); keep those as literal text
                j = i + 1
                if j < n and s[j] == c:
                    j += 1
                if j < n and s[j] == '=':
                    is_redir = False
            if is_redir:
                p = i
                if c == '>' and i > 0 and s[i - 1].isdigit():
                    p = i - 1
                pos = p
                break
        i += 1
    if pos is None:
        return s, ''
    return s[:pos].rstrip(), s[pos:]


def split_args(s):
    """Whitespace-split a command tail respecting single/double quotes."""
    out = []
    cur = []
    q = None
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if q:
            if c == q:
                q = None
            else:
                cur.append(c)
            i += 1
            continue
        if c in '"\'':
            q = c
            i += 1
            continue
        if c.isspace():
            if cur:
                out.append(''.join(cur))
                cur = []
            i += 1
            continue
        cur.append(c)
        i += 1
    if cur:
        out.append(''.join(cur))
    return out


def unquote(s):
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in '"\'':
        return s[1:-1]
    return s


_RX_REPL_PCT = re.compile(r'%([A-Za-z_][\w.]*):([^=%]*)=([^%]*)%')
_RX_SUB_PCT = re.compile(r'%([A-Za-z_]\w*):~(-?\d+)(?:,(\d+))?%')
_RX_MOD = re.compile(r'%~(dp|p|f|nx|n|x)(\d)')
_RX_ARG = re.compile(r'%~?(\d+)')
_RX_ERRLEVEL = re.compile(r'%errorlevel%', re.IGNORECASE)
_RX_VAR = re.compile(r'%([A-Za-z_][\w.]*)%')
_RX_ESC_PCT = re.compile(r'%%(?![\w])')
_RX_REPL_DEL = re.compile(r'!([A-Za-z_][\w.]*):([^=!]*)=([^!]*)!')
_RX_DEL = re.compile(r'!([A-Za-z_][\w.]*(?::~[^!]*)?)!')
_RX_SUBSTR_INNER = re.compile(r'([A-Za-z_][\w.]*):~(-?\d+)(?:,(\d+))?')

# %~dp0-style argument modifiers -> bash snippets
_MOD_MAP = {
    'dp': '"$(dirname "$0")/"',
    'p': '"$(dirname "$0")"',
    'f': '"$(readlink -f "$0")"',
    'nx': '"$(basename "$0")"',
    'n': '"$(basename "$0" .${0##*.})"',
    'x': '".${0##*.}"',
}


def _substr_expr(name, start, length):
    """Bash substring expression for ``%VAR:~s,l%`` / ``!VAR:~s,l!``."""
    name = name.replace('.', '_')
    if start.lstrip('-').isdigit() and (length is None or length.isdigit()):
        if start.startswith('-'):
            k = int(start)
            start = ('$(( ( ${#%s} %d ) < 0 ? 0 : ( ${#%s} %d ) ))'
                     % (name, k, name, k))
        if length is not None:
            return '${%s:%s:%s}' % (name, start, length)
        return '${%s:%s}' % (name, start)
    return '${%s}' % name


def _repl_sub(m):
    """``VAR:find=rep`` -> ``${VAR//find/rep}``.

    Batch replacement is case-insensitive, so every letter of *find* becomes
    a two-case glob class; backslash-free escapes survive dos_slashes.
    """
    find = m.group(2)
    rep = m.group(3)
    if not find or '/' in find:
        return m.group(0)
    out = []
    for ch in find:
        if ch.isalpha():
            out.append('[%s%s]' % (ch.lower(), ch.upper()))
        elif ch == '[':
            out.append('[[]')
        elif ch == '*':
            out.append('[*]')
        elif ch == '?':
            out.append('[?]')
        else:
            out.append(ch)
    return '${%s//%s/%s}' % (m.group(1).replace('.', '_'), ''.join(out), rep)


def _mod_sub(m):
    kinds, num = m.groups()
    if num == '0':
        return _MOD_MAP[kinds]
    return '$%s' % num


def _arg_sub(m):
    if m.group(1) == '0':
        return '$0'
    return '${ARGS[%d]}' % (int(m.group(1)) - 1)


@lru_cache(maxsize=8192)
def expand_vars(s):
    if s is None:
        return s
    if '%' not in s and '!' not in s:
        return s
    s = _RX_REPL_PCT.sub(_repl_sub, s)
    s = _RX_SUB_PCT.sub(lambda m: _substr_expr(m.group(1), m.group(2),
                                               m.group(3)), s)
    s = _RX_MOD.sub(_mod_sub, s)
    s = s.replace('%*', '"${ARGS[@]}"')
    s = _RX_ARG.sub(_arg_sub, s)
    s = _RX_ERRLEVEL.sub('${ERRORLEVEL}', s)
    s = _RX_VAR.sub(lambda m: '${%s}' % m.group(1).replace('.', '_'), s)
    s = _RX_ESC_PCT.sub('%', s)

    def _del(m):
        inner = m.group(1)
        mm = _RX_SUBSTR_INNER.match(inner)
        if mm:
            return _substr_expr(mm.group(1), mm.group(2), mm.group(3))
        return '${%s}' % inner.replace('.', '_')

    s = _RX_REPL_DEL.sub(_repl_sub, s)
    s = _RX_DEL.sub(_del, s)
    return s


_RX_CARET = re.compile(r'\^([&|<>()%^])')


@lru_cache(maxsize=8192)
def unescape_caret(s):
    """Remove batch caret escapes (^&) so bash sees the literal character."""
    if '^' not in s:
        return s
    return _RX_CARET.sub(r'\1', s)


@lru_cache(maxsize=8192)
def dos_slashes(s):
    """Convert DOS backslashes to forward slashes (outside single quotes
    and outside %...% variable references)."""
    if '\\' not in s:
        return s
    if "'" not in s and '%' not in s:
        return s.replace('\\', '/')
    out = []
    q = False
    in_var = False
    for c in s:
        if c == "'":
            q = not q
            out.append(c)
        elif c == '%' and not q:
            in_var = not in_var
            out.append(c)
        elif c == '\\' and not q and not in_var:
            out.append('/')
        else:
            out.append(c)
    return ''.join(out)


def split_top_ops(text):
    """Split a simple statement on top-level &&, || and standalone &.

    Returns list of (segment, operator) where operator is '&&', '||', ';'
    (standalone & -> ';') or '' for the last piece. Quotes/parens respected.
    """
    if '&' not in text and '|' not in text:
        return [(text, '')]
    out = []
    cur = []
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c in '"\'':
            q = c
            cur.append(c)
            i += 1
            while i < n and text[i] != q:
                if text[i] == '\\' and q == '"':
                    cur.append(text[i]); i += 1
                    if i < n:
                        cur.append(text[i]); i += 1
                    continue
                cur.append(text[i]); i += 1
            if i < n:
                cur.append(text[i]); i += 1
            continue
        if c in '()':
            cur.append(c); i += 1; continue
        if c == '^' and i + 1 < n and text[i + 1] in '&|<>()^':
            cur.append('^' + text[i + 1]); i += 2; continue
        if c == '&':
            if i > 0 and text[i - 1] == '>':
                cur.append('&'); i += 1; continue
            if i + 1 < n and text[i + 1] == '&':
                out.append((''.join(cur), '&&')); cur = []; i += 2; continue
            out.append((''.join(cur), ';')); cur = []; i += 1; continue
        if c == '|':
            if i + 1 < n and text[i + 1] == '|':
                out.append((''.join(cur), '||')); cur = []; i += 2; continue
            out.append((''.join(cur), '|')); cur = []; i += 1; continue
        cur.append(c); i += 1
    out.append((''.join(cur), ''))
    return out

