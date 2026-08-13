# REPORT_GsatStoryS3_App端串接 — 執行結果

- 執行時間：2026-08-13
- 狀態：完成，待負責人實機驗收

## 現在你能做什麼

學生切到「學測」後，用「快速建立：選課本頁碼」建立第 16 頁或其他有故事的頁碼批次，進批次 Hub 會看到「故事模式」。點進去後可以讀整頁 Minecraft 故事，英文目標單字會加粗，句子旁的喇叭可以播放整句；中文括號裡的英文單字也可以點擊播放單字發音。

手動勾字建立的學測批次不會出現「故事模式」，避免學生看到沒有內容的灰色入口。

## 改了什麼

- `Batch` 新增 optional `sourcePage?: number`，不影響舊批次資料。
- `BatchBuilderPage.handleCreatePageBatch` 在頁碼快速建立批次後寫入 `sourcePage`；手動選字的 `handleCreate` 沒有寫入。
- 新增 `src/services/stories.ts`，用 `import.meta.env.BASE_URL` 延遲 fetch `data/stories.gsat.json`，並依 `source === 'gsat'`、`sourcePage`、`theme === 'minecraft'` 找故事。
- `BatchHubPage` 只在確認該批次有對應故事後顯示「故事模式」功能格，點擊進 `/batch/:id/story`。
- 新增 `StoryPage` 與路由 `/batch/:id/story`，顯示英文/中文對照、英文目標字加粗、整句與中文括號英文可點發音。
- 複製 `output/story/gsat/stories.gsat.json` 到 `exam-vocab-batcher/public/data/stories.gsat.json`。
- `vite.config.ts` 的 Workbox runtime cache 規則擴大涵蓋 `stories.gsat.json`，策略維持 `StaleWhileRevalidate`。
- 新增 `e2e/gsat-story.spec.ts` 與三張驗證截圖。

## 驗證結果

- `npm.cmd run lint`：通過。
- `npm.cmd run build`：通過。Vite 仍有既有 chunk size warning，未影響 build。
- `npx.cmd playwright test gsat-story`：2 passed。
- `npm.cmd run test:e2e`：13 passed。

Playwright 驗證內容：
- 學測來源建立第 16 頁頁碼批次，Hub 會出現「故事模式」。
- 點進故事模式後，看到第 16 頁句子列表，點整句喇叭與中文括號英文單字發音按鈕沒有頁面錯誤。
- 手動搜尋 `accord` 並勾選建立學測批次，Hub 不顯示「故事模式」。

驗證截圖：
- `exam-vocab-batcher/e2e/screenshots/gsat-story-page16-hub.png`
- `exam-vocab-batcher/e2e/screenshots/gsat-story-page16-list.png`
- `exam-vocab-batcher/e2e/screenshots/gsat-story-manual-batch-no-card.png`

補充：第一次 focused Playwright 測試曾因測試碼把第 16 頁預期句子寫成 S2b 第 13 頁內容而失敗；畫面實際已載入第 16 頁故事。修正測試預期後 focused test 與完整 e2e 都通過。

## 是否偏離 BRIEF

無。

實作選擇補充：故事資料沒有放進 `AppContext`，而是由 `BatchHubPage` 和 `StoryPage` 需要時延遲載入，避免一般使用者一進 App 就下載故事 JSON，也避免改動這次 BRIEF 明確提醒不要碰的 `setSource()` 敏感邏輯。

## 負責人驗收步驟

1. 打開 App，切到「學測」。
2. 進「建立新批次」，在「快速建立：選課本頁碼」點第 16 頁。
3. 進批次 Hub，確認看到「故事模式」。
4. 點進故事模式，確認看得到英文/中文對照；點句子旁喇叭能播放整句，點中文括號裡的英文單字能播放單字。
5. 回到建立批次頁，用進階搜尋手動勾一個字建立批次，進批次 Hub 確認沒有「故事模式」。

## 遇到的問題 / 卡住的地方

- 無產品實作阻塞。
- 完整 e2e 會重寫既有截圖；本次已還原非 S3 的舊截圖，只保留故事模式新增截圖。
