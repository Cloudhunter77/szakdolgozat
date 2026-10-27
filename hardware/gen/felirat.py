# Szitanyomat-feliratok (Reference) elrendezése egy kész/félkész NYÁK-on – Claude, 2026-10-23 (először a LED-modulon).
#   flatpak run --command=python3 org.kicad.KiCad gen/felirat.py <be.kicad_pcb> <ki.kicad_pcb> [--csak R1,C2,…]
# Csak a feliratokhoz nyúl (hely, 0°/90°, méret 1,0 vagy – ha máshogy nem fér el – 0,8 mm); a nyitott KiCad-ben utána
# File → Revert. Futásidő ~2 perc. Ellenőrzés: DRC – silk_over_copper 0, silk_overlap csak néhány figyelmeztetés.
# Minden jelölés a saját alkatrésze mellé kerül (0° vagy 90°, olvasható irányban), és nem lóghat padra, viára, furatra,
# nagyáramú (fedetlen, D82) sávra és maszknyitásra (gen/maszknyitas.py), a lapszélre és más feliratra; büntetett: más alkatrész szitanyomata / udvara,
# a saját körvonal, a távolság és ha a felirat egy másik alkatrészhez közelebb van, mint a sajátjához.
import sys, math
import numpy as np
import pcbnew

mm = pcbnew.ToMM
def FM(v): return pcbnew.FromMM(float(v))
RES = 0.05                      # rács (mm)
GAP = 0.45  # két felirat között legalább ennyi (különben összeolvadnak: „D233D224”)

be, ki = sys.argv[1], sys.argv[2]
# --csak R1,R2,…: csak ezek feliratához nyúl, a többi felirat a mostani helyén marad (akadály) – kézzel igazított lapon
CSAK = set(sys.argv[sys.argv.index('--csak') + 1].split(',')) if '--csak' in sys.argv else None
b = pcbnew.LoadBoard(be)
eb = b.GetBoardEdgesBoundingBox()
OX, OY, W, H = mm(eb.GetX()), mm(eb.GetY()), mm(eb.GetWidth()), mm(eb.GetHeight())
NX, NY = int(math.ceil(W / RES)) + 1, int(math.ceil(H / RES)) + 1
fps = list(b.GetFootprints())
# nagyáramú hálózat = van rajta ≥ 1 mm-es sáv a felső rétegen (D82: ezek fedetlenek lesznek, a felirat elveszne rajtuk)
NAGYARAM = {t.GetNetname() for t in b.GetTracks()
            if t.Type() != pcbnew.PCB_VIA_T and t.GetLayer() == pcbnew.F_Cu and mm(t.GetWidth()) >= 1.0}


def cell(x, y):
    return (x - OX) / RES, (y - OY) / RES


def mark_rect(m, x0, y0, x1, y1, val=1, add=False):
    i0, j0 = cell(x0, y0); i1, j1 = cell(x1, y1)
    i0, j0 = max(0, int(math.floor(i0))), max(0, int(math.floor(j0)))
    i1, j1 = min(NX, int(math.ceil(i1))), min(NY, int(math.ceil(j1)))
    if i1 <= i0 or j1 <= j0:
        return
    if add:
        m[j0:j1, i0:i1] += val
    else:
        m[j0:j1, i0:i1] = val


def mark_seg(m, x0, y0, x1, y1, r, val=1, add=False):
    lo_x, hi_x = min(x0, x1) - r, max(x0, x1) + r
    lo_y, hi_y = min(y0, y1) - r, max(y0, y1) + r
    i0, j0 = cell(lo_x, lo_y); i1, j1 = cell(hi_x, hi_y)
    i0, j0 = max(0, int(math.floor(i0))), max(0, int(math.floor(j0)))
    i1, j1 = min(NX, int(math.ceil(i1)) + 1), min(NY, int(math.ceil(j1)) + 1)
    if i1 <= i0 or j1 <= j0:
        return
    xs = OX + (np.arange(i0, i1) + 0.5) * RES
    ys = OY + (np.arange(j0, j1) + 0.5) * RES
    X, Y = np.meshgrid(xs, ys)
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy
    t = np.zeros_like(X) if L2 == 0 else np.clip(((X - x0) * dx + (Y - y0) * dy) / L2, 0, 1)
    d = np.hypot(X - (x0 + t * dx), Y - (y0 + t * dy))
    sel = d <= r
    if add:
        m[j0:j1, i0:i1][sel] += val
    else:
        m[j0:j1, i0:i1][sel] = val


def mark_poly(m, pts, r):
    """Kitöltött sokszög (csúcsok mm-ben) + r mm-es szegély."""
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    i0, j0 = cell(min(xs), min(ys)); i1, j1 = cell(max(xs), max(ys))
    i0, j0 = max(0, int(math.floor(i0))), max(0, int(math.floor(j0)))
    i1, j1 = min(NX, int(math.ceil(i1)) + 1), min(NY, int(math.ceil(j1)) + 1)
    if i1 > i0 and j1 > j0:
        X, Y = np.meshgrid(OX + (np.arange(i0, i1) + 0.5) * RES, OY + (np.arange(j0, j1) + 0.5) * RES)
        bent = np.zeros(X.shape, bool)
        for k in range(len(pts)):          # páros-páratlan szabály
            (xa, ya), (xb, yb) = pts[k], pts[(k + 1) % len(pts)]
            if ya == yb:
                continue
            bent ^= ((ya > Y) != (yb > Y)) & (X < xa + (Y - ya) * (xb - xa) / (yb - ya))
        m[j0:j1, i0:i1][bent] = 1
    for k in range(len(pts)):
        mark_seg(m, *pts[k], *pts[(k + 1) % len(pts)], r)


def bbox_mm(bb):
    return mm(bb.GetX()), mm(bb.GetY()), mm(bb.GetRight()), mm(bb.GetBottom())


def silk_segments(items):
    """Szitanyomat-rajzok (egy footprinté a felirat nélkül, vagy a lapra rajzoltak) szakaszokként, mm-ben."""
    segs = []
    for g in items:
        if g.GetLayer() != pcbnew.F_SilkS or g.Type() != pcbnew.PCB_SHAPE_T:
            continue
        ps = pcbnew.SHAPE_POLY_SET()
        g.TransformShapeToPolygon(ps, pcbnew.F_SilkS, 0, FM(0.01), pcbnew.ERROR_INSIDE)
        for k in range(ps.OutlineCount()):
            o = ps.Outline(k)
            pts = [(mm(o.CPoint(i).x), mm(o.CPoint(i).y)) for i in range(o.PointCount())]
            bx0, by0 = min(p[0] for p in pts), min(p[1] for p in pts)
            bx1, by1 = max(p[0] for p in pts), max(p[1] for p in pts)
            if (bx1 - bx0) * (by1 - by0) < 1.0 and (g.IsSolidFill() if hasattr(g, 'IsSolidFill') else g.IsFilled()):
                segs.append(('rect', bx0, by0, bx1, by1))
            for i in range(len(pts)):
                segs.append(('seg',) + pts[i] + pts[(i + 1) % len(pts)])
    return segs


def courtyard(f):
    f.BuildCourtyardCaches()
    c = f.GetCourtyard(pcbnew.F_CrtYd)
    if c.OutlineCount() == 0:
        return bbox_mm(f.GetBoundingBox(False))
    return bbox_mm(c.BBox())


def pad_box(f):
    xs = [bbox_mm(p.GetBoundingBox()) for p in f.Pads()]
    return min(a[0] for a in xs), min(a[1] for a in xs), max(a[2] for a in xs), max(a[3] for a in xs)


def rect_gap(a, c):
    dx = max(c[0] - a[2], a[0] - c[2], 0); dy = max(c[1] - a[3], a[1] - c[3], 0)
    return math.hypot(dx, dy)


# ---------------------------------------------------------------- akadálytérképek
HARD = np.zeros((NY, NX), np.int32)
SILK = np.zeros((NY, NX), np.int32)       # szitanyomat-rajzok (minden footprint), darabszám
CRT = np.zeros((NY, NX), np.int32)        # udvarok, darabszám
LAB = np.zeros((NY, NX), np.int32)        # már elhelyezett feliratok (+GAP)
BIG = np.zeros((NY, NX), np.int32)        # a nagy (≥ 20 mm²) alkatrészek udvara

m = 0.35                                   # lapszél
HARD[:, :int(m / RES) + 1] = 1; HARD[:, NX - int(m / RES) - 1:] = 1
HARD[:int(m / RES) + 1, :] = 1; HARD[NY - int(m / RES) - 1:, :] = 1
for f in fps:
    for p in f.Pads():
        x0, y0, x1, y1 = bbox_mm(p.GetBoundingBox())
        mark_rect(HARD, x0 - 0.15, y0 - 0.15, x1 + 0.15, y1 + 0.15)
for t in b.GetTracks():
    if t.Type() == pcbnew.PCB_VIA_T:
        x0, y0, x1, y1 = bbox_mm(t.GetBoundingBox())
        mark_rect(HARD, x0 - 0.1, y0 - 0.1, x1 + 0.1, y1 + 0.1)
    elif t.GetNetname() in NAGYARAM and t.GetLayer() == pcbnew.F_Cu and mm(t.GetWidth()) >= 1.0:   # a vékony mérőág fedett
        mark_seg(HARD, mm(t.GetStart().x), mm(t.GetStart().y), mm(t.GetEnd().x), mm(t.GetEnd().y), mm(t.GetWidth()) / 2 + 0.15)
for z in b.Zones():
    if z.IsOnLayer(pcbnew.F_Cu) and not z.GetIsRuleArea() and z.GetNetname() in NAGYARAM:
        mark_rect(HARD, *bbox_mm(z.GetBoundingBox()))

for g in b.GetDrawings():   # forrasztásgátló-nyitás (D82, gen/maszknyitas.py): a felirat elveszne rajta
    if g.GetLayer() == pcbnew.F_Mask and g.Type() == pcbnew.PCB_SHAPE_T and g.GetShape() == pcbnew.SHAPE_T_POLY:
        ps = g.GetPolyShape()
        for k in range(ps.OutlineCount()):
            o = ps.Outline(k)
            mark_poly(HARD, [(mm(o.CPoint(i).x), mm(o.CPoint(i).y)) for i in range(o.PointCount())], 0.15)

own_silk = {}
for i, f in enumerate(fps):
    segs = silk_segments(f.GraphicalItems())
    own_silk[i] = segs
    for s in segs:
        if s[0] == 'rect':
            mark_rect(SILK, s[1] - 0.1, s[2] - 0.1, s[3] + 0.1, s[4] + 0.1, add=True)
        else:
            mark_seg(SILK, s[1], s[2], s[3], s[4], 0.12, add=True)
    c = courtyard(f)
    mark_rect(CRT, *c, add=True)
    if (c[2] - c[0]) * (c[3] - c[1]) >= 20:
        mark_rect(BIG, *c, add=True)
for s in silk_segments(b.GetDrawings()):   # a lapra rajzolt szitanyomat (pl. keret) is akadály
    if s[0] == 'seg':
        mark_seg(SILK, s[1], s[2], s[3], s[4], 0.12, add=True)


def integral(a):
    s = np.zeros((a.shape[0] + 1, a.shape[1] + 1), np.int64)
    s[1:, 1:] = a.cumsum(0).cumsum(1)
    return s


I_HARD, I_SILK, I_CRT, I_BIG = integral(HARD), integral(SILK), integral(CRT), integral(BIG)
I_LAB = integral(LAB)
AREA = RES * RES

# ---------------------------------------------------------------- feliratok mérete (tinta-befoglaló)
info, eredeti = {}, {}
for i, f in enumerate(fps):
    r = f.Reference()
    if not r.IsVisible() or r.GetLayer() != pcbnew.F_SilkS:
        continue
    if CSAK is not None and f.GetReference() not in CSAK:
        mark_rect(LAB, *(v + dv for v, dv in zip(bbox_mm(r.GetEffectiveTextShape().BBox()), (-GAP, -GAP, GAP, GAP))), add=True)
        continue
    d = {}
    eredeti[i] = (r.GetPosition(), r.GetTextAngleDegrees(), r.GetTextSize(), r.GetTextThickness())
    for size in (1.0, 0.8):
        r.SetTextSize(pcbnew.VECTOR2I(FM(size), FM(size))); r.SetTextThickness(FM(0.15))
        for ang in (0, 90):
            r.SetTextAngleDegrees(ang)
            bb = r.GetEffectiveTextShape().BBox(); p = r.GetPosition()
            d[(size, ang)] = (mm(bb.GetWidth()), mm(bb.GetHeight()),
                              mm(bb.GetX()) + mm(bb.GetWidth()) / 2 - mm(p.x), mm(bb.GetY()) + mm(bb.GetHeight()) / 2 - mm(p.y))
    info[i] = d

I_LAB = integral(LAB)
pads = {i: pad_box(f) for i, f in enumerate(fps)}
crts = {i: courtyard(f) for i, f in enumerate(fps)}


def own_maps(i, j0, j1, i0, i1):
    s = np.zeros((j1 - j0, i1 - i0), np.int32); c = np.zeros_like(s)
    tmp = np.zeros((NY, NX), np.int32)
    for sg in own_silk[i]:
        if sg[0] == 'rect':
            mark_rect(tmp, sg[1] - 0.1, sg[2] - 0.1, sg[3] + 0.1, sg[4] + 0.1, add=True)
        else:
            mark_seg(tmp, sg[1], sg[2], sg[3], sg[4], 0.12, add=True)
    s = tmp[j0:j1, i0:i1].copy()
    tmp[:] = 0
    mark_rect(tmp, *crts[i], add=True)
    c = tmp[j0:j1, i0:i1].copy()
    return s, c


def boxsum(I, j0, i0, hc, wc, nj, ni, step):
    """Az I integrálképen a (hc × wc) cellás téglalap összege minden bal felső sarokra: j0 + k·step, i0 + l·step."""
    J = j0 + np.arange(nj) * step; Ii = i0 + np.arange(ni) * step
    JJ, II = np.meshgrid(J, Ii, indexing='ij')
    return I[JJ + hc, II + wc] - I[JJ, II + wc] - I[JJ + hc, II] + I[JJ, II]


STEP = 2   # 0,1 mm


def candidates(i, extra=0.0):
    """Az i. footprint összes jelölt helye: (költség, x, y, size, ang) – a legjobb néhány. extra: nagyobb keresési körzet."""
    px0, py0, px1, py1 = pads[i]
    R = 4.0 + extra + 0.15 * max(px1 - px0, py1 - py0)
    wx0, wy0, wx1, wy1 = px0 - R, py0 - R, px1 + R, py1 + R
    ci0, cj0 = cell(wx0, wy0); ci1, cj1 = cell(wx1, wy1)
    ci0, cj0 = max(0, int(ci0)), max(0, int(cj0)); ci1, cj1 = min(NX, int(ci1)), min(NY, int(cj1))
    os_, oc = own_maps(i, cj0, cj1, ci0, ci1)
    I_os, I_oc = integral(os_), integral(oc)
    others = [k for k in pads if k != i and rect_gap(pads[k], (wx0, wy0, wx1, wy1)) < 3]
    out = []
    for (size, ang), (tw, th, offx, offy) in info[i].items():
        wc, hc = int(math.ceil(tw / RES)), int(math.ceil(th / RES))
        ni, nj = (ci1 - ci0 - wc) // STEP, (cj1 - cj0 - hc) // STEP
        if ni <= 0 or nj <= 0:
            continue
        hard = boxsum(I_HARD, cj0, ci0, hc, wc, nj, ni, STEP)
        lab = boxsum(I_LAB, cj0, ci0, hc, wc, nj, ni, STEP)
        silk = boxsum(I_SILK, cj0, ci0, hc, wc, nj, ni, STEP)
        crt = boxsum(I_CRT, cj0, ci0, hc, wc, nj, ni, STEP)
        big = boxsum(I_BIG, cj0, ci0, hc, wc, nj, ni, STEP)
        osk = boxsum(I_os, 0, 0, hc, wc, nj, ni, STEP)
        ocr = boxsum(I_oc, 0, 0, hc, wc, nj, ni, STEP)
        # a téglalap bal felső sarka (mm) → középpont
        X0 = OX + (ci0 + np.arange(ni) * STEP) * RES; Y0 = OY + (cj0 + np.arange(nj) * STEP) * RES
        XX, YY = np.meshgrid(X0, Y0)
        x0, y0, x1, y1 = XX, YY, XX + wc * RES, YY + hc * RES
        def gap(bx):
            dx = np.maximum(np.maximum(bx[0] - x1, x0 - bx[2]), 0); dy = np.maximum(np.maximum(bx[1] - y1, y0 - bx[3]), 0)
            return np.hypot(dx, dy)
        g_own = gap(pads[i])
        g_oth = np.full_like(g_own, 99.0)
        for k in others:
            g_oth = np.minimum(g_oth, gap(pads[k]))
        bent = ocr * AREA / (tw * th)          # a felirat ekkora része a saját udvarán belül
        sajat_nagy = (crts[i][2] - crts[i][0]) * (crts[i][3] - crts[i][1]) >= 20
        cost = (25 * g_own + 60 * np.maximum(0, g_own - g_oth + 0.3) - 12 * np.minimum(bent, 1)
                + 6 * (crt - ocr) * AREA + 100 * osk * AREA + 25 * (big - (ocr if sajat_nagy else 0)) * AREA
                + np.where(silk - osk > 0, 200 + 100 * (silk - osk) * AREA, 0)
                + (45 if size < 1 else 0) + (2 if ang == 90 else 0))
        cost = np.where((hard > 0) | (lab > 0), np.inf, cost)
        k = np.argsort(cost, axis=None)[:3]
        for kk in k:
            c = cost.flat[kk]
            if not np.isfinite(c):
                continue
            cx = x0.flat[kk] + wc * RES / 2; cy = y0.flat[kk] + hc * RES / 2
            out.append((float(c), cx, cy, size, ang, (x0.flat[kk], y0.flat[kk], x1.flat[kk], y1.flat[kk]), int(np.isfinite(cost).sum())))
    out.sort()
    return out


def lab_mark(rect, val):
    global I_LAB
    mark_rect(LAB, rect[0] - GAP, rect[1] - GAP, rect[2] + GAP, rect[3] + GAP, val=val, add=True)
    I_LAB = integral(LAB)


# sorrend: a legkevesebb szabad hellyel rendelkező előbb
nfree = {}
for i in info:
    c = candidates(i)
    nfree[i] = c[0][6] if c else 0
order = sorted(info, key=lambda i: nfree[i])
place = {}
for rnd in range(3):
    for i in order:
        if i in place:
            lab_mark(place[i][5], -1)
        c = candidates(i)
        if c:
            place[i] = c[0]
            lab_mark(place[i][5], 1)
        elif i in place:
            lab_mark(place[i][5], 1)

# javítás: ami nem fért el, az előbb kerül le, a 6 mm-en belüli szomszédok utána újra
for i in [i for i in info if i not in place]:
    cx, cy = (pads[i][0] + pads[i][2]) / 2, (pads[i][1] + pads[i][3]) / 2
    szomsz = [k for k in place if math.hypot((pads[k][0] + pads[k][2]) / 2 - cx, (pads[k][1] + pads[k][3]) / 2 - cy) < 6]
    for k in szomsz:
        lab_mark(place.pop(k)[5], -1)
    for k in [i] + sorted(szomsz, key=lambda k: nfree[k]):
        c = candidates(k)
        if c:
            place[k] = c[0]; lab_mark(place[k][5], 1)

# helyi javítás: a legrosszabb feliratok és az 5 mm-en belüli szomszédaik újra, két sorrendben – ha jobb, marad
def kozep(k):
    return (pads[k][0] + pads[k][2]) / 2, (pads[k][1] + pads[k][3]) / 2


def lerak(sorrend):
    uj = {}
    for k in sorrend:
        c = candidates(k)
        if c:
            uj[k] = c[0]; lab_mark(c[0][5], 1)
    return uj, sum(uj[k][0] for k in uj) + 1000 * (len(sorrend) - len(uj))


for kuszob in (50, 80):
    for i in sorted(place, key=lambda k: -place[k][0]):
        if i not in place or place[i][0] < kuszob:
            continue
        ci = kozep(i)
        csop = [i] + [k for k in place if k != i and math.hypot(kozep(k)[0] - ci[0], kozep(k)[1] - ci[1]) < 5]
        regi = {k: place.pop(k) for k in csop}
        for k in csop:
            lab_mark(regi[k][5], -1)
        legjobb, lj_ar = regi, sum(v[0] for v in regi.values())
        for sorrend in ([i] + sorted(csop[1:], key=lambda k: nfree[k]), sorted(csop[1:], key=lambda k: nfree[k]) + [i]):
            uj, ar = lerak(sorrend)
            for k in uj:
                lab_mark(uj[k][5], -1)
            if ar < lj_ar - 1:
                legjobb, lj_ar = uj, ar
        for k, v in legjobb.items():
            place[k] = v; lab_mark(v[5], 1)

# ami így sem fért el: nagyobb körzetben (a távolság büntetése marad, így csak akkor megy messzebb, ha közelebb nincs hely)
tavol = []
for extra in (2.0, 4.0):
    for i in [i for i in info if i not in place]:
        c = candidates(i, extra)
        if c:
            place[i] = c[0]; lab_mark(c[0][5], 1); tavol.append(fps[i].GetReference())

nincs = [fps[i].GetReference() for i in info if i not in place]
kicsi = sorted(fps[i].GetReference() for i in place if place[i][3] < 1)
rossz = sorted(fps[i].GetReference() for i in place if place[i][0] >= 200)

for i, (c, cx, cy, size, ang, rect, _) in place.items():
    r = fps[i].Reference()
    r.SetTextSize(pcbnew.VECTOR2I(FM(size), FM(size))); r.SetTextThickness(FM(0.15))
    r.SetTextAngleDegrees(ang); r.SetKeepUpright(True)
    tw, th, offx, offy = info[i][(size, ang)]
    r.SetPosition(pcbnew.VECTOR2I(FM(cx - offx), FM(cy - offy)))
for i in info:
    if i not in place:   # vissza az eredeti méretre (a mérés átírta)
        r = fps[i].Reference(); p, a, sz, th = eredeti[i]
        r.SetTextSize(sz); r.SetTextThickness(th); r.SetTextAngleDegrees(a); r.SetPosition(p)

pcbnew.SaveBoard(ki, b)
print(f'feliratok: {len(place)} elhelyezve, {len(kicsi)} db 0,8 mm-es: {" ".join(kicsi)}')
print('más szitanyomatra lóg:', ' '.join(rossz) or '–')
print('messzebb került (6–8 mm-es körzet):', ' '.join(tavol) or '–')
print('nem fért el (régi hely):', ' '.join(nincs) or '–')
