"""明亮插畫背景：實物插圖（食物、景物、生活用品）"""
import math
from PIL import Image, ImageDraw, ImageFilter

SS = 2  # 超取樣


def dk(c, k=0.72):
    return tuple(int(v * k) for v in c[:3])


class Pen:
    def __init__(self, d):
        self.d = d

    def el(self, x, y, rx, ry, fill, ol=True, w=5):
        self.d.ellipse((x - rx, y - ry, x + rx, y + ry), fill=fill, outline=dk(fill) if ol else None, width=w if ol else 0)

    def poly(self, pts, fill, ol=True, w=5):
        self.d.polygon(pts, fill=fill, outline=dk(fill) if ol else None, width=w if ol else 0)

    def rr(self, box, r, fill, ol=True, w=5):
        self.d.rounded_rectangle(box, r, fill=fill, outline=dk(fill) if ol else None, width=w if ol else 0)

    def ln(self, pts, col, w):
        self.d.line(pts, fill=col, width=w, joint='curve')


# 每個物件：中心 (x,y)，大小 s（約等於物件高度）
def cloud(p, x, y, s):
    for dx, dy, r in [(-.35, .08, .28), (0, -.1, .38), (.35, .05, .3), (.12, .15, .3), (-.15, .17, .28)]:
        p.el(x + dx * s * 1.3, y + dy * s, r * s, r * s * .9, (255, 255, 255), ol=False)


def sun(p, x, y, s):
    for i in range(12):
        a = i * math.pi / 6
        p.ln([(x + math.cos(a) * s * .62, y + math.sin(a) * s * .62), (x + math.cos(a) * s * .82, y + math.sin(a) * s * .82)], (255, 196, 61), int(s * .07))
    p.el(x, y, s * .5, s * .5, (255, 212, 84), w=int(s * .03))
    for ex in (-.16, .16):
        p.el(x + ex * s, y - .02 * s, s * .035, s * .05, (90, 60, 30), ol=False)
    p.el(x - .28 * s, y + .1 * s, s * .07, s * .04, (255, 160, 120), ol=False)
    p.el(x + .28 * s, y + .1 * s, s * .07, s * .04, (255, 160, 120), ol=False)
    p.d.arc((x - .12 * s, y, x + .12 * s, y + .17 * s), 20, 160, fill=(90, 60, 30), width=int(s * .03))


def tree(p, x, y, s, g=(98, 190, 92)):
    p.rr((x - s * .07, y - s * .1, x + s * .07, y + s * .5), s * .03, (150, 104, 64), w=int(s * .025))
    for dx, dy, r in [(0, -.38, .3), (-.2, -.2, .24), (.2, -.2, .24), (0, -.12, .25)]:
        p.el(x + dx * s, y + dy * s, r * s, r * s, g, w=int(s * .025))
    p.el(x - .08 * s, y - .48 * s, .08 * s, .05 * s, tuple(min(255, v + 50) for v in g), ol=False)


def flower(p, x, y, s, c=(255, 120, 150)):
    p.ln([(x, y), (x, y + s * .55)], (76, 160, 80), int(s * .07))
    p.el(x + s * .12, y + s * .35, s * .12, s * .06, (110, 190, 100), ol=False)
    for i in range(5):
        a = i * 2 * math.pi / 5 - math.pi / 2
        p.el(x + math.cos(a) * s * .2, y + math.sin(a) * s * .2, s * .15, s * .15, c, w=int(s * .025))
    p.el(x, y, s * .12, s * .12, (255, 210, 80), w=int(s * .025))


def broccoli(p, x, y, s):
    p.poly([(x - s * .12, y + s * .45), (x + s * .12, y + s * .45), (x + s * .08, y), (x - s * .08, y)], (150, 205, 110), w=int(s * .03))
    for dx, dy, r in [(-.22, -.08, .18), (.22, -.08, .18), (0, -.22, .22), (-.1, .02, .16), (.1, .02, .16)]:
        p.el(x + dx * s, y + dy * s, r * s, r * s, (70, 160, 80), w=int(s * .03))


def carrot(p, x, y, s):
    for a in (-25, 0, 25):
        r = math.radians(a - 90)
        p.ln([(x, y - s * .28), (x + math.cos(r) * s * .25, y - s * .28 + math.sin(r) * s * .25)], (80, 170, 80), int(s * .08))
    p.poly([(x - s * .14, y - s * .28), (x + s * .14, y - s * .28), (x, y + s * .5)], (255, 140, 50), w=int(s * .03))
    for k in (-.1, .1, .28):
        p.ln([(x - s * .06, y + k * s), (x + s * .02, y + k * s)], (210, 100, 30), int(s * .025))


def tomato(p, x, y, s):
    p.el(x, y + s * .05, s * .42, s * .38, (240, 80, 70), w=int(s * .03))
    for i in range(5):
        a = i * 2 * math.pi / 5 - math.pi / 2
        p.el(x + math.cos(a) * s * .1, y - s * .3 + math.sin(a) * s * .06, s * .1, s * .05, (80, 160, 70), ol=False)
    p.el(x - s * .18, y - s * .08, s * .08, s * .05, (255, 150, 140), ol=False)


def fried_egg(p, x, y, s):
    pts = []
    for i in range(14):
        a = i * 2 * math.pi / 14
        r = s * (.46 + .06 * math.sin(i * 2.3))
        pts.append((x + math.cos(a) * r, y + math.sin(a) * r * .8))
    p.poly(pts, (255, 255, 252), w=int(s * .03))
    p.el(x + s * .05, y, s * .18, s * .17, (255, 190, 40), w=int(s * .03))
    p.el(x, y - s * .05, s * .05, s * .04, (255, 235, 160), ol=False)


def tofu(p, x, y, s):
    a, b = s * .32, s * .16
    top = [(x - a, y - b), (x, y - 2 * b), (x + a, y - b), (x, y)]
    p.poly(top, (255, 250, 228), w=int(s * .025))
    p.poly([(x - a, y - b), (x, y), (x, y + s * .38), (x - a, y + s * .38 - b)], (245, 234, 200), w=int(s * .025))
    p.poly([(x + a, y - b), (x, y), (x, y + s * .38), (x + a, y + s * .38 - b)], (232, 218, 178), w=int(s * .025))


def fish(p, x, y, s):
    p.poly([(x + s * .3, y), (x + s * .55, y - s * .22), (x + s * .55, y + s * .22)], (90, 170, 230), w=int(s * .03))
    p.el(x - s * .05, y, s * .4, s * .22, (120, 190, 240), w=int(s * .03))
    p.el(x - s * .28, y - s * .04, s * .04, s * .04, (40, 50, 70), ol=False)
    p.d.arc((x - s * .2, y - s * .15, x + s * .05, y + s * .15), 300, 60, fill=(80, 150, 210), width=int(s * .025))


def soymilk(p, x, y, s):
    p.poly([(x - s * .2, y - s * .25), (x, y - s * .45), (x + s * .2, y - s * .25)], (240, 235, 215), w=int(s * .025))
    p.rr((x - s * .2, y - s * .25, x + s * .2, y + s * .45), s * .03, (255, 252, 240), w=int(s * .025))
    p.rr((x - s * .2, y, x + s * .2, y + s * .2), 1, (120, 190, 110), ol=False)
    p.el(x, y + s * .1, s * .06, s * .06, (250, 245, 220), ol=False)


def water_glass(p, x, y, s):
    p.poly([(x - s * .25, y - s * .4), (x + s * .25, y - s * .4), (x + s * .19, y + s * .4), (x - s * .19, y + s * .4)], (225, 244, 255), w=int(s * .025))
    p.poly([(x - s * .22, y - s * .15), (x + s * .22, y - s * .15), (x + s * .18, y + s * .37), (x - s * .18, y + s * .37)], (130, 200, 245), ol=False)
    p.el(x - s * .08, y + s * .05, s * .03, s * .1, (220, 245, 255), ol=False)


def apple(p, x, y, s):
    p.el(x - s * .15, y + s * .05, s * .28, s * .35, (235, 70, 70), ol=False)
    p.el(x + s * .15, y + s * .05, s * .28, s * .35, (235, 70, 70), ol=False)
    p.ln([(x, y - s * .25), (x + s * .04, y - s * .42)], (120, 80, 40), int(s * .05))
    p.el(x + s * .16, y - s * .36, s * .12, s * .06, (90, 180, 80), ol=False)
    p.el(x - s * .2, y - s * .08, s * .07, s * .1, (255, 150, 150), ol=False)


def banana(p, x, y, s):
    p.d.chord((x - s * .5, y - s * .6, x + s * .5, y + s * .3), 20, 160, fill=(255, 215, 70), outline=(200, 160, 30), width=int(s * .03))


def salad_bowl(p, x, y, s):
    for dx, c in [(-.25, (90, 180, 80)), (0, (120, 200, 90)), (.25, (70, 160, 70)), (-.1, (240, 80, 70)), (.15, (255, 200, 60))]:
        p.el(x + dx * s, y - s * .08, s * .16, s * .14, c, ol=False)
    p.d.chord((x - s * .5, y - s * .35, x + s * .5, y + s * .35), 0, 180, fill=(255, 255, 255), outline=(170, 190, 200), width=int(s * .03))
    p.ln([(x - s * .3, y + s * .12), (x + s * .3, y + s * .12)], (130, 200, 245), int(s * .04))


def sneaker(p, x, y, s):
    pts = [(x - s * .45, y + s * .2), (x - s * .45, y - s * .2), (x - s * .1, y - s * .22), (x, y - s * .02), (x + s * .4, y + s * .05), (x + s * .48, y + s * .2)]
    p.poly(pts, (255, 110, 90), w=int(s * .03))
    p.rr((x - s * .48, y + s * .16, x + s * .5, y + s * .3), s * .06, (255, 255, 255), w=int(s * .025))
    for k in range(3):
        p.ln([(x - s * .25 + k * s * .08, y - s * .12 + k * s * .04), (x - s * .12 + k * s * .08, y - s * .12 + k * s * .04)], (255, 255, 255), int(s * .03))


def bottle(p, x, y, s):
    p.rr((x - s * .08, y - s * .5, x + s * .08, y - s * .38), s * .02, (60, 120, 200), w=int(s * .02))
    p.rr((x - s * .18, y - s * .4, x + s * .18, y + s * .5), s * .08, (110, 190, 245), w=int(s * .025))
    p.rr((x - s * .18, y - s * .05, x + s * .18, y + s * .15), 1, (255, 255, 255), ol=False)


def dumbbell(p, x, y, s):
    p.rr((x - s * .3, y - s * .04, x + s * .3, y + s * .04), s * .03, (150, 150, 165), w=int(s * .02))
    for sx in (-1, 1):
        p.rr((x + sx * s * .3 - s * .08, y - s * .22, x + sx * s * .3 + s * .08, y + s * .22), s * .05, (90, 110, 200), w=int(s * .025))
        p.rr((x + sx * s * .44 - s * .05, y - s * .15, x + sx * s * .44 + s * .05, y + s * .15), s * .04, (90, 110, 200), w=int(s * .025))


def moon(p, x, y, s, bg):
    p.el(x, y, s * .45, s * .45, (255, 228, 120), ol=False)
    p.el(x + s * .2, y - s * .12, s * .38, s * .38, bg, ol=False)


def star(p, x, y, s, c=(255, 214, 90)):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        r = s * (.5 if i % 2 == 0 else .22)
        pts.append((x + r * math.cos(a), y + r * math.sin(a)))
    p.poly(pts, c, w=int(s * .04))


def clock(p, x, y, s):
    for sx in (-1, 1):
        p.el(x + sx * s * .28, y - s * .38, s * .14, s * .12, (255, 120, 110), w=int(s * .025))
    p.el(x, y, s * .45, s * .45, (255, 120, 110), w=int(s * .03))
    p.el(x, y, s * .36, s * .36, (255, 255, 255), ol=False)
    p.ln([(x, y), (x, y - s * .25)], (60, 60, 70), int(s * .04))
    p.ln([(x, y), (x + s * .18, y + s * .05)], (60, 60, 70), int(s * .04))


def plant(p, x, y, s):
    for a, l in [(-60, .4), (-90, .5), (-120, .4), (-35, .3), (-145, .3)]:
        r = math.radians(a)
        ex, ey = x + math.cos(r) * s * l, y - s * .1 + math.sin(r) * s * l
        p.el(ex, ey, s * .12, s * .07, (80, 175, 90), w=int(s * .02))
        p.ln([(x, y - s * .1), (ex, ey)], (70, 150, 80), int(s * .03))
    p.poly([(x - s * .25, y - s * .1), (x + s * .25, y - s * .1), (x + s * .18, y + s * .4), (x - s * .18, y + s * .4)], (230, 140, 90), w=int(s * .025))


def calendar(p, x, y, s):
    p.rr((x - s * .4, y - s * .35, x + s * .4, y + s * .45), s * .06, (255, 255, 255), w=int(s * .025))
    p.rr((x - s * .4, y - s * .35, x + s * .4, y - s * .12), s * .06, (255, 120, 110), ol=False)
    for i in range(3):
        for j in range(4):
            c = (130, 200, 120) if (i, j) in [(0, 1), (1, 2), (2, 0)] else (225, 225, 225)
            p.el(x - s * .26 + j * s * .17, y + s * .02 + i * s * .14, s * .05, s * .05, c, ol=False)


def flag_pole(p, x, y, s, c=(255, 110, 90)):
    p.ln([(x, y + s * .5), (x, y - s * .5)], (120, 90, 60), int(s * .05))
    p.poly([(x, y - s * .5), (x + s * .45, y - s * .35), (x, y - s * .18)], c, w=int(s * .025))


# ---------- 場景組合 ----------
def _grad(w, h, top, bot):
    g = Image.new('RGB', (1, 256))
    for i in range(256):
        t = i / 255
        g.putpixel((0, i), tuple(int(top[k] * (1 - t) + bot[k] * t) for k in range(3)))
    return g.resize((w, h), Image.BILINEAR).convert('RGBA')


def hills(p, W, H, base_y, cols):
    for k, (c, amp, ph) in enumerate(cols):
        y0 = base_y + k * 60 * SS
        pts = [(0, H)]
        for i in range(0, W + 40, 40):
            pts.append((i, y0 + math.sin(i / W * math.pi * 2 + ph) * amp * SS))
        pts.append((W, H))
        p.d.polygon(pts, fill=c)


THEMES = {
    0: dict(sky=((200, 235, 255), (255, 247, 225))),
    1: dict(sky=((190, 228, 255), (240, 250, 255))),
    2: dict(sky=((255, 226, 190), (255, 249, 230))),
    3: dict(sky=((185, 230, 255), (230, 250, 240))),
    4: dict(sky=((222, 214, 255), (255, 236, 214))),
}


def scene_bg(unit, W, H, layout):
    w, h = W * SS, H * SS
    th = THEMES.get(unit, THEMES[0])
    im = _grad(w, h, *th['sky'])
    d = ImageDraw.Draw(im)
    p = Pen(d)
    S = SS
    hide = {'left': (40, 1200), 'full': (40, 1880), 'center': (330, 1590)}.get(layout, (0, 0))

    def ok(x, y=0):  # x,y 為輸出座標
        if layout == 'full':
            return y < 290 or x > 1850 or x < 60
        return not (hide[0] <= x <= hide[1] and (layout != 'center' or y < 700))
    if unit in (0, 1, 3):
        if ok(1760, 150): sun(p, 1760 * S, 150 * S, 190 * S)
        if ok(1420, 120): cloud(p, 1420 * S, 120 * S, 110 * S)
        if ok(980, 70): cloud(p, 980 * S, 70 * S, 80 * S)
        if ok(300, 60): cloud(p, 300 * S, 60 * S, 70 * S)
        hills(p, w, h, 800 * S, [((150, 215, 120), 25, 0.5), ((115, 195, 100), 30, 2.0), ((95, 175, 90), 20, 4.0)])
        if ok(1260, 820): tree(p, 1260 * S, 820 * S, 230 * S)
        if ok(1860, 800): tree(p, 1860 * S, 800 * S, 280 * S, (80, 175, 90))
        if ok(70, 830): tree(p, 70 * S, 830 * S, 200 * S, (120, 200, 100))
        for fx, c in [(1340, (255, 120, 150)), (1700, (255, 200, 70)), (1820, (190, 140, 255)), (220, (255, 150, 90))]:
            if ok(fx, 900): flower(p, fx * S, 900 * S, 70 * S, c)
        if unit == 1:
            if ok(1180, 760): flag_pole(p, 1180 * S, 760 * S, 110 * S)
            if ok(1660, 740): flag_pole(p, 1660 * S, 740 * S, 100 * S, (90, 140, 240))
            if ok(1480, 300): star(p, 1480 * S, 300 * S, 50 * S)
        if unit == 3:
            if ok(1250, 925): sneaker(p, 1250 * S, 925 * S, 120 * S)
            if ok(1820, 900): bottle(p, 1820 * S, 900 * S, 130 * S)
            if ok(300, 935): dumbbell(p, 300 * S, 935 * S, 130 * S)
        if unit == 0:
            for ox, f in [(150, broccoli), (330, carrot), (1600, apple), (1770, water_glass)]:
                if ok(ox, 880): f(p, ox * S, 880 * S, 120 * S)
    elif unit == 2:
        # 桌巾＋食物
        d.rectangle((0, 840 * S, w, h), fill=(255, 255, 255))
        for i in range(0, w, 60 * S):
            d.rectangle((i, 840 * S, i + 30 * S, h), fill=(255, 196, 160))
        for j in range(840 * S, h, 60 * S):
            d.rectangle((0, j, w, j + 30 * S), fill=(255, 210, 180, 255))
        for i in range(0, w, 60 * S):
            for j in range(840 * S, h, 60 * S):
                d.rectangle((i, j, i + 30 * S, j + 30 * S), fill=(250, 160, 120))
        d.rectangle((0, 830 * S, w, 845 * S), fill=(230, 150, 110))
        items = [(broccoli, 1250, 780, 150), (tomato, 1840, 780, 130), (fried_egg, 1460, 110, 130), (carrot, 1820, 380, 150),
                 (fish, 1690, 130, 150), (tofu, 1880, 600, 130), (soymilk, 1240, 600, 150), (water_glass, 1720, 790, 140),
                 (apple, 90, 790, 120), (banana, 980, 120, 120), (salad_bowl, 1540, 800, 170)]
        for f, ox, oy, s in items:
            if ok(ox, oy): f(p, ox * S, oy * S, s * S)
    elif unit == 4:
        hills(p, w, h, 860 * S, [((200, 190, 240), 15, 1.0), ((175, 165, 225), 20, 3.0)])
        if ok(1760, 140): moon(p, 1760 * S, 140 * S, 200 * S, tuple(int(th['sky'][0][k] * .87 + th['sky'][1][k] * .13) for k in range(3)))
        for sx, sy, ss in [(1420, 90, 50), (1580, 260, 34), (1880, 380, 40), (1000, 40, 36), (250, 40, 30)]:
            if ok(sx, sy): star(p, sx * S, sy * S, ss * S)
        if ok(1250, 860): clock(p, 1250 * S, 860 * S, 140 * S)
        if ok(1850, 860): plant(p, 1850 * S, 860 * S, 190 * S)
        if ok(1240, 560): calendar(p, 1240 * S, 560 * S, 130 * S)
        if ok(1700, 900): water_glass(p, 1700 * S, 900 * S, 120 * S)
        if ok(120, 910): apple(p, 120 * S, 910 * S, 110 * S)
    im = im.resize((W, H), Image.LANCZOS)
    # 文字面板（半透明白卡）
    panel = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    box = {'left': (70, 70, 1170, 950), 'full': (80, 300, 1840, 965), 'center': (360, 150, 1560, 660)}.get(layout)
    if box:
        sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle((box[0], box[1] + 12, box[2], box[3] + 12), 40, fill=(60, 50, 40, 40))
        im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(18)))
        pd.rounded_rectangle(box, 40, fill=(255, 255, 255, 246))
        if layout == 'left':  # 對話框尾巴，指向右側人物
            pd.polygon([(box[2] - 2, 400), (box[2] + 70, 448), (box[2] - 2, 490)], fill=(255, 255, 255, 246))
        im = Image.alpha_composite(im, panel)
    return im
