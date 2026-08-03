# REPORT_S3c_遷移至FirebaseHosting — 執行結果

- 執行時間：2026-07-31 11:18 +08:00
- 狀態：完成（執行層可做的設定已完成；實際 Firebase login/deploy 需負責人親自操作）

## 改了什麼

- `exam-vocab-batcher/vite.config.ts`
  - `base` 從固定 `/vocabbatcher/` 改為 `process.env.VITE_BASE_PATH ?? '/'`。
  - Firebase Hosting 預設使用根路徑 `/`。
  - GitHub Pages 備援 workflow 可用 `VITE_BASE_PATH=/vocabbatcher/` 繼續建置舊子路徑版本。
  - PWA manifest 新增 `start_url` 與 `scope`，跟著 `appBase` 走，避免 PWA 安裝後仍指向 GitHub Pages 子路徑。

- `firebase.json`
  - 新增 Firebase Hosting 設定。
  - `public` 指向 `exam-vocab-batcher/dist`。
  - 加入 SPA rewrite：所有路徑導回 `/index.html`。

- `.firebaserc`
  - 新增佔位 project id：`YOUR_FIREBASE_PROJECT_ID`。
  - 負責人執行 `firebase init hosting` 時可覆蓋成真正的 Firebase 專案 id。

- `.github/workflows/deploy-firebase.yml`
  - 新增 Firebase Hosting 自動部署 workflow。
  - `push` 到 `main` 與手動觸發都會執行。
  - build 階段沿用既有 `VITE_FIREBASE_*` GitHub Secrets。
  - deploy 階段使用 `FirebaseExtended/action-hosting-deploy@v0`，需要 `FIREBASE_SERVICE_ACCOUNT` 與 `FIREBASE_PROJECT_ID`。

- `.github/workflows/deploy.yml`
  - 保留 GitHub Pages workflow，但拿掉 `push` 觸發。
  - 現在只能手動執行，作為 Firebase Hosting 遷移期間的備援。
  - build 時加入 `VITE_BASE_PATH=/vocabbatcher/`，避免備援版本因 Vite base 改成 `/` 而在 GitHub Pages 壞掉。

## 是否偏離 BRIEF

無。

採用一個很小的環境變數切換，是 BRIEF 允許的「過渡期兩種部署並存」做法；沒有改登入程式碼、S3 考試引擎，也沒有執行 `firebase login`、`firebase init`、`firebase deploy`。

## npm run build / 本機靜態伺服器驗證結果

- `npm run lint`：通過（exit code 0）。
- `npm run build`：通過（exit code 0）。
- 本機靜態伺服器：用 `npm run preview -- --host 127.0.0.1 --port 4173` 驗證。
  - `http://127.0.0.1:4173/` 回應 200，HTML 有 `root` 節點，資產路徑是 `/assets/...`。
  - `http://127.0.0.1:4173/#/exam` 回應 200，HashRouter 路由入口可載入。

備註：`npm run lint` 與 `npm run build` 都有 PowerShell/npm 額外印出全域 npm 路徑權限警告：
`Access to the path 'C:\Users\wilson_hsiao\AppData\Roaming\npm\node_modules\npm\bin\npm-cli.js' is denied.`
但兩個指令 exit code 都是 0，不影響本次驗證結果。

Vite 另有 chunk size warning，這是既有 bundle 大小警告，不影響 build 成功。

## ★ 負責人要做的操作清單（最重要，白話、按順序、可直接照做）

1. 安裝 Firebase CLI。

   請在 PowerShell 打開專案資料夾後執行：

   ```powershell
   npm install -g firebase-tools
   ```

2. 用自己的 Google 帳號登入 Firebase。

   請在專案根目錄 `D:\program\vocabbatcher` 執行：

   ```powershell
   firebase login
   ```

   瀏覽器會打開 Google 登入畫面，請用建立 Firebase 專案的同一個 Google 帳號登入。

3. 初始化 Firebase Hosting。

   請確認目前位置是專案根目錄：

   ```powershell
   cd D:\program\vocabbatcher
   firebase init hosting
   ```

   看到互動選項時請這樣選：

   - 問你要不要繼續：選 Yes。
   - 問你要用哪個 Firebase project：選現在 Authentication / Firestore 正在用的那個專案。
   - 問 public directory：輸入 `exam-vocab-batcher/dist`。
   - 問是否設定成 single-page app：選 Yes。
   - 問是否要覆蓋 `index.html`：選 No。

   這一步可能會更新 `.firebaserc`，把 `YOUR_FIREBASE_PROJECT_ID` 換成真正的 project id；這是正常的。

4. 手動部署一次到 Firebase Hosting。

   先建置網站：

   ```powershell
   cd D:\program\vocabbatcher\exam-vocab-batcher
   npm run build
   ```

   再回專案根目錄部署：

   ```powershell
   cd D:\program\vocabbatcher
   firebase deploy --only hosting
   ```

   部署成功後，畫面會顯示 Hosting URL，通常長得像：

   ```text
   https://<project-id>.web.app
   ```

   請把這個新網址記下來，之後驗收登入都改用它，不再用舊的 GitHub Pages 網址。

5. 確認 Firebase 登入允許新網址。

   請打開 Firebase Console：

   ```text
   https://console.firebase.google.com/
   ```

   操作路徑：

   - 選你的 Firebase 專案。
   - 左側選 Authentication。
   - 上方或側邊找到 Settings。
   - 找 Authorized domains。
   - 確認清單裡有 `<project-id>.web.app` 和 `<project-id>.firebaseapp.com`。
   - 如果沒有，按 Add domain，把新網址的網域加進去。只填網域，不要填 `https://`，例如 `gen-lang-client-0930375434.web.app`。

6. 用手機重新測試登入。

   iPhone Safari：

   - 打開新網址 `https://<project-id>.web.app`。
   - 點「使用 Google 登入」。
   - 完成 Google 帳號登入後，確認畫面右上角出現頭像或名字。
   - 重新整理頁面，確認頭像或名字還在。
   - 關掉分頁，再重新打開新網址，確認頭像或名字還在。

   Android Chrome：

   - 重複上面同一套步驟。

7. 確認原本功能沒有因為換網址壞掉。

   請在新網址簡單走過：

   - 單字列表可以打開。
   - 可以建立批次。
   - 翻牌卡可以看。
   - 發音按鈕可以播放。
   - 考試流程可以進入、作答、看到結果。

8. 若要啟用 GitHub Actions 自動部署，再做 GitHub Secrets。

   手動部署成功後，再看下一段「GitHub Secrets 清單」。Secrets 設好後，以後 push 到 `main` 就會自動部署 Firebase Hosting。

## GitHub Secrets 清單（若有新增 workflow 需要）

到 GitHub repo 頁面操作：

```text
Settings → Secrets and variables → Actions → New repository secret
```

需要確認或新增以下 Secrets：

- `VITE_FIREBASE_API_KEY`
  - 用途：讓前端連到 Firebase。
  - 取得位置：Firebase Console → Project settings → General → Your apps → Web app config。

- `VITE_FIREBASE_AUTH_DOMAIN`
  - 用途：Firebase Auth 使用的 authDomain。遷移到 Firebase Hosting 後通常仍是 `<project-id>.firebaseapp.com`。
  - 取得位置：Firebase Console → Project settings → General → Your apps → Web app config。

- `VITE_FIREBASE_PROJECT_ID`
  - 用途：Firebase 專案 id。
  - 取得位置：Firebase Console → Project settings → General。

- `VITE_FIREBASE_STORAGE_BUCKET`
  - 用途：Firebase config 欄位，沿用目前 Web app config。
  - 取得位置：Firebase Console → Project settings → General → Your apps → Web app config。

- `VITE_FIREBASE_MESSAGING_SENDER_ID`
  - 用途：Firebase config 欄位，沿用目前 Web app config。
  - 取得位置：Firebase Console → Project settings → General → Your apps → Web app config。

- `VITE_FIREBASE_APP_ID`
  - 用途：Firebase Web app id。
  - 取得位置：Firebase Console → Project settings → General → Your apps → Web app config。

- `FIREBASE_PROJECT_ID`
  - 用途：GitHub Actions 部署時指定要部署到哪個 Firebase 專案。
  - 值：Firebase project id，例如目前 `.env.local` 顯示的 `gen-lang-client-0930375434`。

- `FIREBASE_SERVICE_ACCOUNT`
  - 用途：讓 GitHub Actions 有權限部署 Firebase Hosting。
  - 建議取得方式：在專案根目錄執行以下指令，照畫面完成 GitHub 串接：

    ```powershell
    firebase init hosting:github
    ```

    這個指令會引導你登入 GitHub、建立部署用服務帳號，並把需要的 secret 加到 GitHub。若它建立的 secret 名稱不是 `FIREBASE_SERVICE_ACCOUNT`，請回來告訴規劃層或執行層，讓 workflow 名稱對齊。

## 遇到的問題 / 卡住的地方（若有）

沒有卡住。

執行層刻意沒有執行 `firebase login`、`firebase init hosting`、`firebase deploy`，因為這些需要負責人的 Google/Firebase 權限。現在 repo 端設定已準備好，剩下是負責人的手動授權與部署。
