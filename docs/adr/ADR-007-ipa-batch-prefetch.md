# ADR-007：IPA 音標從 dictionaryapi.dev 一次性批次補充

日期：2026-05-31
狀態：已採用

## 背景

App 翻牌卡的正面需要顯示國際音標（IPA），幫助學生學發音。`top2025.md` 原始資料沒有音標欄位，需要從外部來源取得。

有兩種策略：
1. App runtime 即時查詢字典 API
2. 開發時一次性批次查詢，結果存入 `vocab.cleaned.json`

## 決定

使用 `src/pdf_parser/fetch_ipa.py` 一次性批次查詢 dictionaryapi.dev，結果快取在 `output/ipa_cache.json`，然後合併回 `vocab.cleaned.json`。App 不在 runtime 呼叫任何 API。

## 理由

1. **離線可用**——App 設計為 PWA，不依賴網路。如果 runtime 查 API，離線就沒音標
2. **避免 rate limit**——1231 個字即時查詢會被限流，而且每次使用都查一次很浪費
3. **快取續傳**——`ipa_cache.json` 記住已查過的字，中斷後重跑只查新的

## 評估過的替代方案

| 方案 | 為什麼沒選 |
|------|-----------|
| Runtime 即時查詢 | 需要網路、有 rate limit、每次啟動都要等 |
| 使用本地字典 DB（如 CMU Pronouncing Dictionary）| 只有 ARPAbet 格式，不是 IPA；需要轉換表 |
| 人工手動標注 1231 筆 | 工作量太大，且容易出錯 |

## 後果

- 覆蓋率不是 100%：US 音標 93.7%（1154/1231），UK 音標 30.6%（377/1231）
- 60 個字完全沒有 IPA——主要是功能詞（and, at, be, for）和專有名詞（America, Christmas）
- 若未來更新單字清單，需要重跑 `fetch_ipa.py`
- 來源 API（dictionaryapi.dev）是免費開源專案，穩定性無保證——但因為是一次性查詢，查完就不依賴了
