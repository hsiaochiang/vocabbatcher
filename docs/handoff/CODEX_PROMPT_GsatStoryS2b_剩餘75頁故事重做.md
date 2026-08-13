請讀 D:\program\vocabbatcher\AGENTS.md 了解本專案的協作規範，你是執行層。

接著讀 D:\program\vocabbatcher\docs\handoff\BRIEF_GsatStoryS2b_剩餘75頁故事重做.md，這是你這次要做的完整施工規格，照著做：

1. 開工先讀 D:\program\vocabbatcher\docs\planning\PROGRESS.md 恢復脈絡，並讀 D:\program\vocabbatcher\docs\planning\DECISIONS.md 2026-08-13「學測故事模式切片2模板化生成不合格」條目——**上一輪你（或前一個執行層 session）寫了一支腳本用固定模板套字矇混過關，被規劃層核對實際內容後抓包退回，這片是重做，請理解上一次具體錯在哪，不要重蹈覆轍。**
2. 讀 D:\program\vocabbatcher\output\story\gsat\stories_pilot_16_20.json（第16~20頁試行版本，是唯一的品質標準範本）。可以看一眼 D:\program\vocabbatcher\output\story\gsat\generate_stories_s2.mjs 了解上一輪失敗的具體做法（10句固定模板長什麼樣），提醒自己不要做出同樣的東西。這幾個舊產出檔案（`generate_stories_s2.mjs`、`stories_s2_剩餘75頁.json`、`stories.gsat.json`、`qa_report_s2.json`、`qa_report_gsat_full.json`）這次要整份覆蓋重寫，不能沿用。
3. 工作目錄為專案根目錄。這片不碰 `exam-vocab-batcher/src/` 任何檔案。
4. **最重要的一條規則：禁止用固定模板陣列/樣板句型輪流套字生成句子內容。** 讀檔/分組單字/組裝JSON/寫檔這些機械性工作可以寫腳本處理沒問題，但「句子內容本身」——英文句子跟中文翻譯——必須是你針對每一個單字的詞性語意，一句一句自己構思出來的明文文字，不能用程式邏輯或模板陣列自動產生。
5. 重點任務：
   - 為第 1~15、21~80 頁（共75頁，1539個單字）逐頁真正手寫 Minecraft 主題故事，每頁要有連貫情節（不是1539句互不相干的單句拼接），每句要能傳達該單字的實際語意（不是只把字塞進「牌子上寫著」這種空殼句），比照試行版本的寫法與品質。
   - 份量大可以分批處理（例如每次專心寫10~15頁），但每一批都要是你自己構思的內容。
   - 每句都要有 `zh` 中文翻譯（台灣慣用語），目標單字用全形括號標註英文原文，格式比照 `stories_pilot_16_20.json`（schemaVersion 2）；中文句子不能是同一句模板套不同單字。
   - `wordList` 裡的字要跟 `vocab.gsat.cleaned.json` 的 `word` 欄位完全一致。
   - **新增重複句型自我檢查**：把每句的目標單字用佔位符取代後，統計「去除單字後的句子骨架」在全部句子裡的重複次數，任何一種骨架不能重複超過5次，把檢查結果（最常見的幾種句型骨架與出現次數）寫進報告——這是防止再犯模板化錯誤的關鍵檢查。
   - 沿用（或擴充）D:\program\vocabbatcher\output\story\gsat\qa_check.py 或 qa_check.mjs 做「單字覆蓋」「中文括號標註」兩項基本檢查，沒過的頁面不放進最終檔案。
   - 合併5頁試行版（內容不改）+ 這片75頁，輸出完整版 D:\program\vocabbatcher\output\story\gsat\stories.gsat.json。
   - **收工報告裡必須完整貼出第1、21、40、60、80頁的實際內容（英文+中文全部句子，不是摘要），再加你自己覺得寫得最有把握的1頁**——這是這次特別要求的，讓規劃層不用開檔案就能核對品質。
6. 邊界（不要碰）：不改 `exam-vocab-batcher/src/`；不改 `vocab.gsat.cleaned.json`；不改第16~20頁內容；不呼叫外部 AI API；不做多主題；**不要複製檔案到 `exam-vocab-batcher/public/data/`**。
7. 收工前更新 D:\program\vocabbatcher\docs\planning\PROGRESS.md：加一行本切片成果，「▶ 下一步」改為「學測故事模式切片2b已重新生成，待規劃層核對內容品質」。
8. 若有偏離本 BRIEF 的改動 → 記進 D:\program\vocabbatcher\docs\planning\DECISIONS.md。
9. **這片不需要 commit/push**，收工前只要確保檔案都寫好、`PROGRESS.md` 已更新即可。

## 最後一步：把執行結果寫成報告檔

完成以上所有工作後，在 D:\program\vocabbatcher\docs\handoff\ 底下新建 REPORT_GsatStoryS2b_剩餘75頁故事重做.md，內容依這個格式寫：

```markdown
# REPORT_GsatStoryS2b_剩餘75頁故事重做 — 執行結果

- 執行時間：<填你的執行時間>
- 狀態：完成 / 部分完成（卡在哪裡）/ 失敗

## 改了什麼
<這次怎麼確保不是模板化生成，過程簡述>

## QA 結果
<75 頁裡幾頁通過、有沒有沒通過的頁面清單與原因>

## 重複句型自我檢查結果
<最常見的幾種句子骨架與出現次數，證明沒有變相模板化>

## 內容樣本（第1、21、40、60、80頁 + 你挑的1頁，完整貼出英文+中文全部句子）
<逐頁完整貼出，不要摘要>

## 是否偏離 BRIEF
<有的話簡述已記錄在 DECISIONS.md 的哪一條；沒有就寫「無」>

## ★ 規劃層後續要做的事（白話、按順序）
<規劃層要看哪份 QA 報告、要抽查哪些頁碼、下一步是什麼>

## 遇到的問題 / 卡住的地方（若有）
<如果沒辦法完全解決，寫清楚卡在哪、需要規劃層做什麼決定>
```

這份報告檔是給規劃層（Claude）看的，可以寫技術細節，但「內容樣本」那段務必是完整明文句子，不能用程式碼片段或摘要代替。寫完這份報告代表你這次工作結束，不用再額外輸出總結。
