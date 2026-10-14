"""Minimal S-expression reader/writer for KiCad files."""
import re

class Sym(str):
    pass

_tok = re.compile(r'\s*(\(|\)|"(?:\\.|[^"\\])*"|[^\s()"]+)', re.S)

def parse(text):
    pos = 0
    stack = [[]]
    for m in _tok.finditer(text):
        t = m.group(1)
        if t == '(':
            stack.append([])
        elif t == ')':
            x = stack.pop()
            stack[-1].append(x)
        elif t.startswith('"'):
            stack[-1].append(bytes(t[1:-1], 'utf-8').decode('unicode_escape').encode('latin-1').decode('utf-8') if '\\' in t else t[1:-1])
        else:
            stack[-1].append(Sym(t))
    return stack[0][0]

def q(s):
    return '"' + str(s).replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'

def dump(x, ind=0):
    if isinstance(x, list):
        simple = all(not isinstance(e, list) for e in x)
        if simple:
            return '(' + ' '.join(dump(e) for e in x) + ')'
        out = '(' + ' '.join(dump(e) for e in x if not isinstance(e, list))
        for e in x:
            if isinstance(e, list):
                out += '\n' + '\t' * (ind + 1) + dump(e, ind + 1)
        return out + '\n' + '\t' * ind + ')'
    if isinstance(x, Sym):
        return str(x)
    if isinstance(x, (int, float)):
        return fmt(x)
    return q(x)

def fmt(v):
    if isinstance(v, float):
        s = ('%.4f' % v).rstrip('0').rstrip('.')
        return '0' if s == '-0' else s
    return str(v)

def find(x, key):
    return [e for e in x if isinstance(e, list) and e and e[0] == key]

def first(x, key):
    r = find(x, key)
    return r[0] if r else None
