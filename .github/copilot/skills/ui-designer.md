# Skill: ui-designer（UI 前端設計師）

## 任務目標
把「每頁都要慢慢調」變成「有規範可對照、一次修到位」，並把修正計畫做成可交付的清單。

## 依據（Evidence）
- `.github/copilot/rules/10-style-guide.md`（唯一 UI 規範）
- `design/stitch/stitch.html`（Stitch evidence；或補充截圖/錄影/URL）
- 目標頁面/元件檔案（repo 內）

## 輸出（必交付）
- `docs/uiux/<date>_ui-review.md`，內容必含：
  1) **Findings（差異清單）**：逐項列「現況 vs 規範」＋引用規範章節
  2) **Patch Plan（修正計畫）**：可直接執行的修改清單（檔案/元件/範圍）
  3) **Acceptance（驗收）**：如何驗收（視覺/互動/狀態）
  4) **Evidence（證據）**：相關 diff、截圖、或 runlog 位置

## 執行步驟（建議順序）
1) 先讀 style guide，列出「可凍結基準」：字級、按鈕高度、卡片 padding、主色/次色、表單狀態
2) 逐頁比對（或抽 3~5 個代表頁）→ 先抓最大的不一致
3) 只做 Smallest Safe Change：先把 tokens/共用元件拉齊，再調個別頁面
4) 若發現規範本身要改：停止，先記錄決策到 docs/decisions/

## 禁止事項
- 未引用 style guide 就做「主觀美化」
- 一次改太多頁面造成漂移（觸發 scope-guard）
