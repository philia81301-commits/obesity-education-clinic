# obesity-education-clinic（專案藍圖）

> 本檔為跨 Agent 通用的專案藍圖（AGENTS.md 開放標準）。任何 Agent 的每個 session 都應先讀本檔＋`handoff.md`。

## 專案簡介
為減重門診接受 GLP-1 RA／GIP 週製劑（Semaglutide、Tirzepatide）治療的病人，建立依治療旅程分五階段（起始期→減重期→停滯期→維持期→停藥/減藥過渡期）的診間飲食運動藥物衛教內容體系。內容模組化，最終目標是診間可依病人狀況組出「飲食／運動／藥物」三區塊的**一頁式個人化衛教單**。另含更年期女性專項一冊。完整需求見 `rdq/RDQ-spec-glp1-education-system-20260822.md`。

## 關鍵時程
- 無死線，做好比做快重要（依旅程順序從起始期逐冊做、逐冊審稿）

## 目標與路線圖
- [ ] 階段一：內容體系——總覽 index＋五階段各冊（目標/飲食/運動/因應/話術/QA 六要素）＋更年期女性專項冊，全部模組化並附 2–3 個一頁組裝範例
- [ ] 階段二：一頁式個人化衛教單的視覺形式與產生方式（單張 PDF／HTML 工具，屆時再定）

## 資料夾結構
```
obesity-education-clinic/
├── agents.md          # 本檔（專案藍圖）
├── handoff.md         # 交接檔
├── content/           # 衛教內容體系（待建）
└── rdq/
    └── RDQ-spec-glp1-education-system-20260822.md   # 需求規格卡
```

## 內容來源（不進 repo 的外部參考）
- Obsidian：`2ndBrain/知識庫/減重代謝基礎-Lehninger.md`、`2ndBrain/創作庫/衛教圖示-少吃多動不夠的生化解釋.md`
- OneDrive：`文件/減重門診分析產出/減重門診評估報告與規劃策略計畫書.docx`（270 份問卷在地數據；院內營運資料，**不放進 repo**，引用時只取必要的比例數字）

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
