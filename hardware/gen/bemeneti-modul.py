"""Általános bemeneti modul – modulmag (A változat, saját 24 V) + 16 bemenet JST-PH-n + HDC3020 (D44, D48, D51, D66)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import kigen
kigen.POWER_UP = {'+3V3', '+5V'}
kigen.POWER_DOWN = {'GND'}

OUT = sys.argv[1]
S = kigen.Sheet('Bemeneti modul – 16 bemenet (JST-PH), 4 érzékelő-tápcsoport, HDC3020, modulmag', 'bemeneti-modul')
S.use('modularis:HDC3020', lib='modularis', name='HDC3020',
      libpath=os.path.join(os.path.dirname(__file__), '..', 'lib', 'modularis.kicad_sym'))
S.label_dx.update({'Power_Protection:TPD4E05U06DQA': 7.62, 'modularis:HDC3020': 12.7,
                   'Regulator_Linear:NCP1117-3.3_SOT223': 10.16, 'Connector_Generic:Conn_01x03': 5.08,
                   'Connector_Generic:Conn_01x04': 5.08, 'Jumper:SolderJumper_3_Bridged12': 5.08})

R0603 = 'Resistor_SMD:R_0603_1608Metric'
C0603 = 'Capacitor_SMD:C_0603_1608Metric'
PH3 = 'Connector_JST:JST_PH_B3B-PH-K_1x03_P2.00mm_Vertical'
PH4 = 'Connector_JST:JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical'

# bemenet → STM32-láb (MODULMAG-SPEC 7., D54)
PINS = ['PA0', 'PA1', 'PA2', 'PA3', 'PA4', 'PA5', 'PA6', 'PA7', 'PA8', 'PA9', 'PA10', 'PB11',
        'PB12', 'PB13', 'PB14', 'PB15']
FT = {8, 9, 10}  # IN8–IN10: 5 V-tűrő (FT) lábak; a többi TTa (≤ 3,6 V)


def note(n):
    return {'Megjegyzés': n}


def R(ref, val, x, y, a, b, fp=R0603, r=0, **k):
    S.comp('Device:R', ref, val, x, y, {'1': a, '2': b}, fp=fp, r=r, **k)


def C(ref, val, x, y, a, b, fp=C0603, r=0, **k):
    S.comp('Device:C', ref, val, x, y, {'1': a, '2': b}, fp=fp, r=r, **k)


# =================== Modulmag ===================
S.text('MODULMAG – A változat, saját 24 V', 20, 24, 1.5)
S.text('P78E05 → NCP1117, izolált CAN (D66)', 20, 28)
left = [('+24V_IN', '+24V_IN'), ('+24V_P', None), ('V_BUS_P', None), ('HW_ID', 'HW_ID')]
right = [(p, f'IN{i}') for i, p in enumerate(PINS)]
right += [('PB8', 'I2C_SCL'), ('PB9', 'I2C_SDA'), ('PC2', 'HDC_ALERT'), ('PC3', None), ('PC6', None), ('PC7', None), ('PC8', None)]
S.subsheet('modulmag', '../modulmag/modulmag.kicad_sch', 30, 35, 40, 2.54 * (len(right) + 1), left=left, right=right)

S.comp('Connector_Generic:Conn_01x02', 'J300', '24V IN', 25, 45, {'1': '+24V_IN', '2': 'GND'},
       fp='TerminalBlock_Phoenix:TerminalBlock_Phoenix_PT-1,5-2-5.0-H_1x02_P5.00mm_Horizontal',
       props=note('push-in, a típus a DIN-ház vállától függ (D50)'))
S.flag('+24V_IN', 25, 60)

# HW-ID (MODULMAG-SPEC 3.5): bemeneti = 3,3k / 10k → 2,48 V → 6. sáv
S.text('HW-ID: bemeneti modul = 6. sáv (2,48 V)', 20, 118)
R('R301', '3k3 1%', 25, 126, '+3V3', 'HW_ID')
R('R302', '10k 1%', 25, 141, 'HW_ID', 'GND')
C('C301', '100n', 38, 141, 'HW_ID', 'GND')

# =================== 1. Érzékelő-táp ===================
S.text('1. ÉRZÉKELŐ-TÁP: külön 3,3 V-os sín (U301, NCP1117) az 5 V-ról – egy zárlatos érzékelő nem indítja újra az MCU-t', 110, 22, 1.5)
S.text('4 csoport × 4 csatlakozó: csoportonként 3 padas forrasztható választó (alap: 3,3 V; átforrasztva: 5 V) + saját PTC', 110, 27)
S.comp('Regulator_Linear:NCP1117-3.3_SOT223', 'U301', 'NCP1117ST33T3G', 135, 45, {'3': '+5V', '1': 'GND', '2': '+3V3S'},
       props=note('csak az érzékelőknek; az MCU 3,3 V-ja a modulmag U5-je'))
C('C302', '10µ/10V', 118, 50, '+5V', 'GND', fp='Capacitor_SMD:C_0805_2012Metric')
S.comp('Device:C_Polarized', 'C303', '10µ tantál', 158, 50, {'1': '+3V3S', '2': 'GND'},
       fp='Capacitor_Tantalum_SMD:CP_EIA-3216-18_Kemet-A', props=note('ESR 0,1–2 Ω (NCP1117 stabilitás)'))
for k in range(1, 5):
    x = 185 + (k - 1) * 55
    S.comp('Jumper:SolderJumper_3_Bridged12', f'JP{300 + k}', f'CSOPORT {k}', x, 45,
           {'1': '+3V3S', '2': f'SUP{k}_SEL', '3': '+5V'}, fp='Jumper:SolderJumper-3_P1.3mm_Bridged12_RoundedPad1.0x1.5mm',
           props=note(f'{k}. csoport tápja: 1–2 = 3,3 V (alap), 2–3 = 5 V'))
    S.comp('Device:Polyfuse', f'F{300 + k}', 'PTC 0,2A', x + 18, 45, {'1': f'SUP{k}_SEL', '2': f'SUP{k}'},
           fp='Fuse:Fuse_1206_3216Metric', props=note('tartóáram ≈ 0,2 A, ≥ 6 V (pl. Bourns MF-NSMF020)'))
    C(f'C{303 + k}', '1µ', x + 32, 50, f'SUP{k}', 'GND')
S.text('5 V-os csoportban az érzékelő jele is 5 V lehet: az IN8–IN10 (PA8–PA10) 5 V-tűrő, a többi bemeneten az osztó-footprint kell (R_s 2k2, R_le 3k9, R_fel ki)', 110, 68)

# =================== 2. Bemenetek ===================
S.text('2. BEMENETEK (× 16): PH-csatlakozó 1 = táp (SUPk), 2 = GND, 3 = JEL → R_s → MCU-láb; R_fel 3,3 V-ra, R_le (DNP) és C a GND-re, ESD az MCU-oldalon', 20, 160, 1.5)
S.text('Alap: R_s 1k + R_fel 10k + C 10n → érintkező, reed, gomb, open-drain (pl. AH1911), 3,3 V-os kimenet. 12/24 V-os jel: R_s 68k, R_le 10k, R_fel ki.', 20, 165)
for n in range(16):
    k = n // 4 + 1
    col, row = n % 4, n // 4
    x = 20 + col * 72
    yy = 180 + row * 26
    S.comp('Connector_Generic:Conn_01x03', f'J{301 + n}', f'IN{n}', x, yy, {'1': f'SUP{k}', '2': 'GND', '3': f'IN{n}_EXT'}, fp=PH3,
           props=note(f'{k}. tápcsoport' + (' – 5 V-tűrő láb' if n in FT else '')))
    R(f'R{310 + n}', '1k', x + 15, yy + 2, f'IN{n}_EXT', f'IN{n}', r=90)
    R(f'R{330 + n}', '10k', x + 27, yy - 6, '+3V3', f'IN{n}')
    R(f'R{350 + n}', 'DNP', x + 37, yy + 8, f'IN{n}', 'GND', dnp=True, props=note('osztó 5/12/24 V-os jelhez'))
    C(f'C{310 + n}', '10n', x + 47, yy + 8, f'IN{n}', 'GND')

# ESD: 4 × TPD4E05U06 (4 csatorna / IC), az MCU-oldalon
S.text('ESD: 4 × TPD4E05U06 – a csatlakozók mellé,', 315, 172)
S.text('a soros R MCU-oldalára', 315, 176)
for g in range(4):
    a = 4 * g
    S.comp('Power_Protection:TPD4E05U06DQA', f'U{303 + g}', 'TPD4E05U06DQAR', 320 + (g % 2) * 45, 185 + (g // 2) * 40,
           {'1': f'IN{a}', '2': f'IN{a + 1}', '4': f'IN{a + 2}', '5': f'IN{a + 3}', '3': 'GND', '8': 'GND'},
           nc=['6', '7', '9', '10'])

# =================== 3. HDC3020 + külső I²C ===================
S.text('3. HŐMÉRSÉKLET / PÁRATARTALOM: HDC3020 a NYÁK szélén (alatta és körülötte marás), + 4 tűs PH külső érzékelőhöz (D66)', 110, 85, 1.5)
S.comp('modularis:HDC3020', 'U302', 'HDC3020DEFR', 150, 115,
       {'5': '+3V3', '6': '+3V3', '2': 'GND', '7': 'GND', '1': 'I2C_SDA', '4': 'I2C_SCL', '3': 'HDC_ALERT', '8': 'GND'}, nc=['9'],
       props=note('I²C-cím 0x44 (ADDR = ADDR1 = GND); a külső érzékelő más címre állítva (0x45–0x47). Az EP lebegve.'))
C('C320', '100n', 128, 105, '+3V3', 'GND')
R('R371', '4k7', 185, 100, '+3V3', 'I2C_SCL')
R('R372', '4k7', 197, 100, '+3V3', 'I2C_SDA')
R('R373', '10k', 209, 100, '+3V3', 'HDC_ALERT')
R('R374', '100R', 230, 112, 'I2C_SCL', 'SCL_EXT', r=90)
R('R375', '100R', 230, 124, 'I2C_SDA', 'SDA_EXT', r=90)
S.comp('Power_Protection:TPD4E05U06DQA', 'U307', 'TPD4E05U06DQAR', 262, 118,
       {'1': 'SCL_EXT', '2': 'SDA_EXT', '3': 'GND', '8': 'GND'}, nc=['4', '5', '6', '7', '9', '10'])
S.comp('Device:Polyfuse', 'F305', 'PTC 0,2A', 282, 102, {'1': '+3V3S', '2': 'SUP_I2C'}, fp='Fuse:Fuse_1206_3216Metric')
S.comp('Connector_Generic:Conn_01x04', 'J320', 'I2C KÜLSŐ', 300, 118,
       {'1': 'SUP_I2C', '2': 'GND', '3': 'SDA_EXT', '4': 'SCL_EXT'}, fp=PH4,
       props=note('külső HDC3020 / I²C-érzékelő, kábel ≤ 2 m, 100 kHz'))

S.text('VÁZLAT – generálva a D44/D48/D51/D66 alapján (2026-10-16). Elrendezést rendezd; a bekötés címkékkel kész.', 20, 287, 1.5)
S.write(OUT, date='2026-10-16')
print('ok', OUT)
