# REPORT_CloudTtsS1_後端Function — 執行結果

- 執行時間：2026-08-14
- 狀態：完成，待規劃層驗證

## 改了什麼

- 新增根目錄 `functions/` Firebase Functions TypeScript 專案：
  - `functions/package.json`
  - `functions/package-lock.json`
  - `functions/tsconfig.json`
  - `functions/src/index.ts`
  - `functions/test/manual-test.mjs`
- `functions/package.json` 使用 Node 20 runtime，安裝：
  - `firebase-functions`
  - `firebase-admin`
  - `@google-cloud/text-to-speech`
  - `typescript`
- 新增 `synthesizeSpeech` callable function：
  - 使用 `firebase-functions/v2/https` 的 `onCall`
  - region：`us-central1`
  - 輸入 `{ text: string, lang: 'en-US' | 'en-GB' }`
  - 驗證 `text` 必填、必須是字串、trim 後不可空白、最多 200 字元
  - 驗證 `lang` 只能是 `en-US` 或 `en-GB`
  - 違反輸入規則時丟 `HttpsError('invalid-argument', ...)`
  - 呼叫 Google Cloud Text-to-Speech API，`audioEncoding: 'MP3'`
  - 回傳 `{ audioBase64: string }`
- `TextToSpeechClient` 採 lazy initialization。第一次部署曾因模組載入階段初始化 client，Firebase CLI 分析 user code 時 timeout；改成 function 執行時才建立 client 後部署通過。
- `firebase.json` 新增 `functions` 設定：
  - `source: "functions"`
  - `runtime: "nodejs20"`
  - predeploy 跑 `npm --prefix "$RESOURCE_DIR" run build`
- `.gitignore` 新增：
  - `functions/lib/`
  - `functions/test-output/`

## 驗證結果

### Build

在 `functions/` 內執行：

```powershell
npm.cmd run build
```

結果：通過。

### Deploy

在專案根目錄執行：

```powershell
npx.cmd --yes firebase-tools@latest deploy --only functions
```

結果：部署完成。

部署目標：

- Firebase project：`gen-lang-client-0930375434`
- Function：`synthesizeSpeech`
- Region：`us-central1`
- Endpoint：`https://us-central1-gen-lang-client-0930375434.cloudfunctions.net/synthesizeSpeech`

補充：Firebase CLI 顯示 Node.js 20 runtime 已在 2026-04-30 deprecated，將於 2026-10-30 decommission。這片依 BRIEF 指定仍使用 Node 20；下一輪若規劃層要長期維運 Functions，建議評估升級 runtime。

### Manual test

測試腳本：

```text
functions/test/manual-test.mjs
```

重跑方式：

```powershell
cd D:\program\vocabbatcher\functions
npm.cmd run test:manual
```

實際輸出：

```text
calling https://us-central1-gen-lang-client-0930375434.cloudfunctions.net/synthesizeSpeech
success: wrote D:\program\vocabbatcher\functions\test-output\synthesizeSpeech-en-US.mp3 (7872 bytes)
invalid lang: rejected with INVALID_ARGUMENT (lang must be either en-US or en-GB.)
```

正常情境：

- request data：`{ text: 'enhance', lang: 'en-US' }`
- response：有 `result.audioBase64`
- 產生檔案：`functions/test-output/synthesizeSpeech-en-US.mp3`
- 檔案大小：7872 bytes
- 腳本驗證：base64 解碼後非空，且檔頭符合 MP3（`ID3` 或 MP3 frame sync）

錯誤情境：

- request data：`{ text: 'enhance', lang: 'en-AU' }`
- response：`INVALID_ARGUMENT`
- message：`lang must be either en-US or en-GB.`

## IAM / 權限調整（若有）

沒有手動調整 IAM 角色，也沒有新增或使用手動 API key。

部署過程中 Firebase CLI 自動啟用首次 Gen 2 Functions 部署所需 API：

- `cloudfunctions.googleapis.com`
- `cloudbuild.googleapis.com`
- `artifactregistry.googleapis.com`
- `firebaseextensions.googleapis.com`
- `run.googleapis.com`
- `eventarc.googleapis.com`

另外依 Firebase CLI 要求，設定 Artifact Registry cleanup policy：

```powershell
npx.cmd --yes firebase-tools@latest functions:artifacts:setpolicy --location us-central1 --days 1 --force
```

結果：`projects/gen-lang-client-0930375434/locations/us-central1/repositories/gcf-artifacts` 會自動刪除 1 天前的 Functions container images，避免映像累積造成小額費用。此雲端設定已記錄在 `docs/planning/DECISIONS.md` 2026-08-14 條目。

## 是否偏離 BRIEF

無產品範圍偏離。

補充：音色選擇採 `voice: { languageCode: lang, ssmlGender: 'NEUTRAL' }`，沒有指定具體 voice name，讓 Google Cloud TTS 依語言挑穩定可用的預設中性語音；這符合 BRIEF 的「固定一個合理預設音色」。

雲端部署配套（必要 API 啟用、Artifact cleanup policy）已記錄在 `DECISIONS.md`。

## ★ 規劃層後續要做的事（白話、按順序）

1. 看 `functions/src/index.ts`，確認輸入限制是 `text <= 200`，`lang` 只有 `en-US` / `en-GB`。
2. 重跑 `functions` build：
   ```powershell
   cd D:\program\vocabbatcher\functions
   npm.cmd run build
   ```
3. 重跑遠端驗證腳本：
   ```powershell
   cd D:\program\vocabbatcher\functions
   npm.cmd run test:manual
   ```
4. 確認輸出有：
   - 成功產生 `functions/test-output/synthesizeSpeech-en-US.mp3`
   - 檔案大小不是 0
   - 不合法 `lang` 被 `INVALID_ARGUMENT` 擋下
5. 如果要人工聽音檔，播放 `functions/test-output/synthesizeSpeech-en-US.mp3`。
6. 驗證通過後，再開切片2：前端串接 `tts.ts` / `SettingsPage.tsx`，並安排 iPhone 實機測試。

## 遇到的問題 / 卡住的地方（若有）

- 第一次部署失敗：`User code failed to load. Cannot determine backend specification. Timeout after 10000.` 根因是 `TextToSpeechClient` 在 module load 階段初始化，Firebase CLI 分析 user code 時會載入模組，導致部署分析 timeout。已改成 lazy initialization 後解決。
- 第一次成功建立 function 後，Firebase CLI 因 Artifact Registry cleanup policy 尚未設定而回傳非 0；已設定 1 天 cleanup policy，重跑 deploy 後成功以 0 結束。
- 本機呼叫遠端 function 第一次被沙箱網路擋住；用授權模式重跑後 manual-test 通過。
