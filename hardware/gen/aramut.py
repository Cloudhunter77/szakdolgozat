"""A fő áramutak legszűkebb pontja a NYÁK-on (D91) – Claude, 2026-10-27.
    flatpak run --command=python3 org.kicad.KiCad gen/aramut.py <lap>
A DRC-szabályban a táp-sávok minimuma 0,2 mm (a mérő- és mellékágak miatt), ezért a fő utat külön nézzük: a W-nél
keskenyebb sávokat elhagyva a kulcspadok egy szigeten maradnak-e (zónák és viák számítanak). Kimenet soronként:
„OK …”, „HIBA …” (a minimum alatt), „FIGYELEM …” (a javasolt alatt, vagy még nincs huzalozva)."""
import sys
import pcbnew

mm = pcbnew.ToMM
LAP = sys.argv[1]
NAGY = (1.5, 2.5)          # nagyáramú út (fedetlen, ónozott – D82): minimum, javasolt (mm)
BUSZ = (0.5, 0.6)          # a busz átmenő +5V / GND_BUS: 2 A (D71)
UTAK = {   # név, hálózat, kulcspadok, (minimum, javasolt)
    'led-modul': [
        ('+24V betáp', '+24V_IN', 'J201.1 F201.1', NAGY), ('sín F201 → F202–F204', '+24V_RAIL', 'F201.2 F202.1 F203.1 F204.1', NAGY),
        ('1. blokk', '+24V_B1', 'F202.2 J202.2', NAGY), ('2. blokk', '+24V_B2', 'F203.2 J203.2', NAGY),
        ('3. blokk', '+24V_B3', 'F204.2 J204.2', NAGY),
        *[(f'CH{i} drain', f'/CH{i}_D', f'Q20{i + 1}.2 {j}', NAGY) for i, j in
          [(1, 'J202.3'), (2, 'J202.1'), (3, 'J203.3'), (4, 'J203.1'), (5, 'J204.3'), (6, 'J204.1')]],
        ('FET-ek → sönt', 'PGND_SH', 'R209.1 Q202.3 Q203.3 Q204.3 Q205.3 Q206.3 Q207.3', NAGY),
        ('sönt → Q201', 'GND', 'R209.4 Q201.1 Q201.2 Q201.3', NAGY), ('Q201 → betáp', '/GND_IN', 'J201.2 Q201.5', NAGY),
        ('busz +5V', '+5V', 'J2.1 J3.1', BUSZ), ('busz GND', '/GND_BUS', 'J2.2 J3.2', BUSZ)],
    'rele-modul': [('busz +5V', '+5V', 'J2.1 J3.1', BUSZ), ('busz GND', '/GND_BUS', 'J2.2 J3.2', BUSZ),
                   *[(f'{k} COM/NO → J10{n}', None, f'{k}.11 J10{n}.1', (2.0, 3.0)) for n, k in
                     [(1, 'K1'), (2, 'K2'), (3, 'K3'), (4, 'K4')]],
                   *[(f'{k} NO → J10{n}', None, f'{k}.14 J10{n}.2', (2.0, 3.0)) for n, k in
                     [(1, 'K1'), (2, 'K2'), (3, 'K3'), (4, 'K4')]]],
    'bemeneti-modul': [('busz +5V', '+5V', 'J2.1 J3.1', BUSZ), ('busz GND', '/GND_BUS', 'J2.2 J3.2', BUSZ)],
    'vezerlo': [('V_BUS (eFuse → busz)', 'V_BUS', 'U3.5 J2.1 J3.1', BUSZ), ('+5V (U12 → eFuse)', '+5V', 'U12.2 U3.3', BUSZ),
                ('24 V betáp', '+24V_IN', 'J1.1 F1.1', BUSZ)],
}


def betolt():
    b = pcbnew.LoadBoard(f'{LAP}/{LAP}.kicad_pcb')
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    return b


def egyben(b, keys):
    def pad(s):
        r, n = s.split('.')
        f = b.FindFootprintByReference(r)
        return [p for p in f.Pads() if p.GetNumber() == n][0] if f else None
    ps = [pad(k) for k in keys.split()]
    if None in ps:
        return None
    b.BuildConnectivity(); c = b.GetConnectivity()
    con = {x.m_Uuid.AsString() for x in c.GetConnectedItems(ps[0]) if x.Type() == pcbnew.PCB_PAD_T}
    return all(p.m_Uuid.AsString() in con for p in ps[1:])


utak = UTAK.get(LAP, [])
kuszob = sorted({w for *_, ws in utak for w in ws})
eredmeny = {}                                     # név → a legnagyobb küszöb, amelyen még egyben van
alap = betolt()
for nev, net, keys, ws in utak:
    eredmeny[nev] = 0.0 if egyben(alap, keys) else None
for w in kuszob:
    b = betolt()
    for t in list(b.GetTracks()):
        if t.Type() != pcbnew.PCB_VIA_T and mm(t.GetWidth()) < w - 1e-6:
            b.Delete(t)
    for nev, net, keys, ws in utak:
        if eredmeny[nev] is not None and egyben(b, keys):
            eredmeny[nev] = w
for nev, net, keys, (wmin, wjo) in utak:
    e = eredmeny[nev]
    if e is None:
        print(f'FIGYELEM {LAP}: {nev} – még nincs végig bekötve ({keys})')
    elif e < wmin:
        print(f'HIBA {LAP}: {nev} – a fő út valahol {wmin} mm-nél keskenyebb ({keys})')
    elif e < wjo:
        print(f'FIGYELEM {LAP}: {nev} – a legszűkebb pont {wmin}–{wjo} mm között (javasolt ≥ {wjo} mm)')
    else:
        print(f'OK {LAP}: {nev} ≥ {wjo} mm')
