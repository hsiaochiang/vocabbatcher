# Skill: scribe（記錄官／投影片素材整理）

## 任務目標
把每次 session 的成果整理成可投影片化素材，不依賴冗長對話匯出。

## Inputs
- 本次做了什麼（或 git diff --stat）
- 重要決策（docs/decisions）
- 重要 bug 與修復證據（docs/bugs、docs/qa）

## Outputs（必交付）
- `experience/<YYYY-MM>/slides_<date>_talk-outline.md`，建議結構：
  1) **目標**：本次 session 要解決什麼
  2) **問題**：遇到什麼阻礙 / 挑戰
  3) **方法**：用什麼策略解決
  4) **結果**：前後對照（before/after）
  5) **學到什麼**：踩雷與修正
- 重點素材：問題/方法/對照/示範步驟/踩雷與修正

## Session 結束前 Checklist
- [ ] `docs/roadmap.md` 已更新目前階段
- [ ] `docs/runlog/<date>_README.md` 已記錄今日進度
- [ ] 未結案的 bug 已記錄在 `docs/bugs/`
- [ ] 重要決策已記錄在 `docs/decisions/`
- [ ] 產出 slides outline
