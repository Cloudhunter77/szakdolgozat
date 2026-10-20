"""Alkatrész-terület becslés: a netlista minden footprintjének courtyard-befoglalója (mm²) laponként."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import sx, pcbnew
H = os.path.join(os.path.dirname(__file__), '..')
SYS = '/app/extensions/Library/footprints'


def load_fp(fpid):
    lib, name = fpid.split(':', 1)
    path = os.path.join(H, 'lib', 'modularis.pretty') if lib == 'modularis' else f'{SYS}/{lib}.pretty'
    return pcbnew.FootprintLoad(path, name)


def comps(board):
    n = sx.parse(open(os.path.join(H, 'out', f'{board}.net')).read())
    for c in sx.find(sx.first(n, 'components'), 'comp'):
        f = sx.first(c, 'footprint')
        dnp = any(p[1] == 'dnp' for p in sx.find(c, 'property') if len(p) > 1)
        yield sx.first(c, 'ref')[1], f[1] if f else None, dnp


for board in sys.argv[1:]:
    tot = tot_dnp = 0
    big = []
    for ref, fpid, dnp in comps(board):
        if not fpid:
            continue
        fp = load_fp(fpid)
        bb = fp.GetCourtyard(pcbnew.F_CrtYd).BBox() if fp.GetCourtyard(pcbnew.F_CrtYd).OutlineCount() else fp.GetBoundingBox(False)
        a = pcbnew.ToMM(bb.GetWidth()) * pcbnew.ToMM(bb.GetHeight())
        tot += a
        if dnp:
            tot_dnp += a
        big.append((a, ref, fpid.split(':')[1][:40]))
    big.sort(reverse=True)
    print(f'== {board}: {len(big)} footprint, courtyard-összeg {tot:.0f} mm² (ebből DNP {tot_dnp:.0f})')
    for a, r, f in big[:8]:
        print(f'   {r:6s} {a:6.0f} mm²  {f}')
