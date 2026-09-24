"""旁白對齊：醫師錄音 → 每句 [開始, 結束] 秒 → timing.json ＋ 處理後旁白檔

用法：python align.py s2-d4
  讀  <模組>/逐字稿.md（「## 逐字稿」下的編號句）、<模組>/audio/narration-raw.wav
  寫  <模組>/timing.json、<模組>/audio/narration.m4a、<模組>/audio/transcript.txt（辨識結果，人工核對用）

做法：faster-whisper 逐字時間 → 與逐字稿做字元比對（difflib）→ 每句頭尾吸附到最近的停頓邊界（ffmpeg silencedetect）。
"""
import sys, re, json, subprocess, difflib, pathlib

ROOT = pathlib.Path(__file__).parent
FFMPEG = str(ROOT / 'node_modules/ffmpeg-static/ffmpeg.exe')
LEAD = 0.6      # 第一句前保留的空白（秒）
TAIL = 2.5      # 最後一句後保留（要跟 index.html 的 TAIL 一致）
SNAP = 0.45     # 吸附停頓邊界的最大距離

PUNCT = re.compile(r'[\s，。、：；？！「」『』（）()—\-…,.:;?!]')

def read_lines(mod):
    md = (mod / '逐字稿.md').read_text(encoding='utf-8')
    body = md.split('## 逐字稿', 1)[1].split('\n## ', 1)[0]
    return [re.sub(r'^\d+\.\s*', '', l).strip() for l in body.splitlines() if re.match(r'^\d+\.\s', l)]

def speech_bounds(wav):
    """silencedetect → (語音開始點清單, 語音結束點清單)"""
    out = subprocess.run([FFMPEG, '-hide_banner', '-i', str(wav), '-af', 'silencedetect=n=-42dB:d=0.25',
                          '-f', 'null', '-'], capture_output=True, text=True, encoding='utf-8', errors='ignore').stderr
    ends = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', out)]      # 靜音結束＝語音開始
    starts = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', out)]  # 靜音開始＝語音結束
    return ends, starts

def snap(t, cands):
    best = min(cands, key=lambda c: abs(c - t), default=t)
    return best if abs(best - t) <= SNAP else t

def main():
    mod = ROOT / sys.argv[1]
    lines = read_lines(mod)
    raw = mod / 'audio/narration-raw.wav'

    from faster_whisper import WhisperModel
    model = WhisperModel('small', device='cpu', compute_type='int8')
    segs, _ = model.transcribe(str(raw), language='zh', word_timestamps=True, vad_filter=False,
                               initial_prompt='以下是繁體中文的衛教旁白：' + ''.join(lines))
    chars = []   # (字, 開始, 結束)
    text_log = []
    for s in segs:
        text_log.append(f'[{s.start:6.2f}–{s.end:6.2f}] {s.text}')
        for w in s.words:
            cs = [c for c in w.word if not PUNCT.match(c)]
            if not cs: continue
            step = (w.end - w.start) / len(cs)
            for k, c in enumerate(cs):
                chars.append((c, w.start + k * step, w.start + (k + 1) * step))
    (mod / 'audio/transcript.txt').write_text('\n'.join(text_log), encoding='utf-8')

    # 逐字稿字串（去標點）與每字所屬句號
    S, owner = '', []
    for i, l in enumerate(lines):
        clean = PUNCT.sub('', l); S += clean; owner += [i] * len(clean)
    R = ''.join(c for c, _, _ in chars)
    sm = difflib.SequenceMatcher(None, S, R, autojunk=False)
    hit = {}   # 句號 → [(字開始, 字結束)]
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            hit.setdefault(owner[a + k], []).append(chars[b + k][1:])

    on, off = speech_bounds(raw)
    out, report = [], []
    for i, l in enumerate(lines):
        h = hit.get(i, [])
        cover = len(h) / len(PUNCT.sub('', l))
        if not h:
            sys.exit(f'第 {i+1} 句完全對不到，請看 audio/transcript.txt')
        s, e = snap(min(x for x, _ in h), on), snap(max(y for _, y in h), off)
        out.append([s, e]); report.append(f'{i+1:2d}. {s:6.2f}–{e:6.2f}  吻合 {cover:4.0%}  {l}')
    for i in range(1, len(out)):          # 保證不重疊
        if out[i][0] < out[i-1][1]: out[i][0] = out[i-1][1] + 0.05

    t0 = max(0, out[0][0] - LEAD); t1 = out[-1][1] + TAIL
    seg_rel = [[round(s - t0, 3), round(e - t0, 3)] for s, e in out]
    # 降噪＋人聲頻段＋響度標準化（-16 LUFS，手機／社群常用）
    subprocess.run([FFMPEG, '-hide_banner', '-loglevel', 'error', '-y', '-ss', f'{t0:.3f}', '-to', f'{t1:.3f}',
                    '-i', str(raw), '-af',
                    'highpass=f=80,afftdn=nf=-45,loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=in:d=0.15,'
                    f'afade=t=out:st={t1 - t0 - 0.6:.3f}:d=0.6',
                    '-ar', '48000', '-c:a', 'aac', '-b:a', '160k', str(mod / 'audio/narration.m4a')], check=True)
    (mod / 'timing.json').write_text(json.dumps({'audio': 'audio/narration.m4a', 'segments': seg_rel},
                                                ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'裁切原始錄音 {t0:.2f}–{t1:.2f} 秒，成片約 {t1 - t0:.1f} 秒')
    print('\n'.join(report))

if __name__ == '__main__':
    main()
