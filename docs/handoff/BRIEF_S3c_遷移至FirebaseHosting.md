# BRIEF_S3c_遷移至FirebaseHosting.md — M3 插入切片：正式站從 GitHub Pages 遷移到 Firebase Hosting

> 交接合約：規劃層 → 執行層，2026-07-31。
> 背景：`BRIEF_S3b_登入異常修復.md` 診斷出登入問題根因是 GitHub Pages 網域與 Firebase Auth helper
> 網域不同源，導致手機瀏覽器封鎖第三方儲存後 `signInWithRedirect()` 讀不回登入結果。
> 負責人已拍板修法（見 `DECISIONS.md` 2026-07-31「登入架構修法定案」）：把正式站部署管道從
> GitHub Pages 改成 Firebase Hosting，讓 App 網域與 Firebase Auth helper 網域同源。
> 這是非商業、個人家庭用途的專案，優先選穩定、免費、好維護的做法，不用做多餘的擴充。

## 開場指令（執行層開工先做）
1. 讀 `PROGRESS.md` 恢復脈絡。
2. 讀 `REPORT_S3b_登入異常修復.md` 了解診斷細節。
3. 工作目錄為 `exam-vocab-batcher/`。

## 目標（一句話）
> 正式站改用 Firebase Hosting 部署，App 網域與 Firebase Auth helper 網域同源，讓 iPhone Safari／Android Chrome 上的 `signInWithRedirect()` 登入能正常運作並持久保存登入狀態。

## 重要：哪些事執行層做得到、哪些需要負責人親自操作

**執行層（你）能做的：**
- 準備 `firebase.json`、`.firebaserc` 等設定檔（`.firebaserc` 的 project id 先留空白/佔位，等負責人提供）。
- 調整 `vite.config.ts` 的 `base` 設定（目前是 `/vocabbatcher/`，因應 GitHub Pages 子路徑；Firebase Hosting 是根網域，需要改成 `/` 或做成依環境變數切換，讓兩種部署方式在遷移過渡期都能建置成功——但最終目標是只保留 Firebase Hosting 一套）。
- 寫新的 GitHub Actions workflow（部署到 Firebase Hosting，用 `FirebaseExtended/action-hosting-deploy@v0`），或先寫好本機手動部署指令，視你評估哪個對這個規模的個人專案較不容易出錯。
- 確認 `src/services/firebase.ts` 的 `authDomain` 設定邏輯不用改（本來就是 `*.firebaseapp.com`，遷移後會跟 Hosting 網域同源）。
- **不要**自己執行 `firebase login`、`firebase init`、`firebase deploy` 這類需要負責人 Google 帳號授權的指令——你在自動化環境沒有負責人的登入權限，硬跑會卡住或用到不對的帳號。

**負責人（我）事後要親自做的事，你要在報告裡列成清楚的步驟清單：**
1. 在自己電腦安裝 Firebase CLI（`npm install -g firebase-tools`），執行 `firebase login` 用自己的 Google 帳號登入。
2. 在專案根目錄執行 `firebase init hosting`，選擇既有的 Firebase 專案（就是現在 Firestore/Auth 在用的那個），public 目錄指向 `exam-vocab-batcher/dist`，設定成單頁應用（SPA rewrite）。這一步會產生/更新 `.firebaserc`（填入真正的 project id）。
3. 若要用 GitHub Actions 自動部署：在 Firebase Console 或用 `firebase init hosting:github` 產生一組 CI 用的服務帳號金鑰，加進 GitHub repo 的 Secrets（例如 `FIREBASE_SERVICE_ACCOUNT`）。
4. 手動跑一次 `npm run build && firebase deploy --only hosting` 確認能成功部署，記下新網址（`https://<project-id>.web.app` 或 `.firebaseapp.com`）。
5. 到 Firebase Console → Authentication → Settings → Authorized domains 確認新網址已自動列入（Firebase Hosting 網域通常會自動加入，若沒有要手動加）。

## 任務

1. **調整建置設定**：`vite.config.ts` 的 `base` 從固定 `/vocabbatcher/` 改為適合 Firebase Hosting 根網域的設定（`/`）。如果要保留過渡期兩種部署並存的彈性，可以用環境變數控制，但不要為了這個過渡期做過度複雜的設計——這是個人專案，遷移完成後 GitHub Pages 那套就可以停用，不需要長期維護兩套。
2. **新增 `firebase.json`**：Hosting 設定，`public` 指向 `dist`，加上 SPA 的 rewrite 規則（所有路徑導回 `index.html`，因為專案用 `HashRouter`，其實通常不需要 rewrite 也能動，但仍建議照 Firebase 標準做法設定，避免使用者直接輸入深層網址時 404）。
3. **新增 `.firebaserc` 佔位檔**：project id 先留一個明顯的佔位字串（例如 `"YOUR_FIREBASE_PROJECT_ID"`），並在報告裡提醒負責人這一步會被 `firebase init hosting` 覆蓋掉，不用擔心。
4. **處理 GitHub Actions**：
   - 新增一份部署到 Firebase Hosting 的 workflow（`.github/workflows/deploy-firebase.yml`），觸發時機比照現有 `deploy.yml`（push 到 main）。用到的 Secrets 名稱要在報告裡清楚列出，讓負責人知道要去 GitHub repo Settings → Secrets 加哪些。
   - 現有 `.github/workflows/deploy.yml`（部署到 GitHub Pages）先**不要刪除**，改成只能手動觸發（`workflow_dispatch`，拿掉 `push` 觸發），保留成備援，避免遷移過程中如果 Firebase Hosting 那邊設定還沒完成，正式站整個掛掉沒有備援。等負責人確認 Firebase Hosting 版本運作正常一段時間後，再由規劃層決定要不要正式移除 GitHub Pages 那套（不在本切片做）。
5. **確認 PWA 設定**：`vite-plugin-pwa` 的設定裡如果有寫死跟 `/vocabbatcher/` 路徑相關的東西（例如 manifest 的 `start_url`、`scope`），一併檢查並調整成根路徑。
6. **本地驗證**：`npm run build` 要過；用 `npx serve dist` 或類似方式本機起一個靜態伺服器，確認頁面能正常載入、路由能動（不用真的測登入，因為本機網域一樣不是 Firebase Hosting 網域，登入測試留給負責人在正式網址上做）。

## 邊界（本切片不做）
- 不執行任何需要負責人 Google 帳號授權的指令（`firebase login`／`firebase deploy`／建立服務帳號金鑰）。
- 不刪除現有 GitHub Pages 部署管道，只改成手動觸發當備援。
- 不動 S3 考試引擎或登入程式碼邏輯本身（`src/services/auth.ts`、`src/services/firebase.ts`、`src/components/UserBadge.tsx`、`src/services/exam.ts`、Exam 三頁面）——這次只動部署/建置設定。
- 不自訂網域（`.web.app` 預設網域對個人使用足夠，自訂網域是額外的、非必要的美化，之後有需要再另開切片）。

## 驗收（負責人操作，需先完成上方「負責人事後要親自做的事」1~5）
1. 用新網址（`https://<project-id>.web.app`）在 iPhone Safari 開啟，點「使用 Google 登入」→ 完成登入 → 出現頭像。
2. 重新整理頁面，頭像仍在。
3. 關閉分頁、重新開啟新網址，仍顯示已登入狀態。
4. Android Chrome 重複步驟 1~3。
5. 確認舊功能（單字列表、批次、翻牌卡、發音按鈕、S3 考試流程）在新網址上運作正常，沒有因為換路徑設定而故障。
6. `npm run lint`、`npm run build` 通過。

## 收尾指令（執行層收工必做）
1. 更新 `PROGRESS.md`：記錄本切片完成狀態，列出「▶ 下一步」為負責人要做的 5 個手動步驟（用白話寫，不要假設負責人懂 Firebase CLI 術語，每一步給實際可以複製貼上的指令或畫面路徑）。
2. 若有偏離本 BRIEF 的改動 → 記 `DECISIONS.md`。
3. 在收工報告（依 `CODEX_PROMPT_S3c_遷移至FirebaseHosting.md` 要求的格式）裡，把「負責人事後要親自做的事」整理成一份獨立、按順序編號、可以直接照做的操作清單，這是這次任務對負責人最重要的交付物。
