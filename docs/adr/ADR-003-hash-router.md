# ADR-003：路由使用 HashRouter 而非 BrowserRouter

日期：2026-05-31
狀態：已採用

## 背景

React Router v6 提供兩種路由模式：
- `BrowserRouter`：URL 像 `/batch/123`，需要 server 支援 SPA 路徑重寫（所有路徑都回傳 `index.html`）
- `HashRouter`：URL 像 `/#/batch/123`，不需要 server 設定

我們的 App 部署在 GitHub Pages，它是純靜態檔案 host，不支援 URL rewrite。

## 決定

使用 `HashRouter`（URL 格式：`/#/batch/123`）。

## 理由

1. **GitHub Pages 不支援 SPA 路徑重寫**——直接輸入 `/batch/123` 或重新整理會得到 404
2. **零設定**——不需要自訂 404.html redirect hack
3. **功能完整**——所有 React Router 功能（嵌套路由、params、navigate）都正常運作

## 評估過的替代方案

| 方案 | 為什麼沒選 |
|------|-----------|
| 自訂 404.html + redirect hack | 可行但脆弱，依賴 GitHub Pages 的 404 回傳行為 |
| 換 Cloudflare Pages / Netlify | 支援 SPA redirect，但增加部署複雜度和外部依賴 |
| 只用首頁路由（不做深層連結）| 犧牲使用者體驗，無法直接分享批次連結 |

## 後果

- URL 有 `/#/` 前綴，稍微不美觀（但使用者不會注意到）
- `import.meta.env.BASE_URL` 需要搭配 `vite.config.ts` 的 `base: '/vocabbatcher/'` 使用
- fetch 資料時路徑要用 `import.meta.env.BASE_URL + 'data/vocab.cleaned.json'`
