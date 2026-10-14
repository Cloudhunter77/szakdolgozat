"""Relémodul – modulmag (hierarchikus lap) + ULN2803A + 4 × Schrack RTD14024 (D62)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import kigen
kigen.POWER_UP = {'+3V3'}
kigen.POWER_DOWN = {'GND'}

OUT = sys.argv[1]
S = kigen.Sheet('Relémodul – 4 × RTD14024 (16 A, 230 V), modulmag', 'rele-modul')
S.label_dx.update({'Relay:Relay_SPDT': 10.16, 'Transistor_Array:ULN2803A': 12.7})

R0805 = 'Resistor_SMD:R_0805_2012Metric'
R0603 = 'Resistor_SMD:R_0603_1608Metric'
C0603 = 'Capacitor_SMD:C_0603_1608Metric'

# ---------------- Modulmag ----------------
S.text('MODULMAG (../modulmag/modulmag.kicad_sch): táp, STM32F303RET6, ISO1042, busz-csatlakozók (J2/J3), lezárás', 20, 25, 1.5)
left = [('+24V_IN', '+24V_IN'), ('+24V_P', '+24V_P'), ('V_BUS_P', None), ('HW_ID', 'HW_ID')]
right = [('PB12', 'REL1'), ('PB13', 'REL2'), ('PB14', 'REL3'), ('PB15', 'REL4')]
right += [(n, None) for n in ['PB8', 'PB9', 'PB11', 'PC2', 'PC3', 'PC6', 'PC7', 'PC8'] + [f'PA{i}' for i in range(11)]]
S.subsheet('modulmag', '../modulmag/modulmag.kicad_sch', 60, 40, 40, 2.54 * (len(right) + 1), left=left, right=right)

# 24 V betáp
S.comp('Connector_Generic:Conn_01x02', 'J100', '24V IN', 25, 45, {'1': '+24V_IN', '2': 'GND'},
       fp='TerminalBlock_Phoenix:TerminalBlock_Phoenix_PT-1,5-2-5.0-H_1x02_P5.00mm_Horizontal',
       props={'Megjegyzés': 'push-in, a típus a DIN-ház vállától függ (D50)'})

# HW-ID (MODULMAG-SPEC 3.5): relé = 10k / 10k → 1,65 V → 4. sáv
S.text('HW-ID: relé = 4. sáv (1,65 V)', 20, 75)
S.comp('Device:R', 'R101', '10k 1%', 25, 85, {'1': '+3V3', '2': 'HW_ID'}, fp=R0603)
S.comp('Device:R', 'R102', '10k 1%', 25, 100, {'1': 'HW_ID', '2': 'GND'}, fp=R0603)
S.comp('Device:C', 'C101', '100n', 40, 100, {'1': 'HW_ID', '2': 'GND'}, fp=C0603)

# ---------------- ULN2803A ----------------
S.text('RELÉMEGHAJTÓ – ULN2803A: a belső kioltó diódák a COM-on (10) át a +24V_P-re; a bemenetek belső lehúzása → bekapcsoláskor minden relé KI', 140, 25, 1.5)
nets = {'1': 'REL1', '2': 'REL2', '3': 'REL3', '4': 'REL4', '5': 'GND', '6': 'GND', '7': 'GND', '8': 'GND',
        '9': 'GND', '10': '+24V_P', '18': 'COIL1', '17': 'COIL2', '16': 'COIL3', '15': 'COIL4'}
S.comp('Transistor_Array:ULN2803A', 'U101', 'ULN2803ADWR', 165, 60, nets, nc=['11', '12', '13', '14'],
       fp='Package_SO:SOIC-18W_7.5x11.6mm_P1.27mm')

# ---------------- 4 relé ----------------
S.text('RELÉK – Schrack RTD14024 (1 váltó, 16 A / 250 V AC, 24 V DC, 400 mW): kimenet csak COM + NO, az NC (12) nincs kivezetve', 140, 95, 1.5)
S.text('230 V: ≥ 8 mm kúszóút + légköz a törpefeszültségű résztől, marás a relék alatt; a hálózati rész alatt egyik rétegen sincs törpefeszültségű réz (D62)', 140, 100, 1.27)
for i in range(1, 5):
    x = 120 + (i - 1) * 55
    y = 130
    S.comp('Relay:Relay_SPDT', f'K{i}', 'RTD14024', x, y,
           {'A1': '+24V_P', 'A2': f'COIL{i}', '11': f'OUT{i}_COM', '14': f'OUT{i}_NO'}, nc=['12'],
           fp='Relay_THT:Relay_SPDT_Schrack-RT1-16A-FormC_RM5mm')
    S.comp('Device:R', f'R{102 + i}', '10k', x - 20, y - 10, {'1': '+24V_P', '2': f'LED{i}_A'}, fp=R0805)
    S.comp('Device:LED', f'D{100 + i}', 'zöld', x - 20, y + 8, {'2': f'LED{i}_A', '1': f'COIL{i}'},
           fp='LED_SMD:LED_0603_1608Metric', r=90, props={'Megjegyzés': f'{i}. relé BE – előlap, fényvezető alatt'})
    S.comp('Connector_Generic:Conn_01x02', f'J{100 + i}', f'RELÉ {i}', x + 25, y, {'1': f'OUT{i}_COM', '2': f'OUT{i}_NO'},
           fp='TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-3-2-5.08_1x02_P5.08mm_Horizontal',
           props={'Megjegyzés': '1 = COM, 2 = NO; ≥ 16 A, ≥ 250 V AC; helyőrző – push-in, a DIN-ház szerint'})
S.text('Visszajelző LED: +24V_P – 10 k – LED – a relé tekercsének alsó vége (ULN-kimenet) → ~2 mA, ha a relé BE', 140, 160)

S.flag('+24V_IN', 25, 60)
S.text('VÁZLAT – generálva a MODULMAG-SPEC + D62 alapján (2026-10-14). Elrendezést rendezd; a bekötés címkékkel kész.', 20, 285, 1.5)
S.write(OUT)
print('ok', OUT)
