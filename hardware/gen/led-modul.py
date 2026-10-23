"""LED-modul – modulmag (hierarchikus lap) + 6 low-side csatorna (D43, D47, D53, D65), elrendezett változat.

Felső sáv: betáp (J201 → F201 → +24V_RAIL; Q201 N-FET a GND-ágban – D78) és a sínről leágazó részek (TVS, pufferek, V_RAIL-mérés,
12 V, blokk-biztosítékok + kimeneti sorkapcsok). Középső sáv: a három gate-meghajtó. Alsó sáv: 6 csatornacella
(gate → FET → drain: szabadonfutó, LED-ek, snubber, drain-mérés). Lent: össz-áram (sönt + INA181), hőmérő (MCP9701A).
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import kigen
kigen.POWER_UP = {'+3V3', '+12V'}
kigen.POWER_DOWN = {'GND'}

OUT = sys.argv[1]
S = kigen.Sheet('LED-modul – 6 × 10 A low-side PWM (össz. 15 A), modulmag', 'led-modul')
S.label_pos.update({
    'Driver_FET:UCC27524D': ((-7.62, -12.7), (3.81, 13.97)),   # érték a GND-láb mellett jobbra
    'Amplifier_Current:INA181': ((7.62, 6.35), (7.62, 8.89)),
    'Regulator_Linear:MC78L12_SO8': ((-7.62, -6.35), (-7.62, -3.81)),
    'Transistor_FET:QM6006D': ((5.08, 3.81), (5.08, 6.35)),
    'Transistor_FET:NTMFS016N06CT1G': ((-5.08, -11.43), (-5.08, -8.89)),
    'Device:R_Shunt': ((5.08, -1.27), (5.08, 1.27)),
})
S.label_dx.update({'Connector_Generic:Conn_01x03': 5.08, 'Connector_Generic:Conn_01x02': 5.08, 'Device:LED': 7.62})   # r=90-es LED: a felirat jobbra igazítva, a végpontja kerül ide
S.ref_pos.update({'TP202': ((-10.16, -5.08), (-10.16, -2.54))})
# a snubber-ellenállás és a drain-osztó alsó tagja: felirat balra (jobbra a szomszéd alkatrész áll)
S.ref_pos.update({f'R{230 + n}': ((-7.62, -1.27), (-7.62, 1.27)) for n in range(1, 7)})
S.ref_pos.update({f'R{270 + n}': ((-6.35, -1.27), (-6.35, 1.27)) for n in range(1, 7)})
S.ref_pos.update({f'C{230 + n}': ((-2.54, 10.16), (-2.54, 12.7)) for n in range(1, 7)})   # a GND alá: jobbra a következő csatorna

R0603 = 'Resistor_SMD:R_0603_1608Metric'
R0805 = 'Resistor_SMD:R_0805_2012Metric'
R1206 = 'Resistor_SMD:R_1206_3216Metric'
C0603 = 'Capacitor_SMD:C_0603_1608Metric'
C0805 = 'Capacitor_SMD:C_0805_2012Metric'
C1206 = 'Capacitor_SMD:C_1206_3216Metric'
C1210 = 'Capacitor_SMD:C_1210_3225Metric'
LED0603 = 'LED_SMD:LED_0603_1608Metric'
TB2 = 'TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2_1x02_P5.00mm_Horizontal'   # D84: Degson DG128-5.0-02P
TB3 = 'TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-3_1x03_P5.00mm_Horizontal'   # D84: KF128-5.0-3P


def P(n):
    return {'Megjegyzés': n}


def up(net, p):
    S.label(net, p, 90)


def down(net, p):
    S.label(net, p, 270)


def shunt(lib, ref, val, top, bottom_net, fp, r=0, top_pin='1', bot_pin='2', **k):
    return S.place(lib, ref, val, {top_pin: None, bot_pin: bottom_net}, top_pin, top, r=r, fp=fp, **k)


def series(lib, ref, val, left, fp, r=90, lpin='1', rpin='2', **k):
    pp = S.place(lib, ref, val, {lpin: None, rpin: None}, lpin, left, r=r, fp=fp, **k)
    return pp[rpin][:2]


def tap(rail_y, x, top_y):
    S.wire((x, rail_y), (x, top_y))


# =================== Modulmag ===================
S.text('MODULMAG – táp a buszról (D71)', 15, 24, 1.5)
S.text('a 24 V-ot a PB1 méri, a főbiztosíték előtt', 15, 28.5, 1.5)
left = [('HW_ID', 'HW_ID'), ('GND_BUS', 'GND_BUS')]
# D78 (STM32L433): CH4/CH5 = TIM15 CH1/CH2 (PB14/PB15), CH6 = TIM16 CH1 (PB8) – a TIM8 helyett; I_SENSE a PA3-on
# (COMP2+ és ADC1_IN8), a DS4 a PA7-re; VIN_SENSE a PB1-en (a PB11 az L433-on nem ADC-s)
right = [('PA8', 'CH1_PWM'), ('PA9', 'CH2_PWM'), ('PA10', 'CH3_PWM'), ('PB14', 'CH4_PWM'), ('PB15', 'CH5_PWM'),
         ('PB8', 'CH6_PWM'), ('PB12', 'DRV_EN'), ('PA3', 'I_SENSE'), ('PA4', 'DAC_THR'), ('PC2', 'V_RAIL_SENSE'),
         ('PC3', 'T_SENSE'), ('PA0', 'DS1'), ('PA1', 'DS2'), ('PA2', 'DS3'), ('PA7', 'DS4'), ('PA5', 'DS5'), ('PA6', 'DS6'),
         ('PB1', 'VIN_SENSE'), ('PB9', None), ('PB11', None), ('PB13', None)]
S.subsheet('modulmag', '../modulmag/modulmag.kicad_sch', 25, 35, 35, 2.54 * (len(right) + 1), left=left, right=right)

# HW-ID (MODULMAG-SPEC 3.5, D71): LED = 10k / 715 Ω → 0,22 V → 1. sáv (16 sáv)
S.text('HW-ID: LED-modul = 1. sáv (0,22 V)', 15, 104)
up('+3V3', (20, 108))
shunt('Device:R', 'R201', '10k 1%', (20, 108), None, R0603)
nh = (20, 118.11)
S.wire((20, 115.62), nh)
shunt('Device:R', 'R202', '715R 1%', (20, 120.65), 'GND', R0603)
S.wire(nh, (20, 120.65))
shunt('Device:C', 'C201', '100n', (30, 120.65), 'GND', C0603)
S.wire(nh, (30, nh[1]), (30, 120.65))
S.wire((30, nh[1]), (36, nh[1]))
S.label('HW_ID', (36, nh[1]), 0)
S.junction(nh)
S.junction((30, nh[1]))

# VIN_SENSE (D71, D78): a 24 V a főbiztosíték ELŐTT → PB1 (150k / 10k: 24 V → 1,5 V, 12 V → 0,75 V)
S.text('VIN_SENSE (PB1): 24 V az F201 előtt', 50, 137)
xvs = 55.88
up('+24V_IN', (xvs, 109.22))
shunt('Device:R', 'R290', '150k', (xvs, 109.22), None, R0603, props=P('fordított polaritásnál a Q201 zár, a lap nem kap feszültséget (D78)'))
nvs = (xvs, 119.38)
S.wire((xvs, 116.84), nvs)
shunt('Device:R', 'R291', '10k', (xvs, 121.92), 'GND', R0603)
S.wire(nvs, (xvs, 121.92))
shunt('Device:C', 'C290', '100n', (xvs + 8.89, 121.92), 'GND', C0603)
S.wire(nvs, (xvs + 8.89, nvs[1]), (xvs + 8.89, 121.92))
S.wire((xvs + 8.89, nvs[1]), (xvs + 13.97, nvs[1]))
S.label('VIN_SENSE', (xvs + 13.97, nvs[1]), 0)
S.junction(nvs)
S.junction((xvs + 8.89, nvs[1]))


# busz-GND (D74): a GND_BUS (XH 2-es tű) a modul GND-jére 1R-on át – a nagyáramú modul hurokárama ne a buszon folyjon
S.label('GND_BUS', (27.94, 135.89), 180)
S.wire((27.94, 135.89), (27.94 + 2.54, 135.89))
_pg = S.place('Device:R', 'R293', '1R', {'1': None, '2': None}, '1', (27.94 + 2.54, 135.89), r=90, fp='Resistor_SMD:R_1206_3216Metric',
              props=P('D74: 1 Ω (1206) – a 20 A-es visszatérő áram legfeljebb ~0,2 A-ig folyhat a buszon (0 Ω-mal 1–2 A); 0 Ω-mal áthidalható'))
_q = _pg['2'][:2]
S.wire(_q, (_q[0] + 2.54, _q[1]), (_q[0] + 2.54, _q[1] + 2.54))
S.label('GND', (_q[0] + 2.54, _q[1] + 2.54), 270)

# =================== 1. Betáp és +24V_RAIL ===================
Y = 45
S.text('1. BETÁP (15 A): J201 → F201 15 A → +24V_RAIL; fordított polaritás ellen Q201 N-FET a GND-ágban (D78) – a közös föld miatt a + ági védelem nem elég', 80, 24, 1.5)
S.text('Q201 hiányában a D–S padek vastag dróttal áthidalhatók (akkor nincs polaritásvédelem)', 150, 29)
S.ref_pos['J201'] = ((-2.54, -7.62), (-2.54, -5.08))   # a csatlakozó fölé
pj = S.comp('Connector_Generic:Conn_01x02', 'J201', '24V IN 15A', 90, 60, {'1': None, '2': None}, fp=TB2,
            props=P('csavaros, liftes: Degson DG128-5.0-02P (5,0 mm, 15 A UL / 18 A IEC, 2,5 mm²) – D84; barna = +24 V, kék = GND (D43)'))
p1, p2 = pj['1'][:2], pj['2'][:2]
xa = p1[0] - 7.62
S.wire(p1, (xa, p1[1]), (xa, Y), (xa + 12.7, Y))
S.wire(p2, (p2[0] - 2.54, p2[1]), (p2[0] - 2.54, p2[1] + 2.54))
S.label('GND_IN', (p2[0] - 2.54, p2[1] + 2.54), 270)
S.wire((xa + 2.54, Y), (xa + 2.54, Y - 5.08))
S.label('+24V_IN', (xa + 2.54, Y - 5.08), 90)
S.junction((xa + 2.54, Y))
p = series('Device:Fuse', 'F201', '15A', (xa + 12.7, Y), 'Fuse:Fuse_Littelfuse-NANO2-451_453',
           props=P('D85: Littelfuse 0451015.MRL (NANO² 15 A, 2410) – beforrasztott; 15 A = a J201 névleges árama (D84)'))
# Q201 a GND-ágban: D = J201 GND-pólusa (GND_IN), S = a lap GND-je; G a +24V_RAIL-ről 10 k-n át, 15 V-os Zener védi.
# Helyes polaritásnál a gate ~15 V-ot kap → vezet (15 A × ~2,8 mΩ ≈ 42 mV, ~0,6 W); fordítva Vgs ≤ 0 és a body-dióda is zár →
# a GND-pólusra kerülő +24 V nem jut a lap (és a busz) GND-jére.
S.ref_pos['Q201'] = ((6.35, -1.27), (6.35, 1.27))   # a FET jobb oldalára
pq = S.place('Transistor_FET:NTMFS016N06CT1G', 'Q201', 'NCEP6090AGU', {'1': None, '2': None, '3': None, '4': None, '5': None},
             '4', (114.3, 66.04), fp='Package_SO:ONSemi_SO-8FL_488AA',
             props={'Megjegyzés': 'D85: NCE 60 V, 2,8 mΩ, DFN5×6 (power-SO8, az SO-8FL padképére; az NTMFS5C604NL nem kapható); D = GND_IN (J201), S = GND',
                    'Description': 'N-MOSFET 60 V, 2,8 mΩ (NCE NCEP6090AGU)'})
qd, qs, qg = pq['5'][:2], pq['1'][:2], pq['4'][:2]
S.wire(qd, (qd[0], qd[1] - 2.54))
S.label('GND_IN', (qd[0], qd[1] - 2.54), 90)
S.wire(qs, (qs[0], qs[1] + 2.54))
down('GND', (qs[0], qs[1] + 2.54))
gn = (qg[0] - 7.62, qg[1])
S.wire(qg, gn)
S.wire((gn[0], gn[1] - 2.54), gn)
shunt('Device:R', 'R294', '10k', (gn[0], gn[1] - 10.16), None, R0603, props=P('gate a +24V_RAIL-ről (26 V-on ~1,1 mA)'))
S.wire((gn[0], gn[1] - 10.16), (gn[0], Y))
S.junction((gn[0], Y))
shunt('Device:D_Zener', 'D202', 'BZT52C15', (gn[0], gn[1] + 2.54), 'GND', 'Diode_SMD:D_SOD-123', r=270,
      props=P('15 V – a gate–source ±20 V-os határa alatt tartja (12 V-os tápnál nem vezet)'))
S.wire(gn, (gn[0], gn[1] + 2.54))
S.junction(gn)

xr0 = p[0] + 27.94
# +24V_RAIL sín
taps = [xr0 + 10 + i * 15.24 for i in range(5)]   # a D201/C203 felirata ne lógjon a szomszédra
xdiv = xr0 + 86.36
xreg = xr0 + 116.84
fuses = [xr0 + 162.56, xr0 + 195.58, xr0 + 228.6]
S.rail(Y, [p[0], xr0, xr0 + 5] + taps + [xdiv, xreg] + fuses)
S.wire((xr0 + 5, Y), (xr0 + 5, Y - 7.62))
S.label('+24V_RAIL', (xr0 + 5, Y - 7.62), 90)
shunt('Device:D_Zener', 'D201', 'SMBJ28A', (taps[0], Y + 5.08), 'GND', 'Diode_SMD:D_SMB', r=270, props=P('TVS a sínen'))
tap(Y, taps[0], Y + 5.08)
shunt('Device:C_Polarized', 'C203', '470µ/50V', (taps[1], Y + 5.08), 'GND', 'Capacitor_THT:CP_Radial_D10.0mm_P5.00mm',
      props=P('low-ESR, 105 °C; GND-oldala a sönt ELŐTT'))
tap(Y, taps[1], Y + 5.08)
for i, x in enumerate(taps[2:5]):
    shunt('Device:C', f'C{204 + i}', '10µ/50V', (x, Y + 5.08), 'GND', C1210, props=P('a FET-ek mellett'))
    tap(Y, x, Y + 5.08)
S.text('pufferek: a GND-oldaluk a sönt előtt', taps[1] - 2, Y + 22)
# V_RAIL mérés (D47)
shunt('Device:R', 'R203', '100k', (xdiv, Y + 5.08), None, R0603)
tap(Y, xdiv, Y + 5.08)
nv = (xdiv, Y + 15.24)
S.wire((xdiv, Y + 12.7), nv)
shunt('Device:R', 'R204', '10k', (xdiv, Y + 17.78), 'GND', R0603)
S.wire(nv, (xdiv, Y + 17.78))
shunt('Device:C', 'C207', '100n', (xdiv + 7.62, Y + 17.78), 'GND', C0603)
S.wire(nv, (xdiv + 7.62, nv[1]), (xdiv + 7.62, Y + 17.78))
S.junction(nv)
S.wire((xdiv + 7.62, nv[1]), (xdiv + 12.7, nv[1]))
S.junction((xdiv + 7.62, nv[1]))
S.label('V_RAIL_SENSE', (xdiv + 12.7, nv[1]), 0)
S.text('V_RAIL → PC2', xdiv - 3, Y + 32)
# 12 V a gate-meghajtóknak
tap(Y, xreg, Y + 10.16)
S.wire((xreg, Y + 10.16), (xreg + 7.62, Y + 10.16))
pr = S.place('Regulator_Linear:MC78L12_SO8', 'U205', 'MC78L12ACDR2G',
             {'8': None, '1': None, '2': 'GND', '3': 'GND', '6': 'GND', '7': 'GND'}, '8', (xreg + 7.62, Y + 10.16),
             nc=['4', '5'], fp='Package_SO:SOIC-8_3.9x4.9mm_P1.27mm')
shunt('Device:C', 'C208', '1µ/50V', (xreg + 2.54, Y + 12.7), 'GND', C0805)
S.wire((xreg + 2.54, Y + 10.16), (xreg + 2.54, Y + 12.7))
S.junction((xreg + 2.54, Y + 10.16))
o = pr['1'][:2]
S.wire(o, (o[0] + 7.62, o[1]))
shunt('Device:C', 'C209', '10µ/25V', (o[0] + 5.08, o[1] + 2.54), 'GND', C1206)
S.wire((o[0] + 5.08, o[1]), (o[0] + 5.08, o[1] + 2.54))
S.junction((o[0] + 5.08, o[1]))
S.wire((o[0] + 7.62, o[1]), (o[0] + 7.62, o[1] - 5.08))
up('+12V', (o[0] + 7.62, o[1] - 5.08))
# blokk-biztosítékok → kimeneti sorkapcsok
for k, x in enumerate(fuses, 1):
    pf = S.place('Device:Fuse', f'F{201 + k}', '10A', {'1': None, '2': None}, '1', (x, Y + 5.08), fp='Fuse:Fuse_Littelfuse-NANO2-451_453',
                 props=P('Littelfuse 451/453 NANO² (2410) – értéke a bekötött szalag szerint (D76/D30): ≤ 100 W-os ághoz 4 A (24 V) / 8 A (12 V); legfeljebb 10 A (0451010.MRL)'))
    tap(Y, x, Y + 5.08)
    b = pf['2'][:2]
    S.ref_pos[f'J{201 + k}'] = ((-2.54, -7.62), (-2.54, -5.08))
    pjb = S.comp('Connector_Generic:Conn_01x03', f'J{201 + k}', f'BLOKK {k}', x + 17.78, b[1] + 10.16, {'1': None, '2': None, '3': None},
                 fp=TB3, props=P(f'1 = +24 V, 2 = CH{2 * k - 1}, 3 = CH{2 * k}; csavaros, KF128-5.0-3P (5,0 mm, 10 A – a blokkbiztosíték ≤ 10 A) – D84'))
    S.wire(b, (b[0], pjb['1'][1]), pjb['1'][:2])
    S.label(f'+24V_B{k}', (b[0], pjb['1'][1]), 180)
    for n, ch in (('2', 2 * k - 1), ('3', 2 * k)):
        a = pjb[n][:2]
        S.wire(a, (a[0] - 7.62, a[1]))
        S.label(f'CH{ch}_D', (a[0] - 7.62, a[1]), 180)

# =================== 2. Gate-meghajtók ===================
yg = 124.46
S.text('2. GATE-MEGHAJTÓK – 3 × UCC27524 (12 V): EN közösen a DRV_EN-en (PB12), 1 k lehúzás → bekapcsoláskor minden csatorna KI', 80, yg - 39, 1.5)
S.text('6 EN-láb belső 200 k felhúzása a 12 V-ra párhuzamosan ~33 k → 1 k-val ~0,35 V (< 0,8 V); az IN-lábakon 120 k belső lehúzás is van', 80, yg - 35.5)
xe = 85
S.label('DRV_EN', (xe, yg), 180)
S.wire((xe, yg), (xe + 5.08, yg))
shunt('Device:R', 'R205', '1k', (xe + 5.08, yg + 2.54), 'GND', R0603,
      props=P('NE legyen nagyobb: 4,7 k-val ~1,5 V → a driverek engedélyezve lehetnek'))
S.wire((xe + 5.08, yg), (xe + 5.08, yg + 2.54))
for d in range(3):
    x = 140 + d * 85
    a, b = 2 * d + 1, 2 * d + 2
    pd = S.comp('Driver_FET:UCC27524D', f'U{201 + d}', 'UCC27524DR', x, yg, {str(i): None for i in range(1, 9)},
                fp='Package_SO:SOIC-8_3.9x4.9mm_P1.27mm')
    for n, net in (('2', f'CH{a}_PWM'), ('4', f'CH{b}_PWM')):
        q = pd[n][:2]
        S.wire(q, (q[0] - 12.7, q[1]))
        S.label(net, (q[0] - 12.7, q[1]), 180)
    e1, e8 = pd['1'][:2], pd['8'][:2]
    xe1 = e1[0] - 5.08
    S.wire(e1, (xe1, e1[1]))
    S.wire(e8, (xe1, e8[1]))
    S.wire((xe1, e1[1]), (xe1, e1[1] - 5.08))
    S.label('DRV_EN', (xe1, e1[1] - 5.08), 90)
    S.wire((xe1, e1[1]), (xe1, e8[1]))
    S.junction((xe1, e1[1]))
    for n, net in (('7', f'CH{a}_GD'), ('5', f'CH{b}_GD')):
        q = pd[n][:2]
        S.wire(q, (q[0] + 10.16, q[1]))
        S.label(net, (q[0] + 10.16, q[1]), 0)
    S.wire(pd['3'][:2], (pd['3'][0], pd['3'][1] + 2.54))
    down('GND', (pd['3'][0], pd['3'][1] + 2.54))
    v = pd['6'][:2]
    yv = v[1] - 15.24
    S.wire(v, (v[0], yv), (v[0] + 25.4, yv))
    up('+12V', (v[0], yv))
    for xc, ref, val, fp in ((v[0] + 12.7, f'C{210 + 2 * d}', '1µ/25V', C0805), (v[0] + 25.4, f'C{211 + 2 * d}', '100n', C0603)):
        shunt('Device:C', ref, val, (xc, yv + 2.54), 'GND', fp)
        S.wire((xc, yv), (xc, yv + 2.54))
    S.junction((v[0] + 12.7, yv))

# =================== 3. Csatornák ===================
yB, yN = 158.75, 180.34          # +24V_Bk sor, drain-csomópont
S.text('3. CSATORNÁK (× 6): FET NCE6080K (DPAK; tartalék IRFR1205) · szabadonfutó SS56B a blokk +24 V-jára · RC snubber (DNP) ·'
       ' gate-LED + drain-LED · drain → ADC osztó', 15, yB - 12, 1.5)
for n in range(1, 7):
    k = (n + 1) // 2
    x0 = 18 + (n - 1) * 64
    xs = x0 + 26                 # drain / szabadonfutó oszlop
    xl = xs - 12.7               # drain-LED oszlop
    S.text(f'CH{n}', x0 + 2, yB - 5)
    # +24V_Bk
    S.wire((xl, yB), (xs, yB))
    S.label(f'+24V_B{k}', (xl, yB), 180)
    S.wire((xs, yB), (xs, yB + 2.54))
    S.place('Device:D_Schottky', f'D{210 + n}', 'SS56B', {'1': None, '2': None}, '1', (xs, yB + 2.54), r=270,
            fp='Diode_SMD:D_SMB', props=P('szabadonfutó, 5 A / 60 V, SMB (D85)'))
    S.wire((xs, yB + 10.16), (xs, yN))
    # drain-LED: +24V_Bk → 10k → LED → drain
    S.wire((xl, yB), (xl, yB + 2.54))
    shunt('Device:R', f'R{250 + n}', '10k', (xl, yB + 2.54), None, R0805)
    S.place('Device:LED', f'D{230 + n}', 'zöld', {'2': None, '1': None}, '2', (xl, yB + 12.7), r=90, fp=LED0603,
            props=P(f'CH{n} kimenet (drain) – előlap'))
    S.wire((xl, yB + 10.16), (xl, yB + 12.7))
    S.wire((xl, yB + 20.32), (xl, yN))
    # FET: D felfelé a csomópontra, S lefelé PGND_SH, G balra
    pq = S.place('Transistor_FET:QM6006D', f'Q{201 + n}', 'NCE6080K', {'1': None, '2': None, '3': None}, '2', (xs, yN + 5.08),
                 fp='Package_TO_SOT_SMD:TO-252-2',
                 props={'Megjegyzés': 'D85: NCE 60 V, 8,5 mΩ @ 10 V, DPAK (az NTD5C648NL megszűnt); 10 A-en ~0,85 W; tartalék: IRFR1205',
                        'Description': 'N-MOSFET 60 V, DPAK (NCE NCE6080K)'})
    S.wire((xs, yN), (xs, yN + 5.08))
    s3 = pq['3'][:2]
    S.wire(s3, (s3[0], s3[1] + 2.54))
    S.label('PGND_SH', (s3[0], s3[1] + 2.54), 270)
    gp = pq['1'][:2]
    # gate: CHn_GD → 10R → G, 10k lehúzás G → PGND_SH
    gn = (gp[0] - 2.54, gp[1])
    S.wire(gn, gp)
    pr_ = S.place('Device:R', f'R{210 + n}', '10R', {'1': None, '2': None}, '2', gn, r=90, fp=R0603,
                  props=P('gate-ellenállás (élmeredekség, EMC)'))
    gd = pr_['1'][:2]
    shunt('Device:R', f'R{220 + n}', '10k', (gn[0], gn[1] + 5.08), 'PGND_SH', R0603, props=P('gate–source lehúzás'))
    S.wire(gn, (gn[0], gn[1] + 5.08))
    S.junction(gn)
    # gate-LED: CHn_GD → 10k → LED → GND (D76: a 4k7 helyett – feleannyi áram az MC78L12-ből, ~1 mA is jól látható)
    xg = gd[0] - 2.54
    S.wire(gd, (xg, gd[1]))
    S.wire((xg, gd[1]), (xg, gd[1] - 5.08))
    S.label(f'CH{n}_GD', (xg, gd[1] - 5.08), 90)
    shunt('Device:R', f'R{240 + n}', '10k', (xg, gd[1] + 2.54), None, R0603)
    S.wire((xg, gd[1]), (xg, gd[1] + 2.54))
    S.junction((xg, gd[1]))
    S.place('Device:LED', f'D{220 + n}', 'zöld', {'2': None, '1': 'GND'}, '2', (xg, gd[1] + 12.7), r=90, fp=LED0603,
            props=P(f'CH{n} gate – előlap, fényvezető'))
    S.wire((xg, gd[1] + 10.16), (xg, gd[1] + 12.7))
    # drain-csomópont jobbra: CHn_D címke, snubber, drain-mérés
    xsn = xr1 = xs + 17.78     # a FET feliratai a FET és a snubber-oszlop között
    S.rail(yN, [xl, xs, xsn, xr1 + 2.54])
    S.wire((xr1, yN), (xr1, yN - 5.08))
    S.label(f'CH{n}_D', (xr1, yN - 5.08), 90)
    shunt('Device:R', f'R{230 + n}', '10R', (xsn, yN + 2.54), None, R1206, dnp=True, props=P('RC snubber – csak mérés után (D24)'))
    S.wire((xsn, yN), (xsn, yN + 2.54))
    shunt('Device:C', f'C{220 + n}', '2n2/100V', (xsn, yN + 12.7), 'PGND_SH', C1206, dnp=True)
    S.wire((xsn, yN + 10.16), (xsn, yN + 12.7))
    pr2 = series('Device:R', f'R{260 + n}', '470k', (xr1 + 2.54, yN), R0603)
    dn = (pr2[0] + 2.54, yN)
    S.wire(pr2, (dn[0] + 7.62, yN))
    shunt('Device:R', f'R{270 + n}', '56k', (dn[0], yN + 2.54), 'GND', R0603)
    S.wire(dn, (dn[0], yN + 2.54))
    shunt('Device:C', f'C{230 + n}', '10n', (dn[0] + 5.08, yN + 2.54), 'GND', C0603)
    S.wire((dn[0] + 5.08, yN), (dn[0] + 5.08, yN + 2.54))
    S.junction(dn)
    S.junction((dn[0] + 5.08, yN))
    S.label(f'DS{n}', (dn[0] + 7.62, yN), 90)
S.text('Drain → ADC: 24 V → 2,55 V. KI: ≈ V_RAIL = szalag rajta; ≈ V_RAIL − ~2 V = nincs szalag (a drain-LED-en át); ~0 V = kiolvadt blokk-biztosíték.'
       ' BE: ≈ V_RAIL × (1 − kitöltés); mindig ~0 V = átütött FET', 15, 219)

# =================== 4. Össz-áram, hőmérő, mérőpontok ===================
ys = 248.92
S.text('4. ÖSSZ-ÁRAM (D47, D53): 1 mΩ sönt a FET-ek közös source-ága (PGND_SH) és a GND között, Kelvin → INA181A2 (×50) → PA3', 15, ys - 23, 1.5)
S.text('(ADC1_IN8 + COMP2 → TIM1/TIM15/TIM16 break, D78); a küszöb a DAC1-ről (PA4, belül a COMP2 − bemenetére); 20 A → 1,0 V', 15, ys - 18.5)
xsh = 40
S.label('PGND_SH', (xsh, ys - 2.54), 90)
S.flag('PGND_SH', xsh - 10, ys - 2.54)
S.wire((xsh - 10, ys - 2.54), (xsh, ys - 2.54))
psh = S.place('Device:R_Shunt', 'R209', '1m 1%', {'1': None, '2': None, '3': None, '4': None}, '1', (xsh, ys + 2.54),
              fp='Resistor_SMD:R_Shunt_Vishay_WSK2512_6332Metric_T1.19mm',
              props=P('D84: Bourns CRE2512-FZ-R001E-3 (2512, 3 W; 15 A-en 0,23 W) – 2 kivezetésű: a Kelvin-padokon összeforrasztva'))
S.wire((xsh, ys - 2.54), (xsh, ys + 2.54))
S.wire(psh['4'][:2], (xsh, psh['4'][1] + 2.54))
down('GND', (xsh, psh['4'][1] + 2.54))
pi = S.place('Amplifier_Current:INA181', 'U206', 'INA181A2IDBVR', {'1': None, '2': 'GND', '3': None, '4': None, '5': 'GND', '6': None},
             '3', (psh['2'][0] + 10.16, psh['2'][1]))
S.wire(psh['2'][:2], pi['3'][:2])
S.wire(psh['3'][:2], pi['4'][:2])
v6 = pi['6'][:2]
S.wire(v6, (v6[0], v6[1] - 10.16), (v6[0] + 12.7, v6[1] - 10.16))
up('+3V3', (v6[0], v6[1] - 10.16))
shunt('Device:C', 'C240', '100n', (v6[0] + 12.7, v6[1] - 10.16), 'GND', C0603)
o = pi['1'][:2]
S.wire(o, (o[0] + 5.08, o[1]))
pr3 = series('Device:R', 'R207', '100R', (o[0] + 5.08, o[1]), R0603)
isn = (pr3[0] + 5.08, o[1])
S.wire(pr3, (isn[0] + 10.16, o[1]))
shunt('Device:C', 'C241', '1n', (isn[0], o[1] + 2.54), 'GND', C0603)
S.wire(isn, (isn[0], o[1] + 2.54))
S.junction(isn)
S.label('I_SENSE', (isn[0] + 10.16, o[1]), 0)
S.place('Connector:TestPoint', 'TP202', 'I_SENSE', {'1': None}, '1', (isn[0] + 5.08, o[1]), fp='TestPoint:TestPoint_Pad_D1.5mm')
S.junction((isn[0] + 5.08, o[1]))
S.label('DAC_THR', (isn[0] + 35, o[1]), 180)
S.wire((isn[0] + 35, o[1]), (isn[0] + 40, o[1]))
S.place('Connector:TestPoint', 'TP201', 'DAC_THR', {'1': None}, '1', (isn[0] + 40, o[1]), fp='TestPoint:TestPoint_Pad_D1.5mm',
        props=P('PA4 = DAC1_OUT1, a COMP2 küszöbe – kívül nincs bekötve'))
# Hőmérő (D78): MCP9701A a FET-ek között – lineáris (19,5 mV/°C, 0 °C = 400 mV), közvetlenül az ADC-re (PC3)
xn = 200
S.text('HŐMÉRŐ (PC3): U207 MCP9701A, 19,5 mV/°C – D30, D78', xn - 20, ys - 12)
S.ref_pos['U207'] = ((-19.05, 8.89), (-19.05, 11.43))
up('+3V3', (xn, ys - 2.54))
pt = S.place('Sensor_Temperature:MCP9700Ax-ETT', 'U207', 'MCP9701AT-E/TT', {'1': None, '2': None, '3': 'GND'}, '1', (xn, ys + 2.54),
             fp='Package_TO_SOT_SMD:SOT-23', props=P('kézben ~21 db; ±2 °C (A); a 100 nF-os terhelés elé 200 Ω soros ellenállás'))
S.wire((xn, ys - 2.54), (xn, ys + 2.54))
shunt('Device:C', 'C243', '100n', (xn - 17.78, ys + 2.54), 'GND', C0603)
S.wire((xn, ys), (xn - 17.78, ys), (xn - 17.78, ys + 2.54))
S.junction((xn, ys))
o = pt['2'][:2]
S.wire(o, (o[0] + 2.54, o[1]))
pr4 = series('Device:R', 'R208', '200R', (o[0] + 2.54, o[1]), R0603, props=P('a VOUT nagy kapacitív terhelés esetén soros ellenállást kér'))
nn = (pr4[0] + 5.08, o[1])
S.wire(pr4, (nn[0] + 7.62, o[1]))
shunt('Device:C', 'C242', '100n', (nn[0], o[1] + 2.54), 'GND', C0603)
S.wire(nn, (nn[0], o[1] + 2.54))
S.junction(nn)
S.label('T_SENSE', (nn[0] + 7.62, o[1]), 0)
# PWR_FLAG-ek a betáp-sínekre (ERC) – külön sorban, a sínek feliratait nem takarják
for i, n in enumerate(['+24V_IN', '+24V_RAIL']):
    S.flag(n, 262 + i * 17.78, 238)

S.text('Generálva (hardware/gen/led-modul.py) – D43/D47/D53/D65 alapján; kézi szerkesztés helyett a generátort módosítsd.', 15, 281, 1.3)
S.write(OUT, date='2026-10-23')
print('ok', OUT)
