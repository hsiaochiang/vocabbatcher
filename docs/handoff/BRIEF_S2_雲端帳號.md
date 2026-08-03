# BRIEF_S2_雲端帳號.md — M3 切片 2：Google 登入 + 雲端基礎

> 交接合約：規劃層(Cowork) → 執行層(Codex CLI)，2026-07-06。
> 對應需求：`REQUIREMENTS.md` R9。切片全景見 `STAGE_3_PLAN.md`。

## 開場指令（執行層開工先做）
1. 讀 `PROGRESS.md` 恢復脈絡。
2. 讀本 BRIEF 全文；工作目錄為 `exam-vocab-batcher/`。

## 目標（一句話）
> 使用者能以 Google 帳號登入/登出，登入狀態與基本使用者資料寫入 Firestore，供 S3~S5 的考試/成績功能使用。

## 前置條件（負責人 Wilson 負責，執行層開工前先確認已完成）
- Wilson 會在 `console.firebase.google.com` 建立 Firebase 專案，並開通：
  1. Authentication → Sign-in method → 啟用 **Google**。
  2. Firestore Database → 建立（測試模式或依需要設安全規則）。
  3. 專案設定 → 新增 Web App，取得 `firebaseConfig`（apiKey、authDomain、projectId 等）。
- Wilson 會把 `firebaseConfig` 提供給執行層（透過環境變數或 `.env.local`，**不要把 key 提交進 git**，需加進 `.gitignore`）。
- 若執行層開工時尚未拿到 `firebaseConfig`，先用假資料/mock 開發 UI 骨架，Firebase 串接留最後一步，待負責人提供再接上驗證。

## 資料模型（本切片定案，S3~S5 共用，不得自行更改結構）
- `users/{uid}` — `displayName`、`createdAt`
- `users/{uid}/examResults/{examId}` — 日期、模式、頁數範圍、題數、得分、逐題紀錄(word, 題型, 對錯)　←（S3 才會寫入資料，本切片只需建好集合/型別即可，不用實作寫入邏輯）
- `users/{uid}/wordStats/{word}` — attempts、wrong、wrongRate　←（同上，S4 才會寫入）

## 任務
1. 安裝並設定 Firebase SDK（`firebase` npm 套件），建立 `src/services/firebase.ts` 初始化 app/auth/firestore，`firebaseConfig` 從環境變數讀取。
2. 建立 `src/services/auth.ts`：`signInWithGoogle()`、`signOut()`、`onAuthStateChange(callback)`（包裝 Firebase Auth）。
3. 登入使用者第一次登入時，在 `users/{uid}` 建立文件（`displayName`、`createdAt`，若已存在則不覆蓋 `createdAt`）。
4. UI：在 App 現有導覽列/Hub 頁加入登入狀態顯示：
   - 未登入：顯示「使用 Google 登入」按鈕。
   - 已登入：顯示使用者名稱/大頭貼 + 「登出」按鈕。
5. **未登入不擋路**：學習功能（批次/翻牌/發音，即 S1 的 `SpeakButton`）未登入也要能正常使用，不強制登入牆。
6. 型別定義：於 `src/types/`（或現有型別檔案位置）新增 `ExamResult`、`WordStat` 型別，對應上方資料模型，供 S3~S5 直接 import 使用。

## 邊界（本切片不做）
- 不做考試功能本身（S3）。
- 不做 examResults / wordStats 的實際寫入邏輯，只建型別與集合命名（S3、S4 才寫入）。
- 不做「未登入使用者能否考試」的 UI 提示邏輯——那是 S3 的範圍，但已拍板：**可以考，但提示「成績不會保存」**（S3 BRIEF 會據此實作）。

## 驗收（負責人操作）
1. 開 App，看到「使用 Google 登入」按鈕；點擊後跳出 Google 帳號選擇，登入成功後畫面顯示自己的名字。
2. iPad Safari 登入一次，Android Chrome 用同一個 Google 帳號登入，兩邊都看到同一個名字（代表 `users/{uid}` 資料共通）。
3. 登出後按鈕變回「使用 Google 登入」。
4. 未登入狀態下，原本的批次/翻牌/發音功能都還能正常使用。
5. `npm run lint` 與 `npm run build` 通過。

## 收尾指令（執行層收工必做）
1. 更新 `PROGRESS.md`：✅ 加一行本切片成果；「▶ 下一步」改為「等負責人驗收 S2，過了開 `BRIEF_S3_考試引擎.md`」。
2. 若有任何偏離本 BRIEF 的改動（例如資料模型欄位調整）→ 記 `DECISIONS.md` 並同步 `STAGE_3_PLAN.md`。
3. 給負責人「現在你能做什麼」＋操作步驟（含 Firebase console 需負責人確認的畫面截圖說明，如有）。
