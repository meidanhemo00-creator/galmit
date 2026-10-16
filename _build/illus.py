"""Generates the technical isometric illustrations used across the landing page.

Every drawing is projected from simple 3D geometry so all products share one
camera, one line weight and one shading model. Output is inline-ready SVG that
is styled by classes in css/main.css (.il-*).

Run:  python3 _build/illus.py   (writes _build/out/*.svg, then build.py inlines them)
"""
import math, os, re

C30, S30 = math.cos(math.radians(30)), 0.5
OUT = os.path.join(os.path.dirname(__file__), 'out')


def f(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith('.0') else s


class Scene:
    def __init__(self, pid, k, ox, oy):
        self.pid, self.k, self.ox, self.oy = pid, k, ox, oy
        self.defs, self.layers = [], {n: [] for n in ('floor', 'shadow', 'xray', 'back', 'body', 'detail', 'glow', 'anno')}
        self.n = 0
        self.groups = []
        self.track = True
        self.bb = [1e9, 1e9, -1e9, -1e9]

    # projection ------------------------------------------------------------
    def P(self, x, y, z):
        X, Y = self.ox + (x - y) * C30 * self.k, self.oy + (x + y) * S30 * self.k - z * self.k
        if self.track:
            self.ext(X, Y)
        return (X, Y)

    def ext(self, X, Y, pad=0):
        b = self.bb
        b[0] = min(b[0], X - pad); b[1] = min(b[1], Y - pad); b[2] = max(b[2], X + pad); b[3] = max(b[3], Y + pad)

    def pt(self, p):
        X, Y = self.P(*p)
        return f"{f(X)} {f(Y)}"

    def uid(self, s):
        self.n += 1
        return f"{self.pid}-{s}{self.n}"

    # path helpers ----------------------------------------------------------
    def path(self, segs, close=False):
        """segs: list of ('M',p) | ('L',p) | ('Q',c,p) | ('C',c1,c2,p)"""
        out = []
        for s in segs:
            op = s[0]
            out.append(op + ' ' + ' '.join(self.pt(p) for p in s[1:]))
        return ' '.join(out) + (' Z' if close else '')

    def add(self, layer, d, cls, extra=''):
        self.layers[layer].append(f'<path class="{cls}" d="{d}"{extra}/>')

    def raw(self, layer, s):
        self.layers[layer].append(s)

    def ellipse_z(self, cx, cy, z, r, n=48):
        pts = [(cx + r * math.cos(t), cy + r * math.sin(t), z) for t in (2 * math.pi * i / n for i in range(n))]
        return 'M ' + ' L '.join(self.pt(p) for p in pts) + ' Z'

    def ellipse_z_half(self, cx, cy, z, r, front=True, n=24):
        # front half of a horizontal circle: angles where (cos+sin) > 0
        a0 = -math.pi / 4 if front else 3 * math.pi / 4
        pts = [(cx + r * math.cos(a0 + math.pi * i / n), cy + r * math.sin(a0 + math.pi * i / n), z) for i in range(n + 1)]
        return 'M ' + ' L '.join(self.pt(p) for p in pts)

    # materials -------------------------------------------------------------
    def weave(self, axis_u, axis_v, step=0.32, cls='il-weave'):
        """pattern aligned to a 3D face spanned by unit axes u, v"""
        pid = self.uid('wv')
        ux, uy = (axis_u[0] - axis_u[1]) * C30 * self.k, (axis_u[0] + axis_u[1]) * S30 * self.k - axis_u[2] * self.k
        vx, vy = (axis_v[0] - axis_v[1]) * C30 * self.k, (axis_v[0] + axis_v[1]) * S30 * self.k - axis_v[2] * self.k
        s = step
        self.defs.append(
            f'<pattern id="{pid}" width="1" height="1" patternUnits="userSpaceOnUse" '
            f'patternTransform="matrix({f(ux*s*10)/10 if False else round(ux*s,3)} {round(uy*s,3)} {round(vx*s,3)} {round(vy*s,3)} 0 0)">'
            f'<path class="{cls}" d="M0 .25 H1 M0 .75 H1" /><path class="{cls} il-weave-v" d="M.25 0 V.5 M.75 .5 V1" /></pattern>')
        return pid

    def grad(self, stops, x1=0, y1=0, x2=0, y2=1):
        gid = self.uid('g')
        st = ''.join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in stops)
        self.defs.append(f'<linearGradient id="{gid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{st}</linearGradient>')
        return gid

    # primitives ------------------------------------------------------------
    def floor_grid(self, x0, x1, y0, y1, step=1.0):
        self.track = False
        d = []
        x = x0
        while x <= x1 + 1e-6:
            d.append(f"M {self.pt((x, y0, 0))} L {self.pt((x, y1, 0))}")
            x += step
        y = y0
        while y <= y1 + 1e-6:
            d.append(f"M {self.pt((x0, y, 0))} L {self.pt((x1, y, 0))}")
            y += step
        self.add('floor', ' '.join(d), 'il-grid')
        self.track = True

    def shadow(self, cx, cy, rx, ry):
        X, Y = self.P(cx, cy, 0)
        hid = self.uid('hs')
        self.defs.append(f'<pattern id="{hid}" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(-30)"><path class="il-hatch" d="M0 0 V5"/></pattern>')
        self.raw('shadow', f'<ellipse class="il-shadow" cx="{f(X)}" cy="{f(Y)}" rx="{f(rx*self.k)}" ry="{f(ry*self.k)}" fill="url(#{hid})"/>')

    def marker(self, p, label, dx=0, dy=0):
        X, Y = self.P(*p)
        mx, my = X + dx, Y + dy
        self.ext(mx, my, 13)
        if dx or dy:
            self.raw('anno', f'<path class="il-lead" d="M {f(X)} {f(Y)} L {f(mx)} {f(my)}"/>')
        self.raw('anno', f'<circle class="il-dot" cx="{f(X)}" cy="{f(Y)}" r="2.2"/>'
                         f'<g class="il-mark" transform="translate({f(mx)} {f(my)})"><circle r="10"/><text y="3.6">{label}</text></g>')

    def dim(self, a, b, off, label, tick=0.35):
        """dimension line between 3D points a,b displaced by 3D vector off"""
        a2 = tuple(a[i] + off[i] for i in range(3)); b2 = tuple(b[i] + off[i] for i in range(3))
        n = math.sqrt(sum(o * o for o in off)) or 1
        u = tuple(o / n * tick for o in off)
        d = (f"M {self.pt(a2)} L {self.pt(b2)} "
             f"M {self.pt(tuple(a2[i]-u[i] for i in range(3)))} L {self.pt(tuple(a2[i]+u[i] for i in range(3)))} "
             f"M {self.pt(tuple(b2[i]-u[i] for i in range(3)))} L {self.pt(tuple(b2[i]+u[i] for i in range(3)))}")
        self.add('anno', d, 'il-dim')
        m = tuple((a2[i] + b2[i]) / 2 + u[i] * 2.2 for i in range(3))
        X, Y = self.P(*m)
        self.raw('anno', f'<text class="il-dimtext" x="{f(X)}" y="{f(Y+3)}">{label}</text>')

    # products --------------------------------------------------------------
    def box_faces(self, W, D, H, x0=0, y0=0, z0=0, bulge=0.0, sag=0.0, cls=('il-face-r', 'il-face-l', 'il-face-t'), weave=True, draw_top=True):
        o = (x0, y0, z0)
        A = lambda x, y, z: (o[0] + x, o[1] + y, o[2] + z)
        b = bulge
        Bb, Cb, Db = A(W, 0, 0), A(W, D, 0), A(0, D, 0)
        Bt, Ct, Dt, At = A(W, 0, H), A(W, D, H), A(0, D, H), A(0, 0, H)
        # right face (x=W)
        r = self.path([('M', Bb), ('Q', A(W + b, D / 2, -sag), Cb), ('L', Ct), ('Q', A(W + b * .6, D / 2, H + sag * .4), Bt),
                       ('Q', A(W + b * .7, -b * .7, H / 2), Bb)], True)
        l = self.path([('M', Cb), ('Q', A(W / 2, D + b, -sag), Db), ('Q', A(-b * .7, D + b * .7, H / 2), Dt),
                       ('Q', A(W / 2, D + b * .6, H + sag * .4), Ct), ('L', Cb)], True)
        t = self.path([('M', Bt), ('Q', A(W + b * .6, D / 2, H + sag * .4), Ct), ('Q', A(W / 2, D + b * .6, H + sag * .4), Dt),
                       ('Q', A(-b * .5, D / 2, H + sag * .4), At), ('Q', A(W / 2, -b * .5, H + sag * .4), Bt)], True)
        gr = self.grad([(0, '#efe4d2', .52), (1, '#bfa98c', .30)], 0, 0, 1, 1)
        gl = self.grad([(0, '#cdb999', .36), (1, '#7d6850', .22)], 1, 0, 0, 1)
        gt = self.grad([(0, '#fbf3e6', .6), (1, '#e4d7c3', .38)], 0, 0, 1, 1)
        self.add('body', r, f'{cls[0]} il-draw', f' pathLength="1"')
        self.add('body', l, f'{cls[1]} il-draw', f' pathLength="1"')
        if draw_top:
            self.add('body', t, f'{cls[2]} il-draw', f' pathLength="1"')
        if weave:
            wr = self.weave((0, 1, 0), (0, 0, -1)); wl = self.weave((1, 0, 0), (0, 0, -1))
            self.add('body', r, 'il-tex', f' fill="url(#{wr})"')
            self.add('body', l, 'il-tex', f' fill="url(#{wl})"')
            if draw_top:
                wt = self.weave((1, 0, 0), (0, 1, 0))
                self.add('body', t, 'il-tex', f' fill="url(#{wt})"')
        # hidden back edges (x-ray)
        Ab = A(0, 0, 0)
        self.add('xray', self.path([('M', Ab), ('L', Bb), ('M', Ab), ('L', Db), ('M', Ab), ('L', At)]), 'il-hidden')
        return dict(Bb=Bb, Cb=Cb, Db=Db, Bt=Bt, Ct=Ct, Dt=Dt, At=At, A=A)

    def strap_loop(self, p1, p2, top1, top2, w=0.32, tail=2.6):
        """cross-corner lifting loop: arch from p1 to p2 with cubic controls top1/top2, plus sewn tails"""
        inner1 = (top1[0], top1[1], top1[2] - w * 1.6); inner2 = (top2[0], top2[1], top2[2] - w * 1.6)
        p1i = (p1[0], p1[1], p1[2] - 0.05); p2i = (p2[0], p2[1], p2[2] - 0.05)
        d = self.path([('M', p1), ('C', top1, top2, p2), ('L', p2i), ('C', inner2, inner1, p1i)], True)
        self.add('detail', d, 'il-strap il-draw', ' pathLength="1"')
        self.add('glow', self.path([('M', p1), ('C', top1, top2, p2)]), 'il-glowline il-draw', ' pathLength="1"')

    def strap_tail(self, top, axis, z1):
        """vertical sewn strap tail on a face: top point, axis = in-face horizontal unit, to z1, with box-X stitch"""
        w = 0.55
        a = top; b = (top[0] + axis[0] * w, top[1] + axis[1] * w, top[2])
        a2 = (a[0], a[1], z1); b2 = (b[0], b[1], z1)
        self.add('detail', self.path([('M', a), ('L', b), ('L', b2), ('L', a2)], True), 'il-strapface')
        zz = z1 + 0.25; zt = z1 + 1.1
        q = lambda p, z: (p[0], p[1], z)
        x = self.path([('M', q(a, zz)), ('L', q(b, zz)), ('L', q(b, zt)), ('L', q(a, zt)), ('Z',),])
        self.add('glow', self.path([('M', q(a, zz)), ('L', q(b, zt)), ('M', q(b, zz)), ('L', q(a, zt)),
                                    ('M', q(a, zz)), ('L', q(b, zz)), ('L', q(b, zt)), ('L', q(a, zt)), ('L', q(a, zz))]), 'il-stitch')

    def half_pts(self, cx, cy, z, r, n=24):
        """front half of a horizontal circle, from the right silhouette point to the left one"""
        a0 = -math.pi / 4
        return [(cx + r * math.cos(a0 + math.pi * i / n), cy + r * math.sin(a0 + math.pi * i / n), z) for i in range(n + 1)]

    def cylinder(self, cx, cy, z0, h, r, cls='il-spout', xray=False, r_top=None):
        rt = r if r_top is None else r_top
        lay = 'xray' if xray else 'detail'
        bot = self.half_pts(cx, cy, z0, r); top = self.half_pts(cx, cy, z0 + h, rt)
        if xray:
            self.add(lay, self.ellipse_z(cx, cy, z0, r) + ' ' + self.ellipse_z(cx, cy, z0 + h, rt) +
                     f" M {self.pt(bot[0])} L {self.pt(top[0])} M {self.pt(bot[-1])} L {self.pt(top[-1])}", 'il-hidden')
            return
        g = self.grad([(0, '#f2e8d8', .36), (1, '#a8916f', .16)], 0, 0, 1, 0)
        side = 'M ' + ' L '.join(self.pt(p) for p in bot) + ' L ' + ' L '.join(self.pt(p) for p in reversed(top)) + ' Z'
        self.add(lay, side, f'{cls} il-draw', f' pathLength="1"')
        self.add(lay, self.ellipse_z(cx, cy, z0 + h, rt), f'{cls}-top il-draw', ' pathLength="1"')

    def logo_slot(self, origin, u, v, w, h):
        """An empty <image> mapped onto a 3D face: origin = top-start corner, u/v = unit axes along the face."""
        ox, oy = self.P(*origin)
        k = self.k
        pu = ((u[0] - u[1]) * C30 * k * w, (u[0] + u[1]) * S30 * k * w - u[2] * k * w)
        pv = ((v[0] - v[1]) * C30 * k * h, (v[0] + v[1]) * S30 * k * h - v[2] * k * h)
        self.raw('glow', f'<g class="il-logo" transform="matrix({pu[0]:.2f} {pu[1]:.2f} {pv[0]:.2f} {pv[1]:.2f} {ox:.1f} {oy:.1f})">'
                         f'<image width="1" height="1" preserveAspectRatio="xMidYMid meet"/></g>')

    # composite products ----------------------------------------------------
    def bulk_bag(self, x0=0, y0=0, W=10, D=10, H=11, loops=True, spout=False, discharge=False, dims=False, marks=False, pallet=False):
        z0 = 0
        if pallet:
            self.pallet(x0 - 0.4, y0 - 0.4, W + 0.8, D + 0.8)
            z0 = 1.1
        fc = self.box_faces(W, D, H, x0, y0, z0, bulge=0.55, sag=0.35)
        A = fc['A']
        # top hem + corner seams (stitch)
        self.add('detail', self.path([('M', A(W + .1, 0.2, H - .7)), ('Q', A(W + .45, D / 2, H - .6), A(W, D, H - .7)),
                                      ('Q', A(W / 2, D + .45, H - .6), A(0.2, D + .1, H - .7))]), 'il-seam')
        self.add('detail', self.path([('M', A(W, D - .35, H - .1)), ('L', A(W, D - .35, .3)), ('M', A(W - .35, D, H - .1)), ('L', A(W - .35, D, .3))]), 'il-seam')
        if loops:
            e = 1.7
            # front corner C
            self.strap_loop(A(W, D - e, H - .05), A(W - e, D, H - .05), A(W + .9, D - e * .5, H + 4.6), A(W - e * .5, D + .9, H + 4.6), w=.5)
            # right corner B: loop sewn along the right face
            self.strap_loop(A(W + .05, .35, H - .05), A(W + .05, .35 + 2 * e, H - .05), A(W + .25, .1, H + 4.3), A(W + .25, .6 + 2 * e, H + 4.3), w=.5)
            # left corner D: loop sewn along the left face
            self.strap_loop(A(.35, D + .05, H - .05), A(.35 + 2 * e, D + .05, H - .05), A(.1, D + .25, H + 4.3), A(.6 + 2 * e, D + .25, H + 4.3), w=.5)
            self.strap_tail(A(W + .05, .35, H - .05), (0, 1, 0), H - 3.6)
            self.strap_tail(A(.35, D + .05, H - .05), (1, 0, 0), H - 3.6)
            # back corner A (partly hidden)
            self.add('back', self.path([('M', A(e, -.05, H)), ('C', A(e * .5, -.9, H + 4.3), A(-.9, e * .5, H + 4.3), A(-.05, e, H))]), 'il-strap-back')
            self.strap_tail(A(W, D - e - .1, H - .05), (0, -1, 0), H - 4.2)
            self.strap_tail(A(W - e - .1, D, H - .05), (-1, 0, 0), H - 4.2)
        if spout:
            self.cylinder(x0 + W / 2, y0 + D / 2, z0 + H + .25, 2.6, 1.7)
        if discharge:
            self.cylinder(x0 + W / 2, y0 + D / 2, z0 - 1.9, 1.9, 1.5, xray=True)
        if dims:
            self.dim(A(0, D, 0), A(0, D, H), (-0.0, 1.8, 0), 'H')
            self.dim(A(0, D, 0), A(W, D, 0), (0, 2.2, 0), 'W')
            self.dim(A(W, 0, 0), A(W, D, 0), (2.2, 0, 0), 'D')
        if marks:
            self.marker(A(W + .7, D - e * .5, H + 3.4), 'A', 44, -10)
            self.marker(A(W * .55, D + .2, H * .55), 'B', -54, 18)
        self.shadow(x0 + W / 2 + .5, y0 + D / 2 + .5, W * 1.0, W * .42)
        return fc

    def pallet(self, x0, y0, W, D, h=1.1):
        self.box_faces(W, D, h, x0, y0, 0, weave=False, cls=('il-wood-r', 'il-wood-l', 'il-wood-t'))
        A = lambda x, y, z: (x0 + x, y0 + y, z)
        # slats on top + runner gaps
        for i in range(1, 7):
            y = D * i / 7
            self.add('detail', self.path([('M', A(0, y, h)), ('L', A(W, y, h))]), 'il-hair')
        for fx in (0.18, 0.5, 0.82):
            gx = W * fx
            self.add('detail', self.path([('M', A(gx - .7, D, .15)), ('L', A(gx + .7, D, .15)), ('L', A(gx + .7, D, .7)), ('L', A(gx - .7, D, .7)), ('Z',)]), 'il-gap')
            gy = D * fx
            self.add('detail', self.path([('M', A(W, gy - .7, .15)), ('L', A(W, gy + .7, .15)), ('L', A(W, gy + .7, .7)), ('L', A(W, gy - .7, .7)), ('Z',)]), 'il-gap')

    def pillow(self, cx, cy, z, L=11, Wd=6.2, t=2.3, rot=0.0, r=1.0, ends=True):
        ca, sa = math.cos(rot), math.sin(rot)
        def R(x, y, zz):
            x -= L / 2; y -= Wd / 2
            return (cx + x * ca - y * sa, cy + x * sa + y * ca, zz)
        def outline(zz, inset=0.0, pinch=0.0):
            segs = []
            pts = [(r, inset), (L - r, inset), (L - inset, r), (L - inset, Wd - r), (L - r, Wd - inset), (r, Wd - inset), (inset, Wd - r), (inset, r)]
            corners = [(L - inset, inset), (L - inset, Wd - inset), (inset, Wd - inset), (inset, inset)]
            segs.append(('M', R(*pts[0], zz)))
            for i in range(4):
                a, b = pts[2 * i], pts[2 * i + 1]
                mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
                segs.append(('Q', R(mid[0], mid[1], zz + pinch), R(*b, zz)))
                nxt = pts[(2 * i + 2) % 8]
                segs.append(('Q', R(*corners[i], zz - pinch * .3), R(*nxt, zz)))
            return self.path(segs, True)
        gb = self.grad([(0, '#7c6650', 1), (1, '#3e2e20', 1)], 0, 0, 0, 1)
        gt = self.grad([(0, '#d8c9b1', 1), (1, '#9a876d', 1)], 0, 0, 1, 1)
        self.add('body', outline(z, 0, -0.2) + ' ' , 'il-face-l il-draw', f' pathLength="1"')
        top = outline(z + t, 0.2, 0.4)
        mid = outline(z + t * .45, -0.18, 0.2)
        self.add('body', mid, 'il-face-l', f'')
        self.add('body', top, 'il-face-t il-draw', f' pathLength="1"')
        wv = self.weave((ca, sa, 0), (-sa, ca, 0), step=0.28)
        self.add('body', top, 'il-tex', f' fill="url(#{wv})"')
        if ends:
            for x in (0.7, L - 0.7):
                self.add('glow', self.path([('M', R(x, 0.5, z + t - .05)), ('L', R(x, Wd - 0.5, z + t - .05))]), 'il-stitch')

    def block_bag(self, x0, y0, W, D, H, kind='paper', z0=0, handle=False, valve=False, dims=False, marks=False, printarea=True):
        weave = kind != 'paper'
        cls = ('il-kraft-r', 'il-kraft-l', 'il-kraft-t') if kind == 'paper' else ('il-face-r', 'il-face-l', 'il-face-t')
        fc = self.box_faces(W, D, H, x0, y0, z0, bulge=0.12 if kind == 'paper' else 0.25, weave=weave, cls=cls, draw_top=True)
        A = fc['A']
        if kind == 'paper':
            # folded top: flap over the front (y=D) face + gusset folds on the side (x=W) face
            self.add('detail', self.path([('M', A(0, D + .06, H)), ('L', A(W, D + .06, H)), ('L', A(W, D + .06, H - 1.5)), ('L', A(0, D + .06, H - 1.5)), ('Z',)]), 'il-kraft-flap')
            self.add('glow', self.path([('M', A(0.2, D + .07, H - 1.1)), ('L', A(W - .2, D + .07, H - 1.1))]), 'il-stitch')
            self.add('detail', self.path([('M', A(W, D / 2, H)), ('L', A(W, D / 2, H * .18)), ('L', A(W, 0.05, 0.05)), ('M', A(W, D / 2, H * .18)), ('L', A(W, D - .05, 0.05))]), 'il-fold')
            fib = self.uid('fib')
            self.defs.append(f'<pattern id="{fib}" width="9" height="9" patternUnits="userSpaceOnUse"><path class="il-fiber" d="M1 2 l3 .6 M6 5 l2 -.8 M2 7.5 l2.4 .3 M7 1 l1.4 1"/></pattern>')
            for key in ('r', 'l'):
                pass
        if printarea:
            pz0, pz1 = H * .22 + z0, H * .62 + z0
            self.add('detail', self.path([('M', A(W * .14, D + .02, pz0 - z0)), ('L', A(W * .86, D + .02, pz0 - z0)), ('L', A(W * .86, D + .02, pz1 - z0)), ('L', A(W * .14, D + .02, pz1 - z0)), ('Z',)]), 'il-print')
        if handle:
            hz = H - 1.3
            hw, hh = W * .34, .55
            cxh = W / 2
            self.add('detail', self.path([('M', A(cxh - hw / 2, D + .02, hz)), ('L', A(cxh + hw / 2, D + .02, hz)), ('Q', A(cxh + hw / 2 + .3, D + .02, hz + hh / 2), A(cxh + hw / 2, D + .02, hz + hh)),
                                          ('L', A(cxh - hw / 2, D + .02, hz + hh)), ('Q', A(cxh - hw / 2 - .3, D + .02, hz + hh / 2), A(cxh - hw / 2, D + .02, hz)), ('Z',)]), 'il-hole il-draw', ' pathLength="1"')
            self.add('detail', self.path([('M', A(0.05, D + .02, H - .45)), ('L', A(W - .05, D + .02, H - .45)), ('M', A(W, D - .05, H - .45)), ('L', A(W, 0.05, H - .45))]), 'il-seam')
        if valve:
            vx = W * .22
            self.add('detail', self.path([('M', A(vx - 1.3, D + .02, H)), ('L', A(vx - 1.0, D + 2.0, H + 1.2)), ('L', A(vx + 1.3, D + 2.0, H + 1.2)), ('L', A(vx + 1.6, D + .02, H)), ('Z',)]), 'il-valve il-draw', ' pathLength="1"')
            self.add('glow', self.path([('M', A(vx - 1.0, D + 2.0, H + 1.2)), ('L', A(vx + 1.3, D + 2.0, H + 1.2))]), 'il-glowline')
            self.add('detail', self.path([('M', A(vx - 1.15, D + 1.0, H + .6)), ('L', A(vx + 1.45, D + 1.0, H + .6))]), 'il-fold')
            for zz in (0.9, H - 0.9):
                self.add('detail', self.path([('M', A(0.05, D, zz)), ('L', A(W, D, zz)), ('L', A(W, 0.05, zz))]), 'il-fold')
        if dims:
            self.dim(A(0, D, 0), A(0, D, H), (0, 1.6, 0), 'H')
            self.dim(A(0, D, 0), A(W, D, 0), (0, 1.9, 0), 'W')
        self.shadow(x0 + W / 2 + .4, y0 + D / 2 + .4, W * .95, W * .4)
        return fc

    def cone(self, cx, cy, z0, h=5.2, r0=1.7, r1=0.75):
        self.cylinder(cx, cy, z0, h, r0, cls='il-face-r', r_top=r1)
        for i in range(1, 10):
            zz = z0 + h * i / 10
            rr = r0 + (r1 - r0) * i / 10
            self.add('detail', 'M ' + ' L '.join(self.pt(p) for p in self.half_pts(cx, cy, zz, rr)), 'il-wind')
        self.cylinder(cx, cy, z0 + h, .9, .38)
        self.shadow(cx + .2, cy + .2, 2.2, 1.0)

    # output ----------------------------------------------------------------
    def flush(self):
        """close the current object so later objects paint over it (painter's order)"""
        body = ''.join(f'<g class="il-{n}">{"".join(v)}</g>' for n, v in self.layers.items() if v)
        if body:
            self.groups.append(body)
        self.layers = {n: [] for n in self.layers}

    def svg(self, vb=None, title=None, cls='il', pad=26):
        if vb is None or True:
            b = self.bb
            vb = f"{f(b[0]-pad)} {f(b[1]-pad)} {f(b[2]-b[0]+2*pad)} {f(b[3]-b[1]+2*pad)}"
        self.flush()
        body = ''.join(self.groups)
        t = f'<title>{title}</title>' if title else ''
        role = 'role="img"' if title else 'aria-hidden="true" focusable="false"'
        return f'<svg class="{cls}" viewBox="{vb}" {role} xmlns="http://www.w3.org/2000/svg">{t}<defs>{"".join(self.defs)}</defs>{body}</svg>'


def write(name, svg):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name + '.svg'), 'w') as fh:
        fh.write(svg)
    print(name, len(svg))


# ---------------------------------------------------------------- scenes ----
def scene_bulk(pid='ib', marks=True, dims=True):
    s = Scene(pid, 15, 300, 250)
    s.floor_grid(-6, 18, -6, 18, 2)
    s.bulk_bag(0, 0, 10, 10, 11, dims=dims, marks=marks)
    return s.svg('40 20 520 420', 'איור טכני של שק ענק עם לולאות הרמה')


def scene_pp(pid='ip'):
    s = Scene(pid, 17, 300, 250)
    s.floor_grid(-6, 18, -6, 18, 2)
    s.shadow(6, 4, 9, 3.6)
    for i, r in enumerate([0.0, 0.07, -0.06, 0.03]):
        s.pillow(6 + (i % 2) * .2, 4, i * 2.05, rot=r)
    s.dim((0.5, 7.1, 0), (11.5, 7.1, 0), (0, 1.9, 0), 'L')
    s.marker((6.0, 4.0, 8.4), 'A', -40, -40)
    s.marker((10.9, 4.0, 8.3), 'B', 50, -30)
    return s.svg('40 40 520 400', 'איור טכני של ערימת שקי פוליפרופילן ארוגים')


def scene_paper(pid='ia'):
    s = Scene(pid, 20, 290, 300)
    s.floor_grid(-6, 16, -6, 16, 2)
    s.block_bag(1.5, 2.0, 5.2, 3.2, 10.5, 'paper', dims=True)
    s.block_bag(8.5, 1.0, 5.2, 3.2, 10.5, 'paper', printarea=True)
    s.marker((4.1, 5.25, 10.4), 'A', -44, -30)
    s.marker((6.7, 3.6, 5.0), 'B', 52, 10)
    return s.svg('40 20 520 420', 'איור טכני של שקיות נייר 1 ק״ג עם תחתית מרובעת וקפל עליון')


def scene_coal(pid='ic'):
    s = Scene(pid, 17, 300, 300)
    s.floor_grid(-6, 20, -6, 16, 2)
    s.block_bag(0.5, 3.0, 6.0, 2.2, 11.0, 'woven', handle=True, dims=True)
    s.block_bag(8.2, 2.5, 5.0, 1.9, 8.6, 'woven', handle=True)
    s.block_bag(14.6, 2.0, 3.9, 1.6, 6.4, 'woven', handle=True)
    s.marker((3.5, 5.2, 9.9), 'A', -46, -24)
    return s.svg('30 0 540 420', 'איור טכני של שקי פחם בשלושה גדלים עם ידית אחיזה')


def scene_special(pid='iv'):
    s = Scene(pid, 18, 290, 290)
    s.floor_grid(-6, 18, -6, 16, 2)
    s.block_bag(0.5, 1.0, 8.5, 4.6, 9.0, 'woven', valve=True, printarea=False, dims=True)
    s.cone(13.5, 3.5, 0)
    s.marker((1.9, 7.6, 10.2), 'A', -40, -34)
    s.marker((13.5, 3.5, 5.6), 'B', 46, -26)
    return s.svg('30 0 540 420', 'איור טכני של שק פייה עם תחתית מרובעת, לצד גליל חוט תפירה')


def scene_tile(kind, pid, logo=False):
    """compact versions for the category strip"""
    s = Scene(pid, 12, 200, 170)
    if kind == 'bulk':
        s.k = 10.5; s.bulk_bag(0, 0, 10, 10, 11, discharge=False)
        if logo: s.logo_slot((1.6, 10.12, 8.2), (1, 0, 0), (0, 0, -1), 6.8, 4.6)
        return s.svg('70 20 260 230')
    if kind == 'pp':
        s.k = 13; s.shadow(6, 4, 9, 3.6)
        for i, (z, r) in enumerate([(0, 0), (2.05, .07), (4.1, 0)]):
            s.pillow(6, 4, z, rot=r); s.flush()
        if logo: s.logo_slot((2.2, 1.9, 4.1 + 2.3 + .05), (1, 0, 0), (0, 1, 0), 7.6, 4.2)
        return s.svg('70 30 260 210')
    if kind == 'paper':
        s.k = 13; s.block_bag(1.5, 2, 5.2, 3.2, 10.5, 'paper'); s.flush(); s.block_bag(8.5, 1, 5.2, 3.2, 10.5, 'paper')
        if logo: s.logo_slot((8.5 + 5.2 * .16, 4.22, 10.5 * .6), (1, 0, 0), (0, 0, -1), 5.2 * .68, 10.5 * .36)
        return s.svg('70 10 260 230')
    if kind == 'coal':
        s.k = 11.5; s.block_bag(0.5, 3, 6, 2.2, 11, 'woven', handle=True); s.flush(); s.block_bag(8.2, 2.5, 5, 1.9, 8.6, 'woven', handle=True); s.flush(); s.block_bag(14.6, 2, 3.9, 1.6, 6.4, 'woven', handle=True)
        if logo: s.logo_slot((0.5 + 6 * .16, 5.22, 11 * .6), (1, 0, 0), (0, 0, -1), 6 * .68, 11 * .36)
        return s.svg('60 0 300 230')
    if kind == 'special':
        s.k = 12; s.block_bag(0.5, 1, 8.5, 4.6, 9, 'woven', valve=True, printarea=False); s.cone(13.5, 3.5, 0)
        return s.svg('60 20 280 220')


def scene_panorama(pid='iw'):
    s = Scene(pid, 11, 560, 160)
    s.floor_grid(-12, 50, -8, 30, 2)
    s.flush()
    # back to front (increasing x + y)
    for i in range(3):
        s.bulk_bag(i * 14, -4, 10, 10, 11, pallet=True, discharge=False); s.flush()
    s.block_bag(44, 2, 6.5, 3.6, 7.0, 'woven', valve=True, printarea=False); s.flush()
    s.cone(49, 9, 0, h=4.2, r0=1.4, r1=.6); s.flush()
    s.pallet(2, 13.5, 11, 7); s.flush()
    for z, r in [(1.1, 0), (3.15, .05), (5.2, -.04)]:
        s.pillow(7.5, 17, z, rot=r); s.flush()
    for j in range(4):
        s.block_bag(18 + j * 3.4, 15.5, 2.6, 1.7, 5.4, 'paper', printarea=False); s.flush()
    for j, (w, h) in enumerate([(3.2, 6.2), (2.6, 4.8), (2.1, 3.6)]):
        s.block_bag(33 + j * 4.1, 14 + j * .3, w, 1.2, h, 'woven', handle=True, printarea=False); s.flush()
    return s.svg()


def scene_loop(pid='il'):
    """orthographic close-up of a lifting loop sewn to the fabric (front view)"""
    W, H = 400, 480
    wv = f'{pid}-wv'
    parts = [f'<defs><pattern id="{wv}" width="8" height="8" patternUnits="userSpaceOnUse"><path class="il-weave" d="M0 2 H8 M0 6 H8"/><path class="il-weave il-weave-v" d="M2 0 V4 M6 4 V8"/></pattern>'
             f'<linearGradient id="{pid}-g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#efe4d2" stop-opacity=".3"/><stop offset="1" stop-color="#8f775c" stop-opacity=".12"/></linearGradient>'
             f'<linearGradient id="{pid}-s" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#e9dcc6" stop-opacity=".55"/><stop offset=".5" stop-color="#fbf3e6" stop-opacity=".7"/><stop offset="1" stop-color="#c9b597" stop-opacity=".5"/></linearGradient></defs>']
    parts.append(f'<g class="il-body"><rect class="il-face-r il-draw" pathLength="1" x="40" y="250" width="320" height="210"/><rect class="il-tex" x="40" y="250" width="320" height="210" fill="url(#{wv})"/></g>')
    parts.append('<g class="il-detail">'
                 '<path class="il-seam" d="M40 270 H360"/>'
                 f'<path class="il-strap il-draw" pathLength="1" d="M150 430 V170 C150 60 250 60 250 170 V430 H212 V176 C212 120 188 120 188 176 V430 Z"/>'
                 '<path class="il-hair" d="M160 430 V172 C160 80 240 80 240 172 V430"/>'
                 '</g>')
    parts.append('<g class="il-glow">'
                 '<path class="il-stitch" d="M156 300 H244 V390 H156 Z M156 300 L244 390 M244 300 L156 390"/>'
                 '<path class="il-stitch" d="M156 408 H244"/>'
                 '<path class="il-glowline il-draw" pathLength="1" d="M150 170 C150 60 250 60 250 170"/>'
                 '</g>')
    parts.append('<g class="il-anno">'
                 '<path class="il-dim" d="M150 470 H250 M150 464 V476 M250 464 V476"/><text class="il-dimtext" x="200" y="466">W</text>'
                 '<path class="il-lead" d="M244 345 L310 300"/><circle class="il-dot" cx="244" cy="345" r="2.2"/><g class="il-mark" transform="translate(320 292)"><circle r="10"/><text y="3.6">X</text></g>'
                 '<path class="il-lead" d="M200 84 L120 60"/><circle class="il-dot" cx="200" cy="84" r="2.2"/><g class="il-mark" transform="translate(110 56)"><circle r="10"/><text y="3.6">L</text></g>'
                 '</g>')
    return f'<svg class="il" viewBox="0 0 {W} {H}" aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg">{"".join(parts)}</svg>'


def scene_dieline(pid='id'):
    """flat die-line of a block-bottom paper bag: cut lines solid, folds dashed"""
    x = [30, 130, 190, 290, 350, 368]
    top, bot, b2 = 40, 330, 400
    cut = (f"M{x[0]} {top} H{x[4]} L{x[5]} {top+12} V{bot-12} L{x[4]} {bot} "
           f"V{b2} H{x[0]} Z")
    folds = ' '.join(f"M{xx} {top} V{b2}" for xx in x[1:5]) + f" M{x[0]} {bot} H{x[4]} M{x[0]} {top+40} H{x[4]}"
    gus = (f"M{x[1]} {bot} L{(x[1]+x[2])/2} {b2-20} L{x[2]} {bot} M{x[3]} {bot} L{(x[3]+x[4])/2} {b2-20} L{x[4]} {bot}")
    return (f'<svg class="il" viewBox="0 0 400 440" aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg">'
            f'<defs><pattern id="{pid}-f" width="9" height="9" patternUnits="userSpaceOnUse"><path class="il-fiber" d="M1 2 l3 .6 M6 5 l2 -.8 M2 7.5 l2.4 .3 M7 1 l1.4 1"/></pattern>'
            f'<linearGradient id="{pid}-k" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#d4b48a" stop-opacity=".34"/><stop offset="1" stop-color="#8a6a50" stop-opacity=".2"/></linearGradient></defs>'
            f'<g class="il-body"><path class="il-kraft-r il-draw" pathLength="1" d="{cut}"/><path class="il-tex" d="{cut}" fill="url(#{pid}-f)"/></g>'
            f'<g class="il-detail"><path class="il-fold" d="{folds}"/><path class="il-fold" d="{gus}"/>'
            f'<path class="il-print" d="M{x[1]+12} {top+80} H{x[2]+48} V{top+200} H{x[1]+12} Z" transform="translate(0 0)"/></g>'
            f'<g class="il-anno"><path class="il-dim" d="M{x[0]} 424 H{x[4]} M{x[0]} 418 V430 M{x[4]} 418 V430"/><text class="il-dimtext" x="{(x[0]+x[4])/2}" y="420">DIE-LINE</text>'
            f'<g class="il-mark" transform="translate(382 200)"><circle r="10"/><text y="3.6">G</text></g></g></svg>')


def scene_print(pid='ir'):
    s = Scene(pid, 22, 210, 300)
    s.floor_grid(-4, 12, -4, 10, 2)
    s.block_bag(0.5, 1, 5.6, 3.4, 10.5, 'paper')
    svg = s.svg('40 20 340 400')
    sw = ''.join(f'<g transform="translate({300} {90 + i*52})"><rect class="il-swatch il-swatch-{i}" width="34" height="34" rx="2"/><text class="il-dimtext" x="-10" y="22" text-anchor="end">0{i+1}</text></g>' for i in range(4))
    reg = '<g class="il-reg" transform="translate(70 70)"><circle r="9"/><path d="M-14 0 H14 M0 -14 V14"/></g>'
    return svg.replace('</svg>', f'<g class="il-anno">{sw}{reg}</g></svg>')



def scene_weave(pid='iwv'):
    """Macro study of plain-woven PP tape: alternating warp/weft tapes with fibrils and a sewn seam."""
    W, H, c = 1440, 820, 40
    g = 2          # gap between tapes
    out = []
    def cell(i, j):
        x, y = i * c, j * c
        o = []
        if (i + j) % 2 == 0:
            o.append(f'<rect class="wv-a" x="{x}" y="{y + g}" width="{c}" height="{c - 2*g}" rx="2"/>')
            o += [f'<path class="wv-f" d="M{x + 3} {y + g + (c - 2*g) * k:.1f} H{x + c - 3}"/>' for k in (0.3, 0.5, 0.7)]
            o.append(f'<path class="wv-dip" d="M{x + 1} {y + g + 2} V{y + c - g - 2} M{x + c - 1} {y + g + 2} V{y + c - g - 2}"/>')
        else:
            o.append(f'<rect class="wv-b" x="{x + g}" y="{y}" width="{c - 2*g}" height="{c}" rx="2"/>')
            o += [f'<path class="wv-f" d="M{x + g + (c - 2*g) * k:.1f} {y + 3} V{y + c - 3}"/>' for k in (0.3, 0.5, 0.7)]
            o.append(f'<path class="wv-dip" d="M{x + g + 2} {y + 1} H{x + c - g - 2} M{x + g + 2} {y + c - 1} H{x + c - g - 2}"/>')
        return ''.join(o)
    tile = ''.join(cell(i, j) for i in (0, 1) for j in (0, 1))
    pat = f'<defs><pattern id="{pid}-p" width="{2*c}" height="{2*c}" patternUnits="userSpaceOnUse" patternTransform="rotate(-14) scale(1.25)">{tile}</pattern></defs>'
    weave = f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#{pid}-p)"/>'
    # seam: folded hem band with a double row of stitches
    sy = 330
    seam = (f'<rect class="wv-hem" x="-300" y="{sy}" width="{W + 600}" height="64"/>'
            f'<path class="wv-hem-edge" d="M-300 {sy} H{W + 300} M-300 {sy + 64} H{W + 300}"/>'
            f'<path class="wv-stitch" d="M-300 {sy + 20} H{W + 300} M-300 {sy + 44} H{W + 300}"/>')
    anno = (f'<g class="il-anno">'
            f'<path class="il-lead" d="M300 {sy + 20} L 250 {sy - 60}"/><circle class="il-dot" cx="300" cy="{sy + 20}" r="3"/>'
            f'<text class="wv-label" x="250" y="{sy - 70}">SEAM · DOUBLE STITCH</text>'
            f'<path class="il-lead" d="M690 230 L 760 160"/><circle class="il-dot" cx="690" cy="230" r="3"/>'
            f'<text class="wv-label" x="760" y="150">WEFT TAPE</text>'
            f'</g>')
    return (f'<svg class="il il-weavebg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg">'
            f'{pat}<rect class="wv-bg" width="{W}" height="{H}"/>{weave}'
            f'<g transform="rotate(-14 {W/2} {H/2})">{seam}</g>{anno}</svg>')

def scene_hero(pid='ih'):
    s = Scene(pid, 30, 600, 420)
    s.bulk_bag(0, 0, 10, 10, 11, dims=True)
    pts = {'loop': (10 + .7, 10 - 1.7 * .5, 11 + 3.4), 'print': (10 * .5, 10.2, 11 * .55)}
    proj = {k: s.P(*v) for k, v in pts.items()}
    svg = s.svg(title='איור טכני של שק ענק עם לולאות הרמה', pad=40)
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', svg).group(1).split()]
    spots = {k: (round((X - vb[0]) / vb[2] * 100, 1), round((Y - vb[1]) / vb[3] * 100, 1)) for k, (X, Y) in proj.items()}
    return svg, spots, vb


if __name__ == '__main__':
    import json
    hs, spots, vb = scene_hero()
    write('hero', hs)
    write('weave', scene_weave())
    open(os.path.join(OUT, 'hero.json'), 'w').write(json.dumps({'spots': spots, 'viewBox': vb}))
    write('bulk', scene_bulk())
    write('bulk-config', scene_bulk('ibc'))
    write('pp', scene_pp())
    write('paper', scene_paper())
    write('coal', scene_coal())
    write('special', scene_special())
    for k in ('bulk', 'pp', 'paper', 'coal', 'special'):
        write('tile-' + k, scene_tile(k, 't' + k[:2]))
    for k in ('bulk', 'pp', 'paper', 'coal'):
        write('fd-' + k, scene_tile(k, 'f' + k[:2], logo=True))
    write('panorama', scene_panorama())
    write('loop', scene_loop())
    write('dieline', scene_dieline())
    write('print', scene_print())
