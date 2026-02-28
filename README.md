# VocabBatcher

國中會考英文單字練習 App — 從 PDF 到互動學習。

## 專案組成

| 元件 | 說明 |
|------|------|
| **PDF Parser** | Python CLI：`top2025.pdf` → 結構化 JSON |
| **Mobile App** | React Native + Expo：勾選單字 → 批次錄音 / 練習 |
| **UI Prototype** | Stitch 高保真手機原型 |

## 核心流程

篩選單字 → 勾選 ≤25 字 → 批次 Hub →
- 🔊 批次錄音（TTS + 間隔 3/5/10 秒）
- 📖 逐字學習（翻牌卡）
- ✏️ 練習測驗（四題型）
- 📊 統計（正確率 / 錯題重練）

## 開發環境

- Python 3.11+（PDF Parser）
- Node.js 18+（React Native / Expo）
- VS Code + GitHub Copilot（Agent mode）

## Workspace 結構

使用 [copilot-workspace-template](https://github.com/hsiaochiang/copilot-workspace-template) 建置。
詳見 `0resource/WORKSPACE_GUIDE.copilot.zh-TW.v1.md`。
