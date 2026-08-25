import re

_RX_WS = re.compile(r'[ \t\r\n]*')


class Parser:
    def __init__(self, text):
        self.text = text
        self.n = len(text)
        self.i = 0

    def eof(self):
        return self.i >= self.n

    def skip_ws(self):
        m = _RX_WS.match(self.text, self.i)
        self.i = m.end()

    def _skip_quoted(self, i):
        q = self.text[i]
        i += 1
        while i < self.n and self.text[i] != q:
            if self.text[i] == '\\' and q == '"':
                i += 2
                continue
            i += 1
        if i < self.n:
            i += 1
        return i

    def _read_first_word(self):
        m = re.match(r'\S+', self.text[self.i:])
        w = m.group(0)
        self.i += len(w)
        self.skip_ws()
        return w

    def _match_word(self, w):
        m = re.match(r'\S+', self.text[self.i:])
        if m and m.group(0).lower() == w.lower():
            self.i += len(m.group(0))
            self.skip_ws()
            return True
        return False

    def _read_until_body_or_eol(self):
        out = []
        i = self.i
        while i < self.n:
            c = self.text[i]
            if c in '"\'':
                q = c
                out.append(c); i += 1
                while i < self.n and self.text[i] != q:
                    if self.text[i] == '\\' and q == '"':
                        out.append(self.text[i]); i += 1
                        if i < self.n:
                            out.append(self.text[i]); i += 1
                        continue
                    out.append(self.text[i]); i += 1
                if i < self.n:
                    out.append(self.text[i]); i += 1
                continue
            if c == '(':
                break
            if c == '\n' or c == '\r':
                break
            if c == '&' and (i + 1 >= self.n or self.text[i + 1] != '&'):
                break
            out.append(c); i += 1
        return ''.join(out)

    def _read_simple_line_from(self, start):
        self.i = start
        out = []
        while self.i < self.n:
            c = self.text[self.i]
            if c in '"\'':
                q = c
                out.append(c); self.i += 1
                while self.i < self.n and self.text[self.i] != q:
                    if self.text[self.i] == '\\' and q == '"':
                        out.append(self.text[self.i]); self.i += 1
                        if self.i < self.n:
                            out.append(self.text[self.i]); self.i += 1
                        continue
                    out.append(self.text[self.i]); self.i += 1
                if self.i < self.n:
                    out.append(self.text[self.i]); self.i += 1
                continue
            if c == '^' and self.i + 1 < self.n and self.text[self.i + 1] in '&|<>()^':
                out.append('^' + self.text[self.i + 1]); self.i += 2; continue
            if c == '\n' or c == '\r':
                break
            if c == '&':
                if self.i + 1 < self.n and self.text[self.i + 1] == '&':
                    out.append(c); self.i += 1; continue
                if self.i > 0 and self.text[self.i - 1] == '>':
                    out.append(c); self.i += 1; continue
                break
            out.append(c); self.i += 1
        if self.i < self.n and self.text[self.i] == '&':
            self.i += 1
        return ''.join(out)

    def _read_block(self):
        self.i += 1
        depth = 1
        start = self.i
        while self.i < self.n:
            c = self.text[self.i]
            if c in '"\'':
                self.i = self._skip_quoted(self.i); continue
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0:
                    inner = self.text[start:self.i]
                    self.i += 1
                    return inner
            self.i += 1
        return self.text[start:]

    def parse_program(self):
        nodes = []
        while True:
            self.skip_ws()
            if self.eof():
                break
            stmt_start = self.i
            word = self._read_first_word()
            low = word.lower()
            if low == '(':
                self.i = stmt_start
                inner = self._read_block()
                node = ('block', Parser(inner).parse_program())
            elif low in ('if', 'for'):
                self.i = stmt_start
                node = self.parse_if_adv() if low == 'if' else self.parse_for_adv()
            else:
                self.i = stmt_start
                text = self._read_simple_line_from(stmt_start)
                node = self.parse_one(text.strip())
            if node is not None:
                nodes.append(node)
        return nodes

    def parse_one(self, chunk):
        if chunk == '':
            return None
        low = chunk.lower()
        if low == 'rem':
            return ('comment', '')
        if low.startswith('rem '):
            return ('comment', chunk[4:].strip())
        if chunk.startswith('::'):
            return ('comment', chunk[2:].strip())
        if chunk.startswith(':'):
            name = chunk[1:].strip()
            if name.lower() == 'eof':
                return ('comment', ':eof')
            return ('label', name)
        if re.match(r'if(\s|/)', chunk, re.IGNORECASE):
            sub = Parser(chunk).parse_program()
            return sub[0] if sub else ('simple', chunk)
        if re.match(r'for(\s|/)', chunk, re.IGNORECASE):
            sub = Parser(chunk).parse_program()
            return sub[0] if sub else ('simple', chunk)
        if re.match(r'goto(\s|/)', chunk, re.IGNORECASE):
            target = chunk[4:].strip()
            if target.startswith(':'):
                target = target[1:]
            return ('goto_eof',) if target.lower() == 'eof' else ('goto', target)
        if re.match(r'call(\s|/)', chunk, re.IGNORECASE):
            rest = chunk[4:].strip()
            if rest.startswith(':'):
                sub = rest[1:].strip()
                args = ''
                if ' ' in sub:
                    sub, args = sub.split(' ', 1)
                return ('call_sub', sub, args)
            return ('call_ext', rest)
        return ('simple', chunk)

    # if
    def parse_if_adv(self):
        self.i += 2  # skip 'if'
        self.skip_ws()
        neg = False
        nocase = False
        while True:
            if self._match_word('/i'):
                nocase = True; continue
            if self._match_word('not'):
                neg = True; continue
            break
        rest_start = self.i
        rest = self._read_until_body_or_eol()
        ctype = None
        cond = None
        consumed = 0
        m = re.match(r'errorlevel\s+(\d+)', rest, re.IGNORECASE)
        if m:
            ctype = 'errorlevel'; cond = int(m.group(1)); consumed = len(m.group(0))
        if ctype is None:
            m = re.match(r'(\S+)\s+(equ|neq|lss|leq|gtr|geq)\s+(\S+)', rest, re.IGNORECASE)
            if m:
                ctype = 'numcompare'
                cond = (m.group(1), m.group(2).lower(), m.group(3))
                consumed = len(m.group(0))
        if ctype is None:
            m = re.match(r'defined\s+(%%?[A-Za-z]\w*|[A-Za-z_][\w.!%$]*)',
                         rest, re.IGNORECASE)
            if m:
                ctype = 'defined'; cond = m.group(1); consumed = len(m.group(0))
        if ctype is None:
            m = re.match(r'exists?\s+', rest, re.IGNORECASE)
            if m:
                after = rest[m.end():]
                if after.startswith('"'):
                    qend = after.find('"', 1)
                    if qend == -1:
                        qend = len(after) - 1
                    cond = after[:qend + 1].strip()
                    consumed = m.end() + qend + 1
                else:
                    parts = after.split(None, 1)
                    cond = parts[0] if parts else ''
                    consumed = m.end() + len(cond)
                ctype = 'exist'
        if ctype is None:
            pos = None
            p = 0
            while p < len(rest):
                c = rest[p]
                if c in '"\'':
                    q = c; p += 1
                    while p < len(rest) and rest[p] != q:
                        p += 1
                    if p < len(rest):
                        p += 1
                    continue
                if rest[p:p + 2] == '==':
                    pos = p; eq = '=='; break
                if c == '(':
                    break
                p += 1
            if pos is None:
                p = 0
                while p < len(rest):
                    c = rest[p]
                    if c in '"\'':
                        q = c; p += 1
                        while p < len(rest) and rest[p] != q:
                            p += 1
                        if p < len(rest):
                            p += 1
                        continue
                    if c == '=' and (p == 0 or rest[p - 1] not in '<>=!') and \
                            (p + 1 >= len(rest) or rest[p + 1] != '='):
                        pos = p; eq = '='; break
                    if c == '(':
                        break
                    p += 1
            if pos is not None:
                left = rest[:pos].strip()
                after = rest[pos + len(eq):]
                after_stripped = after.lstrip()
                mright = re.match(r'\S+', after_stripped)
                right = mright.group(0) if mright else ''
                body_start = (pos + len(eq) + (len(after) - len(after_stripped))
                              + len(right))
                ctype = 'compare'; cond = (left, right); consumed = body_start
        if ctype is None:
            text = self._read_simple_line_from(rest_start)
            return ('simple', text)
        self.i = rest_start + consumed
        self.skip_ws()
        body, elseb = self._read_if_body()
        return ('if', dict(neg=neg, nocase=nocase, ctype=ctype,
                           cond=cond, body=body, elseb=elseb))

    def _read_if_body(self):
        self.skip_ws()
        if self.eof():
            return [], None
        if self.text[self.i] == '(':
            inner = self._read_block()
            self.skip_ws()
            elseb = self._read_else()
            return Parser(inner).parse_program(), elseb
        if re.match(r'if\b', self.text[self.i:], re.IGNORECASE):
            return [self.parse_if_adv()], None
        text = self._read_simple_line_from(self.i)
        return Parser(text).parse_program(), None

    def _read_else(self):
        self.skip_ws()
        if self.eof():
            return None
        if self.text[self.i:self.i + 4].lower() == 'else':
            self.i += 4
            self.skip_ws()
            if self.text[self.i] == '(':
                inner = self._read_block()
                return Parser(inner).parse_program()
            if re.match(r'if\b', self.text[self.i:], re.IGNORECASE):
                return [self.parse_if_adv()]
            text = self._read_simple_line_from(self.i)
            return Parser(text).parse_program()
        return None

    # for
    def parse_for_adv(self):
        self.i += 3  # skip 'for'
        self.skip_ws()
        flags = ''
        if self.text[self.i] == '/':
            j = self.i + 1
            while j < self.n and self.text[j] not in ' \t\r\n':
                j += 1
            flags = self.text[self.i + 1:j].lower()
            self.i = j
        self.skip_ws()
        opts = ''
        if self.i < self.n and self.text[self.i] == '"':
            qi = self.text.find('"', self.i + 1)
            if qi != -1:
                opts = self.text[self.i + 1:qi]
                self.i = qi + 1
            else:
                self.i = self.n
            self.skip_ws()
        vmm = re.match(r'%%?([A-Za-z])', self.text[self.i:])
        base_dir = ''
        if not vmm and 'r' in flags:
            pm = re.match(r'("[^"]*"|\S+)', self.text[self.i:])
            if pm and not pm.group(1).lower().startswith(('%', 'in')):
                j = self.i + pm.end()
                rest = self.text[j:j + 8].lstrip()
                if re.match(r'%%?[A-Za-z]', rest):
                    base_dir = pm.group(1)
                    self.i = j
                    self.skip_ws()
                    vmm = re.match(r'%%?([A-Za-z])', self.text[self.i:])
        if not vmm:
            text = self._read_simple_line_from(self.i - 3)
            return ('simple', text)
        var = vmm.group(1)
        self.i += vmm.end()
        self.skip_ws()
        if not self._match_word('in'):
            text = self._read_simple_line_from(self.i - 3)
            return ('simple', text)
        self.skip_ws()
        if self.text[self.i] != '(':
            text = self._read_simple_line_from(self.i - 3)
            return ('simple', text)
        list_inner = self._read_block()
        self.skip_ws()
        if self._match_word('do'):
            self.skip_ws()
        if self.text[self.i] == '(':
            body_inner = self._read_block()
            body = Parser(body_inner).parse_program()
        else:
            text = self._read_simple_line_from(self.i)
            node = self.parse_one(text.strip())
            body = [node] if node else []
        return ('for', dict(flags=flags, var=var, inner=list_inner, body=body,
                            opts=opts, base_dir=base_dir))
