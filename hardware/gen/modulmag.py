"""Modulmag – a MODULMAG-SPEC.md szerint, elrendezett (vezetékes) változat.

Elrendezés: balra fent a táp (24 V → 5 V → 3,3 V, balról jobbra), középen az STM32, tőle balra a reset/boot,
kvarc, debug és állapot-LED, alatta a hidegítés; jobbra az izolált CAN (ISO1042) és a busz-oldal (GND_BUS).
Blokkon belül vezeték, blokkok között / MCU-lábakon címke.
"""
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
S.use('modularis:GND_BUS', lib='modularis', name='GND_BUS',
      libpath=os.path.join(os.path.dirname(__file__), '..', 'lib', 'modularis.kicad_sym'))
S.use('modularis:ISO1042BDWV', lib='modularis', name='ISO1042BDWV')

S.hier = {'+24V_IN', '+24V_P', 'V_BUS_P', 'HW_ID', 'PC2', 'PC3', 'PB8', 'PB9', 'PB11', 'PB12', 'PB13', 'PB14', 'PB15',
          'PC6', 'PC7', 'PC8'} | {f'PA{i}' for i in range(11)}

R0603 = 'Resistor_SMD:R_0603_1608Metric'
C0603 = 'Capacitor_SMD:C_0603_1608Metric'
S.label_dx.update({'MCU_ST_STM32F3:STM32F303RETx': 20.32, 'modularis:ISO1042BDWV': 10.16,
                   'Converter_DCDC:R-78E5.0-1.0': 10.16, 'Regulator_Linear:NCP1117-3.3_SOT223': 10.16,
                   'Connector_Generic:Conn_01x04': 5.08, 'Connector_Generic:Conn_01x07': 5.08,
                   'Device:Crystal_GND24': 5.08, 'Power_Protection:NUP2105L': 5.08})


S.label_pos.update({
    'MCU_ST_STM32F3:STM32F303RETx': ((-15.24, -47.0), (5.08, 50.8)),
    'modularis:ISO1042BDWV': ((-7.62, -7.62), (-7.62, 10.16)),
    'Converter_DCDC:R-78E5.0-1.0': ((-7.62, -8.89), (-7.62, -6.35)),
    'Regulator_Linear:NCP1117-3.3_SOT223': ((-7.62, -8.89), (-7.62, -6.35)),
})


def P(note):
    return {'Megjegyzés': note} if note else None


def up(net, p):
    """tápszimbólum / címke a pont fölé"""
    S.label(net, p, 90)


def down(net, p):
    S.label(net, p, 270)


def shunt(lib, ref, val, top, bottom_net, fp, r=0, top_pin='1', bot_pin='2', **k):
    """függőleges kétlábú alkatrész: felső lába `top`-ban, alsó lába a `bottom_net`-re (szimbólum/címke)"""
    pp = S.place(lib, ref, val, {top_pin: None, bot_pin: bottom_net}, top_pin, top, r=r, fp=fp, **k)
    return pp


def series(lib, ref, val, left, fp, r=90, lpin='1', rpin='2', **k):
    """vízszintes kétlábú alkatrész, bal lába `left`-ben; visszaadja a jobb láb pontját"""
    pp = S.place(lib, ref, val, {lpin: None, rpin: None}, lpin, left, r=r, fp=fp, **k)
    return pp[rpin][:2]


# =====================================================================================================
# 1. TÁP – +24V_IN → F1 → D1 → R6 → +24V_P → P78E05 (5 V) → NCP1117 (3,3 V)
# =====================================================================================================
S.text('1. TÁP: +24V_IN → F1 → D1 → R6 → +24V_P → U1 P78E05 (5 V) → U5 NCP1117 (3,3 V)', 20, 25, 1.6)
S.text('D56, D57 – a C12 elkó kötelező; a 24 V-os tápot ≤ 26 V-ra! (a P78E05 max. 36 V)', 20, 30)
Y = 45
x0 = 30
S.label('+24V_IN', (x0, Y), 180)
p = series('Device:Fuse', 'F1', '0,5A', (x0 + 5, Y), 'Fuse:Fuse_1206_3216Metric', props=P('≥ 32 V, gyors, 1206'))
S.wire((x0, Y), (x0 + 5, Y))
a = (p[0] + 5, Y)
S.wire(p, a)
p = series('Device:D_Schottky', 'D1', 'SS16', a, 'Diode_SMD:D_SMA', r=180, lpin='2', rpin='1',
           props=P('fordított polaritás ellen'))
a = (p[0] + 5, Y)
S.wire(p, a)
p = series('Device:R', 'R6', '10R', a, 'Resistor_SMD:R_1206_3216Metric',
           props=P('impulzusbíró (pl. ERJ-P08); 0 Ω-mal áthidalható (D57)'))
# +24V_P sín
taps = [75, 87.5, 100, 112.5]
xin = 135
S.rail(Y, [p[0], p[0] + 2.54] + taps + [xin])
S.wire((p[0] + 2.54, Y), (p[0] + 2.54, Y - 7.62))
S.label('+24V_P', (p[0] + 2.54, Y - 7.62), 90)
shunt('Device:D_Zener', 'D2', 'SMBJ28A', (taps[0], Y + 5.08), 'GND', 'Diode_SMD:D_SMB', r=270, top_pin='1', bot_pin='2',
      props=P('TVS, 28 V standoff'))
S.wire((taps[0], Y), (taps[0], Y + 5.08))
shunt('Device:C_Polarized', 'C12', '47µ/50V', (taps[1], Y + 5.08), 'GND', 'Capacitor_SMD:CP_Elec_6.3x7.7',
      props=P('elektrolit, low-ESR, 105 °C – KÖTELEZŐ (D57)'))
S.wire((taps[1], Y), (taps[1], Y + 5.08))
shunt('Device:C', 'C1', '10µ/50V', (taps[2], Y + 5.08), 'GND', 'Capacitor_SMD:C_1210_3225Metric')
S.wire((taps[2], Y), (taps[2], Y + 5.08))
# VIN_SENSE osztó: R3 150k / R4 10k, C9 100n
shunt('Device:R', 'R3', '150k', (taps[3], Y + 5.08), None, R0603)
S.wire((taps[3], Y), (taps[3], Y + 5.08))
nv = (taps[3], Y + 15.24)
S.wire((taps[3], Y + 12.7), nv)
shunt('Device:R', 'R4', '10k', (taps[3], Y + 17.78), 'GND', R0603)
S.wire(nv, (taps[3], Y + 17.78))
shunt('Device:C', 'C9', '100n', (taps[3] + 7.62, Y + 17.78), 'GND', C0603)
S.wire(nv, (taps[3] + 7.62, Y + 15.24), (taps[3] + 7.62, Y + 17.78))
S.wire((taps[3] + 7.62, Y + 15.24), (taps[3] + 15.24, Y + 15.24))
S.label('VIN_SENSE', (taps[3] + 15.24, Y + 15.24), 0)
S.junction(nv)
S.junction((taps[3] + 7.62, Y + 15.24))
S.text('VIN_SENSE: 24 V → 1,5 V (PC1)', taps[3] - 2, Y + 32)
# U1 P78E05
pp = S.place('Converter_DCDC:R-78E5.0-1.0', 'U1', 'P78E05-1000', {'1': None, '2': 'GND', '3': None}, '1', (xin, Y),
             fp='Converter_DCDC:Converter_DCDC_RECOM_R-78E-0.5_THT')
xo = pp['3'][0]
# +5V sín
t5 = [xo + 10, xo + 20]
xin5 = xo + 32.5
S.rail(Y, [xo] + t5 + [xin5])
shunt('Device:C', 'C2', '22µ/10V', (t5[0], Y + 5.08), 'GND', 'Capacitor_SMD:C_1206_3216Metric')
S.wire((t5[0], Y), (t5[0], Y + 5.08))
S.wire((t5[1], Y), (t5[1], Y - 5.08))
up('+5V', (t5[1], Y - 5.08))
pp = S.place('Regulator_Linear:NCP1117-3.3_SOT223', 'U5', 'NCP1117ST33T3G', {'3': None, '1': 'GND', '2': None}, '3', (xin5, Y))
xo3 = pp['2'][0]
t3 = [xo3 + 10, xo3 + 20]
S.rail(Y, [xo3] + t3)
S.junction((t3[0], Y))
shunt('Device:C_Polarized', 'C3', '10µ tantál', (t3[0], Y + 5.08), 'GND', 'Capacitor_Tantalum_SMD:CP_EIA-3216-18_Kemet-A',
      props=P('ESR 0,1–2 Ω (NCP1117 stabilitás) – vagy 22 µF kerámia + 0,1 Ω'))
S.wire((t3[0], Y), (t3[0], Y + 5.08))
S.wire((t3[1], Y), (t3[1], Y - 5.08))
up('+3V3', (t3[1], Y - 5.08))

# Állapot-LED-ek (3.4) – a táp mellett jobbra
xl = 300
S.text('ÁLLAPOT-LED-ek (előlap, fényvezető)', xl - 5, 30)
up('+3V3', (xl, 37))
S.wire((xl, 37), (xl, 40))
shunt('Device:R', 'R8', '2k2', (xl, 40), None, R0603)
pp = S.place('Device:LED', 'D3', 'zöld', {'2': None, '1': 'GND'}, '2', (xl, 52.7), r=90, fp='LED_SMD:LED_0603_1608Metric',
             props=P('táp-LED'))
S.wire((xl, 47.62), (xl, 52.7))
xl2 = xl + 20
up('+3V3', (xl2, 37))
S.wire((xl2, 37), (xl2, 40))
shunt('Device:R', 'R9', '1k', (xl2, 40), None, R0603)
S.place('Device:LED', 'D4', 'piros', {'2': None, '1': None}, '2', (xl2, 52.7), r=90, fp='LED_SMD:LED_0603_1608Metric',
        props=P('állapot-LED, a PC13 nyeli'))
S.wire((xl2, 47.62), (xl2, 52.7))
S.wire((xl2, 60.32), (xl2, 64))
S.label('STATUS_LED', (xl2, 64), 270)

# =====================================================================================================
# 2. STM32F303RET6
# =====================================================================================================
S.text('2. STM32F303RET6 – a modulspecifikus lábak hierarchikus címkék (a modul lapja köti be vagy hagyja üresen)', 120, 88, 1.6)
MX, MY = 215, 160
nets = {'1': None, '19': None, '32': None, '48': None, '64': None, '13': None, '12': None,
        '18': None, '31': None, '47': None, '63': None,
        '2': 'STATUS_LED', '5': 'OSC_IN', '6': 'OSC_OUT', '7': 'NRST', '8': 'HW_ID', '9': 'VIN_SENSE',
        '10': 'PC2', '11': 'PC3', '14': 'PA0', '15': 'PA1', '16': 'PA2', '17': 'PA3',
        '20': 'PA4', '21': 'PA5', '22': 'PA6', '23': 'PA7', '24': 'UART_TX', '25': 'UART_RX', '30': 'PB11',
        '33': 'PB12', '34': 'PB13', '35': 'PB14', '36': 'PB15', '37': 'PC6', '38': 'PC7', '39': 'PC8',
        '41': 'PA8', '42': 'PA9', '43': 'PA10', '44': 'CAN_RX', '45': 'CAN_TX', '46': 'SWDIO', '49': 'SWCLK',
        '60': 'BOOT0', '61': 'PB8', '62': 'PB9'}
nc = ['3', '4', '26', '27', '28', '29', '40', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59']
pp = S.comp('MCU_ST_STM32F3:STM32F303RETx', 'U6', 'STM32F303RET6', MX, MY, nets, nc=nc,
            fp='Package_QFP:LQFP-64_10x10mm_P0.5mm')
# VDD-lábak (1 VBAT, 19, 32, 48, 64) egy sínre, VDDA (13) külön
yt = pp['1'][1] - 5.08
for n in ('1', '19', '32', '48', '64'):
    S.wire(pp[n][:2], (pp[n][0], yt))
S.rail(yt, [pp['1'][0] - 5.08] + [pp[n][0] for n in ('1', '19', '32', '48', '64')], junctions=False)
for n in ('19', '32', '48'):
    S.junction((pp[n][0], yt))
up('+3V3', (pp['1'][0] - 5.08, yt))
S.wire(pp['13'][:2], (pp['13'][0], yt - 2.54))
S.label('+3V3A', (pp['13'][0], yt - 2.54), 90)
# VSS (18/31/47/63 egymáson) + VSSA (12)
yb = pp['18'][1] + 5.08
S.wire(pp['18'][:2], (pp['18'][0], yb))
S.wire(pp['12'][:2], (pp['12'][0], yb))
S.wire((pp['18'][0], yb), (pp['12'][0], yb))
down('GND', (pp['18'][0], yb))

# Reset, BOOT0 – közvetlenül az MCU bal oldalán (az MCU-lábon címke, a kis áramkör vezetékkel)
xr = 150
S.text('RESET / BOOT0', xr - 15, 100)
S.label('NRST', (xr, 110), 0)
S.wire((xr, 110), (xr - 10, 110))
shunt('Device:C', 'C16', '100n', (xr - 10, 112.54), 'GND', C0603)
S.wire((xr - 10, 110), (xr - 10, 112.54))
S.label('BOOT0', (xr, 128), 0)
S.wire((xr, 128), (xr - 10, 128))
shunt('Device:R', 'R2', '10k', (xr - 10, 130.54), 'GND', R0603, props=P('BOOT0 lehúzás – normál indulás a flashből'))
S.wire((xr - 10, 128), (xr - 10, 130.54))
S.wire((xr - 10, 128), (xr - 20, 128))
S.junction((xr - 10, 128))
S.place('Connector:TestPoint', 'TP1', 'BOOT0', {'1': None}, '1', (xr - 20, 128), r=90, fp='TestPoint:TestPoint_Pad_D1.5mm',
        props=P('3V3-ra húzva: ROM-bootloader (USART1)'))
S.place('Connector:TestPoint', 'TP2', '3V3', {'1': '+3V3'}, '1', (xr - 20, 140), r=90, fp='TestPoint:TestPoint_Pad_D1.5mm')

# Kvarc (3.2)
xc, yc = 145, 160
S.text('HSE 8 MHz', xc - 12, yc - 9)
pp = S.place('Device:Crystal_GND24', 'Y1', '8MHz', {'1': None, '3': None, '2': 'GND', '4': 'GND'}, '1', (xc, yc),
             fp='Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm')
x1, x3 = pp['1'][0], pp['3'][0]
S.wire((x1, yc), (x1 - 7.62, yc))
S.wire((x3, yc), (x3 + 7.62, yc))
shunt('Device:C', 'C10', '12p', (x1 - 7.62, yc + 2.54), 'GND', C0603)
S.wire((x1 - 7.62, yc), (x1 - 7.62, yc + 2.54))
shunt('Device:C', 'C11', '12p', (x3 + 7.62, yc + 2.54), 'GND', C0603, props=P('C = 2 × (CL − 3…5 pF) a választott kvarcból'))
S.wire((x3 + 7.62, yc), (x3 + 7.62, yc + 2.54))
S.label('OSC_IN', (x1 - 7.62, yc), 180)
S.label('OSC_OUT', (x3 + 7.62, yc), 0)

# Debug (3.6)
xd, yd = 70, 125
S.text('DEBUG – J1: 1 VTref · 2 SWCLK · 3 GND · 4 SWDIO · 5 NRST · 6 TX · 7 RX', xd - 50, yd - 16)
S.text('(ST-Link klón dupont-tal; beültetés opcionális)', xd - 50, yd - 12)
pp = S.comp('Connector_Generic:Conn_01x07', 'J1', 'DEBUG', xd, yd, {str(i): None for i in range(1, 8)},
            fp='Connector_PinHeader_2.54mm:PinHeader_1x07_P2.54mm_Vertical')
for n, net in {'1': '+3V3', '2': 'SWCLK', '3': 'GND', '4': 'SWDIO', '5': 'NRST', '6': 'UART_TX', '7': 'UART_RX'}.items():
    a = pp[n][:2]
    b = (a[0] - 7.62, a[1])
    S.wire(a, b)
    if net == '+3V3':
        S.wire(b, (b[0], b[1] - 5.08))
        up('+3V3', (b[0], b[1] - 5.08))
    elif net == 'GND':
        S.label('GND', b, 180)
    else:
        S.label(net, b, 180)

# Hidegítés (3.1)
yh = 225
S.text('HIDEGÍTÉS: lábanként 100 nF a saját VDD-lábánál; VDDA a 3V3-ról FB1-en át', 25, yh - 12)
xs = [30, 42.7, 55.4, 68.1, 80.8, 93.5]
S.wire((25, yh), (xs[0], yh))
up('+3V3', (25, yh))
S.rail(yh, xs + [105])
for i, (x, ref, val) in enumerate(zip(xs, ['C4', 'C5', 'C6', 'C7', 'C8', 'C13'], ['100n'] * 5 + ['4µ7'])):
    shunt('Device:C', ref, val, (x, yh + 2.54), 'GND', C0603)
    S.wire((x, yh), (x, yh + 2.54))
p = series('Device:FerriteBead_Small', 'FB1', 'ferrit ≤0,1Ω', (105, yh), 'Inductor_SMD:L_0603_1608Metric',
           props=P('vagy 0 Ω'))
S.rail(yh, [p[0], p[0] + 10, p[0] + 22.7])
for x, ref, val in ((p[0] + 10, 'C14', '1µ'), (p[0] + 22.7, 'C15', '10n')):
    shunt('Device:C', ref, val, (x, yh + 2.54), 'GND', C0603)
    S.wire((x, yh), (x, yh + 2.54))
S.wire((p[0] + 22.7, yh), (p[0] + 30, yh))
S.label('+3V3A', (p[0] + 30, yh), 0)

# =====================================================================================================
# 3. IZOLÁLT CAN – ISO1042BDWV
# =====================================================================================================
IX, IY = 320, 125
S.text('3. IZOLÁLT CAN – ISO1042BDWV: a tok alatt minden rétegen rézmentes rés', 280, 88, 1.6)
S.text('logikai oldal (GND)                 busz-oldal (GND_BUS)', 290, 100)
pp = S.comp('modularis:ISO1042BDWV', 'U2', 'ISO1042BDWV', IX, IY,
            {'1': None, '2': None, '3': 'CAN_RX', '4': None, '5': None, '6': 'CAN_L', '7': 'CAN_H', '8': None},
            fp='Package_SO:SOIC-8_7.5x5.85mm_P1.27mm')
# VCC1 + C17, TXD felhúzás R1
v1 = pp['1'][:2]
xa = v1[0] - 7.62
N = (xa, v1[1] - 7.62)
S.wire(v1, (xa, v1[1]), N)
S.wire(N, (xa, N[1] - 5.08))
up('+3V3', (xa, N[1] - 5.08))
S.wire(N, (xa - 7.62, N[1]))
S.junction(N)
shunt('Device:C', 'C17', '100n', (xa - 7.62, N[1]), 'GND', C0603)
S.label('CAN_TX', pp['2'][:2], 180)
S.text('TXD felhúzás (bootkor recesszív busz):', IX - 62, IY + 14)
up('+3V3', (IX - 40, IY + 17))
S.wire((IX - 40, IY + 17), (IX - 40, IY + 19.54))
shunt('Device:R', 'R1', '10k', (IX - 40, IY + 19.54), 'CAN_TX', R0603)
g1 = pp['4'][:2]
S.wire(g1, (g1[0] - 2.54, g1[1]), (g1[0] - 2.54, g1[1] + 2.54))
down('GND', (g1[0] - 2.54, g1[1] + 2.54))
# VCC2 + C18/C19, GND2
v2 = pp['8'][:2]
xb = v2[0] + 7.62
S.wire(v2, (xb + 12.7, v2[1]))
S.junction((xb, v2[1]))
S.wire((xb, v2[1]), (xb, v2[1] - 7.62))
S.label('V_BUS_P', (xb, v2[1] - 7.62), 90)
for x, ref, val in ((xb + 5.08, 'C18', '100n'), (xb + 12.7, 'C19', '4µ7')):
    shunt('Device:C', ref, val, (x, v2[1] + 2.54), 'GND_BUS', C0603)
    S.wire((x, v2[1]), (x, v2[1] + 2.54))
S.junction((xb + 5.08, v2[1]))
g2 = pp['5'][:2]
S.wire(g2, (g2[0] + 2.54, g2[1]), (g2[0] + 2.54, g2[1] + 2.54))
down('GND_BUS', (g2[0] + 2.54, g2[1] + 2.54))

# =====================================================================================================
# 4. BUSZ-OLDAL (GND_BUS-tartomány): J2 BE / J3 KI átmenő, ESD, lezárás, TVS
# =====================================================================================================
S.text('4. BUSZ-OLDAL (GND_BUS): J2 és J3 azonos tűi átmenők; ESD és TVS a csatlakozók mellé', 280, 160, 1.6)
JX = 395
pj2 = S.comp('Connector_Generic:Conn_01x04', 'J2', 'BUS_IN', JX, 180, {'1': None, '2': None, '3': None, '4': None},
             fp='Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical')
pj3 = S.comp('Connector_Generic:Conn_01x04', 'J3', 'BUS_OUT', JX, 205, {'1': None, '2': None, '3': None, '4': None},
             fp='Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical')
lanes = {'1': JX - 12.7, '2': JX - 15.24, '3': JX - 17.78, '4': JX - 20.32}   # V_BUS_P, GND_BUS, CAN_L, CAN_H
for n, lx in lanes.items():
    S.wire(pj2[n][:2], (lx, pj2[n][1]), (lx, pj3[n][1]), pj3[n][:2])
# a sávok lefelé futnak tovább, és lépcsőzetesen balra fordulnak (nincs keresztezés) → címke
for i, n in enumerate(['4', '3', '1', '2']):        # CAN_H, CAN_L, V_BUS_P, GND_BUS
    lx = lanes[n]
    yt = pj3['4'][1] + 5.08 + i * 3.81
    S.junction((lx, pj3[n][1]))
    S.wire((lx, pj3[n][1]), (lx, yt), (JX - 40, yt))
    net = {'4': 'CAN_H', '3': 'CAN_L', '2': 'GND_BUS', '1': 'V_BUS_P'}[n]
    if net == 'GND_BUS':
        S.wire((JX - 40, yt), (JX - 40, yt + 2.54))
        down('GND_BUS', (JX - 40, yt + 2.54))
    else:
        S.label(net, (JX - 40, yt), 180)
# TVS (D5), ESD (U3), lezárás (JP1 + R5) – címkékkel, egy sorban
yp = 238
S.text('V_BUS TVS · CAN ESD · lezárás (JP1: csak a lánc két végén)', 248, yp - 12)
shunt('Device:D_Zener', 'D5', 'SMF5.0A', (253, yp), 'GND_BUS', 'Diode_SMD:D_SOD-123F', r=270,
      props=P('ESD / hot-plug tüskék ellen, a J2/J3 mellé'))
S.wire((253, yp), (253, yp - 5.08))
S.label('V_BUS_P', (253, yp - 5.08), 90)
pp = S.comp('Power_Protection:NUP2105L', 'U3', 'ESD2CAN24-Q1', 270, yp + 2.54, {'1': 'CAN_L', '2': 'CAN_H', '3': 'GND_BUS'})
pp = S.place('Jumper:Jumper_2_Open', 'JP1', 'LEZÁRÁS', {'1': 'CAN_H', '2': None}, '1', (292, yp),
             fp='Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical')
S.wire(pp['2'][:2], (pp['2'][0] + 2.54, pp['2'][1]))
p = series('Device:R', 'R5', '120R', (pp['2'][0] + 2.54, pp['2'][1]), 'Resistor_SMD:R_0805_2012Metric')
S.label('CAN_L', p, 0)

# Opcionális buszos táp (D66) – alapból NINCS beültetve / bekötve
yo = 268
S.text('BUSZOS TÁP (D66, opció): D6 + JP2 beforrasztva → 24 V nélkül', 190, yo - 10)
S.text('a V_BUS-ról jár (izoláció nélkül!)', 190, yo - 6)
S.label('V_BUS_P', (200, yo), 180)
p = series('Device:D_Schottky', 'D6', 'SS14', (205, yo), 'Diode_SMD:D_SMA', r=180, lpin='2', rpin='1', dnp=True,
           props=P('DNP – buszos táp: V_BUS → +5V'))
S.wire((200, yo), (205, yo))
S.wire(p, (p[0] + 5, yo))
up('+5V', (p[0] + 5, yo))
S.place('Jumper:SolderJumper_2_Open', 'JP2', 'GND_BUS–GND', {'1': 'GND_BUS', '2': 'GND'}, '1', (235, yo),
        fp='Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm',
        props=P('nyitva = izolált (alap); bezárva a D6-tal együtt = buszos táp'))

# PWR_FLAG-ek (ERC: a tápokat a hierarchikus címkék hozzák be)
for i, n in enumerate(['+24V_P', 'GND', 'GND_BUS', 'V_BUS_P', '+3V3A']):
    S.flag(n, 110 + i * 14, 268)
S.text('Generálva a MODULMAG-SPEC.md alapján (hardware/gen/modulmag.py) – kézi szerkesztés helyett a generátort módosítsd.', 20, 287, 1.3)
S.write(OUT, date='2026-10-16')
print('ok', OUT)
