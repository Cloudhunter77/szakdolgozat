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
S.label_pos.update({'Transistor_Array:ULN2803A': ((-7.62, -12.7), (-7.62, 20.32)),
                    'Relay:Relay_SPDT': ((-10.16, -10.16), (-10.16, 11.43))})
S.label_dx.update({'Connector_Generic:Conn_01x02': 5.08})

R0603 = 'Resistor_SMD:R_0603_1608Metric'
R0805 = 'Resistor_SMD:R_0805_2012Metric'
C0603 = 'Capacitor_SMD:C_0603_1608Metric'


def P(note):
    return {'Megjegyzés': note}


def shunt(lib, ref, val, top, bottom_net, fp, r=0, top_pin='1', bot_pin='2', **k):
    return S.place(lib, ref, val, {top_pin: None, bot_pin: bottom_net}, top_pin, top, r=r, fp=fp, **k)


# ---------------- Modulmag + betáp ----------------
S.text('MODULMAG (../modulmag/modulmag.kicad_sch): táp, STM32F303RET6, ISO1042, busz-csatlakozók (J2/J3), lezárás', 20, 25, 1.5)
left = [('+24V_IN', '+24V_IN'), ('+24V_P', '+24V_P'), ('V_BUS_P', None), ('HW_ID', 'HW_ID')]
right = [('PB12', 'REL1'), ('PB13', 'REL2'), ('PB14', 'REL3'), ('PB15', 'REL4')]
right += [(n, None) for n in ['PB8', 'PB9', 'PB11', 'PC2', 'PC3', 'PC6', 'PC7', 'PC8'] + [f'PA{i}' for i in range(11)]]
S.subsheet('modulmag', '../modulmag/modulmag.kicad_sch', 50, 40, 40, 2.54 * (len(right) + 1), left=left, right=right)

pp = S.comp('Connector_Generic:Conn_01x02', 'J100', '24V IN', 25, 70, {'1': None, '2': None},
            fp='TerminalBlock_Phoenix:TerminalBlock_Phoenix_PT-1,5-2-5.0-H_1x02_P5.00mm_Horizontal',
            props=P('push-in, a típus a DIN-ház vállától függ (D50)'))
a1, a2 = pp['1'][:2], pp['2'][:2]
S.wire(a1, (a1[0] - 5.08, a1[1]))
S.label('+24V_IN', (a1[0] - 5.08, a1[1]), 180)
S.wire(a2, (a2[0] - 2.54, a2[1]), (a2[0] - 2.54, a2[1] + 2.54))
S.label('GND', (a2[0] - 2.54, a2[1] + 2.54), 270)
S.flag('+24V_IN', 25, 85)
S.text('24 V betáp (J100)', 12, 62)

# HW-ID (MODULMAG-SPEC 3.5): relé = 10k / 10k → 1,65 V → 4. sáv
S.text('HW-ID: relé = 4. sáv (1,65 V)', 12, 102)
S.label('+3V3', (25, 108), 90)
shunt('Device:R', 'R101', '10k 1%', (25, 108), None, R0603)
nh = (25, 118.11)
S.wire((25, 115.62), nh)
shunt('Device:R', 'R102', '10k 1%', (25, 120.65), 'GND', R0603)
S.wire(nh, (25, 120.65))
shunt('Device:C', 'C101', '100n', (35, 120.65), 'GND', C0603)
S.wire(nh, (35, nh[1]), (35, 120.65))
S.wire((35, nh[1]), (40, nh[1]))
S.label('HW_ID', (40, nh[1]), 0)
S.junction(nh)
S.junction((35, nh[1]))

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
                props=P('1 = COM, 2 = NO; ≥ 16 A, ≥ 250 V AC; helyőrző – push-in, a DIN-ház szerint'))
    com, no = pr['11'][:2], pr['14'][:2]
    S.wire(no, (no[0], no[1] - 2.54), (jx - 10.16, no[1] - 2.54), (jx - 10.16, pj['2'][1]), pj['2'][:2])
    S.wire(com, (com[0], com[1] + 2.54), (jx - 7.62, com[1] + 2.54), (jx - 7.62, pj['1'][1]), pj['1'][:2])
S.text('Visszajelző LED: +24V_P – 10 k – LED – a tekercs alsó vége (ULN-kimenet) → ~2 mA, ha a relé BE', 200, 250)

S.text('Generálva (hardware/gen/rele-modul.py) – a MODULMAG-SPEC + D62 alapján; kézi szerkesztés helyett a generátort módosítsd.', 20, 287, 1.3)
S.write(OUT, date='2026-10-16')
print('ok', OUT)
