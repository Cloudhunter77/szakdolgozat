"""Beszerzési lista egy készlethez (vezérlő + LED- + relé- + bemeneti modul): bom/*.csv → bom/beszerzes.csv

D85: soronként a legolcsóbb forrás (a házak később, programozó kézben) – Hestore (nettó ár + 27 % ÁFA; 25 000 Ft bruttó alatt + szállítás) vagy LCSC (a JLC-s
NYÁK-rendeléshez csapva, közös szállítással; USD × árfolyam + 27 % ÁFA). A Hestore-árat és -készletet a termékoldalról,
az LCSC-t a JLC alkatrészkeresőjéből kéri le (gen/lcsc.py; gyorsítótár: out/hestore/, out/lcsc/). Ha a BOM-ban olyan tétel
van, amihez a FORRAS táblában nincs sor (és nem ellenállás / kondenzátor), „HIBA” – így új alkatrész nem maradhat ki.

Használat (a hardware/ mappából):
    python3 gen/beszerzes.py             # a gyorsítótárból (ami nincs benne, azt letölti)
    python3 gen/beszerzes.py --frissit   # minden árat újra lekér (rendelés előtt: ár, készlet)
"""
import csv, html, math, os, re, sys, time, urllib.request
G = os.path.dirname(os.path.abspath(__file__))
H = os.path.dirname(G)
sys.path.insert(0, G)
import lcsc

LAPOK = ['vezerlo', 'led-modul', 'rele-modul', 'bemeneti-modul']
CACHE = os.path.join(H, 'out', 'hestore')
AFA = 1.27
USD_HUF = 360            # becslés – rendelés előtt a JLC/LCSC pénztárában ellenőrizni
HESTORE_INGYENES = 25000  # Ft bruttó felett ingyenes a GLS CsomagPont
HESTORE_SZALLITAS = 1257  # Ft bruttó alatta

# (érték, footprint) → forrás.  Érték None = a footprint minden értékére (csatlakozók, ahol az érték a funkció neve).
# h = Hestore termékazonosító (prod_<h>.html); l = LCSC-keresés: {'q': kulcsszó, 'tok': tok-részlet, 'tipus': típus-részlet}
# vagy {'R': (érték, tok)} / {'C': (érték, tok, min. V, dielektrikumok)} – ellenállásnál és kondenzátornál a BOM-ból magától;
# ti = a TI-rendelésből jön (az LCSC-ár csak tájékoztató), k = kézben; vesz = darabszám; n = megjegyzés; g = csoportnév.
TUSKE = {'q': 'PZ254V-11-40P', 'tipus': 'PZ254V-11-40P'}
FORRAS = {
    # --- kondenzátorok (a többi 0603/0805/1206/1210-es ellenállás és kondenzátor magától: LCSC + a lenti Hestore-kód)
    ('47µ/50V', 'CP_Elec_6.3x7.7'): dict(l={'q': '47uF 50V SMD electrolytic', 'tok': 'd6.3xl7.7'}),
    ('470µ/50V', 'CP_Radial_D10.0mm_P5.00mm'): dict(h='10028502', l={'q': '470uF 50V electrolytic', 'tok': 'd10xl'},
                                                    n='Ø10 × 20 mm – a magasságot a ház fedeléhez ellenőrizni'),
    ('100n', 'C_0603_1608Metric'): dict(h='10024356'),
    ('10n', 'C_0603_1608Metric'): dict(h='10027791'),
    ('1n', 'C_0603_1608Metric'): dict(h='10027792'),
    ('1µ', 'C_0603_1608Metric'): dict(h='10036059', g='1u0603'),
    ('1µ/16V', 'C_0603_1608Metric'): dict(h='10036059', g='1u0603'),
    ('22p', 'C_0603_1608Metric'): dict(h='10027787'),
    ('22n', 'C_0603_1608Metric'): dict(h='10027796'),
    ('4µ7', 'C_0603_1608Metric'): dict(h='10037167', l={'C': ('4µ7', '0603', 6.3, ('X5R', 'X7R'))}),
    ('6,8n', 'C_0603_1608Metric'): dict(h='10049421'),
    ('10µ', 'C_0805_2012Metric'): dict(h='10034452', g='10u0805'),
    ('10µ/10V', 'C_0805_2012Metric'): dict(h='10034452', g='10u0805'),
    ('10µ/16V', 'C_0805_2012Metric'): dict(h='10034452', g='10u0805'),
    ('1µ/25V', 'C_0805_2012Metric'): dict(h='10027753'),
    ('1µ/50V', 'C_0805_2012Metric'): dict(h='10033068'),
    ('22µ', 'C_0805_2012Metric'): dict(h='10049425', l={'C': ('22µ', '0805', 6.3, ('X5R', 'X7R'))}),
    ('4µ7', 'C_0805_2012Metric'): dict(h='10042711'),
    ('22µ', 'C_1206_3216Metric'): dict(g='22u1206', l={'C': ('22µ', '1206', 10, ('X5R', 'X7R'))}),
    ('22µ/10V', 'C_1206_3216Metric'): dict(g='22u1206', l={'C': ('22µ', '1206', 10, ('X5R', 'X7R'))}),
    ('10µ/50V', 'C_1210_3225Metric'): dict(h='10038374'),
    # --- kvarcok
    ('25MHz ±30ppm', 'Crystal_SMD_3225-4Pin_3.2x2.5mm'): dict(l={'q': 'SX3B25.000F1010F30', 'tipus': 'SX3B25'},
                                                              n='CL = 10 pF, ESR ≤ 30 Ω (W5500) → C40/C41 = 12 pF'),
    ('8MHz', 'Crystal_SMD_3225-4Pin_3.2x2.5mm'): dict(h='10043000', l={'q': '3TJ480000JWLAC', 'tipus': '3TJ480000JWLAC'},
                                                      n='CL = 10 pF, ESR ≤ 120 Ω (STM32L4 HSE: gm-tartalék ~7) → a rajz szerinti 12 pF'),
    # --- diódák
    ('SS16', 'D_SMA'): dict(h='10038974', l={'q': 'SS16 DO-214AC', 'tok': 'DO-214AC', 'tipus': 'SS16'}),
    ('SS56B', 'D_SMB'): dict(l={'q': 'SS56B', 'tok': 'SMB', 'tipus': 'SS56B'}),
    ('SMBJ28A', 'D_SMB'): dict(l={'q': 'SMBJ28A', 'tok': 'SMB', 'tipus': 'SMBJ28A'}),
    ('SMBJ6.0A', 'D_SMB'): dict(l={'q': 'SMBJ6.0A', 'tok': 'SMB', 'tipus': 'SMBJ6.0A'}),
    ('SS56C', 'D_SMC'): dict(h='10043211', l={'q': 'SS56C', 'tok': 'SMC', 'tipus': 'SS56C'}),
    ('BZT52C15', 'D_SOD-123'): dict(h='10039913', l={'q': 'BZT52C15', 'tok': 'SOD-123', 'tipus': 'BZT52C15'}),
    ('SMF5.0A', 'D_SOD-123F'): dict(h='10048902', l={'q': 'SMF5.0A', 'tok': 'SOD-123F', 'tipus': 'SMF5.0A'}),
    ('BAT54HT1G', 'D_SOD-323'): dict(h='10034567', l={'q': 'BAT54WS', 'tok': 'SOD-323', 'tipus': 'BAT54'}),
    # --- IC-k
    ('ESP32-C6-WROOM-1-N8', 'ESP32-C6-WROOM-1'): dict(h='10049443', l={'q': 'ESP32-C6-WROOM-1-N8', 'tipus': 'ESP32-C6-WROOM-1-N8'},
                                                      vesz=1, n='8 MB flash – a firmware 4 MB-ra van beállítva'),
    ('W5500', 'LQFP-48_7x7mm_P0.5mm'): dict(h='10035622', l={'q': 'W5500', 'tok': 'LQFP', 'tipus': 'W5500'}, vesz=1),
    ('AP2112K-3.3TRG1', 'SOT-23-5'): dict(h='10047483', l={'q': 'AP2112K-3.3TRG1', 'tipus': 'AP2112K-3.3'}),
    ('USBLC6-2SC6', 'SOT-23-6'): dict(h='10034399', l={'q': 'USBLC6-2SC6', 'tok': 'SOT-23-6', 'tipus': 'USBLC6-2SC6'}),
    ('LM66200DRLR', 'SOT-583-8'): dict(h='10051566', l={'q': 'LM66200DRLR', 'tipus': 'LM66200'}),
    ('LMR33630ADDA', 'Texas_HSOP-8-1EP_3.9x4.9mm_P1.27mm_ThermalVias'): dict(l={'q': 'LMR33630ADDAR', 'tipus': 'LMR33630ADDA'}),
    ('TPS259531DSGR', 'Texas_DSG0008A_WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm_ThermalVias'): dict(l={'q': 'TPS259531DSGR', 'tipus': 'TPS259531'}),
    ('MC78L12ACDR2G', 'SOIC-8_3.9x4.9mm_P1.27mm'): dict(l={'q': 'MC78L12ACDR2G', 'tok': 'SO', 'tipus': '78L12'}),
    ('NCE6080K', 'TO-252-2'): dict(l={'q': 'NCE6080K', 'tok': 'TO-252', 'tipus': 'NCE6080K'}, vesz=7, n='D85 – az NTD5C648NL megszűnt'),
    ('NCEP6090AGU', 'ONSemi_SO-8FL_488AA'): dict(l={'q': 'NCEP6090AGU', 'tok': 'DFN', 'tipus': 'NCEP6090AGU'}, vesz=2,
                                                n='D85 – az NTMFS5C604NL nem kapható; power-SO8 (5 × 6), az SO-8FL padképére'),
    ('TCAN1044AVDRQ1', 'SOIC-8_3.9x4.9mm_P1.27mm'): dict(ti=1, l={'q': 'TCAN1044AVDRQ1', 'tipus': 'TCAN1044'}),
    ('LMR36015BRNXR', 'TI_VQFN-HR-12_RNX0012B'): dict(ti=1, l={'q': 'LMR36015BRNXR', 'tipus': 'LMR36015B'}),
    ('UCC27524DR', 'SOIC-8_3.9x4.9mm_P1.27mm'): dict(ti=1, l={'q': 'UCC27524DR', 'tipus': 'UCC27524'}),
    ('INA181A2IDBVR', 'SOT-23-6'): dict(ti=1, l={'q': 'INA181A2IDBVR', 'tipus': 'INA181A2'}),
    ('ESD2CAN24-Q1', 'SOT-23'): dict(ti=1, l={'q': 'ESD2CAN24QDBZRQ1', 'tipus': 'ESD2CAN24'}),
    ('TPD4E05U06DQAR', 'USON-10_2.5x1.0mm_P0.5mm'): dict(ti=1, l={'q': 'TPD4E05U06DQAR', 'tipus': 'TPD4E05U06'}),
    ('ULN2803ADWR', 'SOIC-18W_7.5x11.6mm_P1.27mm'): dict(ti=1, l={'q': 'ULN2803ADWR', 'tipus': 'ULN2803'}),
    ('HDC3020DEFR', 'TI_WSON-8-1EP_2.5x2.5mm_DEF0008A'): dict(ti=1, l={'q': 'HDC3020DEFR', 'tipus': 'HDC3020'}),
    ('STM32L433RCT3', 'LQFP-64_10x10mm_P0.5mm'): dict(k=1),
    ('SN65HVD230D', 'SOIC-8_3.9x4.9mm_P1.27mm'): dict(k=1),
    ('MCP9701AT-E/TT', 'SOT-23'): dict(k=1),
    ('74HCT14D', 'SOIC-14_3.9x8.7mm_P1.27mm'): dict(k=1),
    ('IRFR1205', 'TO-252-2'): dict(k=1),
    ('IRFR120N', 'TO-252-2'): dict(k=1),
    ('RTD14024', 'Relay_SPDT_Schrack-RT1-16A-FormC_RM5mm'): dict(k=1),
    # --- tekercsek, ferritek
    ('6,8µH', 'L_FerroCore_HPI0630'): dict(h='10042809', l={'q': 'SLO0630H6R8MTT', 'tipus': '0630'}),
    ('8,2µH', 'L_FerroCore_HPI0630'): dict(h='10042810', l={'q': 'APS0630M8R2A', 'tipus': '0630'}),
    ('BLM18EG221', 'L_0603_1608Metric'): dict(h='10044935', l={'q': 'BLM18EG221TN1D', 'tipus': 'BLM18EG221'}),
    # --- biztosítékok
    ('0,5A', 'Fuse_1206_3216Metric'): dict(l={'q': '0466.500NRHF', 'tipus': '0466.500'}),
    ('2A', 'Fuse_1206_3216Metric'): dict(l={'q': '0466002.NRHF', 'tipus': '0466002'}),
    ('PTC 0,2A', 'Fuse_1206_3216Metric'): dict(h='10039742', l={'q': '1206 resettable fuse 200mA', 'tok': '1206'}),
    ('10A', 'Fuse_Littelfuse-NANO2-451_453'): dict(l={'q': '0451010.MRL', 'tipus': '0451010'},
                                                  n='D76: a szalaghoz kisebb is (0451004.MRL, 4 A)'),
    ('15A', 'Fuse_Littelfuse-NANO2-451_453'): dict(l={'q': '0451015.MRL', 'tipus': '0451015'}, n='D85: F201 – beforrasztott NANO²'),
    # --- csatlakozók
    (None, 'JST_PH_B3B-PH-K_1x03_P2.00mm_Vertical'): dict(h='10049114', l={'q': 'B3B-PH-K-S', 'tipus': 'B3B-PH-K-S'}),
    (None, 'JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical'): dict(l={'q': 'B4B-PH-K-S', 'tipus': 'B4B-PH-K-S'}, vesz=2),
    (None, 'JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical'): dict(h='10041551', l={'q': 'B4B-XH-A', 'tipus': 'B4B-XH-A'}),
    (None, 'PinHeader_1x02_P2.54mm_Vertical'): dict(l=TUSKE, g='tuske', vesz=2, n='40 pólusú, tördelhető (35 tű kell)'),
    (None, 'PinHeader_1x06_P2.54mm_Vertical'): dict(l=TUSKE, g='tuske', vesz=2),
    (None, 'PinHeader_1x07_P2.54mm_Vertical'): dict(l=TUSKE, g='tuske', vesz=2),
    ('HR911105A', 'RJ45_Hanrun_HR911105A_Horizontal'): dict(h='10043564', l={'q': 'HR911105A', 'tipus': 'HR911105A'}, vesz=1,
                                                            n='opcionális (D45)'),
    ('USB-C 16P', 'USB_C_Receptacle_HRO_TYPE-C-31-M-12'): dict(h='10050233', l={'q': 'TYPE-C-31-M-12', 'tipus': 'TYPE-C-31-M-12'}),
    (None, 'SW_SPST_TL3342'): dict(h='10040903', l={'q': 'TS-1187A-B-A-B', 'tipus': 'TS-1187A'},
                                   n='5,1 × 5,1-es, 4 lábú (TS4415/PTS525-típus): lábköz 3,7 mm, a TL3342-footprinten jó'),
    (None, 'TerminalBlock_Phoenix_MKDS-1,5-2_1x02_P5.00mm_Horizontal'): dict(h='10043373', l={'q': 'DG128-5.0-02P', 'tipus': 'DG128-5.0-02P'},
                                                                             n='Degson DG128, 15 A UL / 18 A IEC (J1, J100, J201 – D85)'),
    (None, 'TerminalBlock_Phoenix_MKDS-3-2-5.08_1x02_P5.08mm_Horizontal'): dict(k=1, g='rele-sorkapocs',   # J101–J104
                                                                                n='D83: 5,08 mm-es THT a készletből – a csomagot megnézni (≥ 16 A / 250 V)'),
    (None, 'TerminalBlock_Phoenix_MKDS-1,5-3_1x03_P5.00mm_Horizontal'): dict(h='10052228', l={'q': 'KF128-5.0-3P', 'tipus': 'KF128-5.0-3P'},
                                                                             n='KF128-5.0-3P, 10 A (Hestore) / 24 A (LCSC-adat)'),
    # --- LED-ek
    ('piros', 'LED_0603_1608Metric'): dict(h='10036670', l={'q': '0603 red LED', 'tok': '0603'}),
    ('zöld', 'LED_0603_1608Metric'): dict(k=1),
    ('WS2812B-V5', 'LED_WS2812B_PLCC4_5.0x5.0mm_P3.2mm'): dict(h='10048841', l={'q': 'WS2812B-V5', 'tipus': 'WS2812B-V5'}),
    # --- ellenállások: az LCSC-keresés magától; Hestore-kód, ahol van
    ('0R', 'R_0603_1608Metric'): dict(h='10043634'),
    ('100R', 'R_0603_1608Metric'): dict(h='10051417'),
    ('100k', 'R_0603_1608Metric'): dict(h='10043366', g='100k'),
    ('100k 1%', 'R_0603_1608Metric'): dict(h='10043366', g='100k'),
    ('10R', 'R_0603_1608Metric'): dict(h='10049431', g='10R'),
    ('10R 1%', 'R_0603_1608Metric'): dict(h='10049431', g='10R'),
    ('10k', 'R_0603_1608Metric'): dict(h='10023910', g='10k'),
    ('10k 1%', 'R_0603_1608Metric'): dict(h='10023910', g='10k'),
    ('12,4k 1%', 'R_0603_1608Metric'): dict(h='10049435'),
    ('150k', 'R_0603_1608Metric'): dict(h='10049438'),
    ('1k', 'R_0603_1608Metric'): dict(h='10049434'),
    ('2,2k', 'R_0603_1608Metric'): dict(h='10036842', g='2k2'),
    ('2k2', 'R_0603_1608Metric'): dict(h='10036842', g='2k2'),
    ('200R', 'R_0603_1608Metric'): dict(h='10051418'),
    ('22R', 'R_0603_1608Metric'): dict(h='10023927'),
    ('22k', 'R_0603_1608Metric'): dict(h='10023890'),
    ('330R', 'R_0603_1608Metric'): dict(h='10023883'),
    ('33R', 'R_0603_1608Metric'): dict(h='10023898'),
    ('470k', 'R_0603_1608Metric'): dict(h='10023941'),
    ('47k', 'R_0603_1608Metric'): dict(h='10023901'),
    ('49R9', 'R_0603_1608Metric'): dict(h='10044461'),
    ('4k7', 'R_0603_1608Metric'): dict(h='10031570'),
    ('5,1k', 'R_0603_1608Metric'): dict(h='10036539'),
    ('56k', 'R_0603_1608Metric'): dict(h='10023937'),
    ('10k', 'R_0805_2012Metric'): dict(h='10040338'),
    ('120R', 'R_0805_2012Metric'): dict(h='10027757'),
    ('0R', 'R_1206_3216Metric'): dict(h='10001321'),
    ('1R', 'R_1206_3216Metric'): dict(h='10035914'),
    ('0R', 'R_2512_6332Metric'): dict(h='10037977'),
    ('1m 1%', 'R_Shunt_Vishay_WSK2512_6332Metric_T1.19mm'): dict(h='10037011', l={'R': ('1m', '2512')}, vesz=2,
                                                                 n='2 kivezetésű 2512 – a Kelvin-footprint két-két padját összeforrasztja'),
}

# BOM-on kívüli tételek: (forrás-dict, darab, mire); kesobb = most nem vesszük (D85: a házak később), az összegbe nem számít.
# Programozó (ST-Link) és fejlesztőpanel (Nucleo) kézben van (D85).
EXTRA = [
    (dict(h='10039981', vesz=3, kesobb=1), 3, 'DIN-ház, 4 M: vezérlő, LED-, relémodul – D73'),
    (dict(h='10039989', vesz=1, kesobb=1), 1, 'DIN-ház, 6 M: bemeneti modul – D73'),
    (dict(l={'q': '2.54mm jumper cap'}, vesz=5), 4, 'jumper a LEZÁRÁS tüskesorokra (JP1)'),
    (dict(h='10041545', l={'q': 'XHP-4', 'tipus': 'XHP-4'}, vesz=8, opc=1), 8, 'kábeloldal: XH-ház a buszkábelekhez (4 kábel × 2 vég)'),
    (dict(h='10035076', l={'q': 'SXH-001T-P0.6', 'tipus': 'SXH-001T'}, vesz=40, opc=1), 32, 'kábeloldal: XH-érintkező'),
    (dict(h='10040623', l={'q': 'PHR-3', 'tipus': 'PHR-3'}, vesz=10, opc=1), 10, 'kábeloldal: PH-ház, 3 pólusú (érzékelőkábelek)'),
    (dict(h='10046585', l={'q': 'PHR-4', 'tipus': 'PHR-4'}, vesz=2, opc=1), 1, 'kábeloldal: PH-ház, 4 pólusú (külső I²C)'),
    (dict(h='10038522', l={'q': 'SPH-002T-P0.5S', 'tipus': 'SPH-002T'}, vesz=40, opc=1), 34, 'kábeloldal: PH-érintkező'),
]


def txt(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()


def oldal(cid, frissit):
    f = os.path.join(CACHE, f'{cid}.html')
    if frissit or not os.path.exists(f):
        time.sleep(1.0)
        req = urllib.request.Request(f'https://www.hestore.hu/prod_{cid}.html', headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as r, open(f, 'wb') as o:
            o.write(r.read())
    return open(f, encoding='utf-8', errors='replace').read()


def hestore(cid, frissit):
    t = oldal(cid, frissit)
    nev = txt(re.search(r'<h1>(.*?)</h1>', t, re.S).group(1))
    leiras = txt((re.search(r'itemprop="description">(.*?)</span>', t, re.S) or re.search('()', '')).group(1))
    kod = re.search(r'itemprop="sku">([\d.]+)<', t).group(1)
    arak = [(int(q), float(p)) for q, p in re.findall(
        r'<th[^>]*>(\d+)\+</th>\s*<td[^>]*itemprop="offers"[^>]*>.*?<meta itemprop="price" content="([\d.]+)"', t, re.S)]
    i = t.find('Elérhetőség</th>')
    keszlet = '; '.join(f'{txt(a)} {txt(b)}' for a, b in re.findall(
        r'<td>([^<]+)</td>\s*<td align="right"[^>]*>([^<]+)</td>', t[i:i + 1500])) if i >= 0 else '?'
    return dict(kod=kod, nev=f'{nev} – {leiras}', arak=arak, keszlet=keszlet or 'nincs adat')


def egysegar(arak, db):
    p = [a for q, a in arak if q <= db]
    return p[-1] if p else (arak[0][1] if arak else 0.0)


def rc_spec(ert, fp):
    """Ellenállás / kondenzátor LCSC-keresése a BOM-értékből (pl. '10µ/50V', 'C_1210_3225Metric')."""
    tok = fp.split('_')[1]
    if fp.startswith('R_'):
        return {'R': (ert, tok)}
    v = lcsc.ertek(ert)
    m = re.search(r'/([\d.,]+)(k?)V', ert)
    umin = float(m.group(1).replace(',', '.')) * (1000 if m.group(2) else 1) if m else (50 if v <= 1e-7 else 16)
    diel = ('C0G', 'NP0') if v < 1e-9 else ('X7R', 'C0G', 'NP0') if v <= 1e-7 else ('X7R', 'X5R')
    return {'C': (ert, tok, umin, diel)}


def main():
    frissit = '--frissit' in sys.argv
    os.makedirs(CACHE, exist_ok=True)
    bom = {}
    for lap in LAPOK:
        for r in csv.DictReader(open(os.path.join(H, 'bom', f'{lap}.csv'), encoding='utf-8')):
            fp = r['Footprint'].split(':')[-1]
            if fp.startswith(('TestPoint', 'SolderJumper')):
                continue
            k = (r['Érték'], fp)
            b = bom.setdefault(k, {'db': 0, 'hol': []})
            b['db'] += int(r['Db'])
            b['hol'].append(f"{lap} {r['Jelölés']}")
    hibak = []
    sorok = {}          # csoportkulcs → összesített sor
    for (ert, fp), b in bom.items():
        f = FORRAS.get((ert, fp)) or FORRAS.get((None, fp))
        if f is None and fp.startswith(('R_0', 'R_1', 'R_2', 'C_0', 'C_1')):
            f = {}
        if f is None:
            hibak.append(f'HIBA: nincs forrás a BOM-tételhez: {ert} / {fp} ({b["db"]} db)')
            continue
        if not any(x in f for x in ('l', 'k', 'ti')) and fp.startswith(('R_', 'C_')):
            f = {**f, 'l': rc_spec(ert, fp)}
        kulcs = f.get('g') or f.get('h') or (f.get('l') and str(f['l'])) or f'{ert}|{fp}'
        s = sorok.setdefault(kulcs, dict(f=f, kell=0, mire=[], megj=[], fps=set()))
        s['kell'] += b['db']
        s['fps'].add(fp)
        s['mire'].append(f'{ert} ×{b["db"]} ({", ".join(b["hol"])})')
        if f.get('n') and f['n'] not in s['megj']:
            s['megj'].append(f['n'])
    for f, db, mire in EXTRA:
        sorok[f.get('h') or str(f.get('l'))] = dict(f=f, kell=db, mire=[mire], megj=[], fps=set())

    ki = []
    for s in sorok.values():
        f, kell = s['f'], s['kell']
        passziv = s['fps'] and all(p.startswith(('R_0', 'R_1', 'R_2', 'C_', 'L_0603')) for p in s['fps'])
        sor = dict(Forrás='', Kód='', Termék='', Kell=kell, Vesz='', Egységár='', Összesen='', Készlet='',
                   Mire='; '.join(s['mire']), Megjegyzés='; '.join(s['megj']), Link='', Alternatíva='')
        if f.get('k'):
            sor['Forrás'] = 'kézben'
            ki.append(sor)
            continue
        # Hestore-ajánlat (bruttó Ft)
        ho = None
        if f.get('h'):
            h = hestore(f['h'], frissit)
            v = f.get('vesz')
            if v is None:
                olcso10 = egysegar(h['arak'], 10) <= 20
                v = (max(10 if olcso10 else 0, kell + 2, math.ceil(kell * 1.2)) if passziv
                     else kell + 1 if egysegar(h['arak'], kell + 1) <= 300 else kell)
            ar = egysegar(h['arak'], v)
            ho = dict(forras='Hestore', kod=h['kod'], nev=h['nev'], db=v, ar=ar * AFA, ossz=ar * v * AFA, keszlet=h['keszlet'],
                      link=f'https://www.hestore.hu/prod_{f["h"]}.html', raktaron=h['keszlet'].startswith('Raktáron'))
        # LCSC-ajánlat (bruttó Ft)
        lo = None
        if f.get('l'):
            v = f.get('vesz') or (max(10, kell + 2, math.ceil(kell * 1.2)) if passziv else kell + 1)
            b = lcsc.lcsc_legjobb(f['l'], v, frissit)
            if b:
                lo = dict(forras='LCSC', kod=b['kod'], nev=f"{b['tipus']} – {b['leiras']}", db=b['db'], ar=b['ar'] * USD_HUF * AFA,
                          ossz=b['ossz'] * USD_HUF * AFA, keszlet=f"LCSC: {b['keszlet']} db", link=b['link'], usd=b['ossz'])
        if f.get('ti'):
            sor['Forrás'] = 'TI-rendelés'
            if lo:
                sor['Alternatíva'] = f"ha nem jön: LCSC {lo['kod']} {lo['nev'][:40]} – {lo['ossz']:.0f} Ft"
            ki.append(sor)
            continue
        jo = [o for o in (ho, lo) if o]
        if not jo:
            hibak.append(f'HIBA: se Hestore, se LCSC: {sor["Mire"][:80]}')
            continue
        best = min(jo, key=lambda o: o['ossz'])
        masik = [o for o in jo if o is not best]
        sor.update(Forrás=best['forras'], Kód=best['kod'], Termék=best['nev'], Vesz=best['db'], Egységár=f"{best['ar']:.1f}",
                   Összesen=f"{best['ossz']:.0f}", Készlet=best['keszlet'], Link=best['link'],
                   Alternatíva='; '.join(f"{o['forras']} {o['kod']}: {o['ossz']:.0f} Ft" for o in masik))
        if f.get('kesobb'):
            sor['Forrás'] = 'később'
        if f.get('opc'):
            sor['Megjegyzés'] = ('opcionális; ' + sor['Megjegyzés']).rstrip('; ')
        if best['forras'] == 'Hestore' and not best['raktaron']:
            sor['Megjegyzés'] = (f'NINCS RAKTÁRON ({best["keszlet"]}); ' + sor['Megjegyzés']).rstrip('; ')
        ki.append(sor)

    rend = {'LCSC': 0, 'Hestore': 1, 'TI-rendelés': 2, 'kézben': 3, 'később': 4}
    ki.sort(key=lambda r: (rend[r['Forrás']], 'opcionális' in r['Megjegyzés'], r['Mire']))
    with open(os.path.join(H, 'bom', 'beszerzes.csv'), 'w', encoding='utf-8', newline='') as o:
        w = csv.DictWriter(o, fieldnames=list(ki[0]), quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(ki)

    def osszeg(forras, opc):
        return sum(float(r['Összesen']) for r in ki if r['Forrás'] == forras and ('opcionális' in r['Megjegyzés']) == opc)
    for forras in rend:
        print(f'{forras:12s} {sum(1 for r in ki if r["Forrás"] == forras):3d} tétel')
    hs, ls = osszeg('Hestore', False), osszeg('LCSC', False)
    hz = 0 if hs == 0 or hs >= HESTORE_INGYENES else HESTORE_SZALLITAS
    print(f'Hestore: {hs:,.0f} Ft + szállítás {hz:,.0f} Ft · LCSC: {ls:,.0f} Ft (~{ls / AFA / USD_HUF:.1f} USD nettó, 1 USD = {USD_HUF} Ft)'
          f' · összesen {hs + hz + ls:,.0f} Ft bruttó'.replace(',', ' '))
    print(f'opcionális kábeloldal: Hestore {osszeg("Hestore", True):,.0f} Ft, LCSC {osszeg("LCSC", True):,.0f} Ft'.replace(',', ' '))
    # LCSC-kosár: a BOM-eszközükbe feltölthető lista (LCSC-kód, darab, hová)
    with open(os.path.join(H, 'bom', 'lcsc-kosar.csv'), 'w', encoding='utf-8', newline='') as o:
        w = csv.writer(o)
        w.writerow(['LCSC Part Number', 'Quantity', 'Comment'])
        for r in ki:
            if r['Forrás'] == 'LCSC':
                w.writerow([r['Kód'], r['Vesz'], re.sub(r'\s*\(.*?\)', '', r['Mire'])[:60]])
    print(f'később (most nem): {sum(float(r["Összesen"] or 0) for r in ki if r["Forrás"] == "később"):,.0f} Ft'.replace(',', ' '))
    for r in ki:
        if 'NINCS RAKTÁRON' in r['Megjegyzés']:
            print(f'FIGYELEM: {r["Kód"]} {r["Termék"][:50]} – {r["Készlet"]}')
    for h in hibak:
        print(h)
    print('→ bom/beszerzes.csv, bom/lcsc-kosar.csv')
    sys.exit(1 if hibak else 0)


if __name__ == '__main__':
    main()
