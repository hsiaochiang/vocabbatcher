# ADR-001：資料來源從 PDF 改為 Markdown

日期：2026-05-31
狀態：已採用

## 背景

原始資料是教育部提供的 `top2025.pdf`，一份 62 頁的 PDF 表格，列出國中會考常用 2000 字。我們最初用 pdfplumber 解析它，但發現 PDF 表格只有「英文單字」和「出現年份」兩個欄位——完全沒有詞性（pos）和中文定義（zh_definition）。

解析出的 `vocab.cleaned.json` 裡 pos 和 zh_definition 全是 null，App 的翻牌卡背面一片空白，根本無法用來學習。

## 決定

將 PDF 手動轉為 Markdown 表格（`0resource/top2025.md`），補上詞性和中文定義欄位，作為 parser 的主力輸入來源。

## 理由

1. **PDF 本身就沒有這些資料**——不是解析能力不夠，是源頭格式的限制
2. **Markdown 表格結構穩定**——比 PDF 表格容易解析，regex 就能處理
3. **可以加入額外欄位**——後來又加了「頁碼」欄，方便追溯原始位置

## 評估過的替代方案

| 方案 | 為什麼沒選 |
|------|-----------|
| 串接 DictCN / MoeDict API 自動補充中文 | 速率限制、品質不穩定、不是每個字都查得到 |
| 繼續強化 PDF parser regex | PDF 本身就沒有 pos/zh_def 欄位，再強也解不出來 |
| 直接用現成字典 JSON（BNC/COCA + cedict）| 會考出題分佈和通用字典不同，需要 top2025 這份特定清單 |

## 後果

- `0resource/top2025.md` 需要手動維護——若未來有新版 top2025，要重新轉換
- 舊的 `rules/top2025.py`（PDF parser）保留但不再是主力路徑
- PDF 頁碼透過另一個腳本提取後，補回 MD 的第四欄（`source_page`）
