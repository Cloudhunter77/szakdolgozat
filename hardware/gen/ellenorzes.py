"""Teljes ellenőrzés a layout előtt: ERC, láb ↔ pad, modulmag-bekötés, CubeMX ↔ rajz, polaritásvédő FET-ek, NYÁK ↔ rajz, DRC.

Használat (a hardware/ mappából):
    python3 gen/ellenorzes.py            # minden lapot újragenerál (build.sh), majd ellenőriz
    python3 gen/ellenorzes.py --no-build # a meglévő out/*.net és out/*-erc.rpt alapján
    … --no-cubemx                        # a CubeMX fejsoros kódgenerálása nélkül (~1 perc/modul)
A végén „HIBA” (javítandó) és „FIGYELEM” (átnézendő) sorok; kilépési kód 1, ha van hiba.
"""
import os, re, subprocess, sys, glob
G = os.path.dirname(os.path.abspath(__file__))
H = os.path.dirname(G)
sys.path.insert(0, G)
import sx

LAPOK = ['modulmag', 'vezerlo', 'led-modul', 'rele-modul', 'bemeneti-modul']
NYAKOK = ['vezerlo', 'led-modul', 'rele-modul', 'bemeneti-modul']
MODULOK = ['led-modul', 'rele-modul', 'bemeneti-modul']
KICAD_FP = '/var/lib/flatpak/runtime/org.kicad.KiCad.Library.Footprints/x86_64/stable/active/files/footprints'
CUBEMX_DB = glob.glob(os.path.expanduser('~/.local/share/flatpak/app/com.st.STM32CubeMX/x86_64/stable/*/files/stm32cubemx/db/mcu'))
KCLI = ['timeout', '300', 'flatpak', 'run', '--command=kicad-cli', 'org.kicad.KiCad']

hibak, figy = [], []


def hiba(m):
    hibak.append(m)
    print('  HIBA:', m)


def figyelem(m):
    figy.append(m)
    print('  FIGYELEM:', m)


def nev(n):
    """hierarchikus hálózatnév → rövid név (/modulmag/CAN_TX → CAN_TX)"""
    return n.rsplit('/', 1)[-1] if n.startswith('/') else n


def netlista(lap):
    n = sx.parse(open(f'{H}/out/{lap}.net').read())
    comps = {}
    for c in sx.find(sx.first(n, 'components'), 'comp'):
        f = sx.first(c, 'footprint')
        comps[sx.first(c, 'ref')[1]] = dict(value=sx.first(c, 'value')[1], fp=f[1] if f else '')
    pin = {}       # (ref, láb) → hálózat
    func = {}      # (ref, lábnév) → láb
    nets = {}
    for net in sx.find(sx.first(n, 'nets'), 'net'):
        nm = nev(sx.first(net, 'name')[1])
        for nd in sx.find(net, 'node'):
            r, p = sx.first(nd, 'ref')[1], sx.first(nd, 'pin')[1]
            pf = sx.first(nd, 'pinfunction')
            pin[(r, p)] = nm
            nets.setdefault(nm, []).append((r, p))
            if pf:   # a KiCad a lábnév után „_<lábszám>”-ot ír (PA11_44)
                f_ = pf[1][:-len(p) - 1] if pf[1].endswith('_' + p) else pf[1]
                func[(r, f_)] = p
    return comps, pin, func, nets


# ---------------------------------------------------------------------------------------------------- 1. ERC
def erc(build):
    print('\n== 1. Rajzok: generálás + ERC')
    for lap in LAPOK:
        if build:
            r = subprocess.run(['bash', f'{G}/build.sh', lap], cwd=H, capture_output=True, text=True)
            if r.returncode:
                hiba(f'{lap}: a build.sh hibával állt le:\n{r.stdout[-800:]}{r.stderr[-800:]}')
                continue
            for l in r.stdout.splitlines():
                if 'HIÁNYZIK' in l or 'NINCS FOOTPRINT' in l:
                    hiba(f'{lap}: {l.strip()}')
        rpt = open(f'{H}/out/{lap}-erc.rpt').read()
        blokkok = re.findall(r'^\[(\w+)\]: (.*)$', rpt, re.M)
        tip = {}
        for t, msg in blokkok:
            tip[t] = tip.get(t, 0) + 1
        if lap == 'modulmag':
            rossz = [(t, m) for t, m in blokkok if not (t in ('isolated_pin_label', 'pin_not_connected') and 'ierarchical label' in m
                                                       or t == 'isolated_pin_label')]
            for t, m in rossz:
                hiba(f'modulmag ERC: [{t}] {m}')
        elif lap == 'rele-modul':
            for t, m in blokkok:
                if t != 'lib_symbol_mismatch':
                    hiba(f'{lap} ERC: [{t}] {m}')
            if tip.get('lib_symbol_mismatch', 0) > 4:
                hiba(f'{lap}: {tip["lib_symbol_mismatch"]} lib_symbol_mismatch (eddig 4 volt elfogadva)')
        else:
            for t, m in blokkok:
                hiba(f'{lap} ERC: [{t}] {m}')
        print(f'  {lap}: {sum(tip.values())} jelzés {tip or ""}')


# ---------------------------------------------------------------------------------------------------- 2. láb ↔ pad
_pad_cache = {}


def padok(fp):
    if fp in _pad_cache:
        return _pad_cache[fp]
    lib, name = fp.split(':', 1)
    path = f'{H}/lib/modularis.pretty/{name}.kicad_mod' if lib == 'modularis' else f'{KICAD_FP}/{lib}.pretty/{name}.kicad_mod'
    if not os.path.exists(path):
        _pad_cache[fp] = None
        return None
    s = set(re.findall(r'\(pad "([^"]+)"', open(path).read()))
    _pad_cache[fp] = s
    return s


def lab_pad():
    print('\n== 2. Láb ↔ pad (minden bekötött szimbólumláb létezik-e a footprinten)')
    for lap in LAPOK:
        comps, pin, _, _ = netlista(lap)
        hasznalt = {}
        for (r, p) in pin:
            hasznalt.setdefault(r, set()).add(p)
        n = 0
        for r, c in comps.items():
            if not c['fp']:
                hiba(f'{lap}: {r} ({c["value"]}) – nincs footprint')
                continue
            ps = padok(c['fp'])
            if ps is None:
                hiba(f'{lap}: {r} – a footprint nem található: {c["fp"]}')
                continue
            hiany = hasznalt.get(r, set()) - ps
            if hiany:
                hiba(f'{lap}: {r} ({c["value"]}, {c["fp"]}) – ezek a lábak nincsenek a footprinten: {sorted(hiany)}')
            n += 1
        print(f'  {lap}: {n} alkatrész rendben ellenőrizve' if n else f'  {lap}: –')


# ---------------------------------------------------------------------------------------------------- 3. modulmag
def elvar(lap, pin, ref, lab, halo, megj=''):
    v = pin.get((ref, lab))
    ok = v == halo if not callable(halo) else halo(v)
    if not ok:
        hiba(f'{lap}: {ref}.{lab} → {v!r}, várt: {halo if not callable(halo) else megj}')


def modulmag():
    print('\n== 3. Modulmag (STM32L433, SN65HVD230, AP2112K) – mindhárom modulban')
    for lap in MODULOK:
        comps, pin, func, nets = netlista(lap)
        if comps['U6']['value'] != 'STM32L433RCT3':
            hiba(f'{lap}: U6 = {comps["U6"]["value"]}')
        for p in ('1', '19', '32', '48', '64'):
            elvar(lap, pin, 'U6', p, '+3V3')
        elvar(lap, pin, 'U6', '13', '+3V3A')
        for p in ('12', '18', '31', '47', '63'):
            elvar(lap, pin, 'U6', p, 'GND')
        for p, n in {'44': 'CAN_RX', '45': 'CAN_TX', '46': 'SWDIO', '49': 'SWCLK', '7': 'NRST', '60': 'BOOT0',
                     '5': 'OSC_IN', '6': 'OSC_OUT', '8': 'HW_ID', '9': 'VBUS_SENSE', '26': 'HW_REV', '24': 'UART_TX',
                     '25': 'UART_RX', '2': 'STATUS_LED'}.items():
            elvar(lap, pin, 'U6', p, n)
        # SN65HVD230: 1 D, 2 GND, 3 VCC, 4 R, 5 Vref (nyitva), 6 CANL, 7 CANH, 8 Rs
        if comps['U2']['value'] != 'SN65HVD230D':
            hiba(f'{lap}: U2 = {comps["U2"]["value"]}')
        for p, n in {'1': 'CAN_TX', '2': 'GND', '3': '+3V3', '4': 'CAN_RX', '6': 'CAN_L_T', '7': 'CAN_H_T'}.items():
            elvar(lap, pin, 'U2', p, n)
        elvar(lap, pin, 'U2', '5', lambda v: v is None or v.startswith('unconnected'), 'nyitva')
        rs = pin.get(('U2', '8'))
        if sorted(r for r, _ in nets.get(rs, [])) != ['R12', 'U2'] or 'GND' not in (pin.get(('R12', '1')), pin.get(('R12', '2'))):
            hiba(f'{lap}: az U2 Rs-lába nem R12-n át megy a GND-re ({rs}: {nets.get(rs)})')
        # TXD felhúzás
        if {pin.get(('R1', '1')), pin.get(('R1', '2'))} != {'+3V3', 'CAN_TX'}:
            hiba(f'{lap}: R1 nem a CAN_TX felhúzása a 3V3-ra')
        # AP2112K: 1 VIN, 2 GND, 3 EN, 5 VOUT
        if not comps['U5']['value'].startswith('AP2112K-3.3'):
            hiba(f'{lap}: U5 = {comps["U5"]["value"]} (D80: AP2112K-3.3)')
        for p, n in {'1': '+5V', '3': '+5V', '2': 'GND', '5': '+3V3'}.items():
            elvar(lap, pin, 'U5', p, n)
        # táp-LED a +5V-ról (D78)
        if '+5V' not in (pin.get(('R8', '1')), pin.get(('R8', '2'))):
            hiba(f'{lap}: a táp-LED (R8) nem a +5V-ról jár')
        # BOOT0 lehúzás
        if {pin.get(('R2', '1')), pin.get(('R2', '2'))} != {'BOOT0', 'GND'}:
            hiba(f'{lap}: R2 nem a BOOT0 lehúzása')
        # busz-GND ellenállás (D74)
        r = {'led-modul': ('R293', '1R'), 'rele-modul': ('R113', '0R'), 'bemeneti-modul': ('R390', '0R')}[lap]
        if comps[r[0]]['value'] != r[1] or {pin.get((r[0], '1')), pin.get((r[0], '2'))} != {'GND_BUS', 'GND'}:
            hiba(f'{lap}: {r[0]} nem {r[1]} a GND_BUS és a GND között')
        print(f'  {lap}: kész')


# ---------------------------------------------------------------------------------------------------- 4. CubeMX ↔ rajz
def cubemx():
    print('\n== 4. CubeMX-projekt ↔ kapcsolási rajz (lábankénti címke) ↔ L433-adatbázis')
    src = open(f'{G}/cubemx.py').read()
    ns = {'__file__': f'{G}/cubemx.py'}
    exec(src[:src.index('\ndef ioc(')], ns)
    db = {}
    if CUBEMX_DB:
        t = open(os.path.join(CUBEMX_DB[0], 'STM32L433R(B-C)Tx.xml')).read()
        for m in re.finditer(r'<Pin Name="([^"]+)"[^>]*[^/]>(.*?)</Pin>', t, re.S):   # az önzáró <Pin .../> kimarad
            db[m.group(1).split('-')[0].split(' ')[0]] = set(re.findall(r'Signal Name="([^"]+)"', m.group(2)))
    else:
        figyelem('a CubeMX-adatbázis nem található – a jel ↔ láb ellenőrzés kimarad')
    alias = {'I2C1_SCL': 'I2C_SCL', 'I2C1_SDA': 'I2C_SDA'}
    for lap, extra in ns['MODULES'].items():
        comps, pin, func, nets = netlista(lap)
        for p, sig, mode, label in ns['CORE'] + extra:
            base = p.split('-')[0].split(' ')[0]
            lab = func.get(('U6', base))
            if lab is None:
                hiba(f'{lap}: az U6-on nincs {base} nevű láb')
                continue
            net = pin.get(('U6', lab))
            if label and net != alias.get(label, label):
                hiba(f'{lap}: {base} (láb {lab}) a rajzon „{net}”, a CubeMX-ben „{label}”')
            if db and sig not in ('GPIO_Output', 'GPIO_Input', 'EXTI') and sig not in db.get(base, set()):
                hiba(f'{lap}: a {sig} jel nem rendelhető a {base}-hoz (L433-adatbázis)')
        # fordítva: minden modulspecifikus, bekötött MCU-láb szerepel-e a CubeMX-ben
        cub = {p.split('-')[0].split(' ')[0] for p, *_ in ns['CORE'] + extra}
        for (r, pf), lab in func.items():
            if r != 'U6' or not re.fullmatch(r'P[A-H]\d+', pf):
                continue
            net = pin.get(('U6', lab))
            if net and len(nets.get(net, [])) > 1 and not net.startswith('EXP_') and pf not in cub \
                    and net not in ('BOOT0',):
                figyelem(f'{lap}: {pf} ({net}) be van kötve, de a CubeMX-projektben nincs')
        print(f'  {lap}: kész')


CUBEMX_VART = {'led-modul': {'ADC1', 'CAN1', 'COMP2', 'DAC1', 'TIM1', 'TIM15', 'TIM16', 'USART3'},
               'rele-modul': {'ADC1', 'CAN1', 'USART3'},
               'bemeneti-modul': {'ADC1', 'CAN1', 'I2C1', 'USART3'}}


def cubemx_kodgen():
    """a CubeMX fejsorból betölti az .ioc-t és kódot generál egy próbamappába (out/cubemx-test/) – ha a .ioc-ban hiba
    van, a periféria inicializálása kimarad, vagy a generálás el sem indul („IP not ready”)"""
    print('\n== 4b. CubeMX fejsorból: betöltés + kódgenerálás (out/cubemx-test/)')
    for m, vart in CUBEMX_VART.items():
        t = f'{H}/out/cubemx-test/{m}'
        subprocess.run(['rm', '-rf', t])
        os.makedirs(t)
        subprocess.run(['cp', f'{H}/cubemx/{m}/{m}.ioc', t])
        open(f'{t}/script.txt', 'w').write(f'config load {t}/{m}.ioc\nproject path {t}/gen\nproject name {m}\n'
                                          'project toolchain CMake\nproject generate\nexit\n')
        with open(f'{t}/log.txt', 'w') as lf:
            r = subprocess.run(['timeout', '150', 'flatpak', 'run', 'com.st.STM32CubeMX', '-q', f'{t}/script.txt'],
                               stdout=lf, stderr=subprocess.STDOUT)
        mains = glob.glob(f'{t}/gen/**/main.c', recursive=True)
        if not mains:
            log = open(f'{t}/log.txt', errors='replace').read()
            ok = re.findall(r'not ready for code generation: \w+', log)
            hiba(f'{m}: a CubeMX nem generált kódot ({ok or "lásd " + t + "/log.txt"})')
            continue
        van = set(re.findall(r'MX_(\w+?)(?:_UART)?_Init\(\)', open(mains[0]).read())) - {'GPIO'}
        if vart - van:
            hiba(f'{m}: a CubeMX-kódból hiányzik: {sorted(vart - van)}')
        print(f'  {m}: {" ".join(sorted(van))}')


# ---------------------------------------------------------------------------------------------------- 5. polaritásvédelem
FETEK = {   # lap: (FET, D-láb, S-láb(ak), G-láb, csatlakozó GND-lába, gate-ellenállás, Zener, gate-táp)
    'vezerlo': ('Q1', '2', ['3'], '1', ('J1', '2'), 'R56', 'D12', '+24V_P'),
    'rele-modul': ('Q100', '2', ['3'], '1', ('J100', '2'), 'R114', 'D106', '+24V_P'),
    'led-modul': ('Q201', '5', ['1', '2', '3'], '4', ('J201', '2'), 'R294', 'D202', '+24V_RAIL'),
}


def polaritas():
    print('\n== 5. Polaritásvédő FET-ek a GND-ágban (D78)')
    for lap, (q, d, ss, g, (j, jp), r, z, tap) in FETEK.items():
        comps, pin, func, nets = netlista(lap)
        elvar(lap, pin, q, d, 'GND_IN')
        elvar(lap, pin, j, jp, 'GND_IN')
        if sorted(nets.get('GND_IN', [])) != sorted([(q, d), (j, jp)]):
            hiba(f'{lap}: a GND_IN-en más is van: {nets.get("GND_IN")}')
        for s in ss:
            elvar(lap, pin, q, s, 'GND')
        gn = pin.get((q, g))
        tagok = sorted(nets.get(gn, []))
        if tagok != sorted([(q, g), (r, '2'), (z, '1')]):
            hiba(f'{lap}: a {q} gate-hálózata ({gn}): {tagok}')
        elvar(lap, pin, r, '1', tap)
        elvar(lap, pin, z, '2', 'GND')
        if comps[r]['value'] != '10k' or comps[z]['value'] != 'BZT52C15':
            hiba(f'{lap}: {r} = {comps[r]["value"]}, {z} = {comps[z]["value"]}')
        # a 24 V-os TVS és a pufferek a FET UTÁN (a lap GND-jén) legyenek
        for (rr, pp), nm in pin.items():
            if nm == 'GND_IN' and rr not in (q, j):
                hiba(f'{lap}: {rr}.{pp} a GND_IN-en (a FET előtt)')
        print(f'  {lap}: {q} rendben')


# ---------------------------------------------------------------------------------------------------- 6. NYÁK ↔ rajz, DRC
def nyak():
    print('\n== 6. NYÁK ↔ rajz (alkatrészek, padok hálózatai, szimbólum-kapcsolat), rétegrend, tiltott területek, DRC')
    for lap in NYAKOK:
        comps, pin, _, _ = netlista(lap)
        t = open(f'{H}/{lap}/{lap}.kicad_pcb').read()
        b = sx.parse(t)
        fps = {}
        for f in sx.find(b, 'footprint'):
            ref = None
            for p in sx.find(f, 'property'):
                if p[1] == 'Reference':
                    ref = p[2]
            pads = {}
            for pd in sx.find(f, 'pad'):
                ne = sx.first(pd, 'net')
                if ne:
                    pads[pd[1]] = nev(ne[-1])
            fps[ref] = (f[1], pads)
        for r in sorted(set(comps) - set(fps)):
            hiba(f'{lap} NYÁK: hiányzik {r} ({comps[r]["value"]}) – a NYÁK nem követi a rajzot')
        for r in sorted(set(fps) - set(comps)):
            hiba(f'{lap} NYÁK: fölösleges {r} – a rajzon már nincs')
        elteres = 0
        for (r, p), nm in pin.items():
            if r in fps and p in fps[r][1]:
                pn = fps[r][1][p]
                if pn != nm and not (nm.startswith('unconnected') or nm.startswith('Net-(')) and not pn.startswith('unconnected'):
                    elteres += 1
                    if elteres <= 10:
                        hiba(f'{lap} NYÁK: {r}.{p} a NYÁK-on „{pn}”, a rajzon „{nm}”')
            if r in fps and fps[r][0] != comps[r]['fp']:
                pass
        for r in comps:
            if r in fps and fps[r][0] != comps[r]['fp']:
                hiba(f'{lap} NYÁK: {r} footprintje {fps[r][0]}, a rajzon {comps[r]["fp"]}')
        # „Update PCB from Schematic” (D67): minden footprint a rajz egy szimbólumára mutasson (UUID-útvonal)
        uu = set(re.findall(r'\(uuid "([0-9a-f-]+)"\)', open(f'{H}/{lap}/{lap}.kicad_sch').read()
                            + open(f'{H}/modulmag/modulmag.kicad_sch').read()))
        rossz = [p for p in re.findall(r'\(path "([^"]+)"\)', t) if p.rsplit('/', 1)[-1] not in uu]
        if rossz:
            hiba(f'{lap} NYÁK: {len(rossz)} footprint nem a rajz szimbólumára mutat – a NYÁK-ot újra kell generálni (pcbgen --force), '
                 'vagy KiCad-ben „Update PCB” a hivatkozási jel szerinti újrakapcsolással')
        # rétegrend (D82): 1 oz mindenhol – a nagyáramú sávok fedetlenek, utólag ónozva / vezetékkel megerősítve
        cu = re.search(r'\(layer "F\.Cu" \(type "copper"\) \(thickness ([\d.]+)\)', t)
        if cu and float(cu.group(1)) > 0.04:
            hiba(f'{lap} NYÁK: a külső réz {cu.group(1)} mm – D82 óta 1 oz (0,035 mm) kell')
        # tiltott területek (D77)
        if lap == 'rele-modul' and 'keepout' not in t and 'rule_area' not in t:
            hiba('rele-modul NYÁK: hiányzik a 230 V-os belső rétegi tiltás')
        if lap == 'vezerlo' and t.count('(keepout') < 1:
            hiba('vezerlo NYÁK: hiányzik az antenna alatti tiltás')
        # DRC (alap súlyosság): csak a huzalozatlan kötés elfogadott
        rpt = f'{H}/out/{lap}-drc.rpt'
        subprocess.run(KCLI + ['pcb', 'drc', '-o', rpt, f'{H}/{lap}/{lap}.kicad_pcb'], capture_output=True, text=True)
        tip = {}
        for tt in re.findall(r'^\[(\w+)\]', open(rpt).read(), re.M):
            tip[tt] = tip.get(tt, 0) + 1
        for tt, n in tip.items():
            if tt.startswith('silk_'):
                figyelem(f'{lap} DRC: {n} × {tt} (szitanyomat – a layoutnál rendezendő)')
            elif tt != 'unconnected_items':
                hiba(f'{lap} DRC: {n} × {tt}')
        print(f'  {lap}: {len(fps)} footprint, DRC {tip}')


# ---------------------------------------------------------------------------------------------------- 7. elavult kifejezések
ELAVULT = [
    (r'TIM8(?![^\n]{0,80}(helyett|nincs))', 'L433-on nincs TIM8 (D78)'),
    (r'STM32F303RET6(?![^.\n]{0,60}(tartalék|helyett|D27|lábra|kompatib|F303-mal|is beültethető|is jó))', 'a modul-MCU az L433 (D78)'),
    (r'LM74700(?![^\n]{0,30}helyett)', 'kikerült (D78)'),
    (r'TH201|\bNTC\b(?![^\n]{0,40}(helyett|→|D78))', 'az NTC helyett MCP9701A (D78)'),
    (r"VIN_SENSE[^,'.\n]{0,25}PB11|PB11[^,'.\n]{0,25}VIN_SENSE", 'a VIN_SENSE a PB1-en van (D78)'),
    (r'TC2117(?![^.\n]{0,80}(nem|helyett|kellene|D80|200|kézben))', 'marad az AP2112K (D80)'),
]


# ha a sorban ilyen szövegkörnyezet van, a régi kifejezés szándékos (összevetés, történet, készlet)
KORNYEZET = ('D78', 'D79', 'D80', 'helyett', 'tartalék', 'nincs', 'kikerül', 'nem ADC', 'régi', 'nem kell', 'kellene',
             'kézben', '→', 'F303-on', 'F303-mal')


def elavult():
    print('\n== 7. Elavult kifejezések a generátorokban és a dokumentációban (átnézendő)')
    fajlok = glob.glob(f'{G}/*.py') + [f'{H}/../docs/kontextus/{f}' for f in
                                        ('ATTEKINTES.md', 'MODULMAG-SPEC.md', 'VEZERLO-SPEC.md', 'SAMPLE-KERESEK.md',
                                         )] + [f'{H}/../docs/komponenslista.md', f'{H}/README.md']   # a NYAK-ELOKESZITES történeti lista (fejléc jelzi)
    for f in fajlok:
        if f.endswith('ellenorzes.py'):
            continue
        for i, l in enumerate(open(f).read().splitlines(), 1):
            if '~~' in l or any(w in l for w in KORNYEZET) or re.search(r'\b\d+ TC2117', l):
                continue
            for pat, ok in ELAVULT:
                if re.search(pat, l):
                    figyelem(f'{os.path.relpath(f, H)}:{i}: {ok} – „{l.strip()[:110]}”')


if __name__ == '__main__':
    build = '--no-build' not in sys.argv
    erc(build)
    lab_pad()
    modulmag()
    cubemx()
    if '--no-cubemx' not in sys.argv:
        cubemx_kodgen()
    polaritas()
    nyak()
    elavult()
    print(f'\n== ÖSSZESEN: {len(hibak)} hiba, {len(figy)} figyelmeztetés')
    sys.exit(1 if hibak else 0)
