# PROGRESS.md — VocabBatcher 進度儀表板

> AI 每個 session 結束前必更新。負責人隔週回來只看這一頁。
> 角色綁定見 `WORKFLOW.md` §0。

---

## 專案：VocabBatcher
- **一句話目標：** 國中會考英文單字練習 App，讓學生勾選最多 25 個單字，批次聽錄音、翻牌學習、四題型練習。
- **目前階段：** ③ 開發（垂直切片）— M3-S2「Google 登入 + 雲端基礎」已驗收通過，準備開 S3
- **整體進度：** ▓▓▓▓▓▓▓▓░░ ~68%（M1、M2 完成；M3-S1、S2 完成並驗收通過；S3~S5 未實作；M4 未開始）
- **最後更新：** 2026-07-31 by 執行層

---

## ▶ 下一步就做這個（回來先看這裡）

**寫並開 `BRIEF_S3_考試引擎.md`**（考試設定頁、選擇題中英交互+聽力、作答判分、結果頁）。相依 S1（SpeakButton）與 S2（登入狀態）均已就緒。S3 BRIEF 前需定案：未登入使用者能否考試（建議：可以考但提示「成績不會保存」）。

## ⏳ 等你決定

- 未登入的使用者可以考試嗎？（建議：可以考但提示「成績不會保存」）——S3 BRIEF 前定案即可
- 專案原有的 `.github/copilot-instructions.md`（GitHub Copilot 執行層指示）要保留多久？何時可以淘汰？

---

## ✅ 已完成（最近在前，依 git log 回填）

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

- M3「考試與追蹤」：S1、S2 已完成並驗收通過；S3~S5 切片依序待實作（見 `STAGE_3_PLAN.md`，`BRIEF_S3_考試引擎.md` 尚未寫）
- `.github/` 底下多個 OpenSpec/Copilot 相關檔案目前是 git 未提交的修改狀態（`git status` 顯示大量 `M`），過渡期建議先確認這些改動的用意再決定去留

## 📋 待辦

- [x] M3-S1：發音按鈕全面化（已驗收通過，iPhone/iPad/Android 皆正常）
- [x] 部署至 GitHub Pages（提前於 S1 驗收階段完成，見 `DECISIONS.md` 2026-07-30 條目）
- [x] M3-S2：Google 登入 + Firebase 雲端基礎（已驗收通過，iPhone/iPad/Android 皆正常）
- [ ] M3-S3：考試引擎（頁數範圍+題數，選擇題中英交互+聽力）
- [ ] M3-S4：成績紀錄與累積錯誤率統計
- [ ] M3-S5：錯題複習卷
- [ ] M4：拼字填空、批次歷史/續作、品質收斂
