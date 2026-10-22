"""Általános bemeneti modul – modulmag (táp a buszról, 24 V nincs – D71) + 16 bemenet JST-PH-n + HDC3020 (D44, D48, D51, D66).

Elrendezés: balra a modulmag-blokk és a HW-ID; felül az érzékelő-táp (külön 3,3 V-os LDO, 4 csoport
3,3 / 5 V-os választóval és PTC-vel); középen 4 × 4 bemeneti cella (csatlakozó → soros R → csomópont: felhúzás,
lehúzás-hely, C → címke az MCU felé); lent az ESD-tömbök, jobbra lent a HDC3020 és a külső I²C-csatlakozó.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import kigen
kigen.POWER_UP = {'+3V3', '+5V'}
kigen.POWER_DOWN = {'GND'}

OUT = sys.argv[1]
S = kigen.Sheet('Bemeneti modul – 16 bemenet, 4 tápcsoport, HDC3020', 'bemeneti-modul')
S.use('modularis:HDC3020', lib='modularis', name='HDC3020',
      libpath=os.path.join(os.path.dirname(__file__), '..', 'lib', 'modularis.kicad_sym'))
S.label_pos.update({'Power_Protection:TPD4E05U06DQA': ((-2.54, -11.43), (-10.16, 15.24)),   # ref a két NC-láb között, fölöttük
                    'modularis:HDC3020': ((-7.62, -8.89), (-7.62, 8.89)),
                    'Regulator_Linear:AP2112K-3.3': ((-5.08, -10.16), (-5.08, -7.62)),
                    'Jumper:SolderJumper_3_Bridged12': ((-6.35, -3.81), (-17.78, 0))})   # „CSOPORT k” balra, a PTC felirata ne ütközzön
S.label_dx.update({'Connector_Generic:Conn_01x04': 5.08})
# r=180-as PH: a felirat jobbra igazítva a láb végéig, a csatlakozó fölött
S.label_pos['Connector_Generic:Conn_01x03'] = ((5.08, -8.89), (5.08, -6.35))

R0603 = 'Resistor_SMD:R_0603_1608Metric'
C0603 = 'Capacitor_SMD:C_0603_1608Metric'
PH3 = 'Connector_JST:JST_PH_B3B-PH-K_1x03_P2.00mm_Vertical'
PH4 = 'Connector_JST:JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical'

# bemenet → STM32-láb (MODULMAG-SPEC 7., D54)
PINS = ['PA0', 'PA1', 'PA2', 'PA3', 'PA4', 'PA5', 'PA6', 'PA7', 'PA8', 'PA9', 'PA10', 'PB11',
        'PB12', 'PB13', 'PB14', 'PB15']
FT = {8, 9, 10}  # IN8–IN10: 5 V-tűrő (FT) lábak; a többi TTa (≤ 3,6 V)


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


def stub(p, net, d, length=5.08):
    """rövid vezeték a lábtól d irányba, a végén címke / tápszimbólum"""
    dx, dy = {0: (length, 0), 180: (-length, 0), 90: (0, -length), 270: (0, length)}[d]
    q = (p[0] + dx, p[1] + dy)
    S.wire(p, q)
    S.label(net, q, d)


# =================== Modulmag, betáp, HW-ID ===================
S.text('MODULMAG – táp a buszról (D71)', 15, 24, 1.5)
S.text('24 V nincs a modulon; +5V a buszról', 15, 28.5)
left = [('HW_ID', 'HW_ID'), ('GND_BUS', 'GND_BUS')]
right = [(p, f'IN{i}') for i, p in enumerate(PINS)]
right += [('PB8', 'I2C_SCL'), ('PB9', 'I2C_SDA'), ('PC2', 'HDC_ALERT'), ('PC3', None), ('PB1', None)]
S.subsheet('modulmag', '../modulmag/modulmag.kicad_sch', 25, 35, 35, 2.54 * (len(right) + 1), left=left, right=right)

S.text('HW-ID: bemeneti modul = 3. sáv (0,66 V)', 12, 112)
up('+3V3', (20, 118))
shunt('Device:R', 'R301', '10k 1%', (20, 118), None, R0603)
nh = (20, 128.27)
S.wire((20, 125.62), nh)
shunt('Device:R', 'R302', '2k49 1%', (20, 130.81), 'GND', R0603)
S.wire(nh, (20, 130.81))
shunt('Device:C', 'C301', '100n', (38.1, 130.81), 'GND', C0603)
S.wire(nh, (38.1, nh[1]), (38.1, 130.81))
S.wire((38.1, nh[1]), (43.18, nh[1]))
S.label('HW_ID', (43.18, nh[1]), 0)
S.junction(nh)
S.junction((38.1, nh[1]))


# busz-GND (D74): a GND_BUS (XH 2-es tű) a modul GND-jére 0R-on át – a nagyáramú modul hurokárama ne a buszon folyjon
S.label('GND_BUS', (20, 150), 180)
S.wire((20, 150), (20 + 2.54, 150))
_pg = S.place('Device:R', 'R390', '0R', {'1': None, '2': None}, '1', (20 + 2.54, 150), r=90, fp='Resistor_SMD:R_1206_3216Metric',
              props=P('D74: 0 Ω – a bemeneti modul teljesen a buszról jár, itt ellenállás nem lehet'))
_q = _pg['2'][:2]
S.wire(_q, (_q[0] + 2.54, _q[1]), (_q[0] + 2.54, _q[1] + 2.54))
S.label('GND', (_q[0] + 2.54, _q[1] + 2.54), 270)

# =================== 1. Érzékelő-táp ===================
S.text('1. ÉRZÉKELŐ-TÁP: külön 3,3 V-os sín (U301, AP2112K) a busz 5 V-járól – egy zárlatos érzékelő nem indítja újra az MCU-t;', 80, 22, 1.5)
S.text('4 csoport × 4 csatlakozó: csoportonként 3 padas forrasztható választó (alap 1–2 = 3,3 V; átforrasztva 2–3 = 5 V) + saját PTC (0,2 A)', 80, 26.5)
Y5, Y3 = 34.29, 41.91          # +5V sín, +3V3S sín
xu = 95.25
up('+5V', (85.09, Y5))
pu = S.place('Regulator_Linear:AP2112K-3.3', 'U301', 'AP2112K-3.3TRG1', {'1': None, '3': None, '2': 'GND', '5': None}, '1', (xu, Y3),
             fp='Package_TO_SOT_SMD:SOT-23-5', nc=['4'], props=P('600 mA, kis ejtésű; csak az érzékelőknek – az MCU 3,3 V-ja a modulmag U5-je'))
S.wire(pu['3'][:2], (xu - 2.54, pu['3'][1]), (xu - 2.54, Y3))
S.junction((xu - 2.54, Y3))
S.wire((85.09, Y5), (85.09, Y3))
S.rail(Y3, [85.09, 88.9, xu])
shunt('Device:C', 'C302', '10µ/10V', (88.9, Y3 + 2.54), 'GND', 'Capacitor_SMD:C_0805_2012Metric')
S.wire((88.9, Y3), (88.9, Y3 + 2.54))
x3 = pu['5'][0]
groups = [152.4 + i * 63.5 for i in range(4)]
S.rail(Y3, [x3, x3 + 7.62, x3 + 15.24] + [g - 5.08 for g in groups])
S.rail(Y5, [85.09] + [g + 5.08 for g in groups])
shunt('Device:C', 'C303', '10µ', (x3 + 7.62, Y3 + 2.54), 'GND', 'Capacitor_SMD:C_0805_2012Metric', props=P('X7R, 10 V – kerámia'))
S.wire((x3 + 7.62, Y3), (x3 + 7.62, Y3 + 2.54))
S.wire((x3 + 15.24, Y3), (x3 + 15.24, Y3 - 3.81))
S.label('+3V3S', (x3 + 15.24, Y3 - 3.81), 90)
for k, gx in enumerate(groups, 1):
    yj = Y3 + 10.16
    pjp = S.place('Jumper:SolderJumper_3_Bridged12', f'JP{300 + k}', f'CSOPORT {k}', {'1': None, '2': None, '3': None}, '1',
                  (gx - 5.08, yj), fp='Jumper:SolderJumper-3_P1.3mm_Bridged12_RoundedPad1.0x1.5mm',
                  props=P(f'{k}. csoport tápja: 1–2 = 3,3 V (alap), 2–3 = 5 V'))
    S.wire((gx - 5.08, Y3), (gx - 5.08, yj))
    S.wire((gx + 5.08, Y5), pjp['3'][:2])
    c = pjp['2'][:2]
    S.wire(c, (c[0], c[1] + 1.27))
    S.place('Device:Polyfuse', f'F{300 + k}', 'PTC 0,2A', {'1': None, '2': None}, '1', (c[0], c[1] + 1.27),
            fp='Fuse:Fuse_1206_3216Metric', props=P('tartóáram ≈ 0,2 A, ≥ 6 V (pl. Bourns MF-NSMF020)'))
    ns = (c[0], c[1] + 11.43)
    S.wire((c[0], c[1] + 8.89), ns)
    S.rail(ns[1], [ns[0], ns[0] + 7.62, ns[0] + 12.7])
    shunt('Device:C', f'C{303 + k}', '1µ', (ns[0] + 7.62, ns[1] + 2.54), 'GND', C0603)
    S.wire((ns[0] + 7.62, ns[1]), (ns[0] + 7.62, ns[1] + 2.54))
    S.label(f'SUP{k}', (ns[0] + 12.7, ns[1]), 0)
    S.text(f'IN{4 * k - 4}–IN{4 * k - 1}', gx - 5, ns[1] + 10)
S.text('5 V-os csoportban az érzékelő jele is 5 V lehet: az IN8–IN10 (PA8–PA10) 5 V-tűrő, a többi bemeneten az osztó-hely kell (R_s 2k2, R_le 3k9, R_fel ki)', 80, 84)

# =================== 2. Bemenetek ===================
S.text('2. BEMENETEK (× 16): PH 1 = táp (SUPk), 2 = GND, 3 = JEL → R_fel a 3,3 V-ra (csatlakozó-oldal) → R_s → csomópont (R_le (DNP), C) → MCU; ESD az MCU-oldalon', 80, 93, 1.5)
S.text('Alap: R_fel 10k + R_s 10k + C 10n (D75) – félrekötött 24 V-nál ~2 mA az ESD-tömbbe, a láb ~VBR-en (D81!). 12/24 V-os jel: R_fel ki, R_s 68k, R_le 10k; 5 V: R_s 2k2, R_le 3k9.', 80, 97.5)
for n in range(16):
    k = n // 4 + 1
    col, row = n % 4, n // 4
    x0 = 80 + col * 63.5
    yJ = 114.3 + row * 29.21          # a JEL sora
    pj = S.place('Connector_Generic:Conn_01x03', f'J{301 + n}', f'IN{n}', {'1': None, '2': None, '3': None}, '3', (x0 + 7.62, yJ),
                 r=180, fp=PH3, props=P(f'{k}. tápcsoport' + (' – 5 V-tűrő láb' if n in FT else '')))
    # GND: jobbra a SUP-vezeték mögé, majd lefelé (szabályos GND-szimbólum)
    g2 = pj['2'][:2]
    S.wire(g2, (g2[0] + 7.62, g2[1]), (g2[0] + 7.62, g2[1] + 7.62))
    down('GND', (g2[0] + 7.62, g2[1] + 7.62))
    s1 = pj['1'][:2]
    S.wire(s1, (s1[0] + 2.54, s1[1]), (s1[0] + 2.54, s1[1] + 2.54))
    S.label(f'SUP{k}', (s1[0] + 2.54, s1[1] + 2.54), 270)
    # JEL → csomópont A (R_fel a 3,3 V-ra) → R_s 10k → csomópont B (R_le DNP, C) → IN címke (D75)
    xa = x0 + 12.7
    S.wire((x0 + 7.62, yJ), (xa, yJ), (xa + 5.08, yJ))
    S.place('Device:R', f'R{330 + n}', '10k', {'1': '+3V3', '2': None}, '2', (xa, yJ), fp=R0603,
            props=P('felhúzás a csatlakozó oldalán (D75); 12/24 V-os jelnél kivenni'))
    S.junction((xa, yJ))
    S.ref_pos[f'R{310 + n}'] = ((6.35, -5.08), (6.35, -2.54))   # r=90: jobbra, a felhúzás felirata mellett
    p = series('Device:R', f'R{310 + n}', '10k', (xa + 5.08, yJ), R0603,
               props=P('soros: 24 V-os félrekötésnél ~2 mA az ESD-tömbbe (U303–U306), a láb a letörési feszültségén – D75, D81; 12/24 V-os osztóhoz 68k'))
    xd, xc, xo = p[0] + 7.62, p[0] + 17.78, p[0] + 27.94
    S.rail(yJ, [p[0], xd, xc, xo])
    shunt('Device:R', f'R{350 + n}', 'DNP', (xd, yJ + 2.54), 'GND', R0603, dnp=True, props=P('osztó 5/12/24 V-os jelhez'))
    S.wire((xd, yJ), (xd, yJ + 2.54))
    shunt('Device:C', f'C{310 + n}', '10n', (xc, yJ + 2.54), 'GND', C0603)
    S.wire((xc, yJ), (xc, yJ + 2.54))
    S.label(f'IN{n}', (xo, yJ), 0)

# ESD: 4 × TPD4E05U06 (4 csatorna / IC), az MCU-oldalon
ye = 248.92
S.text('ESD: 4 × TPD4E05U06 – a csatlakozók mellé, a soros R MCU-oldalára (a soros R korlátozza a magasabb feszültség áramát)', 80, ye - 18, 1.3)
for gi in range(4):
    a = 4 * gi
    x = 101.6 + gi * 48.26
    pe = S.comp('Power_Protection:TPD4E05U06DQA', f'U{303 + gi}', 'TPD4E05U06DQAR', x, ye,
                {'1': None, '2': None, '4': None, '5': None, '3': None, '8': None}, nc=['6', '7', '9', '10'])
    stub(pe['1'][:2], f'IN{a}', 180)
    stub(pe['2'][:2], f'IN{a + 1}', 180)
    stub(pe['4'][:2], f'IN{a + 2}', 0)
    stub(pe['5'][:2], f'IN{a + 3}', 0)
    stub(pe['3'][:2], 'GND', 270, 2.54)

# =================== 3. HDC3020 + külső I²C ===================
S.text('3. HŐMÉRSÉKLET / PÁRATARTALOM:', 330, 102, 1.3)
S.text('HDC3020 a NYÁK szélén (marással) + 4 tűs PH', 330, 106)
S.text('külső érzékelőhöz (D66). Cím 0x44 (ADDR = ADDR1', 330, 109.5)
S.text('= GND); a külső más címen. Az EP lebegve.', 330, 113)
hx, hy = 350.52, 137.16
ph = S.comp('modularis:HDC3020', 'U302', 'HDC3020DEFR', hx, hy, {'5': None, '6': None, '2': None, '7': None, '1': None, '4': None,
            '3': None, '8': None}, nc=['9'],
            props=P('a ház belsejének klímáját méri (elosztószekrény), nem a szobáét – szobához a külső I²C-érzékelő (D77); cím 0x44, a külső ne legyen 0x44'))
# táp: VDD (5) + RESET (6) → +3V3, ADDR (2) + ADDR1 (7) → GND
v5, r6 = ph['5'][:2], ph['6'][:2]
xv = v5[0] - 5.08
S.wire(v5, (xv, v5[1]))
S.wire(r6, (xv, r6[1]))
S.wire((xv, r6[1]), (xv, v5[1]), (xv, v5[1] - 5.08))
up('+3V3', (xv, v5[1] - 5.08))
S.junction((xv, v5[1]))
S.rail(v5[1] - 2.54, [xv, xv - 15.24])
S.junction((xv, v5[1] - 2.54))
shunt('Device:C', 'C330', '100n', (xv - 15.24, v5[1] - 2.54), 'GND', C0603)
a2_, a7 = ph['2'][:2], ph['7'][:2]
xg = xv + 2.54
S.wire(a2_, (xg, a2_[1]))
S.wire(a7, (xg, a7[1]))
S.wire((xg, a2_[1]), (xg, a7[1]), (xg, a7[1] + 2.54))
S.junction((xg, a7[1]))
down('GND', (xg, a7[1] + 2.54))
g8 = ph['8'][:2]
S.wire(g8, (g8[0] + 2.54, g8[1]), (g8[0] + 2.54, g8[1] + 2.54))
down('GND', (g8[0] + 2.54, g8[1] + 2.54))
# SDA (1), SCL (4), ALERT (3) → felhúzások (felül, közös magasságban) és címkék
ytop = ph['1'][1] - 12.7
for i, (pin, net, rref, rval) in enumerate((('1', 'I2C_SDA', 'R372', '4k7'), ('4', 'I2C_SCL', 'R371', '4k7'),
                                             ('3', 'HDC_ALERT', 'R373', '10k'))):
    q = ph[pin][:2]
    x = q[0] + 3.81 + i * 8.89
    xe = q[0] + 26.67
    S.rail(q[1], [q[0], x, xe])
    S.place('Device:R', rref, rval, {'1': '+3V3', '2': None}, '1', (x, ytop), fp=R0603)
    S.wire((x, ytop + 7.62), (x, q[1]))
    S.label(net, (xe, q[1]), 0)
# külső I²C: 100R soros + ESD (U307) + PTC (F305) + J320 – címkékkel
xi = 345.44
S.text('KÜLSŐ I²C (J320)', xi, 161)
for i, (a, b, ref) in enumerate((('I2C_SCL', 'SCL_EXT', 'R374'), ('I2C_SDA', 'SDA_EXT', 'R375'))):
    y = 167.64 + i * 10.16
    S.label(a, (xi, y), 180)
    S.wire((xi, y), (xi + 2.54, y))
    p = series('Device:R', ref, '100R', (xi + 2.54, y), R0603)
    stub(p, b, 0, 7.62)
pjx = S.comp('Connector_Generic:Conn_01x04', 'J320', 'I2C KÜLSŐ', 386.08, 190.5, {'1': None, '2': None, '3': None, '4': None},
             fp=PH4, props=P('külső HDC3020 / I²C-érzékelő, kábel ≤ 2 m, 100 kHz'))
stub(pjx['1'][:2], 'SUP_I2C', 180, 7.62)
g2 = pjx['2'][:2]   # GND: a címkék szövege mögött balra, majd lefelé a 4. láb alá
S.wire(g2, (g2[0] - 20.32, g2[1]), (g2[0] - 20.32, pjx['4'][1] + 5.08))
down('GND', (g2[0] - 20.32, pjx['4'][1] + 5.08))
stub(pjx['3'][:2], 'SDA_EXT', 180, 7.62)
stub(pjx['4'][:2], 'SCL_EXT', 180, 7.62)
pe = S.comp('Power_Protection:TPD4E05U06DQA', 'U307', 'TPD4E05U06DQAR', 378.46, 213.36, {'1': None, '2': None, '3': None, '8': None},
            nc=['4', '5', '6', '7', '9', '10'])
stub(pe['1'][:2], 'SCL_EXT', 180)
stub(pe['2'][:2], 'SDA_EXT', 180)
stub(pe['3'][:2], 'GND', 270, 2.54)
S.label('+3V3S', (345.44, 236.22), 180)
S.wire((345.44, 236.22), (347.98, 236.22))
p = series('Device:Polyfuse', 'F305', 'PTC 0,2A', (347.98, 236.22), 'Fuse:Fuse_1206_3216Metric')
stub(p, 'SUP_I2C', 0, 5.08)

S.text('Generálva (hardware/gen/bemeneti-modul.py) – D44/D48/D51/D66 alapján; kézi szerkesztés helyett a generátort módosítsd.', 15, 281, 1.3)
S.write(OUT, date='2026-10-22')
print('ok', OUT)
