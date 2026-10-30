"""輕快版背景音樂：120 BPM、大調、鼓組＋拍手＋烏克麗麗刷弦＋鐵琴旋律（全部程式合成）"""
import sys, wave
import numpy as np

SR = 44100
dur = float(sys.argv[1]) if len(sys.argv) > 1 else 271
out = sys.argv[2] if len(sys.argv) > 2 else 'out/bgm_upbeat.wav'
BPM = 120
beat = 60 / BPM
bar = beat * 4
N = int(dur * SR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(3)


def hz(m): return 440 * 2 ** ((m - 69) / 12)


def add(sig, t0, pan=0.0, g=1.0):
    i = int(t0 * SR)
    if i >= N: return
    j = min(N, i + len(sig))
    L[i:j] += sig[:j - i] * g * (1 - max(0, pan))
    R[i:j] += sig[:j - i] * g * (1 + min(0, pan))


def tt(sec): return np.arange(int(sec * SR)) / SR


def kick():
    t = tt(0.35)
    f = 110 * np.exp(-t * 18) + 45
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)


def clap():
    t = tt(0.22)
    n = rng.standard_normal(len(t))
    n = np.convolve(n, np.ones(6) / 6, 'same') - np.convolve(n, np.ones(40) / 40, 'same')  # 帶通
    env = np.exp(-t * 22)
    for d in (0.0, 0.011, 0.022):  # 多次拍手感
        k = int(d * SR); env[k:] += 0.6 * np.exp(-(t[:len(t) - k]) * 60)
    return n * env * 0.9


def hat(open_=False):
    t = tt(0.18 if open_ else 0.05)
    n = rng.standard_normal(len(t))
    n = n - np.convolve(n, np.ones(4) / 4, 'same')
    return n * np.exp(-t * (18 if open_ else 70)) * 0.35


def bass(m, length):
    t = tt(length)
    f = hz(m)
    s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)
    return s * np.minimum(1, t / 0.005) * np.exp(-t * 3.5)


def uke(m, length=0.5, amp=1.0):
    t = tt(length)
    f = hz(m)
    s = sum((0.6 ** k) * np.sin(2 * np.pi * f * (k + 1) * t) * np.exp(-t * (6 + 4 * k)) for k in range(4))
    return amp * s * np.minimum(1, t / 0.002)


def glock(m, length=0.9, amp=1.0):
    t = tt(length)
    f = hz(m)
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 10)
    return amp * s * np.exp(-t * 4.5) * np.minimum(1, t / 0.002)


# I – V – vi – IV （C G Am F）
chords = [[60, 64, 67], [59, 62, 67], [57, 60, 64], [57, 60, 65]]
roots = [36, 43, 45, 41]
# 兩段旋律輪流（八分音符格，None = 休止）
melA = [[72, None, 76, None, 79, 76, None, 74], [74, None, 71, None, 74, None, 79, None],
        [72, None, 76, 72, None, 69, None, 72], [69, None, 72, 77, None, 76, 74, None]]
melB = [[79, 79, None, 76, None, 74, 76, None], [74, None, 79, None, 78, 79, None, None],
        [76, None, 72, None, 76, 79, None, 81], [81, 79, None, 77, 76, None, 74, None]]
strum = [1, 0, 1, 1, 0, 1, 1, 0]  # 烏克麗麗刷弦節奏（島嶼節拍）

nbar = int(np.ceil(dur / bar))
for b in range(nbar):
    c = b % 4
    t0 = b * bar
    section = (b // 8) % 4          # 每 8 小節換一段，營造起伏
    intro = b < 2
    # 鼓
    for k in range(4):
        add(kick(), t0 + k * beat, g=0.9 if not intro else 0.0)
        if k % 2 == 1 and not intro:
            add(clap(), t0 + k * beat, g=0.55)
    for k in range(8):
        add(hat(open_=(k % 4 == 3)), t0 + k * beat / 2, pan=0.3, g=0.0 if intro else 1.0)
    # 貝斯：根音＋八度跳
    for k, (off, ln) in enumerate([(0, .45), (1.5, .3), (2, .45), (3.5, .3)]):
        add(bass(roots[c] + (12 if k % 2 else 0), ln), t0 + off * beat, g=0.55)
    # 烏克麗麗
    for k in range(8):
        if strum[k]:
            for j, m in enumerate(chords[c]):
                add(uke(m, 0.45, 0.16 if k % 2 == 0 else 0.11), t0 + k * beat / 2 + j * 0.008, pan=-0.35)
    # 鐵琴旋律（第 2、4 段才出現，避免一直搶戲）
    if section in (1, 3) or (section == 2 and b % 2 == 0):
        mel = (melA if section != 3 else melB)[c]
        for k, m in enumerate(mel):
            if m:
                add(glock(m, 0.8, 0.22), t0 + k * beat / 2, pan=0.25)

mix = np.stack([L, R], 1)
# 輕殘響
d = int(0.17 * SR)
mix[d:] += 0.18 * mix[:-d].copy()
fade = int(1.5 * SR)
mix[:fade] *= np.linspace(0, 1, fade)[:, None]
mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.4) * 0.6   # 柔和壓縮
pcm = (mix * 32767).astype(np.int16)
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('ok', dur)
