# ADR-006：狀態管理使用 React Context + localStorage

日期：2026-05-31
狀態：已採用

## 背景

App 需要管理兩種狀態：
1. `allWords`（1231 筆單字，啟動時 fetch 一次，之後唯讀）
2. `batches`（使用者建立的批次清單，需要持久化）

需要決定使用什麼狀態管理工具，以及持久化方案。

## 決定

全域狀態只用 `React.createContext` + `useState`，持久化用 `localStorage`。

## 理由

1. **規模太小**——4 個頁面、2 種狀態，引入 Redux / Zustand 的 boilerplate 代價大於收益
2. **localStorage 容量足夠**——每個批次約 5KB（25 筆 VocabEntry），存 200 個批次也才 1MB，遠低於 localStorage 的 5–10MB 上限
3. **同步寫入最簡單**——每次 `setBatches` 時順便 `localStorage.setItem`，用 `useEffect` 自動同步

## 評估過的替代方案

| 方案 | 為什麼沒選 |
|------|-----------|
| Zustand | 更輕量但仍是外部依賴，專案規模不需要 |
| Redux Toolkit | boilerplate 太多，action/reducer/slice 三層架構對這個 App 過度設計 |
| React Query | 適合 server state 管理，不適合純本地狀態 |
| IndexedDB | API 複雜（需要 transaction），localStorage 的容量對這個資料量完全足夠 |

## 後果

- 若未來加入帳號同步或雲端備份，Context 架構可能需要重構為更正式的狀態管理
- localStorage 在隱私模式下可能被禁用或容量限制——但 App 在一般模式下使用，影響極小
- 所有狀態修改都在 `AppContext.tsx` 一個檔案裡，好處是集中管理，壞處是這個檔案會越來越大
