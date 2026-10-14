"""LED-modul – modulmag (hierarchikus lap) + 6 low-side csatorna (D43, D47, D53, D65)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import kigen
kigen.POWER_UP = {'+3V3', '+12V'}
kigen.POWER_DOWN = {'GND'}

OUT = sys.argv[1]
S = kigen.Sheet('LED-modul – 6 × 10 A low-side PWM (össz. 20 A), modulmag', 'led-modul')
S.label_dx.update({'Driver_FET:UCC27524D': 12.7, 'Amplifier_Current:INA181': 10.16,
                   'Power_Management:LM74700': 15.24, 'Regulator_Linear:MC78L12_SO8': 10.16,
                   'Transistor_FET:QM6006D': 5.08, 'Transistor_FET:NTMFS016N06CT1G': 5.08,
                   'Connector_Generic:Conn_01x03': 5.08, 'Connector_Generic:Conn_01x02': 5.08})

R0603 = 'Resistor_SMD:R_0603_1608Metric'
R0805 = 'Resistor_SMD:R_0805_2012Metric'
R1206 = 'Resistor_SMD:R_1206_3216Metric'
C0603 = 'Capacitor_SMD:C_0603_1608Metric'
C0805 = 'Capacitor_SMD:C_0805_2012Metric'
C1206 = 'Capacitor_SMD:C_1206_3216Metric'
C1210 = 'Capacitor_SMD:C_1210_3225Metric'
LED0603 = 'LED_SMD:LED_0603_1608Metric'
TB2 = 'TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-3-2-5.08_1x02_P5.08mm_Horizontal'
TB3 = 'TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-3-3-5.08_1x03_P5.08mm_Horizontal'


def note(n):
    return {'Megjegyzés': n}


def R(ref, val, x, y, a, b, fp=R0603, r=0, **k):
    S.comp('Device:R', ref, val, x, y, {'1': a, '2': b}, fp=fp, r=r, **k)


def C(ref, val, x, y, a, b, fp=C0603, r=0, **k):
    S.comp('Device:C', ref, val, x, y, {'1': a, '2': b}, fp=fp, r=r, **k)


def LED(ref, x, y, a, k, n):
    S.comp('Device:LED', ref, 'zöld', x, y, {'2': a, '1': k}, fp=LED0603, r=90, props=note(n))


# =================== Modulmag ===================
S.text('MODULMAG – a logikai táp a 20 A-es', 20, 24, 1.5)
S.text('főbiztosíték ELŐTT ágazik le (D54)', 20, 28, 1.5)
left = [('+24V_IN', '+24V_IN'), ('+24V_P', None), ('V_BUS_P', None), ('HW_ID', 'HW_ID')]
right = [('PA8', 'CH1_PWM'), ('PA9', 'CH2_PWM'), ('PA10', 'CH3_PWM'), ('PC6', 'CH4_PWM'), ('PC7', 'CH5_PWM'),
         ('PC8', 'CH6_PWM'), ('PB12', 'DRV_EN'), ('PA7', 'I_SENSE'), ('PA4', 'DAC_THR'), ('PC2', 'V_RAIL_SENSE'),
         ('PC3', 'NTC'), ('PA0', 'DS1'), ('PA1', 'DS2'), ('PA2', 'DS3'), ('PA3', 'DS4'), ('PA5', 'DS5'), ('PA6', 'DS6'),
         ('PB8', None), ('PB9', None), ('PB11', None), ('PB13', None), ('PB14', None), ('PB15', None)]
S.subsheet('modulmag', '../modulmag/modulmag.kicad_sch', 30, 35, 40, 2.54 * (len(right) + 1), left=left, right=right)

# HW-ID (MODULMAG-SPEC 3.5): LED = 10k / 3,3k → 0,82 V → 2. sáv
S.text('HW-ID: LED-modul = 2. sáv (0,82 V)', 20, 112)
R('R201', '10k 1%', 25, 120, '+3V3', 'HW_ID')
R('R202', '3k3 1%', 25, 135, 'HW_ID', 'GND')
C('C201', '100n', 38, 135, 'HW_ID', 'GND')

# =================== 1. Betáp: főbiztosíték + ideális dióda ===================
S.text('1. BETÁP (20 A): J201 → F201 20 A (mini lapos) → ideális dióda (U204 LM74700-Q1 + Q201) → +24V_RAIL', 110, 22, 1.5)
S.text('fordított polaritás ellen, GND-eltolódás nélkül (D65); Q201 hiányában S–D dróttal áthidalható', 110, 27)
y = 40
S.comp('Connector_Generic:Conn_01x02', 'J201', '24V IN 20A', 112, y, {'1': '+24V_IN', '2': 'GND'}, fp=TB2,
       props=note('push-in, 2,5 mm², ≥ 20 A – helyőrző, a DIN-ház szerint; barna = +24 V, kék = GND (D43)'))
S.comp('Device:Fuse', 'F201', '20A', 135, y, {'1': '+24V_IN', '2': '+24V_F'},
       fp='Fuse:Fuseholder_Blade_Mini_Keystone_3568', props=note('mini lapos autós biztosíték, NYÁK-foglalat'))
S.comp('Power_Management:LM74700', 'U204', 'LM74700-Q1', 175, y + 20,
       {'1': 'IDEAL_VCAP', '2': 'GND', '3': '+24V_F', '4': '+24V_RAIL', '5': 'IDEAL_GATE', '6': '+24V_F'},
       fp='Package_TO_SOT_SMD:SOT-23-6', props=note('TI ideális dióda-vezérlő; EN az ANODE-ra (mindig BE)'))
C('C202', '100n', 150, y + 25, 'IDEAL_VCAP', '+24V_F', props=note('VCAP–ANODE, ≥ 0,1 µF, X7R, ≥ 25 V'))
S.comp('Transistor_FET:NTMFS016N06CT1G', 'Q201', 'NTMFS5C604NL', 175, y - 5,
       {'1': '+24V_F', '2': '+24V_F', '3': '+24V_F', '4': 'IDEAL_GATE', '5': '+24V_RAIL'},
       fp='Package_SO:ONSemi_SO-8FL_488AA',
       props={'Megjegyzés': 'onsemi 60 V, ~1,2 mΩ, SO-8FL; S = bemenet, D = sín. Nagy padek: ha nincs FET, S–D vastag dróttal áthidalható',
              'Description': 'N-MOSFET 60 V, ~1,2 mΩ (onsemi NTMFS5C604NL)'})
S.comp('Device:D_Zener', 'D201', 'SMBJ28A', 215, y, {'1': '+24V_RAIL', '2': 'GND'}, fp='Diode_SMD:D_SMB', r=90,
       props=note('TVS a sínen – a P78E05-ös logikai ágon a modulmag D2-je véd'))
S.comp('Device:C_Polarized', 'C203', '470µ/50V', 235, y, {'1': '+24V_RAIL', '2': 'GND'},
       fp='Capacitor_THT:CP_Radial_D10.0mm_P5.00mm', props=note('low-ESR, 105 °C; a GND-oldala a sönt ELŐTT (a sönt a FET-áramot méri)'))
for i, x in enumerate((252, 265, 278)):
    C(f'C{204 + i}', '10µ/50V', x, y, '+24V_RAIL', 'GND', fp=C1210, props=note('a FET-ek mellett, csatornapáronként egy'))
# V_RAIL mérés (D47)
R('R203', '100k', 300, y, '+24V_RAIL', 'V_RAIL_SENSE')
R('R204', '10k', 315, y, 'V_RAIL_SENSE', 'GND')
C('C207', '100n', 328, y, 'V_RAIL_SENSE', 'GND')
S.text('V_RAIL: 24 V → 2,2 V (PC2); a VIN_SENSE-szel (PC1)', 295, y + 12)
S.text('együtt a kiégett F201 / hibás Q201 jelezhető', 295, y + 16)

# 12 V a gate-meghajtóknak
S.comp('Regulator_Linear:MC78L12_SO8', 'U205', 'MC78L12ACDR2G', 300, 75,
       {'8': '+24V_RAIL', '1': '+12V', '2': 'GND', '3': 'GND', '6': 'GND', '7': 'GND'}, nc=['4', '5'],
       fp='Package_SO:SOIC-8_3.9x4.9mm_P1.27mm')
C('C208', '1µ/50V', 285, 85, '+24V_RAIL', 'GND', fp=C0805)
C('C209', '10µ/25V', 318, 85, '+12V', 'GND', fp=C1206)

# =================== 2. Kimeneti blokkok ===================
S.text('2. KIMENETI BLOKKOK: [+24 V, CHa, CHb] × 3, blokkonként SMD biztosíték (D65) – a szalagok közös vezetéke a +24 V (low-side, D43)', 110, 100, 1.5)
for k in range(1, 4):
    x = 120 + (k - 1) * 95
    S.comp('Device:Fuse', f'F{201 + k}', '10A', x, 112, {'1': '+24V_RAIL', '2': f'+24V_B{k}'},
           fp='Fuse:Fuse_Littelfuse-NANO2-451_453',
           props=note('Littelfuse 451/453 NANO² (2410), pl. 0451010.MRL – értéke a szalag szerint (≤ 10 A)'))
    S.comp('Connector_Generic:Conn_01x03', f'J{201 + k}', f'BLOKK {k}', x + 25, 115,
           {'1': f'+24V_B{k}', '2': f'CH{2 * k - 1}_D', '3': f'CH{2 * k}_D'}, fp=TB3,
           props=note(f'1 = +24 V, 2 = CH{2 * k - 1}, 3 = CH{2 * k}; push-in, ≥ 10 A/pólus – helyőrző'))

# =================== 3. Gate-meghajtók ===================
S.text('3. GATE-MEGHAJTÓK – 3 × UCC27524 (12 V): EN közösen a DRV_EN-en (PB12), 1 k lehúzás → bekapcsoláskor minden csatorna KI', 110, 135, 1.5)
S.text('6 EN-láb belső 200 k felhúzása a 12 V-ra párhuzamosan ~33 k → 1 k-val ~0,35 V (< 0,8 V); az IN-lábakon 120 k belső lehúzás is van', 110, 139)
R('R205', '1k', 112, 150, 'DRV_EN', 'GND', props=note('NE legyen nagyobb: 4,7 k-val ~1,5 V → a driverek engedélyezve lehetnek'))
for d in range(3):
    x = 130 + d * 75
    a, b = 2 * d + 1, 2 * d + 2
    S.comp('Driver_FET:UCC27524D', f'U{201 + d}', 'UCC27524DR', x, 160,
           {'1': 'DRV_EN', '2': f'CH{a}_PWM', '3': 'GND', '4': f'CH{b}_PWM', '5': f'CH{b}_GD', '6': '+12V',
            '7': f'CH{a}_GD', '8': 'DRV_EN'}, fp='Package_SO:SOIC-8_3.9x4.9mm_P1.27mm')
    C(f'C{210 + 2 * d}', '1µ/25V', x + 22, 150, '+12V', 'GND', fp=C0805)
    C(f'C{211 + 2 * d}', '100n', x + 32, 150, '+12V', 'GND')

# =================== 4. Csatornák ===================
S.text('4. CSATORNÁK (× 6): FET NTD5C648NL (DPAK; tartalék IRFR1205) · szabadonfutó B360B a blokk +24 V-jára · RC snubber (DNP)', 20, 183, 1.5)
S.text('gate-LED (driver kimenet) + drain-LED (a blokk +24 V-ja → drain) · drain → ADC osztó (D65)', 20, 188)
pa = {1: 'PA0', 2: 'PA1', 3: 'PA2', 4: 'PA3', 5: 'PA5', 6: 'PA6'}
for n in range(1, 7):
    k = (n + 1) // 2
    x = 25 + (n - 1) * 65
    y0 = 200
    R(f'R{210 + n}', '10R', x, y0, f'CH{n}_GD', f'CH{n}_G', props=note('gate-ellenállás (élmeredekség, EMC)'))
    S.comp('Transistor_FET:QM6006D', f'Q{201 + n}', 'NTD5C648NL', x + 20, y0 + 15,
           {'1': f'CH{n}_G', '2': f'CH{n}_D', '3': 'PGND_SH'}, fp='Package_TO_SOT_SMD:TO-252-2',
           props={'Megjegyzés': 'onsemi 60 V, ~4–5 mΩ, DPAK; tartalék: IRFR1205 (kis áramra)',
                  'Description': 'N-MOSFET 60 V, DPAK (onsemi NTD5C648NL)'})
    R(f'R{220 + n}', '10k', x, y0 + 22, f'CH{n}_G', 'PGND_SH', props=note('gate–source lehúzás'))
    S.comp('Device:D_Schottky', f'D{210 + n}', 'B360B', x + 35, y0, {'1': f'+24V_B{k}', '2': f'CH{n}_D'},
           fp='Diode_SMD:D_SMB', r=90, props=note('szabadonfutó, 3 A / 60 V, SMB'))
    # snubber (DNP)
    R(f'R{230 + n}', '10R', x + 48, y0 + 8, f'CH{n}_D', f'CH{n}_SN', fp=R1206, dnp=True, props=note('RC snubber – csak mérés után (D24)'))
    C(f'C{220 + n}', '2n2/100V', x + 48, y0 + 22, f'CH{n}_SN', 'PGND_SH', fp=C1206, dnp=True)
    # gate-LED
    R(f'R{240 + n}', '4k7', x, y0 + 38, f'CH{n}_GD', f'GLED{n}')
    LED(f'D{220 + n}', x, y0 + 50, f'GLED{n}', 'GND', f'CH{n} gate – előlap, fényvezető')
    # drain-LED
    R(f'R{250 + n}', '10k', x + 18, y0 + 38, f'+24V_B{k}', f'DLED{n}', fp=R0805)
    LED(f'D{230 + n}', x + 18, y0 + 50, f'DLED{n}', f'CH{n}_D', f'CH{n} kimenet (drain) – előlap')
    # drain → ADC
    R(f'R{260 + n}', '470k', x + 36, y0 + 38, f'CH{n}_D', f'DS{n}')
    R(f'R{270 + n}', '56k', x + 36, y0 + 52, f'DS{n}', 'GND')
    C(f'C{230 + n}', '10n', x + 48, y0 + 52, f'DS{n}', 'GND')
S.text('Drain → ADC: 24 V → 2,55 V (PA0–PA3, PA5, PA6). KI: ≈ V_RAIL = szalag rajta; ≈ V_RAIL − ~2 V = nincs szalag (a drain-LED-en át, halványan dereng); '
       '~0 V = kiolvadt blokk-biztosíték', 20, 266)
S.text('BE: ≈ V_RAIL × (1 − kitöltés); mindig ~0 V = átütött FET. A „nincs szalag” biztosan az önteszt áramméréséből (D47) látszik.', 20, 270)

# =================== 5. Árammérés, túláramvédelem ===================
S.text('5. ÖSSZ-ÁRAM (D47, D53)', 330, 132, 1.5)
S.text('1 mΩ sönt: PGND_SH (FET-source-ok) → GND, Kelvin', 330, 136)
S.text('INA181A2 (×50) → PA7: ADC + COMP2 → TIM1/TIM8 break', 330, 140)
S.text('küszöb: DAC1 (PA4); 20 A → 1,0 V', 330, 144)
S.comp('Device:R_Shunt', 'R209', '1m 1%', 330, 165, {'1': 'PGND_SH', '2': 'ISNS_P', '3': 'ISNS_N', '4': 'GND'},
       fp='Resistor_SMD:R_Shunt_Vishay_WSK2512_6332Metric_T1.19mm',
       props=note('2512, ≥ 1 W (20 A-en 0,4 W), Kelvin – pl. Vishay WSK2512 / WSLP2512'))
S.comp('Amplifier_Current:INA181', 'U206', 'INA181A2IDBVR', 355, 165,
       {'1': 'INA_OUT', '2': 'GND', '3': 'ISNS_P', '4': 'ISNS_N', '5': 'GND', '6': '+3V3'})
C('C240', '100n', 370, 152, '+3V3', 'GND')
R('R207', '100R', 387, 165, 'INA_OUT', 'I_SENSE', r=90)
C('C241', '1n', 398, 172, 'I_SENSE', 'GND')
S.comp('Connector:TestPoint', 'TP201', 'DAC_THR', 390, 150, {'1': 'DAC_THR'}, fp='TestPoint:TestPoint_Pad_D1.5mm',
       props=note('PA4 = DAC1_OUT1, a COMP2 küszöbe – kívül nincs bekötve'))
S.comp('Connector:TestPoint', 'TP202', 'I_SENSE', 402, 150, {'1': 'I_SENSE'}, fp='TestPoint:TestPoint_Pad_D1.5mm')
# NTC (a FET-ek között)
S.text('NTC a FET-ek között (PC3)', 362, 108)
R('R208', '10k 1%', 365, 120, '+3V3', 'NTC')
S.comp('Device:Thermistor_NTC', 'TH201', '10k B3435', 380, 120, {'1': 'NTC', '2': 'GND'},
       fp='Resistor_SMD:R_0603_1608Metric', props=note('a FET-ek között, a NYÁK-on (D30 – harmadik védelmi réteg)'))
C('C242', '100n', 395, 120, 'NTC', 'GND')

# PWR_FLAG-ek
for i, n in enumerate(['+24V_F', '+24V_RAIL', 'PGND_SH', '+24V_IN']):
    S.flag(n, 235 + i * 14, 75)
S.text('VÁZLAT – generálva a MODULMAG-SPEC + D43/D47/D53/D65 alapján (2026-10-14). Elrendezést rendezd; a bekötés címkékkel kész.', 20, 287, 1.5)
S.write(OUT)
print('ok', OUT)
