A. 給 GitHub Copilot（Python：PDF → JSON）
(此專案無變動，與 v1 相同)

請幫我用 Python 3.11 寫一個可在 Windows 執行的 CLI 工具，將 top2025.pdf 轉成會考英文單字 JSON。

1. 使用 pdfplumber 或 pypdf 抽取每頁文字，保留頁碼。
2. 解析欄位：word, pos, zh_definition, frequency, source_page，若有音標則填 ipa_us/ipa_uk。
3. 輸出三檔：vocab.raw.json, vocab.cleaned.json, vocab.qa_report.json。
4. vocab.cleaned.json 去重（同 word+pos 合併）、清雜訊、trim、空值為 null。
5. 產出 parse_confidence（0~1）與 issues 陣列。
6. CLI 參數：--input, --outdir, --min-frequency, --page-range。
7. pytest 單元測試 + README。
8. 先列出你推測的 PDF 行格式 regex，parser 設計成可替換規則。

---

B. 給 Stitch（前端雛型）— 大幅修改
請為「國中會考英文單字練習 App（Android 優先）」產出高保真手機 UI 原型。
核心情境：從單字庫篩選並勾選最多 25 字 → 聽批次錄音 或 做練習。

1. 風格：乾淨明亮學習風、大按鈕、單手操作、高可讀字體。
2. 核心流程：
首頁(歷史批次+新建) → 條件篩選 → 勾選(計數器 N/25) → 批次 Hub → 選功能：
- 🔊 批次錄音：設定間隔(3/5/10秒) → 產生 MP3 → 播放器（進度條 + 目前單字高亮）
- 📖 逐字學習：翻牌卡（英文 → 中文+詞性+發音）
- ✏️ 練習測驗：選題型 → 作答 → 結果+錯題重練
- 📊 批次統計：正確率/錯題
3. 6 個畫面：
- Home：歷史批次列表 + 大按鈕「建立新批次」
- Batch Builder：上半條件篩選；下半勾選清單 + 即時計數器 N/25 + 滿額禁選
- Batch Hub：四功能入口卡片（錄音/逐字/練習/統計）
- Audio Player：間隔選擇(3/5/10) → 產生 → 播放器 + 進度條 + 目前字高亮 + 單字清單
- Vocab Card：翻牌卡，正面英文大字，背面中文+詞性+發音
- Quiz + Result：作答+結果合併，含錯題重練按鈕
4. UX 條件：
- 每頁一個主 CTA
- 自動儲存中斷（首頁顯示「繼續上次」）
- 勾選計數器即時更新，25 滿額時提示
- Touch target >= 44dp
- Audio Player 顯示目前播到第幾個字

---

C. 給 OpenSpec（程式規格）— 大幅修改
請撰寫 React Native + Expo 的產品與技術規格（不直接產碼），專案名稱：ExamVocabBatcher。
核心情境：勾選最多 25 字 → 產生批次錄音(MP3) 或做練習。

1. MVP 功能：
- 載入本機 JSON 單字庫，支援條件篩選（頁碼/頻率）+ 手動勾選（上限 25）
- 批次錄音產生：TTS 唸「英文單字」→ 靜音間隔 → TTS 唸「中文意思」→ 靜音間隔 → 下一個字… 串接成批次音訊，App 內播放（進度條 + 目前字高亮）
- 間隔可選 3/5/10 秒
- 逐字學習：翻牌卡
- 四題型：中→英、英→中、拼字填空、聽音選字（題庫限本批次）
- 成績、錯題重練、批次歷史
2. 非功能需求：
- 首屏 < 2 秒（中階 Android）
- 斷網可學
- 批次紀錄持久化
3. 架構規格：
- data/（JSON 載入與索引）
- domain/batch/（條件篩+勾選+上限 25+持久化）
- domain/audio/（TTS 合成+靜音插入+播放控制+進度追蹤）
- domain/practice/（四題型+判分+錯題）
- domain/progress/（歷史+統計）
- features/（6 頁畫面）
- infra/（TTS adapter、dictionaryapi adapter、storage adapter）
4. 音訊技術方案：
- 方案 A（MVP）：expo-speech 逐字唸 + 用 setTimeout 控制間隔定時播放，不產生檔案
- 方案 B（增強）：用原生模組合成完整 MP3 存檔，可重播
- 建議先實作方案 A
5. 驗收標準：
- 勾選 25 字可穩定建立批次
- 三種間隔(3/5/10)播放時序正確
- 四題型完整判分
- 歷史批次可重新進入
6. 延後但保留規格：帳號、雲端同步、匯出 MP3 到檔案系統