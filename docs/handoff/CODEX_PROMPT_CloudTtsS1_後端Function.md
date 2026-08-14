請讀 D:\program\vocabbatcher\AGENTS.md 了解本專案的協作規範，你是執行層。

接著讀 D:\program\vocabbatcher\docs\handoff\BRIEF_CloudTtsS1_後端Function.md，這是你這次要做的完整施工規格，照著做：

1. 開工先讀 D:\program\vocabbatcher\docs\planning\PROGRESS.md 恢復脈絡。
2. 工作目錄是專案根目錄 D:\program\vocabbatcher。**這片只新增根目錄下的 `functions/`，完全不碰 `exam-vocab-batcher/` 前端任何檔案。**
3. 重點任務：
   - `firebase init functions`（或手動建立等價結構）建立 TypeScript Firebase Functions 專案（Node 20），安裝 `firebase-functions`、`firebase-admin`、`@google-cloud/text-to-speech`。
   - 實作 `synthesizeSpeech` callable function（`firebase-functions/v2/https` 的 `onCall`）：輸入 `{ text: string, lang: 'en-US' | 'en-GB' }`，驗證 `lang` 只能是這兩個值、`text` 長度上限200字元，違反就用 `HttpsError('invalid-argument', ...)` 拋錯；用 `@google-cloud/text-to-speech` 的 `TextToSpeechClient` 合成語音（`audioEncoding: 'MP3'`），回傳 `{ audioBase64: string }`。不用手動管理 API 金鑰，靠 Cloud Function 預設服務帳號權限；如果實際部署後發現權限不夠（permission denied），可以自行到 IAM 頁面調整（負責人已確認專案是 Blaze 方案、已啟用 Cloud Text-to-Speech API），並在報告裡寫清楚做了什麼調整。
   - `firebase.json` 新增 `functions` 設定區塊（指向 `functions/`，`runtime: nodejs20`，predeploy 跑 TS build）。
   - `firebase deploy --only functions` 部署，然後**用可重現的方式實際驗證**：寫一支暫時性測試腳本呼叫已部署的 function，把回傳的 base64 存成 `.mp3` 確認是有效音檔（檔案大小非0、格式正確），至少測「正常情況」跟「至少一個錯誤情況（例如 lang 傳不合法值）」兩種情境，測試腳本留在專案裡方便規劃層之後重跑，並在報告裡說明怎麼重跑。
4. 邊界（不要碰）：不改 `exam-vocab-batcher/` 任何檔案（前端串接是切片2的事）；不做 Firestore 快取層（切片3的事，這片每次都直接打 API，用量很少不用擔心）；不改 `firestore.rules` 既有內容；**不把 functions 部署塞進現有 `deploy.ps1`**（那支腳本是前端專用，不要動它）；不用做多種音色選擇，固定一個合理預設音色即可。
5. 若有偏離本 BRIEF 的改動（尤其 IAM 權限調整、音色選擇、測試方式）→ 記進 D:\program\vocabbatcher\docs\planning\DECISIONS.md。
6. 收工前更新 D:\program\vocabbatcher\docs\planning\PROGRESS.md：加一行本切片成果，「▶ 下一步」改為「Google Cloud TTS 切片1（後端 Function）已完成待規劃層驗證，驗證通過後開切片2（前端串接，含 iPhone 實測）」。

## 最後一步：把執行結果寫成報告檔

完成以上所有工作後，在 D:\program\vocabbatcher\docs\handoff\ 底下新建 REPORT_CloudTtsS1_後端Function.md，內容依這個格式寫：

```markdown
# REPORT_CloudTtsS1_後端Function — 執行結果

- 執行時間：<填你的執行時間>
- 狀態：完成 / 部分完成（卡在哪裡）/ 失敗

## 改了什麼
<新增了哪些檔案、functions/ 的結構、synthesizeSpeech 的實作重點、firebase.json 的變更>

## 驗證結果
<怎麼測的、測試腳本在哪、怎麼重跑、正常情況與錯誤情況的實際輸出結果、產生的 mp3 檔案路徑跟你怎麼確認它是有效音檔>

## IAM / 權限調整（若有）
<有沒有遇到權限問題、怎麼解決的>

## 是否偏離 BRIEF
<有的話簡述已記錄在 DECISIONS.md 的哪一條；沒有就寫「無」>

## ★ 規劃層後續要做的事（白話、按順序）
<規劃層要怎麼驗證這片、要看哪個檔案/跑哪個指令>

## 遇到的問題 / 卡住的地方（若有）
<如果沒辦法完全解決，寫清楚卡在哪、需要規劃層或負責人做什麼決定>
```

這份報告檔是給規劃層（Claude）看的，可以寫技術細節。寫完這份報告代表你這次工作結束，不用再額外輸出總結。

## 真正的最後一步：commit（不用 push）

寫完報告檔後，確認 `git status` 沒有不該提交的檔案（特別注意 `functions/node_modules/`、測試產生的 mp3 檔案是否該加進 `.gitignore`），然後 `git add` 這次改動的檔案，`git commit`（commit message 用一句話講清楚這片做了什麼，可先 `git log --oneline -10` 看最近幾筆訊息風格再照著寫）。**這次不用 `git push`**，等規劃層確認這片可靠後再決定。

完成 commit 後，這次工作才算真正結束，不用再額外輸出總結。
