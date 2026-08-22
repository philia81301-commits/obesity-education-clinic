#!/usr/bin/env node
/**
 * 把 content/*.md 轉成 docs/ 底下的靜態網站（GitHub Pages 用）。
 * 零相依：自己寫的極簡 markdown 轉換，只支援本專案實際用到的語法。
 * 用法：node tools/build-site.js
 */
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const CONTENT = path.join(ROOT, 'content');
const DOCS = path.join(ROOT, 'docs');

/** 冊目錄：檔名 → 輸出網址、標題、關卡標籤 */
const BOOKS = [
  { md: '01-起始期.md', slug: 's1', level: '第 1 關', title: '起始期', desc: '開始注射 0–4 週，劑量爬升初期。安全度過副作用、建立蛋白質與步行的基礎。' },
  { md: '02-減重期.md', slug: 's2', level: '第 2 關', title: '減重期', desc: '體重穩定下降期。食量最小、掉最順的黃金期，重點是「掉的是脂肪不是肌肉」。' },
  { md: '03-停滯期.md', slug: 's3', level: '魔王關', title: '停滯期', desc: '體重停滯、飢餓感回升。核心訓練與飢餓感因應工具全套上場。', boss: true },
  { md: '04-維持期.md', slug: 's4', level: '第 4 關', title: '維持期', desc: '達標後的體重維持。警戒線制度、72 小時回正軌、運動變主角。' },
  { md: '05-停藥減藥過渡期.md', slug: 's5', level: '第 5 關', title: '停藥／減藥過渡期', desc: '復胖風險最高期。停藥前檢核、恢復用藥去汙名化、計畫懷孕軌道。' },
  { md: '06-更年期女性專項.md', slug: 'm', level: '差異冊', title: '更年期女性專項', desc: '跨階段適用。荷爾蒙與婦科整合、情緒壓力因應、居家運動與漏尿注意。' },
];

const REFS = [
  { md: 'ref-高CP值蛋白質清單.md', slug: 'ref-protein', title: '高 CP 值蛋白質清單', desc: '比價總表（NT$/10g 蛋白質）＋超商／自助餐／超市／吃不下時四場景採買清單。' },
  { md: 'ref-高纖低GI早餐.md', slug: 'ref-breakfast', title: '高纖低 GI 早餐指南', desc: '台式早餐地雷表與可選表、三場景組合、GI 機轉；含三個「假健康」陷阱。' },
];

/* ---------- 極簡 markdown → HTML ---------- */
function esc(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function inline(s) {
  return esc(s)
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
    .replace(/(^|[^"'>=\w])(https?:\/\/[^\s<)]+)/g, '$1<a href="$2" target="_blank" rel="noopener">$2</a>');
}

function mdToHtml(md) {
  const lines = md.split(/\r?\n/);
  const out = [];
  let i = 0;
  let listType = null;

  const closeList = () => { if (listType) { out.push(`</${listType}>`); listType = null; } };

  while (i < lines.length) {
    const line = lines[i];

    if (/^\s*$/.test(line)) { closeList(); i++; continue; }

    // 表格
    if (/^\|/.test(line) && /^\|[\s:|-]+\|$/.test(lines[i + 1] || '')) {
      closeList();
      const cells = r => r.split('|').slice(1, -1).map(c => inline(c.trim()));
      const head = cells(line);
      i += 2;
      const rows = [];
      while (i < lines.length && /^\|/.test(lines[i])) { rows.push(cells(lines[i])); i++; }
      out.push('<div class="tw"><table><thead><tr>' + head.map(c => `<th>${c}</th>`).join('') +
        '</tr></thead><tbody>' + rows.map(r => '<tr>' + r.map(c => `<td>${c}</td>`).join('') + '</tr>').join('') +
        '</tbody></table></div>');
      continue;
    }

    // 標題
    const h = line.match(/^(#{1,4})\s+(.*)$/);
    if (h) {
      closeList();
      const lvl = h[1].length;
      const text = inline(h[2]);
      const id = h[2].replace(/[^\w一-鿿-]/g, '').slice(0, 40);
      out.push(`<h${lvl} id="${id}">${text}</h${lvl}>`);
      i++; continue;
    }

    // 引言區塊
    if (/^>\s?/.test(line)) {
      closeList();
      const buf = [];
      while (i < lines.length && /^>\s?/.test(lines[i])) { buf.push(inline(lines[i].replace(/^>\s?/, ''))); i++; }
      out.push(`<blockquote>${buf.join('<br>')}</blockquote>`);
      continue;
    }

    // 分隔線
    if (/^---+$/.test(line)) { closeList(); out.push('<hr>'); i++; continue; }

    // 清單
    const li = line.match(/^(\s*)([-*]|\d+\.)\s+(.*)$/);
    if (li) {
      const want = /^\d/.test(li[2]) ? 'ol' : 'ul';
      if (listType !== want) { closeList(); out.push(`<${want}>`); listType = want; }
      let text = li[3];
      // 續行（縮排的接續內容）
      while (i + 1 < lines.length && /^\s{2,}\S/.test(lines[i + 1]) && !/^\s*([-*]|\d+\.)\s/.test(lines[i + 1])) {
        i++; text += '<br>' + lines[i].trim();
      }
      out.push(`<li>${inline(text)}</li>`);
      i++; continue;
    }

    closeList();
    out.push(`<p>${inline(line)}</p>`);
    i++;
  }
  closeList();
  return out.join('\n');
}

/* ---------- 版型 ---------- */
const CSS = `
:root{
  --ink:#21281F; --muted:#66705F; --line:#DFDFD4; --paper:#FBFAF4;
  --diet:#C2620A; --diet-soft:#FCE9D4;
  --move:#0A8A4D; --move-soft:#DCF3E5;
  --rx:#3563C9;   --rx-soft:#E1E9FB;
  --flag:#C82D1B;
  --gold:#9A6B2A; --gold-soft:#F5EDDD;
}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);
  font-family:"Noto Sans TC","Microsoft JhengHei",sans-serif;line-height:1.75;
  background-image:linear-gradient(180deg,#fff 0,var(--paper) 420px)}
.kai{font-family:"LXGW WenKai TC","DFKai-SB",serif}
a{color:var(--rx)}
.wrap{max-width:940px;margin:0 auto;padding:0 20px}

/* 頁首 */
.top{border-bottom:1px solid var(--line);background:rgba(255,255,255,.9);
  position:sticky;top:0;z-index:9;backdrop-filter:blur(6px)}
.top .wrap{display:flex;align-items:center;gap:14px;height:56px;font-size:14px}
.top a{color:var(--muted);text-decoration:none}
.top a:hover{color:var(--ink)}
.top .home{font-weight:700;color:var(--ink)}
.top .sp{flex:1}

/* hero */
.hero{padding:44px 0 26px}
.hero h1{font-family:"LXGW WenKai TC",serif;font-size:32px;margin:0 0 10px;letter-spacing:.02em}
.hero p{margin:0;color:var(--muted);font-size:15px;max-width:62ch}
.pill{display:inline-block;background:var(--gold-soft);color:var(--gold);
  border-radius:99px;padding:2px 13px;font-size:12.5px;font-weight:700;letter-spacing:.06em;margin-bottom:12px}

/* 卡片 */
.sec{margin:34px 0 10px;font-size:13px;font-weight:700;letter-spacing:.12em;color:var(--muted)}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(268px,1fr));gap:16px}
.card{display:block;background:#fff;border:1px solid var(--line);border-radius:12px;
  padding:18px 20px;text-decoration:none;color:inherit;transition:.16s;position:relative;overflow:hidden}
.card:hover{transform:translateY(-2px);box-shadow:0 8px 22px rgba(0,0,0,.09);border-color:#C9C9BA}
.card .lv{font-size:11.5px;font-weight:700;letter-spacing:.08em;color:var(--move)}
.card.boss .lv{color:var(--flag)}
.card.ref .lv{color:var(--gold)}
.card h3{margin:5px 0 7px;font-size:18px;font-family:"LXGW WenKai TC",serif}
.card p{margin:0;font-size:13.5px;color:var(--muted);line-height:1.65}
.card::after{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--move)}
.card.boss::after{background:var(--flag)}
.card.ref::after{background:var(--gold)}
.card.sheet::after{background:var(--diet)}
.card.sheet .lv{color:var(--diet)}

/* 內文 */
article{background:#fff;border:1px solid var(--line);border-radius:14px;
  padding:34px 40px 44px;margin:26px 0 40px}
article h1{font-family:"LXGW WenKai TC",serif;font-size:27px;margin:0 0 6px;padding-bottom:14px;border-bottom:2px solid var(--ink)}
article h2{font-family:"LXGW WenKai TC",serif;font-size:20px;margin:34px 0 10px;
  padding-left:11px;border-left:5px solid var(--move)}
article h3{font-size:16.5px;margin:24px 0 6px;color:var(--diet);letter-spacing:.01em}
article h4{font-size:14.5px;margin:16px 0 4px}
article p{margin:.5em 0}
article ul,article ol{padding-left:1.35em;margin:.5em 0}
article li{margin:.3em 0}
article blockquote{margin:16px 0;padding:12px 18px;background:var(--gold-soft);
  border-radius:8px;color:#5A4520;font-size:14px}
article hr{border:0;border-top:1px solid var(--line);margin:30px 0}
article code{background:#F0F0E7;border-radius:4px;padding:1px 5px;font-size:.9em}
article strong{font-weight:700}
.tw{overflow-x:auto;margin:14px 0}
table{border-collapse:collapse;width:100%;font-size:13.5px;min-width:460px}
th,td{border:1px solid var(--line);padding:7px 10px;text-align:left;vertical-align:top}
th{background:#F4F4EC;font-weight:700;white-space:nowrap}

/* 頁尾 */
footer{border-top:1px solid var(--line);margin-top:20px;padding:26px 0 46px;
  font-size:13px;color:var(--muted)}
footer b{color:var(--ink)}
.warn{background:#FDECEA;border-left:4px solid var(--flag);border-radius:8px;
  padding:13px 17px;font-size:13.5px;margin:20px 0;color:#7A2016}

@media(max-width:640px){
  .hero h1{font-size:26px}
  article{padding:24px 20px 32px;border-radius:10px}
  article h1{font-size:22px}
}
`;

function page({ title, body, crumb = '', desc = '' }) {
  return `<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(title)}</title>
<meta name="description" content="${esc(desc)}">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=LXGW+WenKai+TC:wght@400;700&family=Noto+Sans+TC:wght@400;500;700&display=swap">
<style>${CSS}</style>
</head>
<body>
<nav class="top"><div class="wrap">
  <a class="home" href="./">GLP-1 減重衛教</a>
  <span class="sp"></span>
  ${crumb}
  <a href="https://philia81301-commits.github.io/">← 工具集首頁</a>
</div></nav>
${body}
<footer><div class="wrap">
  <b>潘湘如醫師｜家醫科</b>　·　GLP-1 RA／GIP 週製劑減重治療衛教內容體系<br>
  本站內容為衛教參考，不能取代個別醫療評估；用藥與劑量調整請與您的醫師討論。<br>
  原始碼與更新紀錄：<a href="https://github.com/philia81301-commits/obesity-education-clinic">GitHub</a>
</div></footer>
</body>
</html>`;
}

/* ---------- 產出 ---------- */
fs.mkdirSync(DOCS, { recursive: true });
fs.mkdirSync(path.join(DOCS, 'sheets'), { recursive: true });

let built = 0;
for (const b of [...BOOKS, ...REFS]) {
  const src = path.join(CONTENT, b.md);
  if (!fs.existsSync(src)) { console.warn(`  ⚠ 找不到 ${b.md}，略過`); continue; }
  const md = fs.readFileSync(src, 'utf8');
  const crumb = `<a href="./">總覽</a><span style="color:#C9C9BA">/</span><span>${esc(b.title)}</span>`;
  const html = page({
    title: `${b.title}｜GLP-1 減重衛教`,
    desc: b.desc,
    crumb,
    body: `<div class="wrap"><article>${mdToHtml(md)}</article></div>`,
  });
  fs.writeFileSync(path.join(DOCS, `${b.slug}.html`), html, 'utf8');
  built++;
}

// 衛教單（直接複製既有 A4 HTML）
const SHEETS = [
  { file: '衛教單-S1起始期-A4.html', out: 's1-a4.html', title: 'S1 起始期 A4 衛教單' },
];
const sheetLinks = [];
for (const s of SHEETS) {
  const src = path.join(ROOT, 'design', s.file);
  if (!fs.existsSync(src)) { console.warn(`  ⚠ 找不到衛教單 ${s.file}，略過`); continue; }
  fs.copyFileSync(src, path.join(DOCS, 'sheets', s.out));
  sheetLinks.push(s);
}

// 首頁
const cardHtml = (cls, lv, title, desc, href) =>
  `<a class="card ${cls}" href="${href}"><span class="lv">${lv}</span><h3>${title}</h3><p>${desc}</p></a>`;

const home = page({
  title: 'GLP-1 減重治療衛教內容體系｜潘湘如醫師',
  desc: 'GLP-1 RA／GIP 週製劑減重治療的分階段飲食運動衛教：起始期、減重期、停滯期、維持期、停藥過渡期，含更年期女性專項與診間衛教單。',
  crumb: '',
  body: `<div class="wrap">
  <div class="hero">
    <span class="pill">診間衛教內容體系</span>
    <h1>打針之後，怎麼吃、怎麼動</h1>
    <p>GLP-1 RA／GIP 週製劑（週纖達、猛健樂）減重治療的分階段衛教。依治療旅程分五關，加一冊更年期女性專項與兩份共用採買清單；每個模組都有病人版、醫師備註與依據出處。</p>
  </div>

  <div class="sec">治療旅程五關</div>
  <div class="cards">
    ${BOOKS.filter(b => b.slug !== 'm').map(b =>
      cardHtml(b.boss ? 'boss' : '', b.level, b.title, b.desc, `${b.slug}.html`)).join('\n    ')}
  </div>

  <div class="sec">差異冊與共用清單</div>
  <div class="cards">
    ${cardHtml('ref', '差異冊', BOOKS.find(b => b.slug === 'm').title, BOOKS.find(b => b.slug === 'm').desc, 'm.html')}
    ${REFS.map(r => cardHtml('ref', '共用清單', r.title, r.desc, `${r.slug}.html`)).join('\n    ')}
  </div>

  ${sheetLinks.length ? `<div class="sec">診間可列印衛教單（A4）</div>
  <div class="cards">
    ${sheetLinks.map(s => cardHtml('sheet', 'A4 可列印', s.title, '一頁式個人化衛教單：飲食／運動／藥物三區塊＋本週任務＋紅旗症狀。開啟後直接列印。', `sheets/${s.out}`)).join('\n    ')}
  </div>` : ''}

  <div class="warn">
    <b>給病人的提醒</b>：本站是衛教參考資料，內容以一般情況撰寫。您的劑量、用藥調整、停藥時機都需要由您的醫師依個人狀況評估——出現嚴重嘔吐、劇烈腹痛、皮膚眼白變黃、心悸冒冷汗等情況，請不要等回診，直接就醫。
  </div>
</div>`,
});
fs.writeFileSync(path.join(DOCS, 'index.html'), home, 'utf8');
fs.writeFileSync(path.join(DOCS, '.nojekyll'), '', 'utf8');

console.log(`✅ 已產出 docs/：${built} 篇內容頁、${sheetLinks.length} 張衛教單、1 個首頁`);
