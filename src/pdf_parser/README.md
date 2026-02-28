# VocabBatcher PDF Parser

將國中會考英文單字 PDF 教材轉換為結構化 JSON 單字庫。

## 安裝

```bash
pip install -r requirements.txt
```

## 使用方式

```bash
python -m src.pdf_parser --input top2025.pdf --outdir output/
```

### 參數

| 參數 | 必填 | 說明 |
|------|------|------|
| `--input` | ✅ | PDF 檔案路徑 |
| `--outdir` | ✅ | 輸出目錄 |
| `--min-frequency` | | 最低頻率門檻（預設不過濾） |
| `--page-range` | | 頁碼範圍，格式 `start-end`（例：`1-50`） |
| `--rule` | | parser 規則模組名稱（預設 `top2025`） |

## 輸出檔案

| 檔案 | 說明 |
|------|------|
| `vocab.raw.json` | 逐頁原始解析結果 |
| `vocab.cleaned.json` | 去重、清雜訊後的乾淨資料（按 word 排序） |
| `vocab.qa_report.json` | 品質報告（含 parse_confidence、issues） |

### vocab.cleaned.json 欄位

```json
{
  "word": "apple",
  "pos": "n.",
  "zh_definition": "蘋果",
  "frequency": 3,
  "source_page": [5, 12],
  "ipa_us": "/ˈæp.əl/",
  "ipa_uk": "/ˈæp.əl/",
  "parse_confidence": 0.95,
  "issues": []
}
```

## 開發

```bash
# 執行測試
pytest tests/ -v
```
