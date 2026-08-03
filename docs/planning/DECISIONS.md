# DECISIONS.md — 變更與決策日誌

> 給 AI：**任何偏離原始需求(REQUIREMENTS.md)的改動，都要在這裡記一筆**，並同步更新 REQUIREMENTS.md。
> 給負責人：隔週回來時，看這裡就知道「為什麼系統跟我當初想的不一樣」。
> 角色綁定見 `WORKFLOW.md` §0。
>
> **本專案 2026-07-06 前的歷史決策記錄在 `docs/decision-log.md` 與 `docs/decisions/`（OpenSpec 舊流程），
> 本檔只記錄 2026-07-06 起、兩層 vibe coding 流程下的新決策，不重複搬移舊紀錄。**

---

## 2026-07-31　M3-S2 修復：Google 登入改用 signInWithRedirect（偏離 BRIEF 原定實作方式）

- **狀態：** 已採納
- **背景：** `BRIEF_S2_雲端帳號.md` 原始實作採 `signInWithPopup`（跳出視窗登入）。負責人於 iPhone、iPad、Android 三平台實測，點擊「使用 Google 登入」後畫面閃一下即消失、登入未完成——這是手機瀏覽器（iOS Safari、Android Chrome）普遍封鎖或立即關閉彈出視窗的已知限制。
- **改動：** `src/services/auth.ts` 的 `signInWithGoogle()` 改為 `signInWithRedirect`（整頁導向登入），新增 `completeRedirectSignIn()` 於頁面載入時接住導回結果並建立 `users/{uid}` 文件；`UserBadge.tsx` 新增登入失敗錯誤提示文字。修復後三平台重測皆成功。
- **影響的原始需求：** 不影響 R9 驗收標準本身（使用者能以 Google 帳號登入、跨裝置同步），僅實作方式從彈出視窗改為整頁導向；`BRIEF_S2_雲端帳號.md` 與 `STAGE_3_PLAN.md` 的「發音一律經 tts.ts」等跨切片一致性規則不受影響。往後 S3~S5 若涉及登入流程，一律沿用 `signInWithRedirect` 模式。
- **負責人是否同意：** 是（負責人回報成功後追認）

## 2026-07-30　提前執行 M4 部署項目：建立 GitHub Pages 正式環境

- **狀態：** 已採納
- **背景：** M3-S1「發音按鈕全面化」驗收時，負責人在本機 LAN（`vite --host` 開放區網 IP）測試，iPad Safari 與 Android Chrome 皆卡在「連線中」空白畫面（疑似 Windows 防火牆 Public 設定檔或路由器 AP 隔離導致連線被靜默丟棄）。負責人要求改用正式環境測試，因為正式上線本來就不應依賴負責人本機網路。
- **改動：** 新增 `.github/workflows/deploy.yml`，push 到 `main` 時自動 `npm run build` 並用官方 `actions/upload-pages-artifact` + `actions/deploy-pages` 部署到 GitHub Pages（`https://hsiaochiang.github.io/vocabbatcher/`）。此為 `ROADMAP.md` M4「部署至 GitHub Pages」項目的提前執行，非依原排序在 M3 全部完成後才做。
- **影響的原始需求：** 無新增/刪除需求條目；`ROADMAP.md` M4 的部署工作項目已提前完成，M4 階段屆時可跳過此項。後續 S2~S5、M4 其餘項目仍沿用同一 GitHub Pages 網址，不需另建部署管線。
- **負責人是否同意：** 是（負責人主動要求）

## 2026-07-06　使用者回饋功能定案：併入 M3，新增雲端帳號(推翻原排除項)

- **狀態：** 已採納
- **背景：** 負責人提供了關鍵使用者回饋的 4 項期待：(1) 每個單字旁有發音按鈕；(2) 選擇題考試，可設頁數範圍與題數，中→英/英→中交互出題；(3) 聽力考試(英文發音→選中文)，可設頁數範圍；(4) 每位使用者的每次考試成績、累積錯誤單字比率，並依錯誤率再出複習卷。
- **改動：** 三項決策(負責人 2026-07-06 拍板)：
  1. **「每位使用者」採雲端帳號同步**(Google 帳號登入，後端用 Firebase)——**推翻原始範圍「不做帳號系統/雲端同步」的排除項**。
  2. **考試出題範圍依頁數範圍**，跳脫 25 字批次限制；批次仍保留給聽錄音/翻牌學習。
  3. **新功能併入 M3 並重定義**為「考試與追蹤」；原 M3 的拼字填空題型與批次統計挪到 M4。
- **影響的原始需求：** 新增 R8~R12；刪除排除清單「不做帳號系統/雲端同步」;R6/R7 範圍調整(詳見 `REQUIREMENTS.md`)。技術評估：全功能純網頁(PWA)可達成，iPad Safari 與 Android Chrome 皆支援 Web Speech API，不需開發原生 App。
- **負責人是否同意：** 是

## 2026-07-06　套入兩層開發模式(初始化)

- **狀態：** 已採納
- **背景：** 專案原本由 OpenSpec + GitHub Copilot（含 WOS agent）驅動開發，文件散落在 `docs/roadmap.md`、`docs/decision-log.md`、`.github/copilot-instructions.md` 等處。負責人（Wilson）決定改用「兩層 vibe coding」流程（規劃層 = Cowork、執行層 = Codex CLI），逐步取代舊流程。
- **改動：** 在專案根補齊 `AGENTS.md`、`WORKFLOW.md`、`REQUIREMENTS.md`、`ROADMAP.md`、`PROGRESS.md`、`DECISIONS.md`。原有 `.github/copilot-instructions.md`（GitHub Copilot 專用指示）因已存在且內容完整，依非破壞性原則保留、不覆蓋，待負責人逐步淘汰舊流程時再決定去留。
- **影響的原始需求：** 無（純流程/工具變更，不影響產品功能需求）。
- **負責人是否同意：** 是

## 2026-07-06　待處理：使用者回饋新增功能需求

- **狀態：** 已結案(由上方「使用者回饋功能定案」決策取代)
- **背景：** 負責人提到「有關鍵使用者回饋，描述了對這個專案期待的功能」，需要完成這些功能，但尚未提供回饋的具體內容。
- **改動：** 尚未進行任何實作。待負責人提供回饋內容後，由規劃層拆解為新的 `REQUIREMENTS.md` 條目，評估併入 M3 或另開里程碑，再寫 `BRIEF` 交給執行層。
- **影響的原始需求：** 待評估（可能新增 R8 及以後的條目，或調整 M3 範圍，詳見 `ROADMAP.md`「重大相依與風險」）。
- **負責人是否同意：** 待確認

<!-- 新的決策往上加，保持最新在最上面 -->
