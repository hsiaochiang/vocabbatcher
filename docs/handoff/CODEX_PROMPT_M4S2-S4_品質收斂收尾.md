請讀 D:\program\vocabbatcher\AGENTS.md 了解本專案的協作規範，你是執行層。

接著讀 D:\program\vocabbatcher\docs\handoff\BRIEF_M4S2-S4_品質收斂收尾.md，這是你這次要做的完整施工規格（合併了原本規劃的 M4-S2、S3、S4 三片），照著做：

1. 開工先讀 D:\program\vocabbatcher\docs\planning\PROGRESS.md 恢復脈絡，並讀 D:\program\vocabbatcher\docs\handoff\REPORT_M4S1_拼字填空題型.md 了解上一片內容。
2. 工作目錄以 exam-vocab-batcher/ 為主，README.md 更新在專案根目錄。
3. 三個任務區塊（收工前都要做完）：
   - **任務一（批次頁面收斂）**：`BatchHubPage.tsx` 拿掉「錄音播放」格；「練習測驗」串到 `/exam`（注意不是 `/exam/setup`）並帶入本批次頁碼範圍當預設值（`ExamSetupPage.tsx` 要能吃 `location.state` 的初始頁碼範圍）；「學習統計」串到 `/stats`。同步更新 `docs/planning/REQUIREMENTS.md` R4（標記移除）、R7（標記已滿足），並在 `docs/planning/DECISIONS.md` 記錄負責人拍板不做批次 TTS 播放的決策。
   - **任務二（邊界情況與效能）**：`BatchBuilderPage.tsx` 加「重複批次」建立前提示（單字組成相同就跳確認）；實測 1231 筆單字清單捲動效能，卡頓才加虛擬化，不卡頓就記錄實測結果即可。0 字批次阻止、空搜尋結果空狀態已經做過，只要確認沒被破壞，不用重做。
   - **任務三（UX 查漏補缺與上線收尾）**：快篩 touch target／單一主 CTA（抽查，不是重新設計）；走一輪主要頁面確認無白屏/閃退/console 錯誤，整理成 smoke test 清單寫進報告；重寫專案根目錄 `README.md`（目前內容嚴重過時，還寫著 React Native + Expo，要改成符合實際的 React + Vite PWA 技術棧與功能流程）。
4. 邊界（不要碰）：不改 `exam.ts` 出題邏輯本身；不動 `BrowserRouter`；不動 Workbox `navigateFallbackDenylist`；不動 Firestore 規則；虛擬化只處理 `BatchBuilderPage.tsx`。
5. `npm run lint`、`npm run build` 要過。
6. 若有偏離本 BRIEF 的改動 → 記進 D:\program\vocabbatcher\docs\planning\DECISIONS.md。
7. 收工前更新 D:\program\vocabbatcher\docs\planning\PROGRESS.md：標記 M4「品質收斂」全部完成，「▶ 下一步」改為「M4 全部完成，等負責人驗收，過了 M1~M4 全部里程碑都完成」。

## 最後一步：把執行結果寫成報告檔

完成以上所有工作後，在 D:\program\vocabbatcher\docs\handoff\ 底下新建（或覆寫）REPORT_M4S2-S4_品質收斂收尾.md，內容依這個格式寫：

```markdown
# REPORT_M4S2-S4_品質收斂收尾 — 執行結果

- 執行時間：<填你的執行時間>
- 狀態：完成 / 部分完成（卡在哪裡）/ 失敗

## 改了什麼
<分三段對應任務一、二、三，逐項列出具體改了哪些檔案與做法>

## 任務二效能實測結果
<怎麼測的、有沒有卡頓、有沒有加虛擬化套件（若加了，用了哪個套件）>

## 任務三 Smoke Test 清單
<走過哪些頁面/路徑、結果如何>

## 是否偏離 BRIEF
<有的話簡述已記錄在 DECISIONS.md 的哪一條；沒有就寫「無」>

## npm run lint / npm run build 結果
<過 / 不過>

## ★ 負責人驗收步驟（白話、按順序）
<照 BRIEF 的「驗收（負責人操作）」章節，寫成負責人看得懂、能照做的步驟。>

## 遇到的問題 / 卡住的地方（若有）
<如果沒辦法完全解決，寫清楚卡在哪、需要規劃層或負責人做什麼決定>
```

這份報告檔是給規劃層（Claude）看的，除了「負責人驗收步驟」那段要白話，其餘可以寫技術細節。

## 真正的最後一步：commit 並 push

寫完報告檔後，確認 `npm run lint`、`npm run build` 都通過、`PROGRESS.md` 已更新，且 `git status` 沒有不該提交的檔案，然後：

1. `git add` 這次改動的檔案（含 `docs/handoff/REPORT_M4S2-S4_品質收斂收尾.md`、`docs/planning/PROGRESS.md`、`docs/planning/REQUIREMENTS.md`，若有動 `DECISIONS.md` 也一併加入）。
2. `git commit`，commit message 用一句話講清楚這片做了什麼（例如「功能: M4 品質收斂收尾（批次頁面收斂／邊界情況／UX 與上線檢查）」），可以先 `git log --oneline -10` 看最近幾筆訊息的風格再照著寫。
3. `git push` 到 `origin main`。
4. push 完成後在報告檔（或對負責人的回覆）中註明 commit hash 與 push 是否成功；若 push 失敗（例如遠端有新 commit、需要先 pull），不要用 force push，把卡住的狀況寫清楚讓規劃層或負責人決定怎麼處理。

完成 commit 並 push（或記錄清楚卡住原因）後，這次工作才算真正結束，不用再額外輸出總結。
