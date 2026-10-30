"""旅程夥伴衛教影片 — 繪圖工具：字型、文字、圖示、角色（佔位或貼圖）"""
import json, math, os
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1920, 1080, 30
ROOT = os.path.dirname(os.path.abspath(__file__))

# ---- 旅程夥伴配色 ----
BG = (250, 250, 243)
SURF = (255, 255, 255)
SURF2 = (241, 241, 230)
INK = (33, 40, 31)
MUTED = (102, 112, 95)
LINE = (224, 224, 210)
C = {
    'diet': ((194, 98, 10), (252, 233, 212)),
    'move': ((10, 138, 77), (220, 243, 229)),
    'rx': ((53, 99, 201), (225, 233, 251)),
    'gold': ((154, 107, 42), (245, 237, 221)),
    'flag': ((200, 45, 27), (251, 227, 222)),
}

# ---- 字型 ----
NOTO = '/usr/share/fonts/opentype/noto/NotoSansCJK-{}.ttc'
_WK_MAP = {int(k): v for k, v in json.load(open(f'{ROOT}/fonts/wk/map.json')).items()}


@lru_cache(None)
def noto(size, weight='Regular'):
    return ImageFont.truetype(NOTO.format(weight), size, index=3)


@lru_cache(None)
def _wk_file(path, size):
    return ImageFont.truetype(f'{ROOT}/fonts/{path}', size)


def wk_font_for(ch, size):
    p = _WK_MAP.get(ord(ch))
    return _wk_file(p, size) if p else noto(size, 'Medium')


class Face:
    """kind: 'wk' 霞鶩文楷（標題、話術）；'sans' Noto Sans TC（內文）"""
    def __init__(self, kind, size, weight='Regular'):
        self.kind, self.size, self.weight = kind, size, weight

    def font(self, ch):
        return wk_font_for(ch, self.size) if self.kind == 'wk' else noto(self.size, self.weight)

    def width(self, s):
        if self.kind == 'sans':
            return noto(self.size, self.weight).getlength(s)
        return sum(self.font(c).getlength(c) for c in s)

    def draw(self, d, xy, s, fill):
        x, y = xy
        if self.kind == 'sans':
            d.text((x, y), s, font=noto(self.size, self.weight), fill=fill)
            return
        for c in s:
            f = self.font(c)
            d.text((x, y), c, font=f, fill=fill)
            x += f.getlength(c)


NO_START = set('，。、；：！？）」』》〉—…％%．,.;:!?)')


NO_END = set('「『《〈（(')


BREAK_AFTER = set('，、。；：！？」』）—')


def _char_wrap(face, s, maxw):
    lines, cur = [], ''
    for ch in s:
        if face.width(cur + ch) > maxw and cur:
            buf = cur + ch
            k = len(cur)
            while k > 1 and (buf[k] in NO_START or buf[k - 1] in NO_END):
                k -= 1
            lines.append(buf[:k]); cur = buf[k:]
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines


def wrap(face, s, maxw):
    """按詞組斷行：優先在標點後換行，避免孤字；詞組太長才逐字斷。"""
    if face.width(s) <= maxw:
        return [s]
    segs, cur = [], ''
    for i, ch in enumerate(s):
        cur += ch
        nxt = s[i + 1] if i + 1 < len(s) else ''
        if ch in BREAK_AFTER and nxt not in NO_START and not (ch == '—' and nxt == '—'):
            segs.append(cur); cur = ''
    if cur:
        segs.append(cur)
    lines, line = [], ''
    for sg in segs:
        if face.width(line + sg) <= maxw:
            line += sg
        elif face.width(sg) <= maxw:
            if line:
                lines.append(line)
            line = sg
        else:
            parts = _char_wrap(face, line + sg, maxw)
            lines += parts[:-1]; line = parts[-1]
    if line:
        lines.append(line)
    # 末行仍過短（≤2 字）時，往前借字
    if len(lines) > 1 and len(lines[-1]) <= 2:
        prev = lines[-2]
        k = max(1, len(prev) // 3)
        lines[-2], lines[-1] = prev[:-k], prev[-k:] + lines[-1]
    return lines


def text_layer(s, face, fill=INK, maxw=None, gap=1.45):
    """把一段文字畫成透明圖層（可多行）。"""
    rows = wrap(face, s, maxw) if maxw else [s]
    lh = int(face.size * gap)
    w = int(max(face.width(r) for r in rows)) + 8
    h = lh * (len(rows) - 1) + int(face.size * 1.35)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, r in enumerate(rows):
        face.draw(d, (0, i * lh), r, fill)
    return im


def pill(text, face, fg, bg, padx=28, pady=12):
    tw = face.width(text)
    w, h = int(tw + padx * 2), int(face.size * 1.3 + pady * 2)
    s = 2
    im = Image.new('RGBA', (w * s, h * s), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w * s - 1, h * s - 1), radius=h * s // 2, fill=bg)
    im = im.resize((w, h), Image.LANCZOS)
    face.draw(ImageDraw.Draw(im), (padx, pady - face.size * 0.08), text, fg)
    return im


def card(w, h, fill=SURF, radius=28, shadow=True, border=LINE):
    pad = 40
    im = Image.new('RGBA', (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    if shadow:
        sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle((pad, pad + 10, pad + w, pad + h + 10), radius, fill=(33, 40, 31, 34))
        im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(16)))
    ImageDraw.Draw(im).rounded_rectangle((pad, pad, pad + w, pad + h), radius, fill=fill, outline=border, width=2)
    return im, pad


# ---- 圖示：圓角單色描邊（旅程夥伴圖示規範），2x 超取樣 ----
def icon(name, size, color):
    S = 4
    n = size * S
    im = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    u = n / 48.0  # 48 格網
    lw = max(2, int(2.6 * u))

    def L(*pts, w=lw):
        p = [(x * u, y * u) for x, y in pts]
        d.line(p, fill=color, width=w, joint='curve')
        for x, y in p[0], p[-1]:
            d.ellipse((x - w / 2, y - w / 2, x + w / 2, y + w / 2), fill=color)

    def R(x0, y0, x1, y1, r=4, fill=None):
        d.rounded_rectangle((x0 * u, y0 * u, x1 * u, y1 * u), r * u, outline=color, width=lw, fill=fill)

    def E(x0, y0, x1, y1, fill=None, w=None):
        d.ellipse((x0 * u, y0 * u, x1 * u, y1 * u), outline=color, width=w or lw, fill=fill)

    if name == 'flag':
        L((12, 42), (12, 6)); d.polygon([(12 * u, 7 * u), (38 * u, 13 * u), (12 * u, 22 * u)], fill=color)
    elif name == 'calendar':
        R(6, 10, 42, 42); L((6, 19), (42, 19)); L((15, 5), (15, 13)); L((33, 5), (33, 13))
        E(29, 26, 37, 34, fill=color)
    elif name == 'egg':
        E(13, 6, 35, 42)
        E(20, 20, 28, 28, fill=color)
    elif name == 'bowl':
        d.chord((6 * u, 4 * u, 42 * u, 40 * u), 0, 180, outline=color, width=lw); L((6, 22), (42, 22))
        L((18, 41), (30, 41)); L((30, 6), (40, 16)); L((24, 4), (36, 14))
    elif name == 'cup':
        L((10, 8), (14, 42), (34, 42), (38, 8)); L((8, 8), (40, 8)); L((12, 20), (36, 20), w=lw // 2)
    elif name == 'leaf':
        d.chord((6 * u, 6 * u, 46 * u, 46 * u), 180, 270, outline=color, width=lw)
        d.chord((2 * u, 2 * u, 42 * u, 42 * u), 0, 90, outline=color, width=lw)
        L((8, 40), (40, 8))
    elif name == 'shoe':
        L((6, 34), (6, 14), (18, 14), (22, 24), (40, 28), (42, 34), (6, 34)); L((6, 40), (42, 40))
        L((12, 20), (17, 20), w=lw // 2); L((12, 26), (20, 26), w=lw // 2)
    elif name == 'chair':
        L((12, 4), (12, 44)); L((12, 26), (36, 26)); L((36, 26), (36, 44)); L((12, 34), (36, 34))
    elif name == 'dumbbell':
        L((10, 24), (38, 24)); R(4, 14, 12, 34, 3); R(36, 14, 44, 34, 3)
    elif name == 'check':
        R(5, 5, 43, 43, 8); L((14, 24), (21, 32), (35, 15))
    elif name == 'star':
        pts = []
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5
            r = 20 if i % 2 == 0 else 8.5
            pts.append(((24 + r * math.cos(a)) * u, (25 + r * math.sin(a)) * u))
        d.polygon(pts, fill=color)
    elif name == 'moon':
        E(6, 6, 42, 42, fill=color)
        d.ellipse((16 * u, 0, 50 * u, 34 * u), fill=(0, 0, 0, 0))
    elif name == 'alert':
        d.polygon([(24 * u, 4 * u), (45 * u, 42 * u), (3 * u, 42 * u)], outline=color, width=lw)
        L((24, 17), (24, 29)); E(22, 34, 26, 38, fill=color, w=1)
    elif name == 'phone':
        R(12, 3, 36, 45, 6); L((21, 39), (27, 39))
    elif name == 'chat':
        R(4, 6, 44, 34, 8); L((14, 34), (12, 44), (24, 34))
    elif name == 'clock':
        E(5, 5, 43, 43); L((24, 13), (24, 24), (32, 29))
    elif name == 'heart':
        d.polygon([(24 * u, 42 * u), (5 * u, 22 * u), (24 * u, 14 * u), (43 * u, 22 * u)], fill=color)
        d.ellipse((4 * u, 6 * u, 25 * u, 27 * u), fill=color); d.ellipse((23 * u, 6 * u, 44 * u, 27 * u), fill=color)
    return im.resize((size, size), Image.LANCZOS)


# ---- 角色：優先用貼圖 stickers/<pose>.png，沒有就畫原創佔位小夥伴 ----
STICKER_DIR = f'{ROOT}/stickers'


def _trim(im):
    bb = im.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox()
    return im.crop(bb) if bb else im


@lru_cache(None)
def character(pose, size):
    for ext in ('png', 'webp'):
        p = f'{STICKER_DIR}/{pose}.{ext}'
        if os.path.exists(p):
            im = _trim(Image.open(p).convert('RGBA'))
            k = size / max(im.size)
            return im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)
    return _placeholder(pose, size)


def _placeholder(pose, size):
    S = 4
    n = size * S
    im = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    body = (122, 201, 160); dark = (58, 125, 92); ink = (40, 44, 38); blush = (246, 160, 150)
    cx, cy, rx, ry = n * .5, n * .58, n * .34, n * .32
    lw = int(n * .018)

    def arm(ang, length=.2):
        sx, sy = cx + math.cos(ang) * rx * .92, cy + math.sin(ang) * ry * .55
        a2 = ang
        ex, ey = sx + math.cos(a2) * n * length, sy + math.sin(a2) * n * length
        d.line((sx, sy, ex, ey), fill=dark, width=int(n * .07))
        r = n * .045
        d.ellipse((ex - r, ey - r, ex + r, ey + r), fill=body, outline=dark, width=lw)

    arms = {
        'wave': (math.radians(-40), math.radians(160)),
        'cheer': (math.radians(-50), math.radians(-130)),
        'think': (math.radians(200), math.radians(20)),
        'point': (math.radians(-10), math.radians(160)),
        'eat': (math.radians(30), math.radians(150)),
        'walk': (math.radians(40), math.radians(140)),
        'alert': (math.radians(-60), math.radians(-120)),
        'sleep': (math.radians(30), math.radians(150)),
        'thumbs': (math.radians(-30), math.radians(150)),
    }.get(pose, (math.radians(30), math.radians(150)))
    # 腳
    for fx in (-.13, .13):
        d.ellipse((cx + fx * n - n * .07, cy + ry * .82, cx + fx * n + n * .07, cy + ry * .82 + n * .09), fill=dark)
    for a in arms:
        if math.sin(a) > 0.1:
            arm(a)
    # 身體
    d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=body, outline=dark, width=lw)
    # 葉子頭飾
    d.chord((cx - n * .02, cy - ry - n * .17, cx + n * .2, cy - ry + n * .03), 90, 270, fill=(10, 138, 77))
    d.line((cx, cy - ry - n * .02, cx + n * .02, cy - ry + n * .02), fill=dark, width=lw)
    # 高光
    d.ellipse((cx - rx * .6, cy - ry * .75, cx - rx * .25, cy - ry * .45), fill=(200, 238, 215))
    for a in arms:
        if math.sin(a) <= 0.1:
            arm(a)
    # 臉
    ey = cy - ry * .05
    if pose == 'sleep':
        for ex in (-.11, .11):
            d.arc((cx + ex * n - n * .04, ey - n * .02, cx + ex * n + n * .04, ey + n * .04), 0, 180, fill=ink, width=lw)
    else:
        for ex in (-.11, .11):
            x = cx + ex * n
            d.ellipse((x - n * .032, ey - n * .045, x + n * .032, ey + n * .045), fill=ink)
            d.ellipse((x - n * .012, ey - n * .03, x + n * .008, ey - n * .008), fill='white')
    for ex in (-.2, .2):
        x = cx + ex * n
        d.ellipse((x - n * .045, ey + n * .04, x + n * .045, ey + n * .075), fill=blush)
    if pose in ('alert',):
        d.ellipse((cx - n * .03, ey + n * .07, cx + n * .03, ey + n * .12), fill=ink)
    else:
        d.arc((cx - n * .05, ey + n * .03, cx + n * .05, ey + n * .1), 20, 160, fill=ink, width=lw)
    return im.resize((size, size), Image.LANCZOS)


# ---- 合成工具 ----
def ease_out(x):
    x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3


def ease_back(x):
    x = max(0.0, min(1.0, x)); c = 1.70158
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def paste(frame, layer, xy, alpha=1.0, scale=1.0, anchor='lt'):
    if alpha <= 0.004:
        return
    if scale != 1.0:
        if scale <= 0.02:
            return
        layer = layer.resize((max(1, int(layer.width * scale)), max(1, int(layer.height * scale))), Image.BILINEAR)
    x, y = xy
    if anchor == 'c':
        x, y = x - layer.width / 2, y - layer.height / 2
    elif anchor == 'cb':
        x, y = x - layer.width / 2, y - layer.height
    if alpha < 0.999:
        a = layer.getchannel('A').point(lambda v: int(v * alpha))
        layer = layer.copy(); layer.putalpha(a)
    x, y = int(round(x)), int(round(y))
    sx, sy = max(0, -x), max(0, -y)
    if sx or sy or x + layer.width > frame.width or y + layer.height > frame.height:
        ex, ey = min(layer.width, frame.width - x), min(layer.height, frame.height - y)
        if ex <= sx or ey <= sy:
            return
        frame.alpha_composite(layer, (x + sx, y + sy), (sx, sy, ex, ey))
    else:
        frame.alpha_composite(layer, (x, y))
