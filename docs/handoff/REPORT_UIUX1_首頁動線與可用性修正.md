# REPORT_UIUX1_首頁動線與可用性修正 — 執行結果

- 執行時間：2026-08-03 08:44:29 +08:00
- 狀態：完成

## 改了什麼

1. 首頁動線重新設計：`HomePage.tsx` 改成同一時間只保留一個最強主 CTA。沒有批次時主 CTA 是「建立新批次」；已有批次時主 CTA 是「開始考試」。成績歷史、單字統計改為較輕的橫列入口，功能沒有拿掉。
2. 全站淺灰色文字對比度修正：將有意義的 `text-gray-400` 說明文字改成 `text-gray-500` 或 `text-gray-600`，涉及 `HomePage`、`BatchBuilderPage`、`BatchHubPage`、`FlashCardPage`、`ExamSetupPage`、`ExamRunPage`、`ExamResultPage`、`ExamHistoryPage`、`WordStatsPage`、`WordCard`。剩下的 `text-gray-400` 只用在搜尋圖示。
3. 單字庫載入失敗錯誤畫面：`AppContext.tsx` 新增 `loadError`；`HomePage.tsx` 在單字庫載入失敗時顯示「單字庫載入失敗」與「重新載入」按鈕。
4. 所有頁面統一顯示登入狀態：`BatchBuilderPage`、`BatchHubPage`、`FlashCardPage`、`ExamSetupPage`、`ExamRunPage`、`ExamResultPage` 補上 `UserBadge`。
5. 刪除批次改自訂確認彈窗：`BatchHubPage.tsx` 移除 `window.confirm()`，改成 App 風格的置中 modal，明確提醒會刪除批次與翻牌進度且無法復原。
6. 考試作答頁對錯圖示：`ExamRunPage.tsx` 在答題後的正確選項顯示 `check_circle`，錯誤選項顯示 `cancel`。
7. 考試設定頁頁碼範圍驗證：`ExamSetupPage.tsx` 在 `minPage > maxPage` 時即時顯示紅色提示並停用「開始考試」。
8. 翻牌卡上一張進度儲存：`FlashCardPage.tsx` 的 `goPrev()` 也會呼叫 `persistIndex()`，往回看後關閉重開會保留最後位置。

## 是否偏離 BRIEF

無。

## npm run lint / npm run build 結果

- `npm run lint`：通過。
- `npm run build`：通過。
- 備註：PowerShell 環境仍會在命令結束時印出既有的 `npm.ps1` 權限雜訊，但兩個命令 exit code 皆為 0。另以 `npm.cmd run lint`、`npm.cmd run build` 驗證也通過。

## ★ 負責人驗收步驟（白話、按順序）

1. 開首頁。你現在應該會先看到一個最明顯的主要動作：新帳號/沒有批次時是「建立新批次」；已有批次時是「開始考試」。成績歷史與單字統計還在，但不會跟主動作搶焦點。
2. 看首頁、批次列表、找不到資料、空統計等畫面，確認說明文字比以前更深、更容易讀。
3. 若能模擬單字庫載入失敗，畫面應該會明確顯示「單字庫載入失敗」和「重新載入」，不會只像空資料。
4. 進批次建立、翻牌、考試設定、考試作答、考試結果頁，確認右上角都看得到登入狀態。
5. 刪除一個批次，確認跳出的是 App 自己的確認彈窗，並清楚寫出刪除後無法復原。
6. 考一次試，答題後確認正確答案有勾勾，答錯的選項有叉叉，不再只靠紅綠色分辨。
7. 在考試設定頁故意讓最小頁大於最大頁，確認畫面會立刻提示，且不能按「開始考試」進入模糊錯誤。
8. 翻牌卡按「上一張」往回看，關閉分頁再重開，確認進度停在最後看的那張。
9. iPhone Safari、Android Chrome 各跑一次首頁、考試設定、考試作答、翻牌與刪除批次流程。

## 遇到的問題 / 卡住的地方（若有）

沒有卡住。建置時 Vite 仍顯示 chunk 大小提醒，這是既有 bundle 體積提醒，不影響本次 UI/UX 修正與 build 結果。
