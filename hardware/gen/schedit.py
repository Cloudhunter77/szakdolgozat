"""Kézzel szerkesztett (D67) kapcsolási rajzok módosítása szkriptből – Claude, 2026-10-27 (a konzulensi visszajelzéshez, D90).

    from schedit import Lap
    L = Lap('vezerlo/vezerlo.kicad_sch')
    L.pin('Q1', '2')                      # láb vége (mm, rajzkoordináta)
    L.wire((x0, y0), (x1, y1)); L.power('+24V_P', (x, y), 90); L.remove(L.sym('D7'))
    L.save()                              # csak ha a fájl a beolvasás óta nem változott (Balázs nem mentett közben)

A fájlt az sx-szel olvassa és írja (a KiCad a következő mentéskor a saját formájára hozza). Az új elemek UUID-je
determinisztikus (fájlnév + sorszám), így két futás ugyanazt adja.
"""
import copy
import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(__file__))
import sx
from sx import Sym
from kigen import load_lib, flat_symbol, pins_of, rot, g, G

NS = uuid.UUID('0c5e7a8b-d90d-4a2b-9e61-6b6f6e7a7562')
# tápszimbólum-rajzolatok: a hálózat neve a Value mező (KiCad 7+), a rajzolat csak jelzés
RAJZOLAT_LE = {'GND', 'GNDPWR', 'GNDA', 'GNDD', 'Earth'}


def _key(p):
    return (g(p[0]), g(p[1]))


class Lap:
    def __init__(self, path, tag='d90'):
        self.path = path
        self.mtime = os.path.getmtime(path)
        self.t = sx.parse(open(path, encoding='utf-8').read())
        self.libs = sx.first(self.t, 'lib_symbols')
        self._ns = uuid.uuid5(NS, os.path.basename(path) + '/' + tag)
        self._n = 0

    # ------------------------------------------------------------------ alap
    def uid(self):
        self._n += 1
        return str(uuid.uuid5(self._ns, str(self._n)))

    def top(self, kind):
        return [e for e in self.t if isinstance(e, list) and e and e[0] == kind]

    def symbols(self):
        return self.top('symbol')

    @staticmethod
    def prop(it, name):
        for p in sx.find(it, 'property'):
            if p[1] == name:
                return p
        return None

    def ref(self, it):
        p = self.prop(it, 'Reference')
        return p[2] if p else None

    def sym(self, ref, unit=None):
        r = [s for s in self.symbols() if self.ref(s) == ref and (unit is None or int(sx.first(s, 'unit')[1]) == unit)]
        if len(r) != 1:
            raise KeyError(f'{ref}: {len(r)} találat')
        return r[0]

    def has(self, ref):
        return any(self.ref(s) == ref for s in self.symbols())

    def libdef(self, lib_id):
        for s in sx.find(self.libs, 'symbol'):
            if s[1] == lib_id:
                return s
        raise KeyError(lib_id)

    def pins(self, it):
        """{lábszám: (x, y, kifelé mutató irány °)} – a kigen.pinpoints szerint"""
        at = sx.first(it, 'at'); x, y, r = float(at[1]), float(at[2]), int(float(at[3]))
        mir = sx.first(it, 'mirror'); mir = str(mir[1]) if mir else None
        unit = int(sx.first(it, 'unit')[1])
        out = {}
        for num, lst in pins_of(self.libdef(sx.first(it, 'lib_id')[1]), unit).items():
            px, py, pa = lst[0]
            rx, ry = rot(px, py, r)
            a = (pa + r) % 360
            if mir == 'y':
                rx, a = -rx, (180 - a) % 360
            elif mir == 'x':
                ry, a = -ry, (-a) % 360
            out[num] = (g(x + rx), g(y - ry), (a + 180) % 360)
        return out

    def pin(self, ref, num, unit=None):
        p = self.pins(self.sym(ref, unit))[num]
        return p[0], p[1]

    def remove(self, it):
        self.t.remove(it)

    # ------------------------------------------------------------------ keresés pont szerint
    def wires(self):
        return self.top('wire')

    @staticmethod
    def wpts(w):
        p = sx.first(w, 'pts')
        return [(float(q[1]), float(q[2])) for q in sx.find(p, 'xy')]

    def wires_at(self, p):
        k = _key(p)
        return [w for w in self.wires() if k in (_key(q) for q in self.wpts(w))]

    def wires_through(self, p):
        """vezetékek, amelyeknek a belsején (nem a végén) megy át a pont"""
        x, y = p; out = []
        for w in self.wires():
            (ax, ay), (bx, by) = self.wpts(w)
            if _key(p) in (_key((ax, ay)), _key((bx, by))):
                continue
            if abs(ax - bx) < 1e-6 and abs(x - ax) < 1e-6 and min(ay, by) < y < max(ay, by):
                out.append(w)
            elif abs(ay - by) < 1e-6 and abs(y - ay) < 1e-6 and min(ax, bx) < x < max(ax, bx):
                out.append(w)
        return out

    def at_point(self, kinds, p):
        k = _key(p)
        return [e for kind in kinds for e in self.top(kind) if _key((float(sx.first(e, 'at')[1]), float(sx.first(e, 'at')[2]))) == k]

    def labels(self, name=None):
        return [e for e in self.top('label') + self.top('global_label') if name is None or e[1] == name]

    def pin_owner(self, p):
        """(hivatkozás, lábszám) párok, amelyek lába ebben a pontban ér véget"""
        k = _key(p); out = []
        for s in self.symbols():
            for num, (x, y, _) in self.pins(s).items():
                if _key((x, y)) == k:
                    out.append((self.ref(s), num))
        return out

    # ------------------------------------------------------------------ új elemek
    def wire(self, *pts):
        """derékszögű vezeték a pontokon át (ahol kell, L-töréssel)"""
        pts = [(g(p[0]), g(p[1])) for p in pts]
        path = [pts[0]]
        for q in pts[1:]:
            a = path[-1]
            if a[0] != q[0] and a[1] != q[1]:
                path.append((q[0], a[1]))
            path.append(q)
        for a, b in zip(path, path[1:]):
            if a != b:
                self.t.append([Sym('wire'), [Sym('pts'), [Sym('xy'), a[0], a[1]], [Sym('xy'), b[0], b[1]]],
                               [Sym('stroke'), [Sym('width'), 0], [Sym('type'), Sym('default')]], [Sym('uuid'), self.uid()]])

    def junction(self, p):
        self.t.append([Sym('junction'), [Sym('at'), g(p[0]), g(p[1])], [Sym('diameter'), 0],
                       [Sym('color'), 0, 0, 0, 0], [Sym('uuid'), self.uid()]])

    def label(self, name, p, d):
        """helyi címke a p pontban, d irányba (0 = jobbra, 90 = fel, …) olvasható szöveggel"""
        just = Sym('left') if d in (0, 90) else Sym('right')
        self.t.append([Sym('label'), name, [Sym('at'), g(p[0]), g(p[1]), d],
                       [Sym('fields_autoplaced'), Sym('yes')],
                       [Sym('effects'), [Sym('font'), [Sym('size'), 1.27, 1.27]], [Sym('justify'), just, Sym('bottom')]],
                       [Sym('uuid'), self.uid()]])

    def text(self, s, p, size=1.27):
        self.t.append([Sym('text'), s, [Sym('exclude_from_sim'), Sym('no')], [Sym('at'), g(p[0]), g(p[1]), 0],
                       [Sym('effects'), [Sym('font'), [Sym('size'), size, size]], [Sym('justify'), Sym('left'), Sym('bottom')]],
                       [Sym('uuid'), self.uid()]])

    def _ensure_lib(self, lib_id):
        try:
            return self.libdef(lib_id)
        except KeyError:
            lib, name = lib_id.split(':')
            d = flat_symbol(lib, name)
            d[1] = lib_id
            self.libs.append(d)
            return d

    def next_ref(self, prefix, lo, hi, tilos=()):
        used = set(tilos)
        for s in self.symbols():
            r = self.ref(s) or ''
            used.add(r)
            for inst in self._inst_paths(s):
                used.add(sx.first(inst, 'reference')[1])
        for n in range(lo, hi):
            r = f'{prefix}{n:03d}'
            if r not in used:
                return r
        raise SystemExit(f'{prefix}: nincs szabad szám {lo}–{hi}')

    @staticmethod
    def _inst_paths(s):
        inst = sx.first(s, 'instances')
        return [pth for prj in sx.find(inst, 'project') for pth in sx.find(prj, 'path')] if inst else []

    def power(self, name, p, d, rajzolat=None, ref=None, minta=None):
        """tápszimbólum (a hálózat neve = Value) a p pontban, d irányba mutatva (90 = felfelé). A példány-szerkezetet
        (instances) egy meglévő tápszimbólumról másolja (minta)."""
        rajzolat = rajzolat or ('GND' if name.startswith('GND') else '+24V')
        lib_id = f'power:{rajzolat}'
        self._ensure_lib(lib_id)
        if minta is None:
            minta = next(s for s in self.symbols() if str(sx.first(s, 'lib_id')[1]).startswith('power:')
                         and not self.ref(s).startswith('#FLG'))
        it = copy.deepcopy(minta)
        le = rajzolat in RAJZOLAT_LE
        r = ({270: 0, 90: 180, 0: 90, 180: 270} if le else {90: 0, 270: 180, 180: 90, 0: 270})[d]
        x, y = g(p[0]), g(p[1])
        sx.first(it, 'lib_id')[1] = lib_id
        at = sx.first(it, 'at'); at[1:] = [x, y, r]
        m = sx.first(it, 'mirror')
        if m:
            it.remove(m)
        sx.first(it, 'uuid')[1] = self.uid()
        ref = ref or self.next_ref('#PWR', 1, 999)
        # a szöveg: lefelé mutatónál alatta, felfelé mutatónál fölötte (forgatás nélkül olvasható)
        off = {0: (0, 3.81), 180: (0, -3.81), 90: (3.81, 0), 270: (-3.81, 0)}[r] if le else \
              {0: (0, -3.81), 180: (0, 3.81), 90: (-3.81, 0), 270: (3.81, 0)}[r]
        for pr in sx.find(it, 'property'):
            pat = sx.first(pr, 'at')
            if pr[1] == 'Reference':
                pr[2] = ref; pat[1:] = [x, g(y + (3 if le else -3)), 0]
            elif pr[1] == 'Value':
                pr[2] = name; pat[1:] = [g(x + off[0]), g(y + off[1]), 90 if r in (90, 270) else 0]
                eff = sx.first(pr, 'effects')
                for j in sx.find(eff, 'justify'):
                    eff.remove(j)
                if r in (90, 270):
                    j = 'right' if off[0] < 0 else 'left'
                    if r == 90:                                   # 90°-nál a KiCad megfordítja az igazítást
                        j = {'left': 'right', 'right': 'left'}[j]
                    eff.append([Sym('justify'), Sym(j)])
            else:
                pat[1:] = [x, y, 0]
        for pn in sx.find(it, 'pin'):
            sx.first(pn, 'uuid')[1] = self.uid()
        for pth in self._inst_paths(it):
            sx.first(pth, 'reference')[1] = ref
        self.t.append(it)
        return it

    def move(self, it, dx, dy):
        """szimbólum (a mezőivel együtt), címke, szöveg vagy csomópont eltolása"""
        for a in [sx.first(it, 'at')] + [sx.first(p, 'at') for p in sx.find(it, 'property')]:
            if a:
                a[1], a[2] = g(float(a[1]) + dx), g(float(a[2]) + dy)

    # ------------------------------------------------------------------ mentés
    def save(self, path=None, force=False):
        path = path or self.path
        if path == self.path and not force and os.path.getmtime(path) != self.mtime:
            raise SystemExit(f'{path}: a beolvasás óta megváltozott (Balázs mentett?) – nem írom felül')
        open(path, 'w', encoding='utf-8').write(sx.dump(self.t) + '\n')


# ---------------------------------------------------------------------- D-hivatkozások (döntésnapló) kivétele
import re as _re
_D = r'D(?:1[3-9]|[2-9]\d)(?!\d)'            # döntés-sorszám (D10–D12 alkatrész a vezérlőn, azokat nem)
_DL = _D + r'(?:\s*[,/]\s*' + _D + r')*'


def strip_d(s):
    """„(D78)”, „(D69, D71, D89)”, „D71: …”, „…, D63)”, „– D30, D78” → kivéve (a konzulensnek érthetetlen)."""
    o = s
    s = _re.sub(r'\s*[–-]\s*' + _DL + r'(?=\s*(?:$|\)|\\n|\n))', '', s)
    s = _re.sub(r'\s*[–-]\s*' + _DL + r'(?=\s*[;,])', '', s)          # „… – D84; …”
    s = _re.sub(r'\s*\(\s*' + _DL + r'\s*\)', '', s)
    s = _re.sub(r'\(\s*' + _DL + r'\s*[;,]\s*', '(', s)
    s = _re.sub(r'\s*[,;]\s*' + _DL + r'\s*\)', ')', s)
    s = _re.sub(r'(^|[.;·]\s+|\n)' + _DL + r':\s*(\w)', lambda m: m.group(1) + (m.group(2).upper() if m.group(1).strip() in ('', '.') else m.group(2)), s)
    s = _re.sub(r'\b' + _DL + r':\s*', '', s)
    s = _re.sub(r'  +', ' ', s).replace(' )', ')').replace('( ', '(').replace(' ,', ',')
    return s if s != o else o


def strip_d_lap(L):
    """a lap szövegeiből és mezőiből (a hivatkozás, lábnyom, adatlap kivételével); visszaadja a módosítások számát"""
    n = 0
    for e in L.top('text') + L.top('text_box'):
        u = strip_d(e[1])
        if u != e[1]:
            e[1] = u; n += 1
    for s in L.symbols():
        for p in sx.find(s, 'property'):
            if p[1] in ('Reference', 'Footprint', 'Datasheet'):
                continue
            u = strip_d(p[2])
            if u != p[2]:
                p[2] = u; n += 1
    return n


def _lap_stub(self, ref, hossz=5.08):
    """a ref lábaira közvetlenül tett címkék egy hossz mm-es vezetékcsonk végére kerülnek (a konzulens kérése)"""
    n = 0
    lab_kinds = ('label', 'hierarchical_label', 'global_label')
    for s in [s for s in self.symbols() if self.ref(s) == ref]:
        for num, (x, y, a) in self.pins(s).items():
            labs = self.at_point(lab_kinds, (x, y))
            if not labs or self.wires_at((x, y)):
                continue
            dx, dy = {0: (1, 0), 90: (0, -1), 180: (-1, 0), 270: (0, 1)}[a]
            for e in labs:
                self.move(e, dx * hossz, dy * hossz)
            self.wire((x, y), (x + dx * hossz, y + dy * hossz))
            n += 1
    return n


def _lap_clone(self, minta_ref, uj_ref, at, value=None, r=None):
    """egy meglévő szimbólum másolata új hivatkozással (minden projekt-példányban), új helyen"""
    s = copy.deepcopy(self.sym(minta_ref))
    a = sx.first(s, 'at'); dx, dy = at[0] - float(a[1]), at[1] - float(a[2])
    self.move(s, dx, dy)
    if r is not None:
        a[3] = r
    sx.first(s, 'uuid')[1] = self.uid()
    for pn in sx.find(s, 'pin'):
        sx.first(pn, 'uuid')[1] = self.uid()
    self.prop(s, 'Reference')[2] = uj_ref
    for pth in self._inst_paths(s):
        sx.first(pth, 'reference')[1] = uj_ref
    if value is not None:
        self.prop(s, 'Value')[2] = value
    self.t.append(s)
    return s


Lap.stub_labels = _lap_stub
Lap.clone = _lap_clone


def _lap_wire_between(self, a, b):
    ka, kb = _key(a), _key(b)
    r = [w for w in self.wires() if {_key(q) for q in self.wpts(w)} == {ka, kb}]
    if len(r) != 1:
        raise KeyError(f'vezeték {a}–{b}: {len(r)} találat')
    return r[0]


def _lap_unwire(self, a, b):
    self.remove(self.wire_between(a, b))


def _lap_split(self, p):
    """a p ponton átmenő vezetéket két darabra vágja (T-elágazáshoz), csomóponttal"""
    w = self.wires_through(p)
    if len(w) != 1:
        raise KeyError(f'split {p}: {len(w)} vezeték megy át')
    a, b = self.wpts(w[0]); self.remove(w[0])
    self.wire(a, p); self.wire(p, b); self.junction(p)


def _lap_place(self, it, x, y, r=None, mirror=None):
    """szimbólum új helyre (a mezők együtt mozognak), új forgatás / tükrözés"""
    a = sx.first(it, 'at')
    self.move(it, x - float(a[1]), y - float(a[2]))
    if r is not None:
        a[3] = r
    m = sx.first(it, 'mirror')
    if m:
        it.remove(m)
    if mirror:
        i = it.index(a) + 1
        it.insert(i, [Sym('mirror'), Sym(mirror)])


def _lap_field(self, it, name, x, y, just=None):
    """mező új helyre; vízszintesen olvasható (álló szimbólumnál a KiCad 90°-kal tárolja)"""
    p = self.prop(it, name)
    rr = int(float(sx.first(it, 'at')[3])) % 360
    a = sx.first(p, 'at'); a[1:] = [g(x), g(y), 90 if rr % 180 == 90 else 0]
    eff = sx.first(p, 'effects')
    for j in sx.find(eff, 'justify'):
        eff.remove(j)
    if just:
        m = sx.first(it, 'mirror')
        if (rr in (90, 180)) != bool(m and str(m[1]) == 'y'):   # a KiCad ilyenkor megfordítja az igazítást
            just = {'left': 'right', 'right': 'left'}[just]
        eff.append([Sym('justify'), Sym(just)])


def _lap_remove_at(self, kinds, p, name=None):
    r = [e for e in self.at_point(kinds, p) if name is None or e[1] == name]
    if not r:
        raise KeyError(f'{kinds} @ {p}: nincs')
    for e in r:
        self.remove(e)


def _lap_pwr_at(self, p):
    """a p pontban lévő tápszimbólum (#PWR…)"""
    r = [o for o in self.pin_owner(p) if o[0].startswith('#PWR')]
    if len(r) != 1:
        raise KeyError(f'tápszimbólum @ {p}: {r}')
    return self.sym(r[0][0])


def _lap_labels_to_power(self, name, rajzolat):
    """a name címkéi helyett tápszimbólum (ugyanott, a címke irányába mutatva); visszaadja a darabszámot"""
    n = 0
    for e in self.labels(name):
        a = sx.first(e, 'at'); p = (float(a[1]), float(a[2])); d = int(float(a[3]))
        self.remove(e)
        mid = self.wires_through(p)
        if mid:                                       # a címke a vezeték közepén: a láb csak vezetékvégen kapcsolódik
            a1, b1 = self.wpts(mid[0]); self.remove(mid[0]); self.wire(a1, p); self.wire(p, b1)
        self.power(name, p, d, rajzolat=rajzolat)
        n += 1
    return n


Lap.wire_between = _lap_wire_between
Lap.unwire = _lap_unwire
Lap.split = _lap_split
Lap.place = _lap_place
Lap.field = _lap_field
Lap.remove_at = _lap_remove_at
Lap.pwr_at = _lap_pwr_at
Lap.labels_to_power = _lap_labels_to_power


def _lap_flag(self, name, p, rajzolat='VCC'):
    """PWR_FLAG a p pontban (lefelé lóg) + a hálózat tápszimbóluma felfelé – mint a kigen.flag"""
    self._ensure_lib('power:PWR_FLAG')
    minta = next(s for s in self.symbols() if str(sx.first(s, 'lib_id')[1]).startswith('power:'))
    it = copy.deepcopy(minta)
    x, y = g(p[0]), g(p[1])
    sx.first(it, 'lib_id')[1] = 'power:PWR_FLAG'
    sx.first(it, 'at')[1:] = [x, y, 180]
    sx.first(it, 'uuid')[1] = self.uid()
    ref = self.next_ref('#FLG', 1, 999)
    for pr in sx.find(it, 'property'):
        pat = sx.first(pr, 'at')
        if pr[1] == 'Reference':
            pr[2] = ref; pat[1:] = [x, g(y + 1.91), 0]
        elif pr[1] == 'Value':
            pr[2] = 'PWR_FLAG'; pat[1:] = [x, g(y + 5.08), 0]
        else:
            pat[1:] = [x, y, 0]
    for pn in sx.find(it, 'pin'):
        sx.first(pn, 'uuid')[1] = self.uid()
    for pth in self._inst_paths(it):
        sx.first(pth, 'reference')[1] = ref
    self.t.append(it)
    self.power(name, p, 90, rajzolat=rajzolat)


Lap.flag = _lap_flag
