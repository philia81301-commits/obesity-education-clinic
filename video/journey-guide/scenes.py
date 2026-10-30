"""旅程夥伴衛教影片 — 腳本與場景（候診區循環版）"""
import math
from PIL import Image, ImageDraw
from lib import *

UNITS = {1: ('減重', 'rx'), 2: ('營養', 'diet'), 3: ('運動', 'move'), 4: ('好習慣', 'gold')}
BRAND = '高雄榮總 家庭醫學部 · 減重門診'

F_TITLE = Face('wk', 92)
F_BODY = Face('sans', 50)
F_BODY_B = Face('sans', 50, 'Bold')
F_CHIP = Face('sans', 30, 'Bold')
F_SMALL = Face('sans', 26, 'Medium')


# ---------- 背景 ----------
_bg_cache = {}


def background(unit, layout='left'):
    key = (unit, layout)
    if key in _bg_cache:
        return _bg_cache[key]
    import objects
    im = objects.scene_bg(unit, W, H, layout)
    d = ImageDraw.Draw(im)
    # 底部進度列（白色底條）
    d.rectangle((0, 980, W, H), fill=SURF + (255,))
    d.line((0, 980, W, 980), fill=LINE, width=2)
    F_SMALL.draw(d, (72, 1006), BRAND, MUTED)
    x = 1060
    for k, (name, key2) in UNITS.items():
        col, soft = C[key2]
        label = f'{k}  {name}'
        p = pill(label, F_SMALL, SURF, col, padx=22, pady=6) if k == unit else pill(label, F_SMALL, MUTED, SURF2, padx=22, pady=6)
        im.alpha_composite(p, (x, 998))
        x += p.width + 18
    _bg_cache[key] = im
    return im


# ---------- 場景描述 ----------
class Scene:
    def __init__(self, name, unit, dur):
        self.name, self.unit, self.dur = name, unit, dur
        self.els = []      # (layer, (x,y), t0, anim, anchor, extra)
        self.custom = []   # f(frame, t, k_out)
        self.layout = 'left'

    def add(self, layer, xy, t0, anim='up', anchor='lt', bob=0.0, motion=None):
        self.els.append((layer, xy, t0, anim, anchor, (bob, motion)))
        return layer

    def frame(self, t):
        fr = background(self.unit, self.layout).copy()
        k_out = ease_out((self.dur - t) / 0.5) if t > self.dur - 0.5 else 1.0
        for f in self.custom:
            f(fr, t, k_out)
        for layer, (x, y), t0, anim, anchor, bob in self.els:
            p = (t - t0) / 0.55
            if p <= 0:
                continue
            a = ease_out(p) * k_out
            sc = 1.0
            if anim == 'up':
                y = y + (1 - ease_out(p)) * 36
            elif anim == 'pop':
                sc = max(0.02, ease_back(min(1, (t - t0) / 0.5)))
                a = min(1, p * 2) * k_out
            elif anim == 'left':
                x = x - (1 - ease_out(p)) * 60
            bob, motion = bob if isinstance(bob, tuple) else (bob, None)
            lay = layer
            u = t - t0
            if motion == 'point':      # 指向左邊文字：往左輕戳
                jab = max(0.0, math.sin(u * 2.6)) ** 4
                x -= 22 * jab
                y += math.sin(u * 1.3) * 4
            elif motion == 'hop':      # 雙手上揚：小跳步
                y -= 22 * abs(math.sin(u * 2.8)) * min(1, u)
            elif motion == 'tilt':     # 讚美：左右輕擺
                ang = 3.2 * math.sin(u * 1.9)
                lay = layer.rotate(ang, resample=Image.BICUBIC, expand=True)
                y += math.sin(u * 2.2) * 5
            elif bob:
                y = y + math.sin(u * 2.2) * bob
                sc *= 1 + 0.012 * math.sin(u * 4.4)
            paste(fr, lay, (x, y), a, sc, anchor)
        return fr


def unit_chip(unit, sub):
    name, key = UNITS[unit]
    col, soft = C[key]
    return pill(f'{name} · {sub}', F_CHIP, col, soft)


MOTION = {'g': 'hop', 'gm': 'hop', 'w': 'point', 'b': 'tilt'}


def std(unit, sub, title, lines, pose, icon_name=None, dur=12, line_gap=1.0):
    """標準版面：左文字、右角色。lines: str 為段落；('•', str) 為條列；('!', str) 為強調。"""
    s = Scene(title, unit, dur)
    col, soft = C[UNITS[unit][1]]
    s.add(unit_chip(unit, sub), (120, 112), 0.15)
    tl = s.add(text_layer(title, F_TITLE, INK, maxw=1080, gap=1.25), (120, 178), 0.35)
    y = 178 + tl.height + 44
    t = 1.1
    for ln in lines:
        if isinstance(ln, tuple) and ln[0] == '•':
            lay = text_layer(ln[1], F_BODY, INK, maxw=960)
            dot = Image.new('RGBA', (60, 60), (0, 0, 0, 0))
            ImageDraw.Draw(dot).ellipse((8, 24, 30, 46), fill=col)
            row = Image.new('RGBA', (lay.width + 60, lay.height), (0, 0, 0, 0))
            row.alpha_composite(dot, (0, 0)); row.alpha_composite(lay, (60, 0))
            lay = row
        elif isinstance(ln, tuple) and ln[0] == '!':
            inner = text_layer(ln[1], F_BODY_B, col, maxw=960)
            lay = Image.new('RGBA', (inner.width + 56, inner.height + 30), (0, 0, 0, 0))
            ImageDraw.Draw(lay).rounded_rectangle((0, 0, lay.width - 1, lay.height - 1), 18, fill=soft)
            lay.alpha_composite(inner, (28, 12))
        else:
            lay = text_layer(ln, F_BODY, INK, maxw=1020)
        s.add(lay, (120, y), t, 'up')
        y += lay.height + 26
        t += line_gap
    s.add(character(pose, 520), (1570, 570), 0.3, 'pop', 'c', motion=MOTION[pose])
    if icon_name:
        bub = Image.new('RGBA', (150, 150), (0, 0, 0, 0))
        ImageDraw.Draw(bub).ellipse((0, 0, 149, 149), fill=SURF, outline=col, width=5)
        bub.alpha_composite(icon(icon_name, 88, col), (31, 31))
        s.add(bub, (1290, 190), 0.9, 'pop', 'c', bob=5)
    return s


def chapter(unit, line):
    name, key = UNITS[unit]
    col, soft = C[key]
    s = Scene(f'chapter{unit}', unit, 5)
    s.layout = 'center'
    num = text_layer(f'第 {unit} 單元', Face('sans', 40, 'Bold'), col)
    s.add(num, (W / 2, 250), 0.1, 'up', 'c')
    s.add(text_layer(name, Face('wk', 190), INK), (W / 2, 400), 0.3, 'pop', 'c')
    s.add(text_layer(line, Face('wk', 56), col), (W / 2, 570), 0.8, 'up', 'c')
    pz = 'g' if unit % 2 else 'gm'
    s.add(character(pz, 300), (W / 2, 815), 0.6, 'pop', 'c', motion='hop')
    return s


# ---------- 特殊場景 ----------
def intro():
    s = Scene('intro', 0, 9)
    s.layout = 'center'
    s.add(text_layer('健康旅程攻略', Face('wk', 150), INK), (W / 2, 330), 0.3, 'pop', 'c')
    s.add(text_layer('減重・營養・運動・好習慣', Face('wk', 64), C['move'][0]), (W / 2, 480), 1.0, 'up', 'c')
    s.add(text_layer('整條路先畫給你看，關卡標清楚，一關一關破。', F_BODY, MUTED), (W / 2, 580), 1.8, 'up', 'c')
    s.add(character('g', 300), (W / 2, 812), 0.6, 'pop', 'c', motion='hop')
    xs = [380, 620, 1300, 1540]
    for i, (k, (name, key)) in enumerate(UNITS.items()):
        b = Image.new('RGBA', (170, 170), (0, 0, 0, 0))
        ImageDraw.Draw(b).ellipse((0, 0, 169, 169), fill=C[key][1])
        b.alpha_composite(icon(['flag', 'bowl', 'shoe', 'star'][i], 96, C[key][0]), (37, 37))
        s.add(b, (xs[i], 790), 2.4 + i * 0.25, 'pop', 'c', bob=4)
    return s


def outro():
    s = Scene('outro', 0, 10)
    s.layout = 'center'
    s.add(text_layer('一關一關破', Face('wk', 150), INK), (W / 2, 300), 0.3, 'pop', 'c')
    s.add(text_layer('我們陪你走', Face('wk', 110), C['move'][0]), (W / 2, 450), 1.0, 'pop', 'c')
    s.add(text_layer('有問題隨時打電話，不用等回診日', F_BODY, MUTED), (W / 2, 580), 1.8, 'up', 'c')
    s.add(character('b', 320), (W / 2, 790), 0.6, 'pop', 'c', motion='tilt')
    s.add(icon('star', 90, C['gold'][0]), (W / 2 + 230, 720), 2.2, 'pop', 'c', bob=5)
    s.add(icon('heart', 70, C['diet'][0]), (W / 2 - 230, 740), 2.5, 'pop', 'c', bob=5)
    return s


def journey_map():
    s = Scene('map', 1, 15)
    s.layout = 'full'
    col = C['move'][0]
    s.add(unit_chip(1, '破關地圖'), (120, 112), 0.15)
    s.add(text_layer('減重像破關：一共五關', F_TITLE, INK), (120, 178), 0.35)
    # 曲線（640x240 原圖放大 2.6 倍）
    k, ox, oy = 2.45, 220, 300
    def P(x, y): return (ox + x * k, oy + y * k)
    def bez(p0, p1, p2, p3, n=40):
        return [((1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t * t * p2[0] + t ** 3 * p3[0],
                 (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t * t * p2[1] + t ** 3 * p3[1])
                for t in [i / n for i in range(n + 1)]]
    pts = (bez((40, 52), (90, 55), (130, 68), (160, 88)) + bez((160, 88), (200, 115), (240, 128), (292, 131))[1:]
           + [(292 + i * 108 / 20, 131) for i in range(1, 21)]
           + bez((400, 131), (440, 132), (470, 142), (505, 150))[1:] + bez((505, 150), (545, 158), (575, 159), (600, 159))[1:])
    pts = [P(*p) for p in pts]
    seg = [0] + [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    cum = [sum(seg[:i + 1]) for i in range(len(seg))]
    total = cum[-1]
    T0, T1 = 1.2, 8.5

    # 魔王關底色與文字（靜態圖層）
    boss = Image.new('RGBA', (int(120 * k), int(170 * k)), (0, 0, 0, 0))
    ImageDraw.Draw(boss).rounded_rectangle((0, 0, boss.width - 1, boss.height - 1), 20, fill=C['gold'][1])
    def under(fr, t, ko):
        a = ease_out((t - 4.6) / 0.6) * ko
        paste(fr, boss, P(286, 18), a)
    s.custom.append(under)
    s.add(text_layer('停滯期＝魔王關', Face('wk', 46), C['diet'][0]), (P(346, 40)[0], P(346, 40)[1]), 5.0, 'up', 'c')
    labels = [('起始期', 95), ('減重期', 226), ('停滯期', 346), ('維持期', 452), ('過渡期', 565)]
    nodes = [(40, 52), (160, 88), (292, 131), (400, 131), (505, 150)]
    for i, (lab, x) in enumerate(labels):
        f = Face('sans', 34, 'Bold')
        lay = text_layer(f'第{i + 1}關', Face('sans', 26, 'Medium'), MUTED)
        s.add(lay, (P(x, 0)[0], oy + 206 * k - 6), 1.0 + i * 0.2, 'up', 'c')
        s.add(text_layer(lab, f, C['diet'][0] if i == 2 else INK), (P(x, 0)[0], oy + 206 * k + 38), 1.1 + i * 0.2, 'up', 'c')
    s.add(text_layer('會卡住，是荷爾蒙的設定，不是你不努力。', Face('wk', 52), C['diet'][0]), (W / 2, 925), 9.0, 'up', 'c')

    walker = character('g', 200)
    star = icon('star', 70, C['gold'][0])
    flagI = icon('flag', 60, col)

    def draw(fr, t, ko):
        prog = ease_out((t - T0) / (T1 - T0)) if t > T0 else 0
        d = ImageDraw.Draw(fr)
        d.line((P(40, 194)[0], P(40, 194)[1], P(600, 194)[0], P(600, 194)[1]), fill=LINE, width=3)
        if prog <= 0:
            return
        L = prog * total
        n = next((i for i, c in enumerate(cum) if c >= L), len(pts) - 1)
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        ld.line(pts[:n + 1], fill=col + (int(255 * ko),), width=12, joint='curve')
        for nx, ny in nodes:
            cx, cy = P(nx, ny)
            if cum[min(range(len(pts)), key=lambda i: math.dist(pts[i], (cx, cy)))] <= L:
                c2 = C['gold'][0] if (nx, ny) == (292, 131) else col
                ld.ellipse((cx - 15, cy - 15, cx + 15, cy + 15), fill=c2 + (int(255 * ko),))
        fr.alpha_composite(lay)
        for nx, ny in nodes:
            cx, cy = P(nx, ny)
            j = min(range(len(pts)), key=lambda i: math.dist(pts[i], (cx, cy)))
            if (nx, ny) != (292, 131) and cum[j] <= L:
                paste(fr, flagI, (cx - 8, cy - 62), ko)
        if prog > 0.98:
            paste(fr, star, P(600, 159), ko, ease_back(min(1, (t - T1) / 0.5)), 'c')
        px, py = pts[n]
        paste(fr, walker, (px, py - 6 + math.sin(t * 9) * 4), ko, 1.0, 'cb')
    s.custom.append(draw)
    return s


def walk_blocks():
    s = std(3, '每天動一動', '每天走路 30 分鐘', ['可以拆成 3 次、每次 10 分鐘——一樣算數！'],
            'gm', 'shoe', dur=12)
    col, soft = C['move']
    lbl = ['早上', '午餐後', '晚餐後']
    labs = [text_layer(f'{l}  10 分鐘', Face('sans', 36, 'Bold'), SURF) for l in lbl]
    tot = text_layer('＝ 30 分鐘 ✓'.replace(' ✓', ''), Face('wk', 64), col)
    x0, y0, bw, bh = 120, 560, 330, 96

    def draw(fr, t, ko):
        d = ImageDraw.Draw(fr)
        for i in range(3):
            x = x0 + i * (bw + 16)
            d.rounded_rectangle((x, y0, x + bw, y0 + bh), 22, fill=SURF2)
            p = ease_out((t - (3.0 + i * 1.3)) / 1.0)
            if p > 0:
                lay = Image.new('RGBA', (bw, bh), (0, 0, 0, 0))
                ImageDraw.Draw(lay).rounded_rectangle((0, 0, int(bw * p), bh - 1), 22, fill=col + (int(255 * ko),))
                fr.alpha_composite(lay, (x, y0))
                if p > 0.6:
                    paste(fr, labs[i], (x + bw / 2, y0 + bh / 2), ko * (p - 0.6) / 0.4, 1, 'c')
        if t > 7.3:
            paste(fr, tot, (x0, y0 + bh + 34), ko * ease_out((t - 7.3) / 0.5))
    s.custom.append(draw)
    return s


def checklist():
    s = Scene('tasks', 4, 15)
    col, soft = C['gold']
    s.add(unit_chip(4, '每週任務'), (120, 112), 0.15)
    s.add(text_layer('把目標變成打勾', F_TITLE, INK), (120, 178), 0.35)
    s.add(text_layer('做到就打勾，回診一起結算戰績。', F_BODY, MUTED, maxw=1100), (120, 320), 0.9)
    cd, pad = card(1040, 430)
    s.add(cd, (120 - pad, 430 - pad), 1.4, 'up')
    items = ['每餐都先吃了蛋白質', '走路 30 分鐘，達成 5 天以上', '含糖飲料換成無糖或白開水']
    lays = [text_layer(it, Face('sans', 48, 'Medium'), INK) for it in items]
    box = icon('check', 80, col)
    empty = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
    ImageDraw.Draw(empty).rounded_rectangle((4, 4, 75, 75), 16, outline=LINE, width=6)
    for i, lay in enumerate(lays):
        y = 480 + i * 128
        s.add(empty, (170, y), 1.8 + i * 0.3, 'fade')
        s.add(lay, (290, y + 8), 1.9 + i * 0.3, 'up')
        s.add(box, (210, y + 40), 5.0 + i * 1.6, 'pop', 'c')
    s.add(character('w', 480), (1560, 570), 0.3, 'pop', 'c', motion='point')
    s.add(pill('連勝中！', Face('wk', 52), SURF, col, padx=34, pady=10), (1540, 260), 9.6, 'pop', 'c', bob=4)
    return s


def streak():
    s = std(4, '連勝紀錄', '連續做到，就累積連勝', ['斷了也沒關係——明天重新開始，紀錄可以再拚。'],
            'gm', 'star', dur=12)
    col, soft = C['gold']
    big = Face('wk', 120)

    def draw(fr, t, ko):
        if t < 2.6:
            return
        n = min(9, 1 + int((t - 2.6) / 0.45))
        a = ko * ease_out((t - 2.6) / 0.4)
        chip = pill(f'戒糖飲挑戰  第 {n} 天', Face('wk', 64), INK, soft, padx=40, pady=16)
        paste(fr, chip, (120, 560), a)
        st = icon('star', 60, col)
        for i in range(n):
            paste(fr, st, (130 + i * 72, 720), a)
    s.custom.append(draw)
    return s


def red_flags():
    s = Scene('redflag', 4, 16)
    col, soft = C['flag']
    s.add(pill('用藥中的安全提醒', F_CHIP, col, soft), (120, 112), 0.15)
    s.add(text_layer('出現這些，不要等回診', F_TITLE, col), (120, 178), 0.35)
    items = ['吐到連水都喝不下', '上腹劇痛', '皮膚、眼白變黃', '心悸、冒冷汗、手抖', '小便量明顯變少']
    for i, it in enumerate(items):
        x = 120 + (i % 2) * 540
        y = 340 + (i // 2) * 120
        row = Image.new('RGBA', (510, 96), (0, 0, 0, 0))
        ImageDraw.Draw(row).rounded_rectangle((0, 0, 509, 95), 24, fill=soft)
        row.alpha_composite(icon('alert', 52, col), (24, 22))
        Face('sans', 40, 'Bold').draw(ImageDraw.Draw(row), (96, 20), it, INK)
        s.add(row, (x, y), 1.2 + i * 0.7, 'left')
    msg = pill('直接聯絡診所，或到急診就醫', Face('wk', 56), SURF, col, padx=40, pady=16)
    s.add(msg, (120, 740), 5.6, 'pop')
    s.add(character('w', 480), (1560, 570), 0.3, 'pop', 'c', motion='point')
    s.add(icon('phone', 120, col), (1290, 330), 5.8, 'pop', 'c', bob=4)
    return s


# ---------- 腳本 ----------
def build():
    return [
        intro(),
        chapter(1, '先看懂地圖，再出發'),
        journey_map(),
        std(1, '魔王關', '停滯期＝魔王關',
            ['體重卡住，是荷爾蒙在調控，不是你不努力。', ('!', '打到魔王關，代表你已經走很遠了。'), '攻略我們有——不要放棄，就是破關的關鍵。'],
            'gm', 'flag', dur=13),
        std(1, '不靠意志力', '不是在考驗意志力',
            ['用藥後覺得不太想吃？', '那是藥在把「一直想吃」的訊號關小聲，', ('!', '代表藥有在做事。'), '把力氣花在「怎麼吃」，而不是「忍住不吃」。'],
            'b', 'heart', dur=13),
        std(1, '用藥的朋友', '用藥的朋友，記住三件事',
            [('•', '每週固定同一天打，手機設好提醒'), ('•', '肚皮、大腿、上臂，輪流換位置'), ('•', '不舒服就回來討論——劑量可以商量，不要自己停藥')],
            'w', 'calendar', dur=14, line_gap=1.2),

        chapter(2, '吃對順序，比吃很少重要'),
        std(2, '吃的順序', '每餐先吃蛋白質',
            [('•', '蛋、豆腐、豆漿、魚、雞肉'), ('!', '先吃夠蛋白質，才不會瘦到肌肉。'), '吃完蛋白質，再吃青菜，最後才是飯麵。'],
            'w', 'egg', dur=13),
        std(2, '外食攻略', '外食這樣選',
            [('•', '自助餐：先夾蛋白質，再夾兩樣青菜'), ('•', '便當：炸物去皮、醬汁不淋飯'), ('•', '湯麵：麵吃一半、湯少喝幾口')],
            'b', 'bowl', dur=13, line_gap=1.2),
        std(2, '喝什麼', '含糖飲料，換成無糖',
            ['無糖茶、白開水，都是好選擇。', ('!', '胃口變小的現在，正是戒糖飲最容易成功的時機。')],
            'w', 'cup', dur=11),
        std(2, '水與纖維', '水要喝夠，青菜要夠',
            ['水少量多次喝，一天分好幾次補充。', '每餐至少一份青菜，纖維幫助腸胃順暢。'],
            'gm', 'leaf', dur=11),
        std(2, '胃不舒服時', '想吐的時候，這樣吃',
            [('•', '吃清淡、少量，吃到七分飽就停'), ('•', '油炸、濃湯、甜點在胃裡停留久，初期先少碰'), '大多數人會越來越輕，不用太擔心。'],
            'b', 'bowl', dur=13),

        chapter(3, '走得到、走得久，就是贏'),
        walk_blocks(),
        std(3, '慢慢來', '走得久，比走得快重要',
            ['從家附近、公園，或捷運提早一站下車開始。', ('!', '能持續的運動，才是好運動。')],
            'w', 'shoe', dur=11),
        std(3, '低衝擊', '膝蓋不舒服？坐著也能動',
            ['椅上抬腿：坐穩椅子，一腳伸直抬起，', '停 5 秒再放下，左右輪流各 10 下。', ('!', '看電視的時候就能做。')],
            'gm', 'chair', dur=13),
        std(3, '保住肌肉', '加一點肌力訓練',
            [('•', '靠牆半蹲、彈力帶、扶椅子起立'), ('•', '每週 2～3 次，每次 15 分鐘'), '減重時保住肌肉，代謝才不會掉。'],
            'w', 'dumbbell', dur=13),

        chapter(4, '小事天天做，就會變成習慣'),
        checklist(),
        streak(),
        std(4, '睡眠與壓力', '睡飽、少壓力，也是減重',
            [('•', '固定時間上床，睡滿 7 小時'), ('•', '壓力大想吃東西時，先喝杯水、走一走'), '睡不好，隔天會更想吃甜的。'],
            'b', 'moon', dur=13),
        std(4, '回診', '回診＝結算戰績的日子',
            ['把這週的打勾帶來，', '我們一起看你的進步，再調整下一關的打法。'],
            'g', 'chat', dur=11),
        red_flags(),
        outro(),
    ]


if __name__ == '__main__':
    sc = build()
    print(len(sc), 'scenes', sum(s.dur for s in sc), 'sec')
