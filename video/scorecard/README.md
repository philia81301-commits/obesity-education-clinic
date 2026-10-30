# 門診成績單影片（16:9 首頁版）——工作說明與待辦

> 2026-10-31 在醫師個人 Claude 帳號完成第一版並上線首頁，之後改由院內 Claude Team 帳號接手。兩個帳號都用醫師個人 Gmail 登入、Google Drive 相同，差別只在費用；以本檔為準。

## 現況

- 成品：`design/assets-video/scorecard.mp4`（1920×1080、30fps、71.5 秒、無配音，旁白燒在畫面字幕），首頁 hero 下方播放
- 產生器：本資料夾 `make_video.py`（Python＋Pillow＋ffmpeg，字型 Noto Sans CJK TC，ttc index=3）
- 內容七幕：開場 → 門診夥伴輪廓 → 常合併疾病 → 治療方式 → 3–5 個月成效 → 每月預算 → 結尾＋免責
- 講師貼圖三張：`bravo.png`（已去背）、`whoop.png`、`morning.png`（白底，程式自動去背）。**不用 Cheers 那張**（手拿啤酒、有酒類品牌）

## 不放進本 repo 的東西（公開 repo）

| 項目 | 位置 |
|---|---|
| 每月數據 JSON（`data_YYYY_MM.json`） | Google Drive「減重門診分析／成績單影片工具」（資料夾 ID `1IApmanz4u6DeTmloPd6IESYDdWNWte3Z`；10 月範本 `1hLU8-K96piw5bc88viIPiB3aSzd_yUUA`） |
| 貼圖原檔 | Google Drive 根目錄：`sticker_bravo_transparent.png`、`sticker_whoop_*.png`、`bravo_早安_*.png`（醫師帳號 philia81301@gmail.com） |
| 月報來源 | Drive「減重門診分析／減重門診分析產出_YYYY_MM」內的 Google Doc「減重門診評估報告與規劃策略計畫書_YYYY_MM」 |

院內帳號同樣用 philia81301@gmail.com 登入，Drive 上的貼圖、data JSON、月報都直接讀得到。

## 每月更新流程

1. 讀當月月報 Doc，依下表填新的 `data_YYYY_MM.json`（欄位與 10 月範本相同）
   - `roc_month`（例「民國115年11月」）、`data_period`（問卷資料期間，民國紀年）
   - `n_cases`／`age_mean`／`weight_mean_kg`／`bmi_mean`：6.1 個案追蹤檔總覽
   - `female_pct`／`male_pct`：6.1 個案檔性別比；`n_survey`：有效問卷數
   - `weight_rising_pct`：1.3；`comorbidities`：2.1 前五大
   - `comorbid_any_text`：2.2 加權（女有共病%×女人數＋男有共病%×男人數）÷問卷數，寫成白話（75% →「約每 4 人就有 3 人」）
   - `treatments`：6.2 依類別加總 ÷ n_cases，一位小數。GLP-1 類＝Mounjaro＋Ozempic＋Wegovy＋Rybelsus＋Saxenda；其他口服＝Contrave＋Xenical＋Jardiance＋Acarbose；另含無用藥、併用／轉換、手術。合計 100%±0.2
   - `m3_loss_pct`／`m3_success_pct`：6.4「追蹤3-5個月」；`timeline`：6.4 的 3-5／6-8／9-11 個月
   - `budget`：5.1 費用分布
2. `python3 make_video.py stills --data data.json --assets <貼圖夾> --out out` → 7 張靜態畫面目視檢查（文字重疊、去背、數字）
3. `python3 make_video.py full --data data.json --assets <貼圖夾> --out out`（約 1.5 分鐘）
4. 覆蓋 `design/assets-video/scorecard.mp4`，重做封面（`ffmpeg -ss 4.5 -i scorecard.mp4 -frames:v 1 -vf scale=1280:-2 scorecard-poster.jpg`），改 `tools/build-site.js` 的 `VIDEO.month`，`node tools/build-site.js`，明確路徑 commit 後 push
5. 新 data JSON 存回 Drive「成績單影片工具」

## 內容規範（不可改）

- 對民眾的影片**不出現處方藥商品名**，只寫藥物類別（藥事法處方藥廣告限制）
- 費用一幕只能標「初診問卷：可接受的每月治療預算」；月報沒有實際自費金額時，不可寫成「平均花費」
- 結尾保留資料來源與「個人成效因體質與配合度而異；實際治療以醫師評估為準」
- n<10 的數字不上片

## ⏳ 待醫師決定（轉院內帳號後繼續）

### 1. 是否改放 YouTube（目前：放 GitHub，選項 A）

- YouTube 上傳**免費**、不限支數
- 做法：YouTube Studio →「建立 → 上傳影片」→「是否為兒童打造」選否 → 瀏覽權限先選**「不公開」**（搜尋不到，但嵌入可播；院方同意後改「公開」不用重傳）→ 把連結交給 Claude
- Claude 接手：首頁改成 iframe 嵌入（用 `youtube-nocookie.com`、`rel=0` 讓片尾盡量只推薦同頻道），移除 repo 內 mp4，每月流程第 4 步改成「上傳 YouTube 並替換影片 ID」
- 三個顧慮：
  - **頻道歸屬**：個人頻道最快；若要掛高榮名義或支數變多，建「品牌帳號」（如「高榮家醫減重門診」），可多人共管——一併問院方
  - **廣告**：YouTube 可在未營利頻道插廣告，病人可能看到減重產品／保健食品廣告；GitHub 版沒有這問題
  - **片尾推薦**：可限縮但無法完全關閉
- 目前建議：只有一支時留在 GitHub 最乾淨；支數多或要更大量對外時再搬 YouTube。每支新版約 4 MB 進 git 歷史，每月更新一年約 50 MB

### 2. 院方確認公開門診統計數字

- handoff 原註記「公開前：不用商品名、不寫療效保證，法規面先問院方」。影片已無商品名並附免責，但頁面有成效平均值與門診人數（883 位、445 份問卷），請院方確認可公開

### 3. 配音（可選）

- 目前無聲。醫師原則「旁白一律本人錄音，不用 AI 聲音」。若要配音：依畫面字幕錄一段，用 `ffmpeg -i scorecard.mp4 -i voice.m4a -map 0:v -map 1:a -c:v copy -shortest out.mp4` 合併，畫面不用重做（每幕秒數：7／11／10.5／10.5／12／10.5／10）
