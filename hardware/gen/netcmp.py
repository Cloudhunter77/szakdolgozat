"""Két KiCad-netlista összevetése: ugyanazok a lábak vannak-e összekötve (a hálózatnevektől függetlenül)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import sx


def groups(path):
    n = sx.parse(open(path).read())
    out = {}
    for net in sx.find(sx.first(n, 'nets'), 'net'):
        nodes = frozenset(sx.first(x, 'ref')[1] + '.' + sx.first(x, 'pin')[1] for x in sx.find(net, 'node'))
        out[nodes] = sx.first(net, 'name')[1]
    return out


a, b = groups(sys.argv[1]), groups(sys.argv[2])
only_a = [a[k] + ': ' + ' '.join(sorted(k)) for k in a if k not in b]
only_b = [b[k] + ': ' + ' '.join(sorted(k)) for k in b if k not in a]
print(f'{len(a)} / {len(b)} hálózat; csak a régiben: {len(only_a)}, csak az újban: {len(only_b)}')
for l in only_a[:30]:
    print('  - ' + l[:200])
for l in only_b[:30]:
    print('  + ' + l[:200])
