"""Vezérlő – a VEZERLO-SPEC.md szerint, elrendezett (vezetékes) változat, A2.

Felső sáv: táp (12–26 V-os bemenet → LMR33630 5,2 V → LM66200 (+ USB) → +5V; VIN_BUCK → LMR36015 3,3 V) és a V_BUS-eFuse (TPS2595).
Középső sáv: ESP32-C6 (EN, strapping- és felhúzó-ellenállások) és a W5500 + MagJack (MDI-lezárás, LED-ek, hidegítés).
Alsó sáv: USB-C, CAN + busz, kezelőszervek / LED-ek / RGB / debug.
Blokkon belül vezeték, blokkok között és az IC-lábakon címke.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import kigen
import sx
kigen.POWER_UP = {'+3V3', '+5V'}
kigen.POWER_DOWN = {'GND'}

OUT = sys.argv[1]
S = kigen.Sheet('Vezérlő – ESP32-C6-WROOM-1 + W5500 + CAN + V_BUS', 'vezerlo', paper='A2')
S.ref_pos.update({'D9': ((3.81, -1.27), (10.16, 1.27)), 'U8': ((7.62, 10.16), (7.62, 12.7)), 'JP2': ((-25.4, -7.62), (-25.4, -5.08)),
                  'JP3': ((-25.4, -7.62), (-25.4, -5.08)), 'R39': ((-5.08, -2.54), (1.27, -2.54)),
                  'D6': ((7.62, 5.08), (7.62, 7.62))})
ML = os.path.join(os.path.dirname(__file__), '..', 'lib', 'modularis.kicad_sym')
for n in ('LMR36015BRNXR', 'TPS259531DSG', 'LM66200DRL', 'ESP32-C6-WROOM-1', 'E22-900M22S'):
    S.use(f'modularis:{n}', lib='modularis', name=n, libpath=ML)
# a W5500 MISO-ja valójában tri-state (CS = 1-nél nagy impedanciás) – a KiCad-szimbólumban „output”; a közös SPI-buszon
# (U10 LoRa) e nélkül az ERC ütközést jelez
for _u in sx.find(S.use('Interface_Ethernet:W5500'), 'symbol'):
    for _p in sx.find(_u, 'pin'):
        if sx.first(_p, 'number')[1] == '34':
            _p[1] = sx.Sym('tri_state')
S.label_pos.update({
    'modularis:ESP32-C6-WROOM-1': ((-25.4, -38.1), (-25.4, -35.56)),
    'Interface_Ethernet:W5500': ((-12.7, -35.56), (5.08, -35.56)),
    'modularis:LMR36015BRNXR': ((-7.62, -16.51), (-7.62, -13.97)),
    'modularis:TPS259531DSG': ((-10.16, -12.7), (-10.16, -10.16)),
    'modularis:LM66200DRL': ((-7.62, -12.7), (-7.62, -10.16)),
    'Regulator_Switching:LMR33630ADDA': ((-7.62, -13.97), (-7.62, -11.43)),
    'Interface_CAN_LIN:MCP2562-E-SN': ((5.08, -13.97), (5.08, -11.43)),
    'Connector:RJ45_Hanrun_HR911105A_Horizontal': ((-10.16, -15.24), (-10.16, -12.7)),
    'Connector:USB_C_Receptacle_USB2.0_16P': ((-10.16, -25.4), (-10.16, -22.86)),
    'Power_Protection:USBLC6-2SC6': ((5.08, -8.89), (5.08, -6.35)),
    'LED:WS2812B': ((7.62, -8.89), (7.62, -6.35)),
    'Jumper:SolderJumper_3_Bridged12': ((3.81, -3.81), (3.81, -1.27)),
    'modularis:E22-900M22S': ((-8.89, -22.86), (-8.89, -20.32)),
})
S.label_dx.update({'Connector_Generic:Conn_01x04': 5.08, 'Connector_Generic:Conn_01x06': 5.08,
                   'Connector_Generic:Conn_01x02': 5.08, 'Device:Crystal_GND24': 5.08, 'Power_Protection:NUP2105L': 5.08,
                   '74xx:74HC14': 5.08})
R0603, C0603 = 'Resistor_SMD:R_0603_1608Metric', 'Capacitor_SMD:C_0603_1608Metric'
C0805, C1206, C1210 = 'Capacitor_SMD:C_0805_2012Metric', 'Capacitor_SMD:C_1206_3216Metric', 'Capacitor_SMD:C_1210_3225Metric'
U9FP = 'Package_SO:SOIC-14_3.9x8.7mm_P1.27mm'
SJ3 = 'Jumper:SolderJumper-3_P1.3mm_Bridged12_RoundedPad1.0x1.5mm'
TPFP = 'TestPoint:TestPoint_Pad_D1.5mm'


def P(n):
    return {'Megjegyzés': n} if n else None


def up(net, p):
    S.label(net, p, 90)


def down(net, p):
    S.label(net, p, 270)


def shunt(lib, ref, val, top, bottom_net, fp, r=0, top_pin='1', bot_pin='2', **k):
    """függőleges kétlábú: `top_pin` a `top` pontban, `bot_pin` lent a `bottom_net`-re (None = kézzel kötve)"""
    return S.place(lib, ref, val, {top_pin: None, bot_pin: bottom_net}, top_pin, top, r=r, fp=fp, **k)


def hang(x, y, ref, val, bottom_net='GND', fp=C0603, lib='Device:C', **k):
    """sínről (x, y) lelógó kétlábú alkatrész, 2,54 mm-es vezetékkel"""
    S.wire((x, y), (x, y + 2.54))
    return shunt(lib, ref, val, (x, y + 2.54), bottom_net, fp, **k)


def series(lib, ref, val, left, fp, r=90, lpin='1', rpin='2', **k):
    """vízszintes kétlábú, `lpin` a `left` pontban; visszaadja a jobb láb pontját"""
    pp = S.place(lib, ref, val, {lpin: None, rpin: None}, lpin, left, r=r, fp=fp, **k)
    return pp[rpin][:2]


def stub(p, net, d, length=5.08):
    dx, dy = {0: (length, 0), 180: (-length, 0), 90: (0, -length), 270: (0, length)}[d]
    q = (p[0] + dx, p[1] + dy)
    S.wire(p, q)
    S.label(net, q, d)
    return q


def divider(x, y, rt, rtv, rb, rbv, cref, net):
    """(x, y)-ból lefelé: rt – csomópont – rb → GND, mellette C → GND, a csomópontról címke jobbra"""
    S.wire((x, y), (x, y + 2.54))
    shunt('Device:R', rt, rtv, (x, y + 2.54), None, R0603)
    n = (x, y + 12.7)
    S.wire((x, y + 10.16), n)
    shunt('Device:R', rb, rbv, (x, n[1] + 2.54), 'GND', R0603)
    S.wire(n, (x, n[1] + 2.54))
    S.rail(n[1], [x, x + 8.89, x + 13.97])
    shunt('Device:C', cref, '100n', (x + 8.89, n[1] + 2.54), 'GND', C0603)
    S.wire((x + 8.89, n[1]), (x + 8.89, n[1] + 2.54))
    S.label(net, (x + 13.97, n[1]), 0)


# =====================================================================================================
# 1. TÁP
# =====================================================================================================
S.text('1. TÁP (12–26 V): +24V_IN → F1 → D1 → +24V_P → D8 → VIN_BUCK (U1 LMR36015 → 3,3 V); +24V_P → R7 → +24V_F → U2 LMR33630 (5,2 V) → U12 LM66200 → +5V', 20, 22, 2)
S.text('D71: központi 5 V a buszra (2 A); USB-ről is: az U12 a nagyobbat választja (buck 5,2 V > USB). D57: a C1 elkó kötelező; a tápot ≤ 26 V-ra (az U2 max. 36 V)', 20, 27, 1.4)
Y = 45.72
pj = S.comp('Connector_Generic:Conn_01x02', 'J1', '24V IN', 27.94, 55.88, {'1': None, '2': None},
            fp='TerminalBlock_Phoenix:TerminalBlock_Phoenix_PT-1,5-2-3.5-H_1x02_P3.50mm_Horizontal',
            props=P('push-in sorkapocs – a típus a DIN-ház vállához (D50)'))
a1, a2 = pj['1'][:2], pj['2'][:2]
x0 = a1[0] - 5.08
S.wire(a1, (x0, a1[1]), (x0, Y))
S.wire(a2, (a2[0] - 2.54, a2[1]), (a2[0] - 2.54, a2[1] + 2.54))
down('GND', (a2[0] - 2.54, a2[1] + 2.54))
S.rail(Y, [x0, x0 + 5.08, x0 + 10.16])
S.wire((x0 + 5.08, Y), (x0 + 5.08, Y - 5.08))
S.label('+24V_IN', (x0 + 5.08, Y - 5.08), 90)
p = series('Device:Fuse', 'F1', '2A', (x0 + 10.16, Y), 'Fuse:Fuse_1206_3216Metric', props=P('≥ 32 V, gyors; D71: 12 V-on és 2 A-es buszterhelésnél ~1,2 A'))
S.wire(p, (p[0] + 5.08, Y))
p = series('Device:D_Schottky', 'D1', 'B360', (p[0] + 5.08, Y), 'Diode_SMD:D_SMC', r=180, lpin='2', rpin='1',
           props=P('60 V, 3 A – D71: a bemeneti áram 12 V-on ~1,2 A'))
# +24V_P sín
t = [p[0] + 5.08, p[0] + 15.24, p[0] + 30.48, p[0] + 60.96, p[0] + 71.12]
S.rail(Y, [p[0]] + t)
S.wire((t[0], Y), (t[0], Y - 5.08))
S.label('+24V_P', (t[0], Y - 5.08), 90)
hang(t[1], Y, 'D2', 'SMBJ28A', lib='Device:D_Zener', fp='Diode_SMD:D_SMB', r=270)
divider(t[2], Y, 'R1', '150k', 'R2', '10k', 'C3', 'VIN_SENSE')
S.wire((t[3], Y), (t[3], Y + 2.54))
S.place('Device:D_Schottky', 'D8', 'SS16', {'1': None, '2': None}, '2', (t[3], Y + 2.54), r=90, fp='Diode_SMD:D_SMA',
        props=P('az USB ne táplálja vissza a 24 V-os oldalt'))
stub((t[3], Y + 10.16), 'VIN_BUCK', 270, 5.08)
p = series('Device:R', 'R7', '0R', (t[4], Y), 'Resistor_SMD:R_2512_6332Metric', props=P('D70: 0 Ω; a footprint marad – szükség esetén 10 Ω impulzusbíró'))
f = [p[0] + 5.08, p[0] + 15.24, p[0] + 30.48, p[0] + 43.18, p[0] + 55.88]
S.rail(Y, [p[0]] + f)
S.wire((f[0], Y), (f[0], Y - 5.08))
S.label('+24V_F', (f[0], Y - 5.08), 90)
hang(f[1], Y, 'D7', 'SMBJ28A', lib='Device:D_Zener', fp='Diode_SMD:D_SMB', r=270)
hang(f[2], Y, 'C1', '47µ/50V', lib='Device:C_Polarized', fp='Capacitor_SMD:CP_Elec_6.3x7.7',
     props=P('elektrolit, low-ESR, 105 °C – KÖTELEZŐ (D57)'))
hang(f[3], Y, 'C2', '10µ/50V', fp=C1210, props=P('CIN az U2 VIN-lábánál; mellette C53 220 nF'))
# --- U2 LMR33630ADDA: +24V_F → +5V_BUCK (5,2 V, 400 kHz, ~2 A – D71) ---
x4 = f[4] + 12.7
pu2 = S.comp('Regulator_Switching:LMR33630ADDA', 'U2', 'LMR33630ADDA', x4 + 10.16, Y + 5.08,
             {k: None for k in '123456789'}, fp='Package_SO:Texas_HSOP-8-1EP_3.9x4.9mm_P1.27mm_ThermalVias',
             props=P('400 kHz; TI 9-2. táblázat (5 V): L 8 µH, 4 × 22 µF, 10 µF + 220 nF'))
S.rail(Y, [f[3], f[4], x4])
hang(f[4], Y, 'C53', '220n/50V', props=P('CHF – közvetlenül a VIN–PGND lábaknál'))
# EN (3) → VIN; VCC (6) → C54 1 µF
en2 = pu2['3'][:2]
S.wire(en2, (x4 - 2.54, en2[1]), (x4 - 2.54, Y))
S.junction((x4 - 2.54, Y))
vc2 = pu2['6'][:2]
S.wire(vc2, (x4 - 5.08, vc2[1]))
shunt('Device:C', 'C54', '1µ/16V', (x4 - 5.08, vc2[1]), 'GND', C0603, props=P('VCC – csak ez a kondenzátor'))
stub(pu2['1'][:2], 'GND', 270, 2.54)
# BOOT (7) – C55 – SW (8) → L3
xr = pu2['7'][0]
S.wire(pu2['7'][:2], (xr + 2.54, Y), (xr + 2.54, Y - 7.62), (xr + 5.08, Y - 7.62))
p = series('Device:C', 'C55', '100n', (xr + 5.08, Y - 7.62), C0603)
S.wire(p, (xr + 15.24, Y - 7.62), (xr + 15.24, Y + 2.54))
S.wire(pu2['8'][:2], (xr + 20.32, Y + 2.54))
S.junction((xr + 15.24, Y + 2.54))
pL3 = S.place('Device:L', 'L3', '8,2µH', {'1': None, '2': None}, '1', (xr + 20.32, Y + 2.54), r=90,
              fp='Inductor_SMD:L_Bourns_SRN6045TA', props=P('árnyékolt, Isat ≥ 3,5 A, ~14 mΩ (pl. SRN6045TA-8R2M) – 3 A-ig'))
xo5 = pL3['2'][0]
ys5 = Y + 2.54
c5 = [xo5 + 7.62, xo5 + 17.78, xo5 + 27.94, xo5 + 38.1, xo5 + 48.26]
XL = xo5 + 76.2
S.rail(ys5, [xo5, xo5 + 2.54] + c5 + [XL - 10.16])
hang(c5[0], ys5, 'R54', '100k 1%', bottom_net=None, lib='Device:R', fp=R0603)
nf5 = (c5[0], ys5 + 12.7)
S.wire((c5[0], ys5 + 10.16), nf5)
shunt('Device:R', 'R55', '23,7k 1%', (c5[0], nf5[1] + 2.54), 'GND', R0603, props=P('→ 5,22 V (VFB = 1,0 V)'))
S.wire(nf5, (c5[0], nf5[1] + 2.54))
fb2 = pu2['5'][:2]
S.wire(fb2, (xr + 5.08, fb2[1]), (xr + 5.08, nf5[1]), nf5)
S.junction(nf5)
for i, x in enumerate(c5[1:]):
    hang(x, ys5, f'C{56 + i}', '22µ', fp=C1206, props=P('X7R, 10 V, 1206'))
stub((xo5 + 2.54, ys5), '+5V_BUCK', 90, 5.08)
# --- U12 LM66200: VIN1 = +5V_BUCK, VIN2 = VUSB → +5V (a nagyobb táplál, visszatáplálás nincs) ---
pu12 = S.comp('modularis:LM66200DRL', 'U12', 'LM66200DRLR', XL, ys5 + 5.08, {k: None for k in '12345678'},
              props=P('VIN max. 5,5 V (abs. 6 V); a buck 5,2 V-ja 24 V mellett biztosan az USB fölött van'))
stub(pu12['6'][:2], 'VUSB', 180, 5.08)
on = pu12['4'][:2]
S.wire(on, (on[0] - 2.54, on[1]), (on[0] - 2.54, on[1] + 2.54))
down('GND', (on[0] - 2.54, on[1] + 2.54))
xv5 = pu12['2'][0] + 2.54
S.wire(pu12['2'][:2], (xv5, pu12['2'][1]))
S.wire(pu12['7'][:2], (xv5, pu12['7'][1]), (xv5, pu12['2'][1]))
S.wire(pu12['1'][:2], (xv5, pu12['1'][1]), (xv5, pu12['5'][1] + 2.54))
S.wire(pu12['5'][:2], (xv5, pu12['5'][1]))
S.junction((xv5, pu12['5'][1]))
down('GND', (xv5, pu12['5'][1] + 2.54))
S.items.append([sx.Sym('no_connect'), [sx.Sym('at'), pu12['8'][0], pu12['8'][1]], [sx.Sym('uuid'), kigen.U()]])
S.items.append([sx.Sym('no_connect'), [sx.Sym('at'), pu2['4'][0], pu2['4'][1]], [sx.Sym('uuid'), kigen.U()]])
o5 = [xv5, xv5 + 7.62, xv5 + 15.24]
S.rail(ys5, o5)
S.junction((xv5, ys5))
hang(o5[1], ys5, 'C13', '22µ/10V', fp=C1206)
S.wire((o5[2], ys5), (o5[2], ys5 - 5.08))
up('+5V', (o5[2], ys5 - 5.08))

# --- LMR36015: VIN_BUCK → 3,3 V ---
S.text('3,3 V – U1 LMR36015BRNXR (1 MHz, L1 6,8 µH), VQFN-HR (RNX0012B)', 20, 86, 1.6)
UX, UY = 101.6, 119.38
pl = S.comp('modularis:LMR36015BRNXR', 'U1', 'LMR36015BRNXR', UX, UY, {str(i): None for i in range(1, 13)},
            fp='modularis:TI_VQFN-HR-12_RNX0012B')
vin = [pl[n][:2] for n in ('2', '10', '9')]
xv = vin[0][0] - 5.08
for q in vin:
    S.wire(q, (xv, q[1]))
yb = vin[0][1] - 7.62
S.wire((xv, vin[2][1]), (xv, yb))
S.junction((xv, vin[0][1]))
S.junction((xv, vin[1][1]))
S.rail(yb, [xv - 35.56, xv - 27.94, xv - 17.78, xv - 7.62, xv])
S.label('VIN_BUCK', (xv - 35.56, yb), 180)
hang(xv - 27.94, yb, 'C4', '4µ7/50V', fp=C1210)
hang(xv - 17.78, yb, 'C5', '220n/50V', props=P('a 2-es VIN-lábnál'))
hang(xv - 7.62, yb, 'C6', '220n/50V', props=P('a 10-es VIN-lábnál'))
vcc = pl['5'][:2]
S.wire(vcc, (vcc[0] - 12.7, vcc[1]), (vcc[0] - 12.7, vcc[1] + 2.54))
shunt('Device:C', 'C8', '1µ/16V', (vcc[0] - 12.7, vcc[1] + 2.54), 'GND', C0603, props=P('VCC–AGND, más terhelés nem mehet rá'))
gx = pl['1'][0] - 5.08
for n in ('1', '11', '6'):
    S.wire(pl[n][:2], (gx, pl[n][1]))
S.wire((gx, pl['1'][1]), (gx, pl['6'][1] + 2.54))
S.junction((gx, pl['11'][1]))
S.junction((gx, pl['6'][1]))
down('GND', (gx, pl['6'][1] + 2.54))
# BOOT (4) – C7 – SW (12, 3)
bt, sw1, sw2 = pl['4'][:2], pl['12'][:2], pl['3'][:2]
xs = bt[0] + 5.08
S.wire(sw1, (xs, sw1[1]))
S.wire(sw2, (xs, sw2[1]))
S.wire((xs, sw1[1]), (xs, sw2[1]))
S.junction((xs, sw1[1]))
yc7 = bt[1] - 7.62
S.wire(bt, (bt[0] + 2.54, bt[1]), (bt[0] + 2.54, yc7), (xs + 5.08, yc7))
p = series('Device:C', 'C7', '100n', (xs + 5.08, yc7), C0603)
S.wire(p, (p[0] + 2.54, yc7), (p[0] + 2.54, sw1[1]), (xs, sw1[1]))
# SW → L1 → +3V3 kimeneti sín
S.wire((xs, sw2[1]), (xs + 7.62, sw2[1]))
S.junction((xs, sw2[1]))
pL = S.place('Device:L', 'L1', '6,8µH', {'1': None, '2': None}, '1', (xs + 7.62, sw2[1]), r=90,
             fp='Inductor_SMD:L_Coilcraft_XAL5030-XXX', props=P('árnyékolt, Isat ≥ 2,1 A (ideálisan ≥ 2,8 A), ~5 × 5 mm'))
ysw = sw2[1]
xo = pL['2'][0]
fb = [xo + 7.62, xo + 15.24, xo + 25.4, xo + 33.02, xo + 40.64, xo + 48.26]
S.rail(ysw, [xo] + fb)
S.wire((fb[5], ysw), (fb[5], ysw - 5.08))
up('+3V3', (fb[5], ysw - 5.08))
hang(fb[0], ysw, 'R3', '100k 1%', bottom_net=None, lib='Device:R', fp=R0603)
hang(fb[1], ysw, 'C9', '20p', bottom_net=None, props=P('CFF, R3-mal párhuzamosan'))
nfb = (fb[0], ysw + 12.7)
S.wire((fb[0], ysw + 10.16), nfb, (fb[1], nfb[1]), (fb[1], ysw + 10.16))
S.junction(nfb)
shunt('Device:R', 'R4', '43,2k 1%', (fb[0], nfb[1] + 2.54), 'GND', R0603, props=P('→ 3,31 V (VFB = 1,0 V)'))
S.wire(nfb, (fb[0], nfb[1] + 2.54))
fbp = pl['7'][:2]
S.wire(fbp, (xs - 2.54, fbp[1]), (xs - 2.54, nfb[1]), nfb)
for i, x in enumerate(fb[2:5]):
    hang(x, ysw, f'C{10 + i}', '22µ', fp=C1206, props=P('X7R, 10 V, 1206'))
pg = pl['8'][:2]
S.wire(pg, (pg[0] + 1.27, pg[1]), (pg[0] + 1.27, pg[1] + 2.54))
down('GND', (pg[0] + 1.27, pg[1] + 2.54))

# =====================================================================================================
# 2. V_BUS – TPS2553
# =====================================================================================================
S.text('2. V_BUS – U3 TPS259531 eFuse (D71): 2 A-es korlát, 5,7 V-os túlfeszültség-vágás; EN-osztó a +5V-ról (bármelyik forrásról BE), a GPIO20 a D9-en (BAT54) át letiltja',
       300, 86, 1.6)
TX, TY = 370.84, 119.38
pt = S.comp('modularis:TPS259531DSG', 'U3', 'TPS259531DSGR', TX, TY, {str(i): None for i in range(1, 10)},
            props=P('WSON-8 2 × 2 mm, a PAD a GND-re; abs. max. 20 V'))
i1 = pt['3'][:2]
S.wire(pt['4'][:2], (i1[0] - 2.54, pt['4'][1]), (i1[0] - 2.54, i1[1]))
S.rail(i1[1], [i1[0] - 30.48, i1[0] - 20.32, i1[0] - 12.7, i1[0] - 2.54, i1[0]])
S.wire((i1[0] - 30.48, i1[1]), (i1[0] - 30.48, i1[1] - 5.08))
up('+5V', (i1[0] - 30.48, i1[1] - 5.08))
hang(i1[0] - 20.32, i1[1], 'C22', '1µ')
hang(i1[0] - 12.7, i1[1], 'C23', '100n')
# EN/UVLO (2): R10 a +5V-ról, R11 a GND-re (5,2 V → 1,66 V; BE ~3,7 V felett), D9 (anód az EN-en) → VBUS_EN
en = pt['2'][:2]
ne = (en[0] - 7.62, en[1] + 20.32)
S.wire(en, (ne[0], en[1]), ne)
S.label('+5V', (ne[0] - 33.02, ne[1]), 180)
S.wire((ne[0] - 33.02, ne[1]), (ne[0] - 30.48, ne[1]))
p = series('Device:R', 'R10', '100k', (ne[0] - 30.48, ne[1]), R0603)
S.rail(ne[1], [p[0], ne[0] - 15.24, ne[0]])
hang(ne[0] - 15.24, ne[1], 'R11', '47k', lib='Device:R', fp=R0603)
S.wire(ne, (ne[0], ne[1] + 2.54))
S.junction(ne)
S.place('Device:D_Schottky', 'D9', 'BAT54WS', {'1': None, '2': None}, '2', (ne[0], ne[1] + 2.54), r=90, fp='Diode_SMD:D_SOD-323',
        props=P('anód az EN-en, katód a GPIO20-on'))
stub((ne[0], ne[1] + 10.16), 'VBUS_EN', 270, 2.54)
# dVdt (1) → C60 22 nF → ~1,9 V/ms: 5 V 2,7 ms alatt, 200 µF buszkapacitáson ~0,4 A bekapcsolási áram
dv = pt['1'][:2]
S.wire(dv, (dv[0] - 2.54, dv[1]), (dv[0] - 2.54, dv[1] + 5.08))
shunt('Device:C', 'C60', '22n', (dv[0] - 2.54, dv[1] + 5.08), 'GND', C0603, props=P('dVdt: lassú felfutás, kis bekapcsolási áram'))
# ILM (7) → R12 → GND; GND (8) + PAD (9)
il = pt['7'][:2]
S.wire(il, (il[0] + 22.86, il[1]))
shunt('Device:R', 'R12', '1,02k 1%', (il[0] + 22.86, il[1]), 'GND', R0603, props=P('R = 2000 / (I − 0,04) → 2,0 A'))
g8, g9 = pt['8'][:2], pt['9'][:2]
S.wire(g8, (g8[0] + 5.08, g8[1]), (g8[0] + 5.08, g9[1] + 2.54))
S.wire(g9, (g9[0] + 5.08, g9[1]))
S.junction((g8[0] + 5.08, g9[1]))
down('GND', (g8[0] + 5.08, g9[1] + 2.54))
# FLT (6) → R34 felhúzás + címke
fl = pt['6'][:2]
S.rail(fl[1], [fl[0], fl[0] + 12.7, fl[0] + 17.78])
S.place('Device:R', 'R34', '10k', {'1': '+3V3', '2': None}, '2', (fl[0] + 12.7, fl[1]), fp=R0603, props=P('FLT felhúzás (nyitott drain)'))
S.label('VBUS_FAULT', (fl[0] + 17.78, fl[1]), 0)
# OUT (5) → V_BUS sín
ou = pt['5'][:2]
yv = ou[1] - 17.78
S.wire(ou, (ou[0] + 2.54, ou[1]), (ou[0] + 2.54, yv))
vb = [ou[0] + 2.54, ou[0] + 22.86, ou[0] + 33.02, ou[0] + 43.18, ou[0] + 55.88, ou[0] + 76.2]
S.rail(yv, vb)
hang(vb[1], yv, 'C24', '100n')
hang(vb[2], yv, 'C25', '10µ/16V', fp=C0805)
hang(vb[3], yv, 'D4', 'SMF5.0A', lib='Device:D_Zener', fp='Diode_SMD:D_SOD-123F', r=270)
divider(vb[4], yv, 'R13', '100k', 'R14', '22k', 'C14', 'VBUS_SENSE')
S.label('V_BUS', (vb[5], yv), 0)
S.text('VBUS_SENSE: 5 V → 0,9 V (GPIO1)', vb[4] - 5, yv + 36)

# =====================================================================================================
# 3. ESP32-C6-WROOM-1
# =====================================================================================================
S.text('3. ESP32-C6-WROOM-1-N16 (fém szekrénybe -1U ugyanerre a footprintre, D63) – strapping: GPIO8 = 1, GPIO9 = 1 (BOOT gomb → 0), GPIO15', 20, 166, 2)
EX, EY = 132.08, 233.68
nets = {str(i): None for i in range(1, 30) if i != 22}
pe = S.comp('modularis:ESP32-C6-WROOM-1', 'U4', 'ESP32-C6-WROOM-1-N16', EX, EY, nets, nc=['22'], fp='modularis:ESP32-C6-WROOM-1')
v = pe['2'][:2]
yt = v[1] - 25.4
S.wire(v, (v[0], yt))
S.rail(yt, [v[0] - 17.78, v[0] - 10.16, v[0], v[0] + 5.08])
S.wire((v[0] + 5.08, yt), (v[0] + 5.08, yt - 2.54))
up('+3V3', (v[0] + 5.08, yt - 2.54))
hang(v[0] - 17.78, yt, 'C26', '22µ', fp=C0805, props=P('a 3V3-lábnál'))
hang(v[0] - 10.16, yt, 'C27', '100n', props=P('a 3V3-lábnál'))
stub(pe['1'][:2], 'GND', 270, 2.54)
# EN (3): R15 + C15 → CHIP_EN
en = pe['3'][:2]
xn = en[0] - 7.62
S.rail(en[1], [en[0], xn, en[0] - 33.02, en[0] - 40.64])
S.place('Device:R', 'R15', '10k', {'1': '+3V3', '2': None}, '2', (xn, en[1]), fp=R0603)
hang(en[0] - 33.02, en[1], 'C15', '1µ', props=P('RC-késleltetés az EN-en'))
S.label('CHIP_EN', (en[0] - 40.64, en[1]), 180)
# bal oldali jelek
for n, net in (('8', 'VIN_SENSE'), ('9', 'VBUS_SENSE'), ('27', 'SPI_MISO'), ('26', 'W5500_INT'), ('7', 'SPI_MOSI')):
    stub(pe[n][:2], net, 180, 7.62)
# GPIO4 → LoRa DIO1 (D68), GPIO5 → bővítő-csatlakozó (J8, D69)
stub(pe['4'][:2], 'LORA_DIO1', 180, 7.62)
stub(pe['5'][:2], 'EXP_GPIO5', 180, 7.62)
# SPI_SCLK: GPIO6 (6) → R19 0R → SPI_SCLK, C28 (DNP)
q = pe['6'][:2]
S.wire(q, (q[0] - 25.4, q[1]))
pr = S.place('Device:R', 'R19', '0R', {'1': None, '2': None}, '1', (q[0] - 25.4, q[1]), r=270, fp=R0603, props=P('33 Ω-hoz footprint'))
xk = pr['2'][0]
S.rail(q[1], [xk, xk - 5.08, xk - 10.16])
hang(xk - 5.08, q[1], 'C28', 'DNP', dnp=True, props=P('kondenzátor-footprint, nem beültetve'))
S.label('SPI_SCLK', (xk - 10.16, q[1]), 180)
# jobb oldali jelek
for n, net in (('24', 'U0RXD'), ('14', 'USB_DP'), ('13', 'USB_DM'), ('17', 'CAN_RX'), ('18', 'VBUS_EN'), ('19', 'VBUS_FAULT')):
    stub(pe[n][:2], net, 0, 7.62)
for n, net in (('20', 'LORA_CS'), ('21', 'LORA_BUSY')):
    stub(pe[n][:2], net, 0, 7.62)
q = pe['25'][:2]
S.wire(q, (q[0] + 2.54, q[1]))
p = series('Device:R', 'R39', '499R', (q[0] + 2.54, q[1]), R0603, props=P('Espressif-ajánlás'))
stub(p, 'U0TXD', 0, 5.08)
# felhúzott jelek (GPIO8, BOOT, CS, RST, GPIO15, CAN_TX – egymás alatti lábak): vízszintes 10 k → közös +3V3 sín
pu_list = (('10', 'RGB_DIN_3V3', 'R17', 'strapping: letöltéshez GPIO8 = 1'), ('15', 'BOOT', 'R16', None),
           ('11', 'W5500_CS', 'R36', None), ('12', 'W5500_RST', 'R37', None), ('23', 'GPIO15', 'R18', None),
           ('16', 'CAN_TX', 'R35', 'reset alatt recesszív busz'))
# lépcsőzetesen: a felső jel ér véget legközelebb, így a függőleges szakaszok nem keresztezik egymást
xr0 = pe['10'][0] + 25.4
ys = [pe[n][1] for n, *_ in pu_list]
yrb = min(ys) - 5.08
for i, (n, net, ref, nt) in enumerate(pu_list):
    q = pe[n][:2]
    xr = xr0 + i * 7.62
    S.wire(q, (xr, q[1]), (xr, yrb))
    S.label(net, (q[0] + 7.62, q[1]), 0)
    S.place('Device:R', ref, '10k', {'1': '+3V3', '2': None}, '2', (xr, yrb), fp=R0603, props=P(nt))
S.text('felhúzások (10 k): GPIO8 · BOOT · CS · RST · GPIO15 · CAN_TX', xr0 - 2, yrb - 15)
# R38: W5500_INT felhúzás (a bal oldali jelen)
up('+3V3', (EX - 55.88, 175.26))
shunt('Device:R', 'R38', '10k', (EX - 55.88, 175.26), None, R0603)
stub((EX - 55.88, 182.88), 'W5500_INT', 270, 2.54)

# =====================================================================================================
# 4. ETHERNET – W5500 + HR911105A
# =====================================================================================================
S.text('4. ETHERNET – U5 W5500 + J6 HR911105A MagJack (opcionálisan beültetve; MDI a WIZnet use_mag referencia szerint)', 300, 166, 2)
S.text('VBG (18) NYITVA · RSVD 38–42 NYITVA · RSVD 23 GND · PMODE nyitva = auto-negotiation (R48–R50 lehúzás DNP)', 300, 171)
WX, WY = 365.76, 233.68
w = {n: None for n in ('1', '2', '5', '6', '10', '20', '22', '23', '25', '27', '28', '29', '30', '31', '32', '33', '34',
                         '35', '36', '37', '3', '9', '14', '16', '19', '48', '4', '8', '11', '15', '17', '21', '43', '44', '45')}
pw = S.comp('Interface_Ethernet:W5500', 'U5', 'W5500', WX, WY, w,
            nc=['7', '12', '13', '46', '47', '18', '24', '26', '38', '39', '40', '41', '42'])
for n, net in (('32', 'W5500_CS'), ('33', 'SPI_SCLK'), ('34', 'SPI_MISO'), ('35', 'SPI_MOSI'), ('36', 'W5500_INT'),
               ('37', 'W5500_RST')):
    stub(pw[n][:2], net, 180, 7.62)
stub(pw['23'][:2], 'GND', 180, 2.54)
for n, k in (('43', 2), ('44', 1), ('45', 0)):
    stub(pw[n][:2], f'PMODE{k}', 180, 2.54)
q = pw['28'][:2]
S.wire(q, (q[0], q[1] - 2.54))
up('+3V3', (q[0], q[1] - 2.54))
stub(pw['4'][:2], '+3V3A', 90, 5.08)
stub(pw['29'][:2], 'GND', 270, 2.54)
stub(pw['3'][:2], 'GND', 270, 2.54)
# 25 MHz kvarc a 30/31-en: Y1 függőlegesen balra, terhelőkondenzátorok a GND-re
xi, xq = pw['30'][:2], pw['31'][:2]
xc = xi[0] - 20.32
pyx = S.place('Device:Crystal_GND24', 'Y1', '25MHz ±30ppm', {'1': None, '3': None, '2': 'GND', '4': 'GND'}, '1',
              (xc, xi[1] - 2.54), r=270, fp='Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm')
y1t, y1b = pyx['1'][:2], pyx['3'][:2]
# XTAL25_I = Y1.1, XTAL25_O = Y1.3 → a felső lábról a 30-as, az alsóról a 31-es lábra
pin_i = pyx['1'][:2]
pin_o = pyx['3'][:2]
S.wire(pin_i, (pin_i[0] + 7.62, pin_i[1]), (pin_i[0] + 7.62, xi[1]), xi)
S.wire(pin_o, (pin_o[0] + 10.16, pin_o[1]), (pin_o[0] + 10.16, xq[1]), xq)
pr47 = S.place('Device:R', 'R47', '1M', {'1': None, '2': None}, '1', (pin_i[0] + 3.81, pin_i[1]), fp=R0603, dnp=True,
               props=P('a WIZnet-referencia szerint, alapból nem beültetve'))
S.wire(pr47['2'][:2], (pin_i[0] + 3.81, pin_o[1]))
S.junction((pin_i[0] + 3.81, pin_i[1]))
S.junction((pin_i[0] + 3.81, pin_o[1]))
for pin_, ref, nt in ((pin_i, 'C40', 'C = 2 × (CL − 3…5 pF) a megvett kvarcból'), (pin_o, 'C41', None)):
    S.wire(pin_, (pin_[0] - 7.62, pin_[1]))
    pc_ = S.place('Device:C', ref, '18p', {'1': None, '2': None}, '1', (pin_[0] - 7.62, pin_[1]), r=270, fp=C0603, props=P(nt))
    e = pc_['2'][:2]
    S.wire(e, (e[0] - 2.54, e[1]), (e[0] - 2.54, e[1] + 2.54))
    down('GND', (e[0] - 2.54, e[1] + 2.54))
# jobb oldal: EXRES, TOCAP, 1V2O → GND (az alkatrészek a lábtól jobbra lépcsőzve)
for n, ref, val, lib, fp, dx in (('10', 'R40', '12,4k 1%', 'Device:R', R0603, 5.08), ('20', 'C29', '4µ7', 'Device:C', C0805, 10.16),
                                ('22', 'C30', '10n', 'Device:C', C0603, 15.24)):
    q = pw[n][:2]
    S.wire(q, (q[0] + dx, q[1]))
    shunt(lib, ref, val, (q[0] + dx, q[1]), 'GND', fp)
for n, net in (('25', 'ETH_LED_LINK'), ('27', 'ETH_LED_ACT')):
    stub(pw[n][:2], net, 0, 22.86)
for n, net in (('1', 'ETH_TXN'), ('2', 'ETH_TXP'), ('5', 'ETH_RXN_W'), ('6', 'ETH_RXP_W')):
    stub(pw[n][:2], net, 0, 7.62)
# MDI-lezárás (WIZnet W5500-Ref-RJ45WithMag): TX → 49,9 Ω → +3V3A; RX: 49,9 Ω-ok közös pontja = RCT, 10 nF a GND-re;
# az RX-vonalakban soros 6,8 nF (C19, C61) a W5500 és a MagJack között
mx, my = 419.1, 190.5
S.text('MDI (WIZnet-referencia): TX 49,9 Ω a +3V3A-ra; RX 49,9 Ω → RCT + 10 nF; RX-ben soros 6,8 nF', mx + 25.4, my - 12)
S.rail(my, [mx, mx + 7.62, mx + 17.78, mx + 27.94])
S.label('+3V3A', (mx, my), 180)
for x, ref, net in ((mx + 7.62, 'R20', 'ETH_TXP'), (mx + 17.78, 'R21', 'ETH_TXN')):
    S.place('Device:R', ref, '49R9', {'1': None, '2': None}, '2', (x, my), fp=R0603, props=P('1 %'))
    S.label(net, (x, my - 7.62), 90)
S.wire((mx + 27.94, my), (mx + 27.94, my + 2.54))
S.place('Device:C', 'C16', '10n', {'1': None, '2': 'GND'}, '1', (mx + 27.94, my + 2.54), fp=C0603, props=P('a TXB csomópontnál'))
ry = my + 27.94
S.rail(ry, [mx + 7.62, mx + 17.78, mx + 27.94, mx + 35.56])
S.label('ETH_RCT', (mx + 35.56, ry), 0)
for x, ref, net in ((mx + 7.62, 'R22', 'ETH_RXP_W'), (mx + 17.78, 'R23', 'ETH_RXN_W')):
    S.place('Device:R', ref, '49R9', {'1': None, '2': None}, '2', (x, ry), fp=R0603, props=P('1 %'))
    S.label(net, (x, ry - 7.62), 90)
S.wire((mx + 27.94, ry), (mx + 27.94, ry + 2.54))
S.place('Device:C', 'C17', '10n', {'1': None, '2': 'GND'}, '1', (mx + 27.94, ry + 2.54), fp=C0603,
        props=P('a WIZnet-referencia C15-je: az RX-lezárás közepe és az RCT, 10 nF a GND-re'))
# soros 6,8 nF az RX-vonalakban (WIZnet-referencia C9, C10)
for k, (ref, a, b) in enumerate((('C19', 'ETH_RXP_W', 'ETH_RXP'), ('C61', 'ETH_RXN_W', 'ETH_RXN'))):
    yy = ry + 17.78 + k * 7.62
    S.label(a, (mx + 2.54, yy), 180)
    S.wire((mx + 2.54, yy), (mx + 5.08, yy))
    q = series('Device:C', ref, '6,8n', (mx + 5.08, yy), C0603, props=P('soros, a W5500 RX-lába és a MagJack között'))
    S.wire(q, (q[0] + 5.08, yy))
    S.label(b, (q[0] + 5.08, yy), 0)
# J6 MagJack
JX, JY = 515.62, 226.06
pjx = S.comp('Connector:RJ45_Hanrun_HR911105A_Horizontal', 'J6', 'HR911105A', JX, JY,
             {k: None for k in ('1', '2', '3', '4', '5', '6', '8', '9', '10', '11', '12', 'SH')}, nc=['7'],
             props=P('a lábkiosztást a megvett darab adatlapjából ellenőrizni (TCT és RCT külön lábon)'))
for n, net in (('1', 'ETH_TXP'), ('2', 'ETH_TXN'), ('3', 'ETH_RXP'), ('6', 'ETH_RXN')):
    stub(pjx[n][:2], net, 180, 12.7)
# TCT (4): R24 a +3V3A-ról + C18; RCT (5): C19 – balra, az MDI-címkék alatt
tct, rct = pjx['4'][:2], pjx['5'][:2]
S.wire(tct, (tct[0] - 7.62, tct[1]))
S.wire(rct, (rct[0] - 5.08, rct[1]))
xt = 469.9
yct = JY + 22.86
S.wire((tct[0] - 7.62, tct[1]), (tct[0] - 7.62, yct), (xt, yct))
S.wire((rct[0] - 5.08, rct[1]), (rct[0] - 5.08, yct + 12.7), (xt + 15.24, yct + 12.7))
S.place('Device:R', 'R24', '10R 1%', {'1': None, '2': None}, '2', (xt, yct), r=90, fp=R0603)
S.label('+3V3A', (xt - 7.62, yct), 180)
S.wire((xt + 5.08, yct), (xt + 5.08, yct + 2.54))
S.junction((xt + 5.08, yct))
S.place('Device:C', 'C18', '22n', {'1': None, '2': 'GND'}, '1', (xt + 5.08, yct + 2.54), fp=C0603)
S.label('ETH_RCT', (xt + 15.24, yct + 12.7), 0)
# LED-ek: anód 330 Ω-on át a +3V3-ra, katód a W5500 LED-kimenetén
for n_a, n_k, ref, nt, net in (('9', '10', 'R41', 'zöld = link', 'ETH_LED_LINK'), ('12', '11', 'R42', 'sárga = aktivitás', 'ETH_LED_ACT')):
    qa = pjx[n_a][:2]
    S.wire(qa, (qa[0] + 2.54, qa[1]))
    pr = S.place('Device:R', ref, '330R', {'1': '+3V3', '2': None}, '2', (qa[0] + 2.54, qa[1]), r=270, fp=R0603, props=P(nt))
    stub(pjx[n_k][:2], net, 0, 15.24)
stub(pjx['8'][:2], 'ETH_CGND', 270, 2.54)
sh = pjx['SH'][:2]
S.wire(sh, (sh[0], sh[1] + 7.62))
S.label('ETH_CGND', (sh[0], sh[1] + 3.81), 0)
S.place('Device:C', 'C20', '1n/2kV', {'1': None, '2': 'GND'}, '1', (sh[0], sh[1] + 7.62), fp=C1206,
        props=P('WIZnet-referencia C16: a MagJack árnyékolása és a Bob Smith-lezárás (8-as láb) → 1 nF / 2 kV → GND'))
# W5500 hidegítés: +3V3 → FB1 → +3V3A
hy = 297.18
S.text('W5500 hidegítés: AVDD-lábanként 100 nF; FB1 = HH-1M1608-121JT, ≥ 300 mA', 300, hy - 10)
up('+3V3', (304.8, hy))
S.rail(hy, [304.8, 312.42, 320.04, 327.66])
hang(312.42, hy, 'C37', '100n', props=P('VDD (28)'))
hang(320.04, hy, 'C38', '10µ', fp=C0805)
p = series('Device:FerriteBead_Small', 'FB1', '120R@100MHz', (327.66, hy), 'Inductor_SMD:L_0603_1608Metric',
           props=P('HH-1M1608-121JT, ≥ 300 mA'))
xs_ = [p[0] + 7.62 * (i + 1) for i in range(8)]
S.rail(hy, [p[0]] + xs_)
for i, x in enumerate(xs_[:6]):
    hang(x, hy, f'C{31 + i}', '100n', props=P('AVDD-lábanként'))
hang(xs_[6], hy, 'C39', '10µ', fp=C0805)
S.label('+3V3A', (xs_[7], hy), 0)

# =====================================================================================================
# 5. USB-C
# =====================================================================================================
S.text('5. USB-C – csak eszköz, csak táp-fogyasztó', 20, 322, 2)
S.text('CC1/CC2 külön 5,1 kΩ; USBLC6 az aljzatnál, 22 Ω a C6-nál', 20, 327, 1.4)
UXc, UYc = 40.64, 365.76
pu = S.comp('Connector:USB_C_Receptacle_USB2.0_16P', 'J4', 'USB-C 16P', UXc, UYc,
            {k: None for k in ('A1', 'A12', 'B1', 'B12', 'A4', 'A9', 'B4', 'B9', 'A5', 'B5', 'A6', 'B6', 'A7', 'B7', 'SH')},
            nc=['A8', 'B8'], fp='Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12')
stub(pu['A1'][:2], 'GND', 270, 2.54)
stub(pu['SH'][:2], 'GND', 270, 2.54)
# VUSB sín felül: R30, C21, VUSB-címke, D3 → VIN_BUCK
vu = pu['A4'][:2]
yu = vu[1] - 7.62
S.wire(vu, (vu[0] + 5.08, vu[1]), (vu[0] + 5.08, yu))
vx = [vu[0] + 5.08, vu[0] + 25.4, vu[0] + 33.02, vu[0] + 43.18, vu[0] + 50.8]
S.rail(yu, vx)
hang(vx[1], yu, 'R30', '2,2k', lib='Device:R', fp=R0603, props=P('levezető: a D3 szivárgása ne húzza fel a kihúzott aljzat VBUS-át'))
hang(vx[2], yu, 'C21', '1µ')
S.wire((vx[3], yu), (vx[3], yu - 5.08))
S.label('VUSB', (vx[3], yu - 5.08), 90)
p = series('Device:D_Schottky', 'D3', 'B360', (vx[4], yu), 'Diode_SMD:D_SMC', r=180, lpin='2', rpin='1',
           props=P('60 V-os kell (túlfeszültségnél VIN_BUCK ~45 V, VUSB ~0 V)'))
stub(p, 'VIN_BUCK', 0, 5.08)
# CC1 / CC2 → 5,1 kΩ a GND-re
for pin, ref, dx in (('A5', 'R28', 15.24), ('B5', 'R29', 7.62)):
    q = pu[pin][:2]
    S.wire(q, (q[0] + dx, q[1]))
q1, q2 = pu['A5'][:2], pu['B5'][:2]
# CC1: jobbra 15,24, fel 0 → R28 a csomóponttól felfelé? – a CC-vonalak a DP/DM fölött vannak, ezért az ellenállások FELFELÉ, a VUSB-sín alá nem érnek
S.place('Device:R', 'R28', '5,1k', {'1': None, '2': None}, '1', (q1[0] + 15.24, q1[1]), r=90, fp=R0603)
xcg = q1[0] + 27.94
S.wire(((q1[0] + 15.24) + 7.62, q1[1]), (xcg, q1[1]), (xcg, q2[1] + 2.54))
S.place('Device:R', 'R29', '5,1k', {'1': None, '2': None}, '1', (q2[0] + 7.62, q2[1]), r=90, fp=R0603)
S.wire(((q2[0] + 7.62) + 7.62, q2[1]), (xcg, q2[1]))
S.junction((xcg, q2[1]))
down('GND', (xcg, q2[1] + 2.54))
# DP (A6 + B6) és DM (A7 + B7) párosítva → U8 (USBLC6) → R26 / R27 (22 Ω) → USB_DP / USB_DM
pul = S.comp('Power_Protection:USBLC6-2SC6', 'U8', 'USBLC6-2SC6', 93.98, 383.54, {k: None for k in ('1', '2', '3', '4', '5', '6')})
stub(pul['5'][:2], 'VUSB', 90, 2.54)
stub(pul['2'][:2], 'GND', 270, 2.54)
for a, b, lp, dy in (('A6', 'B6', '1', -5.08), ('A7', 'B7', '3', 5.08)):
    qa, qb = pu[a][:2], pu[b][:2]
    xm = qa[0] + (2.54 if a == 'A7' else 5.08)
    yl, xp = pul[lp][1] + dy, pul[lp][0] - 2.54
    S.wire(qa, (xm, qa[1]))
    S.wire(qb, (xm, qb[1]))
    S.wire((xm, qa[1]), (xm, qb[1]), (xm, yl), (xp, yl), (xp, pul[lp][1]), pul[lp][:2])
    S.junction((xm, qb[1]) if qb[1] > qa[1] else (xm, qa[1]))
    S.label({'1': 'USB_DP_CONN', '3': 'USB_DM_CONN'}[lp], (xm, yl), 0)
for q, ref, net, dy in ((pul['6'][:2], 'R26', 'USB_DP', -5.08), (pul['4'][:2], 'R27', 'USB_DM', 5.08)):
    yl = q[1] + dy
    S.wire(q, (q[0] + 2.54, q[1]), (q[0] + 2.54, yl), (q[0] + 17.78, yl))
    S.label(net + '_CONN', (q[0] + 2.54, yl), 0)
    p = series('Device:R', ref, '22R', (q[0] + 17.78, yl), R0603, props=P('a C6 közelében'))
    S.wire(p, (p[0] + 10.16, yl))
    S.label(net, (p[0] + 10.16, yl), 0)
    S.junction((p[0] + 5.08, yl))
    hang(p[0] + 5.08, yl, {'R26': 'C49', 'R27': 'C50'}[ref], 'DNP', dnp=True, props=P('kondenzátor-footprint (VEZERLO-SPEC 7.), nem beültetve'))

# =====================================================================================================
# 6. CAN + busz
# =====================================================================================================
S.text('6. CAN – U6 TCAN1044AVDRQ1 (MCP2562 szimbólum, lábról lábra azonos) · JP2 alap 5 V: 1044/2562 · 3V3: 330/230 (D60)', 160, 322, 2)
CX, CY = 223.52, 373.38
pc = S.comp('Interface_CAN_LIN:MCP2562-E-SN', 'U6', 'TCAN1044AVDRQ1', CX, CY, {k: None for k in '12345678'},
            fp='Package_SO:SOIC-8_3.9x4.9mm_P1.27mm')
stub(pc['1'][:2], 'CAN_TX', 180, 7.62)
stub(pc['4'][:2], 'CAN_RX', 180, 7.62)
stub(pc['2'][:2], 'GND', 270, 2.54)
# VDD (3) ← JP2 + C42/C43
vd = pc['3'][:2]
yv = vd[1] - 17.78
S.wire(vd, (vd[0], yv))
S.rail(yv, [vd[0] - 20.32, vd[0] - 12.7, vd[0] - 5.08, vd[0], vd[0] + 5.08])
hang(vd[0] - 12.7, yv, 'C43', '1µ')
hang(vd[0] - 5.08, yv, 'C42', '100n')
S.label('CAN_VCC', (vd[0] - 20.32, yv), 180)
pj2 = S.place('Jumper:SolderJumper_3_Bridged12', 'JP2', 'VCC: 1-2=5V / 2-3=3V3', {'1': None, '2': None, '3': None}, '2',
              (vd[0] + 5.08, yv), r=270, fp=SJ3, props=P('SOHA ne legyen mindkét oldal összeforrasztva!'))
for pin, net in (('1', '+5V'), ('3', '+3V3')):
    q = pj2[pin][:2]
    S.wire(q, (q[0] + 5.08, q[1]))
    S.label(net, (q[0] + 5.08, q[1]), 90)
# VIO (5) ← JP3 + C44
vi = pc['5'][:2]
xj3 = vi[0] - 38.1
S.rail(vi[1], [vi[0], vi[0] - 15.24, vi[0] - 25.4, xj3])
hang(vi[0] - 15.24, vi[1], 'C44', '100n')
pj3 = S.place('Jumper:SolderJumper_3_Bridged12', 'JP3', 'VIO: 1-2=3V3 / 2-3=GND', {'1': None, '2': None, '3': None}, '2',
              (xj3, vi[1]), r=90, fp=SJ3, props=P('SN65HVD230-nál nyitva'))
for pin, net in (('1', '+3V3'), ('3', 'GND')):
    q = pj3[pin][:2]
    S.wire(q, (q[0] - 5.08, q[1]))
    S.label(net, (q[0] - 5.08, q[1]), 180)
S.label('CAN_VIO', (vi[0] - 25.4, vi[1]), 270)
# STB (8) → R43 0R → GND
sb = pc['8'][:2]
S.wire(sb, (sb[0] - 5.08, sb[1]), (sb[0] - 5.08, sb[1] + 2.54))
shunt('Device:R', 'R43', '0R', (sb[0] - 5.08, sb[1] + 2.54), 'GND', R0603, props=P('STB → normál mód (nyitva készenlét!)'))
# CANH / CANL → J2 / J3 sávok; ESD (U7) és lezárás (JP1 + R25) a sávok előtt
ch, cl = pc['7'][:2], pc['6'][:2]
BX = 330.2
pj2c = S.comp('Connector_Generic:Conn_01x04', 'J2', 'BUS (XH)', BX, 355.6, {k: None for k in '1234'},
              fp='Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical')
pj3c = S.comp('Connector_Generic:Conn_01x04', 'J3', 'BUS (XH)', BX, 381.0, {k: None for k in '1234'},
              fp='Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical')
lanes = {'1': BX - 12.7, '2': BX - 15.24, '3': BX - 17.78, '4': BX - 20.32}
for n, lx in lanes.items():
    S.wire(pj2c[n][:2], (lx, pj2c[n][1]), (lx, pj3c[n][1]), pj3c[n][:2])
# V_BUS a sáv tetején, GND a sáv alján
S.wire((lanes['1'], pj2c['1'][1]), (lanes['1'], pj2c['1'][1] - 5.08))
S.label('V_BUS', (lanes['1'], pj2c['1'][1] - 5.08), 90)
S.junction((lanes['1'], pj2c['1'][1]))
S.wire((lanes['2'], pj3c['2'][1]), (lanes['2'], pj3c['4'][1] + 7.62))
S.junction((lanes['2'], pj3c['2'][1]))
down('GND', (lanes['2'], pj3c['4'][1] + 7.62))
# CANH → a 4-es sáv, CANL → a 3-as sáv (vízszintes vezetékek a J2 alatt)
ych, ycl = pj2c['4'][1] + 5.08, pj2c['4'][1] + 7.62
stub(ch, 'CAN_H_T', 0, 5.08)
stub(cl, 'CAN_L_T', 0, 5.08)
S.junction((lanes['4'], ych))
S.junction((lanes['3'], ycl))
# a CAN-vonalakról: U7 ESD és JP1 + R25 lezárás – címkével (a vonalakon CAN_H / CAN_L)
xl = ch[0] + 20.32
S.wire((xl, ych), (xl, ych - 7.62))
S.label('CAN_H', (xl, ych - 7.62), 90)
S.wire((xl, ych), (lanes['4'], ych))
S.wire((xl + 7.62, ycl), (xl + 7.62, ycl + 5.08))
S.label('CAN_L', (xl + 7.62, ycl + 5.08), 270)
S.wire((xl + 7.62, ycl), (lanes['3'], ycl))
S.text('ESD (U7) · lezárás: JP1 + R25 (csak a lánc végén)', 255, 398)
S.comp('Power_Protection:NUP2105L', 'U7', 'ESD2CAN24-Q1', 266.7, 406.4, {'1': 'CAN_L', '2': 'CAN_H', '3': 'GND'})
pjp = S.place('Jumper:Jumper_2_Open', 'JP1', 'LEZÁRÁS', {'1': 'CAN_H', '2': None}, '1', (284.48, 406.4),
              fp='Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical')
S.wire(pjp['2'][:2], (pjp['2'][0] + 2.54, pjp['2'][1]))
p = series('Device:R', 'R25', '120R', (pjp['2'][0] + 2.54, pjp['2'][1]), 'Resistor_SMD:R_0805_2012Metric')
S.label('CAN_L', p, 0)

# =====================================================================================================
# 7. Gombok, LED-ek, RGB, debug
# =====================================================================================================
S.text('7. GOMBOK, LED-EK, RGB, DEBUG – U9 és R32 egyszerre NE legyen beültetve', 370, 322, 2)
for i, (ref, val, net) in enumerate((('SW1', 'RESET', 'CHIP_EN'), ('SW2', 'BOOT', 'BOOT'))):
    x = 381 + i * 30.48
    ps = S.comp('Switch:SW_Push', ref, val, x, 340.36, {'1': None, '2': None}, fp='Button_Switch_SMD:SW_SPST_TL3342')
    stub(ps['1'][:2], net, 180, 5.08)
    q = ps['2'][:2]
    S.wire(q, (q[0] + 2.54, q[1]), (q[0] + 2.54, q[1] + 2.54))
    down('GND', (q[0] + 2.54, q[1] + 2.54))
up('+3V3', (439.42, 332.74))
shunt('Device:R', 'R44', '2,2k', (439.42, 332.74), None, R0603)
S.place('Device:LED', 'D5', 'zöld', {'2': None, '1': 'GND'}, '2', (439.42, 345.44), r=90, fp='LED_SMD:LED_0603_1608Metric',
        props=P('táp-LED'))
S.wire((439.42, 340.36), (439.42, 345.44))
# RGB: RGB_DIN_3V3 → U9A → U9B → R31 → RGB_DIN → D6; R32 (DNP) áthidalja az U9-et
ry0 = 368.3
xa = 381.0
S.label('RGB_DIN_3V3', (xa, ry0), 180)
pa = S.place('74xx:74HC14', 'U9', '74HCT14D', {'1': None, '2': None}, '1', (xa + 7.62, ry0), unit=1, fp=U9FP)
S.rail(ry0, [xa, xa + 3.81, xa + 7.62])
pb = S.place('74xx:74HC14', 'U9', '74HCT14D', {'3': None, '4': None}, '3', (pa['2'][0] + 5.08, ry0), unit=2, fp=U9FP)
S.wire(pa['2'][:2], pb['3'][:2])
S.wire(pb['4'][:2], (pb['4'][0] + 2.54, ry0))
p = series('Device:R', 'R31', '33R', (pb['4'][0] + 2.54, ry0), R0603)
xd6 = p[0] + 5.08
S.rail(ry0, [p[0], xd6, xd6 + 5.08])
pd6 = S.place('LED:WS2812B', 'D6', 'WS2812B-V5', {'1': None, '3': 'GND', '4': None}, '4', (xd6 + 5.08, ry0), nc=['2'])
v6 = pd6['1'][:2]
S.wire(v6, (v6[0], v6[1] - 5.08), (v6[0] + 15.24, v6[1] - 5.08))
up('+5V', (v6[0], v6[1] - 5.08))
shunt('Device:C', 'C46', '100n', (v6[0] + 15.24, v6[1] - 5.08), 'GND', C0603, props=P('D6 VDD'))
yr32 = ry0 + 10.16
S.wire((xa + 3.81, ry0), (xa + 3.81, yr32), (xa + 7.62, yr32))
p = series('Device:R', 'R32', '0R', (xa + 7.62, yr32), R0603, dnp=True,
           props=P('DNP – csak ha az U9 nincs beültetve (WS2812B-V5 3,3 V-os bemenettel)'))
S.wire(p, (xd6, yr32), (xd6, ry0))
S.text('RGB_DIN', xd6 - 2, ry0 - 3)
# U9 táp (7. egység) + C45, a nem használt kapuk bemenete a GND-re
pu9 = S.comp('74xx:74HC14', 'U9', '74HCT14D', 368.3, 397.51, {'14': None, '7': None}, unit=7, fp=U9FP)
q = pu9['14'][:2]
S.wire(q, (q[0], q[1] - 2.54), (q[0] + 10.16, q[1] - 2.54))
up('+5V', (q[0], q[1] - 2.54))
shunt('Device:C', 'C45', '100n', (q[0] + 10.16, q[1] - 2.54), 'GND', C0603, props=P('U9 VCC'))
stub(pu9['7'][:2], 'GND', 270, 2.54)
for u, (a, yy) in enumerate((('5', '6'), ('9', '8'), ('11', '10'), ('13', '12')), start=3):
    pg_ = S.comp('74xx:74HC14', 'U9', '74HCT14D', 401.32 + (u - 3) * 20.32, 388.62, {a: None}, nc=[yy], unit=u, fp=U9FP)
    stub(pg_[a][:2], 'GND', 180, 2.54)
# debug (J5) + R33 (DNP)
pj5 = S.comp('Connector_Generic:Conn_01x06', 'J5', 'DEBUG', 568.96, 350.52, {str(i): None for i in range(1, 7)},
             fp='Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical')
for n, net in (('2', 'GND'), ('3', 'U0TXD'), ('4', 'U0RXD'), ('5', 'CHIP_EN'), ('6', 'BOOT')):
    stub(pj5[n][:2], net, 180, 10.16)
q = pj5['1'][:2]
S.wire(q, (q[0] - 5.08, q[1]))
pr = S.place('Device:R', 'R33', '0R', {'1': None, '2': None}, '2', (q[0] - 5.08, q[1]), r=90, fp=R0603, dnp=True,
             props=P('DNP – csak referencia, különben az USB-UART visszatáplál'))
S.wire(pr['1'][:2], (pr['1'][0] - 2.54, q[1]))
up('+3V3', (pr['1'][0] - 2.54, q[1]))
S.text('J5: 1 VREF · 2 GND · 3 TX · 4 RX · 5 EN · 6 BOOT', 530, 340)

# közös módusú CAN-fojtó (DNP) a transceiver és a busz között; alapból a két forrasztható áthidaló köti át (VEZERLO-SPEC 6.4)
S.text('CAN-fojtó: L2 DNP + JP4/JP5 zárva; fojtóval: JP4/JP5 átvágva', 262, 330)
pl2 = S.comp('Device:Filter_EMI_CommonMode', 'L2', 'DNP', 283.21, 339.09, {k: None for k in '1234'}, dnp=True,
             fp='Inductor_SMD:L_CommonModeChoke_Coilank_ACM3225', props=P('pl. TDK ACT45B-510 / ACM3225 – csak ha a mérés indokolja'))
for a, b, n_t, n in (('1', '2', 'CAN_H_T', 'CAN_H'), ('3', '4', 'CAN_L_T', 'CAN_L')):
    stub(pl2[a][:2], n_t, 180, 5.08)
    stub(pl2[b][:2], n, 0, 5.08)
for i, (n_t, n) in enumerate((('CAN_H_T', 'CAN_H'), ('CAN_L_T', 'CAN_L'))):
    pj = S.comp('Jumper:SolderJumper_2_Bridged', f'JP{4 + i}', 'áthidaló', 283.21, 349.25 + i * 7.62, {'1': None, '2': None},
                fp='Jumper:SolderJumper-2_P1.3mm_Bridged_RoundedPad1.0x1.5mm', props=P('alapból zárt; fojtó beültetésekor átvágni'))
    stub(pj['1'][:2], n_t, 180, 5.08)
    stub(pj['2'][:2], n, 0, 5.08)

# W5500 PMODE-lehúzások (DNP): mind nyitva = auto-negotiation
S.text('W5500 PMODE-lehúzás (DNP)', 286, 314)
for i, k in enumerate((0, 1, 2)):
    x = 292.1 + i * 7.62
    S.label(f'PMODE{k}', (x, 302.26), 90)
    shunt('Device:R', f'R{48 + i}', 'DNP', (x, 302.26), 'GND', R0603, dnp=True, props=P('10 k, csak fix PHY-módhoz'))

# =====================================================================================================
# 8. LoRa (D68) – Ebyte E22-900M22S (SX1262, 868 MHz), MINDEN DNP: később beültethető
# =====================================================================================================
S.text('8. LoRa (D68) – U10 Ebyte E22-900M22S (SX1262, 868 MHz) + J7 u.FL – MINDEN DNP, később beültethető', 455, 24, 2)
S.text('SPI a W5500-zal közös; NRST = W5500_RST (közös reset); TXEN = DIO2, RXEN = ¬DIO2 (U11) → firmware: setDio2AsRfSwitch', 455, 29.5)
pk = S.comp('modularis:E22-900M22S', 'U10', 'E22-900M22S', 530.86, 69.85,
            {k: None for k in ('9', '19', '18', '17', '16', '15', '14', '13', '8', '7', '6', '21', '1', '2', '3', '4', '5', '10', '11', '12', '20', '22')},
            fp='modularis:Ebyte_E22-900M22S', dnp=True, props=P('Ebyte E22-900M22S, 14 × 20 mm; az antennarész alatt réz-tiltás'))
for n, net in (('19', 'LORA_CS'), ('18', 'SPI_SCLK'), ('17', 'SPI_MOSI'), ('16', 'SPI_MISO'),
               ('15', 'W5500_RST'), ('14', 'LORA_BUSY'), ('13', 'LORA_DIO1'), ('8', 'LORA_DIO2'), ('7', 'LORA_DIO2'), ('6', 'LORA_RXEN')):
    stub(pk[n][:2], net, 180, 7.62)
# GND-lábak: közös függőleges sínre
gx = pk['1'][0] + 5.08
gns = ('1', '2', '3', '4', '5', '10', '11', '12', '20', '22')
for n in gns:
    S.wire(pk[n][:2], (gx, pk[n][1]))
S.wire((gx, pk['1'][1]), (gx, pk['22'][1] + 2.54))
for n in gns:
    S.junction((gx, pk[n][1]))
down('GND', (gx, pk['22'][1] + 2.54))
# ANT → J7 u.FL (rövid 50 Ω-os vonal a NYÁK-on)
an = pk['21'][:2]
S.wire(an, (an[0] + 12.7, an[1]))
pj7 = S.place('Connector:Conn_Coaxial', 'J7', 'u.FL', {'1': None, '2': 'GND'}, '1', (an[0] + 12.7, an[1]),
              fp='Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical', dnp=True,
              props=P('Hirose U.FL-R-SMT-1; pigtail a ház SMA-jához; 50 Ω-os vonal, alatta folytonos GND'))
# táp: +3V3 → R46 (0 Ω, DNP) → +3V3_LORA, C51 10 µF + C52 100 nF a modul VCC-jénél
xs0, ys0 = 472.44, 40.64
up('+3V3', (xs0, ys0))
pr46 = S.place('Device:R', 'R46', '0R', {'1': None, '2': None}, '1', (xs0, ys0), fp=R0603, dnp=True,
               props=P('a LoRa tápja leválasztható / árammérés'))
yl0 = pr46['2'][1] + 2.54
S.wire(pr46['2'][:2], (xs0, yl0))
vc = pk['9'][:2]
S.rail(yl0, [xs0, xs0 + 7.62, xs0 + 17.78, xs0 + 27.94, vc[0] - 5.08])
S.wire((vc[0] - 5.08, yl0), (vc[0] - 5.08, vc[1]), vc)
hang(xs0 + 7.62, yl0, 'C51', '10µ', fp=C0805, dnp=True)
hang(xs0 + 17.78, yl0, 'C52', '100n', dnp=True)
S.label('+3V3_LORA', (xs0 + 27.94, yl0), 90)
# LORA_CS felhúzás (DNP – a modullal együtt beültetni)
up('+3V3', (482.6, 86.36))
shunt('Device:R', 'R51', '10k', (482.6, 86.36), None, R0603, dnp=True, props=P('NSS felhúzás – a modullal együtt'))
stub((482.6, 93.98), 'LORA_CS', 270, 2.54)
# RXEN = ¬DIO2 – U11 74LVC1G04
pu11 = S.comp('74xGxx:74LVC1G04', 'U11', '74LVC1G04', 515.62, 106.68, {'2': None, '4': None, '3': 'GND', '5': None}, nc=['1'],
              fp='Package_TO_SOT_SMD:SOT-353_SC-70-5', dnp=True, props=P('RF-kapcsoló: RXEN = NOT DIO2'))
stub(pu11['2'][:2], 'LORA_DIO2', 180, 5.08)
stub(pu11['4'][:2], 'LORA_RXEN', 0, 5.08)
v11 = pu11['5'][:2]
S.wire(v11, (v11[0], v11[1] - 2.54), (v11[0] + 10.16, v11[1] - 2.54))
S.label('+3V3_LORA', (v11[0] + 10.16, v11[1] - 2.54), 0)

# =====================================================================================================
# 9. Bővítés és mérőpontok (D69)
# =====================================================================================================
S.text('9. BŐVÍTŐ (J8, GPIO5 = ADC1_CH5): 1-wire / gomb / revízió-osztó · MÉRŐPONTOK', 20, 280, 1.6)
pj8 = S.comp('Connector_Generic:Conn_01x03', 'J8', 'BŐVÍTŐ', 25.4, 297.18, {'1': None, '2': None, '3': None}, mirror='y',
             fp='Connector_JST:JST_PH_B3B-PH-K_1x03_P2.00mm_Vertical', props=P('1 3V3 · 2 GPIO5 · 3 GND (mint a bemeneti modul PH-i)'))
q1, q3 = pj8['1'][:2], pj8['3'][:2]
S.wire(q1, (q1[0] + 2.54, q1[1]), (q1[0] + 2.54, q1[1] - 2.54))
up('+3V3', (q1[0] + 2.54, q1[1] - 2.54))
S.wire(q3, (q3[0] + 2.54, q3[1]), (q3[0] + 2.54, q3[1] + 2.54))
down('GND', (q3[0] + 2.54, q3[1] + 2.54))
q8 = pj8['2'][:2]
S.wire(q8, (q8[0] + 22.86, q8[1]))
S.label('EXP_GPIO5', (q8[0] + 22.86, q8[1]), 0)
S.junction((q8[0] + 7.62, q8[1]))
S.junction((q8[0] + 15.24, q8[1]))
S.wire((q8[0] + 7.62, q8[1]), (q8[0] + 7.62, q8[1] - 2.54))
shunt('Device:R', 'R52', '4k7', (q8[0] + 7.62, q8[1] - 10.16), None, R0603, dnp=True, props=P('felhúzás (pl. 1-wire DS18B20)'))
up('+3V3', (q8[0] + 7.62, q8[1] - 10.16))
hang(q8[0] + 15.24, q8[1], 'R53', 'DNP', lib='Device:R', fp=R0603, dnp=True, props=P('lehúzás / osztó alsó tagja'))
tps = ('+24V_P', '+5V', '+3V3', 'V_BUS', 'CAN_H', 'CAN_L', 'GND')
for i, net in enumerate(tps):
    x = 76.2 + i * 12.7
    if net in ('+3V3', '+5V'):   # tápsín: a tesztpont lefelé, a tápszimbólum fölötte
        S.ref_pos[f'TP{i + 1}'] = ((3.81, 2.54), (3.81, 5.08))
        S.place('Connector:TestPoint', f'TP{i + 1}', net, {'1': None}, '1', (x, 297.18), r=180, fp=TPFP)
        S.wire((x, 297.18), (x, 294.64))
        up(net, (x, 294.64))
        continue
    S.place('Connector:TestPoint', f'TP{i + 1}', net, {'1': None}, '1', (x, 297.18), fp=TPFP)
    S.wire((x, 297.18), (x, 299.72))
    if net == 'GND':
        down('GND', (x, 299.72))
    else:
        S.label(net, (x, 299.72), 270)

# PWR_FLAG-ek
for i, n in enumerate(['GND', '+3V3', '+24V_P', '+24V_F', 'VIN_BUCK', '+3V3A', 'CAN_VCC', 'CAN_VIO', 'VUSB', '+3V3_LORA', '+5V_BUCK', 'ETH_CGND']):
    S.flag(n, 20 + i * 20.32, 405)
S.text('Generálva (hardware/gen/vezerlo.py) – a VEZERLO-SPEC.md alapján; kézi szerkesztés helyett a generátort módosítsd.', 20, 414, 1.4)
S.write(OUT, date='2026-10-19')
print('ok', OUT)
