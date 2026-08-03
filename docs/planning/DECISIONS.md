# DECISIONS.md — 變更與決策日誌

> 給 AI：**任何偏離原始需求(REQUIREMENTS.md)的改動，都要在這裡記一筆**，並同步更新 REQUIREMENTS.md。
> 給負責人：隔週回來時，看這裡就知道「為什麼系統跟我當初想的不一樣」。
> 角色綁定見 `WORKFLOW.md` §0。
>
> **本專案 2026-07-06 前的歷史決策記錄在 `docs/decision-log.md` 與 `docs/decisions/`（OpenSpec 舊流程），
> 本檔只記錄 2026-07-06 起、兩層 vibe coding 流程下的新決策，不重複搬移舊紀錄。**

---

## 2026-08-04　M5-S2 App 載入時忽略非正整數頁碼

- **狀態：** 已採納
- **背景：** M5-S2 串接學測資料時，發現目前 `vocab.gsat.cleaned.json` 仍有少數單字的 `source_page` 是 `0`。如果前端照單全收，批次建立器與頁碼考試會出現「第 0 頁」，對拿紙本教材操作的使用者很困惑。
- **改動：** `AppContext` 在載入單字資料時只保留大於 0 的整數頁碼；資料檔本身不改。這些單字仍會存在於單字庫、可用搜尋與手動勾選加入批次，但不會出現在「點頁碼建立批次」或「依頁碼出考卷」的頁碼範圍裡，直到未來資料源補回正確頁碼。
- **影響的原始需求：** `REQUIREMENTS.md` R13 學測單字庫；頁碼操作以可對照教材的有效印刷頁碼為準，不新增第 0 頁這種教材上不存在的操作入口。
- **負責人是否同意：** 待確認（依 M5-S2 驗收風險先行處理並在本次報告中回報）

## 2026-08-03　規劃層直接人工修正學測資料剩餘 15 筆缺值/殘留錯誤（未走 BRIEF/執行層流程）

- **狀態：** 已採納
- **背景：** M5-S1b 收工後仍有 8 筆缺詞性（`attach`、`bullying`、`evaluate`、`impress`、`landmark`、`layer`、`splash`、`terrify`）、3 筆缺中文定義（`fiber`、`glory`、`humidity`）。負責人要求手動修正這份清單，規劃層判斷這是範圍明確、風險低的小幅資料修正，直接讀取 `0resource/TopAcademy 學測高頻率單字表.pdf` 對應頁碼（比對 `source_page` 印刷頁碼＋2 的固定偏移換算出實際 PDF 頁）核對正確內容，不另開 BRIEF 走執行層流程。核對這 11 筆時，順帶發現附近另有 4 筆殘留 OCR 雜訊（`bound`「界限;ERE 5 SIAL」、`landscape`「風景 5 美化景觀」、`spin`／`spray` 詞性欄殘留 `巴.]` 碎片），回報負責人後負責人要求一併修正。
- **改動：** 直接編輯 `0resource/topsat.md` 這 15 筆的詞性／中文定義欄位（依 PDF 原文核對，例如 `attach`→`[v.] 附上;附加`、`bound`→`[adj.] 註定的;受約束的;[n.] 界限;[v.] 跳躍;彈回`，其餘同理），重跑 `python -m src.pdf_parser --input 0resource/topsat.md --outdir output/gsat --rule topsat` 重新產出 `output/gsat/vocab.raw.json`／`vocab.cleaned.json`／`vocab.qa_report.json`，並覆蓋 `exam-vocab-batcher/public/data/vocab.gsat.cleaned.json`。修正後 QA：詞性完整率 99.5%→100%、中文定義完整率 99.8%→100%、低信心 0。`python -m pytest tests/` 66 passed。這 15 筆之外的資料未逐一巡查，理論上仍可能有零星未發現的 OCR 殘留，若日後抽查再發現可比照這次做法個別修正。
- **影響的原始需求：** `REQUIREMENTS.md` R13 學測單字庫資料管線；不影響會考資料或 App 前端邏輯。
- **負責人是否同意：** 是（負責人直接要求修正這份清單，含追加的 4 筆）

## 2026-08-03　M5-S1b OCR 方案改用 Tesseract 300 DPI 優化版（PaddleOCR 推論失敗）

- **狀態：** 已採納
- **背景：** M5-S1b BRIEF 原定優先改用 PaddleOCR `lang='chinese_cht'`／PP-OCRv5。執行層已成功安裝 `paddleocr 3.7.0` 與 `paddlepaddle 3.3.1`，且模型可下載到使用者快取；但在 Windows CPU 推論時固定拋出 PaddlePaddle oneDNN runtime 錯誤：`ConvertPirAttribute2RuntimeAttribute not support [pir::ArrayAttribute<pir::DoubleAttribute>]`，關閉 MKL-DNN / PIR 相關旗標後仍失敗，無法可靠產出資料。
- **改動：** 本次資料改用可重複執行的 `src/pdf_parser/tools/topsat_transcribe.py` 產出：單字、Level、頁碼、出現次數仍取 PDF 表格層；中文定義改以 Tesseract `eng+chi_tra` 在 300 DPI 裁切字義 cell 後辨識，並加入少量已目視確認的人工校正表（例如 `splendor`、`cruelly`、`refer`、`suffer`）。腳本保留 `--engine paddleocr` 入口，待未來 PaddleOCR / PaddlePaddle 在本機環境可正常推論時可重試。
- **影響的原始需求：** R13 學測單字庫資料管線仍維持「大幅改善中文定義辨識率、產出可抽查 JSON」的驗收目標；但本版不宣稱是 PaddleOCR 產物。M5-S2 仍須等負責人抽查新版資料通過後才可開。
- **負責人是否同意：** 待確認（依 M5-S1b BRIEF 的備援條件先行實作並回報）

## 2026-08-03　新增 M5：學測高頻率單字庫（獨立於會考）

- **狀態：** 已採納
- **背景：** 負責人取得 TopAcademy 官方「學測高頻率單字表」PDF，希望 App 除了現有的會考單字庫之外，也能練學測單字。與負責人確認範圍：兩份單字庫要完全獨立（各自的搜尋/篩選/批次/頁碼範圍/考試出題互不混用，不合併成同一個單字庫），學測資料保留 `level`（第三/四/五/六級）欄位、不保留個別出現年份標記。
- **改動：** 新增 `REQUIREMENTS.md` R13；`docs/planning/ROADMAP.md` 新增 M5 里程碑；規劃拆成兩片：M5-S1（學測 PDF → 乾淨 JSON 資料管線，先驗證資料正確性）、M5-S2（App 端會考/學測來源切換）。拆兩片的原因：學測 PDF 排版比會考版複雜（多了 Level 分級），比照 UIUX3 頁碼固定偏移 2 頁的教訓——資料錯誤如果跟 App 功能一起做完才驗收，會很晚才被發現、回頭修的成本更高，這次先讓資料管線單獨過一輪負責人驗收。
- **影響的原始需求：** 新增 `REQUIREMENTS.md` R13；不影響既有 R1~R12（會考單字庫的既有流程不變）。
- **負責人是否同意：** 是

## 2026-08-03　負責人拍板：不做批次 TTS 循環播放，批次統計接回既有全域功能

- **狀態：** 已採納
- **背景：** M4 品質收斂檢查批次 Hub 時，原本的「錄音播放」「練習測驗」「學習統計」仍是即將推出格子。負責人已拍板：批次 TTS 循環播放不是 MVP 必要功能，翻牌卡點擊發音與考試聽力題已滿足核心聽力需求；練習測驗與學習統計不重做批次專屬資料流，接回既有全域考試與統計即可。
- **改動：** 批次 Hub 移除「錄音播放」格；「練習測驗」導向 `/exam` 並帶入該批次單字頁碼範圍作為預設值；「學習統計」導向 `/stats`。`REQUIREMENTS.md` R4 標記正式移除，R7 標記由首頁批次歷史/續作與 R11 統計功能滿足。
- **影響的原始需求：** R4（原本要做批次 TTS 循環播放 → 現在正式移除）；R7（原本批次統計 → 現在由 R11 的全域成績與錯誤率統計承接）。
- **負責人是否同意：** 是（依 `BRIEF_M4S2-S4_品質收斂收尾.md` 執行）

## 2026-08-03　M4-S1 相容修正：結果頁與歷史頁補上拼字題型標籤

- **狀態：** 已採納
- **背景：** M4-S1 BRIEF 原本要求不改 `ExamResultPage.tsx`、`WordStatsPage.tsx`，因為成績統計只依 `ExamQuestionRecord.correct` 判斷，不需要改資料模型。但 `QuestionType` 新增 `spelling` 後，`ExamResultPage.tsx` 與 `ExamHistoryPage.tsx` 的 `TYPE_LABEL: Record<ExamQuestionRecord['type'], string>` 必須補齊 `spelling`，否則 TypeScript build 會失敗；若只放寬型別不補文字，結果頁/歷史頁會出現無法辨識的題型標示。
- **改動：** 僅在 `ExamResultPage.tsx` 與 `ExamHistoryPage.tsx` 的題型顯示文字補上 `spelling: '拼字'`；沒有改成績儲存、統計計算、Firestore 寫入或頁面流程。
- **影響的原始需求：** R6（四題型練習）新增拼字填空題型後，結果清單與成績歷史能正確顯示該題型名稱；R11（成績與錯誤率統計）的資料計算方式維持不變。
- **負責人是否同意：** 是（依 M4-S1 型別相容與驗收需求執行）

## 2026-08-03　修正：source_page 從 PDF 內部頁碼改為課本印刷頁碼

- **狀態：** 已採納
- **背景：** UIUX2 驗收前核對課本時，發現 App 顯示的頁碼與課本印刷頁碼固定差 2 頁；根因是 `top2025.md` 第 4 欄保留的是 PDF 內部頁碼，PDF 第 3 頁才是課本印刷第 1 頁。這會讓「依頁碼找單字」與「依頁碼出考卷」畫面看起來可用，但使用者拿實體課本對照時會翻錯頁。
- **改動：** `exam-vocab-batcher/public/data/vocab.cleaned.json` 與 `output/vocab.cleaned.json` 的 `source_page` 全部減 2，修正後全書頁碼為 1~60 且沒有 0 或負數；`src/pdf_parser/rules/top2025_md.py` 新增 `PRINTED_PAGE_OFFSET = 2`，未來重新從 Markdown 產資料時會直接輸出課本印刷頁碼；批次建立器同步改為「點單一頁碼按鈕就建立該頁批次」。
- **影響的原始需求：** R2（搜尋 / 篩選單字）與 R10（選定頁數範圍產生考卷）過去使用的是錯位 2 頁的頁碼標示；功能流程本身可用，但頁碼語意不準。本次修正後，App 顯示頁碼改以課本印刷頁碼為準。
- **負責人是否同意：** 是（依 `BRIEF_UIUX3_頁碼修正與單頁建立批次.md` 執行固定偏移快修）

## 2026-08-02　修復：Firestore 安全規則預設鎖死一切讀寫，導致成績/統計從未真正儲存

- **狀態：** 已採納
- **背景：** S4「成績歷史」「單字統計」上線後，負責人回報兩個頁面都沒有資料，即使已登入且重新考過。查 Firebase Console → Firestore → Rules，發現規則是 `allow read, write: if false;`——這是建立 Firestore 資料庫時的預設鎖死規則，從未被改成允許登入使用者讀寫自己的資料。往回推：S2、S3 驗收時「已登入考完一次不出現任何錯誤」之所以能通過，是因為 `ExamResultPage` 的得分/對錯清單是用考試當下的本機資料直接顯示，不需要從 Firestore 讀回來，寫入失敗只會在背景 console 出現錯誤（`.catch(console.error)`），畫面完全正常、負責人看不出來。也就是說，`examResults`、`wordStats` 從 S3 開始其實從來沒有真正寫進 Firestore 過，直到 S4 的兩個新頁面第一次「真的去讀」，才讓這個問題現形。
- **改動：** 把 Firestore 規則改為：登入使用者只能讀寫自己 `users/{uid}` 底下的文件與所有子集合（`examResults`、`wordStats`），其餘一律不開放。規則內容存進專案根目錄 `firestore.rules`，並在 `firebase.json` 加上 `"firestore": { "rules": "firestore.rules" }`，避免以後 `firebase deploy` 沒有把規則一併部署、或被 Console 手動改動又忘記同步回 repo。負責人已直接在 Firebase Console 貼上新規則並發布。
- **影響的原始需求：** R9（帳號同步）、R11（成績與錯誤率統計）過去的「已驗收通過」紀錄需要註記：**功能流程本身沒問題，但資料其實從未真正落地**，直到本次修復才是第一次「成績/統計真的會被儲存」。建議負責人之後重新用「成績歷史」「單字統計」頁面驗證一次舊有的登入/考試驗收項目，確保資料確實持久化。
- **負責人是否同意：** 是（負責人依規劃層提供的規則內容直接發布）

## 2026-07-31　登入問題第二根因確認：PWA Service Worker 攔截 Firebase 登入保留路徑

- **狀態：** 已採納
- **背景：** S3e 改用 `BrowserRouter` 後，iPhone 登入流程已有進展，但桌機／Android 仍不穩定。規劃層再次檢查正式站 `sw.js`，發現 Workbox 的 `NavigationRoute(createHandlerBoundToURL("index.html"))` 會攔截所有整頁導覽請求；Firebase Auth redirect 需要使用 `/__/auth/handler`、`/__/auth/iframe` 等保留路徑，但這些請求被瀏覽器端 Service Worker 攔截後回傳本 App 的 `index.html`，導致登入處理頁無法執行。這證實 `BRIEF_S3b` 當初列出的「PWA Service Worker 快取干擾」是登入問題的主要根因之一，與 HashRouter 衝突並存。
- **改動：** `exam-vocab-batcher/vite.config.ts` 的 `VitePWA.workbox` 新增 `navigateFallbackDenylist: [/^\/__\/auth\//, /^\/__\/firebase\//]`，讓 Firebase 保留路徑不被 SPA navigation fallback 攔截；PWA precache 與 `data/vocab.cleaned.json` 的離線快取維持不變。
- **影響的原始需求：** R9「使用者能以 Google 帳號登入/登出，跨裝置同步」恢復可驗收；R4「斷網可用」不應受影響，因為沒有關閉 PWA/Service Worker，只排除 Firebase 登入保留路徑。
- **負責人是否同意：** 是（依 S3f 修復 BRIEF 執行，待負責人部署後重新驗收）

## 2026-07-31　登入問題真正根因確認：HashRouter 與 Firebase 登入網址片段衝突（推翻前兩輪假設）

- **狀態：** 已採納
- **背景：** 規劃層直接用瀏覽器工具重現登入問題，在主控台看到本專案自己的 React Router 印出警告：`No routes matched location "/id=I0_...&_gfid=...&parent=...&pfname=&rpctoken=..."`。這證實登入失敗的真正原因是 `src/App.tsx` 使用的 `HashRouter`（用網址 `#` 片段記錄目前畫面）跟 Firebase Auth 內部用網址 `#` 片段傳遞登入流程狀態互相衝突，`signInWithRedirect()` 流程在還沒跳出 Google 帳號選擇畫面前就被自家路由系統打斷。這個衝突與部署平台（GitHub Pages／Firebase Hosting）、裝置（iPhone／Android／桌機）都無關，純粹是前端路由函式庫的選型問題。
- **改動：** 推翻 `BRIEF_S3b`「跨網域第三方儲存限制」與 `BRIEF_S3c`「遷移到 Firebase Hosting 可解決登入」兩輪假設——這兩輪的環境調整（保留下來，Firebase Hosting 遷移仍是合理的長期做法，只是不是本次登入問題的解方）沒有真正解決問題。真正修法見 `BRIEF_S3e_改用BrowserRouter.md`：把路由系統從 `HashRouter` 換成 `BrowserRouter`。
- **影響的原始需求：** R9「使用者能以 Google 帳號登入/登出，跨裝置同步」的驗收方式不變；`BRIEF_S3d_登入除錯面板.md`（原本要加除錯面板協助診斷）因根因已找到而不需要執行。
- **負責人是否同意：** 是（規劃層直接診斷確認，待執行與負責人重新驗收）

## 2026-07-31　登入架構修法定案：正式站遷移到 Firebase Hosting

- **狀態：** 已採納
- **背景：** S3 驗收時，iPhone Safari 與 Android Chrome 完成 Google 導向登入後，App 仍顯示「使用 Google 登入」，重新整理也沒有頭像。執行層診斷根因：正式站部署在 GitHub Pages project site (`hsiaochiang.github.io/vocabbatcher/`)，Firebase `authDomain` 用預設 `firebaseapp.com`，兩者不同網域，`signInWithRedirect()` 在封鎖第三方儲存的手機瀏覽器上讀不回登入結果（詳細診斷見 `REPORT_S3b_登入異常修復.md`）。
- **改動：** 負責人（考量非商業、個人家庭使用）拍板：正式站部署管道由 GitHub Pages 改為 Firebase Hosting（`*.web.app` / `*.firebaseapp.com` 網域，免費額度足夠家庭用量），讓 App 網域與 Firebase Auth helper 網域同源，`signInWithRedirect()` 不需再改寫即可正常運作。捨棄方案：改用 Google Identity Services 重寫登入流程（負責人評估對個人專案複雜度過高，不採用）。此決策的具體施工見 `BRIEF_S3c_遷移至FirebaseHosting.md`。
- **影響的原始需求：** R9「使用者能以 Google 帳號登入/登出，跨裝置同步」的驗收方式不變；但正式站網址會從 `hsiaochiang.github.io/vocabbatcher/` 變成 Firebase Hosting 網域，`ROADMAP.md`/`DECISIONS.md` 2026-07-30「提前建立 GitHub Pages 正式環境」條目的網址記錄需同步更新為新網址（待遷移完成後回填）。
- **負責人是否同意：** 是（2026-07-31 拍板採用 Firebase Hosting 方案）

## 2026-07-31　M3-S2 修復：Google 登入改用 signInWithRedirect（偏離 BRIEF 原定實作方式）

- **狀態：** 已採納
- **背景：** `BRIEF_S2_雲端帳號.md` 原始實作採 `signInWithPopup`（跳出視窗登入）。負責人於 iPhone、iPad、Android 三平台實測，點擊「使用 Google 登入」後畫面閃一下即消失、登入未完成——這是手機瀏覽器（iOS Safari、Android Chrome）普遍封鎖或立即關閉彈出視窗的已知限制。
- **改動：** `src/services/auth.ts` 的 `signInWithGoogle()` 改為 `signInWithRedirect`（整頁導向登入），新增 `completeRedirectSignIn()` 於頁面載入時接住導回結果並建立 `users/{uid}` 文件；`UserBadge.tsx` 新增登入失敗錯誤提示文字。修復後三平台重測皆成功。
- **影響的原始需求：** 不影響 R9 驗收標準本身（使用者能以 Google 帳號登入、跨裝置同步），僅實作方式從彈出視窗改為整頁導向；`BRIEF_S2_雲端帳號.md` 與 `STAGE_3_PLAN.md` 的「發音一律經 tts.ts」等跨切片一致性規則不受影響。往後 S3~S5 若涉及登入流程，一律沿用 `signInWithRedirect` 模式。
- **負責人是否同意：** 是（負責人回報成功後追認）

## 2026-07-30　提前執行 M4 部署項目：建立 GitHub Pages 正式環境

- **狀態：** 已採納
- **背景：** M3-S1「發音按鈕全面化」驗收時，負責人在本機 LAN（`vite --host` 開放區網 IP）測試，iPad Safari 與 Android Chrome 皆卡在「連線中」空白畫面（疑似 Windows 防火牆 Public 設定檔或路由器 AP 隔離導致連線被靜默丟棄）。負責人要求改用正式環境測試，因為正式上線本來就不應依賴負責人本機網路。
- **改動：** 新增 `.github/workflows/deploy.yml`，push 到 `main` 時自動 `npm run build` 並用官方 `actions/upload-pages-artifact` + `actions/deploy-pages` 部署到 GitHub Pages（`https://hsiaochiang.github.io/vocabbatcher/`）。此為 `ROADMAP.md` M4「部署至 GitHub Pages」項目的提前執行，非依原排序在 M3 全部完成後才做。
- **影響的原始需求：** 無新增/刪除需求條目；`ROADMAP.md` M4 的部署工作項目已提前完成，M4 階段屆時可跳過此項。後續 S2~S5、M4 其餘項目仍沿用同一 GitHub Pages 網址，不需另建部署管線。
- **負責人是否同意：** 是（負責人主動要求）

## 2026-07-06　使用者回饋功能定案：併入 M3，新增雲端帳號(推翻原排除項)

- **狀態：** 已採納
- **背景：** 負責人提供了關鍵使用者回饋的 4 項期待：(1) 每個單字旁有發音按鈕；(2) 選擇題考試，可設頁數範圍與題數，中→英/英→中交互出題；(3) 聽力考試(英文發音→選中文)，可設頁數範圍；(4) 每位使用者的每次考試成績、累積錯誤單字比率，並依錯誤率再出複習卷。
- **改動：** 三項決策(負責人 2026-07-06 拍板)：
  1. **「每位使用者」採雲端帳號同步**(Google 帳號登入，後端用 Firebase)——**推翻原始範圍「不做帳號系統/雲端同步」的排除項**。
  2. **考試出題範圍依頁數範圍**，跳脫 25 字批次限制；批次仍保留給聽錄音/翻牌學習。
  3. **新功能併入 M3 並重定義**為「考試與追蹤」；原 M3 的拼字填空題型與批次統計挪到 M4。
- **影響的原始需求：** 新增 R8~R12；刪除排除清單「不做帳號系統/雲端同步」;R6/R7 範圍調整(詳見 `REQUIREMENTS.md`)。技術評估：全功能純網頁(PWA)可達成，iPad Safari 與 Android Chrome 皆支援 Web Speech API，不需開發原生 App。
- **負責人是否同意：** 是

## 2026-07-06　套入兩層開發模式(初始化)

- **狀態：** 已採納
- **背景：** 專案原本由 OpenSpec + GitHub Copilot（含 WOS agent）驅動開發，文件散落在 `docs/roadmap.md`、`docs/decision-log.md`、`.github/copilot-instructions.md` 等處。負責人（Wilson）決定改用「兩層 vibe coding」流程（規劃層 = Cowork、執行層 = Codex CLI），逐步取代舊流程。
- **改動：** 在專案根補齊 `AGENTS.md`、`WORKFLOW.md`、`REQUIREMENTS.md`、`ROADMAP.md`、`PROGRESS.md`、`DECISIONS.md`。原有 `.github/copilot-instructions.md`（GitHub Copilot 專用指示）因已存在且內容完整，依非破壞性原則保留、不覆蓋，待負責人逐步淘汰舊流程時再決定去留。
- **影響的原始需求：** 無（純流程/工具變更，不影響產品功能需求）。
- **負責人是否同意：** 是

## 2026-07-06　待處理：使用者回饋新增功能需求

- **狀態：** 已結案(由上方「使用者回饋功能定案」決策取代)
- **背景：** 負責人提到「有關鍵使用者回饋，描述了對這個專案期待的功能」，需要完成這些功能，但尚未提供回饋的具體內容。
- **改動：** 尚未進行任何實作。待負責人提供回饋內容後，由規劃層拆解為新的 `REQUIREMENTS.md` 條目，評估併入 M3 或另開里程碑，再寫 `BRIEF` 交給執行層。
- **影響的原始需求：** 待評估（可能新增 R8 及以後的條目，或調整 M3 範圍，詳見 `ROADMAP.md`「重大相依與風險」）。
- **負責人是否同意：** 待確認

<!-- 新的決策往上加，保持最新在最上面 -->
