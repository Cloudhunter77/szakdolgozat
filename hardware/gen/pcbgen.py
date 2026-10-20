"""NYÁK-előkészítés (D73): board-fájl a netlistából – körvonal, rétegek, footprintek a hálózatokkal, kezdő elhelyezés.

Futtatás (a KiCad Flatpak Pythonjával, a pcbnew modul miatt):
    flatpak run --command=python3 org.kicad.KiCad hardware/gen/pcbgen.py <lap> [--force]

- A footprintek a kapcsolási rajz szimbólumaihoz kötve (KIID-útvonal) → később a KiCad „Update PCB from Schematic” működik.
- A csatlakozók a DIN-ház szerinti élre kerülnek és arra néznek; a többi alkatrész a hozzá kötött IC köré (a közös,
  nem tápjellegű hálózatok alapján), az IC régiójába. Huzalozás nincs – azt Balázs csinálja.
- D67 mintájára: amint a .kicad_pcb-t kézzel szerkesztjük, az a forrás; a szkript csak --force-szal írja felül.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import sx
import pcbnew

H = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
SYS = '/app/extensions/Library/footprints'
OX, OY = 100.0, 100.0          # a NYÁK bal felső sarka a lapon (mm)
GAP = 0.5                      # minimális távolság két courtyard között (mm)
EDGE = 0.5                     # courtyard – NYÁK-él
POWER = {'GND', '+3V3', '+5V', '+3V3A', '+24V_P', '+24V_IN', '+24V_F', '+24V_RAIL', 'VIN_BUCK', '+5V_BUCK', 'VUSB',
         '+3V3S', '+12V', 'PGND_SH', 'ETH_CGND', '+3V3_LORA', 'V_BUS'}

# ---------------------------------------------------------------------------------------------------------------
# Lapok: méret, DIN-zónák, rögzített (él menti) alkatrészek, csoport-régiók
#   fixed:  ref -> (x, y, él)  – a courtyard középpontja a NYÁK-on (mm, bal felső sarok = 0,0); él: 'N','S','W','E'
#           (a csatlakozó nyílása / vezeték-bevezetése erre néz) vagy None (csak forgatás nélkül)
#   anchors: ref -> régió (x0, y0, x1, y1) – az IC és a hozzá rendelt kis alkatrészek ide kerülnek
# ---------------------------------------------------------------------------------------------------------------
W4, L = 68.0, 86.5
SH = 20.75                      # vállmélység: (86,5 − 45) / 2 – az előlapi ablak 45 mm (DIN 43880)
TOP, FRONT, BOT = (0, 0, W4, SH), (0, SH, W4, L - SH), (0, L - SH, W4, L)

BOARDS = {
    'rele-modul': dict(
        size=(W4, L),
        fixed={'J100': (6, 6, 'N'), 'J2': (22, 4.5, None), 'J3': (36, 4.5, None), 'JP1': (46, 4, None),
               'K1': (8.5, 58, 'coilN'), 'K2': (25, 58, 'coilN'), 'K3': (41.5, 58, 'coilN'), 'K4': (58, 58, 'coilN'),
               'J101': (8.5, 79.8, 'S'), 'J102': (25, 79.8, 'S'), 'J103': (41.5, 79.8, 'S'), 'J104': (58, 79.8, 'S'),
               'J105': (59, 7.5, 'N')},
        anchors={'U6': (12, 10, 52, 40), 'U101': (40, 10, 68, 42), 'U2': (14, 8, 44, 22), 'F100': (0, 10, 20, 40)},
        hv=(0, 43, W4, L),       # 230 V-os tartomány: ide csak a relék érintkezői és a sorkapcsok kerülhetnek
    ),
    'vezerlo': dict(
        size=(W4, L),
        fixed={'J1': (5.5, 6, 'N'), 'J2': (19, 4.5, None), 'J3': (33, 4.5, None), 'JP1': (44.5, 4, None),
               'U4': (58, 16, 'antN'), 'J6': (20, 76, 'S'), 'J4': (42, 82, 'S'), 'U10': (8.5, 40, None),
               'J7': (3, 26, None), 'J8': (55, 82.5, 'S'), 'SW1': (51, 70, None), 'SW2': (61.5, 70, None)},
        anchors={'U1': (0, 10, 30, 35), 'U2': (14, 10, 46, 32), 'U12': (30, 22, 50, 34), 'U3': (24, 10, 48, 24),
                 'U5': (14, 46, 50, 68), 'U6': (28, 8, 50, 24), 'U9': (46, 30, 68, 68), 'U8': (30, 62, 56, 80),
                 'U11': (0, 28, 20, 56)},
        keepout=[(46, 0, W4, 8)],   # a C6 antennája előtt/mellett ne legyen réz (a modul maga ide lóg)
    ),
    'led-modul': dict(
        size=(W4, L),
        # teljesítményút fentről lefelé: J201 → F201 → Q201 (ideális dióda) → +24V_RAIL → F202–F204 → J202–J204;
        # a FET-ek drain-füle a kimenet felé, a szabadonfutó diódák és a blokk-biztosítékok a sorkapcsok fölött
        fixed={'J201': (7, 6.5, 'N'), 'J2': (24, 4.5, None), 'J3': (38, 4.5, None), 'JP1': (47.5, 4, None),
               'Q201': (60, 5.5, None), 'F201': (9.5, 17, None), 'C203': (61, 19, None),
               'Q202': (5.5, 59, 'tabS'), 'Q203': (16.5, 59, 'tabS'), 'Q204': (28.5, 59, 'tabS'),
               'Q205': (39.5, 59, 'tabS'), 'Q206': (51.5, 59, 'tabS'), 'Q207': (62.5, 59, 'tabS'),
               'D211': (4, 69.3, 90), 'F202': (11, 69.3, None), 'D212': (18, 69.3, 90),
               'D213': (27, 69.3, 90), 'F203': (34, 69.3, None), 'D214': (41, 69.3, 90),
               'D215': (50, 69.3, 90), 'F204': (57, 69.3, None), 'D216': (64, 69.3, 90),
               'J202': (11, 79.8, 'S'), 'J203': (34, 79.8, 'S'), 'J204': (57, 79.8, 'S'),
               'R209': (22.5, 49.5, None)},
        anchors={'U6': (14, 21, 54, 42), 'U204': (50, 0, 68, 14), 'U2': (18, 9, 50, 21),
                 'U201': (0, 43, 18, 54), 'U202': (26, 43, 44, 54), 'U203': (48, 43, 68, 54),
                 'U206': (14, 40, 34, 54), 'U205': (0, 22, 14, 44)},
    ),
    'bemeneti-modul': dict(
        size=(103.0, L),
        fixed={'J2': (8, 4.5, None), 'J3': (22, 4.5, None), 'JP1': (32, 4, None),
               'U302': (99.5, 43, None)},        # HDC3020 a jobb szélen, a melegedő részektől távol (D66)
        anchors={'U6': (30, 25, 75, 60), 'U2': (0, 10, 40, 24), 'U301': (40, 10, 70, 24)},
        edge_rows={'N': (36, 103, ['J3%02d' % i for i in range(1, 7)] + ['J320']),          # felső váll: PH-k
                   'S': (0, 103, ['J3%02d' % i for i in range(7, 17)])},                   # alsó váll
    ),
}


# ---------------------------------------------------------------------------------------------------------------
def load_fp(fpid):
    lib, name = fpid.split(':', 1)
    path = os.path.join(H, 'lib', 'modularis.pretty') if lib == 'modularis' else f'{SYS}/{lib}.pretty'
    fp = pcbnew.FootprintLoad(path, name)
    if fp is None:
        raise SystemExit(f'nincs footprint: {fpid}')
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    return fp


def mm(v):
    return pcbnew.FromMM(v)


def bbox_mm(fp):
    """courtyard-befoglaló (x0, y0, x1, y1) mm-ben, a lap koordinátáiban"""
    cy = fp.GetCourtyard(pcbnew.F_CrtYd)
    bb = cy.BBox() if cy.OutlineCount() else fp.GetBoundingBox(False)
    return (pcbnew.ToMM(bb.GetX()), pcbnew.ToMM(bb.GetY()),
            pcbnew.ToMM(bb.GetX() + bb.GetWidth()), pcbnew.ToMM(bb.GetY() + bb.GetHeight()))


def pads_centroid(fp, names=None):
    ps = [p for p in fp.Pads() if names is None or p.GetNumber() in names]
    if not ps:
        ps = list(fp.Pads())
    return (sum(pcbnew.ToMM(p.GetPosition().x) for p in ps) / len(ps),
            sum(pcbnew.ToMM(p.GetPosition().y) for p in ps) / len(ps))


def center_at(fp, cx, cy):
    """a courtyard középpontját (cx, cy)-ba (NYÁK-koordináta) teszi"""
    x0, y0, x1, y1 = bbox_mm(fp)
    pos = fp.GetPosition()
    fp.SetPosition(pcbnew.VECTOR2I(pos.x + mm(OX + cx - (x0 + x1) / 2), pos.y + mm(OY + cy - (y0 + y1) / 2)))


DIRV = {'N': (0, -1), 'S': (0, 1), 'W': (-1, 0), 'E': (1, 0)}


def orient(fp, mode):
    """forgatás úgy, hogy a csatlakozó nyílása / a vezeték-bevezetés (a courtyard a padokhoz képest) az él felé nézzen;
    'coilN': relé – a tekercs-lábak (A1/A2) felül; 'antN': ESP-modul – az antenna (a padok nélküli vég) felül"""
    if mode is None:
        return
    if isinstance(mode, (int, float)):
        fp.SetOrientationDegrees(mode)
        return
    best = None
    for rot in (0, 90, 180, 270):
        fp.SetOrientationDegrees(rot)
        x0, y0, x1, y1 = bbox_mm(fp)
        bc = ((x0 + x1) / 2, (y0 + y1) / 2)
        if mode == 'tabS':
            big = max(fp.Pads(), key=lambda p: p.GetSizeX() * p.GetSizeY())
            pc = (pcbnew.ToMM(big.GetPosition().x), pcbnew.ToMM(big.GetPosition().y))
            v, d = (pc[0] - bc[0], pc[1] - bc[1]), (0, 1)
        elif mode == 'coilN':
            pc = pads_centroid(fp, {'A1', 'A2'})
            v, d = (pc[0] - bc[0], pc[1] - bc[1]), (0, -1)
        elif mode == 'antN':
            pc = pads_centroid(fp)
            v, d = (bc[0] - pc[0], bc[1] - pc[1]), (0, -1)
        else:
            pc = pads_centroid(fp)
            v, d = (bc[0] - pc[0], bc[1] - pc[1]), DIRV[mode]
        score = v[0] * d[0] + v[1] * d[1]
        if best is None or score > best[0]:
            best = (score, rot)
    fp.SetOrientationDegrees(best[1])


def overlaps(r, rects):
    for q in rects:
        if r[0] < q[2] + GAP and r[2] + GAP > q[0] and r[1] < q[3] + GAP and r[3] + GAP > q[1]:
            return True
    return False


def try_place(fp, region, near, rects, size, forbid):
    """a régióban a `near` ponthoz legközelebbi szabad helyre (0,5 mm-es rács, 0°/90°)"""
    W, Hh = size
    best = None
    for rot in (0, 90):
        fp.SetOrientationDegrees(rot)
        x0, y0, x1, y1 = bbox_mm(fp)
        w, h = x1 - x0, y1 - y0
        rx0, ry0 = max(region[0], EDGE) + w / 2, max(region[1], EDGE) + h / 2
        rx1, ry1 = min(region[2], W - EDGE) - w / 2, min(region[3], Hh - EDGE) - h / 2
        if rx1 < rx0 or ry1 < ry0:
            continue
        cands = []
        x = rx0
        while x <= rx1 + 1e-6:
            y = ry0
            while y <= ry1 + 1e-6:
                cands.append(((x - near[0]) ** 2 + (y - near[1]) ** 2, x, y))
                y += 0.5
            x += 0.5
        cands.sort()
        for d, x, y in cands:
            if best and d >= best[0]:
                break
            r = (x - w / 2, y - h / 2, x + w / 2, y + h / 2)
            if not overlaps(r, rects) and not overlaps(r, forbid):
                best = (d, rot, x, y, r)
                break
    if not best:
        return None
    _, rot, x, y, r = best
    fp.SetOrientationDegrees(rot)
    center_at(fp, x, y)
    return r


def netlist(board):
    n = sx.parse(open(os.path.join(H, 'out', f'{board}.net')).read())
    comps = {}
    for c in sx.find(sx.first(n, 'components'), 'comp'):
        ref = sx.first(c, 'ref')[1]
        f = sx.first(c, 'footprint')
        sp = sx.first(sx.first(c, 'sheetpath'), 'tstamps')[1]
        comps[ref] = dict(fp=f[1] if f else None, value=sx.first(c, 'value')[1],
                          path=sp.rstrip('/') + '/' + sx.first(c, 'tstamps')[1])
    nets = {}
    for net in sx.find(sx.first(n, 'nets'), 'net'):
        nets[sx.first(net, 'name')[1]] = [(sx.first(x, 'ref')[1], sx.first(x, 'pin')[1]) for x in sx.find(net, 'node')]
    return comps, nets


def groups(comps, nets, anchors, fixed):
    """minden nem rögzített alkatrész ahhoz a horgonyhoz (IC) tartozik, amellyel a legtöbb nem-táp hálózata közös;
    ami közvetlenül nem kapcsolódik, az a szomszédja csoportjába kerül"""
    adj = {r: {} for r in comps}
    for name, nodes in nets.items():
        if name.split('/')[-1] in POWER or name in POWER or len(nodes) > 12:
            continue
        refs = {r for r, _ in nodes}
        for a in refs:
            for b in refs:
                if a != b:
                    adj[a][b] = adj[a].get(b, 0) + 1
    grp = {a: a for a in anchors}
    for r in fixed:
        grp[r] = None
    todo = [r for r in comps if r not in grp and comps[r]['fp']]
    for _ in range(6):
        left = []
        for r in todo:
            sc = {}
            for b, w in adj[r].items():
                g = grp.get(b)
                if g:
                    sc[g] = sc.get(g, 0) + w * (3 if b in anchors else 1)
            if sc:
                grp[r] = max(sc, key=sc.get)
            else:
                left.append(r)
        todo = left
    for r in todo:
        grp[r] = '_misc'
    return grp


def main():
    board = sys.argv[1]
    cfg = BOARDS[board]
    W, Hh = cfg['size']
    out = os.path.join(H, board, f'{board}.kicad_pcb')
    if os.path.exists(out) and '--force' not in sys.argv:
        raise SystemExit(f'{out} már létezik – kézi szerkesztés után az a forrás (D67); felülírás: --force')
    comps, nets = netlist(board)
    b = pcbnew.BOARD()
    b.SetCopperLayerCount(4)
    ds = b.GetDesignSettings()
    nc = ds.m_NetSettings.GetDefaultNetclass()
    nc.SetClearance(mm(0.15)); nc.SetTrackWidth(mm(0.2)); nc.SetViaDiameter(mm(0.6)); nc.SetViaDrill(mm(0.3))
    ds.m_TrackMinWidth = mm(0.127); ds.m_MinClearance = mm(0.127); ds.m_ViasMinSize = mm(0.45); ds.m_MinThroughDrill = mm(0.2)   # JLC 4 réteg: 0,2 mm (a TPS2595 hűtőpadjának viái)
    # körvonal
    rect = pcbnew.PCB_SHAPE(b, pcbnew.SHAPE_T_RECTANGLE)
    rect.SetStart(pcbnew.VECTOR2I(mm(OX), mm(OY))); rect.SetEnd(pcbnew.VECTOR2I(mm(OX + W), mm(OY + Hh)))
    rect.SetLayer(pcbnew.Edge_Cuts); rect.SetWidth(mm(0.1)); b.Add(rect)

    def guide(x0, y0, x1, y1, text, layer=pcbnew.Dwgs_User):
        s = pcbnew.PCB_SHAPE(b, pcbnew.SHAPE_T_RECTANGLE)
        s.SetStart(pcbnew.VECTOR2I(mm(OX + x0), mm(OY + y0))); s.SetEnd(pcbnew.VECTOR2I(mm(OX + x1), mm(OY + y1)))
        s.SetLayer(layer); s.SetWidth(mm(0.15)); b.Add(s)
        t = pcbnew.PCB_TEXT(b); t.SetText(text); t.SetLayer(layer)
        t.SetPosition(pcbnew.VECTOR2I(mm(OX + (x0 + x1) / 2), mm(OY + y0 + 1.5))); t.SetTextSize(pcbnew.VECTOR2I(mm(1), mm(1)))
        b.Add(t)

    guide(0, 0, W, SH, 'FELSŐ VÁLL (sorkapcsok, busz)')
    guide(0, Hh - SH, W, Hh, 'ALSÓ VÁLL (terepi csatlakozók)')
    guide(0, SH, W, Hh - SH, 'ELŐLAPI ABLAK (45 mm) – LED-ek fényvezetővel')
    forbid = []
    for k in cfg.get('keepout', []):
        guide(*k, 'ANTENNA – réz nélkül', pcbnew.Cmts_User)
        forbid.append(k)
    if 'hv' in cfg:
        guide(*cfg['hv'], '230 V – ≥ 8 mm a törpefeszültségtől', pcbnew.Cmts_User)
    # hálózatok
    ni = {}
    for name in nets:
        n_ = pcbnew.NETINFO_ITEM(b, name); b.Add(n_); ni[name] = n_
    padnet = {}
    for name, nodes in nets.items():
        for r, p in nodes:
            padnet[(r, p)] = ni[name]
    # footprintek
    fps = {}
    for ref, c in sorted(comps.items()):
        if not c['fp']:
            continue
        fp = load_fp(c['fp'])
        fp.SetReference(ref); fp.SetValue(c['value'])
        fp.SetPath(pcbnew.KIID_PATH(c['path']))
        for p in fp.Pads():
            n_ = padnet.get((ref, p.GetNumber()))
            if n_:
                p.SetNet(n_)
        b.Add(fp)
        fps[ref] = fp
    rects, report, unplaced = [], [], []
    fixed = {r: v for r, v in cfg['fixed'].items() if r in fps}
    # él menti PH-sorok (bemeneti modul)
    for edge, (xa, xb, refs) in cfg.get('edge_rows', {}).items():
        refs = [r for r in refs if r in fps]
        ws = []
        for r in refs:
            orient(fps[r], edge)
            q = bbox_mm(fps[r])
            ws.append(q[2] - q[0])
        gap = (xb - xa - sum(ws)) / (len(refs) + 1)          # egyenletes hézag a valódi szélességekkel
        x = xa + gap
        for r, w_ in zip(refs, ws):
            fixed[r] = (x + w_ / 2, 4.5 if edge == 'N' else Hh - 4.5, edge)
            x += w_ + gap
    for ref, (x, y, mode) in fixed.items():
        fp = fps[ref]
        orient(fp, mode)
        center_at(fp, x, y)
        r = bbox_mm(fp)
        r = (r[0] - OX, r[1] - OY, r[2] - OX, r[3] - OY)
        if overlaps(r, rects):
            report.append(f'ÜTKÖZÉS (rögzített): {ref}')
        if r[0] < 0 or r[1] < 0 or r[2] > W or r[3] > Hh:
            report.append(f'LELÓG a NYÁK-ról (rögzített): {ref} {tuple(round(v, 1) for v in r)}')
        rects.append(r)
    anchors = {r: v for r, v in cfg['anchors'].items() if r in fps}
    grp = groups(comps, nets, anchors, fixed)
    hv = cfg.get('hv')
    lv_forbid = forbid + ([hv] if hv else [])
    # horgonyok a régiójuk közepére, aztán a csoportjuk köréjük (nagyobbak előbb)
    order = list(anchors)
    centers = {}
    for a in order:
        reg = anchors[a]
        near = ((reg[0] + reg[2]) / 2, (reg[1] + reg[3]) / 2)
        r = try_place(fps[a], reg, near, rects, (W, Hh), lv_forbid)
        if not r:
            r = try_place(fps[a], (0, 0, W, Hh), near, rects, (W, Hh), lv_forbid)
        if not r:
            unplaced.append(a); continue
        rects.append(r)
        centers[a] = ((r[0] + r[2]) / 2, (r[1] + r[3]) / 2)
    members = {}
    for r, g in grp.items():
        if g and r not in anchors and r not in fixed and r in fps:
            members.setdefault(g, []).append(r)
    for g, refs in members.items():
        refs.sort(key=lambda r: -((bbox_mm(fps[r])[2] - bbox_mm(fps[r])[0]) * (bbox_mm(fps[r])[3] - bbox_mm(fps[r])[1])))
        reg = anchors.get(g, (0, 0, W, Hh))
        near = centers.get(g, ((reg[0] + reg[2]) / 2, (reg[1] + reg[3]) / 2))
        for r in refs:
            # a 230 V-os tartományba csak a relé-érintkezőhöz tartozó elemek mehetnének – ide semmi más
            got = try_place(fps[r], reg, near, rects, (W, Hh), lv_forbid) or \
                try_place(fps[r], (0, 0, W, Hh), near, rects, (W, Hh), lv_forbid)
            if got:
                rects.append(got)
            else:
                unplaced.append(r)
    # ami nem fért el: a NYÁK mellé, jól láthatóan
    for i, r in enumerate(unplaced):
        center_at(fps[r], W + 10 + (i % 4) * 9, 5 + (i // 4) * 9)
    pcbnew.SaveBoard(out, b)
    area = sum((q[2] - q[0]) * (q[3] - q[1]) for q in rects)
    print(f'{board}: {len(fps)} footprint, elhelyezve {len(fps) - len(unplaced)}, NEM FÉRT EL: {len(unplaced)} {unplaced}')
    print(f'  courtyard-kihasználtság: {area:.0f} / {W * Hh:.0f} mm² = {100 * area / (W * Hh):.0f} %')
    for line in report:
        print('  ' + line)
    print('  ->', out)


if __name__ == '__main__':
    main()
