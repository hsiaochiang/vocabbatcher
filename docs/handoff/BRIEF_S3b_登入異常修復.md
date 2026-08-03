# BRIEF_S3b_登入異常修復.md — M3 插入切片：Google 登入在手機上失效（回歸問題）

> 交接合約：規劃層 → 執行層，2026-07-31。
> 觸發背景：負責人驗收 `BRIEF_S3_考試引擎.md` 時，測試項 1、2（混合模式出題、聽力題）已通過，
> 但測試項 4（已登入狀態）卡住——iPhone、Android 手機點擊 Google 登入、完成登入導回 App 後，
> 畫面仍顯示「使用 Google 登入」按鈕，沒有出現使用者頭像。此為 S2 既有登入功能的回歸，
> **S3 未修改任何登入相關程式碼**（`git log` 確認 `src/services/auth.ts`、`src/services/firebase.ts`、
> `src/components/UserBadge.tsx` 自 S2 修復（commit `7d44332`）後未再變動），需先修好才能繼續 S3 驗收。

## 開場指令（執行層開工先做）
1. 讀 `PROGRESS.md` 恢復脈絡。
2. 讀本 BRIEF 全文；工作目錄為 `exam-vocab-batcher/`。

## 已知現象（負責人回報，2026-07-31）
- 平台：iPhone（Safari）、Android（Chrome）皆發生；iPad 未測試回報。
- 操作：點擊「使用 Google 登入」→ 完成 Google 帳號選擇/登入 → 導回 App。
- 結果：畫面仍是「使用 Google 登入」按鈕，未出現頭像／使用者名稱。
- 手動重新整理頁面後，頭像仍未出現（排除「只是畫面沒重新渲染」的可能性）。
- 畫面上沒有出現 `UserBadge.tsx` 裡 `setError('登入失敗，請再試一次')` 的紅字提示（代表 `completeRedirectSignIn()` 沒有拋出例外，或例外沒被觸發到那個 catch）。
- 使用一般瀏覽模式（非無痕、無特別隱私設定）。
- 2026-07-31 稍早，S2 驗收時同樣的 `signInWithRedirect` 流程在三平台皆測試通過（見 `DECISIONS.md` 2026-07-31 條目）。今天間隔數小時後同樣流程失敗，程式碼未變動。

## 待查方向（規劃層初步假設，執行層需實際驗證而非照單全收）
1. **PWA Service Worker 快取干擾**：專案用 `vite-plugin-pwa`（`generateSW` 模式，會 precache）。確認 SW 更新/啟用時機是否可能攔截或延遲 `getRedirectResult()` 依賴的請求或儲存存取；測試時可先在該手機瀏覽器「清除網站資料」後重試一次，若因此恢復正常，代表 SW/快取是根因，需研究修法（例如登入導回路徑排除 SW、或 SW 更新策略調整）。
2. **Firebase 主控台設定**：確認 Firebase Authentication → Settings → Authorized domains 是否包含 `hsiaochiang.github.io`；確認 Google Cloud OAuth 同意畫面的發布狀態（Testing / Production）——若仍是 Testing，只有名單內的測試帳號能完整登入，其餘帳號可能在同意畫面卡住或悄悄失敗。
3. **IndexedDB/sessionStorage 持久化**：`signInWithRedirect` 依賴瀏覽器儲存在導向 Google、导回本站的過程中維持 pending 狀態；確認手機瀏覽器（尤其 iOS Safari）是否因某種機制（例如背景分頁被系統回收、記憶體不足關閉分頁）導致這個狀態遺失。
4. **時間差因素**：S2 驗收（今天稍早）成功、間隔數小時後失敗——留意是否跟 Firebase token/session 過期、或負責人手機瀏覽器在期間被更新有關（可請負責人確認瀏覽器版本是否剛更新，但非必要，供參考）。

## 任務
1. 先在本機／可控環境重現問題（不需要真手機，桌機模擬手機 UA 或用瀏覽器遠端偵錯連 Android 皆可），找出 `getRedirectResult()` 實際回傳值與是否有被吞掉的例外。
2. 找到根因後修復。若修法造成任何跟原本 S2 BRIEF 不同的實作方式（例如換一種登入流程），依 `AGENTS.md` 規則記錄進 `DECISIONS.md`。
3. **暫時加一小段「可視化除錯資訊」**（例如頁面角落一行小字顯示登入流程目前狀態/錯誤訊息），因為負責人不會操作瀏覽器開發者工具，只能用肉眼回報畫面文字。修復確認後，這段除錯文字要移除或收斂成正式的錯誤提示（不可留一坨除錯字在正式畫面上）。
4. 確認修復後，在 iPhone Safari、Android Chrome（若可，iPad Safari）重新走一次「登入 → 出現頭像 → 頭像持續存在（重新整理不消失）」。

## 邊界（本切片不做）
- 不重新設計登入 UI／不換登入方式（除非診斷後認定 `signInWithRedirect` 本身在此情境不可行，需先回報規劃層討論，不可自行決定換方案）。
- 不動 S3 考試引擎本身的程式碼（`src/services/exam.ts`、`ExamSetupPage/RunPage/ResultPage`）。

## 驗收（負責人操作）
1. iPhone Safari：點「使用 Google 登入」→ 完成登入 → 畫面出現頭像與名字。
2. Android Chrome：同上。
3. 重新整理頁面，頭像仍在（代表登入狀態有被正確記住，不是導回瞬間才有）。
4. 關閉瀏覽器分頁、重新開啟網址，仍顯示已登入狀態（測試持久化）。

## 收尾指令（執行層收工必做）
1. 更新 `PROGRESS.md`：記錄根因與修法；「▶ 下一步」改為「等負責人重新驗收登入，過了回頭繼續 S3 驗收項 3~6」。
2. 若修法偏離本 BRIEF 或 S2 原始 BRIEF → 記 `DECISIONS.md`。
3. 給負責人白話說明「這次為什麼會壞、怎麼修好的」＋操作步驟。
