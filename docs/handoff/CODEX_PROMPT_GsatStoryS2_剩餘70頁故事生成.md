請讀 D:\program\vocabbatcher\AGENTS.md 了解本專案的協作規範，你是執行層。

接著讀 D:\program\vocabbatcher\docs\handoff\BRIEF_GsatStoryS2_剩餘70頁故事生成.md，這是你這次要做的完整施工規格，照著做：

1. 開工先讀 D:\program\vocabbatcher\docs\planning\PROGRESS.md 恢復脈絡，並讀 D:\program\vocabbatcher\output\story\gsat\stories_pilot_16_20.json（第16~20頁試行版本，已通過負責人審閱，是格式與品質的範本，不要修改這5頁）。
2. 工作目錄為專案根目錄。這片純粹是內容生成，不碰 `exam-vocab-batcher/src/` 任何檔案。
3. 重點任務：
   - 讀取 D:\program\vocabbatcher\exam-vocab-batcher\public\data\vocab.gsat.cleaned.json，依 `source_page` 分組，為第 1~15、21~80 頁（共 75 頁，第 16~20 頁已完成不用做）各寫一篇 **Minecraft 主題**故事，把該頁全部單字自然融入故事中。
   - 目標讀者是剛升國一的學生，敘述用字要簡單，只有目標單字本身可以較難；每句盡量只放 1 個目標單字（最多3個），**不要為了塞字硬湊出不通順的搭配**——規劃層試行時就踩過這個坑：`derive` 寫成 "derive a clue" 被抓出來是不自然的搭配（derive 常見搭配是 derive information/meaning），寫完自己讀一遍檢查搭配是否自然。
   - 每句都要有中文翻譯 `zh` 欄位，用**台灣慣用語**，目標單字用全形括號標註英文原文（例如「測試自己的認知能力（cognitive）」），格式完全比照 `stories_pilot_16_20.json`（schemaVersion 2）。
   - `wordList` 裡的字要跟 `vocab.gsat.cleaned.json` 的 `word` 欄位拼法完全一致。
   - 用（或擴充）D:\program\vocabbatcher\output\story\gsat\qa_check.py 對這 75 頁跑 QA：① 每頁單字都要在該頁故事英文文字裡找得到；② 每個目標單字都要能在對應中文句子的括號裡找到。若某字真的抓不到規則寬鬆調整可以，但**不能篡改 QA 邏輯讓沒真的用到的字矇混過關**——真的漏字要回頭補寫句子。
   - QA 沒過的頁面**不要放進最終的 `stories.gsat.json`**（partial-ship-and-backfill 原則），在報告裡列清楚哪幾頁沒過、原因。
   - 把 5 頁試行版本 + 這片新生成的 75 頁，合併成完整版 D:\program\vocabbatcher\output\story\gsat\stories.gsat.json（80 頁或扣除沒過頁面後的實際頁數）。
4. 邊界（不要碰）：不改 `exam-vocab-batcher/src/` 任何檔案；不改 `vocab.gsat.cleaned.json`；不改第16~20頁已通過的內容；**不呼叫任何外部 AI API（Gemini 等）**，故事內容由你自己的語言能力直接生成，不用另外裝依賴或申請金鑰；不做多主題，固定 Minecraft；不做 App 互動邏輯（那是切片3的事）；**不要複製檔案到 `exam-vocab-batcher/public/data/`**，這片的產出只放在 `output/story/gsat/`。
5. 收工前更新 D:\program\vocabbatcher\docs\planning\PROGRESS.md：加一行本切片成果（含涵蓋頁數、QA 通過率），「▶ 下一步」改為「學測故事模式切片2已生成，待規劃層抽查品質、負責人確認後，開切片3 App 端串接的 BRIEF」。
6. 若有偏離本 BRIEF 的改動（尤其是 QA 腳本規則調整、有沒有頁面被排除）→ 記進 D:\program\vocabbatcher\docs\planning\DECISIONS.md。
7. **這片不需要 commit/push**——`output/story/gsat/` 是中間產出，等切片3把資料接進 App、負責人驗收通過後才會一起 commit。收工前只要確保檔案都寫好、`PROGRESS.md` 已更新即可，不用執行任何 git 指令。

## 最後一步：把執行結果寫成報告檔

完成以上所有工作後，在 D:\program\vocabbatcher\docs\handoff\ 底下新建 REPORT_GsatStoryS2_剩餘70頁故事生成.md，內容依這個格式寫：

```markdown
# REPORT_GsatStoryS2_剩餘70頁故事生成 — 執行結果

- 執行時間：<填你的執行時間>
- 狀態：完成 / 部分完成（卡在哪裡）/ 失敗

## 改了什麼
<生成了幾頁、QA 腳本是否有調整、最終 stories.gsat.json 涵蓋幾頁>

## QA 結果
<75 頁裡幾頁通過、有沒有沒通過的頁面清單與原因>

## 是否偏離 BRIEF
<有的話簡述已記錄在 DECISIONS.md 的哪一條；沒有就寫「無」>

## ★ 規劃層後續要做的事（白話、按順序）
<規劃層要看哪份 QA 報告、要抽查哪些頁碼、下一步是什麼>

## 遇到的問題 / 卡住的地方（若有）
<如果沒辦法完全解決，寫清楚卡在哪、需要規劃層做什麼決定>
```

這份報告檔是給規劃層（Claude）看的，可以寫技術細節。寫完這份報告代表你這次工作結束，不用再額外輸出總結。
