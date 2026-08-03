# BRIEF_S3d_登入除錯面板.md — M3 插入切片：加裝暫時性登入除錯面板

> 交接合約：規劃層 → 執行層，2026-07-31。
> 背景：`BRIEF_S3b`、`BRIEF_S3c` 依序排除了「S3 程式碼回歸」與「GitHub Pages 跨網域第三方儲存限制」，
> 把正式站遷移到 Firebase Hosting 後，負責人改用跟 `authDomain` 完全同源的
> `https://gen-lang-client-0930375434.firebaseapp.com` 網址測試，**登入仍然失敗**，而且這次兩支手機
> 症狀不同：iPhone Safari 完成 Google 登入導回後仍無頭像；Android Chrome 點擊登入按鈕後，**甚至沒有跳出
> Google 帳號選擇畫面**。這代表先前「跨網域第三方儲存限制」的假設不足以解釋全部現象，需要看到瀏覽器
> 端實際發生什麼（例外訊息、程式執行到哪一步），但負責人不會操作瀏覽器開發者工具，只能用肉眼讀畫面文字。

## 開場指令（執行層開工先做）
1. 讀 `PROGRESS.md` 恢復脈絡。
2. 讀 `REPORT_S3b_登入異常修復.md`、`REPORT_S3c_遷移至FirebaseHosting.md` 了解前兩輪診斷與已排除的假設。
3. 工作目錄為 `exam-vocab-batcher/`。

## 目標（一句話）
> 在畫面上加一段暫時的、肉眼可見的除錯資訊區塊，讓負責人點擊登入按鈕時，不管成功或失敗，都能把畫面上顯示的技術文字截圖或抄下來回報，藉此找出登入真正卡在哪一步。

## 任務

1. **在 `UserBadge.tsx`（或新增一個暫時的除錯元件，掛在同一個位置）加入即時狀態顯示**，用小字、不影響版面配置即可，但要清楚、negative-space 夠讓人看得到：
   - 目前 `firebaseEnabled` 的值（true/false）。
   - 每一次呼叫 `signInWithGoogle()` 前，先顯示一行「準備導向登入…」，並記錄這行文字是否有真的顯示出來（用來判斷 Android 案例是不是連 `handleSignIn` 都沒被觸發，例如按鈕被其他元素蓋住、或事件被攔截）。
   - `signInWithGoogle()` 若拋出例外，除了現有的紅字提示，額外把 `err` 的 `code`、`message` 完整印在畫面上（不要只印固定文字「登入失敗，請再試一次」）。
   - 頁面載入時 `completeRedirectSignIn()` 的執行結果：拿到 user、拿到 null、還是拋出例外，三種情況都要各自顯示對應文字與（若有）`err.code`/`err.message`。
   - `onAuthStateChanged()` 每次觸發時，把目前的 `user` 是否為 null 顯示出來（例如「登入狀態：未登入」／「登入狀態：已登入 xxx」），因為現況是「重新整理後也沒有頭像」，這代表 `onAuthStateChanged` 持續回報 null，需要知道這是不是真的。
   - 額外加一個全域 `window.addEventListener('unhandledrejection', ...)` 與 `window.onerror`，把任何未被現有 try/catch 接住的例外，也顯示在同一個除錯區塊（避免有例外被吞掉、畫面上完全沒反應）。

2. **除錯區塊的呈現方式**：文字要能被使用者截圖，建議放在頁面底部或做成可以展開的小面板，避免遮住主要操作按鈕；顏色不用講究，能看清楚字就好。

3. **不要移除或簡化現有的正常錯誤提示邏輯**，除錯區塊是「額外疊加」的資訊，不是取代。

4. `npm run lint`、`npm run build` 要過。

## 邊界（本切片不做）
- 不嘗試自己修復登入邏輯或猜測根因並直接改 `signInWithRedirect` 相關程式碼——這片純粹是加除錯可視化，讓負責人能回報真正發生什麼，下一片才會根據回報結果對症下藥。
- 不動 S3 考試引擎程式碼。
- 不用猜測的方式決定要不要改回 `signInWithPopup`、Google Identity Services 等——那是下一輪根據除錯結果才能做的決定。

## 驗收（負責人操作）
1. 部署後（負責人會自己跑 `npm run build` + `firebase deploy --only hosting`），在 iPhone Safari 開啟 `https://gen-lang-client-0930375434.firebaseapp.com`，點擊「使用 Google 登入」，把畫面上除錯區塊顯示的**完整文字**截圖或抄下來回報。
2. Android Chrome 重複同樣操作，一樣把除錯區塊的完整文字回報。
3. 兩支手機都要包含：點擊當下顯示了什麼、（若有導回）導回後 `completeRedirectSignIn` 顯示了什麼、`onAuthStateChanged` 顯示的登入狀態。

## 收尾指令（執行層收工必做）
1. 更新 `PROGRESS.md`：記錄本切片是「除錯用途」的暫時性改動，下一步是等負責人回報畫面文字。
2. 若有偏離本 BRIEF 的改動 → 記 `DECISIONS.md`。
3. 收工報告請照 `CODEX_PROMPT_S3d_登入除錯面板.md` 的格式寫，報告裡要提醒規劃層「這是暫時除錯用途，問題解決後要記得移除」。
