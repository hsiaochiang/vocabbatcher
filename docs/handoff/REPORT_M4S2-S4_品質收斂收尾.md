# REPORT_M4S2-S4_品質收斂收尾 — 執行結果

- 執行時間：2026-08-03 16:37 +08:00
- 狀態：完成

## 改了什麼

### 任務一：批次頁面收斂

- `exam-vocab-batcher/src/pages/BatchHubPage.tsx`：移除「錄音播放」即將推出格，批次 Hub 現在只剩「翻牌學習／練習測驗／學習統計」三格。
- `BatchHubPage.tsx`：「練習測驗」改為可點擊，導向 `/exam`，並帶入該批次單字的最小/最大頁碼作為預設頁碼範圍；「學習統計」導向 `/stats`。
- `exam-vocab-batcher/src/pages/ExamSetupPage.tsx`：新增讀取 `location.state.initialMinPage` / `initialMaxPage`，讓從批次 Hub 進來時預設使用該批次頁碼範圍；從首頁直接進考試仍維持全書預設。
- `docs/planning/REQUIREMENTS.md`：R4 標記正式移除批次 TTS 循環播放；R7 標記批次歷史/續作與統計已由既有功能承接。
- `docs/planning/DECISIONS.md`：記錄「不做批次 TTS 循環播放，批次統計接回既有全域功能」決策。

### 任務二：邊界情況與效能

- `exam-vocab-batcher/src/pages/BatchBuilderPage.tsx`：新增重複批次提示。若新批次與既有批次的單字集合完全相同，會用確認提示詢問是否仍要建立；按取消不建立，按確定仍可建立。
- 已確認既有 0 字批次阻止仍存在：未選字時「建立批次」按鈕為 disabled。
- 已確認既有空搜尋結果仍存在：搜尋不到單字時顯示「沒有符合條件的單字」。
- 新增 `exam-vocab-batcher/e2e/m4s2-s4.spec.ts`，用 Playwright 覆蓋本片主要 smoke test 與清單捲動量測。

### 任務三：UX 查漏補缺與上線收尾

- 快篩 touch target：本次新增/調整的批次 Hub 刪除鍵補 `min-h/min-w 44px`；練習測驗、學習統計、重複批次確認與主要 CTA 均保留足夠高度。
- 快篩單一主 CTA：首頁、批次建立器、批次 Hub、考試設定/作答維持既有主操作，不做重新設計。
- 根目錄 `README.md` 已重寫為符合現況的 React + Vite PWA、Firebase Auth/Firestore、四題型考試、部署與文件地圖說明。

## 任務二效能實測結果

- 測試方式：新增 Playwright smoke test，打開 `/builder`，確認未篩選時顯示 1231 筆，接著用 `requestAnimationFrame` 分 20 段捲動完整文件高度。
- 實測結果：`M4S2-S4 full list scroll probe: 329ms`。
- 結論：桌機 Chromium 自動測試環境下捲動順暢，沒有明顯卡頓，本片未加入虛擬化套件。

## 任務三 Smoke Test 清單

- 批次建立器載入 1231 筆單字：通過
- 未選字時建立批次按鈕禁用：通過
- 空搜尋結果顯示「沒有符合條件的單字」：通過
- 建立第 1 頁批次並進入批次 Hub：通過
- 批次 Hub 只剩翻牌學習／練習測驗／學習統計，無「即將推出」與「錄音播放」：通過
- 練習測驗導向 `/exam` 並預設第 1-1 頁：通過
- 學習統計導向 `/stats`：通過
- 重複建立相同頁碼批次會跳確認，取消後不建立：通過
- 翻牌學習可進入並返回批次 Hub：通過
- 考試設定 → 作答 5 題 → 結果頁：通過
- 單字統計頁、成績歷史頁可正常渲染未登入提示：通過

## 是否偏離 BRIEF

無。任務一要求的 R4/R7 決策已記錄在 `docs/planning/DECISIONS.md`，屬 BRIEF 指定事項。

## npm run lint / npm run build 結果

- `npm.cmd run lint`：通過
- `npm.cmd run build`：通過
- `npx.cmd playwright test m4s2-s4`：4 passed

## ★ 負責人驗收步驟（白話、按順序）

1. 打開 App，進任一個已建立的批次頁。
2. 確認畫面只剩三格：「翻牌學習」「練習測驗」「學習統計」，沒有「錄音播放」或「即將推出」。
3. 點「練習測驗」，確認會到考試設定頁，而且頁碼範圍已自動變成這個批次的頁碼，不是全書 1~60。
4. 回批次頁點「學習統計」，確認會到單字統計頁。
5. 回批次建立器，用同一頁課本或同一組單字再建立一次，確認會跳出「已有內容相同批次」的提示；按取消時不會建立新批次。
6. 在批次建立器搜尋一個查不到的字，確認畫面會顯示「沒有符合條件的單字」；不選任何字時，下方「建立批次」按鈕是灰色不能按。
7. 不套任何篩選時，捲動整份 1231 筆單字清單，確認操作順暢。
8. 依序點過首頁、批次建立器、批次 Hub、翻牌、考試設定、作答、結果、單字統計、成績歷史，確認沒有白屏或整個 App 卡住。
9. 讀根目錄 `README.md`，確認新接手的人看得懂這是 React/Vite PWA、怎麼安裝、怎麼跑、怎麼部署。
10. iPhone Safari、Android Chrome 各測一次「練習測驗帶頁碼」與「重複批次提示」。

## 遇到的問題 / 卡住的地方（若有）

沒有未解決卡點。第一次執行 smoke test 時，測試腳本誤把聽力題「播放發音」按鈕當作答案按鈕，造成下一題按鈕未啟用；已修正測試定位為只點答案區按鈕，重跑後 4 項全通過。
