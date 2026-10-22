"""Relémodul – modulmag (hierarchikus lap) + ULN2803A + 4 × Schrack RTD14024 (D62), elrendezett változat.

Balra a modulmag-blokk és a 24 V-os betáp, középen a relémeghajtó, jobbra a 4 relécella egy sorban:
+24V_P sín felül, a tekercs alsó vége a meghajtó kimenetére, mellette a visszajelző LED, jobbra a sorkapocs.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import kigen
kigen.POWER_UP = {'+3V3'}
kigen.POWER_DOWN = {'GND'}

OUT = sys.argv[1]
S = kigen.Sheet('Relémodul – 4 × RTD14024 (16 A, 230 V), modulmag', 'rele-modul')
S.label_pos.update({'Transistor_Array:ULN2803A': ((-7.62, -12.7), (5.08, 20.32)),     # érték a GND-láb mellett jobbra
                    'Relay:Relay_SPDT': ((-10.16, -10.16), (-21.59, 11.43))})       # érték balra lent, nem a COIL-vezetéken
S.label_dx.update({'Connector_Generic:Conn_01x02': 5.08, 'Device:LED': 8.89})

R0603 = 'Resistor_SMD:R_0603_1608Metric'
R0805 = 'Resistor_SMD:R_0805_2012Metric'
C0603 = 'Capacitor_SMD:C_0603_1608Metric'


def P(note):
    return {'Megjegyzés': note}


def shunt(lib, ref, val, top, bottom_net, fp, r=0, top_pin='1', bot_pin='2', **k):
    return S.place(lib, ref, val, {top_pin: None, bot_pin: bottom_net}, top_pin, top, r=r, fp=fp, **k)


# ---------------- Modulmag + betáp ----------------
S.text('MODULMAG (../modulmag/modulmag.kicad_sch): táp a buszról, STM32L433RCT3, SN65HVD230, busz-csatlakozók (J2/J3), lezárás (D71, D78)', 20, 25, 1.5)
left = [('HW_ID', 'HW_ID'), ('GND_BUS', 'GND_BUS')]
right = [('PB12', 'REL1'), ('PB13', 'REL2'), ('PB14', 'REL3'), ('PB15', 'REL4')]
right += [('PB1', 'VIN_SENSE')]   # D78: a PB11 az L433-on nem ADC-s
right += [(n, None) for n in ['PB8', 'PB9', 'PB11', 'PC2', 'PC3'] + [f'PA{i}' for i in range(11)]]
right = [(n, 'CT_SENSE' if n == 'PA0' else net) for n, net in right]   # D69: SCT-013 előkészítés
S.subsheet('modulmag', '../modulmag/modulmag.kicad_sch', 50, 40, 40, 2.54 * (len(right) + 1), left=left, right=right)

pp = S.comp('Connector_Generic:Conn_01x02', 'J100', '24V IN', 33, 70, {'1': None, '2': None},
            fp='TerminalBlock_Phoenix:TerminalBlock_Phoenix_PT-1,5-2-5.0-H_1x02_P5.00mm_Horizontal',
            props=P('push-in, a típus a DIN-ház vállától függ (D50)'))
a1, a2 = pp['1'][:2], pp['2'][:2]
S.wire(a1, (a1[0] - 5.08, a1[1]))
S.label('+24V_IN', (a1[0] - 5.08, a1[1]), 180)
S.wire(a2, (a2[0] - 2.54, a2[1]), (a2[0] - 2.54, a2[1] + 2.54))
S.label('GND_IN', (a2[0] - 2.54, a2[1] + 2.54), 270)
S.flag('+24V_IN', 33, 85)
S.text('24 V betáp (J100)', 22, 62)

# HW-ID (MODULMAG-SPEC 3.5, D71): relé, 24 V-os tekercs = 10k / 1,54k → 0,44 V → 2. sáv; 12 V-os tekercs: 3,65k → 4. sáv
S.text('HW-ID: relé 24 V = 2. sáv (0,44 V)', 12, 102)
S.text('12 V-os relé: R102 = 3k65 → 4. sáv', 45, 110)
S.label('+3V3', (25, 108), 90)
shunt('Device:R', 'R101', '10k 1%', (25, 108), None, R0603)
nh = (25, 118.11)
S.wire((25, 115.62), nh)
shunt('Device:R', 'R102', '1k54 1%', (25, 120.65), 'GND', R0603, props=P('24 V-os tekercs: 1,54k (2. sáv); 12 V-os tekercs: 3,65k (4. sáv)'))
S.wire(nh, (25, 120.65))
shunt('Device:C', 'C101', '100n', (38.1, 120.65), 'GND', C0603)
S.wire(nh, (38.1, nh[1]), (38.1, 120.65))
S.wire((38.1, nh[1]), (43.18, nh[1]))
S.label('HW_ID', (43.18, nh[1]), 0)
S.junction(nh)
S.junction((38.1, nh[1]))


# busz-GND (D74): a GND_BUS (XH 2-es tű) a modul GND-jére 0R-on át – a nagyáramú modul hurokárama ne a buszon folyjon
S.label('GND_BUS', (100, 130), 180)
S.wire((100, 130), (100 + 2.54, 130))
_pg = S.place('Device:R', 'R113', '0R', {'1': None, '2': None}, '1', (100 + 2.54, 130), r=90, fp='Resistor_SMD:R_1206_3216Metric',
              props=P('D74: 0 Ω (a tekercsek kis árama miatt); ha a busz GND-jén hurokáram mérhető: 1 Ω'))
_q = _pg['2'][:2]
S.wire(_q, (_q[0] + 2.54, _q[1]), (_q[0] + 2.54, _q[1] + 2.54))
S.label('GND', (_q[0] + 2.54, _q[1] + 2.54), 270)

# GND-ági polaritásvédelem (D78): Q100 – D = J100 GND-pólusa (GND_IN), S = a lap GND-je, G a +24V_P-ről 10 k + 15 V Zener.
# A közös föld miatt (D71) a + ági D100 egymagában nem elég: fordított bekötésnél a busz GND-érén át zárlat lenne.
S.text('POLARITÁSVÉDELEM a GND-ágban (D78)', 100, 91)
S.ref_pos['Q100'] = ((6.35, -1.27), (6.35, 1.27))
pq = S.place('Transistor_FET:Q_NMOS_GDS', 'Q100', 'IRFR120N', {'1': None, '2': None, '3': None}, '1', (114.3, 111.76),
             fp='Package_TO_SOT_SMD:TO-252-2', props=P('kézben; 100 V, ~0,21 Ω – a tekercsek ~70 mA-jén ~15 mV'))
qg, qd, qs = pq['1'][:2], pq['2'][:2], pq['3'][:2]
S.wire(qd, (qd[0], qd[1] - 2.54))
S.label('GND_IN', (qd[0], qd[1] - 2.54), 90)
S.wire(qs, (qs[0], qs[1] + 2.54))
S.label('GND', (qs[0], qs[1] + 2.54), 270)
gn = (qg[0] - 7.62, qg[1])
S.wire(qg, gn)
S.wire((gn[0], gn[1] - 2.54), gn)
shunt('Device:R', 'R114', '10k', (gn[0], gn[1] - 10.16), None, R0603)
S.label('+24V_P', (gn[0], gn[1] - 10.16), 90)
shunt('Device:D_Zener', 'D106', 'BZT52C15', (gn[0], gn[1] + 2.54), 'GND', 'Diode_SMD:D_SOD-123', r=270,
      props=P('15 V – a gate–source-feszültség határa (±20 V) alatt'))
S.wire(gn, (gn[0], gn[1] + 2.54))
S.junction(gn)

# ---------------- Tekercs-táp (D71): +24V_IN → F100 → D100 → +24V_P; TVS, puffer, VIN_SENSE → PB1 ----------------
S.text('TEKERCS-TÁP (D71): J100 → F100 → D100 → +24V_P (12 V-os tápnál 12 V-os relé!)', 12, 137)
S.text('VIN_SENSE (PB1): 150k / 10k – a firmware összeveti a HW-ID-vel', 12, 141)
Yt = 152.4
S.label('+24V_IN', (17.78, Yt), 180)
S.wire((17.78, Yt), (20.32, Yt))
p = S.place('Device:Fuse', 'F100', '0,5A', {'1': None, '2': None}, '1', (20.32, Yt), r=90, fp='Fuse:Fuse_1206_3216Metric',
            props=P('≥ 32 V, gyors, 1206; 4 tekercs × ~17 mA'))['2'][:2]
S.wire(p, (p[0] + 2.54, Yt))
p = S.place('Device:D_Schottky', 'D100', 'SS16', {'1': None, '2': None}, '2', (p[0] + 2.54, Yt), r=180, fp='Diode_SMD:D_SMA',
            props=P('fordított polaritás ellen'))['1'][:2]
tt = [p[0] + 5.08, p[0] + 16.51, p[0] + 27.94, p[0] + 39.37, p[0] + 50.8]
S.rail(Yt, [p[0]] + tt)
shunt('Device:D_Zener', 'D105', 'SMBJ28A', (tt[0], Yt + 5.08), 'GND', 'Diode_SMD:D_SMB', r=270, props=P('TVS, 28 V standoff'))
S.wire((tt[0], Yt), (tt[0], Yt + 5.08))
shunt('Device:C', 'C104', '10µ/50V', (tt[1], Yt + 5.08), 'GND', 'Capacitor_SMD:C_1210_3225Metric')
S.wire((tt[1], Yt), (tt[1], Yt + 5.08))
shunt('Device:C_Polarized', 'C105', '47µ/50V', (tt[2], Yt + 5.08), 'GND', 'Capacitor_SMD:CP_Elec_6.3x7.7',
      props=P('elektrolit: a betápkábel LC-lengését csillapítja (D57 mintájára)'))
S.wire((tt[2], Yt), (tt[2], Yt + 5.08))
shunt('Device:R', 'R111', '150k', (tt[3], Yt + 5.08), None, R0603)
S.wire((tt[3], Yt), (tt[3], Yt + 5.08))
nvs = (tt[3], Yt + 15.24)
S.wire((tt[3], Yt + 12.7), nvs)
shunt('Device:R', 'R112', '10k', (tt[3], Yt + 17.78), 'GND', R0603)
S.wire(nvs, (tt[3], Yt + 17.78))
shunt('Device:C', 'C106', '100n', (tt[3] + 8.89, Yt + 17.78), 'GND', C0603)
S.wire(nvs, (tt[3] + 8.89, nvs[1]), (tt[3] + 8.89, Yt + 17.78))
S.wire((tt[3] + 8.89, nvs[1]), (tt[3] + 13.97, nvs[1]))
S.label('VIN_SENSE', (tt[3] + 13.97, nvs[1]), 0)
S.junction(nvs)
S.junction((tt[3] + 8.89, nvs[1]))
S.wire((tt[4], Yt), (tt[4], Yt - 5.08))
S.label('+24V_P', (tt[4], Yt - 5.08), 90)
S.flag('+24V_P', 48, 85)

# ---------------- ULN2803A ----------------
S.text('RELÉMEGHAJTÓ – ULN2803A: belső kioltó diódák', 110, 140, 1.5)
S.text('a COM-on (10) át a +24V_P-re; a bemenetek belső', 110, 145)
S.text('lehúzása → bekapcsoláskor minden relé KI', 110, 149)
UX, UY = 135, 175
nets = {'1': None, '2': None, '3': None, '4': None, '5': None, '6': None, '7': None, '8': None,
        '9': None, '10': None, '18': None, '17': None, '16': None, '15': None}
pu = S.comp('Transistor_Array:ULN2803A', 'U101', 'ULN2803ADWR', UX, UY, nets, nc=['11', '12', '13', '14'],
            fp='Package_SO:SOIC-18W_7.5x11.6mm_P1.27mm')
for i, n in enumerate(['1', '2', '3', '4']):
    a = pu[n][:2]
    S.wire(a, (a[0] - 7.62, a[1]))
    S.label(f'REL{i + 1}', (a[0] - 7.62, a[1]), 180)
# nem használt bemenetek (5–8) a GND-re
xg = pu['5'][0] - 5.08
for n in ['5', '6', '7', '8']:
    S.wire(pu[n][:2], (xg, pu[n][1]))
S.wire((xg, pu['5'][1]), (xg, pu['8'][1] + 2.54))
for n in ['6', '7']:
    S.junction((xg, pu[n][1]))
S.junction((xg, pu['8'][1]))
S.label('GND', (xg, pu['8'][1] + 2.54), 270)
S.wire(pu['9'][:2], (pu['9'][0], pu['9'][1] + 2.54))
S.label('GND', (pu['9'][0], pu['9'][1] + 2.54), 270)
# COM (10) → +24V_P
c = pu['10'][:2]
S.wire(c, (c[0] + 5.08, c[1]), (c[0] + 5.08, c[1] - 7.62))
S.label('+24V_P', (c[0] + 5.08, c[1] - 7.62), 90)
# kimenetek → COILn címke
for i, n in enumerate(['18', '17', '16', '15']):
    a = pu[n][:2]
    S.wire(a, (a[0] + 12.7, a[1]))
    S.label(f'COIL{i + 1}', (a[0] + 12.7, a[1]), 0)

# ---------------- 4 relécella ----------------
S.text('RELÉK – Schrack RTD14024 (1 váltó, 16 A / 250 V AC, 24 V DC, 400 mW): kimenet csak COM + NO, az NC (12) nincs kivezetve', 200, 60, 1.5)
S.text('230 V: ≥ 8 mm kúszóút + légköz a törpefeszültségű résztől, marás a relék alatt; a hálózati rész alatt egyik rétegen sincs törpefeszültségű réz (D62)', 200, 65)
rows = [(95, 125), (185, 215)]      # (+24V_P sín, relé középpont) soronként
cols = [235, 335]
for RY, _ in rows:
    S.rail(RY, [205] + [x - 5.08 for x in cols] + [x - 17.78 for x in cols])
    S.label('+24V_P', (205, RY), 180)
for i in range(4):
    k = i + 1
    RY, CY = rows[i // 2]
    x = cols[i % 2]
    pr = S.comp('Relay:Relay_SPDT', f'K{k}', 'RTD14024', x, CY, {'A1': None, 'A2': None, '11': None, '14': None}, nc=['12'],
                fp='Relay_THT:Relay_SPDT_Schrack-RT1-16A-FormC_RM5mm')
    a1, a2 = pr['A1'][:2], pr['A2'][:2]
    S.wire((a1[0], RY), a1)
    S.junction((a1[0], RY))
    # tekercs alsó vége → COILk (meghajtó kimenet) + a LED katódja
    yc = a2[1] + 5.08
    S.wire(a2, (a2[0], yc))
    S.label(f'COIL{k}', (a2[0], yc), 270)
    # visszajelző LED: +24V_P → 10k → LED → COILk
    xl = x - 17.78
    S.junction((xl, RY))
    shunt('Device:R', f'R{102 + k}', '10k', (xl, RY + 5.08), None, R0805)
    S.wire((xl, RY), (xl, RY + 5.08))
    S.place('Device:LED', f'D{100 + k}', 'zöld', {'2': None, '1': None}, '2', (xl, RY + 17.78), r=90,
            fp='LED_SMD:LED_0603_1608Metric', props=P(f'{k}. relé BE – előlap, fényvezető alatt'))
    S.wire((xl, RY + 12.7), (xl, RY + 17.78))
    S.wire((xl, RY + 25.4), (xl, a2[1]), a2)
    S.junction(a2)
    # érintkezők → sorkapocs (1 = COM, 2 = NO)
    jx = x + 25.4
    pj = S.comp('Connector_Generic:Conn_01x02', f'J{100 + k}', f'RELÉ {k}', jx, CY, {'1': None, '2': None},
                fp='TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-3-2-5.08_1x02_P5.08mm_Horizontal',
                props=P('1 = COM, 2 = NO; ≥ 16 A, ≥ 250 V AC; push-in (D79) – a típus és a footprint a DIN-ház vállától függ, ez helyőrző'))
    com, no = pr['11'][:2], pr['14'][:2]
    S.wire(no, (no[0], no[1] - 2.54), (jx - 10.16, no[1] - 2.54), (jx - 10.16, pj['2'][1]), pj['2'][:2])
    S.wire(com, (com[0], com[1] + 2.54), (jx - 7.62, com[1] + 2.54), (jx - 7.62, pj['1'][1]), pj['1'][:2])
S.text('Visszajelző LED: +24V_P – 10 k – LED – a tekercs alsó vége (ULN-kimenet) → ~2 mA, ha a relé BE', 200, 250)

# ---------------- Fogyasztásmérés előkészítése (D37, D69) – minden DNP ----------------
S.text('FOGYASZTÁSMÉRÉS (D37, D69) – minden DNP: SCT-013 lakatfogós áramváltó 3,5 mm-es jackre → PA0 (ADC)', 20, 184)
S.text('SCT-013-030 (1 V kimenet): R109 nincs; áramkimenetes típushoz R109 = terhelő-ellenállás', 20, 188.5)
S.ref_pos['J105'] = ((-7.62, -7.62), (-7.62, -5.08))
pjk = S.comp('Connector_Audio:AudioJack3', 'J105', 'SCT-013', 30.48, 228.6, {'S': None, 'T': None}, nc=['R'],
             fp='Connector_Audio:Jack_3.5mm_CUI_SJ1-3513N_Horizontal', dnp=True, props=P('a lakatfogó leválaszt – a 230 V-os oldalt nem érinti'))
sl, tp = pjk['S'][:2], pjk['T'][:2]
ym = 213.36
S.wire(sl, (sl[0] + 5.08, sl[1]), (sl[0] + 5.08, ym), (76.2, ym))
S.label('+3V3', (66.04, 198.12), 90)
shunt('Device:R', 'R107', '10k', (66.04, 198.12), None, R0603, dnp=True)
S.wire((66.04, 205.74), (66.04, ym))
shunt('Device:R', 'R108', '10k', (66.04, ym), 'GND', R0603, dnp=True, props=P('középfeszültség 1,65 V'))
shunt('Device:C', 'C102', '10µ', (76.2, ym), 'GND', 'Capacitor_SMD:C_0805_2012Metric', dnp=True)
S.junction((66.04, ym))
S.wire((50.8, ym), (50.8, ym + 2.54))
shunt('Device:R', 'R109', 'DNP', (50.8, ym + 2.54), None, R0603, dnp=True, props=P('terhelő-ellenállás (csak áramkimenetes áramváltóhoz)'))
S.wire((50.8, ym + 10.16), (50.8, tp[1]))
S.junction((50.8, ym))
S.wire(tp, (81.28, tp[1]))
S.junction((50.8, tp[1]))
S.place('Device:R', 'R110', '1k', {'1': None, '2': None}, '1', (81.28, tp[1]), r=90, fp=R0603, dnp=True)
S.wire((88.9, tp[1]), (99.06, tp[1]))
S.wire((93.98, tp[1]), (93.98, tp[1] + 2.54))
shunt('Device:C', 'C103', '10n', (93.98, tp[1] + 2.54), 'GND', C0603, dnp=True)
S.junction((93.98, tp[1]))
S.label('CT_SENSE', (99.06, tp[1]), 0)

S.text('Generálva (hardware/gen/rele-modul.py) – a MODULMAG-SPEC + D62 alapján; kézi szerkesztés helyett a generátort módosítsd.', 20, 281, 1.3)
S.write(OUT, date='2026-10-22')
print('ok', OUT)
