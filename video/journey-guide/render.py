"""逐場景輸出 → concat → 加配樂"""
import os, subprocess, sys
from multiprocessing import Pool
import scenes
from lib import W, H, FPS

OUT = '/home/claude/video/out'
os.makedirs(OUT, exist_ok=True)


def render_one(i):
    sc = scenes.build()[i]
    n = int(round(sc.dur * FPS))
    tmp, final = f'{OUT}/s{i:02d}.tmp.mp4', f'{OUT}/s{i:02d}.mp4'
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                          '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast',
                          '-crf', '20', '-pix_fmt', 'yuv420p', '-r', str(FPS), tmp], stdin=subprocess.PIPE)
    for f in range(n):
        p.stdin.write(sc.frame(f / FPS).convert('RGB').tobytes())
    p.stdin.close()
    if p.wait() == 0:
        os.replace(tmp, final)
    return i, sc.dur


if __name__ == '__main__':
    total = len(scenes.build())
    idx = [int(a) for a in sys.argv[1:]] or list(range(total))
    with Pool(min(len(idx), os.cpu_count() or 4)) as pool:
        for i, d in pool.imap_unordered(render_one, idx):
            print('done', i, d, flush=True)
    with open(f'{OUT}/list.txt', 'w') as f:
        for i in range(total):
            f.write(f"file 's{i:02d}.mp4'\n")
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', f'{OUT}/list.txt',
                    '-c', 'copy', f'{OUT}/video_silent.mp4'], check=True)
    print('concat ok')
