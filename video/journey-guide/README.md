# 健康旅程攻略（候診區循環衛教片）

16:9、1920×1080、30 fps、4 分 31 秒，無配音（字幕即旁白），輕快合成配樂。
成品：`design/assets-video/journey-guide.mp4`（網頁版，crf 28）→ build 時複製到 `docs/assets/video/`。

## 內容
片頭 → ①減重（五關地圖、停滯期＝魔王關、不靠意志力、用藥三件事）→ ②營養（蛋白質優先、外食、無糖飲、水與青菜、想吐時）
→ ③運動（30 分鐘拆三次、走得久、椅上抬腿、肌力）→ ④好習慣（每週三任務、連勝、睡眠壓力、回診結算）→ 紅旗症狀 → 片尾。
內容來源：`design/旅程夥伴視覺提案-v2.html` 與 S1 審定文案；肌力訓練、睡眠 7 小時、進食順序、「到急診就醫」為 Claude 補充，待醫師審。

## 檔案
- `scenes.py`：腳本與場景（要改字改這裡）
- `objects.py`：明亮插畫背景（食物、景物、生活用品，純程式繪製）
- `lib.py`：字型、斷行（按詞組斷行，避免孤字）、圖示、貼圖載入
- `stickers/`：醫師貼圖 g＝雙手上揚、gm＝其左右翻轉、w＝手指文字、b＝Bravo
- `render.py`：逐場景輸出再 concat；`music_upbeat.py`：120 BPM 配樂合成

## 重出
1. 字型：`npm pack lxgw-wenkai-tc-web` 解開到 `fonts/package`，再把 `lxgwwenkaitc-medium/*.woff2` 轉 TTF 到 `fonts/wk/` 並產生 `fonts/wk/map.json`（字元→分片檔；轉換程式見 handoff.md）；Noto Sans CJK TC 用系統字型
2. `python3 render.py` → `out/video_silent.mp4`；`python3 music_upbeat.py 271 out/bgm_upbeat.wav`
3. 合成：`ffmpeg -i out/video_silent.mp4 -i out/bgm_upbeat.wav -map 0:v -map 1:a -c:v libx264 -crf 28 -preset veryfast -c:a aac -b:a 128k -af volume=0.7 -movflags +faststart -shortest journey-guide.mp4`
