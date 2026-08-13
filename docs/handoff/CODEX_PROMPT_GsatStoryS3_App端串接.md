請讀 D:\program\vocabbatcher\AGENTS.md 了解本專案的協作規範，你是執行層。

接著讀 D:\program\vocabbatcher\docs\handoff\BRIEF_GsatStoryS3_App端串接.md，這是你這次要做的完整施工規格，照著做：

1. 開工先讀 D:\program\vocabbatcher\docs\planning\PROGRESS.md 恢復脈絡，並讀 D:\program\vocabbatcher\docs\handoff\REPORT_GsatStoryS2b_剩餘75頁故事重做.md 了解故事資料的來源與格式。
2. 工作目錄為 `exam-vocab-batcher/`（App 本體），故事資料在專案根目錄的 `output/story/gsat/stories.gsat.json`（schemaVersion 2，含 `wordList`、逐句 `text`/`zh`/`targetWords`，`zh` 裡目標單字用括號標註英文原文）。
3. 重點任務：
   - `exam-vocab-batcher/src/types/batch.ts` 的 `Batch` 型別新增 `sourcePage?: number`。
   - `BatchBuilderPage.handleCreatePageBatch`（頁碼快速建立批次）建立後呼叫 `updateBatch(batch.id, { sourcePage: page })`；手動勾字建立的批次（`handleCreate`）不要打這個標籤。
   - 寫 fetch 邏輯載入 `data/stories.gsat.json`（比照 `AppContext.tsx` 載入 `vocab.gsat.cleaned.json` 的既有 pattern，用 `import.meta.env.BASE_URL` 組路徑），建議在 `StoryPage` 內用 `useEffect` page-local fetch，不用一開始就進全域 `AppContext`（除非你評估後覺得更好，並在報告說明理由）。
   - `BatchHubPage`（`exam-vocab-batcher/src/pages/BatchHubPage.tsx` 約68-105行 `features` 陣列）新增「故事模式」格子，只有 `batch.sourcePage != null` 且 `stories.gsat.json` 裡有對應 `page` 的故事時才顯示；**沒有故事的批次完全不顯示這格，不要做成灰色disabled樣式**。
   - 新增 `exam-vocab-batcher/src/pages/StoryPage.tsx`，路由 `/batch/:id/story`（`App.tsx` 加一行路由）：逐句顯示英文（目標單字粗體 + `SpeakButton` 播放整句）與中文對照（括號內符合 `targetWords` 的英文單字做成可點擊元件，點下去 `speakEn(word)` 只唸該單字）。`SpeakButton`／`speakEn`／`speakZh`（`src/components/SpeakButton.tsx`、`src/services/tts.ts`）直接沿用不用改。
   - 複製 D:\program\vocabbatcher\output\story\gsat\stories.gsat.json 到 D:\program\vocabbatcher\exam-vocab-batcher\public\data\stories.gsat.json。
   - `exam-vocab-batcher/vite.config.ts` 的 `runtimeCaching`（約31-41行）目前只匹配 `vocab(.gsat)?.cleaned.json`，要擴大正則同時涵蓋 `stories.gsat.json`，策略維持 `StaleWhileRevalidate`——2026-08-04 曾因快取規則沒涵蓋到學測資料檔導致部署後看不到更新，不要重蹈覆轍。
4. 邊界（不要碰，這幾個都是今天才修好的敏感區域）：
   - 不改 `App.tsx` 的 `BrowserRouter`／`basename` 設定（今天稍早修的部署 bug）。
   - 不改 `AppContext.tsx` 裡 `setSource()` 的邏輯（今天稍早修的「重複點選同一來源卡住」bug），這片只需要用 `updateBatch`。
   - 不做會考（CAP）故事模式、不做多主題、不改任何 `vocab.gsat.cleaned.json`／`0resource/` 資料檔、不呼叫外部 AI API。
5. `npm run lint`、`npm run build` 要過。
6. **Playwright 自我驗證**：用學測來源、選課本頁碼建立第16頁批次，確認出現「故事模式」格子、進去能看到句子列表、點發音按鈕不報錯；再用手動勾字建立一個批次，確認**不會**出現「故事模式」格子。過程與結果寫進報告。
7. 若有偏離本 BRIEF 的改動 → 記進 D:\program\vocabbatcher\docs\planning\DECISIONS.md。
8. 收工前更新 D:\program\vocabbatcher\docs\planning\PROGRESS.md：加一行本切片成果，「▶ 下一步」改為「學測 Minecraft 故事模式全部完成，待負責人在自己裝置上實際操作驗收」。

## 最後一步：把執行結果寫成報告檔

完成以上所有工作後，在 D:\program\vocabbatcher\docs\handoff\ 底下新建 REPORT_GsatStoryS3_App端串接.md，內容依這個格式寫：

```markdown
# REPORT_GsatStoryS3_App端串接 — 執行結果

- 執行時間：<填你的執行時間>
- 狀態：完成 / 部分完成（卡在哪裡）/ 失敗

## 改了什麼
<逐項對應 BRIEF 的任務，具體改了哪些檔案>

## Playwright 自我驗證結果
<驗證了什麼、截圖有沒有留、結果如何>

## 是否偏離 BRIEF
<有的話簡述已記錄在 DECISIONS.md 的哪一條；沒有就寫「無」>

## lint / build 結果
<過 / 不過>

## ★ 負責人驗收步驟（白話、按順序）
<照 BRIEF 的「驗收（負責人操作）」章節，寫成負責人看得懂、能照做的步驟。>

## 遇到的問題 / 卡住的地方（若有）
<如果沒辦法完全解決，寫清楚卡在哪、需要規劃層或負責人做什麼決定>
```

這份報告檔是給規劃層（Claude）看的，除了「負責人驗收步驟」那段要白話，其餘可以寫技術細節。

## 真正的最後一步：commit（不用 push）

寫完報告檔後，確認 `npm run lint`、`npm run build` 都通過、`PROGRESS.md` 已更新，且 `git status` 沒有不該提交的檔案，然後 `git add` 這次改動的檔案（含 `exam-vocab-batcher/src/` 相關檔案、`exam-vocab-batcher/public/data/stories.gsat.json`、`exam-vocab-batcher/vite.config.ts`、`docs/handoff/REPORT_GsatStoryS3_App端串接.md`、`docs/planning/PROGRESS.md`，若有動 `DECISIONS.md` 也一併加入），`git commit`（commit message 用一句話講清楚這片做了什麼，可先 `git log --oneline -10` 看最近幾筆訊息風格再照著寫）。**這次不用 `git push`**，等負責人實機驗收過再由規劃層決定要不要部署。

完成 commit 後，這次工作才算真正結束，不用再額外輸出總結。
