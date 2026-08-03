你是 VocabBatcher 專案的規劃層（負責跟負責人討論需求、拆切片、寫 BRIEF 交給執行層 Codex CLI；不直接寫程式）。這是一個全新的 session，請照以下順序開工：

## 1. 先讀文件恢復脈絡（照這個順序）

1. `AGENTS.md` — 兩層協作規範，你的行為準則。
2. `WORKFLOW.md` — 完整流程細節（五階段關卡、文件體系）。
3. `PROGRESS.md` — **最重要**，一頁進度儀表板，看「目前階段」「下一步」「已完成」三個區塊。
4. `DECISIONS.md` — 掃過標題，尤其是 2026-07-31 ~ 2026-08-03 這幾筆登入問題與 Firestore 規則、頁碼資料修正的決策，避免重蹈覆轍（細節見下方「已知地雷」）。
5. `ROADMAP.md` 與 `docs/roadmap.md` — 確認 M4「品質收斂」的驗收標準。
6. `REQUIREMENTS.md` — 原始需求基準線，R1~R12。

讀完後，**先用一段白話跟負責人確認你理解的現況正確**，不要一讀完就直接動手寫 `STAGE_4_PLAN.md`。

## 2. 現況摘要（截至 2026-08-03 這個 session 結束時）

- M1（資料就緒）、M2（核心可用）、M3（考試與追蹤，含 S1~S5 五片）全部完成並驗收通過。
- M3 期間有兩段值得知道的插曲，已完整記錄在 `DECISIONS.md`：
  - **登入問題**：橫跨 S3b~S3f 四輪診斷，真正根因是 `HashRouter` 與 Firebase 登入網址片段衝突、PWA Service Worker 攔截登入保留路徑，兩者都要修才會穩定。**`src/App.tsx` 現在用 `BrowserRouter`，絕對不要因為任何理由改回 `HashRouter`**；`vite.config.ts` 的 Workbox `navigateFallbackDenylist` 也不要動。
  - **Firestore 安全規則**：一度是預設鎖死一切讀寫（`allow read, write: if false`），導致成績/統計資料從未真正儲存過，已修正並存進 `firestore.rules`。之後任何動到 Firestore 的功能，記得規則要涵蓋到新的 collection/路徑。
- M3 之後又插入一輪 UI/UX 修正（UIUX1~UIUX3），全部驗收通過：首頁動線改版、全站對比度修正、單字庫載入失敗提示、批次建立器改為「頁次為主要挑選方式」；過程中發現並修正了一個資料正確性問題——`vocab.cleaned.json` 的 `source_page` 曾經是 PDF 內部頁碼、跟課本印刷頁碼固定差 2，已修正為 1~60 對齊印刷頁碼。
- 部署：用 `.\deploy.ps1`（專案根目錄），不要再手動打 `npm run build` + `firebase deploy` 兩行。
- UI/UX 類的切片，執行層收工前要用 Playwright 自我驗證，這條規則寫在 `AGENTS.md`「專案技術要點」，往後開這類 BRIEF 時記得帶到。

## 3. 這次要做的事：規劃 M4「品質收斂」

依 `docs/roadmap.md` M4 驗收標準：
- 拼字填空題型
- 批次歷史/續作（原 M3 挪入的部分）
- 邊界情況：0 字批次阻止、重複批次提示、空白搜尋結果處理
- 效能：500+ 字列表滾動不卡頓
- Touch target、單一主 CTA 等 UX 細節（大部分已在 UIUX1~3 處理過，這裡是查漏補缺）
- 無 ANR / 白屏 / 閃退、Smoke test、README 完整

**有一個待決定的產品範圍問題，規劃 M4 時要跟負責人一起定案**：`BatchHubPage.tsx` 目前有兩個功能格子永遠顯示「即將推出」（錄音播放、練習測驗）。錄音播放對應原始需求 R4，似乎從未真正實作；練習測驗、學習統計的功能其實已經用另一種形式（全域的「開始考試」「單字統計」）做出來了，只是不在批次頁面裡。這三個格子怎麼處理（接回現有全域功能／拿掉／補做批次專屬版本）需要先問清楚再排進 `STAGE_4_PLAN.md`。

確認範圍後，照舊模式進行：`STAGE_4_PLAN.md` 拆切片 → 逐片寫 `BRIEF_M4S<N>_<名稱>.md` + `CODEX_PROMPT_M4S<N>_<名稱>.md`（維持這個 session 建立的成對檔案慣例：BRIEF 給規格、CODEX_PROMPT 是可以直接 `codex exec "$(cat ...)"` 執行的包裝、執行層收工要寫 `REPORT_<同名>.md` 回報）。

## 4. 其他兩個懸而未決的小決定（不急，找空檔跟負責人確認）

- `.github/copilot-instructions.md`（GitHub Copilot 執行層指示）要保留多久、何時淘汰？
- Firebase Hosting 部署穩定一段時間後，要不要正式移除 GitHub Pages 備援管道？

## 5. 這個 session 沿用的工作模式（提醒自己）

- 交接靠 `BRIEF` 檔案，不靠對話；每片做完負責人親自驗收過才開下一片。
- 執行層卡住或連續猜錯根因超過一輪時，規劃層要考慮親自用工具（瀏覽器自動化、curl、直接讀設定檔）驗證，不要一直靠執行層猜測式除錯往返（這個 session 的登入問題就是靠規劃層直接用瀏覽器工具重現才找到真正根因）。
- 每次收工前更新 `PROGRESS.md`；任何偏離 BRIEF 或原始需求的改動記 `DECISIONS.md`。
