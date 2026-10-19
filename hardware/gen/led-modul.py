"""LED-modul – modulmag (hierarchikus lap) + 6 low-side csatorna (D43, D47, D53, D65), elrendezett változat.

Felső sáv: betáp (J201 → F201 → ideális dióda → +24V_RAIL) és a sínről leágazó részek (TVS, pufferek, V_RAIL-mérés,
12 V, blokk-biztosítékok + kimeneti sorkapcsok). Középső sáv: a három gate-meghajtó. Alsó sáv: 6 csatornacella
(gate → FET → drain: szabadonfutó, LED-ek, snubber, drain-mérés). Lent: össz-áram (sönt + INA181), NTC.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import kigen
kigen.POWER_UP = {'+3V3', '+12V'}
kigen.POWER_DOWN = {'GND'}

OUT = sys.argv[1]
S = kigen.Sheet('LED-modul – 6 × 10 A low-side PWM (össz. 20 A), modulmag', 'led-modul')
S.label_pos.update({
    'Driver_FET:UCC27524D': ((-7.62, -12.7), (-7.62, 13.97)),
    'Amplifier_Current:INA181': ((-2.54, 11.43), (-2.54, 13.97)),
    'Power_Management:LM74700': ((-10.16, 13.97), (-10.16, 16.51)),
    'Regulator_Linear:MC78L12_SO8': ((-7.62, -6.35), (-7.62, -3.81)),
    'Transistor_FET:QM6006D': ((5.08, -1.27), (5.08, 1.27)),
    'Transistor_FET:NTMFS016N06CT1G': ((-5.08, -6.35), (-5.08, -3.81)),
    'Device:R_Shunt': ((5.08, -1.27), (5.08, 1.27)),
})
S.label_dx.update({'Connector_Generic:Conn_01x03': 5.08, 'Connector_Generic:Conn_01x02': 5.08})

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
S.text('MODULMAG – a logikai táp a 20 A-es', 15, 24, 1.5)
S.text('főbiztosíték ELŐTT ágazik le (D54)', 15, 28.5, 1.5)
left = [('+24V_IN', '+24V_IN'), ('+24V_P', None), ('V_BUS_P', None), ('HW_ID', 'HW_ID')]
right = [('PA8', 'CH1_PWM'), ('PA9', 'CH2_PWM'), ('PA10', 'CH3_PWM'), ('PC6', 'CH4_PWM'), ('PC7', 'CH5_PWM'),
         ('PC8', 'CH6_PWM'), ('PB12', 'DRV_EN'), ('PA7', 'I_SENSE'), ('PA4', 'DAC_THR'), ('PC2', 'V_RAIL_SENSE'),
         ('PC3', 'NTC'), ('PA0', 'DS1'), ('PA1', 'DS2'), ('PA2', 'DS3'), ('PA3', 'DS4'), ('PA5', 'DS5'), ('PA6', 'DS6'),
         ('PB8', None), ('PB9', None), ('PB11', None), ('PB13', None), ('PB14', None), ('PB15', None)]
S.subsheet('modulmag', '../modulmag/modulmag.kicad_sch', 25, 35, 35, 2.54 * (len(right) + 1), left=left, right=right)

# HW-ID (MODULMAG-SPEC 3.5): LED = 10k / 3,3k → 0,82 V → 2. sáv
S.text('HW-ID: LED-modul = 2. sáv (0,82 V)', 15, 104)
up('+3V3', (20, 108))
shunt('Device:R', 'R201', '10k 1%', (20, 108), None, R0603)
nh = (20, 118.11)
S.wire((20, 115.62), nh)
shunt('Device:R', 'R202', '3k3 1%', (20, 120.65), 'GND', R0603)
S.wire(nh, (20, 120.65))
shunt('Device:C', 'C201', '100n', (30, 120.65), 'GND', C0603)
S.wire(nh, (30, nh[1]), (30, 120.65))
S.wire((30, nh[1]), (36, nh[1]))
S.label('HW_ID', (36, nh[1]), 0)
S.junction(nh)
S.junction((30, nh[1]))

# =================== 1. Betáp és +24V_RAIL ===================
Y = 45
S.text('1. BETÁP (20 A): J201 → F201 20 A → ideális dióda (U204 LM74700-Q1 + Q201) → +24V_RAIL – fordított polaritás ellen, GND-eltolódás nélkül (D65)', 80, 24, 1.5)
S.text('Q201 hiányában a S–D padek vastag dróttal áthidalhatók', 150, 33)
pj = S.comp('Connector_Generic:Conn_01x02', 'J201', '24V IN 20A', 90, 60, {'1': None, '2': None}, fp=TB2,
            props=P('push-in, 2,5 mm², ≥ 20 A – helyőrző; barna = +24 V, kék = GND (D43)'))
p1, p2 = pj['1'][:2], pj['2'][:2]
xa = p1[0] - 7.62
S.wire(p1, (xa, p1[1]), (xa, Y), (xa + 12.7, Y))
S.wire(p2, (p2[0] - 2.54, p2[1]), (p2[0] - 2.54, p2[1] + 2.54))
down('GND', (p2[0] - 2.54, p2[1] + 2.54))
S.wire((xa + 2.54, Y), (xa + 2.54, Y - 5.08))
S.label('+24V_IN', (xa + 2.54, Y - 5.08), 90)
S.junction((xa + 2.54, Y))
S.flag('+24V_IN', xa + 7.62, Y - 10)
S.wire((xa + 7.62, Y - 10), (xa + 7.62, Y))
S.junction((xa + 7.62, Y))
p = series('Device:Fuse', 'F201', '20A', (xa + 12.7, Y), 'Fuse:Fuseholder_Blade_Mini_Keystone_3568',
           props=P('mini lapos autós biztosíték, NYÁK-foglalat'))
# +24V_F → Q201 (S balra, D jobbra, G lefelé) → +24V_RAIL
xs = p[0] + 15.24
S.rail(Y, [p[0], xs - 7.62, xs - 2.54, xs])
pq = S.place('Transistor_FET:NTMFS016N06CT1G', 'Q201', 'NTMFS5C604NL', {'1': None, '2': None, '3': None, '4': None, '5': None},
             '1', (xs, Y), r=90, mirror='y', fp='Package_SO:ONSemi_SO-8FL_488AA',
             props={'Megjegyzés': 'onsemi 60 V, ~1,2 mΩ, SO-8FL; S = bemenet, D = sín; nagy padek (áthidalható)',
                    'Description': 'N-MOSFET 60 V, ~1,2 mΩ (onsemi NTMFS5C604NL)'})
xd = pq['5'][0]
gq = pq['4'][:2]
S.wire((xs - 7.62, Y), (xs - 7.62, Y - 5.08))
S.label('+24V_F', (xs - 7.62, Y - 5.08), 90)
S.flag('+24V_F', xs - 7.62, Y - 15)
S.wire((xs - 7.62, Y - 15), (xs - 7.62, Y - 5.08))
# LM74700 a Q201 alatt: ANODE / GATE / CATHODE felfelé
pl = S.place('Power_Management:LM74700', 'U204', 'LM74700-Q1', {'1': None, '2': 'GND', '3': None, '4': None, '5': None, '6': None},
             '5', (gq[0], gq[1] + 7.62), fp='Package_TO_SOT_SMD:SOT-23-6', props=P('TI ideális dióda-vezérlő; EN az ANODE-ra'))
S.wire(gq, pl['5'][:2])
S.wire(pl['6'][:2], (pl['6'][0], Y))
S.wire(pl['4'][:2], (pl['4'][0], Y))
# VCAP – C202 – +24V_F, EN – +24V_F
vc, en = pl['1'][:2], pl['3'][:2]
S.wire(vc, (vc[0] - 5.08, vc[1]))
shunt('Device:C', 'C202', '100n', (vc[0] - 5.08, vc[1] - 7.62), None, C0603, r=180, top_pin='2', bot_pin='1',
      props=P('VCAP–ANODE, ≥ 0,1 µF, X7R, ≥ 25 V'))
S.wire((vc[0] - 5.08, vc[1] - 7.62), (vc[0] - 5.08, vc[1] - 10.16))
S.label('+24V_F', (vc[0] - 5.08, vc[1] - 10.16), 90)
S.wire(en, (en[0] - 10.16, en[1]))
S.label('+24V_F', (en[0] - 10.16, en[1]), 180)

# +24V_RAIL sín
xr0 = pl['4'][0]
taps = [xr0 + 10 + i * 12.7 for i in range(5)]
xdiv = xr0 + 78.74
xreg = xr0 + 101.6
fuses = [xr0 + 134.62, xr0 + 170.18, xr0 + 205.74]
S.rail(Y, [xd, xr0, xr0 + 5] + taps + [xdiv, xreg] + fuses)
S.wire((xr0 + 5, Y), (xr0 + 5, Y - 7.62))
S.label('+24V_RAIL', (xr0 + 5, Y - 7.62), 90)
S.flag('+24V_RAIL', xr0 + 5, Y - 17)
S.wire((xr0 + 5, Y - 17), (xr0 + 5, Y - 7.62))
shunt('Device:D_Zener', 'D201', 'SMBJ28A', (taps[0], Y + 5.08), 'GND', 'Diode_SMD:D_SMB', r=270, props=P('TVS a sínen'))
tap(Y, taps[0], Y + 5.08)
shunt('Device:C_Polarized', 'C203', '470µ/50V', (taps[1], Y + 5.08), 'GND', 'Capacitor_THT:CP_Radial_D10.0mm_P5.00mm',
      props=P('low-ESR, 105 °C; GND-oldala a sönt ELŐTT'))
tap(Y, taps[1], Y + 5.08)
for i, x in enumerate(taps[2:5]):
    shunt('Device:C', f'C{204 + i}', '10µ/50V', (x, Y + 5.08), 'GND', C1210, props=P('a FET-ek mellett'))
    tap(Y, x, Y + 5.08)
S.text('pufferek: a GND-oldaluk a sönt előtt', taps[0] - 2, Y + 22)
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
                 props=P('Littelfuse 451/453 NANO² (2410), pl. 0451010.MRL – értéke a szalag szerint (≤ 10 A)'))
    tap(Y, x, Y + 5.08)
    b = pf['2'][:2]
    pjb = S.comp('Connector_Generic:Conn_01x03', f'J{201 + k}', f'BLOKK {k}', x + 17.78, b[1] + 10.16, {'1': None, '2': None, '3': None},
                 fp=TB3, props=P(f'1 = +24 V, 2 = CH{2 * k - 1}, 3 = CH{2 * k}; push-in, ≥ 10 A/pólus – helyőrző'))
    S.wire(b, (b[0], pjb['1'][1]), pjb['1'][:2])
    S.label(f'+24V_B{k}', (b[0], pjb['1'][1]), 180)
    for n, ch in (('2', 2 * k - 1), ('3', 2 * k)):
        a = pjb[n][:2]
        S.wire(a, (a[0] - 7.62, a[1]))
        S.label(f'CH{ch}_D', (a[0] - 7.62, a[1]), 180)

# =================== 2. Gate-meghajtók ===================
yg = 108
S.text('2. GATE-MEGHAJTÓK – 3 × UCC27524 (12 V): EN közösen a DRV_EN-en (PB12), 1 k lehúzás → bekapcsoláskor minden csatorna KI', 80, yg - 20, 1.5)
S.text('6 EN-láb belső 200 k felhúzása a 12 V-ra párhuzamosan ~33 k → 1 k-val ~0,35 V (< 0,8 V); az IN-lábakon 120 k belső lehúzás is van', 80, yg - 15.5)
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
    yv = v[1] - 2.54
    S.wire(v, (v[0], yv), (v[0] + 22, yv))
    up('+12V', (v[0], yv))
    for xc, ref, val, fp in ((v[0] + 12, f'C{210 + 2 * d}', '1µ/25V', C0805), (v[0] + 22, f'C{211 + 2 * d}', '100n', C0603)):
        shunt('Device:C', ref, val, (xc, yv + 2.54), 'GND', fp)
        S.wire((xc, yv), (xc, yv + 2.54))
    S.junction((v[0] + 12, yv))

# =================== 3. Csatornák ===================
yB, yN = 150, 172          # +24V_Bk sor, drain-csomópont
S.text('3. CSATORNÁK (× 6): FET NTD5C648NL (DPAK; tartalék IRFR1205) · szabadonfutó B360B a blokk +24 V-jára · RC snubber (DNP) ·'
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
    S.place('Device:D_Schottky', f'D{210 + n}', 'B360B', {'1': None, '2': None}, '1', (xs, yB + 2.54), r=270,
            fp='Diode_SMD:D_SMB', props=P('szabadonfutó, 3 A / 60 V, SMB'))
    S.wire((xs, yB + 10.16), (xs, yN))
    # drain-LED: +24V_Bk → 10k → LED → drain
    S.wire((xl, yB), (xl, yB + 2.54))
    shunt('Device:R', f'R{250 + n}', '10k', (xl, yB + 2.54), None, R0805)
    S.place('Device:LED', f'D{230 + n}', 'zöld', {'2': None, '1': None}, '2', (xl, yB + 12.7), r=90, fp=LED0603,
            props=P(f'CH{n} kimenet (drain) – előlap'))
    S.wire((xl, yB + 10.16), (xl, yB + 12.7))
    S.wire((xl, yB + 20.32), (xl, yN))
    # FET: D felfelé a csomópontra, S lefelé PGND_SH, G balra
    pq = S.place('Transistor_FET:QM6006D', f'Q{201 + n}', 'NTD5C648NL', {'1': None, '2': None, '3': None}, '2', (xs, yN + 5.08),
                 fp='Package_TO_SOT_SMD:TO-252-2',
                 props={'Megjegyzés': 'onsemi 60 V, ~4–5 mΩ, DPAK; tartalék: IRFR1205 (kis áramra)',
                        'Description': 'N-MOSFET 60 V, DPAK (onsemi NTD5C648NL)'})
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
    # gate-LED: CHn_GD → 4k7 → LED → GND
    xg = gd[0] - 2.54
    S.wire(gd, (xg, gd[1]))
    S.wire((xg, gd[1]), (xg, gd[1] - 5.08))
    S.label(f'CH{n}_GD', (xg, gd[1] - 5.08), 90)
    shunt('Device:R', f'R{240 + n}', '4k7', (xg, gd[1] + 2.54), None, R0603)
    S.wire((xg, gd[1]), (xg, gd[1] + 2.54))
    S.junction((xg, gd[1]))
    S.place('Device:LED', f'D{220 + n}', 'zöld', {'2': None, '1': 'GND'}, '2', (xg, gd[1] + 12.7), r=90, fp=LED0603,
            props=P(f'CH{n} gate – előlap, fényvezető'))
    S.wire((xg, gd[1] + 10.16), (xg, gd[1] + 12.7))
    # drain-csomópont jobbra: CHn_D címke, snubber, drain-mérés
    xsn, xr1 = xs + 5.08, xs + 10.16
    S.rail(yN, [xl, xs, xsn, xr1, xr1 + 2.54])
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
       ' BE: ≈ V_RAIL × (1 − kitöltés); mindig ~0 V = átütött FET', 15, 215)

# =================== 4. Össz-áram, NTC, mérőpontok ===================
ys = 240
S.text('4. ÖSSZ-ÁRAM (D47, D53): 1 mΩ sönt a FET-ek közös source-ága (PGND_SH) és a GND között, Kelvin → INA181A2 (×50) → PA7', 15, ys - 13, 1.5)
S.text('(ADC + COMP2 → TIM1/TIM8 break); a küszöb a DAC1-ről (PA4); 20 A → 1,0 V', 15, ys - 8.5)
xsh = 40
S.label('PGND_SH', (xsh, ys - 2.54), 90)
S.flag('PGND_SH', xsh - 10, ys - 2.54)
S.wire((xsh - 10, ys - 2.54), (xsh, ys - 2.54))
psh = S.place('Device:R_Shunt', 'R209', '1m 1%', {'1': None, '2': None, '3': None, '4': None}, '1', (xsh, ys + 2.54),
              fp='Resistor_SMD:R_Shunt_Vishay_WSK2512_6332Metric_T1.19mm',
              props=P('2512, ≥ 1 W (20 A-en 0,4 W), Kelvin – pl. Vishay WSK2512 / WSLP2512'))
S.wire((xsh, ys - 2.54), (xsh, ys + 2.54))
S.wire(psh['4'][:2], (xsh, psh['4'][1] + 2.54))
down('GND', (xsh, psh['4'][1] + 2.54))
pi = S.place('Amplifier_Current:INA181', 'U206', 'INA181A2IDBVR', {'1': None, '2': 'GND', '3': None, '4': None, '5': 'GND', '6': None},
             '3', (psh['2'][0] + 10.16, psh['2'][1]))
S.wire(psh['2'][:2], pi['3'][:2])
S.wire(psh['3'][:2], pi['4'][:2])
v6 = pi['6'][:2]
S.wire(v6, (v6[0], v6[1] - 2.54), (v6[0] + 7.62, v6[1] - 2.54))
up('+3V3', (v6[0], v6[1] - 2.54))
shunt('Device:C', 'C240', '100n', (v6[0] + 7.62, v6[1] - 2.54), 'GND', C0603)
o = pi['1'][:2]
pr3 = series('Device:R', 'R207', '100R', o, R0603)
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
# NTC
xn = 200
S.text('NTC a FET-ek között (PC3) – D30, harmadik védelmi réteg', xn - 10, ys - 8.5)
up('+3V3', (xn, ys - 2.54))
shunt('Device:R', 'R208', '10k 1%', (xn, ys - 2.54), None, R0603)
nn = (xn, ys + 7.62)
S.wire((xn, ys + 5.08), nn)
shunt('Device:Thermistor_NTC', 'TH201', '10k B3435', (xn, ys + 10.16), 'GND', 'Resistor_SMD:R_0603_1608Metric')
S.wire(nn, (xn, ys + 10.16))
shunt('Device:C', 'C242', '100n', (xn + 7.62, ys + 10.16), 'GND', C0603)
S.wire(nn, (xn + 7.62, nn[1]), (xn + 7.62, ys + 10.16))
S.wire((xn + 7.62, nn[1]), (xn + 12.7, nn[1]))
S.label('NTC', (xn + 12.7, nn[1]), 0)
S.junction(nn)
S.junction((xn + 7.62, nn[1]))

S.text('Generálva (hardware/gen/led-modul.py) – D43/D47/D53/D65 alapján; kézi szerkesztés helyett a generátort módosítsd.', 15, 287, 1.3)
S.write(OUT, date='2026-10-16')
print('ok', OUT)
