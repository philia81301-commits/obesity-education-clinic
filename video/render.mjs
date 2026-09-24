// 逐格截圖輸出影片：node render.mjs s2-d4
// 用本機 Edge（playwright-core channel=msedge）開 <模組>/index.html?capture，
// 每格呼叫頁面的 render(t) 後截圖，串流給 ffmpeg 編成 H.264；有 timing.json 就合上旁白。
import { chromium } from 'playwright-core';
import ffmpegPath from 'ffmpeg-static';
import { spawn } from 'node:child_process';
import { existsSync, readFileSync } from 'node:fs';
import { resolve, join } from 'node:path';
import { pathToFileURL } from 'node:url';

const mod = resolve(process.argv[2] || 's2-d4');
const FPS = 30;
const timingPath = join(mod, 'timing.json');
const timing = existsSync(timingPath) ? JSON.parse(readFileSync(timingPath, 'utf8')) : null;
const audio = timing?.audio ? join(mod, timing.audio) : null;
const out = join(mod, timing ? 'out/s2-d4.mp4' : 'out/s2-d4-preview-silent.mp4');

const browser = await chromium.launch({ channel: 'msedge' });
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
await page.goto(pathToFileURL(join(mod, 'index.html')).href + '?capture');
if (timing) await page.evaluate(s => setTiming(s), timing.segments);
// 等字型：Google Fonts 的中文字型按字切子集，先把畫面上用到的字全部載入
await page.evaluate(async () => {
  const text = document.body.innerText + LINES.join('');
  await Promise.all(['700 96px "LXGW WenKai TC"', '700 48px "Noto Sans TC"', '900 48px "Noto Sans TC"', '500 48px "Noto Sans TC"']
    .map(f => document.fonts.load(f, text)));
  await document.fonts.ready;
  await Promise.all([...document.images].map(i => i.complete || new Promise(r => (i.onload = r))));
});
const dur = await page.evaluate(() => totalDuration());
const frames = Math.ceil(dur * FPS);

const args = ['-hide_banner', '-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-'];
if (audio) args.push('-i', audio);
args.push('-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', String(FPS));
if (audio) args.push('-c:a', 'aac', '-b:a', '160k', '-shortest');
args.push('-movflags', '+faststart', out);
await import('node:fs').then(fs => fs.mkdirSync(join(mod, 'out'), { recursive: true }));
const ff = spawn(ffmpegPath, args, { stdio: ['pipe', 'inherit', 'inherit'] });

const t0 = Date.now();
for (let f = 0; f < frames; f++) {
  await page.evaluate(t => render(t), f / FPS);
  const buf = await page.screenshot({ type: 'jpeg', quality: 94 });
  if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  if (f % 150 === 0) console.log(`${f}/${frames} 格（${((Date.now() - t0) / 1000).toFixed(0)} 秒）`);
}
ff.stdin.end();
await new Promise(r => ff.on('close', r));
await browser.close();
console.log(`完成：${out}（${dur.toFixed(1)} 秒，${frames} 格）`);
