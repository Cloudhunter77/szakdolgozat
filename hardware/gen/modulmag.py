"""Modulmag – a MODULMAG-SPEC.md szerint, elrendezett (vezetékes) változat.

Elrendezés: balra fent a táp (a busz +5V-ja → 3,3 V, D71), középen az STM32, tőle balra a reset/boot,
kvarc, debug és állapot-LED, alatta a hidegítés; jobbra a CAN (SN65HVD230, közös föld – D71, D79) és a busz-oldal.
Blokkon belül vezeték, blokkok között / MCU-lábakon címke.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import kigen
kigen.POWER_UP = {'+3V3', '+5V'}
kigen.POWER_DOWN = {'GND'}

OUT = sys.argv[1]
S = kigen.Sheet('Modulmag – STM32L433RCT3, CAN, táp a buszról (+5V → 3,3 V)', 'modulmag')
# a modulmag a három modul hierarchikus lapja is → ott is legyenek hivatkozásai
S.extra_inst = [(p, f'/{kigen.root_uuid(p)}/{kigen.sheet_uuid(p, "modulmag")}')
                for p in ('rele-modul', 'led-modul', 'bemeneti-modul')]

S.hier = {'HW_ID', 'GND_BUS', 'PC2', 'PC3', 'PB1', 'PB8', 'PB9', 'PB11', 'PB12', 'PB13', 'PB14', 'PB15'} | {f'PA{i}' for i in range(11)}

R0603 = 'Resistor_SMD:R_0603_1608Metric'
C0603 = 'Capacitor_SMD:C_0603_1608Metric'
S.label_dx.update({'MCU_ST_STM32L4:STM32L433RCTx': 20.32,
                   'Connector_Generic:Conn_01x04': 5.08, 'Connector_Generic:Conn_01x07': 5.08,
                   'Device:Crystal_GND24': 5.08, 'Power_Protection:NUP2105L': 5.08, 'Device:LED': 8.89})


S.label_pos.update({
    'MCU_ST_STM32L4:STM32L433RCTx': ((-15.24, -47.0), (5.08, 50.8)),
    'Interface_CAN_LIN:SN65HVD230': ((3.81, 11.43), (3.81, 13.97)),
    'Regulator_Linear:AP2112K-3.3': ((-5.08, -10.16), (-5.08, -7.62)),
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
# 1. TÁP – a busz +5V-ja (J2/J3 1-es tű) → U5 AP2112K (3,3 V); 24 V nincs a modulmagon (D71)
# =====================================================================================================
S.text('1. TÁP: a busz +5V-ja (J2/J3, 1-es tű) → U5 AP2112K-3.3 (kis ejtésű LDO) → +3V3', 20, 20, 1.6)
S.text('D71: központi 5 V a vezérlőről, közös föld; 24 V a modulmagon nincs (a LED- és a relélap maga méri)', 20, 25)
Y = 45
x0 = 30
S.wire((x0, Y), (x0, Y - 5.08))
up('+5V', (x0, Y - 5.08))
taps = [x0 + 12.7, x0 + 25.4]
xin = x0 + 55.88
S.rail(Y, [x0] + taps + [xin])
shunt('Device:C', 'C2', '10µ', (taps[0], Y + 5.08), 'GND', 'Capacitor_SMD:C_0805_2012Metric',
      props=P('X7R, 16 V – a buszról érkező 5 V puffere'))
S.wire((taps[0], Y), (taps[0], Y + 5.08))
# VBUS_SENSE osztó: R3 10k / R4 10k, C9 100n → PC1 (5 V → 2,5 V; a lánc végén mért busz-feszültség)
shunt('Device:R', 'R3', '10k 1%', (taps[1], Y + 5.08), None, R0603)
S.wire((taps[1], Y), (taps[1], Y + 5.08))
nv = (taps[1], Y + 15.24)
S.wire((taps[1], Y + 12.7), nv)
shunt('Device:R', 'R4', '10k 1%', (taps[1], Y + 17.78), 'GND', R0603)
S.wire(nv, (taps[1], Y + 17.78))
shunt('Device:C', 'C9', '100n', (taps[1] + 8.89, Y + 17.78), 'GND', C0603)
S.wire(nv, (taps[1] + 8.89, Y + 15.24), (taps[1] + 8.89, Y + 17.78))
S.wire((taps[1] + 8.89, Y + 15.24), (taps[1] + 15.24, Y + 15.24))
S.label('VBUS_SENSE', (taps[1] + 15.24, Y + 15.24), 0)
S.junction(nv)
S.junction((taps[1] + 8.89, Y + 15.24))
S.text('VBUS_SENSE: 5 V → 2,5 V (PC1)', taps[1] - 2, Y + 32)
# U5 AP2112K-3.3: VIN 1, GND 2, EN 3 (→ VIN), NC 4, VOUT 5
pp = S.place('Regulator_Linear:AP2112K-3.3', 'U5', 'AP2112K-3.3TRG1', {'1': None, '3': None, '2': 'GND', '5': None}, '1', (xin, Y),
             fp='Package_TO_SOT_SMD:SOT-23-5', nc=['4'], props=P('600 mA, ejtés ~0,25 V; bemenet abs. max. 6,5 V'))
en = pp['3'][:2]
S.wire(en, (en[0] - 2.54, en[1]), (en[0] - 2.54, Y))
S.junction((en[0] - 2.54, Y))
xo3 = pp['5'][0]
t3 = [xo3 + 10, xo3 + 20]
S.rail(Y, [xo3] + t3)
S.junction((t3[0], Y))
shunt('Device:C', 'C3', '10µ', (t3[0], Y + 5.08), 'GND', 'Capacitor_SMD:C_0805_2012Metric', props=P('X7R, 10 V – kerámia (az AP2112 stabil vele)'))
S.wire((t3[0], Y), (t3[0], Y + 5.08))
S.wire((t3[1], Y), (t3[1], Y - 5.08))
up('+3V3', (t3[1], Y - 5.08))

# Állapot-LED-ek (3.4) – a táp mellett jobbra
xl = 300
S.text('ÁLLAPOT-LED-ek (előlap, fényvezető)', xl - 5, 30)
up('+5V', (xl, 37))
S.wire((xl, 37), (xl, 40))
shunt('Device:R', 'R8', '2k2', (xl, 40), None, R0603, props=P('D78: a +5V-ról – a kézben lévő zöld LED (522 nm) nyitófeszültsége ~3 V, a 3,3 V-ról alig világítana'))
pp = S.place('Device:LED', 'D3', 'zöld', {'2': None, '1': 'GND'}, '2', (xl, 52.7), r=90, fp='LED_SMD:LED_0603_1608Metric',
             props=P('táp-LED: a busz 5 V-ja (HL-PST-1608U51GC, 522 nm)'))
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
# 2. STM32L433RCT3 (D78; az F303RET6 lábra kompatibilis – a relé- és a bemeneti modulon az is beültethető)
# =====================================================================================================
S.text('2. STM32L433RCT3 (D78) – a modulspecifikus lábak hierarchikus címkék (a modul lapja köti be vagy hagyja üresen)', 120, 88, 1.6)
S.text('F303RET6-tal is beültethető (relé, bemeneti modul): azonos táplábak; 48 = VDDUSB (L433) / VDD (F303), 60 = PH3-BOOT0 / BOOT0', 120, 92.5)
MX, MY = 215, 160
nets = {'1': None, '19': None, '32': None, '48': None, '64': None, '13': None, '12': None,
        '18': None, '31': None, '47': None, '63': None,
        '2': 'STATUS_LED', '5': 'OSC_IN', '6': 'OSC_OUT', '7': 'NRST', '8': 'HW_ID', '9': 'VBUS_SENSE',
        '10': 'PC2', '11': 'PC3', '14': 'PA0', '15': 'PA1', '16': 'PA2', '17': 'PA3',
        '20': 'PA4', '21': 'PA5', '22': 'PA6', '23': 'PA7', '24': 'UART_TX', '25': 'UART_RX', '27': 'PB1', '30': 'PB11',
        '33': 'PB12', '34': 'PB13', '35': 'PB14', '36': 'PB15',
        '41': 'PA8', '42': 'PA9', '43': 'PA10', '44': 'CAN_RX', '45': 'CAN_TX', '46': 'SWDIO', '49': 'SWCLK',
        '60': 'BOOT0', '61': 'PB8', '62': 'PB9',
        # D69: revízió-azonosító + DNP bővítő-tüskesor
        '26': 'HW_REV', '29': 'EXP_PB10', '50': 'EXP_PA15', '55': 'EXP_PB3', '56': 'EXP_PB4', '57': 'EXP_PB5',
        '58': 'EXP_PB6', '59': 'EXP_PB7'}
nc = ['3', '4', '28', '37', '38', '39', '40', '51', '52', '53', '54']
pp = S.comp('MCU_ST_STM32L4:STM32L433RCTx', 'U6', 'STM32L433RCT3', MX, MY, nets, nc=nc,
            fp='Package_QFP:LQFP-64_10x10mm_P0.5mm',
            props=P('D78: 75 db kézben, −40…125 °C, MSL3 – reflow előtt kisütni; tartalék: STM32F303RET6 (a LED-modulon nem)'))
# VDD-lábak (1 VBAT, 19, 32, 48 = VDDUSB, 64) egy sínre, VDDA (13) külön
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
        props=P('3V3-ra húzva: ROM-bootloader – a USART-jai nem a J1-en vannak (AN2606; a PC4/PC5 a USART3, F303-on USART1); a programozás SWD-n'))
S.place('Connector:TestPoint', 'TP2', '3V3', {'1': None}, '1', (xr - 25, 145), r=90, fp='TestPoint:TestPoint_Pad_D1.5mm')
S.wire((xr - 25, 145), (xr - 20, 145), (xr - 20, 142.46))
up('+3V3', (xr - 20, 142.46))

# Kvarc (3.2)
xc, yc = 145, 160
S.text('HSE 8 MHz', xc - 12, yc - 9)
pp = S.place('Device:Crystal_GND24', 'Y1', '8MHz', {'1': None, '3': None, '2': 'GND', '4': 'GND'}, '1', (xc, yc),
             fp='Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm',
             props=P('D85: 3TJ480000JWLAC (LCSC C3031779) – CL = 10 pF, ESR ≤ 120 Ω (HSE gm-tartalék ~7)'))
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
S.text('DEBUG – J1: 1 VTref · 2 SWCLK · 3 GND · 4 SWDIO · 5 NRST · 6 TX · 7 RX', xd - 50, yd - 22)
S.text('(ST-Link klón dupont-tal; beültetés opcionális)', xd - 50, yd - 18)
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
        # a címkék szövege mögött balra, majd lefelé a 7. láb alá → szabályos, lefelé mutató GND
        g = (a[0] - 25.4, pp['7'][1] + 5.08)
        S.wire(b, (g[0], a[1]), g)
        down('GND', g)
    else:
        S.label(net, b, 180)

# Bővítés (D69): HW_REV – a NYÁK-revízió a PB0-n (ADC), a HW-ID sávjaival; J4 – DNP 2 × 5-ös tüskesor
S.text('BŐVÍTÉS (D69, D71) – HW_REV: NYÁK-revízió a PB0-n (v1: 10k / 715 Ω → 1. sáv) · J4: DNP bővítő-tüskesor', 20, 158)
xv = 30.48
up('+3V3', (xv, 165.1))
shunt('Device:R', 'R10', '10k 1%', (xv, 165.1), None, R0603, props=P('felső ellenállás mindig 10 k; az alsó adja a revíziót (16 sáv, 0 és 15 fenntartva)'))
S.wire((xv, 172.72), (xv, 177.8))
shunt('Device:R', 'R11', '715R 1%', (xv, 177.8), 'GND', R0603, props=P('v1 = 1. sáv (0,22 V); csak R10: 15. sáv = a firmware-ből megadott'))
shunt('Device:C', 'C20', '100n', (xv + 10.16, 177.8), 'GND', C0603)
S.wire((xv, 175.26), (xv + 10.16, 175.26), (xv + 10.16, 177.8))
S.wire((xv + 10.16, 175.26), (xv + 17.78, 175.26))
S.label('HW_REV', (xv + 17.78, 175.26), 0)
S.junction((xv, 175.26))
S.junction((xv + 10.16, 175.26))
S.ref_pos['J4'] = ((-3.81, 8.89), (-3.81, 11.43))
S.comp('Connector_Generic:Conn_02x05_Odd_Even', 'J4', 'BŐVÍTŐ', 86.36, 180.34,
       {'1': '+3V3', '2': 'GND', '3': 'EXP_PA15', '4': 'EXP_PB6', '5': 'EXP_PB3', '6': 'EXP_PB7', '7': 'EXP_PB4',
        '8': 'EXP_PB10', '9': 'EXP_PB5', '10': 'GND'},
       fp='Connector_PinHeader_2.54mm:PinHeader_2x05_P2.54mm_Vertical', dnp=True,
       props=P('SPI1: PB3 SCK / PB4 MISO / PB5 MOSI / PA15 NSS · I²C1 (alt.): PB6 SCL / PB7 SDA · PB10'))

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
p = series('Device:FerriteBead_Small', 'FB1', 'BLM18EG221', (105, yh), 'Inductor_SMD:L_0603_1608Metric',
           props=P('D84: Murata BLM18EG221TN1D (0,15 Ω – a VDDA pár mA-jén elhanyagolható); vagy 0 Ω'))
S.rail(yh, [p[0], p[0] + 10, p[0] + 22.7])
for x, ref, val in ((p[0] + 10, 'C14', '1µ'), (p[0] + 22.7, 'C15', '10n')):
    shunt('Device:C', ref, val, (x, yh + 2.54), 'GND', C0603)
    S.wire((x, yh), (x, yh + 2.54))
S.wire((p[0] + 22.7, yh), (p[0] + 30, yh))
S.label('+3V3A', (p[0] + 30, yh), 0)

# =====================================================================================================
# 3. CAN – SN65HVD230 (közös föld, D71; kézben 86 db – D79)
# =====================================================================================================
IX, IY = 320, 125
S.text('3. CAN – U2 SN65HVD230D (D79, kézben): VCC = +3V3, Vref (5) nyitva, Rs (8) → GND = nagy sebesség', 280, 88, 1.6)
S.text('D71: közös föld – izoláció nincs; a vezérlő és minden modul egy tápról, csillagpontosan', 280, 93)
pp = S.comp('Interface_CAN_LIN:SN65HVD230', 'U2', 'SN65HVD230D', IX, IY,
            {'1': 'CAN_TX', '4': 'CAN_RX', '2': 'GND', '3': None, '8': None, '7': 'CAN_H_T', '6': 'CAN_L_T'}, nc=['5'],
            fp='Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',
            props=P('3,3 V, 1 Mbit/s; buszlábak −4…16 V, közös módus −2…7 V (a TCAN1044AV ±58 V-ja helyett – Balázs vállalja, D79)'))
# VCC (3) ← +3V3 + C18 / C19
vd = pp['3'][:2]
yv = vd[1] - 12.7
S.wire(vd, (vd[0], yv))
S.rail(yv, [vd[0], vd[0] + 7.62, vd[0] + 15.24, vd[0] + 22.86])
for x, ref, val in ((vd[0] + 7.62, 'C18', '100n'), (vd[0] + 15.24, 'C19', '4µ7')):
    shunt('Device:C', ref, val, (x, yv + 2.54), 'GND', C0603)
    S.wire((x, yv), (x, yv + 2.54))
S.label('+3V3', (vd[0] + 22.86, yv), 0)
# Rs (8) → R12 0R → GND (nagy sebességű mód; 10–100 k-val meredekség-szabályozás)
sb = pp['8'][:2]
S.wire(sb, (sb[0] - 5.08, sb[1]), (sb[0] - 5.08, sb[1] + 2.54))
shunt('Device:R', 'R12', '0R', (sb[0] - 5.08, sb[1] + 2.54), 'GND', R0603,
      props=P('Rs → GND: nagy sebesség; 10–100 k: meredekség-szabályozás (EMC); nyitva/3V3: készenlét'))
S.text('TXD felhúzás (bootkor recesszív busz):', IX - 62, IY + 18)
up('+3V3', (IX - 50, IY + 23))
S.wire((IX - 50, IY + 23), (IX - 50, IY + 25.54))
shunt('Device:R', 'R1', '10k', (IX - 50, IY + 25.54), 'CAN_TX', R0603)

# közös módusú CAN-fojtó (DNP) a transceiver és a busz között – mint a vezérlőn (D24, D74): izoláció nélkül olcsó EMC-tartalék
xf, yf = 368.3, 118.11
S.text('CAN-fojtó (D74): L1 DNP + JP2/JP3 zárva; fojtóval JP2/JP3 átvágva', 345.44, yf - 9)
pl1 = S.comp('Device:Filter_EMI_CommonMode', 'L1', 'DNP', xf, yf, {k: None for k in '1234'}, dnp=True,
             fp='Inductor_SMD:L_CommonModeChoke_Coilank_ACM3225', props=P('pl. TDK ACT45B-510 / ACM3225 – csak ha a mérés indokolja'))
for a, b, n_t, n in (('1', '2', 'CAN_H_T', 'CAN_H'), ('3', '4', 'CAN_L_T', 'CAN_L')):
    q = pl1[a][:2]; S.wire(q, (q[0] - 5.08, q[1])); S.label(n_t, (q[0] - 5.08, q[1]), 180)
    q = pl1[b][:2]; S.wire(q, (q[0] + 5.08, q[1])); S.label(n, (q[0] + 5.08, q[1]), 0)
for i, (n_t, n) in enumerate((('CAN_H_T', 'CAN_H'), ('CAN_L_T', 'CAN_L'))):
    pj = S.comp('Jumper:SolderJumper_2_Bridged', f'JP{2 + i}', 'áthidaló', xf, yf + 12.7 + i * 7.62, {'1': None, '2': None},
                fp='Jumper:SolderJumper-2_P1.3mm_Bridged_RoundedPad1.0x1.5mm', props=P('alapból zárt; fojtó beültetésekor átvágni'))
    q = pj['1'][:2]; S.wire(q, (q[0] - 5.08, q[1])); S.label(n_t, (q[0] - 5.08, q[1]), 180)
    q = pj['2'][:2]; S.wire(q, (q[0] + 5.08, q[1])); S.label(n, (q[0] + 5.08, q[1]), 0)

# =====================================================================================================
# 4. BUSZ-OLDAL: J2 BE / J3 KI átmenő, ESD, lezárás, TVS
# =====================================================================================================
S.text('4. BUSZ: J2 és J3 azonos tűi átmenők (1 +5V · 2 GND_BUS · 3 CAN_L · 4 CAN_H); ESD és TVS a csatlakozók mellé', 280, 160, 1.6)
S.text('GND_BUS: a modul lapján R-en át a GND-re (LED-modul 1 Ω, a többi 0 Ω) – a nagyáramú modul hurokárama ne a buszon folyjon (D74)', 280, 164.5)
JX = 395
pj2 = S.comp('Connector_Generic:Conn_01x04', 'J2', 'BUS_IN', JX, 180, {'1': None, '2': None, '3': None, '4': None},
             fp='Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical')
pj3 = S.comp('Connector_Generic:Conn_01x04', 'J3', 'BUS_OUT', JX, 205, {'1': None, '2': None, '3': None, '4': None},
             fp='Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical')
lanes = {'1': JX - 12.7, '2': JX - 15.24, '3': JX - 17.78, '4': JX - 20.32}   # +5V, GND, CAN_L, CAN_H
for n, lx in lanes.items():
    S.wire(pj2[n][:2], (lx, pj2[n][1]), (lx, pj3[n][1]), pj3[n][:2])
# a sávok lefelé futnak tovább, és lépcsőzetesen balra fordulnak (nincs keresztezés) → címke
for i, n in enumerate(['4', '3', '1', '2']):        # CAN_H, CAN_L, +5V, GND
    lx = lanes[n]
    yt = pj3['4'][1] + 5.08 + i * 3.81
    S.junction((lx, pj3[n][1]))
    S.wire((lx, pj3[n][1]), (lx, yt), (JX - 40, yt))
    net = {'4': 'CAN_H', '3': 'CAN_L', '2': 'GND_BUS', '1': '+5V'}[n]
    if net == '+5V':
        S.wire((JX - 40, yt), (JX - 53.34, yt), (JX - 53.34, yt - 10.16))
        up('+5V', (JX - 53.34, yt - 10.16))
    else:
        S.label(net, (JX - 40, yt), 180)
# TVS (D5), ESD (U3), lezárás (JP1 + R5) – címkékkel, egy sorban
yp = 238
S.text('+5V TVS · CAN ESD · lezárás (JP1: csak a lánc két végén)', 248, yp - 19)
shunt('Device:D_Zener', 'D5', 'SMF5.0A', (253, yp), 'GND', 'Diode_SMD:D_SOD-123F', r=270,
      props=P('ESD / hot-plug tüskék ellen, a J2/J3 mellé'))
S.wire((253, yp), (253, yp - 5.08))
up('+5V', (253, yp - 5.08))
pp = S.comp('Power_Protection:NUP2105L', 'U3', 'ESD2CAN24-Q1', 270, yp + 2.54, {'1': 'CAN_L', '2': 'CAN_H', '3': 'GND'})
pp = S.place('Jumper:Jumper_2_Open', 'JP1', 'LEZÁRÁS', {'1': 'CAN_H', '2': None}, '1', (302, yp),
             fp='Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical')
S.wire(pp['2'][:2], (pp['2'][0] + 2.54, pp['2'][1]))
p = series('Device:R', 'R5', '120R', (pp['2'][0] + 2.54, pp['2'][1]), 'Resistor_SMD:R_0805_2012Metric')
S.label('CAN_L', p, 0)

# PWR_FLAG-ek (ERC: a tápokat a hierarchikus címkék hozzák be)
for i, n in enumerate(['+5V', 'GND', '+3V3A']):
    S.flag(n, 110 + i * 14, 262)
S.text('Generálva a MODULMAG-SPEC.md alapján (hardware/gen/modulmag.py) – kézi szerkesztés helyett a generátort módosítsd.', 20, 281, 1.3)
S.write(OUT, date='2026-10-20')
print('ok', OUT)
