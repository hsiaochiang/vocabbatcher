# ADR-005：CSS 使用 Tailwind v4 + @tailwindcss/vite

日期：2026-05-31
狀態：已採用

## 背景

原始規格書指定 Tailwind CSS v3，需要 `tailwind.config.ts` + `postcss.config.js` 的傳統設定方式。但在執行 `npm install tailwindcss` 時，npm 預設安裝了 v4（目前最新版）。

Tailwind v4 推出了 Vite 專屬 plugin（`@tailwindcss/vite`），設定方式和 v3 完全不同。

## 決定

使用 Tailwind v4 + `@tailwindcss/vite` plugin，CSS 中直接 `@import "tailwindcss"`，不用 PostCSS。

## 理由

1. **v4 是當前穩定版**——刻意降版到 v3 反而增加維護負擔
2. **Vite 原生整合更快**——不需要 PostCSS pipeline，建構速度更快
3. **設定更簡潔**——不需要 `tailwind.config.ts` 和 `postcss.config.js`，自訂 theme 用 CSS 的 `@theme` 指令

## 評估過的替代方案

| 方案 | 為什麼沒選 |
|------|-----------|
| 降版到 Tailwind v3 | 增加維護負擔，v3 逐漸進入維護模式 |
| 用 v4 但走 PostCSS 方式 | v4 推薦 Vite plugin，PostCSS 方式是 fallback |

## 後果

- 網路上大多數 Tailwind 教學是 v3 語法，搜尋時要注意版本
- `content: [...]` 設定方式不適用於 v4——v4 自動掃描
- 自訂色彩用 `@theme { --color-primary: #3c83f6; }`，不是 `theme.extend.colors`
- 自訂 `darkMode: 'class'` 在 v4 改為 CSS 層的 `@variant dark { ... }`
