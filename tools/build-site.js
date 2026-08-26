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

/** 章節闖關小遊戲：每冊 5 題四選一，題目與解說全部出自該冊已審定的病人版內容 */
const QUIZ = {
  s1: {
    mascot: '🐣', name: '新手村五連闖', badge: '新手村畢業生',
    next: { href: 's2.html', label: '前往第 2 關：減重期 →' },
    qs: [
      { q: '胃口變小，每餐第一口先吃？', o: ['白飯', '水果', '蛋白質', '冰淇淋'], a: 2,
        w: '蛋、豆腐、魚、雞肉先吃夠，才不會瘦到肌肉。' },
      { q: '每天的水至少要喝多少？', o: ['500 毫升', '2000 毫升', '喝湯就好', '口渴再喝'], a: 1,
        w: '食量變小水常跟著變少，分次小口喝到 2000 毫升。' },
      { q: '每週打針日怎麼安排最好？', o: ['想到才打', '每天換時間', '痛了就停', '固定同一天'], a: 3,
        w: '固定星期幾最不容易漏打，肚皮、大腿、上臂輪流換位置。' },
      { q: '這個月的運動目標是什麼？', o: ['每天走路 30 分鐘', '每天跑 5 公里', '週末爬山一次', '先不用動'], a: 0,
        w: '可以拆成 3 次、每次 10 分鐘——走得到比走得快重要。' },
      { q: '皮膚眼白變黃，該怎麼做？', o: ['等下次回診', '多喝水觀察', '直接就醫', '自己停藥就好'], a: 2,
        w: '這是紅旗症狀——不要等回診，直接聯絡診所或就醫。' },
    ],
  },
  s2: {
    mascot: '🐿️', name: '黃金期五連闖', badge: '黃金期戰士',
    next: { href: 's3.html', label: '挑戰魔王關：停滯期 →' },
    qs: [
      { q: '體重掉太快，最怕流失什麼？', o: ['水分', '肌肉', '脂肪', '鈣質'], a: 1,
        w: '肌肉掉了代謝跟著降——穩穩掉脂肪才是真的贏。' },
      { q: '外食餐盤，蔬菜要佔多少？', o: ['四分之一', '三分之一', '一半', '不用蔬菜'], a: 2,
        w: '菜半盤、豆魚蛋肉四分之一、飯最多四分之一。' },
      { q: '兩餐之間嘴饞，第一步先？', o: ['先喝水', '吃點餅乾', '喝含糖飲料', '忍到頭暈'], a: 0,
        w: '先喝水，再檢查上一餐蛋白質有沒有吃夠。' },
      { q: '快走要走到什麼程度才夠？', o: ['能唱歌', '微喘還能講話', '喘到說不出話', '不流汗就好'], a: 1,
        w: '「微喘、能講話但沒辦法唱歌」就是剛好的中等強度。' },
      { q: '一週掉超過幾公斤要回報？', o: ['0.5 公斤', '1 公斤', '1.5 公斤', '3 公斤'], a: 2,
        w: '連續掉太快會流失肌肉，也會增加膽結石的機會。' },
    ],
  },
  s3: {
    mascot: '🐉', name: '魔王關五連闖', badge: '魔王剋星',
    next: { href: 's4.html', label: '前往第 4 關：維持期 →' },
    qs: [
      { q: '體重卡住，最不該做的是？', o: ['回診討論', '吃得更少', '肌力加量', '把步數找回來'], a: 1,
        w: '越餓煞車踩得越死——代謝降更多、之後反彈更大。' },
      { q: '停滯期主要是誰在搞鬼？', o: ['你不夠努力', '藥完全失效', '賀爾蒙調控', '天氣太熱'], a: 2,
        w: '瘦體素變少、飢餓素變多——是生理現象，不是你失敗。' },
      { q: '分不清真餓還是嘴饞，先？', o: ['直接吃再說', '喝水等 15 分鐘', '買鹽酥雞', '餓就是餓'], a: 1,
        w: '真餓不會消失；嘴饞多半 15 分鐘就自己過去了。' },
      { q: '核心菜單「沒有」哪個動作？', o: ['橋式', '棒式', '仰臥起坐', '死蟲式'], a: 2,
        w: '菜單是橋式、死蟲式、鳥狗式、棒式——記得正常呼吸不憋氣。' },
      { q: '防宵夜的第一道防線是？', o: ['晚餐蛋白質吃夠', '忍耐到睡著', '多囤零食', '喝含糖飲料'], a: 0,
        w: '晚餐沒吃夠晚上一定餓；再加上家裡不囤零食、提早上床。' },
    ],
  },
  s4: {
    mascot: '🐢', name: '守關五連闖', badge: '守成高手',
    next: { href: 's5.html', label: '前往第 5 關：停藥過渡期 →' },
    qs: [
      { q: '體重警戒線是比目標多幾公斤？', o: ['2 公斤', '5 公斤', '1 公斤', '10 公斤'], a: 0,
        w: '碰線就做三件事：盤點聚餐、運動補量、提早回診。' },
      { q: '聚餐吃多了，多久內回正軌？', o: ['24 小時', '72 小時', '一星期', '下個月'], a: 1,
        w: '三天內回到正常吃法，體重多半自己回落。' },
      { q: '維持期的主角是誰？', o: ['藥物', '節食', '運動', '斷食'], a: 2,
        w: '減重靠飲食七分，維持靠運動和習慣——量不減、變日常。' },
      { q: '達標了可以自己停藥嗎？', o: ['可以馬上停', '偷偷減量', '跟醫師討論', '丟掉針就好'], a: 2,
        w: '飢餓賀爾蒙還在，自己默默停藥復胖風險最高。' },
      { q: '維持期多久量一次體重？', o: ['每天三次', '每週固定一次', '每月一次', '都不用量'], a: 1,
        w: '每週固定同一天、同一時間量——日波動不用緊張。' },
    ],
  },
  s5: {
    mascot: '🦋', name: '畢業五連闖', badge: '畢業旅人',
    next: { href: './', label: '回到總覽，看看你的徽章 →' },
    qs: [
      { q: '停藥後食慾變大代表？', o: ['你退步了', '正常生理反應', '藥白打了', '意志力差'], a: 1,
        w: '賀爾蒙還在——把這一路學的工具全部拿出來用。' },
      { q: '過渡期多久量一次體重？', o: ['每週 1–2 次', '每月一次', '不用量', '想到才量'], a: 0,
        w: '監測加密，碰到警戒線就提早回診。' },
      { q: '過渡期運動唯一的目標？', o: ['破紀錄', '不中斷', '練出腹肌', '跑馬拉松'], a: 1,
        w: '狀態差就做保底版：10 分鐘核心或 15 分鐘快走。' },
      { q: '復胖碰到警戒線，該？', o: ['不好意思躲起來', '自己重新打針', '回診找醫師', '放棄'], a: 2,
        w: '回來就好——恢復用藥不是失敗，是計畫的一部分。' },
      { q: '想懷孕的人第一步是？', o: ['先偷偷備孕', '提前告訴醫師', '自己停藥', '上網查就好'], a: 1,
        w: '需要提前規劃停藥時程——先規劃再備孕，母嬰都安全。' },
    ],
  },
  m: {
    mascot: '🌸', name: '女王五連闖', badge: '不敗女王',
    next: { href: './', label: '回到總覽，看看你的徽章 →' },
    qs: [
      { q: '更年期後脂肪最愛搬去哪？', o: ['手臂', '大腿', '肚子', '臉頰'], a: 2,
        w: '荷爾蒙讓脂肪往肚子搬家——這不是你的錯，我們有對策。' },
      { q: '這個階段運動的主角是？', o: ['肌力訓練', '慢跑', '拉筋', '散步'], a: 0,
        w: '一次顧三件事：肌肉（代謝）、骨頭（密度）、平衡（防跌倒）。' },
      { q: '每天鈣質目標大約多少？', o: ['100 毫克', '500 毫克', '1000 毫克', '3000 毫克'], a: 2,
        w: '大約等於每天 1.5–2 份奶類或高鈣豆製品。' },
      { q: '停經後又出血，該怎麼辦？', o: ['正常不用理', '就醫檢查', '觀察半年', '多喝水'], a: 1,
        w: '多數不是大事，但一定要檢查；乳房摸到硬塊也一樣。' },
      { q: '壓力大想吃的第一步？', o: ['先吃再說', '離開現場走 10 分鐘', '買零食囤著', '硬忍'], a: 1,
        w: '動一動本身就是紓壓，常常走完就不想吃了。' },
    ],
  },
};

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

/** 回傳 { html, headings }；headings 供產生頁內目錄 */
function mdToHtml(md) {
  const lines = md.split(/\r?\n/);
  const out = [];
  const headings = [];
  const usedIds = new Set();
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
      let id = h[2].replace(/[^\w一-鿿-]/g, '').slice(0, 40) || `h${headings.length}`;
      while (usedIds.has(id)) id += '-';   // 去重，避免同名標題錨點衝突
      usedIds.add(id);
      if (lvl === 2 || lvl === 3) {
        headings.push({ lvl, id, text: h[2].replace(/\*\*/g, '') });
      }
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
      // 醫師備註／出處：標記為醫護專用，預設收起（病人掃 QR 只看病人版）
      const liHtml = inline(text);
      const isDoc = /^<strong>(醫師備註|出處)<\/strong>/.test(liHtml);
      out.push(`<li${isDoc ? ' class="docnote"' : ''}>${liHtml}</li>`);
      i++; continue;
    }

    closeList();
    out.push(`<p>${inline(line)}</p>`);
    i++;
  }
  closeList();
  return { html: out.join('\n'), headings };
}

/** 判斷 h2 段落是否為醫護專用（整段收起） */
function isDocSection(text) {
  const t = text.replace(/<[^>]+>/g, '').trim();
  return /醫師講解層|醫師備註|依據總表|組裝範例/.test(t) || t === '出處';
}

/** 把醫護專用的 h2 段落（含其後內容直到下一個 h2）包進 .docsec */
function wrapDocSections(html) {
  return html.split(/(?=<h2 )/).map(chunk => {
    const m = chunk.match(/^<h2[^>]*>([\s\S]*?)<\/h2>/);
    if (!m || !isDocSection(m[1])) return chunk;
    return `<div class="docsec">${chunk}</div>`;
  }).join('');
}

/** 由 headings 產生兩層目錄：h2 為段落、h3 為該段落底下的模組 */
function buildToc(headings) {
  const secs = [];
  for (const h of headings) {
    if (h.lvl === 2) secs.push({ ...h, kids: [] });
    else if (secs.length) secs[secs.length - 1].kids.push(h);
  }
  if (secs.length < 2) return '';
  // 模組標題在「：」或「（」處截短——目錄要能掃，不是把內文再抄一遍
  const shorten = t => t.split(/[：（(]/)[0].trim();
  const rows = secs.map(s => {
    const kids = s.kids.length
      ? `<div class="toc-k">${s.kids.map(k => `<a href="#${k.id}">${esc(shorten(k.text))}</a>`).join('')}</div>`
      : '';
    const cls = isDocSection(s.text) ? ' docsec' : '';
    return `<div class="toc-s${cls}"><a class="toc-h" href="#${s.id}">${esc(s.text)}</a>${kids}</div>`;
  }).join('');
  return `<nav class="toc"><div class="toc-t">本頁內容</div>${rows}</nav>`;
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
  font-family:"Noto Sans TC","Microsoft JhengHei",sans-serif;
  font-size:17px;line-height:1.78;   /* 長文閱讀：內文 17px */
  background-image:linear-gradient(180deg,#fff 0,var(--paper) 420px)}
.kai{font-family:"LXGW WenKai TC","DFKai-SB",serif}
a{color:var(--rx)}
.wrap{max-width:940px;margin:0 auto;padding:0 20px}

/* 頁首 */
.top{border-bottom:1px solid var(--line);background:rgba(255,255,255,.9);
  position:sticky;top:0;z-index:9;backdrop-filter:blur(6px)}
.top .wrap{display:flex;align-items:center;gap:14px;height:62px;font-size:14.5px}
.top a{color:var(--muted);text-decoration:none}
.top a:hover{color:var(--ink)}
.top .home{font-family:"LXGW WenKai TC","DFKai-SB",serif;
  font-weight:700;color:var(--ink);font-size:21px;letter-spacing:.02em}
.top .sp{flex:1}

/* hero */
.hero{padding:44px 0 26px}
.hero h1{font-family:"LXGW WenKai TC",serif;font-size:32px;margin:0 0 10px;letter-spacing:.02em}
.hero p{margin:0;color:var(--muted);font-size:16px;max-width:62ch}
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
.card h3{margin:5px 0 7px;font-size:19px;font-family:"LXGW WenKai TC",serif}
.card p{margin:0;font-size:14.5px;color:var(--muted);line-height:1.68}
.card::after{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--move)}
.card.boss::after{background:var(--flag)}
.card.ref::after{background:var(--gold)}
.card.sheet::after{background:var(--diet)}
.card.sheet .lv{color:var(--diet)}

/* 內文 */
article{background:#fff;border:1px solid var(--line);border-radius:14px;
  padding:34px 40px 44px;margin:26px 0 40px}
article h1{font-family:"LXGW WenKai TC",serif;font-size:29px;margin:0 0 6px;padding-bottom:14px;border-bottom:2px solid var(--ink)}
article h2{font-family:"LXGW WenKai TC",serif;font-size:22px;margin:36px 0 10px;
  padding-left:11px;border-left:5px solid var(--move)}
article h3{font-size:17.5px;margin:26px 0 6px;color:var(--diet);letter-spacing:.01em}
article h4{font-size:15.5px;margin:16px 0 4px}
article p{margin:.5em 0}
article ul,article ol{padding-left:1.35em;margin:.5em 0}
article li{margin:.3em 0}
article blockquote{margin:16px 0;padding:13px 18px;background:var(--gold-soft);
  border-radius:8px;color:#5A4520;font-size:15px}
article hr{border:0;border-top:1px solid var(--line);margin:30px 0}
article code{background:#F0F0E7;border-radius:4px;padding:1px 5px;font-size:.9em}
article strong{font-weight:700}
.tw{overflow-x:auto;margin:14px 0}
table{border-collapse:collapse;width:100%;font-size:14.5px;min-width:460px}
th,td{border:1px solid var(--line);padding:7px 10px;text-align:left;vertical-align:top}
th{background:#F4F4EC;font-weight:700;white-space:nowrap}

/* 醫護專用內容：預設收起，由導覽列開關切換 */
html:not(.show-doc) .docnote,
html:not(.show-doc) .docsec{display:none}

.docsw{font:inherit;font-size:13.5px;color:var(--muted);background:#fff;
  border:1px solid var(--line);border-radius:99px;padding:4px 13px 4px 10px;
  cursor:pointer;display:inline-flex;align-items:center;gap:7px;white-space:nowrap;
  transition:.15s}
.docsw:hover{border-color:var(--move);color:var(--ink)}
.docsw i{width:9px;height:9px;border-radius:50%;background:#C9C9BA;
  flex-shrink:0;transition:.15s}
html.show-doc .docsw{border-color:var(--move);color:var(--move);background:var(--move-soft)}
html.show-doc .docsw i{background:var(--move)}
.docsw .off{display:inline}
.docsw .on{display:none}
html.show-doc .docsw .off{display:none}
html.show-doc .docsw .on{display:inline}

/* 頁內目錄 */
.toc{background:#F7F7EF;border:1px solid var(--line);border-radius:10px;
  padding:14px 18px 15px;margin:0 0 26px;
  /* 冊子模組多時（如 M 冊 18 個），目錄不得佔掉整個螢幕：超過就自己捲 */
  max-height:40vh;overflow-y:auto;overscroll-behavior:contain}
.toc-t{font-size:12px;font-weight:700;letter-spacing:.1em;color:var(--muted);margin-bottom:8px}
.toc-s{margin-bottom:7px}
.toc-s:last-child{margin-bottom:0}
.toc-h{display:inline-block;font-weight:700;font-size:15.5px;color:var(--ink);
  text-decoration:none;line-height:1.5}
.toc-h:hover{color:var(--move)}
.toc-k{display:flex;flex-wrap:wrap;gap:3px 14px;margin:1px 0 0 2px}
.toc-k a{font-size:13.6px;color:var(--muted);text-decoration:none;line-height:1.65}
.toc-k a:hover{color:var(--move);text-decoration:underline}

/* 錨點跳轉時避開黏頂的頁首 */
article h2,article h3{scroll-margin-top:76px}

/* 回到頂端 */
.totop{position:fixed;right:20px;bottom:20px;width:44px;height:44px;border-radius:50%;
  border:1px solid var(--line);background:#fff;color:var(--ink);cursor:pointer;
  box-shadow:0 4px 14px rgba(0,0,0,.14);display:flex;align-items:center;justify-content:center;
  opacity:0;visibility:hidden;transition:.18s;z-index:20;padding:0}
.totop.on{opacity:1;visibility:visible}
.totop:hover{border-color:var(--move);color:var(--move)}
.totop svg{width:20px;height:20px}

/* 頁尾 */
footer{border-top:1px solid var(--line);margin-top:20px;padding:26px 0 46px;
  font-size:14px;color:var(--muted)}
footer b{color:var(--ink)}
.warn{background:#FDECEA;border-left:4px solid var(--flag);border-radius:8px;
  padding:14px 18px;font-size:15px;margin:20px 0;color:#7A2016;line-height:1.7}

/* 章節闖關小遊戲（可愛風） */
.quiz{margin:0 0 46px}
.quiz-box{background:linear-gradient(160deg,#FFFDF4,#FDF1DE);border:2px solid #F0D9A8;
  border-radius:24px;padding:24px 26px 28px;box-shadow:0 10px 30px rgba(154,107,42,.08);
  position:relative;overflow:hidden}
.quiz-box::before{content:"✦";position:absolute;top:14px;right:20px;font-size:20px;
  color:#E8B83C;opacity:.55;animation:qtwinkle 2.2s ease-in-out infinite}
.quiz-box::after{content:"✦";position:absolute;bottom:18px;left:16px;font-size:13px;
  color:#E8B83C;opacity:.4;animation:qtwinkle 2.2s ease-in-out infinite 1.1s}
@keyframes qtwinkle{0%,100%{opacity:.2;transform:scale(.85)}50%{opacity:.7;transform:scale(1.1)}}
.quiz-head{display:flex;gap:16px;align-items:center;flex-wrap:wrap}
.quiz-mascot{font-size:46px;line-height:1;filter:drop-shadow(0 3px 4px rgba(0,0,0,.12));
  animation:qbob 2.6s ease-in-out infinite}
.quiz-mascot img{width:86px;height:86px;border-radius:26px;display:block;
  border:2.5px solid #fff;box-shadow:0 5px 14px rgba(154,107,42,.22)}
.qmedal{width:132px;height:132px;object-fit:cover;border-radius:50%;display:block;
  margin:6px auto 2px;border:3px solid #F0D9A8;background:#fff;
  box-shadow:0 6px 18px rgba(154,107,42,.22);animation:qpop .6s}
.qmedal.ring{border:4px solid #E8B83C}
@keyframes qbob{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
.quiz-kicker{font-size:12px;font-weight:700;letter-spacing:.12em;color:var(--gold)}
.quiz-title{font-family:"LXGW WenKai TC",serif;margin:2px 0 4px;font-size:22px}
.quiz-sub{margin:0;color:var(--muted);font-size:14.5px}
.quiz-stars{display:flex;gap:6px;margin-left:auto}
.quiz-stars i{width:34px;height:34px;border-radius:50%;background:#fff;border:2px dashed #E3CFA2;
  display:flex;align-items:center;justify-content:center;font-style:normal;font-size:16px;
  color:#D8C49B;transition:.2s}
.quiz-stars i.on{border-style:solid;border-color:#E8B83C;background:#FFF3CE;animation:qpop .45s}
@keyframes qpop{0%{transform:scale(.4)}60%{transform:scale(1.3)}100%{transform:scale(1)}}
.qcard{background:#fff;border:1.5px solid #EFE3C8;border-radius:18px;padding:16px 18px 18px;
  margin-top:16px;animation:qin .4s}
@keyframes qin{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
.qnum{display:inline-block;background:var(--move-soft);color:var(--move);font-weight:700;
  font-size:12.5px;border-radius:99px;padding:2px 11px}
.qtext{font-size:17.5px;font-weight:700;margin:9px 0 12px}
.qopts{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.qopts button{font:inherit;font-size:15.5px;text-align:left;background:#FDFBF3;
  border:1.5px solid #E7DDC2;border-radius:99px;padding:8px 16px 8px 8px;cursor:pointer;
  transition:.15s;display:flex;align-items:center;gap:10px}
.qopts button i{width:27px;height:27px;border-radius:50%;background:#F4E7C8;color:#8A6215;
  font-style:normal;font-weight:700;font-size:13px;display:flex;align-items:center;
  justify-content:center;flex-shrink:0;transition:.15s}
.qopts button:hover:not(:disabled){transform:translateY(-2px) rotate(-.4deg);
  border-color:var(--move);background:#fff;box-shadow:0 4px 12px rgba(10,138,77,.12)}
.qopts button:hover:not(:disabled) i{background:var(--move-soft);color:var(--move)}
.qopts button:disabled{cursor:default}
.qopts button.no{opacity:.5;background:#F4F1E7;animation:qshake .4s}
.qopts button.no i{background:#DDD8C8;color:#8B8674}
.qopts button.no::after{content:"💦";margin-left:auto}
.qopts button.yes{background:var(--move-soft);border-color:var(--move);color:#0A6B3D;font-weight:700}
.qopts button.yes i{background:var(--move);color:#fff}
.qopts button.yes::after{content:"⭕";margin-left:auto}
@keyframes qshake{0%,100%{transform:translateX(0)}25%{transform:translateX(-5px)}75%{transform:translateX(5px)}}
.qmiss{margin-top:9px;font-size:13.5px;color:#A8834B}
.qwhy{margin-top:10px;background:var(--gold-soft);color:#5A4520;border-radius:10px;
  padding:8px 12px;font-size:14px;line-height:1.7}
.quiz-done{margin-top:18px;background:linear-gradient(180deg,#FFFDF4,#FFF4D8);
  border:2px solid #E8B83C;border-radius:18px;
  padding:22px 20px;text-align:center;animation:qin .5s}
.quiz-done .party span{display:inline-block;font-size:26px;margin:0 3px;animation:qbob 1.2s ease-in-out infinite}
.quiz-done .party span:nth-child(2){animation-delay:.15s}
.quiz-done .party span:nth-child(3){animation-delay:.3s}
.quiz-done .party span:nth-child(4){animation-delay:.45s}
.quiz-done .party span:nth-child(5){animation-delay:.6s}
.quiz-done h3{font-family:"LXGW WenKai TC",serif;font-size:21px;margin:8px 0 4px}
.quiz-done p{margin:0 0 14px;color:var(--muted);font-size:14.5px}
.qbtn{display:inline-block;font:inherit;font-size:15px;font-weight:700;border-radius:99px;
  padding:8px 20px;cursor:pointer;text-decoration:none;margin:0 5px 6px;transition:.15s}
.qbtn:hover{transform:translateY(-2px)}
.qbtn.go{background:var(--move);border:2px solid var(--move);color:#fff;
  animation:qpulse 1.8s ease-in-out infinite}
@keyframes qpulse{0%,100%{box-shadow:0 0 0 0 rgba(10,138,77,.35)}50%{box-shadow:0 0 0 7px rgba(10,138,77,0)}}
.qbtn.again{background:#fff;border:2px solid var(--line);color:var(--muted)}
.qbadge{position:absolute;top:10px;right:12px;background:#FFF3CE;border:1.5px solid #E8B83C;
  color:#8A6215;font-size:11.5px;font-weight:700;border-radius:99px;padding:1px 9px}

@media(max-width:640px){
  .qopts{grid-template-columns:1fr}
  .quiz-box{padding:18px 16px 22px;border-radius:18px}
  .quiz-stars{margin-left:0}
  .top .wrap{height:56px;gap:10px}
  .top .home{font-size:18px}
  .top .crumb{display:none}   /* 手機空間有限，麵包屑讓位給站名與開關 */
  .docsw{font-size:12.5px;padding:3px 10px 3px 8px;gap:5px}
  .docsw .off{display:none}   /* 手機只留「醫師版」二字 */
  .docsw::after{content:"醫師版"}
  html.show-doc .docsw .on{display:none}
  .hero h1{font-size:26px}
  article{padding:24px 20px 32px;border-radius:10px}
  article h1{font-size:22px}
  .toc{padding:12px 14px 13px;margin-bottom:20px;max-height:38vh}
  .toc-k{gap:2px 12px}
  .totop{right:14px;bottom:14px}
}
`;

function page({ title, body, crumb = '', desc = '', docSwitch = false }) {
  const sw = docSwitch ? `<button class="docsw" type="button" aria-pressed="false">
    <i></i><span class="off">顯示醫師備註</span><span class="on">隱藏醫師備註</span>
  </button>` : '';
  return `<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(title)}</title>
<meta name="description" content="${esc(desc)}">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=LXGW+WenKai+TC:wght@400;700&family=Noto+Sans+TC:wght@400;500;700&display=swap">
<style>${CSS}</style>
<script>
/* 在繪製前套用偏好，避免醫師備註閃一下才收起 */
try{if(localStorage.getItem('glp1-show-doc')==='1')document.documentElement.classList.add('show-doc');}catch(e){}
</script>
</head>
<body>
<nav class="top"><div class="wrap">
  <a class="home" href="./">GLP-1 減重衛教</a>
  <span class="sp"></span>
  ${crumb}
  ${sw}
  <a href="https://philia81301-commits.github.io/">← 工具集首頁</a>
</div></nav>
${body}
<footer><div class="wrap">
  <b>潘湘如醫師｜家醫科</b>　·　GLP-1 RA／GIP 週製劑減重治療衛教內容體系<br>
  本站內容為衛教參考，不能取代個別醫療評估；用藥與劑量調整請與您的醫師討論。<br>
  原始碼與更新紀錄：<a href="https://github.com/philia81301-commits/obesity-education-clinic">GitHub</a>
</div></footer>
<button class="totop" type="button" aria-label="回到頂端">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5"/><path d="m5 12 7-7 7 7"/></svg>
</button>
<script>
(function(){
  var b=document.querySelector('.totop');
  if(!b)return;
  var show=function(){ b.classList.toggle('on', window.scrollY>420); };
  window.addEventListener('scroll', show, {passive:true});
  show();
  b.addEventListener('click', function(){ window.scrollTo({top:0, behavior:'smooth'}); });
})();
(function(){
  var sw=document.querySelector('.docsw');
  if(!sw)return;
  var root=document.documentElement;
  var sync=function(){ sw.setAttribute('aria-pressed', root.classList.contains('show-doc')?'true':'false'); };
  sync();
  sw.addEventListener('click', function(){
    var on=root.classList.toggle('show-doc');
    try{ localStorage.setItem('glp1-show-doc', on?'1':'0'); }catch(e){}
    sync();
  });
})();
</script>
</body>
</html>`;
}

/** 遊戲圖檔（Canva 生成的吉祥物貼圖與徽章）：來源在 design/assets-quiz/，build 時複製進 docs/assets/quiz/ */
const QUIZ_ASSETS = path.join(ROOT, 'design', 'assets-quiz');
const hasAsset = name => fs.existsSync(path.join(QUIZ_ASSETS, name));

/** 產生章節闖關小遊戲區塊（含互動腳本；一頁一個，資料內嵌） */
function quizHtml(slug) {
  const z = QUIZ[slug];
  if (!z) return '';
  const stars = z.qs.map(() => '<i>☆</i>').join('');
  // 吉祥物：有 Canva 貼圖就用圖，沒有退回 emoji
  const mascotImg = hasAsset(`${slug}-mascot.png`)
    ? `<img src="assets/quiz/${slug}-mascot.png" alt="" loading="lazy">`
    : z.mascot;
  // 通關徽章：有徽章圖用徽章圖；只有貼圖就用金環包貼圖；都沒有就不放圖
  const medalImg = hasAsset(`${slug}-badge.png`)
    ? `<img class="qmedal" src="assets/quiz/${slug}-badge.png" alt="通關徽章">`
    : hasAsset(`${slug}-mascot.png`)
      ? `<img class="qmedal ring" src="assets/quiz/${slug}-mascot.png" alt="通關徽章">`
      : '';
  // 內嵌腳本不用樣板字串，避免與外層樣板衝突
  const js = '(function(){' +
    'var Q=' + JSON.stringify(z.qs) + ';' +
    'var box=document.getElementById("quiz");if(!box)return;' +
    'var qs=box.querySelector(".quiz-qs"),stars=box.querySelectorAll(".quiz-stars i"),done=box.querySelector(".quiz-done"),slug=box.getAttribute("data-slug");' +
    'function reset(){qs.innerHTML="";done.hidden=true;for(var i=0;i<stars.length;i++){stars[i].textContent="\\u2606";stars[i].className="";}show(0);}' +
    'function finish(){done.hidden=false;try{localStorage.setItem("glp1-quiz-"+slug,"1");}catch(e){}done.scrollIntoView({behavior:"smooth",block:"nearest"});}' +
    'function show(i){var q=Q[i];var card=document.createElement("div");card.className="qcard";' +
    'var h=\'<span class="qnum">\\u7b2c \'+(i+1)+\' \\u984c</span><div class="qtext"></div><div class="qopts">\';' +
    'for(var j=0;j<q.o.length;j++)h+=\'<button type="button" data-j="\'+j+\'"><i>\'+"ABCD"[j]+\'</i><span></span></button>\';' +
    'h+=\'</div><div class="qmiss" hidden>\\u5dee\\u4e00\\u9ede\\uff0c\\u63db\\u4e00\\u500b\\u8a66\\u8a66\\uff01</div><div class="qwhy" hidden></div>\';' +
    'card.innerHTML=h;card.querySelector(".qtext").textContent=q.q;' +
    'var btns=card.querySelectorAll(".qopts button");' +
    'for(var k=0;k<btns.length;k++)btns[k].querySelector("span").textContent=q.o[k];' +
    'qs.appendChild(card);if(i>0)card.scrollIntoView({behavior:"smooth",block:"nearest"});' +
    'for(var k2=0;k2<btns.length;k2++)(function(b){b.addEventListener("click",function(){' +
    'if(+b.getAttribute("data-j")===q.a){b.className="yes";for(var x=0;x<btns.length;x++)btns[x].disabled=true;' +
    'card.querySelector(".qmiss").hidden=true;var w=card.querySelector(".qwhy");w.textContent="\\ud83d\\udca1 "+q.w;w.hidden=false;' +
    'stars[i].textContent="\\u2b50";stars[i].className="on";' +
    'setTimeout(function(){if(i+1<Q.length)show(i+1);else finish();},700);' +
    '}else{b.className="no";b.disabled=true;card.querySelector(".qmiss").hidden=false;}' +
    '});})(btns[k2]);}' +
    'var again=done.querySelector(".again");if(again)again.addEventListener("click",reset);' +
    'show(0);})();';
  return `<section class="quiz" id="quiz" data-slug="${slug}">
  <div class="quiz-box">
    <div class="quiz-head">
      <div class="quiz-mascot">${mascotImg}</div>
      <div>
        <div class="quiz-kicker">讀完來玩</div>
        <h2 class="quiz-title">${z.name}</h2>
        <p class="quiz-sub">一次一題、四選一，答對才會出現下一題。答錯不扣分，放心作答！</p>
      </div>
      <span class="quiz-stars">${stars}</span>
    </div>
    <div class="quiz-qs"></div>
    <div class="quiz-done" hidden>
      <div class="party"><span>🎉</span><span>${z.mascot}</span><span>⭐</span><span>${z.mascot}</span><span>🎉</span></div>
      ${medalImg}
      <h3>五題全通關！獲得稱號「${z.badge}」</h3>
      <p>把答案講給家人聽一遍，記得更牢喔。</p>
      <div>
        <a class="qbtn go" href="${z.next.href}">${z.next.label}</a>
        <button class="qbtn again" type="button">再玩一次</button>
      </div>
    </div>
  </div>
  <script>${js}</script>
</section>`;
}

/* ---------- 產出 ---------- */
fs.mkdirSync(DOCS, { recursive: true });
fs.mkdirSync(path.join(DOCS, 'sheets'), { recursive: true });

// 遊戲圖檔：design/assets-quiz/*.png → docs/assets/quiz/
if (fs.existsSync(QUIZ_ASSETS)) {
  const outDir = path.join(DOCS, 'assets', 'quiz');
  fs.mkdirSync(outDir, { recursive: true });
  for (const f of fs.readdirSync(QUIZ_ASSETS).filter(f => f.endsWith('.png'))) {
    fs.copyFileSync(path.join(QUIZ_ASSETS, f), path.join(outDir, f));
  }
}

let built = 0;
for (const b of [...BOOKS, ...REFS]) {
  const src = path.join(CONTENT, b.md);
  if (!fs.existsSync(src)) { console.warn(`  ⚠ 找不到 ${b.md}，略過`); continue; }
  const md = fs.readFileSync(src, 'utf8');
  const crumb = `<span class="crumb"><a href="./">總覽</a><span style="color:#C9C9BA"> / </span>${esc(b.title)}</span>`;
  const { html: bodyHtml, headings } = mdToHtml(md);
  // 目錄插在第一個 h1 之後（標題下方），沒有 h1 就放最前面
  const withToc = wrapDocSections(bodyHtml).replace(/(<\/h1>)/, `$1\n${buildToc(headings)}`);
  const html = page({
    title: `${b.title}｜GLP-1 減重衛教`,
    desc: b.desc,
    crumb,
    docSwitch: true,
    body: `<div class="wrap"><article>${withToc}</article>${quizHtml(b.slug)}</div>`,
  });
  fs.writeFileSync(path.join(DOCS, `${b.slug}.html`), html, 'utf8');
  built++;
}

// 衛教單（直接複製既有 A4 HTML）
const SHEETS = [
  { file: '衛教單-S1起始期-A4.html', out: 's1-a4.html', title: 'S1 起始期 A4 衛教單',
    desc: '第 1 關：蛋白質優先、水分、外食選擇＋走路 30 分鐘＋打針基本功與想吐時的因應。' },
  { file: '衛教單-S2減重期-A4.html', out: 's2-a4.html', title: 'S2 減重期 A4 衛教單',
    desc: '第 2 關：蛋白質不鬆懈、主食減量、外食公式＋肌力訓練與「短而喘」＋升劑量與頭暈因應。' },
  { file: '衛教單-S3停滯期-A4.html', out: 's3-a4.html', title: 'S3 停滯期 A4 衛教單',
    desc: '魔王關：先盤點不節食、抗餓餐盤＋每天 10 分鐘核心菜單＋飢餓感三招（劑量可談、15 分鐘法、宵夜三道防線）。' },
  { file: '衛教單-S4維持期-A4.html', out: 's4-a4.html', title: 'S4 維持期 A4 衛教單',
    desc: '第 4 關：體重警戒線（＋2 公斤）與三步行動、72 小時回正軌＋運動不減量＋維持期劑量共同決策。' },
  { file: '衛教單-S5停藥過渡期-A4.html', out: 's5-a4.html', title: 'S5 停藥／減藥過渡期 A4 衛教單',
    desc: '第 5 關：食慾回升的工具總動員、監測加密＋運動接棒＋停藥方式可回頭、計畫懷孕，以及「回來就好」。' },
  { file: '衛教單-M更年期專項-A4.html', out: 'm-a4.html', title: 'M 更年期專項 A4 衛教單',
    desc: '更年期專屬補充單（配各關使用）：蛋白質與骨骼、肌力主角＋追劇超慢跑、腰圍追蹤、荷爾蒙治療轉介、情緒壓力三招與婦科紅旗。' },
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
    <p>GLP-1 RA／GIP 週製劑（週纖達、猛健樂）減重治療的分階段衛教。依治療旅程分五關，加一冊更年期女性專項與兩份共用採買清單；每個模組都有病人版、醫師備註與依據出處。每一關讀完都有五題小遊戲，全對就能收集通關徽章 🏅。</p>
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
    ${sheetLinks.map(s => cardHtml('sheet', 'A4 可列印', s.title, s.desc || '一頁式衛教單：飲食／運動／藥物三區塊＋本週任務＋紅旗症狀。開啟後直接列印。', `sheets/${s.out}`)).join('\n    ')}
  </div>` : ''}

  <div class="warn">
    <b>給病人的提醒</b>：本站是衛教參考資料，內容以一般情況撰寫。您的劑量、用藥調整、停藥時機都需要由您的醫師依個人狀況評估——出現嚴重嘔吐、劇烈腹痛、皮膚眼白變黃、心悸冒冷汗等情況，請不要等回診，直接就醫。
  </div>
</div>
<script>
/* 通關徽章：讀 localStorage 幫已通關的冊別卡片掛上徽章 */
(function(){
  try{
    var cs=document.querySelectorAll('a.card');
    for(var i=0;i<cs.length;i++){
      var m=(cs[i].getAttribute('href')||'').match(/^(s[1-5]|m)\\.html$/);
      if(m&&localStorage.getItem('glp1-quiz-'+m[1])==='1'){
        var b=document.createElement('span');b.className='qbadge';b.textContent='🏅 已通關';cs[i].appendChild(b);
      }
    }
  }catch(e){}
})();
</script>`,
});
fs.writeFileSync(path.join(DOCS, 'index.html'), home, 'utf8');
fs.writeFileSync(path.join(DOCS, '.nojekyll'), '', 'utf8');

console.log(`✅ 已產出 docs/：${built} 篇內容頁、${sheetLinks.length} 張衛教單、1 個首頁`);
