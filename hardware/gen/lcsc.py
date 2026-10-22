"""LCSC-árak a JLCPCB alkatrészkeresőjén át (a NYÁK-rendeléshez csapva közös a szállítás – D85).

lcsc_legjobb(spec, db) → a legolcsóbb raktáron lévő találat: dict(kod, tipus, tok, leiras, db, ar, ossz, link) vagy None.
spec: {'q': kulcsszó, 'tok': tok-részlet} vagy {'R': (érték, tok)} / {'C': (érték, tok, min. feszültség, dielektrikum)}.
Gyorsítótár: out/lcsc/ (a beszerzes.py --frissit törli).
"""
import hashlib, json, os, re, time, urllib.request
G = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(os.path.dirname(G), 'out', 'lcsc')
URL = 'https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList'


def kereses(kw, n=25, frissit=False):
    os.makedirs(CACHE, exist_ok=True)
    f = os.path.join(CACHE, hashlib.md5(f'{kw}|{n}'.encode()).hexdigest() + '.json')
    if frissit or not os.path.exists(f):
        time.sleep(0.7)
        req = urllib.request.Request(URL, data=json.dumps({'keyword': kw, 'currentPage': 1, 'pageSize': n}).encode(),
                                     headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as r, open(f, 'wb') as o:
            o.write(r.read())
    d = json.load(open(f, encoding='utf-8'))
    return (d.get('data') or {}).get('componentPageInfo', {}).get('list') or []


def _ar(r, db):
    p = [x['productPrice'] for x in r.get('componentPrices') or [] if x['startNumber'] <= db]
    return p[-1] if p else None


def _attr(r):
    return {a['attribute_name_en']: a['attribute_value_name'] for a in (r.get('attributes') or [])}


SZORZO = {'p': 1e-12, 'n': 1e-9, 'u': 1e-6, 'µ': 1e-6, 'm': 1e-3, 'k': 1e3, 'M': 1e6, 'R': 1, '': 1}


def ertek(s):
    """'4µ7' → 4.7e-6, '2k2' → 2200, '49R9' → 49.9, '10k' → 1e4, '1m' → 1e-3, '715R' → 715"""
    s = re.sub(r'\s*\d+%$', '', s.split('/')[0].strip()).replace(',', '.').replace('Ω', '').replace('F', '')
    m = re.fullmatch(r'(\d+)([pnuµmkMR])(\d+)', s)
    if m:
        return float(f'{m.group(1)}.{m.group(3)}') * SZORZO[m.group(2)]
    m = re.fullmatch(r'(\d+(?:\.\d+)?)\s*([pnuµmkMR]?)', s)
    return float(m.group(1)) * SZORZO[m.group(2)] if m else None


def _lcsc_ertek(s):
    """LCSC-attribútum ('10kΩ', '4.7uF', '100nF', '49.9Ω') → szám"""
    m = re.match(r'([\d.]+)\s*([pnuµmkM]?)', s or '')
    return float(m.group(1)) * SZORZO[m.group(2)] if m else None


def _feszultseg(s):
    m = re.match(r'([\d.]+)\s*(k?)V', s or '')
    return float(m.group(1)) * (1000 if m.group(2) else 1) if m else 0


def _rc_kulcsszo(v, tok, tipus):
    if tipus == 'R':
        if v == 0:
            return f'0Ω {tok}'
        for e, jel in ((1e6, 'MΩ'), (1e3, 'kΩ'), (1, 'Ω'), (1e-3, 'mΩ')):
            if v >= e:
                return f'{v / e:g}{jel} {tok}'
    for e, jel in ((1e-6, 'uF'), (1e-9, 'nF'), (1e-12, 'pF')):
        if v >= e * 0.999:
            return f'{v / e:g}{jel} {tok}'


def lcsc_legjobb(spec, db, frissit=False):
    jeloltek = []
    if 'R' in spec or 'C' in spec:
        tipus = 'R' if 'R' in spec else 'C'
        v_str, tok = spec[tipus][:2]
        v = ertek(v_str)
        kw = _rc_kulcsszo(v, tok, tipus) + (' 1%' if tipus == 'R' else '')
        for r in kereses(kw, 40, frissit):
            a = _attr(r)
            if tok not in (r.get('componentSpecificationEn') or ''):
                continue
            if tipus == 'R':
                rv = _lcsc_ertek(a.get('Resistance'))
                if rv is None or abs(rv - v) > max(v, 1e-9) * 0.001 + (1e-6 if v == 0 else 0):
                    continue
                tol = a.get('Tolerance', '')
                if v and not re.search(r'±(1|0\.\d+)%', tol):
                    continue
            else:
                cv = _lcsc_ertek(a.get('Capacitance'))
                if cv is None or abs(cv - v) > v * 0.001:
                    continue
                umin, diel = spec['C'][2], spec['C'][3]
                if _feszultseg(a.get('Voltage Rating') or a.get('Voltage Rated')) < umin:
                    continue
                tc = a.get('Temperature Coefficient', '')
                if diel and not any(d in tc for d in diel):
                    continue
            jeloltek.append(r)
    else:
        for r in kereses(spec['q'], 25, frissit):
            if spec.get('tok') and spec['tok'].lower() not in (r.get('componentSpecificationEn') or '').lower() + (r.get('describe') or '').lower():
                continue
            if spec.get('tipus') and spec['tipus'].lower() not in r['componentModelEn'].lower():
                continue
            jeloltek.append(r)
    best = None
    for r in jeloltek:
        q = max(db, r.get('minPurchaseNum') or 1)
        p = _ar(r, q)
        if p is None or (r.get('stockCount') or 0) < q:
            continue
        o = p * q
        if best is None or o < best['ossz']:
            best = dict(kod=r['componentCode'], tipus=r['componentModelEn'], tok=r.get('componentSpecificationEn'),
                        leiras=(r.get('describe') or '')[:120], db=q, ar=p, ossz=o, keszlet=r.get('stockCount'),
                        link=f"https://www.lcsc.com/product-detail/{r['componentCode']}.html")
    return best
