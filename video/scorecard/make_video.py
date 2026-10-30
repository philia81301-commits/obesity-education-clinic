import math, os, subprocess, sys, json, argparse
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1920, 1080, 30
BG = (251, 248, 243)
DARK = (26, 43, 60); TEAL = (2, 128, 144); GREEN = (45, 122, 79)
AMBER = (194, 123, 10); RED = (192, 57, 43); PURPLE = (91, 63, 174); NAVY = (28, 53, 87)
MUTED = (110, 120, 130); SOFT = (232, 242, 243)
FD = '/usr/share/fonts/opentype/noto/'
D = {}; ASSETS = 'assets'
def pct(v): return f'{v:.0f}%' if v >= 10 else f'{v:.1f}%'
def fmt1(v): return f'{v:g}'
def F(size, w='Bold'):
    return ImageFont.truetype(FD + f'NotoSansCJK-{w}.ttc', size, index=3)

# ---------- stickers ----------
def load_sticker(name):
    im = Image.open(f'{ASSETS}/{name}.png').convert('RGBA')
    if name != 'bravo':  # white background -> transparent via flood fill from corners
        rgb = im.convert('RGB')
        for c in [(0, 0), (im.width - 1, 0), (0, im.height - 1), (im.width - 1, im.height - 1)]:
            ImageDraw.floodfill(rgb, c, (255, 0, 255), thresh=18)
        mask = Image.new('L', im.size, 255); px = rgb.load(); m = mask.load()
        for y in range(im.height):
            for x in range(im.width):
                if px[x, y] == (255, 0, 255): m[x, y] = 0
        im.putalpha(mask.filter(ImageFilter.GaussianBlur(0.8)))
    im = im.crop(im.getbbox())
    return im
ST = {}
_cache = {}
def sticker(name, h):
    k = (name, h)
    if k not in _cache:
        if name not in ST: ST[name] = load_sticker(name)
        s = ST[name]; _cache[k] = s.resize((int(s.width * h / s.height), h), Image.LANCZOS)
    return _cache[k]

# ---------- helpers ----------
def clamp(x): return max(0.0, min(1.0, x))
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3
def prog(t, a, d=0.6): return ease((t - a) / d)

def text(d, xy, s, font, fill=DARK, anchor='la', alpha=1.0, bg=BG):
    if alpha <= 0: return
    if alpha < 1: fill = tuple(int(bg[i] + (fill[i] - bg[i]) * alpha) for i in range(3))
    d.text(xy, s, font=font, fill=fill, anchor=anchor)

def mix(c, a, bg=BG): return tuple(int(bg[i] + (c[i] - bg[i]) * a) for i in range(3))

def base(t, dur, title, kicker, accent=TEAL):
    im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im)
    # soft decorative circles
    d.ellipse((1380, -220, 2160, 560), fill=(238, 246, 246))
    d.ellipse((-180, 860, 260, 1300), fill=(246, 239, 228))
    if title:
        a = prog(t, 0.1)
        d.rounded_rectangle((110, 92, 110 + 12, 92 + 92), 6, fill=mix(accent, a))
        text(d, (148, 80), kicker, F(30, 'Medium'), mix(accent, a))
        text(d, (148, 116), title, F(62), DARK, alpha=a)
    return im, d

def caption(im, d, t, s, start=0.8):
    a = prog(t, start, 0.5)
    if a <= 0: return
    y0 = 930
    d.rounded_rectangle((110, y0, 1810, y0 + 100), 50, fill=mix(DARK, a))
    text(d, (960, y0 + 50), s, F(40, 'Medium'), (255, 255, 255), anchor='mm', alpha=a, bg=mix(DARK, a))

def put_sticker(im, t, name, h=640, x=1290, y=None, delay=0.2):
    s = sticker(name, h)
    a = prog(t, delay, 0.7)
    bob = math.sin(t * 2.2) * 8
    yy = (y if y is not None else 900 - h) + int((1 - a) * 80 + bob)
    if a <= 0: return
    if a < 1:
        s = s.copy(); al = s.split()[3].point(lambda v: int(v * a)); s.putalpha(al)
    im.paste(s, (x, yy), s)

def fade(im, t, dur, fin=0.35, fout=0.35):
    k = min(clamp(t / fin), clamp((dur - t) / fout))
    if k >= 1: return im
    return Image.blend(Image.new('RGB', (W, H), BG), im, k)

# ---------- scenes ----------
def s1(t, dur):
    im, d = base(t, dur, None, None)
    a = prog(t, 0.2, 0.8)
    text(d, (140, 250), '高雄榮總 家庭醫學部', F(40, 'Medium'), TEAL, alpha=a)
    text(d, (130, 310), '減重門診', F(140, 'Black'), DARK, alpha=prog(t, 0.5, 0.8))
    text(d, (130, 480), '大家的成績單', F(140, 'Black'), TEAL, alpha=prog(t, 0.8, 0.8))
    b = prog(t, 1.3)
    d.rounded_rectangle((140, 690, 140 + 760, 760), 35, fill=mix(SOFT, b))
    text(d, (520, 725), f"{D['roc_month']} 門診數據分享", F(36, 'Medium'), NAVY, anchor='mm', alpha=b, bg=mix(SOFT, b))
    put_sticker(im, t, 'morning', h=720, x=1180, y=150)
    caption(im, d, t, '大家好！我是潘湘如醫師，帶你看看門診夥伴們的真實數據', 1.8)
    return im

def s2(t, dur):
    im, d = base(t, dur, '來看診的是哪些人？', '我們的減重夥伴')
    cards = [(D['n_cases'], '位', '累積追蹤個案', TEAL, 0),
             (D['age_mean'], '歲', '平均年齡', GREEN, 1),
             (D['weight_mean_kg'], '公斤', '平均起始體重', AMBER, 1),
             (D['bmi_mean'], '', '平均起始 BMI', PURPLE, 1)]
    for i, (num, unit, lab, col, dec) in enumerate(cards):
        cx = 110 + (i % 2) * 560; cy = 260 + (i // 2) * 250
        a = prog(t, 0.5 + i * 0.25)
        if a <= 0: continue
        d.rounded_rectangle((cx, cy + int((1 - a) * 30), cx + 520, cy + 220 + int((1 - a) * 30)), 28,
                            fill=mix((255, 255, 255), a), outline=mix(col, a * 0.5), width=3)
        v = float(num) * ease((t - 0.5 - i * 0.25) / 1.4)
        sv = f'{v:,.0f}' if dec == 0 else f'{v:.1f}'
        text(d, (cx + 40, cy + 30), lab, F(32, 'Medium'), MUTED, alpha=a, bg=(255, 255, 255))
        nf = F(96, 'Black')
        text(d, (cx + 40, cy + 70), sv, nf, col, alpha=a, bg=(255, 255, 255))
        nw = d.textlength(sv, font=nf)
        text(d, (cx + 52 + nw, cy + 130), unit, F(40, 'Medium'), col, alpha=a, bg=(255, 255, 255))
    a = prog(t, 2.0)
    text(d, (110, 790), f"女性 {D['female_pct']}%　・　男性 {D['male_pct']}%", F(38, 'Medium'), NAVY, alpha=a)
    a = prog(t, 2.6)
    text(d, (110, 845), f"來診前半年，{D['weight_rising_pct']}% 的人體重正在上升", F(38, 'Bold'), RED, alpha=a)
    put_sticker(im, t, 'whoop', h=680, x=1230, y=200)
    caption(im, d, t, '你不孤單：來看診的人，大多和你一樣正在努力', 3.2)
    return im

def hbars(d, t, items, x0, y0, maxw, rowh, start, maxv=None, labw=330, fmt='{:.0f}%'):
    maxv = maxv or max(v for _, v, _ in items)
    for i, (lab, v, col) in enumerate(items):
        y = y0 + i * rowh; a = prog(t, start + i * 0.2)
        text(d, (x0 + labw - 20, y + 30), lab, F(36, 'Medium'), DARK, anchor='ra', alpha=a) if False else \
            text(d, (x0 + labw - 24, y + 32), lab, F(36, 'Medium'), DARK, anchor='rm', alpha=a)
        g = ease((t - start - i * 0.2) / 1.0)
        w = int(maxw * v / maxv * g)
        d.rounded_rectangle((x0 + labw, y + 6, x0 + labw + maxw, y + 58), 26, fill=mix((236, 236, 232), a))
        if w > 52: d.rounded_rectangle((x0 + labw, y + 6, x0 + labw + w, y + 58), 26, fill=col)
        if g > 0.05:
            text(d, (x0 + labw + max(w, 52) + 18, y + 32), fmt.format(v * g), F(40, 'Black'), col, anchor='lm', alpha=a)

def s3(t, dur):
    im, d = base(t, dur, '常合併的健康問題', '不只是體重', RED)
    items = [(l, v, c) for (l, v), c in zip(D['comorbidities'], [RED, AMBER, PURPLE, NAVY, TEAL])]
    hbars(d, t, items, 110, 270, 560, 105, 0.5, maxv=max(v for _, v, _ in items) * 1.1, labw=390)
    a = prog(t, 2.2)
    d.rounded_rectangle((110, 810, 1180, 885), 20, fill=mix((253, 236, 233), a))
    text(d, (140, 847), f"{D['comorbid_any_text']}，合併至少一種代謝問題", F(36, 'Bold'), RED, anchor='lm', alpha=a, bg=mix((253, 236, 233), a))
    put_sticker(im, t, 'bravo', h=700, x=1220, y=180)
    caption(im, d, t, '好消息是：體重下降，這些問題也常跟著改善', 2.8)
    return im

def s4(t, dur):
    im, d = base(t, dur, '大家選擇的治療方式', '治療模式')
    pal = {'GLP-1 類藥物': TEAL, '生活型態調整（不用藥）': GREEN, '其他口服減重藥物': AMBER,
           '兩種藥物併用／轉換': PURPLE, '減重手術評估': RED}
    items = [(l, v, pal.get(l, NAVY)) for l, v in D['treatments']]
    cx, cy, R, r = 420, 560, 250, 150
    g = ease((t - 0.4) / 1.6); ang = -90
    for lab, v, col in items:
        sweep = 360 * v / 100 * g
        if sweep > 0.3: d.pieslice((cx - R, cy - R, cx + R, cy + R), ang, ang + sweep, fill=col)
        ang += 360 * v / 100
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=BG)
    a = prog(t, 1.4)
    text(d, (cx, cy - 25), str(D['n_cases']), F(80, 'Black'), DARK, anchor='mm', alpha=a)
    text(d, (cx, cy + 45), '位個案', F(32, 'Medium'), MUTED, anchor='mm', alpha=a)
    for i, (lab, v, col) in enumerate(items):
        y = 330 + i * 92; a = prog(t, 0.8 + i * 0.2)
        d.rounded_rectangle((740, y, 772, y + 32), 8, fill=mix(col, a))
        text(d, (792, y + 16), lab, F(36, 'Medium'), DARK, anchor='lm', alpha=a)
        text(d, (1330, y + 16), pct(v), F(40, 'Black'), col, anchor='rm', alpha=a)
    put_sticker(im, t, 'whoop', h=540, x=1400, y=350)
    caption(im, d, t, '用不用藥、用哪一種，都由醫師依你的身體狀況一起討論', 2.6)
    return im

def s5(t, dur):
    im, d = base(t, dur, '三個月可以減多少？', '減重成效', GREEN)
    a = prog(t, 0.4)
    text(d, (110, 250), '追蹤 3–5 個月，平均體重下降', F(38, 'Medium'), MUTED, alpha=a)
    v = D['m3_loss_pct'] * ease((t - 0.5) / 1.5)
    text(d, (100, 290), f'{v:.1f}%', F(200, 'Black'), GREEN, alpha=a)
    b = prog(t, 1.6)
    d.rounded_rectangle((110, 545, 700, 625), 20, fill=mix((231, 242, 235), b))
    text(d, (140, 585), f"以 80 公斤為例 ≈ 減 {80 * D['m3_loss_pct'] / 100:.1f} 公斤", F(36, 'Bold'), GREEN, anchor='lm', alpha=b, bg=mix((231, 242, 235), b))
    b = prog(t, 2.1)
    text(d, (110, 665), f"{'一半的人' if 45 <= D['m3_success_pct'] <= 55 else '有'}（{D['m3_success_pct']}%）", F(44, 'Black'), DARK, alpha=b)
    text(d, (110, 728), '減掉 5% 以上體重——醫學上已有感的改善', F(36, 'Medium'), DARK, alpha=b)
    # column chart: time course
    bars = D['timeline']; top = max(v for _, v in bars) * 1.08
    bx, by, bw, gap, mh = 900, 820, 120, 60, 420
    text(d, (bx, 280), '持續回診，成效會累積', F(34, 'Bold'), NAVY, alpha=prog(t, 2.6))
    for i, (lab, val) in enumerate(bars):
        s = 2.8 + i * 0.35; g = ease((t - s) / 0.9); a2 = prog(t, s)
        x = bx + i * (bw + gap); h = int(mh * val / top * g)
        if h > 4: d.rounded_rectangle((x, by - h, x + bw, by), min(18, h // 2), fill=mix(GREEN if i == 0 else TEAL, 0.55 + 0.45 * (i / 2)))
        if g > 0.05: text(d, (x + bw / 2, by - h - 30), f'{val * g:.1f}%', F(36, 'Black'), DARK, anchor='mm', alpha=a2)
        text(d, (x + bw / 2, by + 32), lab, F(28, 'Medium'), MUTED, anchor='mm', alpha=a2)
    put_sticker(im, t, 'bravo', h=520, x=1440, y=380, delay=0.3)
    caption(im, d, t, '穩穩減、持續回診，比一次減很多更重要', 4.2)
    return im

def s6(t, dur):
    im, d = base(t, dur, '每個月大概花多少？', '費用參考', AMBER)
    a = prog(t, 0.3)
    text(d, (110, 220), '初診問卷：大家可以接受的每月治療預算', F(34, 'Medium'), MUTED, alpha=a)
    items = [(l, v, c) for (l, v), c in zip(D['budget'], [GREEN, TEAL, NAVY, AMBER, RED])]
    hbars(d, t, items, 110, 290, 560, 100, 0.6, maxv=max(v for _, v, _ in items) * 1.06, labw=330)
    b = prog(t, 2.4)
    d.rounded_rectangle((110, 815, 1180, 890), 20, fill=mix((250, 240, 222), b))
    text(d, (140, 852), '從生活型態方案到藥物療程，都有適合的選擇', F(36, 'Bold'), AMBER, anchor='lm', alpha=b, bg=mix((250, 240, 222), b))
    put_sticker(im, t, 'whoop', h=640, x=1260, y=220)
    caption(im, d, t, '看診時可以依你的預算，和醫師一起規劃方案', 3.0)
    return im

def s7(t, dur):
    im, d = base(t, dur, None, None)
    a = prog(t, 0.2, 0.8)
    text(d, (130, 170), '減重，', F(110, 'Black'), DARK, alpha=a)
    text(d, (130, 310), '我們陪你一起走', F(110, 'Black'), TEAL, alpha=prog(t, 0.6, 0.8))
    pts = ['先評估：體重、共病與生活習慣', '再討論：適合你的治療方式與預算', '持續回診：成效最穩、最安全']
    for i, p in enumerate(pts):
        b = prog(t, 1.3 + i * 0.35)
        y = 500 + i * 80
        d.ellipse((140, y + 8, 172, y + 40), fill=mix(GREEN, b))
        text(d, (156, y + 24), '✓', F(24, 'Bold'), (255, 255, 255), anchor='mm', alpha=b, bg=mix(GREEN, b))
        text(d, (196, y + 24), p, F(40, 'Medium'), DARK, anchor='lm', alpha=b)
    b = prog(t, 2.6)
    d.rounded_rectangle((130, 770, 1150, 860), 45, fill=mix(TEAL, b))
    text(d, (640, 815), '高雄榮總 家醫科 減重門診｜潘湘如 醫師', F(40, 'Bold'), (255, 255, 255), anchor='mm', alpha=b, bg=mix(TEAL, b))
    c = prog(t, 3.2)
    text(d, (130, 905), f"資料來源：本門診 {D['n_cases']} 位追蹤個案與 {D['n_survey']} 份初診問卷（{D['data_period']}）。", F(24, 'Regular'), MUTED, alpha=c)
    text(d, (130, 942), '以上為整體平均，個人成效因體質與配合度而異；實際治療以醫師評估為準。', F(24, 'Regular'), MUTED, alpha=c)
    put_sticker(im, t, 'bravo', h=760, x=1200, y=150)
    return im

SCENES = [('s1', s1, 7.0), ('s2', s2, 11.0), ('s3', s3, 10.5), ('s4', s4, 10.5),
          ('s5', s5, 12.0), ('s6', s6, 10.5), ('s7', s7, 10.0)]

def render(name, fn, dur):
    out = f'{name}.mp4'; tmp = f'{name}.tmp.mp4'
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                          '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast',
                          '-crf', '20', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    n = int(round(dur * FPS))
    for i in range(n):
        t = i / FPS
        p.stdin.write(fade(fn(t, dur), t, dur).tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, out)
    else: sys.exit(f'fail {name}')

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='減重門診成績單影片產生器')
    ap.add_argument('mode', choices=['stills', 'render', 'full'])
    ap.add_argument('--data', required=True, help='每月數據 JSON')
    ap.add_argument('--assets', default='assets', help='貼圖資料夾（bravo/whoop/morning.png）')
    ap.add_argument('--out', default='out')
    ap.add_argument('--scenes', nargs='*')
    a = ap.parse_args()
    D.update(json.load(open(a.data, encoding='utf-8'))); ASSETS = os.path.abspath(a.assets)
    os.makedirs(a.out, exist_ok=True); os.chdir(a.out)
    if a.mode == 'stills':
        for name, fn, dur in SCENES:
            fn(dur - 0.6, dur).save(f'still_{name}.jpg', quality=88)
    else:
        for name, fn, dur in SCENES:
            if a.scenes and name not in a.scenes: continue
            render(name, fn, dur); print('done', name, flush=True)
        if a.mode == 'full':
            open('list.txt', 'w').write(''.join(f"file '{n}.mp4'\n" for n, _, _ in SCENES))
            final = f"減重門診成績單_{D['roc_month'].replace('民國', '')}.mp4"
            subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', 'list.txt',
                            '-c', 'copy', '-movflags', '+faststart', final], check=True)
            print('final', os.path.abspath(final))
