# ADR-004：TTS 只做單詞發音，不做循環播放

日期：2026-05-31
狀態：已採用

## 背景

原始規格書（M2）要求 TTS 批次播放：英文 → 間隔 → 中文 → 間隔 → 下一字，循環播放 25 個字。三種間隔（3/5/10 秒）可選。

調研後發現 Chrome Android 的 `speechSynthesis.pause()` / `resume()` 有嚴重 bug（Chromium issue #335907，開放超過 10 年，至今未修）。在 Android 上用 `pause()` + `setTimeout` 實作間隔靜音，實際上會截斷 utterance。Chrome Desktop 也有 15 秒以上自動截斷的問題。

## 決定

TTS 只做單詞發音：`speakEn(word)` 和 `speakZh(text)`，每次只播一個字。不實作 25 字循環連播。

## 理由

1. **Chrome Android 的 pause/resume 有已知 bug**——無法可靠暫停和恢復語音
2. **15 秒截斷問題**——Chrome Desktop 對長 utterance 也有自動截斷
3. **翻牌卡設計天然適合單詞發音**——翻到背面自動播中文一次，比循環播放更自然

## 評估過的替代方案

| 方案 | 為什麼沒選 |
|------|-----------|
| utterance chaining + setTimeout | 可行但 Android 實測成本高，邊界情況多 |
| expo-speech（React Native）| 已放棄 React Native 平台 |
| 預先合成 MP3（Web Audio API）| 合成品質差，需要後端或複雜 JavaScript |

## 後果

- 循環發音列入 B-2+ 待辦，若日後要加，需要用 Android 實機反覆測試
- 翻牌卡的 UX 設計改為：翻到背面自動播中文一次，正面有手動播英文按鈕
- `speakEn` / `speakZh` 每次呼叫前先 `cancel()`，避免前一個 utterance 卡住
