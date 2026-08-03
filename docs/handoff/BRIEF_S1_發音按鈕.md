# BRIEF_S1_發音按鈕.md — M3 切片 1：發音按鈕全面化

> 交接合約：規劃層(Cowork) → 執行層(Codex CLI)，2026-07-06。
> 對應需求：`REQUIREMENTS.md` R8。切片全景見 `STAGE_3_PLAN.md`。

## 開場指令（執行層開工先做）
1. 讀 `PROGRESS.md` 恢復脈絡。
2. 讀本 BRIEF 全文；工作目錄為 `exam-vocab-batcher/`。

## 目標（一句話）
> 使用者在 App 內任何看得到英文單字的地方，都有一個 🔊 按鈕，點了用英文 TTS 唸出該字。

## 現況
- TTS 服務已存在：`src/services/tts.ts`（`speakEn` / `speakZh`），目前只有 `FlashCardPage` 在用。
- 單字顯示位置：`WordCard.tsx`（列表/選字用）、`FlashCardPage.tsx`（已有發音）、`BatchHubPage.tsx`。

## 任務
1. 建立可重用元件 `src/components/SpeakButton.tsx`：props 收 `word: string`，點擊呼叫 `speakEn(word)`；`window.speechSynthesis` 不存在時不渲染。
2. 在 `WordCard.tsx` 每個單字旁加入 `SpeakButton`（點擊不可觸發卡片勾選——`stopPropagation`）。
3. 檢查 `BatchHubPage` 等其他顯示單字處，一併補上。
4. 觸控面積 ≥ 44×44px（沿用 2026-05-31 UI 修正的既有標準）。
5. 發音一律經 `tts.ts`，不得在元件內直接 `new SpeechSynthesisUtterance`。

## 邊界（本切片不做）
- 不做中文發音按鈕（翻牌卡既有行為不動）。
- 不做語速/音色設定。
- 不動考試相關程式（S3 才做，屆時重用 `SpeakButton`）。

## 驗收（負責人操作）
1. 開單字列表頁，每個字旁有喇叭圖示；點喇叭會唸該字，且不會誤勾選該字。
2. iPad Safari 與 Android Chrome 實機各測一次。
3. `npm run lint` 與 `npm run build` 通過。

## 收尾指令（執行層收工必做）
1. 更新 `PROGRESS.md`：✅ 加一行本切片成果；「▶ 下一步」改為「等負責人驗收 S1，過了開 `BRIEF_S2_雲端帳號.md`」。
2. 若有任何偏離本 BRIEF 的改動 → 記 `DECISIONS.md`。
3. 給負責人「現在你能做什麼」＋操作步驟。
