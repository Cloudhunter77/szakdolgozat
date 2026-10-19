"""Draft KiCad schematic generator: places symbols and connects pins with labels / power symbols.

Coordinates in mm, schematic space (y down). Library symbols are flattened (extends) and embedded.
"""
import copy, uuid, sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
import sx
from sx import Sym

LIBDIR = __import__('os').path.join(__import__('os').path.dirname(__file__), 'kilib')  # build.sh tölti fel
_libcache = {}

def U():
    return str(uuid.uuid4())

NS = uuid.UUID('6f1c2a52-6d6f-4475-9c61-72697361626c')

def DU(name):
    """deterministic uuid (root sheets, sheet blocks – so the modulmag instances stay valid)"""
    return str(uuid.uuid5(NS, name))

def root_uuid(project):
    return DU(project + '/root')

def sheet_uuid(project, sheetname):
    return DU(project + '/' + sheetname)

def load_lib(name, path=None):
    if name not in _libcache:
        p = path or f'{LIBDIR}/{name}.kicad_sym'
        lib = sx.parse(open(p, encoding='utf-8').read())
        _libcache[name] = {s[1]: s for s in sx.find(lib, 'symbol')}
    return _libcache[name]

def flat_symbol(lib, name):
    syms = load_lib(lib)
    s = copy.deepcopy(syms[name])
    ext = sx.first(s, 'extends')
    if ext:
        parent = flat_symbol(lib, ext[1])
        child_props = {p[1]: p for p in sx.find(s, 'property')}
        out = [Sym('symbol'), name]
        for e in parent[2:]:
            if isinstance(e, list) and e[0] == 'property' and e[1] in child_props:
                out.append(child_props.pop(e[1]))
            elif isinstance(e, list) and e[0] == 'symbol':
                e = copy.deepcopy(e)
                e[1] = name + e[1][len(ext[1]):]
                out.append(e)
            else:
                out.append(copy.deepcopy(e))
        # child-only keys (extra properties)
        for p in child_props.values():
            out.append(p)
        s = out
    return s

def pins_of(symdef, unit=1):
    res = {}
    for sub in sx.find(symdef, 'symbol'):
        parts = sub[1].rsplit('_', 2)
        u = int(parts[-2])
        if u not in (0, unit):
            continue
        for p in sx.find(sub, 'pin'):
            at = sx.first(p, 'at')
            num = sx.first(p, 'number')[1]
            res.setdefault(num, []).append((float(at[1]), float(at[2]), int(float(at[3]))))
    return res

def rot(x, y, r):
    r %= 360
    if r == 0: return x, y
    if r == 90: return -y, x
    if r == 180: return -x, -y
    if r == 270: return y, -x
    raise ValueError(r)

def g(v):
    """snap to 0.01 mm"""
    return round(v * 100) / 100

def G(v):
    """1,27 mm-es rácsra kerekítés (minden vezetékpont és alkatrész-láb ezen van)"""
    return g(round(v / 1.27) * 1.27)


def snap(v, grid=2.54):
    return g(round(v / grid) * grid)

POWER_UP = {'+3V3', '+5V', '+24V', 'V_BUS', '+3V3A'}
POWER_DOWN = {'GND', 'GND_BUS'}

class Sheet:
    def __init__(self, title, project, paper='A3'):
        self.title, self.project, self.paper = title, project, paper
        self.uuid = root_uuid(project)
        self.extra_inst = []  # (project, path) – this sheet used as a sub-sheet elsewhere
        self.libsyms = {}
        self.items = []
        self.refs = {}
        self.power_n = 0
        self.hier = set()
        self.power_lib = {}  # net -> (lib, name)
        self.label_dx = {'Device:LED': 3.81}   # lib_id -> x offset of Reference/Value
        self.label_pos = {}  # lib_id -> ((dx, dy) Reference, (dx, dy) Value) – balra igazítva, IC-k fölé/alá
        self.ref_pos = {}    # ref -> ((dx, dy), (dx, dy)) – egyedi felülírás

    def use(self, lib_id, lib=None, name=None, libpath=None):
        if lib_id not in self.libsyms:
            l, n = lib_id.split(':')
            if libpath:
                load_lib(lib or l, libpath)
            d = flat_symbol(lib or l, name or n)
            d[1] = lib_id
            self.libsyms[lib_id] = d
        return self.libsyms[lib_id]

    def _symbol(self, lib_id, x, y, ref, value, fp='', r=0, unit=1, props=None, power=False, mirror=None, dnp=False):
        d = self.use(lib_id)
        pins = pins_of(d, unit)
        if not fp and not power:
            fp = next((pr[2] for pr in sx.find(d, 'property') if pr[1] == 'Footprint'), '')
        el = [Sym('symbol'), [Sym('lib_id'), lib_id], [Sym('at'), g(x), g(y), r]]
        if mirror:
            el.append([Sym('mirror'), Sym(mirror)])
        el += [[Sym('unit'), unit], [Sym('exclude_from_sim'), Sym('no')], [Sym('in_bom'), Sym('no' if power else 'yes')],
               [Sym('on_board'), Sym('no' if power else 'yes')], [Sym('dnp'), Sym('yes' if dnp else 'no')],
               [Sym('uuid'), U()]]
        def prop(k, v, dx, dy, hide=False, left=False):
            eff = [Sym('effects'), [Sym('font'), [Sym('size'), 1.27, 1.27]]]
            if left:
                eff.append([Sym('justify'), Sym('left')])
            # a mezők szöge a szimbólumhoz képest értendő → a forgatással ellentétesen, hogy vízszintesen olvasható legyen
            e = [Sym('property'), k, v, [Sym('at'), g(x + dx), g(y + dy), (r if not power else 0) % 180], eff]
            if hide:
                e[-1].append([Sym('hide'), Sym('yes')])
            return e
        if power:
            el.append(prop('Reference', ref, 0, -2.54, hide=True))
            el.append(prop('Value', value, 0, 2.54 if r == 0 and lib_id.endswith(('GND', 'GND_BUS')) else -2.54))
        else:
            pp0 = self.pinpoints(pins_of(d, unit), 0, 0, r)
            two_pin = len(pp0) == 2
            horizontal = two_pin and len({round(v[1], 2) for v in pp0.values()}) == 1
            pos = self.ref_pos.get(ref) or self.label_pos.get(lib_id)
            if pos:
                (rx, ry), (vx, vy) = pos
                el.append(prop('Reference', ref, rx, ry, left=True))
                el.append(prop('Value', value, vx, vy, left=True))
            elif horizontal:
                # vízszintes kétlábú: felirat a vezeték fölé / alá, középre
                el.append(prop('Reference', ref, 0, -2.54))
                el.append(prop('Value', value, 0, 2.54))
            else:
                ox = self.label_dx.get(lib_id, 2.54)
                el.append(prop('Reference', ref, ox, -1.27, left=True))
                el.append(prop('Value', value, ox, 1.27, left=True))
        el.append(prop('Footprint', fp, 0, 0, hide=True))
        el.append(prop('Datasheet', '', 0, 0, hide=True))
        for k, v in (props or {}).items():
            el.append(prop(k, v, 0, 0, hide=True))
        for num in pins:
            el.append([Sym('pin'), num, [Sym('uuid'), U()]])
        inst = [Sym('instances'), [Sym('project'), self.project,
                [Sym('path'), '/' + self.uuid, [Sym('reference'), ref], [Sym('unit'), unit]]]]
        for proj, path in self.extra_inst:
            inst.append([Sym('project'), proj, [Sym('path'), path, [Sym('reference'), ref], [Sym('unit'), unit]]])
        el.append(inst)
        self.items.append(el)
        return pins

    def pinpoints(self, pins, x, y, r, mirror=None):
        """mirror: 'y' = vízszintes tükrözés (a forgatás után), 'x' = függőleges"""
        out = {}
        for num, lst in pins.items():
            px, py, pa = lst[0]
            rx, ry = rot(px, py, r)
            a = (pa + r) % 360
            if mirror == 'y':
                rx, a = -rx, (180 - a) % 360
            elif mirror == 'x':
                ry, a = -ry, (-a) % 360
            out[num] = (g(x + rx), g(y - ry), a)
        return out

    def offsets(self, lib_id, r=0, unit=1, mirror=None):
        """pin end offsets from the symbol origin (schematic coords) for rotation r"""
        pins = pins_of(self.use(lib_id), unit)
        return self.pinpoints(pins, 0, 0, r, mirror)

    def place(self, lib_id, ref, value, nets, pin, at, r=0, **kw):
        """place a symbol so that `pin` ends exactly at `at`; returns pin points"""
        ox, oy, _ = self.offsets(lib_id, r, kw.get('unit', 1), kw.get('mirror'))[pin]
        at = (G(at[0]), G(at[1]))
        return self.comp(lib_id, ref, value, at[0] - ox, at[1] - oy, nets, r=r, **kw)

    def wire(self, *pts):
        """orthogonal wire through the points (an L corner is inserted where needed)"""
        pts = [(G(p[0]), G(p[1])) for p in pts]
        path = [pts[0]]
        for q in pts[1:]:
            a = path[-1]
            if a[0] != q[0] and a[1] != q[1]:
                path.append((q[0], a[1]))
            path.append(q)
        for a, b in zip(path, path[1:]):
            if a != b:
                self.items.append([Sym('wire'), [Sym('pts'), [Sym('xy'), a[0], a[1]], [Sym('xy'), b[0], b[1]]],
                                   [Sym('stroke'), [Sym('width'), 0], [Sym('type'), Sym('default')]], [Sym('uuid'), U()]])

    def junction(self, p):
        self.items.append([Sym('junction'), [Sym('at'), G(p[0]), G(p[1])], [Sym('diameter'), 0],
                           [Sym('color'), 0, 0, 0, 0], [Sym('uuid'), U()]])

    def rail(self, y, xs, junctions=True):
        """horizontal wire at y through the given x taps (segment by segment), junctions on inner taps"""
        y = G(y)
        xs = sorted(set(G(x) for x in xs))
        for a, b in zip(xs, xs[1:]):
            self.wire((a, y), (b, y))
        if junctions:
            for x in xs[1:-1]:
                self.junction((x, y))

    def label(self, net, p, d):
        """net marker (label / hier label / power symbol) at point p, pointing outward in direction d"""
        self.attach(net, G(p[0]), G(p[1]), d)

    def comp(self, lib_id, ref, value, x, y, nets, fp='', r=0, nc=(), props=None, dnp=False, unit=1, mirror=None):
        """nets: {pin_number: net_name or None (wired by hand)}. Every pin must appear in nets or nc.
        Returns {pin: (x, y, outward_angle)}."""
        x, y = snap(x, 1.27), snap(y, 1.27)
        pins = self._symbol(lib_id, x, y, ref, value, fp, r, props=props, dnp=dnp, unit=unit, mirror=mirror)
        pp = self.pinpoints(pins, x, y, r, mirror)
        missing = set(pp) - set(nets) - set(nc)
        extra = set(nets) - set(pp)
        if missing or extra:
            raise SystemExit(f'{ref}: missing pins {sorted(missing)} unknown pins {sorted(extra)}')
        done = set()
        for num, net in nets.items():
            px, py, pa = pp[num]
            if net is None:
                continue
            if (px, py) in done:
                continue  # stacked pins
            done.add((px, py))
            self.attach(net, px, py, (pa + 180) % 360)
        for num in nc:
            px, py, pa = pp[num]
            self.items.append([Sym('no_connect'), [Sym('at'), px, py], [Sym('uuid'), U()]])
        return {n: (px, py, (pa + 180) % 360) for n, (px, py, pa) in pp.items()}

    def attach(self, net, x, y, d):
        """put a net marker at (x,y), pointing outward in direction d (deg, ccw, 0 = right)"""
        if net in POWER_UP or net in POWER_DOWN:
            self.power(net, x, y, d)
            return
        just = Sym('left') if d in (0, 90) else Sym('right')
        if net in self.hier:
            self.items.append([Sym('hierarchical_label'), net, [Sym('shape'), Sym('bidirectional')],
                               [Sym('at'), x, y, d],
                               [Sym('effects'), [Sym('font'), [Sym('size'), 1.27, 1.27]], [Sym('justify'), just]],
                               [Sym('uuid'), U()]])
        else:
            self.items.append([Sym('label'), net, [Sym('at'), x, y, d],
                               [Sym('effects'), [Sym('font'), [Sym('size'), 1.27, 1.27]], [Sym('justify'), just, Sym('bottom')]],
                               [Sym('uuid'), U()]])

    def power(self, net, x, y, d):
        lib_id = self.power_lib.get(net, f'power:{net}')
        if net in POWER_DOWN:
            r = {270: 0, 90: 180, 0: 90, 180: 270}[d]
        else:
            r = {90: 0, 270: 180, 180: 90, 0: 270}[d]
        self.power_n += 1
        self._symbol(lib_id, x, y, f'#PWR{self.power_n:03d}', net, r=r, power=True)

    def flag(self, net, x, y):
        """PWR_FLAG on a net (with its own net marker below it)"""
        x, y = G(x), G(y)
        self.power_n += 1
        self._symbol('power:PWR_FLAG', x, y, f'#FLG{self.power_n:03d}', 'PWR_FLAG', power=True)
        self.attach(net, x, y, 270)

    def subsheet(self, name, file, x, y, w, h, left=(), right=(), page='2'):
        """hierarchical sheet block; left/right: list of (pin_name, net or None) top→bottom; None net = no_connect"""
        x, y = snap(x), snap(y)
        eff = lambda j: [Sym('effects'), [Sym('font'), [Sym('size'), 1.27, 1.27]], [Sym('justify')] + [Sym(t) for t in j]]
        el = [Sym('sheet'), [Sym('at'), x, y], [Sym('size'), w, h], [Sym('fields_autoplaced'), Sym('yes')],
              [Sym('stroke'), [Sym('width'), 0.1524], [Sym('type'), Sym('solid')]],
              [Sym('fill'), [Sym('color'), 0, 0, 0, 0.0]], [Sym('uuid'), sheet_uuid(self.project, name)],
              [Sym('property'), 'Sheetname', name, [Sym('at'), x, g(y - 0.7), 0], eff(('left', 'bottom'))],
              [Sym('property'), 'Sheetfile', file, [Sym('at'), x, g(y + h + 0.6), 0], eff(('left', 'top'))]]
        for side, lst in (('L', left), ('R', right)):
            for i, (pin, net) in enumerate(lst):
                py = g(y + 2.54 * (i + 1))
                px, a, j = (x, 180, 'left') if side == 'L' else (g(x + w), 0, 'right')
                el.append([Sym('pin'), pin, Sym('bidirectional'), [Sym('at'), px, py, a], eff((j,)), [Sym('uuid'), U()]])
                if net is None:
                    self.items.append([Sym('no_connect'), [Sym('at'), px, py], [Sym('uuid'), U()]])
                else:
                    self.attach(net, px, py, a)
        el.append([Sym('instances'), [Sym('project'), self.project, [Sym('path'), '/' + self.uuid, [Sym('page'), page]]]])
        self.items.append(el)

    def text(self, s, x, y, size=1.27):
        self.items.append([Sym('text'), s, [Sym('exclude_from_sim'), Sym('no')], [Sym('at'), x, y, 0],
                           [Sym('effects'), [Sym('font'), [Sym('size'), size, size]], [Sym('justify'), Sym('left'), Sym('bottom')]],
                           [Sym('uuid'), U()]])

    def write(self, path, date='2026-10-14', rev='v1 vázlat'):
        doc = [Sym('kicad_sch'), [Sym('version'), 20231120], [Sym('generator'), 'eeschema'],
               [Sym('generator_version'), '8.0'], [Sym('uuid'), self.uuid], [Sym('paper'), self.paper],
               [Sym('title_block'), [Sym('title'), self.title], [Sym('date'), date], [Sym('rev'), rev],
                [Sym('company'), 'Moduláris okosotthon platform – szakdolgozat']],
               [Sym('lib_symbols')] + list(self.libsyms.values())]
        doc += self.items
        doc.append([Sym('sheet_instances'), [Sym('path'), '/', [Sym('page'), '1']]])
        open(path, 'w', encoding='utf-8').write(sx.dump(doc) + '\n')


def make_ic(name, left, right, footprint='', datasheet='', desc='', ref='U', width=15.24):
    """left/right: list of (number, name, electrical_type) top→bottom; None = gap"""
    n = max(len(left), len(right))
    h = (n + 1) * 2.54
    top = h / 2
    body = [Sym('symbol'), f'{name}_0_1',
            [Sym('rectangle'), [Sym('start'), g(-width / 2), g(top)], [Sym('end'), g(width / 2), g(-top)],
             [Sym('stroke'), [Sym('width'), 0.254], [Sym('type'), Sym('default')]],
             [Sym('fill'), [Sym('type'), Sym('background')]]]]
    pins = [Sym('symbol'), f'{name}_1_1']
    for side, lst in (('L', left), ('R', right)):
        for i, pd in enumerate(lst):
            if pd is None:
                continue
            num, pname, et = pd
            y = g(top - 2.54 * (i + 1))
            x, a = (g(-width / 2 - 2.54), 0) if side == 'L' else (g(width / 2 + 2.54), 180)
            pins.append([Sym('pin'), Sym(et), Sym('line'), [Sym('at'), x, y, a], [Sym('length'), 2.54],
                         [Sym('name'), pname, [Sym('effects'), [Sym('font'), [Sym('size'), 1.27, 1.27]]]],
                         [Sym('number'), num, [Sym('effects'), [Sym('font'), [Sym('size'), 1.27, 1.27]]]]])
    def prop(k, v, y, hide):
        e = [Sym('property'), k, v, [Sym('at'), 0, g(y), 0], [Sym('effects'), [Sym('font'), [Sym('size'), 1.27, 1.27]]]]
        if hide:
            e[-1].append([Sym('hide'), Sym('yes')])
        return e
    return [Sym('symbol'), name, [Sym('exclude_from_sim'), Sym('no')], [Sym('in_bom'), Sym('yes')],
            [Sym('on_board'), Sym('yes')],
            prop('Reference', ref, top + 1.27, False), prop('Value', name, -top - 1.27, False),
            prop('Footprint', footprint, 0, True), prop('Datasheet', datasheet, 0, True),
            prop('Description', desc, 0, True), body, pins]
