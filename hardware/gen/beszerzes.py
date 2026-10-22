"""Beszerzési lista egy készlethez (vezérlő + LED- + relé- + bemeneti modul): bom/*.csv → bom/beszerzes.csv

Minden BOM-tételhez forrást rendel (Hestore / DigiKey / TI-rendelés / kézben – D84: a legolcsóbb felállás), a Hestore-tételek nettó árát és
készletét a termékoldalról kéri le (gyorsítótár: out/hestore/, 1 s szünet kérésenként). Ha a BOM-ban olyan tétel van,
amihez a FORRAS táblában nincs sor, „HIBA” – így új alkatrész nem maradhat ki a rendelésből.

Használat (a hardware/ mappából):
    python3 gen/beszerzes.py             # a gyorsítótárból (ami nincs benne, azt letölti)
    python3 gen/beszerzes.py --frissit   # minden Hestore-oldalt újra letölt (rendelés előtt: ár, készlet)
"""
import csv, glob, hashlib, html, math, os, re, sys, time, urllib.request
G = os.path.dirname(os.path.abspath(__file__))
H = os.path.dirname(G)
LAPOK = ['vezerlo', 'led-modul', 'rele-modul', 'bemeneti-modul']
CACHE = os.path.join(H, 'out', 'hestore')
AFA = 1.27

# (érték, footprint) → forrás.  Érték None = a footprint minden értékére (csatlakozók, ahol az érték a funkció neve).
# h = Hestore termékazonosító (prod_<h>.html), m = gyártói típusszám a DigiKeyhez (Mouser/TME is jó), vesz = darabszám (ha nem
# a szabály: passzív ≥ 10 db és +20 %, minden más +1 db, ha olcsó), n = megjegyzés.
FORRAS = {
    # --- kondenzátorok
    ('47µ/50V', 'CP_Elec_6.3x7.7'): dict(m='Panasonic EEE-FK1H470P (47 µF / 50 V, 6,3 × 7,7 mm, low-ESR)',
                                         n='Hestore-ban 6,3 × 7,7-es nincs (a „47 uF / 50V SMD” mérete ismeretlen)'),
    ('470µ/50V', 'CP_Radial_D10.0mm_P5.00mm'): dict(h='10028502', n='Ø10 × 20 mm – a 20 mm-es magasságot a ház fedeléhez ellenőrizni'),
    ('100n', 'C_0603_1608Metric'): dict(h='10024356'),
    ('10n', 'C_0603_1608Metric'): dict(h='10027791'),
    ('12p', 'C_0603_1608Metric'): dict(m='Murata GRM1885C1H120JA01D (12 pF, C0G, 0603)', g='12p',
                                       n='Hestore-ban 0603-as 12 pF nincs; 8 MHz-es kvarc CL = 9 pF → 12 pF'),
    ('1n', 'C_0603_1608Metric'): dict(h='10027792'),
    ('1µ', 'C_0603_1608Metric'): dict(h='10036059'),
    ('1µ/16V', 'C_0603_1608Metric'): dict(h='10036059'),
    ('22p', 'C_0603_1608Metric'): dict(h='10027787'),
    ('220n/50V', 'C_0603_1608Metric'): dict(m='Murata GRM188R71H224KAC4D (220 nF, 50 V, X7R, 0603)',
                                            n='Hestore-ban 0603-ban csak 16 V-os Y5V van'),
    ('22n', 'C_0603_1608Metric'): dict(h='10027796'),
    ('4µ7', 'C_0603_1608Metric'): dict(h='10037167', n='6,3 V X5R – a 3,3 V-os sínen megfelel'),
    ('6,8n', 'C_0603_1608Metric'): dict(h='10049421'),
    ('10µ', 'C_0805_2012Metric'): dict(h='10034452'),
    ('10µ/10V', 'C_0805_2012Metric'): dict(h='10034452'),
    ('10µ/16V', 'C_0805_2012Metric'): dict(h='10034452'),
    ('1µ/25V', 'C_0805_2012Metric'): dict(h='10027753'),
    ('1µ/50V', 'C_0805_2012Metric'): dict(h='10033068'),
    ('22µ', 'C_0805_2012Metric'): dict(h='10049425'),
    ('4µ7', 'C_0805_2012Metric'): dict(h='10042711'),
    ('10µ/25V', 'C_1206_3216Metric'): dict(h='10031309'),
    ('1n/2kV', 'C_1206_3216Metric'): dict(m='KEMET C1206C102KGRACTU (1 nF, 2 kV, X7R, 1206)'),
    ('22µ', 'C_1206_3216Metric'): dict(m='Murata GRM31CR71A226KE15L (22 µF, 10 V, X7R, 1206)', g='22u1206',
                                       n='Hestore-ban csak 6,3 V-os X5R – az 5,2 V-os sínen a kapacitás nagy része elveszne'),
    ('22µ/10V', 'C_1206_3216Metric'): dict(m='Murata GRM31CR71A226KE15L (22 µF, 10 V, X7R, 1206)', g='22u1206'),
    ('10µ/50V', 'C_1210_3225Metric'): dict(h='10038374'),
    # --- kvarcok
    ('25MHz ±30ppm', 'Crystal_SMD_3225-4Pin_3.2x2.5mm'): dict(h='10049461', n='Kyocera CX3225, ±20 ppm, CL = 10 pF → C40/C41 = 12 pF'),
    ('8MHz', 'Crystal_SMD_3225-4Pin_3.2x2.5mm'): dict(h='10043000', n='CL = 9 pF → 12 pF-os terhelő kondenzátor (a rajz szerinti)'),
    # --- diódák
    ('SS16', 'D_SMA'): dict(h='10038974'),
    ('STPS3L60U', 'D_SMB'): dict(h='10035880'),
    ('SMBJ28A', 'D_SMB'): dict(m='Littelfuse SMBJ28A', n='Hestore-ban csak 33 V-os van – annak a vágófeszültsége (53 V) túl nagy'),
    ('SMBJ6.0A', 'D_SMB'): dict(m='Littelfuse SMBJ6.0A', n='Hestore-ban csak SOD-123F-ben (SMF6.0A, 200 W) – az kevés az F1 kiolvasztásához'),
    ('SS56C', 'D_SMC'): dict(h='10043211'),
    ('BZT52C15', 'D_SOD-123'): dict(h='10039913'),
    ('SMF5.0A', 'D_SOD-123F'): dict(h='10048902'),
    ('BAT54HT1G', 'D_SOD-323'): dict(h='10034567'),
    # --- IC-k
    ('ESP32-C6-WROOM-1-N8', 'ESP32-C6-WROOM-1'): dict(h='10049443', vesz=1, n='8 MB flash – a firmware 4 MB-ra van beállítva'),
    ('W5500', 'LQFP-48_7x7mm_P0.5mm'): dict(h='10035622', vesz=1),
    ('AP2112K-3.3TRG1', 'SOT-23-5'): dict(h='10047483'),
    ('USBLC6-2SC6', 'SOT-23-6'): dict(h='10034399'),
    ('LM66200DRLR', 'SOT-583-8'): dict(h='10051566'),
    ('LMR33630ADDA', 'Texas_HSOP-8-1EP_3.9x4.9mm_P1.27mm_ThermalVias'): dict(m='TI LMR33630ADDAR'),
    ('TPS259531DSGR', 'Texas_DSG0008A_WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm_ThermalVias'): dict(m='TI TPS259531DSGR'),
    ('MC78L12ACDR2G', 'SOIC-8_3.9x4.9mm_P1.27mm'): dict(m='onsemi MC78L12ACDR2G', n='Hestore-ban csak SOT-89 / TO-92'),
    ('NTD5C648NL', 'TO-252-2'): dict(m='onsemi NTD5C648NLT4G', vesz=7),
    ('NTMFS5C604NL', 'ONSemi_SO-8FL_488AA'): dict(m='onsemi NTMFS5C604NLT1G', vesz=2, n='nincs kézben – a Q201-hez meg kell venni'),
    ('TCAN1044AVDRQ1', 'SOIC-8_3.9x4.9mm_P1.27mm'): dict(ti=1),
    ('LMR36015BRNXR', 'TI_VQFN-HR-12_RNX0012B'): dict(ti=1),
    ('UCC27524DR', 'SOIC-8_3.9x4.9mm_P1.27mm'): dict(ti=1),
    ('INA181A2IDBVR', 'SOT-23-6'): dict(ti=1),
    ('ESD2CAN24-Q1', 'SOT-23'): dict(ti=1, n='ha nem jön: Hestore PESD2CAN (100.424.82, 24 V, SOT-23, azonos lábkiosztás)'),
    ('TPD4E05U06DQAR', 'USON-10_2.5x1.0mm_P0.5mm'): dict(ti=1),
    ('ULN2803ADWR', 'SOIC-18W_7.5x11.6mm_P1.27mm'): dict(ti=1, n='ha nem jön: Hestore ULN2803A-CF (100.407.11, SO18W)'),
    ('HDC3020DEFR', 'TI_WSON-8-1EP_2.5x2.5mm_DEF0008A'): dict(ti=1),
    ('STM32L433RCT3', 'LQFP-64_10x10mm_P0.5mm'): dict(k=1),
    ('SN65HVD230D', 'SOIC-8_3.9x4.9mm_P1.27mm'): dict(k=1),
    ('MCP9701AT-E/TT', 'SOT-23'): dict(k=1),
    ('74HCT14D', 'SOIC-14_3.9x8.7mm_P1.27mm'): dict(k=1),
    ('IRFR1205', 'TO-252-2'): dict(k=1),
    ('IRFR120N', 'TO-252-2'): dict(k=1),
    ('RTD14024', 'Relay_SPDT_Schrack-RT1-16A-FormC_RM5mm'): dict(k=1),
    # --- tekercsek, ferritek
    ('6,8µH', 'L_FerroCore_HPI0630'): dict(h='10042809'),
    ('8,2µH', 'L_FerroCore_HPI0630'): dict(h='10042810'),
    ('BLM18EG221', 'L_0603_1608Metric'): dict(h='10044935'),
    # --- biztosítékok
    ('0,5A', 'Fuse_1206_3216Metric'): dict(m='Littelfuse 0466.500NR (1206, gyors, 0,5 A)', n='a ≥ 32 V-ot az adatlapon ellenőrizni'),
    ('2A', 'Fuse_1206_3216Metric'): dict(m='Littelfuse 0466002.NR (1206, gyors, 2 A)', n='a ≥ 32 V-ot az adatlapon ellenőrizni'),
    ('PTC 0,2A', 'Fuse_1206_3216Metric'): dict(h='10039742'),
    ('10A', 'Fuse_Littelfuse-NANO2-451_453'): dict(m='Littelfuse 0451010.MRL (NANO² 10 A)',
                                                  n='Hestore-ban csak 0,5 A-es NANO²; D76: a szalaghoz kisebb is (0451004.MRL, 4 A)'),
    ('15A', 'Fuseholder_Blade_Mini_Keystone_3568'): dict(m='Keystone 3568 (mini késes biztosíték-foglalat, NYÁK)',
                                                         n='a Hestore SL-506P lábai egy sorban vannak – nem illik a footprintre'),
    # --- csatlakozók
    (None, 'JST_PH_B3B-PH-K_1x03_P2.00mm_Vertical'): dict(h='10049114'),
    (None, 'JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical'): dict(m='JST B4B-PH-K-S', vesz=2),
    (None, 'JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical'): dict(h='10041551'),
    (None, 'PinHeader_1x02_P2.54mm_Vertical'): dict(h='10026161', g='tuske', n='40 pólusú, tördelhető'),
    (None, 'PinHeader_1x06_P2.54mm_Vertical'): dict(h='10026161', g='tuske'),
    (None, 'PinHeader_1x07_P2.54mm_Vertical'): dict(h='10026161', g='tuske'),
    ('HR911105A', 'RJ45_Hanrun_HR911105A_Horizontal'): dict(h='10043564', n='Hestore: csak rendelésre (átfutás?) – opcionális (D45)'),
    ('USB-C 16P', 'USB_C_Receptacle_HRO_TYPE-C-31-M-12'): dict(h='10050233'),
    (None, 'SW_SPST_TL3342'): dict(h='10040903', n='PTS525S5215A (TS4415-típus): lábköz 3,7 mm, a TL3342-footprinten jó'),
    ('24V IN 15A', 'TerminalBlock_Phoenix_MKDS-1,5-2_1x02_P5.00mm_Horizontal'): dict(h='10043373', n='Degson DG128, 15 A UL / 18 A IEC'),
    (None, 'TerminalBlock_Phoenix_MKDS-3-2-5.08_1x02_P5.08mm_Horizontal'): dict(k=1, g='rele-sorkapocs',   # J101–J104
                                                                                n='D83: 5,08 mm-es THT a készletből – a csomagot megnézni (≥ 16 A / 250 V)'),
    (None, 'TerminalBlock_Phoenix_MKDS-1,5-3_1x03_P5.00mm_Horizontal'): dict(h='10052228', n='KF128-5.0-3P, 10 A / 300 V'),
    (None, 'TerminalBlock_Degson_DG250-3.5-02P_1x02_P3.50mm_45Degree'): dict(h='10044102', n='rugós, 8 A (UL)'),
    # --- LED-ek
    ('piros', 'LED_0603_1608Metric'): dict(h='10036670'),
    ('zöld', 'LED_0603_1608Metric'): dict(k=1),
    ('WS2812B-V5', 'LED_WS2812B_PLCC4_5.0x5.0mm_P3.2mm'): dict(h='10048841'),
    # --- ellenállások (0603, ha nincs más jelölve)
    ('0R', 'R_0603_1608Metric'): dict(h='10043634'),
    ('100R', 'R_0603_1608Metric'): dict(h='10051417'),
    ('100k', 'R_0603_1608Metric'): dict(h='10043366'),
    ('100k 1%', 'R_0603_1608Metric'): dict(h='10043366'),
    ('10R', 'R_0603_1608Metric'): dict(h='10049431'),
    ('10R 1%', 'R_0603_1608Metric'): dict(h='10049431'),
    ('10k', 'R_0603_1608Metric'): dict(h='10023910'),
    ('10k 1%', 'R_0603_1608Metric'): dict(h='10023910'),
    ('12,4k 1%', 'R_0603_1608Metric'): dict(h='10049435'),
    ('150k', 'R_0603_1608Metric'): dict(h='10049438'),
    ('1k', 'R_0603_1608Metric'): dict(h='10049434'),
    ('2,2k', 'R_0603_1608Metric'): dict(h='10036842'),
    ('2k2', 'R_0603_1608Metric'): dict(h='10036842'),
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
    ('1,02k 1%', 'R_0603_1608Metric'): dict(m='Yageo RC0603FR-071K02L', n='E96 – Hestore-ban 0603-ban nincs'),
    ('1k54 1%', 'R_0603_1608Metric'): dict(m='Yageo RC0603FR-071K54L', n='E96 – Hestore-ban 0603-ban nincs'),
    ('2k49 1%', 'R_0603_1608Metric'): dict(m='Yageo RC0603FR-072K49L', n='E96 – Hestore-ban 0603-ban nincs'),
    ('23,7k 1%', 'R_0603_1608Metric'): dict(m='Yageo RC0603FR-0723K7L', n='E96 – Hestore-ban nincs (24 k-val ~5,17 V lenne)'),
    ('43,2k 1%', 'R_0603_1608Metric'): dict(m='Yageo RC0603FR-0743K2L', n='E96 – Hestore-ban nincs (43 k-val 3,33 V, az is jó)'),
    ('499R', 'R_0603_1608Metric'): dict(m='Yageo RC0603FR-07499RL', n='E96 – Hestore-ban 0603-ban nincs'),
    ('715R 1%', 'R_0603_1608Metric'): dict(m='Yageo RC0603FR-07715RL', n='E96 – Hestore-ban 0603-ban nincs'),
    ('10k', 'R_0805_2012Metric'): dict(h='10040338'),
    ('120R', 'R_0805_2012Metric'): dict(h='10027757'),
    ('0R', 'R_1206_3216Metric'): dict(h='10001321'),
    ('1R', 'R_1206_3216Metric'): dict(h='10035914'),
    ('0R', 'R_2512_6332Metric'): dict(h='10037977'),
    ('1m 1%', 'R_Shunt_Vishay_WSK2512_6332Metric_T1.19mm'): dict(h='10037011', vesz=2,
                                                                 n='Bourns CRE2512, 2 kivezetésű – a Kelvin-footprint két-két padját összeforrasztja'),
}

# BOM-on kívüli tételek: (forrás-dict, darab, mire)
EXTRA = [
    (dict(h='10039981', vesz=4), 3, 'DIN-ház, 4 M: vezérlő, LED-, relémodul (+1 tartalék) – D73'),
    (dict(h='10039989', vesz=1), 1, 'DIN-ház, 6 M: bemeneti modul – D73'),
    (dict(m='ST NUCLEO-L433RC-P'), 1, 'fejlesztőpanel a modul-firmware-hez (D79)'),
    (dict(m='Littelfuse 0297015.WXNV (MINI, 15 A)', vesz=2), 1, 'F201 betétje – normál mini (az alacsony profilú rövid lábú)'),
    (dict(h='10025120', vesz=5), 4, 'jumper a LEZÁRÁS tüskesorokra (JP1)'),
    (dict(h='10041545', vesz=8, opc=1), 8, 'kábeloldal: XH-ház a buszkábelekhez (4 kábel × 2 vég)'),
    (dict(h='10035076', vesz=40, opc=1), 32, 'kábeloldal: XH-érintkező (BXH-001T-P0.6)'),
    (dict(h='10040623', vesz=10, opc=1), 10, 'kábeloldal: PH-ház, 3 pólusú (érzékelőkábelek)'),
    (dict(h='10046585', vesz=2, opc=1), 1, 'kábeloldal: PH-ház, 4 pólusú (külső I²C)'),
    (dict(h='10038522', vesz=40, opc=1), 34, 'kábeloldal: PH-érintkező (SPH-002T-P0.5S)'),
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
        if f is None:
            hibak.append(f'HIBA: nincs forrás a BOM-tételhez: {ert} / {fp} ({b["db"]} db)')
            continue
        kulcs = f.get('h') or f.get('g') or f.get('m') or f'{ert}|{fp}'
        s = sorok.setdefault(kulcs, dict(f=f, kell=0, mire=[], megj=[], fps=set()))
        s['kell'] += b['db']
        s['fps'].add(fp)
        s['mire'].append(f'{ert} ×{b["db"]} ({", ".join(b["hol"])})')
        if f.get('n') and f['n'] not in s['megj']:
            s['megj'].append(f['n'])
        if 'vesz' in f:
            s['f'] = {**s['f'], 'vesz': f['vesz']}
    for f, db, mire in EXTRA:
        kulcs = f.get('h') or f.get('m')
        sorok[kulcs] = dict(f=f, kell=db, mire=[mire], megj=[], fps=set())

    ki, ossz, ossz_opc = [], 0.0, 0.0
    for s in sorok.values():
        f, kell = s['f'], s['kell']
        forras = 'Hestore' if f.get('h') else 'DigiKey' if f.get('m') else 'TI-rendelés' if f.get('ti') else 'kézben'
        sor = dict(Forrás=forras, Kód='', Termék=f.get('m', ''), Kell=kell, Vesz='', Egységár='', Összesen='',
                   Készlet='', Mire='; '.join(s['mire']), Megjegyzés='; '.join(s['megj']), Link='')
        h = hestore(f['h'], frissit) if forras == 'Hestore' else None
        if forras in ('Hestore', 'DigiKey'):
            vesz = f.get('vesz')
            if vesz is None:
                # passzív: 10 db, ha 10 db-tól legfeljebb 20 Ft/db, különben +20 % (min. +2); más: +1 db, ha olcsó
                passziv = s['fps'] and all(p.startswith(('R_0', 'R_1', 'C_', 'L_0603')) for p in s['fps'])
                olcso10 = h is None or egysegar(h['arak'], 10) <= 20
                olcso = h is None or egysegar(h['arak'], kell + 1) <= 300
                vesz = (max(10 if olcso10 else 0, kell + 2, math.ceil(kell * 1.2)) if passziv
                        else kell + 1 if olcso else kell)
            sor['Vesz'] = vesz
        if forras == 'Hestore':
            ar = egysegar(h['arak'], sor['Vesz'])
            sor.update(Kód=h['kod'], Termék=h['nev'], Egységár=f'{ar:.2f}', Összesen=f'{ar * sor["Vesz"]:.0f}',
                       Készlet=h['keszlet'], Link=f'https://www.hestore.hu/prod_{f["h"]}.html')
            if f.get('opc'):
                sor['Megjegyzés'] = ('opcionális; ' + sor['Megjegyzés']).rstrip('; ')
                ossz_opc += ar * sor['Vesz']
            else:
                ossz += ar * sor['Vesz']
            if not h['keszlet'].startswith('Raktáron'):
                sor['Megjegyzés'] = (f'NINCS RAKTÁRON ({h["keszlet"]}); ' + sor['Megjegyzés']).rstrip('; ')
        ki.append(sor)
    rend = {'Hestore': 0, 'DigiKey': 1, 'TI-rendelés': 2, 'kézben': 3}
    ki.sort(key=lambda r: (rend[r['Forrás']], 'opcionális' in r['Megjegyzés'], r['Mire']))
    with open(os.path.join(H, 'bom', 'beszerzes.csv'), 'w', encoding='utf-8', newline='') as o:
        w = csv.DictWriter(o, fieldnames=list(ki[0]), quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(ki)
    for forras in rend:
        print(f'{forras:12s} {sum(1 for r in ki if r["Forrás"] == forras):3d} tétel')
    print(f'Hestore nettó: {ossz:,.0f} Ft, bruttó: {ossz * AFA:,.0f} Ft (+ opcionális kábeloldal: {ossz_opc * AFA:,.0f} Ft bruttó)'
          .replace(',', ' '))
    for r in ki:
        if 'NINCS RAKTÁRON' in r['Megjegyzés']:
            print(f'FIGYELEM: {r["Kód"]} {r["Termék"][:50]} – {r["Készlet"]}')
    for h in hibak:
        print(h)
    print('→ bom/beszerzes.csv')
    sys.exit(1 if hibak else 0)


if __name__ == '__main__':
    main()
