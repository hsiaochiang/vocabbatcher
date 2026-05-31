# ADR-002：平台從 React Native + Expo 改為 Web PWA

日期：2026-05-31
狀態：已採用

## 背景

專案初期規劃使用 React Native + Expo 開發 Android App。但在評估實作成本後，發現 React Native 需要 Android Studio 編譯環境、TTS 實作（expo-speech）比瀏覽器複雜、部署需要簽署 APK 上架。

這個 App 的使用者是國中生，使用情境是「在手機上練習會考單字」，不需要 App Store 的曝光和分發。

## 決定

放棄 React Native，改為 React + Vite + vite-plugin-pwa，部署到 GitHub Pages。

## 理由

1. **零部署成本**——GitHub Pages 免費，靜態檔案直接 serve，不需要任何 server
2. **開發門檻低**——不需要 Android Studio / Xcode，一台有 Node.js 的電腦就能開發
3. **Web Speech API 夠用**——瀏覽器原生支援 TTS，不需要額外套件

## 評估過的替代方案

| 方案 | 為什麼沒選 |
|------|-----------|
| React Native + Expo | 編譯環境複雜、TTS 實作繁瑣、部署需 APK 簽署 |
| Capacitor（Web 轉原生）| 比直接 PWA 複雜，對這個專案優勢不明顯 |
| Flutter | 學習成本高，與現有技術棧（React / TypeScript）不符 |

## 後果

- iOS Safari 的「加入主畫面」需要使用者手動操作（不像 Android Chrome 有自動提示）
- 後台持續播放受瀏覽器限制（但 App 設計上不需要後台播放）
- 無法上架 Google Play / App Store（但使用者直接開網址即可）
