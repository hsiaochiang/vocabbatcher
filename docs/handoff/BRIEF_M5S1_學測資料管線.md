# BRIEF_M5S1_學測資料管線.md — M5 切片 1：學測 PDF → 獨立乾淨 JSON 單字庫

> 交接合約：規劃層 → 執行層，2026-08-03。
> 對應 `docs/planning/REQUIREMENTS.md` R13、`docs/planning/DECISIONS.md` 2026-08-03「新增 M5」條目。
> 切片全景見 `docs/planning/STAGE_5_PLAN.md`（M5-S1，無相依）。**這片只做資料，完全不動 App 前端邏輯**——先讓負責人肉眼核對資料正確性，通過後才會開 M5-S2（App 端會考/學測來源切換）。這個順序是刻意的：比照 `DECISIONS.md` 2026-08-03「頁碼固定偏移 2 頁」的教訓，資料錯誤如果跟 App 功能一起做完才驗收，會很晚才被發現、回頭修的成本更高。

## 開場指令（執行層開工先做）
1. 讀 `docs/planning/PROGRESS.md` 恢復脈絡。
2. 工作目錄為專案根目錄（Python `src/pdf_parser/` pipeline）。

## 目標（一句話）
> 把 `0resource/TopAcademy 學測高頻率單字表.pdf` 轉成一份跟現有會考單字庫完全獨立、格式相容、可供負責人抽查驗證的乾淨 JSON 單字庫（`output/gsat/vocab.cleaned.json`），並複製一份到前端資料目錄備用。

## 現況（可直接重用）

- **會考單字庫的正式資料來源不是直接解析 PDF**：因為 PDF 文字抽取有排版/字型問題（`src/pdf_parser/ocr_extractor.py` 開頭註解有說明），實際生產資料是一份手動/半自動轉出的 `0resource/top2025.md`（表格式 Markdown，依「出現次數」分章節），由 `src/pdf_parser/rules/top2025_md.py` 解析。**這條「先轉 Markdown、再用規則解析」的路徑比較可靠，本片比照辦理，不要硬解 PDF 原始檔。**
- `top2025.md` 格式範例（開頭幾行）：
  ```markdown
  ## 十、出現次數：10

  | 單字 | 詞性 | 中文定義 | 頁碼 |
  |------|------|---------|------|
  | **a** | [art.] | 一個;一種 | 3 |
  ```
  `src/pdf_parser/rules/top2025_md.py` 用正則 `_FREQ_HEADER_RE`（比對 `## ...出現次數：N`）、`_TABLE_ROW_RE`（比對表格資料列）解析這種格式，`PRINTED_PAGE_OFFSET` 常數處理頁碼偏移。
- `src/pdf_parser/models.py` 定義 `VocabEntry`（原始）／`CleanedEntry`（清洗後）兩個 `TypedDict`，欄位是 `word/pos/zh_definition/frequency/source_page/ipa_us/ipa_uk`（+ `CleanedEntry` 多 `parse_confidence/issues`）。
- `src/pdf_parser/cleaner.py` 的 `clean_entries()` 用固定欄位建構 `CleanedEntry`（第 43~51 行、第 85~97 行），新增欄位要在這裡同步加，不會自動透傳未宣告的欄位。
- `src/pdf_parser/qa.py` 的 `compute_confidence()`／`compute_issues()` 只讀 `_OPTIONAL_FIELDS = ["pos", "zh_definition", "frequency", "ipa_us", "ipa_uk"]`，新增的 `level` 欄位**不需要**、也**不要**加進這個信心分數計算（維持既有評分邏輯不變）。
- `src/pdf_parser/__main__.py` 的 `_run_md()` 已經是「讀 `.md` 副檔名 → 走 Markdown pipeline」的通用流程（呼叫 `parse_md_file` → `clean_entries` → `generate_qa_report`），本片理論上不用改 `__main__.py`，只要新的解析規則模組提供跟 `top2025_md.py` 的 `parse_md_file()` 同樣簽名的函式，並在 `_run_md()` 需要的地方 import 對應規則即可（見任務 3 的實作彈性）。

## 學測 PDF 排版跟會考版不一樣的地方（規劃層已讀過內容，先告訴你）

- 章節不是單純依「出現次數：N」逐一分，而是：「出現次數：10~7」「出現次數：6」「出現次數：5」「出現次數：4」「出現次數：3」「出現次數：2」「出現次數：1」，其中 **「出現次數：2」與「出現次數：1」底下又各自再分「第四級」「第五級」「第六級」三個 Level 子章節**。
- 單字資料本身還帶有 **Level 標記**（第三/四/五/六級，看起來是單字難度分級)。
- PDF 內容裡有逐年出現標記（例如「05 07 09」代表 2005、2007、2009 年學測出現過），**負責人已確認不需要保留這個欄位**，只要出現次數與 Level。
- 你可以直接讀 `0resource/TopAcademy 學測高頻率單字表.pdf` 原始內容確認排版細節（PDF 文字抽取可能有字型問題，讀不清楚的地方用你手上可用的工具盡量交叉確認，例如試著用不同抽取方式或工具重讀同一頁比對）。

## 任務

1. **產出學測 Markdown 轉錄檔 `0resource/topsat.md`**：
   - 格式比照 `top2025.md`（表格式，依章節分），但這次要加一欄 `Level`（值為「第三級」「第四級」「第五級」「第六級」其中之一；如果某個字沒有標明 Level，欄位留空即可）。
   - 章節標題請用清楚可辨識的格式，方便寫解析正則，例如：
     ```markdown
     ## 出現次數：10~7

     | 單字 | 詞性 | 中文定義 | Level | 頁碼 |
     |------|------|---------|-------|------|
     | **unique** | [adj.] | 獨特的 | | 12 |
     ```
     「出現次數：2」「出現次數：1」底下若有 Level 子章節，你可以選擇：(a) 用子標題（例如 `### 第四級`）分節，或 (b) 直接把 Level 值填進每一列的 Level 欄——兩種都可以，挑你比較不容易解析出錯的方式，但整份文件裡要一致，不要兩種混用。
   - 這一步是精確度最關鍵的環節，錯字/漏字/中文定義誤植都會直接反映到 App 上使用者看到的內容。**盡可能交叉核對**（例如同一頁多讀幾次、注意常見 OCR 誤判如 `l`/`1`、`O`/`0`），並在收工報告裡誠實記錄你對這份轉錄檔的信心程度與可能有疑慮的地方（例如某幾頁字型模糊、某幾個字不確定拼法），不要隱瞞不確定的部分。

2. **新增 `level` 欄位到資料模型**：
   - `src/pdf_parser/models.py`：`VocabEntry`、`CleanedEntry` 都加上 `level: str | None`。
   - `src/pdf_parser/cleaner.py` 的 `clean_entries()`：`enriched` 階段的 `normalized = VocabEntry(...)`（第 43~51 行）與最後 `cleaned.append(CleanedEntry(...))`（第 85~97 行）都要多帶 `level` 欄位（用 `_trim_or_null()` 處理，空字串轉 `None`，跟其他字串欄位一致）。
   - 會考既有的 `top2025_md.py` 解析出來的 `VocabEntry` 不會有 `level`（維持 `None`），**不影響會考既有資料與既有 pytest 測試的預期輸出**——這件事你動手前後都要各跑一次既有測試（`python -m pytest tests/`）確認沒有壞掉。

3. **新增學測專用解析規則 `src/pdf_parser/rules/topsat_md.py`**：
   - 架構比照 `top2025_md.py`（正則比對章節標題與表格列、`_strip_bold`／`_strip_pos_brackets`／`_clean_definition` 這類小工具函式可以重用邏輯風格，不用整段複製，你可以判斷哪些真的能共用、哪些因格式不同要重寫）。
   - 提供跟 `parse_md_file(md_path) -> ParseResult` 一樣的函式簽名，讀你在任務 1 寫的 `topsat.md`，輸出的每筆 `VocabEntry` 要帶出 `level`。
   - 出現次數章節「10~7」這種範圍寫法，要能正確解析成一個數字用的頻率值，或你判斷更合理的處理方式（例如取範圍下界、或該章節本身視為同一個 frequency 分組值），只要在收工報告講清楚你的處理邏輯即可，沒有絕對對錯，合理就好。
   - 頁碼欄位處理：學測 PDF 有沒有跟會考版一樣「PDF 內部頁碼 vs 課本印刷頁碼」的固定偏移，你要自己核對（不能假設偏移量一樣是 2，那是會考版 `top2025.pdf` 特有的裝訂結構），核對方式可以是：挑幾個你能在原始 PDF 上直接看到印刷頁碼的地方，比對 PDF 內部頁碼差幾頁。**這是本片第二重要的資料正確性環節**，處理方式跟 `top2025_md.py` 的 `PRINTED_PAGE_OFFSET` 常數一樣：如果確認有固定偏移，比照寫一個明確命名的常數並註解清楚；如果沒有偏移或無法確認，就先不做偏移轉換，在報告裡誠實記錄。

4. **產生輸出並複製到前端**：
   - 跑 `python -m src.pdf_parser --input 0resource/topsat.md --outdir output/gsat --rule topsat`（或你實際串接規則模組的方式，只要最終能透過既有 CLI 或等價腳本跑出結果即可，不強制一定要用 `--rule` 參數這個確切機制，你可以評估 `_run_md()`／`load_rule()` 現有的規則選擇機制是否需要小幅擴充才能指到新規則，這部分你有實作彈性），確認產出 `output/gsat/vocab.raw.json`、`output/gsat/vocab.cleaned.json`、`output/gsat/vocab.qa_report.json`。
   - 把 `output/gsat/vocab.cleaned.json` 複製一份到 `exam-vocab-batcher/public/data/vocab.gsat.cleaned.json`（新檔名，**不要覆蓋或修改既有的 `exam-vocab-batcher/public/data/vocab.cleaned.json`**，那是會考資料，這片完全不動）。

5. **測試**：
   - 新增 `tests/test_topsat_md.py`，比照 `tests/test_top2025_md.py` 的測試風格，涵蓋：章節標題解析、Level 欄位解析、表格列解析、頁碼處理邏輯（有沒有偏移）。
   - `python -m pytest tests/` 全部通過（含既有會考測試，確認沒有因為新增 `level` 欄位而壞掉）。

## 邊界（本切片不做）

- **完全不動 App 前端邏輯**：不改 `exam-vocab-batcher/src/` 底下任何 `.tsx`／`.ts` 檔案（前端 `VocabEntry` TS 型別要不要加 `level` 欄位，留給 M5-S2 決定，這片只負責把資料準備好放在 `vocab.gsat.cleaned.json`）。
- 不改既有會考 pipeline：`src/pdf_parser/rules/top2025_md.py`、`0resource/top2025.md`、`output/vocab.*.json`、`exam-vocab-batcher/public/data/vocab.cleaned.json` 一律不動。
- 不用把 `level` 欄位加進 `qa.py` 的 `compute_confidence()`／`compute_issues()` 信心分數計算，維持既有評分邏輯。
- 不做「會考/學測合併」的任何邏輯——兩份資料要維持完全獨立的檔案，不要寫任何合併/交叉引用的程式碼。
- 不用處理 PDF 裡的個別出現年份標記（例如「05 07 09」），這個資訊不用保留進 `topsat.md` 或 JSON 輸出。

## 驗收（負責人操作）

1. 打開 `output/gsat/vocab.cleaned.json`（或請執行層在報告裡附一份精簡摘要／抽樣清單），對照你手上的 `TopAcademy 學測高頻率單字表.pdf`，抽查至少 20~30 個單字：
   - 拼字、詞性、中文定義是否跟 PDF 上印的一致。
   - Level 標記（第三/四/五/六級）是否正確。
   - 出現次數是否合理（跟 PDF 目錄章節對得上）。
   - 每個 Level 至少抽查幾個字，不要只集中在同一個章節。
2. 看一下 `output/gsat/vocab.qa_report.json` 的整體統計（總筆數、`parse_confidence` 平均、issues 數量），跟報告裡執行層的說明對照，確認沒有異常大量的低信心筆數。
3. 確認 `exam-vocab-batcher/public/data/vocab.gsat.cleaned.json` 存在，且內容跟 `output/gsat/vocab.cleaned.json` 一致。
4. 確認 `exam-vocab-batcher/public/data/vocab.cleaned.json`（會考資料）沒有被動到（可以用 `git status`／`git diff` 確認這個檔案沒有出現在改動清單裡）。
5. `python -m pytest tests/` 全部通過（執行層在報告裡會附結果，你可以自己重跑一次確認）。
6. **這一步通過才會開 M5-S2**——如果抽查發現資料有明顯錯誤（拼字、定義、Level 錯很多），先不要放行，回頭跟規劃層討論要人工修正 `topsat.md` 還是調整解析規則。

## 收工指令（執行層收工必做）

1. 更新 `docs/planning/PROGRESS.md`：加一行本切片成果；「▶ 下一步」改為「M5-S1 待負責人抽查資料正確性，過了才開 M5-S2（App 端來源切換）」。
2. 若有任何偏離本 BRIEF 的改動（尤其是章節解析邏輯、頁碼偏移處理方式的判斷）→ 記 `docs/planning/DECISIONS.md`。
3. 給負責人「現在你能做什麼」＋操作步驟＋一份精簡的抽樣清單（例如挑 10~15 個字直接列在報告裡，方便負責人快速對照，不用要求負責人自己去開 JSON 檔）。
4. **完成以上所有事項、且 `python -m pytest tests/` 全部通過後，將本次變更 commit 並 push 到遠端（`origin main`）。** commit message 用一句話講清楚這片做了什麼（例如「功能: 新增學測單字庫資料管線」），可先 `git log --oneline -10` 看最近幾筆訊息風格再照著寫。push 前務必確認 `git status` 沒有不該提交的檔案。若 push 失敗，不要 force push，把卡住的狀況寫清楚在報告裡。
