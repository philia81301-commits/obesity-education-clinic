// 關鍵畫面抽查：node snap.mjs s2-d4 <輸出png> → 每句中段各一格，拼成一張縮圖總表
import { chromium } from 'playwright-core';
import ffmpegPath from 'ffmpeg-static';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, existsSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { resolve, join } from 'node:path';
import { pathToFileURL } from 'node:url';

const mod = resolve(process.argv[2] || 's2-d4');
const outPng = resolve(process.argv[3] || 'contact.png');
const timingPath = join(mod, 'timing.json');
const browser = await chromium.launch({ channel: 'msedge' });
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
await page.goto(pathToFileURL(join(mod, 'index.html')).href + '?capture');
if (existsSync(timingPath)) await page.evaluate(s => setTiming(s), JSON.parse(readFileSync(timingPath, 'utf8')).segments);
await page.evaluate(async () => { await document.fonts.load('700 96px "LXGW WenKai TC"', document.body.innerText); await document.fonts.ready; });
const times = await page.evaluate(() => [...SEG.map(([s, e]) => s + (e - s) * 0.8), totalDuration() - 0.3]);
const dir = mkdtempSync(join(tmpdir(), 'snap-'));
for (const [i, t] of times.entries()) {
  await page.evaluate(t => render(t), t);
  await page.screenshot({ path: join(dir, `f${String(i).padStart(2, '0')}.png`) });
}
await browser.close();
execFileSync(ffmpegPath, ['-hide_banner', '-loglevel', 'error', '-y', '-framerate', '1', '-i', join(dir, 'f%02d.png'),
  '-vf', 'scale=270:480,tile=6x2:padding=6:color=gray', '-frames:v', '1', outPng]);
console.log('ok', outPng, times.map(t => t.toFixed(1)).join(' '));
