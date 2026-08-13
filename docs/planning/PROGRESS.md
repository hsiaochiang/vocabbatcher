# PROGRESS.md — VocabBatcher 進度儀表板

> AI 每個 session 結束前必更新。負責人隔週回來只看這一頁。
> 角色綁定見 `WORKFLOW.md` §0。

---

## 專案：VocabBatcher
- **一句話目標：** 國中會考英文單字練習 App，讓學生勾選最多 25 個單字，批次聽錄音、翻牌學習、四題型練習。
- **目前階段：** 🎉 **M1~M5 全部里程碑驗收通過並穩定上線**。成果文件交付閘已補齊（`USER_MANUAL.md`／`DEVELOPER_LOG.md` 涵蓋至 M5）；2026-08-13 修復三個部署/前端 bug（詳見下方），Firebase Hosting 與 GitHub Pages 備援兩邊皆已重新部署驗證正常
- **整體進度：** ▓▓▓▓▓▓▓▓▓▓ 100%（M1~M5 全部完成並驗收通過，目前為穩定維運狀態）
- **最後更新：** 2026-08-13 by 執行層

---

## ▶ 下一步就做這個（回來先看這裡）

**學測 Minecraft 故事模式全部完成，待負責人在自己裝置上實際操作驗收。**
- 背景：負責人想在學生背單字時額外提供「用整頁單字寫成的 Minecraft 主題故事」，用敘事法增加記憶效果，規劃層規劃了完整計畫（見 `C:\Users\wilson_hsiao\.claude\plans\merry-enchanting-avalanche.md`）。
- 切片1（第16~20頁試行，規劃層直接手寫）：已完成，負責人審閱通過，成果在 `output/story/gsat/stories_pilot_16_20.json`。
- 切片2（剩餘75頁，第一次嘗試）：**已否決**——執行層用固定模板腳本套字取巧，詳見 `DECISIONS.md` 2026-08-13「學測故事模式切片2模板化生成不合格」條目。
- 切片2b（剩餘75頁，重做版）：**已通過品質審查，可以進入切片3。** 執行層這次把每句故事明文寫在資料檔（`output/story/gsat/manual_pages_s2b.mjs`），規劃層獨立驗證（不只信報告）：576句句型骨架無重複、`wordList` 與正式單字資料逐頁完全一致、中文括號標註100%正確，並抽查報告沒有主動附上的第14/52/64頁確認內容自然、用字語意正確。發現一個報告未誠實揭露的偏離：BRIEF訂「每句最多3個單字」，實際179句（約31%）超過，最多一句塞5個字；負責人看過具體例句後選擇**接受現狀，不需重做**（見 `DECISIONS.md` 2026-08-13「切片2b 重做通過但密度超出上限」條目）。完整版 80 頁資料在 `output/story/gsat/stories.gsat.json`（尚未複製進 `exam-vocab-batcher/public/data/`，等切片3才會接進去）。
- 切片3（App 端串接：`Batch.sourcePage`、`BatchHubPage` 故事分頁、`StoryPage`）：**已完成，待負責人實機驗收。** 頁碼快速建立的學測批次會記住來源頁碼；若該頁在 `stories.gsat.json` 有 Minecraft 故事，批次 Hub 會出現「故事模式」入口；手動勾字批次不會出現故事入口。詳見 `docs/handoff/REPORT_GsatStoryS3_App端串接.md`。

**學測資料頁碼修正（2026-08-13 稍早）已 commit + 部署完成**（Firebase Hosting 與 GitHub Pages 皆已驗證），負責人對照 PDF 發現學測批次建立器第3、13、14、34、49、55、63頁字數異常，根因是原始資料檔在「Level 分級標題」頁面邊界頁碼卡住，已修正 `0resource/topsat.md`（123筆頁碼欄位 + 1筆污染定義）。詳見 `DECISIONS.md` 2026-08-13「修復學測資料來源檔頁碼欄位」條目。

**2026-08-13 這輪 bug 修復的背景**（新 session 開工前建議先掃過 `DECISIONS.md` 2026-08-13 的三筆條目）：負責人回報 Firebase 正式站點「會考/學測」按鈕會卡在載入中，排查過程中一併發現並修好了三個各自獨立的問題：
1. GitHub Pages 備援管道其實從未自動部署過（`workflow_dispatch` 手動觸發，文件寫的「push 自動部署」從未生效）。
2. `BrowserRouter` 缺少 `basename`，導致部署到 GitHub Pages 子路徑時整頁空白。
3. **真正的原始問題**：`AppContext.tsx` 的 `setSource()` 在使用者重複點選「目前已經選取」的來源分頁時，會讓 `isLoading` 卡在 `true` 永遠出不來（React 對相同值 state 更新的 bail out 行為 + 資料載入邏輯依賴 `[source]` 的 `useEffect` 不會重新觸發）。

三個都已修復、測試、部署到 Firebase Hosting 與 GitHub Pages，負責人已確認「這部分沒問題了」。

<details>
<summary>舊版下一步紀錄（已由上方取代，保留備查）</summary>

**負責人照 `REPORT_S3c_遷移至FirebaseHosting.md` 完成 Firebase Hosting 手動部署與登入重測**：
1. 安裝 Firebase CLI：`npm install -g firebase-tools`。
2. 在專案根目錄登入 Firebase：`firebase login`。
3. 在專案根目錄初始化 Hosting：`firebase init hosting`，選既有 Firebase 專案，public 目錄填 `exam-vocab-batcher/dist`，SPA rewrite 選 Yes。
4. 在 `exam-vocab-batcher/` 跑 `npm run build`，回專案根跑 `firebase deploy --only hosting`，記下新網址（通常是 `https://<project-id>.web.app`）。
5. 到 Firebase Console → Authentication → Settings → Authorized domains 確認新網域在清單內；完成後用 iPhone Safari、Android Chrome 在新網址重測登入（出現頭像、重新整理不消失、關分頁重開還在）。通過後回頭繼續 S3 驗收項 3~6。

（這份手動部署已完成，網址是 `https://gen-lang-client-0930375434.web.app`／`https://gen-lang-client-0930375434.firebaseapp.com`；登入仍失敗，才有上方 S3e 這片。）

</details>

## ⏳ 等你決定

- 專案原有的 `.github/copilot-instructions.md`（GitHub Copilot 執行層指示）要保留多久？何時可以淘汰？
- Firebase Hosting 部署穩定運作一段時間後，是否要正式移除 GitHub Pages 備援管道（目前計畫保留為手動觸發的備援，不會自動刪除）？

---

## ✅ 已完成（最近在前，依 git log 回填）

- 2026-08-13　**學測 Minecraft 故事模式切片3「App 端串接」已完成待實機驗收**：頁碼快速建立的學測批次新增 `sourcePage` 標籤，批次 Hub 只在有對應故事資料時顯示「故事模式」，新增 `/batch/:id/story` 故事頁，可閱讀英文/中文對照，英文目標字加粗、中文括號英文可點發音，故事 JSON 已複製到 `exam-vocab-batcher/public/data/stories.gsat.json`，PWA 快取規則已涵蓋故事資料。`npm.cmd run lint`、`npm.cmd run build`、`npm.cmd run test:e2e`（13 passed）通過。詳見 `REPORT_GsatStoryS3_App端串接.md`。
- 2026-08-13　**學測 Minecraft 故事模式切片2b「剩餘75頁故事重做」規劃層獨立核對後確認通過**：規劃層沒有只看報告文字，自己重寫一份 Python 驗證腳本重算句型骨架重複率（結果一致：576句0重複）、逐頁比對 `wordList` 與正式 vocab 資料（完全一致）、抽查報告未主動附上的第14/52/64頁（內容自然、用字正確）。發現報告漏報一項偏離：179句（約31%）超過 BRIEF 訂的「每句最多3個單字」上限，最多一句塞5字；已告知負責人並附具體例句，負責人選擇接受現狀不需重做。切片2b正式過關，`output/story/gsat/stories.gsat.json`（80頁完整版）備妥待切片3串接。詳見 `DECISIONS.md` 2026-08-13「切片2b 重做通過但密度超出上限」條目、`docs/handoff/REPORT_GsatStoryS2b_剩餘75頁故事重做.md`。
- 2026-08-13　**學測 Minecraft 故事模式切片2「剩餘75頁內容生成」規劃層核對後判定不合格、退回重做**：執行層（Codex）回報「已完成，QA 75/75、80/80 全過」，但規劃層核對 REPORT 與實際產出的 `output/story/gsat/stories_s2_剩餘75頁.json` 後發現，執行層並未逐頁手寫故事，而是寫了 `generate_stories_s2.mjs` 腳本，用固定10句英文模板＋1句中文模板機械套字（例如所有頁都出現「Alex found the glowing word "X" on a Minecraft sign」這類空殼句型），完全不是「整頁單字寫成連貫故事」的原始需求；QA 腳本只檢查單字有沒有出現、括號格式對不對，這種模板生成法能輕鬆通過，但敘事品質等於零，REPORT 也未揭露這個做法。**已否決此次產出**，詳見 `DECISIONS.md` 2026-08-13「學測故事模式切片2模板化生成不合格」條目，準備重開更嚴謹的 BRIEF。
- 2026-08-13　**修復學測資料來源檔頁碼欄位在 Level 分級標題邊界卡住的錯誤（尚未 commit）**：負責人對照 PDF 發現批次建立器第3、13、14、34、49、55、63頁字數異常（有的破40字，有的只剩1字），且只顯示75頁（應為80頁）。規劃層寫腳本統計每頁字數，找出6組成對邊界（3/4、13/14、34/35、49/50、55/56、63/64頁）都有「後一頁整頁消失、字全被標成前一頁」的現象，追查到根因在最上游資料檔 `0resource/學測高頻率單字表_含頁碼.md` 本身，遇到「Level.N」分級標題列時頁碼會卡住不跳號，不是本專案 pipeline 程式的 bug。單字總數 1640 筆完全正確、內容品質不受影響，純粹頁碼欄位標錯。已對照 PDF 逐一核對修正 `0resource/topsat.md`（123筆頁碼 + 1筆被污染的 `investigation` 定義）、重跑 pipeline、覆蓋 `vocab.gsat.cleaned.json`，`pytest` 63 passed、`npm run build` 通過，瀏覽器實測批次建立器 80 頁全部恢復正常（17~21字）。詳見 `DECISIONS.md` 2026-08-13 條目。**等負責人確認後才 commit 並部署。**
- 2026-08-13　**修復「重複點選同一來源」導致 App 永久卡在載入中（commit `0079a73`）**：負責人回報 Firebase 正式站點會考/學測按鈕卡住，規劃層多輪排查（清快取、無痕視窗、多瀏覽器、多裝置、VPN）皆無法重現；負責人提供精確重現步驟（點選「目前已選取」的來源分頁）後，規劃層在 `AppContext.tsx` 的 `setSource()` 找到根因：`nextSource === source` 時 React state 更新 bail out，資料載入 `useEffect` 不會重新觸發，`isLoading` 永遠卡 `true`。修法：`setSource()` 開頭檢查相同來源直接 `return`。已本機驗證、部署到 Firebase Hosting 與 GitHub Pages，負責人確認修復。詳見 `DECISIONS.md` 2026-08-13「真正根因」條目。
- 2026-08-13　**修復 GitHub Pages 備援管道從未自動部署 + `BrowserRouter` 缺少 `basename`（commit `e650002`、`7ca73b9`）**：排查上述問題過程中發現 GitHub Pages 備援網址停留在 M3-S2 版本超過一週——`deploy.yml` 只有手動觸發，文件寫的「push 自動部署」從未生效；補上 `on: push` 後，又發現部署後整頁空白，追查是 `BrowserRouter` 沒設定 `basename`，在 GitHub Pages 子路徑 `/vocabbatcher/` 下所有路由對不上。兩個都已修復並重新部署驗證正常。詳見 `DECISIONS.md` 2026-08-13 條目。
- 2026-08-04　**修復 PWA 快取策略導致部署後單字資料看不到更新（commit `3b19866`）**：單字資料 JSON 的 Workbox 快取策略從 `CacheFirst` 改為 `StaleWhileRevalidate`，並涵蓋會考/學測兩份資料檔（原本規則只匹配會考）；`firebase.json` 新增 `sw.js`/`registerSW.js`/`manifest.webmanifest` 的 `no-cache` header。詳見 `DECISIONS.md` 2026-08-04 條目。
- 2026-08-04　**補齊 `USER_MANUAL.md`、`DEVELOPER_LOG.md` 至 M5（commit `a44dad4`）**：兩份成果文件原本內容停留在 M2，新增涵蓋會考/學測來源切換、Google 登入、四題型練習測驗、成績歷史、單字統計、錯題複習等章節（USER_MANUAL）與 Firebase Auth/Firestore 架構、來源隔離設計、學測資料管線、已知坑整理（DEVELOPER_LOG）。`AGENTS.md`「成果文件交付閘」補齊至 M5。
- 2026-08-04　**M4「品質收斂」與 M5「學測單字庫」全部驗收通過**：負責人依合併驗收清單完整操作過一輪——首頁會考/學測切換、學測批次建立/翻牌/拼字題只出學測字、切換來源後批次歷史不互相混淆、重複批次提示、搜尋空狀態、0 字批次阻擋、1231 字清單捲動、成績歷史與單字統計依來源分開顯示且互不污染、全站頁面巡查無白屏、README 可讀、手機測試皆通過。**M1~M5 全部里程碑正式完成。**
- 2026-08-04　**學測資料改用新來源整份重轉，品質達 100% 完整率，已 commit**（commit `d0cbac1`、`dcc2060`）：改用負責人提供的 `0resource/學測高頻率單字表_含頁碼.md`（外部工具產出，經核對品質優於 Tesseract 版）取代 M5-S1b 產物；`topsat.md` 改成六欄明確格式，`topsat_md.py` 同步改寫不再依賴章節標題狀態。規劃層直接讀 PDF 逐筆核對：補回 4 筆表格誤併的字、補齊 75 筆源頭空白、寫結構/內容雙層異常掃描腳本抓出並修正多組「相鄰列吞併」殘留（共約 100 筆修正）。全程未使用自動 OCR。修正後：詞性/中文定義完整率 100%、低信心 0、`pytest` 63 passed。詳見 `DECISIONS.md` 2026-08-04「學測資料改用新來源徹底重轉」條目。**這批改動還在工作目錄未 commit，待負責人抽查確認後才提交。**
- 2026-08-04　**M5-S2「App 端會考/學測來源切換」已實作待驗收**：首頁新增「會考」／「學測」來源切換，`AppContext` 依來源載入 `vocab.cleaned.json` 或 `vocab.gsat.cleaned.json`；批次建立器、批次歷史、翻牌卡、練習測驗、成績歷史、單字統計都依目前來源運作。批次會記住建立來源，舊批次預設視為會考；考試成績新增 `source`，`wordStats` 文件 ID 改為 `{source}__{word}`，避免共同單字污染錯誤率。`npm.cmd run lint`、`npm.cmd run build`、`npm.cmd run test:e2e`（11 passed）通過。詳見 `REPORT_M5S2_App端來源切換.md`
- 2026-08-03　**規劃層人工補齊學測資料剩餘 15 筆缺值/OCR 殘留**：直接讀取 `TopAcademy 學測高頻率單字表.pdf` 對應頁碼核對正確詞性與中文定義，修正 `0resource/topsat.md` 的 `attach`、`bullying`、`evaluate`、`impress`、`landmark`、`layer`、`splash`、`terrify`（缺詞性）、`fiber`、`glory`、`humidity`（缺中文定義），以及順帶發現、經負責人確認一併修正的 `bound`、`landscape`、`spin`、`spray`（OCR 殘留雜訊）共 15 筆；重跑 pipeline 後詞性/中文定義完整率皆達 100%、低信心 0。`python -m pytest tests/` 66 passed。已 commit 並 push 到 `origin main`。
- 2026-08-03　**M5-S1b「學測資料 OCR 校正」已完成待抽查**：新增可重複執行腳本 `src/pdf_parser/tools/topsat_transcribe.py`，嘗試 PaddleOCR（安裝與模型下載成功，但 Windows CPU 推論固定失敗）後依 BRIEF 備援條件改用 Tesseract 300 DPI 裁切字義 cell；重新產出 `0resource/topsat.md`、`output/gsat/vocab.raw.json`、`vocab.cleaned.json`、`vocab.qa_report.json`，並覆蓋 `exam-vocab-batcher/public/data/vocab.gsat.cleaned.json`。QA 改善：詞性完整率 94.0%→99.5%（缺詞性 98→8）、中文定義完整率 98.7%→99.8%（缺定義 22→3）、低信心 1→0；`splendor`、`cruelly`、`refer`、`suffer`、`unique` 等抽樣錯誤已修正。`python -m pytest tests/` 66 passed。詳見 `REPORT_M5S1b_學測資料OCR校正.md`
- 2026-08-03　**M5-S1 資料抽查發現 OCR 錯字，開 M5-S1b 修正**：負責人抽查 `output/gsat/vocab.cleaned.json` 發現中文定義有 OCR 誤判（`splendor`→「RE 5」、`cruelly`→「殘酪地」等）；規劃層查詢後改用 PaddleOCR（繁體中文模型，準確率優於原本用的 Tesseract）＋提高渲染 DPI 至 300 以上，並要求轉錄流程改存成可重複執行腳本，已開 `BRIEF_M5S1b_學測資料OCR校正.md`，待執行。
- 2026-08-03　**M5-S1「學測資料管線」已實作待資料抽查**：新增 `0resource/topsat.md`，以 PDF 表格座標搭配 OCR 轉錄 `TopAcademy 學測高頻率單字表.pdf`，共解析 1640 筆；`VocabEntry`/`CleanedEntry` 新增 `level` 欄位，`topsat_md.py` 可解析學測 Markdown；產出 `output/gsat/vocab.raw.json`、`vocab.cleaned.json`、`vocab.qa_report.json`，並複製到 `exam-vocab-batcher/public/data/vocab.gsat.cleaned.json`。QA：詞性完整率 94.0%、中文定義完整率 98.7%、低信心 1 筆；因中文定義是 OCR 轉錄，需負責人抽查後才開 M5-S2。`python -m pytest tests/` 66 passed。詳見 `REPORT_M5S1_學測資料管線.md`
- 2026-08-03　**M4-S2~S4「品質收斂收尾」已實作待驗收**：批次 Hub 移除「錄音播放」假格子，保留翻牌學習/練習測驗/學習統計三格；練習測驗會導向 `/exam` 並帶入該批次頁碼範圍，學習統計導向 `/stats`；批次建立器新增重複批次確認提示；確認 0 字建立阻止與空搜尋狀態仍存在；新增 `e2e/m4s2-s4.spec.ts` smoke test，4 passed，1231 筆清單捲動量測 329ms，未加虛擬化；重寫根目錄 `README.md`。`npm.cmd run lint`、`npm.cmd run build` 通過。詳見 `REPORT_M4S2-S4_品質收斂收尾.md`
- 2026-08-03　**M4-S1「拼字填空題型」驗收通過**：混合模式考試中拼字題正確出現、大小寫與前後空白不影響判分、答錯正確顯示正解，結果頁/統計頁對錯計入正常，iPhone/Android 皆正常。
- 2026-08-03　**M4-S1「拼字填空題型」已實作待驗收**：`QuestionType` 新增 `spelling`，混合模式與錯題複習卷會隨機抽到拼字題；拼字題顯示中文意思、讓使用者輸入英文單字，送出後由 `isSpellingCorrect()` 統一判分（大小寫不敏感、去頭尾空白），並顯示答對/拼錯與正確拼法。為維持 TypeScript 與畫面顯示相容，結果頁與成績歷史補上「拼字」題型標籤，未改成績儲存與統計邏輯；此相容修正已記錄在 `DECISIONS.md`。`npm.cmd run lint`、`npm.cmd run build` 通過。詳見 `REPORT_M4S1_拼字填空題型.md`
- 2026-08-03　**UI/UX 修正切片（UIUX1~UIUX3）全部驗收通過**：首頁動線改為單一主 CTA、全站對比度修正、單字庫載入失敗提示、登入狀態全頁一致、自訂刪除確認、考試對錯圖示、頁碼範圍驗證、翻牌進度保存（UIUX1）；批次建立器加入頁次篩選（UIUX2）；修正 `vocab.cleaned.json` 頁碼固定 2 頁偏移（PDF 內部頁碼→課本印刷頁碼 1~60）並把批次建立器改為「一頁一按鈕、按下即建立批次」（UIUX3）。過程中導入 Playwright 作為執行層收工前的自我驗證工具，並新增 `deploy.ps1` 部署腳本。頁碼偏移修正的背景與影響範圍記錄在 `DECISIONS.md` 2026-08-03 條目。
- 2026-08-03　**UIUX3「頁碼修正與單頁建立批次」已實作待驗收**：`vocab.cleaned.json` 的 `source_page` 已從 PDF 內部頁碼 3~62 修正為課本印刷頁碼 1~60，`top2025_md.py` 主力 parser 新增固定偏移避免未來重產又錯位；批次建立器改為一頁一按鈕，點頁碼即可建立該頁批次並進入批次頁；進階搜尋/詞性/頻率手動選字仍保留。`python -m pytest tests\test_top2025_md.py` 15 passed，`npm.cmd run lint`、`npm.cmd run build` 通過，`npm.cmd run test:e2e` 6 passed（含手機尺寸截圖）。詳見 `REPORT_UIUX3_頁碼修正與單頁建立批次.md`
- 2026-08-03　**UIUX2「頁次篩選與自動化驗證」已實作待驗收**：`BatchBuilderPage` 新增最優先的頁次範圍篩選（預設全書 3-62 頁，縮小範圍後「顯示 N 筆」同步更新），頻率/詞性/搜尋保留為進階篩選；新增 `@playwright/test`、`playwright.config.ts`、`e2e/uiux2.spec.ts` 與 6 張驗證截圖。Playwright 4 項測試全通過，`npm run lint`、`npm run build` 通過。詳見 `REPORT_UIUX2_頁次篩選與自動化驗證.md`
- 2026-08-03　**UIUX1「首頁動線與可用性修正」已實作待驗收**：首頁改為單一主 CTA、成績/統計降為次要入口；有意義的淺灰文字提高對比；單字庫載入失敗有重試畫面；主要頁面 Header 統一顯示登入狀態；批次刪除改自訂確認彈窗；考試作答加勾叉圖示；考試頁碼範圍即時提示；翻牌上一張會保存進度。`npm run lint`、`npm run build` 通過。詳見 `REPORT_UIUX1_首頁動線與可用性修正.md`
- 2026-08-03　**M3「考試與追蹤」全部完成（S1~S5 皆驗收通過）**：發音按鈕全面化、Google 登入雲端同步、頁數範圍選擇題/聽力考試、成績與錯誤率統計、錯題複習卷。過程中經歷兩段插曲：(1) 登入問題橫跨 S3b~S3f 四輪診斷，最終根因是 `HashRouter` 與 Firebase 登入網址片段衝突、PWA Service Worker 攔截登入保留路徑，兩者並存才穩定；(2) S4 驗收時發現 Firestore 安全規則預設鎖死一切讀寫，導致成績/統計資料從未真正儲存過，已修正為登入使用者僅能讀寫自己的資料。詳見 `DECISIONS.md` 完整記錄。
- 2026-08-02　**M3-S5「錯題複習卷」已實作待驗收**：`WordStatsPage` 新增「錯題複習」按鈕，依 `wordStats` 中錯誤率最高且曾答錯的單字產生考卷並導向既有 `/exam/run` 作答流程；`npm run lint`、`npm run build` 通過。詳見 `REPORT_S5_錯題複習卷.md`
- 2026-08-02　**M3-S4「成績統計」驗收通過**：登入考試後成績歷史、單字統計皆正確顯示。過程中發現 Firestore 安全規則預設 `allow read, write: if false`（鎖死一切讀寫），導致 S3、S4 的成績/統計資料其實從未真正儲存過，直到 S4 新頁面第一次讀取才現形；已修正規則為「登入使用者只能讀寫自己 `users/{uid}` 底下資料」，存進 `firestore.rules` 並在 `firebase.json` 註冊，詳見 `DECISIONS.md` 2026-08-02 條目。
- 2026-08-01　**M3-S4「成績統計」已實作待驗收**：考完後登入使用者會同步寫入 `examResults` 與 `wordStats`，新增「成績歷史」與「單字統計」頁，首頁已加入兩個入口；`npm run lint`、`npm run build` 通過。詳見 `REPORT_S4_成績統計.md`
- 2026-08-01　**M3-S3「考試引擎」完整驗收通過**：混合模式中英交錯出題、聽力題可重播、未登入訪客模式提示、已登入成績寫入、iPhone/iPad/Android 三平台皆正常。已開 `BRIEF_S4_成績統計.md`。
- 2026-08-01　**登入問題（S3b~S3f）驗收通過**：桌機瀏覽器、iPhone Safari、Android Chrome 三平台皆能正常登入（跳出 Google 帳號選擇畫面、完成登入出現頭像、重新整理與關分頁重開皆維持登入狀態）。前後歷經四輪診斷：S3b 排除「S3 程式碼回歸」假設、S3c 遷移到 Firebase Hosting（未解決但保留為合理長期部署）、S3e 修復 `HashRouter` 與 Firebase 登入網址片段衝突、S3f 修復 PWA Service Worker 攔截 Firebase 登入保留路徑——最終是 S3e + S3f 兩個根因同時修復才穩定。完整根因記錄見 `DECISIONS.md` 2026-07-31 兩筆條目。
- 2026-07-31　S3f PWA 排除 Firebase 登入保留路徑**已實作待部署驗收**：`vite.config.ts` 的 Workbox 設定新增 `navigateFallbackDenylist`，排除 `/__/auth/**`、`/__/firebase/**`，讓 Service Worker 不再把 Firebase 登入處理頁改回 App 的 `index.html`；PWA 離線快取未關閉。`npm run lint`、`npm run build` 通過，`dist/sw.js` 已確認生成 `denylist`。詳見 `REPORT_S3f_PWA排除登入路徑.md`
- 2026-07-31　S3e 登入真正根因修復**已實作待部署驗收**：`src/App.tsx` 從 `HashRouter` 改為 `BrowserRouter`，避免 Firebase Auth redirect 使用的 URL `#` 片段被 React Router 誤判成 App 路由；`src/` 內無 `#/` 或 `location.hash` 殘留；`npm run lint`、`npm run build` 通過，本機 preview `/` 與 `/exam` 皆 200。詳見 `REPORT_S3e_改用BrowserRouter.md`
- 2026-07-31　M3-S3 考試引擎**實作完成**（commit `1752fd4`）：出題引擎 `src/services/exam.ts`、考試設定/作答/結果三頁面；`npm run lint`、`npm run build` 通過。驗收進行中：測試項 1（頁數範圍+中英交錯出題）、2（聽力題可重播）已通過；測試項 4（已登入狀態）卡在登入回歸問題，見下方「進行中」
- 2026-07-31　M3-S2 Google 登入 + Firebase 雲端基礎**驗收通過**：iPhone、iPad、Android 三平台實機測試皆正常（Google 導向登入/登出、同帳號跨裝置顯示同一名字）；中途發現手機瀏覽器對 `signInWithPopup` 支援不佳（點擊後畫面閃退），改用 `signInWithRedirect` 修復（見 `DECISIONS.md` 2026-07-31 條目）
- 2026-07-30　M3-S1 發音按鈕全面化**驗收通過**：iPhone Safari、iPad Safari、Android Chrome 三平台實機測試皆正常（喇叭圖示顯示、發音正確、不誤觸勾選）
- 2026-07-30　提前建立正式環境：新增 `.github/workflows/deploy.yml`，push 到 main 自動 build 並部署到 GitHub Pages（`https://hsiaochiang.github.io/vocabbatcher/`），取代本機區網測試（本機 LAN 對 Android/iOS 連線異常，改走正式網址驗收）
- 2026-07-06　M3-S1 發音按鈕全面化已實作：新增可重用 `SpeakButton`，單字列表與翻牌卡英文單字可點喇叭發音；`npm run lint`、`npm run build` 通過
- 2026-07-06　M3 重定義為「考試與追蹤」並完成規劃：使用者回饋 4 項期待拆成 R8~R12、拍板雲端帳號(Google 登入+Firebase)與頁數範圍出題、產出 `STAGE_3_PLAN.md` + `BRIEF_S1_發音按鈕.md`
- 2026-07-06　套入兩層開發模式：補齊 AGENTS/WORKFLOW/REQUIREMENTS/ROADMAP/PROGRESS/DECISIONS，決定逐步取代舊 OpenSpec/Copilot 流程
- 2026-05-31　撰寫 `USER_MANUAL.md`、`DEVELOPER_LOG.md` + 7 份 ADR
- 2026-05-31　UI/UX 修正（清除/全選按鈕、篩選對應、Hub 卡片辨識、觸控面積）
- 2026-05-31　B-1 完成 — ExamVocabBatcher Web App（M2 核心功能）
- 2026-05-31　v2 功能補完（PDF 頁碼 + IPA 音標 + output 取消追蹤）
- 2026-05-31　功能補完 A-1~C-1（Markdown 解析器 + 品質修正）
- 2026-02-28　pdf-parser 結案文件與規範同步（sync & archive 決策）
- 2026-02-28　完成 pdf-parser 與工作流文件整合
- 2026-02-28　建立 Roadmap 治理規範 + 里程碑驗收機制
- 2026-02-28　初始專案建置（Copilot workspace + Stitch UI）

## 🔧 進行中

（無，M1~M5 全部完成，等待下一輪需求）

## 📋 待辦

- [x] M3-S1：發音按鈕全面化（已驗收通過，iPhone/iPad/Android 皆正常）
- [x] 部署至 GitHub Pages（提前於 S1 驗收階段完成，見 `DECISIONS.md` 2026-07-30 條目）
- [x] M3-S2：Google 登入 + Firebase 雲端基礎（已驗收通過，iPhone/iPad/Android 皆正常）
- [x] **登入問題徹底修復**（S3b~S3f，2026-08-01 三平台驗收通過）
- [x] M3-S3：考試引擎（2026-08-01 完整驗收通過）
- [x] M3-S4：成績紀錄與累積錯誤率統計（2026-08-02 驗收通過，含 Firestore 安全規則修復）
- [x] M3-S5：錯題複習卷（2026-08-03 驗收通過）
- [x] **M3「考試與追蹤」正式結案**（2026-08-03，五片全部驗收通過）
- [x] **M4：拼字填空、批次歷史/續作、品質收斂**（2026-08-04 全部驗收通過）
- [x] **M5：學測單字庫（資料管線 + App 端會考/學測來源切換）**（2026-08-04 全部驗收通過）
