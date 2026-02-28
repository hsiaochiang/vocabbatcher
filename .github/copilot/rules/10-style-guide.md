# 10-style-guide（Style Contract）

> 狀態：**PENDING**
> 來源：（尚未提供 Stitch HTML）

## 1) 字體（Fonts）
- （待匯入 Stitch HTML 後自動萃取或人工補齊）

## 2) 顏色（Colors）
- （待匯入 Stitch HTML 後自動萃取或人工補齊）

## 3) 間距 / 版面（Spacing / Layout）
- 統一使用 4px 基準（4/8/12/16/24/32...）
- 同一層級卡片 padding 一致（避免每頁漂移）
- 主要內容區塊盡量「有效滿版」：避免左右留白不一致

## 4) 按鈕 / 表單 / 互動狀態（Controls & States）
- Primary/Secondary/Link Button：高度/圓角/字重/hover/disabled/loading 必須一致
- 表單狀態：default / focus / error / success / disabled
- 空狀態（empty state）與載入（loading）必須有明確訊息與 skeleton/indicator

## 5) Freeze 機制（避免 UI 返工）
- UI 確認 OK 後：記錄「Style Freeze」決策到 `docs/decisions/`（原因→影響→驗收→證據）
- Freeze 後若需要改 UI：必須先記錄決策（原因→影響→驗收）才能動

## 6) 行動裝置 / 觸控（Mobile / Touch）
- 觸控目標最小尺寸：48×48 dp（依平台設計規範）
- Safe Area：頂部（狀態列）與底部（手勢列 / Home Indicator）必須留空
- Navigation Bar / Tab Bar：高度與圖示規格統一
- 捲動區域需有明確邊界（避免與系統手勢衝突）
- 長按（long-press）行為需有視覺回饋（highlight / tooltip）

## 7) 深色模式（Dark Mode）
- 提供 Light / Dark 兩組色彩 token（或至少預留命名空間）
- 背景：Dark 模式建議 #121212 或品牌深色，避免純黑 #000000
- 文字對比：Dark 模式下前景/背景對比 ≥ 4.5:1
- 圖片/圖示：需額外確認在深色背景上的可見度

## 8) 無障礙（Accessibility）
- 最小字級：14sp（正文），12sp（輔助文字，不可低於此值）
- 色彩對比：前景/背景 ≥ 4.5:1（WCAG AA）
- 可聚焦元件需有明確的 focus indicator
- 按鈕/連結需提供 accessibility label（螢幕閱讀器可讀）
- 觸控回饋：haptic / ripple / 視覺 highlight（至少擇一）

## 9) 使用方式
- 匯入 Stitch：重新跑 bootstrap `--stitch-html`
- 手動填入 tokens：直接編輯本文件的字體/顏色區段，將狀態改為 **FROZEN**
- 做 UI 盤點：依據本文件 + `skills/ui-designer.md` 產出 `docs/uiux/<date>_ui-review.md`
- Freeze：記錄決策到 `docs/decisions/` + `docs/decision-log.md`
