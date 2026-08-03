# PROGRESS.md — VocabBatcher 進度儀表板

> AI 每個 session 結束前必更新。負責人隔週回來只看這一頁。
> 角色綁定見 `WORKFLOW.md` §0。

---

## 專案：VocabBatcher
- **一句話目標：** 國中會考英文單字練習 App，讓學生勾選最多 25 個單字，批次聽錄音、翻牌學習、四題型練習。
- **目前階段：** **UI/UX 修正切片（UIUX1~UIUX3）全部驗收通過**，含頁碼資料修正（PDF 內部頁碼→課本印刷頁碼）與批次建立器改版（一頁一按鈕）；下一步規劃 M4「品質收斂」
- **整體進度：** ▓▓▓▓▓▓▓▓▓░ ~98%（M1、M2、M3、UI/UX 修正切片全部完成並驗收通過；M4 未規劃）
- **最後更新：** 2026-08-03 by 規劃層

---

## ▶ 下一步就做這個（回來先看這裡）

**規劃 M4「品質收斂」**：對照 `docs/roadmap.md` M4 驗收標準（拼字填空題型、批次歷史/續作、邊界情況、效能、UI 打磨），規劃層需要先寫 `STAGE_4_PLAN.md` 拆切片，再逐片開 BRIEF。其中 `BatchHubPage` 兩個「即將推出」功能格子（錄音播放、練習測驗）的產品決策，要在規劃時一起定案：是接回現有全域考試/統計功能、拿掉、還是補做批次專屬功能。目前尚未開始，等負責人確認要不要現在啟動 M4。

<details>
<summary>舊版下一步紀錄（已由上方取代，保留備查）</summary>

**負責人照 `REPORT_S3c_遷移至FirebaseHosting.md` 完成 Firebase Hosting 手動部署與登入重測**：
1. 安裝 Firebase CLI：`npm install -g firebase-tools`。
2. 在專案根目錄登入 Firebase：`firebase login`。
3. 在專案根目錄初始化 Hosting：`firebase init hosting`，選既有 Firebase 專案，public 目錄填 `exam-vocab-batcher/dist`，SPA rewrite 選 Yes。
4. 在 `exam-vocab-batcher/` 跑 `npm run build`，回專案根跑 `firebase deploy --only hosting`，記下新網址（通常是 `https://<project-id>.web.app`）。
5. 到 Firebase Console → Authentication → Settings → Authorized domains 確認新網域在清單內；完成後用 iPhone Safari、Android Chrome 在新網址重測登入（出現頭像、重新整理不消失、關分頁重開還在）。通過後回頭繼續 S3 驗收項 3~6。

（這份手動部署已完成，網址是 `https://gen-lang-client-0930375434.web.app`／`https://gen-lang-client-0930375434.firebaseapp.com`；登入仍失敗，才有上方 S3e 這片。）

</details>

## ⏳ 等你決定

- 專案原有的 `.github/copilot-instructions.md`（GitHub Copilot 執行層指示）要保留多久？何時可以淘汰？
- Firebase Hosting 部署穩定運作一段時間後，是否要正式移除 GitHub Pages 備援管道（目前計畫保留為手動觸發的備援，不會自動刪除）？

---

## ✅ 已完成（最近在前，依 git log 回填）

- 2026-08-03　**UI/UX 修正切片（UIUX1~UIUX3）全部驗收通過**：首頁動線改為單一主 CTA、全站對比度修正、單字庫載入失敗提示、登入狀態全頁一致、自訂刪除確認、考試對錯圖示、頁碼範圍驗證、翻牌進度保存（UIUX1）；批次建立器加入頁次篩選（UIUX2）；修正 `vocab.cleaned.json` 頁碼固定 2 頁偏移（PDF 內部頁碼→課本印刷頁碼 1~60）並把批次建立器改為「一頁一按鈕、按下即建立批次」（UIUX3）。過程中導入 Playwright 作為執行層收工前的自我驗證工具，並新增 `deploy.ps1` 部署腳本。頁碼偏移修正的背景與影響範圍記錄在 `DECISIONS.md` 2026-08-03 條目。
- 2026-08-03　**UIUX3「頁碼修正與單頁建立批次」已實作待驗收**：`vocab.cleaned.json` 的 `source_page` 已從 PDF 內部頁碼 3~62 修正為課本印刷頁碼 1~60，`top2025_md.py` 主力 parser 新增固定偏移避免未來重產又錯位；批次建立器改為一頁一按鈕，點頁碼即可建立該頁批次並進入批次頁；進階搜尋/詞性/頻率手動選字仍保留。`python -m pytest tests\test_top2025_md.py` 15 passed，`npm.cmd run lint`、`npm.cmd run build` 通過，`npm.cmd run test:e2e` 6 passed（含手機尺寸截圖）。詳見 `REPORT_UIUX3_頁碼修正與單頁建立批次.md`
- 2026-08-03　**UIUX2「頁次篩選與自動化驗證」已實作待驗收**：`BatchBuilderPage` 新增最優先的頁次範圍篩選（預設全書 3-62 頁，縮小範圍後「顯示 N 筆」同步更新），頻率/詞性/搜尋保留為進階篩選；新增 `@playwright/test`、`playwright.config.ts`、`e2e/uiux2.spec.ts` 與 6 張驗證截圖。Playwright 4 項測試全通過，`npm run lint`、`npm run build` 通過。詳見 `REPORT_UIUX2_頁次篩選與自動化驗證.md`
- 2026-08-03　**UIUX1「首頁動線與可用性修正」已實作待驗收**：首頁改為單一主 CTA、成績/統計降為次要入口；有意義的淺灰文字提高對比；單字庫載入失敗有重試畫面；主要頁面 Header 統一顯示登入狀態；批次刪除改自訂確認彈窗；考試作答加勾叉圖示；考試頁碼範圍即時提示；翻牌上一張會保存進度。`npm run lint`、`npm run build` 通過。詳見 `REPORT_UIUX1_首頁動線與可用性修正.md`
- 2026-08-03　**M3「考試與追蹤」全部完成（S1~S5 皆驗收通過）**：發音按鈕全面化、Google 登入雲端同步、頁數範圍選擇題/聽力考試、成績與錯誤率統計、錯題複習卷。過程中經歷兩段插曲：(1) 登入問題橫跨 S3b~S3f 四輪診斷，最終根因是 `HashRouter` 與 Firebase 登入網址片段衝突、PWA Service Worker 攔截登入保留路徑，兩者並存才穩定；(2) S4 驗收時發現 Firestore 安全規則預設鎖死一切讀寫，導致成績/統計資料從未真正儲存過，已修正為登入使用者僅能讀寫自己的資料。詳見 `DECISIONS.md` 完整記錄。
- 2026-08-02　**M3-S5「錯題複習卷」已實作待驗收**：`WordStatsPage` 新增「錯題複習」按鈕，依 `wordStats` 中錯誤率最高且曾答錯的單字產生考卷並導向既有 `/exam/run` 作答流程；`npm run lint`、`npm run build` 通過。詳見 `REPORT_S5_錯題複習卷.md`
- 2026-08-02　**M3-S4「成績統計」驗收通過**：登入考試後成績歷史、單字統計皆正確顯示。過程中發現 Firestore 安全規則預設 `allow read, write: if false`（鎖死一切讀寫），導致 S3、S4 的成績/統計資料其實從未真正儲存過，直到 S4 新頁面第一次讀取才現形；已修正規則為「登入使用者只能讀寫自己 `users/{uid}` 底下資料」，存進 `firestore.rules` 並在 `firebase.json` 註冊，詳見 `DECISIONS.md` 2026-08-02 條目。
- 2026-08-01　**M3-S4「成績統計」已實作待驗收**：考完後登入使用者會同步寫入 `examResults` 與 `wordStats`，新增「成績歷史」與「單字統計」頁，首頁已加入兩個入口；`npm run lint`、`npm run build` 通過。詳見 `REPORT_S4_成績統計.md`
- 2026-08-01　**M3-S3「考試引擎」完整驗收通過**：混合模式中英交錯出題、聽力題可重播、未登入訪客模式提示、已登入成績寫入、iPhone/iPad/Android 三平台皆正常。已開 `BRIEF_S4_成績統計.md`。
- 2026-08-01　**登入問題（S3b~S3f）驗收通過**：桌機瀏覽器、iPhone Safari、Android Chrome 三平台皆能正常登入（跳出 Google 帳號選擇畫面、完成登入出現頭像、重新整理與關分頁重開皆維持登入狀態）。前後歷經四輪診斷：S3b 排除「S3 程式碼回歸」假設、S3c 遷移到 Firebase Hosting（未解決但保留為合理長期部署）、S3e 修復 `HashRouter` 與 Firebase 登入網址片段衝突、S3f 修復 PWA Service Worker 攔截 Firebase 登入保留路徑——最終是 S3e + S3f 兩個根因同時修復才穩定。完整根因記錄見 `DECISIONS.md` 2026-07-31 兩筆條目。
- 2026-07-31　S3f PWA 排除 Firebase 登入保留路徑**已實作待部署驗收**：`vite.config.ts` 的 Workbox 設定新增 `navigateFallbackDenylist`，排除 `/__/auth/**`、`/__/firebase/**`，讓 Service Worker 不再把 Firebase 登入處理頁改回 App 的 `index.html`；PWA 離線快取未關閉。`npm run lint`、`npm run build` 通過，`dist/sw.js` 已確認生成 `denylist`。詳見 `REPORT_S3f_PWA排除登入路徑.md`
- 2026-07-31　S3e 登入真正根因修復**已實作待部署驗收**：`src/App.tsx` 從 `HashRouter` 改為 `BrowserRouter`，避免 Firebase Auth redirect 使用的 URL `#` 片段被 React Router 誤判成 App 路由；`src/` 內無 `#/` 或 `location.hash` 殘留；`npm run lint`、`npm run build` 通過，本機 preview `/` 與 `/exam` 皆 200。詳見 `REPORT_S3e_改用BrowserRouter.md`
- 2026-07-31　M3-S3 考試引擎**實作完成**（commit `1752fd4`）：出題引擎 `src/services/exam.ts`、考試設定/作答/結果三頁面；`npm run lint`、`npm run build` 通過。驗收進行中：測試項 1（頁數範圍+中英交錯出題）、2（聽力題可重播）已通過；測試項 4（已登入狀態）卡在登入回歸問題，見下方「進行中」
- 2026-07-31　M3-S2 Google 登入 + Firebase 雲端基礎**驗收通過**：iPhone、iPad、Android 三平台實機測試皆正常（Google 導向登入/登出、同帳號跨裝置顯示同一名字）；中途發現手機瀏覽器對 `signInWithPopup` 支援不佳（點擊後畫面閃退），改用 `signInWithRedirect` 修復（見 `DECISIONS.md` 2026-07-31 條目）
- 2026-07-30　M3-S1 發音按鈕全面化**驗收通過**：iPhone Safari、iPad Safari、Android Chrome 三平台實機測試皆正常（喇叭圖示顯示、發音正確、不誤觸勾選）
- 2026-07-30　提前建立正式環境：新增 `.github/workflows/deploy.yml`，push 到 main 自動 build 並部署到 GitHub Pages（`https://hsiaochiang.github.io/vocabbatcher/`），取代本機區網測試（本機 LAN 對 Android/iOS 連線異常，改走正式網址驗收）
- 2026-07-06　M3-S1 發音按鈕全面化已實作：新增可重用 `SpeakButton`，單字列表與翻牌卡英文單字可點喇叭發音；`npm run lint`、`npm run build` 通過
- 2026-07-06　M3 重定義為「考試與追蹤」並完成規劃：使用者回饋 4 項期待拆成 R8~R12、拍板雲端帳號(Google 登入+Firebase)與頁數範圍出題、產出 `STAGE_3_PLAN.md` + `BRIEF_S1_發音按鈕.md`
- 2026-07-06　套入兩層開發模式：補齊 AGENTS/WORKFLOW/REQUIREMENTS/ROADMAP/PROGRESS/DECISIONS，決定逐步取代舊 OpenSpec/Copilot 流程
- 2026-05-31　撰寫 `USER_MANUAL.md`、`DEVELOPER_LOG.md` + 7 份 ADR
- 2026-05-31　UI/UX 修正（清除/全選按鈕、篩選對應、Hub 卡片辨識、觸控面積）
- 2026-05-31　B-1 完成 — ExamVocabBatcher Web App（M2 核心功能）
- 2026-05-31　v2 功能補完（PDF 頁碼 + IPA 音標 + output 取消追蹤）
- 2026-05-31　功能補完 A-1~C-1（Markdown 解析器 + 品質修正）
- 2026-02-28　pdf-parser 結案文件與規範同步（sync & archive 決策）
- 2026-02-28　完成 pdf-parser 與工作流文件整合
- 2026-02-28　建立 Roadmap 治理規範 + 里程碑驗收機制
- 2026-02-28　初始專案建置（Copilot workspace + Stitch UI）

## 🔧 進行中

- M4「品質收斂」尚未規劃：需要先寫 `STAGE_4_PLAN.md` 拆切片（拼字填空題型、批次歷史/續作、邊界情況、效能、UI 打磨），再逐片開 BRIEF

## 📋 待辦

- [x] M3-S1：發音按鈕全面化（已驗收通過，iPhone/iPad/Android 皆正常）
- [x] 部署至 GitHub Pages（提前於 S1 驗收階段完成，見 `DECISIONS.md` 2026-07-30 條目）
- [x] M3-S2：Google 登入 + Firebase 雲端基礎（已驗收通過，iPhone/iPad/Android 皆正常）
- [x] **登入問題徹底修復**（S3b~S3f，2026-08-01 三平台驗收通過）
- [x] M3-S3：考試引擎（2026-08-01 完整驗收通過）
- [x] M3-S4：成績紀錄與累積錯誤率統計（2026-08-02 驗收通過，含 Firestore 安全規則修復）
- [x] M3-S5：錯題複習卷（2026-08-03 驗收通過）
- [ ] **M3「考試與追蹤」正式結案** ✅（2026-08-03，五片全部驗收通過）
- [ ] M4：拼字填空、批次歷史/續作、品質收斂（尚未規劃）
