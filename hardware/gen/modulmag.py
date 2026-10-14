"""Modulmag – first draft from docs/kontextus/MODULMAG-SPEC.md (A változat)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import kigen
kigen.POWER_UP = {'+3V3', '+5V'}
kigen.POWER_DOWN = {'GND', 'GND_BUS'}

OUT = sys.argv[1]
S = kigen.Sheet('Modulmag – STM32F303RET6 + izolált CAN + 24 V → 5 V → 3,3 V', 'modulmag')
# a modulmag a három modul hierarchikus lapja is → ott is legyenek hivatkozásai
S.extra_inst = [(p, f'/{kigen.root_uuid(p)}/{kigen.sheet_uuid(p, "modulmag")}')
                for p in ('rele-modul', 'led-modul', 'bemeneti-modul')]
S.power_lib['GND_BUS'] = 'modularis:GND_BUS'
S.use('modularis:GND_BUS', lib='modularis', name='GND_BUS', libpath='/home/balazs/dev/szakdolgozat/hardware/lib/modularis.kicad_sym')
S.use('modularis:ISO1042BDWV', lib='modularis', name='ISO1042BDWV')

S.hier = {'+24V_IN', '+24V_P', 'V_BUS_P', 'HW_ID', 'PC2', 'PC3', 'PB8', 'PB9', 'PB11', 'PB12', 'PB13', 'PB14', 'PB15',
          'PC6', 'PC7', 'PC8'} | {f'PA{i}' for i in range(11)}

R0603 = 'Resistor_SMD:R_0603_1608Metric'
C0603 = 'Capacitor_SMD:C_0603_1608Metric'

def N(note, k):
    if note:
        k.setdefault('props', {})['Megjegyzés'] = note
    return k

def R(ref, val, x, y, a, b, fp=R0603, note=None, **k):
    S.comp('Device:R', ref, val, x, y, {'1': a, '2': b}, fp=fp, **N(note, k))

def C(ref, val, x, y, a, b, fp=C0603, note=None, **k):
    S.comp('Device:C', ref, val, x, y, {'1': a, '2': b}, fp=fp, **N(note, k))

S.label_dx.update({'MCU_ST_STM32F3:STM32F303RETx': 20.32, 'modularis:ISO1042BDWV': 10.16,
                   'Converter_DCDC:R-78E5.0-1.0': 10.16, 'Regulator_Linear:NCP1117-3.3_SOT223': 10.16,
                   'Connector_Generic:Conn_01x04': 5.08, 'Connector_Generic:Conn_01x07': 5.08,
                   'Device:Crystal_GND24': 5.08, 'Power_Protection:NUP2105L': 5.08})

# ---------------- 2. Tápblokk (A változat) ----------------
S.text('2. TÁP: +24V_IN → F1 → D1 → R6 → +24V_P → P78E05 (5 V) → NCP1117 (3,3 V)   (D56, D57 – a 24 V-os tápot ≤ 26 V-ra!)', 20, 25, 2)
y = 45
S.comp('Device:Fuse', 'F1', '0,5A', 20, y, {'1': '+24V_IN', '2': '+24V_F1'}, fp='Fuse:Fuse_1206_3216Metric', props={'Megjegyzés': '≥ 32 V, gyors, 1206'})
S.comp('Device:D_Schottky', 'D1', 'SS16', 42, y, {'2': '+24V_F1', '1': '+24V_D1'}, fp='Diode_SMD:D_SMA')
R('R6', '10R', 65, y, '+24V_D1', '+24V_P', fp='Resistor_SMD:R_1206_3216Metric', note='impulzusbíró (pl. ERJ-P08); 0 Ω-mal áthidalható (D57)')
S.comp('Device:D_Zener', 'D2', 'SMBJ28A', 85, y, {'1': '+24V_P', '2': 'GND'}, fp='Diode_SMD:D_SMB', r=90)
S.comp('Device:C_Polarized', 'C12', '47µ/50V', 105, y, {'1': '+24V_P', '2': 'GND'}, fp='Capacitor_SMD:CP_Elec_6.3x7.7', props={'Megjegyzés': 'elektrolit, low-ESR, 105 °C – KÖTELEZŐ (D57)'})
C('C1', '10µ/50V', 125, y, '+24V_P', 'GND', fp='Capacitor_SMD:C_1210_3225Metric')
S.comp('Converter_DCDC:R-78E5.0-1.0', 'U1', 'P78E05-1000', 150, y, {'1': '+24V_P', '2': 'GND', '3': '+5V'},
       fp='Converter_DCDC:Converter_DCDC_RECOM_R-78E-0.5_THT')
C('C2', '22µ/10V', 180, y, '+5V', 'GND', fp='Capacitor_SMD:C_1206_3216Metric')
S.comp('Regulator_Linear:NCP1117-3.3_SOT223', 'U5', 'NCP1117ST33T3G', 205, y, {'3': '+5V', '1': 'GND', '2': '+3V3'})
S.comp('Device:C_Polarized', 'C3', '10µ tantál', 235, y, {'1': '+3V3', '2': 'GND'}, props={'Megjegyzés': 'ESR 0,1–2 Ω (NCP1117 stabilitás) – vagy 22 µF kerámia + 0,1 Ω'},
       fp='Capacitor_Tantalum_SMD:CP_EIA-3216-18_Kemet-A')
R('R3', '150k', 255, y, '+24V_P', 'VIN_SENSE')
R('R4', '10k', 270, y, 'VIN_SENSE', 'GND')
C('C9', '100n', 285, y, 'VIN_SENSE', 'GND')
S.text('VIN_SENSE: 24 V → 1,5 V (PC1)', 250, 62)
# állapot-LED-ek (3.4)
R('R8', '2k2', 310, y, '+3V3', 'LED_PWR')
S.comp('Device:LED', 'D3', 'zöld', 325, y, {'2': 'LED_PWR', '1': 'GND'}, fp='LED_SMD:LED_0603_1608Metric', r=90)
R('R9', '1k', 345, y, '+3V3', 'LED_STAT')
S.comp('Device:LED', 'D4', 'piros', 360, y, {'2': 'LED_STAT', '1': 'STATUS_LED'}, fp='LED_SMD:LED_0603_1608Metric', r=90)

# ---------------- 3. STM32F303RET6 ----------------
S.text('3. STM32F303RET6 – a modulspecifikus lábak hierarchikus címkék (a modul lapja köti be vagy köti NC-re)', 20, 95, 2)
nets = {'1': '+3V3', '2': 'STATUS_LED', '5': 'OSC_IN', '6': 'OSC_OUT', '7': 'NRST', '8': 'HW_ID', '9': 'VIN_SENSE',
        '10': 'PC2', '11': 'PC3', '12': 'GND', '13': '+3V3A', '14': 'PA0', '15': 'PA1', '16': 'PA2', '17': 'PA3',
        '18': 'GND', '31': 'GND', '47': 'GND', '63': 'GND', '19': '+3V3', '32': '+3V3', '48': '+3V3', '64': '+3V3',
        '20': 'PA4', '21': 'PA5', '22': 'PA6', '23': 'PA7', '24': 'UART_TX', '25': 'UART_RX', '30': 'PB11',
        '33': 'PB12', '34': 'PB13', '35': 'PB14', '36': 'PB15', '37': 'PC6', '38': 'PC7', '39': 'PC8',
        '41': 'PA8', '42': 'PA9', '43': 'PA10', '44': 'CAN_RX', '45': 'CAN_TX', '46': 'SWDIO', '49': 'SWCLK',
        '60': 'BOOT0', '61': 'PB8', '62': 'PB9'}
nc = ['3', '4', '26', '27', '28', '29', '40', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59']
S.comp('MCU_ST_STM32F3:STM32F303RETx', 'U6', 'STM32F303RET6', 150, 165, nets, nc=nc,
       fp='Package_QFP:LQFP-64_10x10mm_P0.5mm')
# hidegítés (3.1)
y = 240
C('C4', '100n', 30, y, '+3V3', 'GND')
for i, x in enumerate((45, 60, 75, 90)):
    C(f'C{5 + i}', '100n', x, y, '+3V3', 'GND')
C('C13', '4µ7', 105, y, '+3V3', 'GND')
S.comp('Device:FerriteBead_Small', 'FB1', 'ferrit ≤0,1Ω', 125, y, {'1': '+3V3', '2': '+3V3A'}, fp='Inductor_SMD:L_0603_1608Metric')
C('C14', '1µ', 145, y, '+3V3A', 'GND')
C('C15', '10n', 160, y, '+3V3A', 'GND')
S.text('Hidegítés: lábanként 100 nF a saját VDD-lábánál; VDDA a 3V3-ról FB1-en át (nem jöhet fel később, mint a VDD)', 25, 255)
# órajel (3.2)
S.comp('Device:Crystal_GND24', 'Y1', '8MHz', 55, 130, {'1': 'OSC_IN', '3': 'OSC_OUT', '2': 'GND', '4': 'GND'},
       fp='Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm')
C('C10', '12p', 45, 150, 'OSC_IN', 'GND')
C('C11', '12p', 68, 150, 'OSC_OUT', 'GND', note='C = 2 × (CL − 3…5 pF) a választott kvarcból')
# reset, boot (3.3)
C('C16', '100n', 88, 135, 'NRST', 'GND')
R('R2', '10k', 103, 135, 'BOOT0', 'GND')
S.comp('Connector:TestPoint', 'TP1', 'BOOT0', 115, 125, {'1': 'BOOT0'}, fp='TestPoint:TestPoint_Pad_D1.5mm')
S.comp('Connector:TestPoint', 'TP2', '3V3', 125, 125, {'1': '+3V3'}, fp='TestPoint:TestPoint_Pad_D1.5mm')
# debug (3.6)
S.comp('Connector_Generic:Conn_01x07', 'J1', 'DEBUG', 40, 200,
       {'1': '+3V3', '2': 'SWCLK', '3': 'GND', '4': 'SWDIO', '5': 'NRST', '6': 'UART_TX', '7': 'UART_RX'},
       fp='Connector_PinHeader_2.54mm:PinHeader_1x07_P2.54mm_Vertical')
S.text('J1: 1 VTref · 2 SWCLK · 3 GND · 4 SWDIO · 5 NRST · 6 TX · 7 RX (ST-Link klón dupont-tal)', 20, 215)

# ---------------- 4. ISO1042 ----------------
S.text('4. IZOLÁLT CAN – ISO1042BDWV: a tok alatt minden rétegen rézmentes rés', 225, 95, 2)
S.comp('modularis:ISO1042BDWV', 'U2', 'ISO1042BDWV', 270, 140,
       {'1': '+3V3', '2': 'CAN_TX', '3': 'CAN_RX', '4': 'GND', '5': 'GND_BUS', '6': 'CAN_L', '7': 'CAN_H', '8': 'V_BUS_P'},
       fp='Package_SO:SOIC-8_7.5x5.85mm_P1.27mm')
R('R1', '10k', 245, 120, '+3V3', 'CAN_TX')
C('C17', '100n', 245, 165, '+3V3', 'GND')
C('C18', '100n', 300, 165, 'V_BUS_P', 'GND_BUS')
C('C19', '4µ7', 315, 165, 'V_BUS_P', 'GND_BUS')

# ---------------- 5. Busz-oldal ----------------
S.text('5. BUSZ-OLDAL (GND_BUS-tartomány): J2/J3 azonos tűi átmenők', 225, 195, 2)
bus = {'1': 'V_BUS_P', '2': 'GND_BUS', '3': 'CAN_L', '4': 'CAN_H'}
S.comp('Connector_Generic:Conn_01x04', 'J2', 'BUS_IN', 350, 215, bus, fp='Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical')
S.comp('Connector_Generic:Conn_01x04', 'J3', 'BUS_OUT', 350, 240, bus, fp='Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical')
S.comp('Device:D_Zener', 'D5', 'SMF5.0A', 255, 225, {'1': 'V_BUS_P', '2': 'GND_BUS'}, fp='Diode_SMD:D_SOD-123F', r=90, props={'Megjegyzés': 'ESD / hot-plug tüskék ellen, a J2/J3 mellé'})
S.comp('Power_Protection:NUP2105L', 'U3', 'ESD2CAN24-Q1', 275, 225, {'1': 'CAN_L', '2': 'CAN_H', '3': 'GND_BUS'})
S.comp('Jumper:Jumper_2_Open', 'JP1', 'LEZÁRÁS', 300, 225, {'1': 'CAN_H', '2': 'CAN_TERM'},
       fp='Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical')
R('R5', '120R', 320, 225, 'CAN_TERM', 'CAN_L', fp='Resistor_SMD:R_0805_2012Metric')
S.text('D55 lezárva: a buszon nincs 24 V → nincs PTC; a TVS az ESD / hot-plug ellen. Zárlatvédelem: a vezérlő TPS2553-a', 225, 255)

# ---------------- PWR_FLAG-ek ----------------
for i, n in enumerate(['+24V_P', 'GND', 'GND_BUS', 'V_BUS_P', '+3V3A']):
    S.flag(n, 160 + i * 14, 268)
S.text('VÁZLAT – generálva a MODULMAG-SPEC.md alapján (2026-10-14). Elrendezést rendezd; a bekötés címkékkel kész.', 20, 285, 1.5)
S.write(OUT)
print('ok', OUT)
