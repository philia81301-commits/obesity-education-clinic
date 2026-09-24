# 交接檔（handoff.md）

> 任何 Agent、任何電腦接手前**必讀**；收工時**必更新**。只放交接必需資訊，一頁內讀完。

## ⏯️ 目前做到哪

**階段一到四全部完成，進入內容維護期。** 內容體系八份審定、六張 A4 衛教單實印驗證、網站上線並分流病人／醫護視角、六冊章節闖關小遊戲上線（遊戲先、本章內容後）。

2026-09-15 本日完成（S1 衛教單內容微調，醫師逐句指示）：

1. **噁心處理刪「蘇打餅乾」**——四處同步：`content/01-起始期.md` 病人版、`design/衛教單-S1起始期-A4.html`、build 出的 `docs/s1.html`、`docs/sheets/s1-a4.html`。現為「當天吃清淡、少量、避油膩；薑茶可緩解」。
2. **S1 衛教單「飲食」前新增區塊「藥在你身體裡做什麼」**（`.blk.b-how`，沿用藥物藍 `--rx-soft`，靶心 icon）。兩條：①胃排空變慢＋腦部食慾中樞把「想吃」訊號調小；②前幾週低劑量暖身、體重沒明顯動是正常的。**只加在 S1，其他五張不加（醫師明確指示）。** 醫師刪掉了原本的收尾句「所以吃得少是藥在做的事，不是你在硬撐」。
3. 版面實測：整頁 297 mm、底部 spacer 仍剩約 23 mm，一頁 A4 印得下。

2026-09-24 本日完成（衛教短片試作，**醫師核可為樣板**）：

- **S2-D4 外食配餐公式**直式短片：1080×1920、71.8 秒、醫師本人配音、字幕燒入。先跑 RDQ（規格卡 `rdq/RDQ-spec-s2d4-video-pilot-20260924.md`，已 confirmed）
- 第 8 句醫師念成「**可以**用蛋白質和蔬菜補飽」，字幕與逐字稿已跟著改
- 成品 mp4 與錄音在本機 `video/s2-d4/out/`、`audio/`，**不進 git**（公開 repo）；要換電腦用得先另外搬

## 🎬 影片製作（做下一支照這個）

1. 複製 `video/s2-d4/` 當底稿，改 `逐字稿.md`、`提詞.html`、`index.html` 的 `LINES` 與場景（三處句子要一致）
2. 開提詞頁，用這台電腦的 **Logi USB Headset** 錄 120 秒（ffmpeg dshow）。**響「叮」之後醫師才開口**，錄音檔存成 `audio/narration-raw.wav`
3. `python video/align.py <模組>` → 輸出每句的吻合率，要 100%；辨識原文在 `audio/transcript.txt`
4. `node video/snap.mjs <模組> <png>` 看版面 → `node video/render.mjs <模組>` 輸出（約 5 分鐘）
- 踩坑：npm 預設擋掉 ffmpeg-static 的安裝腳本（`npm approve-scripts ffmpeg-static` 後再 `npm rebuild`）；醫師錄音時手邊一定要有提詞畫面（第一次沒開，整段作廢）；錄音 73 秒後有環境嗡嗡聲，align 會自動裁掉；光靠停頓切不開句子（第 4／5 句只停 0.4 秒），所以一定要用 whisper 對齊
- 新電腦要先裝：`cd video; npm i`、`pip install faster-whisper`（第一次跑會下載 small 模型，約 500 MB）

## 🚦 目前狀態

- **網站產生方式**：`docs/` 由 `tools/build-site.js` 從 `content/*.md` 自動產生（零相依 Node 腳本）。**改完 content 或 design 衛教單，都要重跑 `node tools/build-site.js` 再 commit**，否則線上不會變
- **同一句話可能同時存在四處**（content 病人版／design 衛教單／docs 兩份產物）：改字先 `grep` 全 repo，來源檔都改，再 build
- **小遊戲題庫**在 `tools/build-site.js` 的 `QUIZ` 常數（不在 content）；圖檔來源 `design/assets-quiz/`，build 時複製到 `docs/assets/quiz/`，**缺圖會自動退回 emoji 不會壞版**
- **通關記錄** localStorage key：`glp1-quiz-<slug>`；首頁靠它掛「🏅 已通關」
- **摺疊機制**：模組內「醫師備註」「出處」→ `.docnote`；整段醫護專用區塊 → `.docsec`，目錄對應項連動隱藏。判定在 `isDocSection()` 與 `wrapDocSections()`
- **視覺定調 v2.1**：飲食烈橘 #C2620A／運動勝利綠 #0A8A4D／藥物電光藍 #3563C9／成就暖金 #9A6B2A／紅 #C82D1B 只給紅旗；字體 LXGW WenKai TC＋Noto Sans TC；五階段＝第 1–5 關、停滯期＝魔王關
- **M 冊 50 歲數據守則**：月度更新只換數字；若某月結論反轉（50+ 顯著較差），**不得自動改寫文字，先回報醫師**

## ➡️ 下一步

0. 衛教短片：挑下一個模組批量做；決定 16:9 候診室版、上網站／YouTube 的方式（公開前：不用商品名、不寫療效保證，法規面先問院方）
1. **8 月底個案檔上傳後跑月度分析**——更新 M 冊 50 歲分組數字；**11 歲個案改另列**（`subgroup_female_age.js` 需加年齡下限與兒少另列邏輯）
2. 可選：向台灣更年期醫學會索取《2025 台灣更年期婦女健康管理及藥物治療建議》全文，補強 M 冊出處
3. 可選：`衛教圖示-少吃多動不夠的生化解釋` 的 **v3 圖檔仍含舊的「BMR 10–40%」數字**（筆記文字已勘誤），下次重做圖時出 v4
4. 備忘：S5／M 徽章為程式合成（`design/badge-forge.html`＋`badge-forge-server.js`）；若 Canva 額度回復想重生，直接覆蓋同名檔重跑 build。Pollinations 免費生圖畫不出非人類吉祥物金牌，別再試

## 🎯 出題守則（醫師四輪審題換來的，改題必看）

1. **選項要同構**——四個都是「情境」或四個都是「數值」，不要混入「⋯⋯才算」這種在講判定標準的句子
2. **干擾項不能也成立**——問「掉超過幾公斤要回報」時 3 公斤也對；改問**警戒值本身**才有唯一解。同理「多久內回正軌」要加「最晚」
3. **不用內部術語當題幹**——「體重警戒線是比目標多幾公斤」民眾看不懂；改「瘦下來後，胖回幾公斤就要處理」，術語移到答對解說教
4. **不考背誦，考安全重點**——「核心菜單沒有哪個動作」改成「做核心運動要記得什麼→正常呼吸不憋氣」（高血壓病人的實際風險）
5. **用藥題一律導向醫師**——不做「生活型態 vs 藥物」的效果比較，避免服藥者誤讀為可自行停藥

## ⚠️ 注意事項

- **`.sheet` 底部 padding 16mm 不要改回 11mm**：印表機驅動會把內容下偏 4–5mm，貼紙緣的字會被裁（2026-08-25 紅旗警語被切半的事故；CSS 內有註解）
- **SVG 內的文字標籤注意 viewBox 裁切**：超出部分預設會被切掉，螢幕與列印都一樣
- **中文內容檔只用 Edit 工具改，不要用 PowerShell `-replace`**（曾造成整份編碼毀損，靠 git 還原）。Git Bash 的 `sed -i` 改 UTF-8 中文實測安全（2026-09-15）
- **Canva connector 的 `export-design` 對 AI 生成設計會被擋**（Not allowed to access design）→ 改用 `read-design` 取 `thumbnails` 的 447px 簽名 PNG 網址下載，**網址每個參數都在簽名內，一個字都不能改**
- commit 用明確路徑，**不要 `git add .`**（多 session 平行工作）
- 兩台電腦都放 `C:\projects\obesity-education-clinic\`，開工前 `git pull`、收工後 `git push`；不要放進 OneDrive／雲端硬碟
- 計畫書 docx（270 份問卷）是院內營運資料，留在 OneDrive，不 commit 進 repo；引用只取比例數字
- GitHub Pages 有瀏覽器快取，改版後看不到新版是正常的，Ctrl+Shift+R 強制重整

## 🧩 新增衛教單時照做

- 底稿複製 `design/衛教單-S3停滯期-A4.html`（模組最多、間距最緊、已含列印修正）
- 路徑亮點依關卡位移，已過的關轉 `opacity .45`；標籤字若在 SVG 頂端，`.path svg` 要有 `overflow: visible`
- 每張挑一個重點模組做成 `.core` 專區
- 頁尾固定紅旗；完成後**量測頁尾底部 ≤1062px（＝墨水底線 281mm）**才算安全——⚠️ 舊安全線 1081px 已作廢；`.sheet` 有 `overflow:hidden`，光看高度會被騙
- 做完**加進 `tools/build-site.js` 的 `SHEETS` 陣列**再跑 build

## 🕐 最後更新

- 時間：2026-09-24（S2-D4 衛教短片試作，核可為樣板）
- 更新者：Claude Code（Opus 5.5）
- Git push：✅ 已推（`76509fa`）；L3 Obsidian 未更新
- 前一筆：2026-09-15 @ X108521 · S1 衛教單刪蘇打餅乾＋新增藥物機轉區塊 · ✅ 已推 · L3 ✅。踩坑：這台電腦的 vault 筆記是 OneDrive「僅線上」佔位檔，OneDrive.exe 主程式沒起來時讀不到；`Start-Process OneDrive.exe /background` 拉起後 `attrib -U +P` 釘選，約一分鐘可讀寫
- 前一筆：2026-08-27 @ X108521 · S5／M 徽章補齊＋遊戲移到章首 · ✅ 已推（101ecad）· L3 未更新（當時此電腦無 vault 資料夾）
