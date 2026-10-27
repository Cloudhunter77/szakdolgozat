# D82: forrasztásgátló-nyitás a nagyáramú sávokon és zónákon (ónnal / rézdróttal megvastagításhoz) – Claude, 2026-10-27.
#   flatpak run --command=python3 org.kicad.KiCad gen/maszknyitas.py <be.kicad_pcb> <ki.kicad_pcb> [--halok REGEX] [--sont R209]
# Nyitás = a nagyáramú hálózatok ≥ 1 mm-es sávjai és külső rétegű zónái, pontosan a réz körvonalán (a zóna-kitöltésből:
# előtte töltsd ki a zónákat). Felül levonja az alkatrészek udvarát (test alá nem kerül fedetlen réz) és a sönt környékét
# (a söntöt és a Kelvin-pontjait nem szabad ónnal áthidalni); a 0,4 mm-nél keskenyebb maradékot és az 1 mm² alatti
# darabokat elhagyja. Az eredmény zárolt kitöltött sokszög az F.Mask / B.Mask rétegen, a „D82 maszknyitás” csoportban –
# újrafuttatva előbb a régi csoportot törli, így huzalozás-módosítás után egyszerűen újra lehet generálni.
import re
import sys
import pcbnew

mm = pcbnew.ToMM
def FM(v): return pcbnew.FromMM(float(v))
ERR = FM(0.005)
CS = pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS
CSOPORT = 'D82 maszknyitás'

be, ki = sys.argv[1], sys.argv[2]
def opt(nev, alap): return sys.argv[sys.argv.index(nev) + 1] if nev in sys.argv else alap
# LED-modul (D82): +24 V-os út, csatorna-drainek, visszatérő út (PGND_SH → sönt → GND → Q201 → GND_IN)
HALOK = re.compile(opt('--halok', r'^(/?\+24V_(IN|RAIL|B\d)|/CH\d_D|/?PGND_SH|/GND_IN|GND)$'))
SONT, SONT_TAV = opt('--sont', 'R209'), 1.5          # a sönt udvara + ennyi mm fedett marad
UDVAR_TAV, MIN_SZEL, MIN_TER = 0.1, 0.4, 1.0         # mm, mm, mm²

b = pcbnew.LoadBoard(be)
for g in list(b.Groups()):
    if g.GetName() == CSOPORT:
        for it in list(g.GetItems()):
            b.Delete(it)
        b.Delete(g)

nyitas = {pcbnew.F_Cu: pcbnew.SHAPE_POLY_SET(), pcbnew.B_Cu: pcbnew.SHAPE_POLY_SET()}
for t in b.GetTracks():
    if (t.Type() != pcbnew.PCB_VIA_T and t.GetLayer() in nyitas and HALOK.match(t.GetNetname())
            and mm(t.GetWidth()) >= 0.99):
        t.TransformShapeToPolygon(nyitas[t.GetLayer()], t.GetLayer(), 0, ERR, pcbnew.ERROR_INSIDE)
for z in b.Zones():
    if z.GetIsRuleArea() or not HALOK.match(z.GetNetname()):
        continue
    for l in nyitas:
        if z.IsOnLayer(l) and z.HasFilledPolysForLayer(l):
            nyitas[l].BooleanAdd(pcbnew.SHAPE_POLY_SET(z.GetFilledPolysList(l)))

# felül: az udvarok és a sönt környéke fedett marad
tilt = pcbnew.SHAPE_POLY_SET()
for f in b.GetFootprints():
    if f.GetLayer() != pcbnew.F_Cu:
        continue
    f.BuildCourtyardCaches()
    c = pcbnew.SHAPE_POLY_SET(f.GetCourtyard(pcbnew.F_CrtYd))
    if c.OutlineCount() == 0:
        continue
    c.Inflate(FM(SONT_TAV if f.GetReference() == SONT else UDVAR_TAV), CS, ERR)
    tilt.BooleanAdd(c)
nyitas[pcbnew.F_Cu].BooleanSubtract(tilt)

csop = pcbnew.PCB_GROUP(b); csop.SetName(CSOPORT); b.Add(csop)
for l, ps in nyitas.items():
    eredeti = pcbnew.SHAPE_POLY_SET(ps)
    ps.Deflate(FM(MIN_SZEL / 2), CS, ERR); ps.Inflate(FM(MIN_SZEL / 2), CS, ERR)   # keskeny maradék el
    ps.BooleanIntersection(eredeti)                                                # a réznél nem nagyobb
    ps.Fracture()
    mask = pcbnew.F_Mask if l == pcbnew.F_Cu else pcbnew.B_Mask
    n, ter = 0, 0.0
    for k in range(ps.OutlineCount()):
        egy = pcbnew.SHAPE_POLY_SET(); egy.AddOutline(ps.Outline(k))
        a = egy.Area() / 1e12
        if a < MIN_TER:
            continue
        s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_POLY); s.SetPolyShape(egy)
        s.SetFilled(True); s.SetWidth(0); s.SetLayer(mask); s.SetLocked(True)
        b.Add(s); csop.AddItem(s); n += 1; ter += a
    print(f'{b.GetLayerName(mask)}: {n} nyitás, {ter:.0f} mm²')
pcbnew.SaveBoard(ki, b)
