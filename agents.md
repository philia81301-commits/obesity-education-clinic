# obesity-education-clinic（專案藍圖）

> 本檔為跨 Agent 通用的專案藍圖（AGENTS.md 開放標準）。任何 Agent 的每個 session 都應先讀本檔＋`handoff.md`。

## 專案簡介
為減重門診接受 GLP-1 RA／GIP 週製劑（Semaglutide、Tirzepatide）治療的病人，建立依治療旅程分五階段（起始期→減重期→停滯期→維持期→停藥/減藥過渡期）的診間飲食運動藥物衛教內容體系。內容模組化，最終目標是診間可依病人狀況組出「飲食／運動／藥物」三區塊的**一頁式個人化衛教單**。另含更年期女性專項一冊。完整需求見 `rdq/RDQ-spec-glp1-education-system-20260822.md`。

## 關鍵時程
- 無死線，做好比做快重要（依旅程順序從起始期逐冊做、逐冊審稿）

## 目標與路線圖
- [x] 階段一：內容體系——總覽 index＋五階段各冊（目標/飲食/運動/因應/話術/QA 六要素）＋更年期女性專項冊，全部模組化並附 2–3 個一頁組裝範例（**2026-08-22 全數審定完成**：S1–S5＋M＋兩份 ref）
- [x] **階段一完成**：八份內容檔全數審定（S1–S5＋M＋兩份 ref）
- [ ] 階段二：一頁式個人化衛教單的視覺形式與產生方式（單張 PDF／HTML 工具，屆時再定）
  - [x] 底圖定案（2026-08-25 醫師選 **F 能量斜紋＋路徑點**，見 `design/底圖提案-程式紋理v1.html`）；S1 衛教單已套用並通過
  - [x] **GitHub Pages 上線**：`docs/` 由 `tools/build-site.js` 從 content/*.md 產生，網址 https://philia81301-commits.github.io/obesity-education-clinic/ ；已在個人入口網站加卡片＋QR
  - [x] **六張 A4 衛教單全部完成並上站**（S1–S5＋M；版型慣例見 handoff.md）
  - [ ] 診間印表機實機實測（彩色＋黑白）
  - [x] 視覺提案 v2.1（2026-08-22 醫師定調：高飽和戰鬥力配色＋遊戲化闖關框架＋個人網頁暖金對比增強，見 `design/旅程夥伴視覺提案-v2.html`）
  - [x] 第一張 A4 可列印衛教單（S1 起始期，`design/衛教單-S1起始期-A4.html`；頁尾定案不放回診日）
  - [ ] A4 衛教單診間印表機實測（彩色＋黑白）；S2–S5＋M 逐冊比照產出

## 資料夾結構
```
obesity-education-clinic/
├── agents.md          # 本檔（專案藍圖）
├── handoff.md         # 交接檔
├── content/
│   ├── index.md       # 體系總覽：冊目錄、模組編碼、一頁組裝規則
│   ├── 01-起始期.md   # S1（已審定）
│   ├── 02-減重期.md   # S2（已審定，含 D7 早餐）
│   ├── 03-停滯期.md   # S3（已審定）
│   ├── 04-維持期.md   # S4（已審定）
│   ├── 05-停藥減藥過渡期.md   # S5（已審定）
│   ├── 06-更年期女性專項.md   # M 差異冊（已審定；本院 50 歲分組數據每月由月度分析 skill 更新）
│   ├── ref-高CP值蛋白質清單.md   # 共用清單（已審定）
│   └── ref-高纖低GI早餐.md       # 共用清單（已審定）
├── design/
│   ├── 旅程夥伴視覺提案-v2.html   # 視覺識別提案 v2.1（配色/字體/圖示/語氣/衛教單 mockup）
│   ├── 底圖提案-程式紋理v1.html   # 六款純程式底紋（醫師選 F 能量斜紋＋路徑點）
│   └── 衛教單-S1起始期-A4.html    # 第一張 A4 可列印衛教單（已通過，含 F 底紋）
├── docs/              # GitHub Pages 網站（build-site.js 產生，勿手改）
├── tools/
│   └── build-site.js  # content/*.md → docs/；改內容後重跑再 commit
└── rdq/
    └── RDQ-spec-glp1-education-system-20260822.md   # 需求規格卡
```

## 內容來源（不進 repo 的外部參考）
- Obsidian：`2ndBrain/知識庫/減重代謝基礎-Lehninger.md`、`2ndBrain/創作庫/衛教圖示-少吃多動不夠的生化解釋.md`
- OneDrive：`文件/減重門診分析產出/減重門診評估報告與規劃策略計畫書.docx`（270 份問卷在地數據；院內營運資料，**不放進 repo**，引用時只取必要的比例數字）
- 高雄榮總家醫部衛教三摺頁「減重衛教0824(修).pdf」（使用者提供，Downloads；含飲食行為評估／運動評估／減重計畫勾選欄——S3-D1 停滯盤點直接沿用其四個數量欄；PDF 本身不進 repo）

## 同步層級（本專案初始化至第 2 層級）

| 層級 | 平台 | 位置 | 讀取時機 |
|------|------|------|---------|
| L1 | 本地（`C:\projects\obesity-education-clinic\`，不放雲端同步資料夾） | `agents.md`＋`handoff.md` | 每個 session |
| L2 | GitHub（**跨電腦同步唯一管道**） | philia81301-commits/obesity-education-clinic（公開） | 指定時 |
| L3 | Obsidian | 未啟用（本電腦無 Obsidian MCP，之後可補建） | 有需要時 |

## 工作約定
- 任何 Agent、任何電腦：**開工先讀 `handoff.md`，收工必更新 `handoff.md`**
- 修改共用檔案前先讀最新內容，避免覆蓋其他 Agent 的變更
- 所有回應與文件使用繁體中文
- 修改前先確認計畫，優先保留原有資料結構
- 衛教內容關鍵數值（蛋白質 g/kg、熱量、運動頻率、藥物資訊）必須標示依據來源，由醫師逐份審稿後才算定稿
