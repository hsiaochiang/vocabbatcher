"""從 vocab.cleaned.json 生成 top2025.md"""
import json
from pathlib import Path

with open('output/vocab.cleaned.json', encoding='utf-8') as f:
    data = json.load(f)

# 按 frequency 分組，每組內字母排序
freq_groups: dict[int, list] = {}
for e in data:
    freq = e['frequency'] or 0
    freq_groups.setdefault(freq, []).append(e)
for freq in freq_groups:
    freq_groups[freq].sort(key=lambda e: e['word'].lower())

freq_counts = sorted(freq_groups.keys(), reverse=True)

# 中文數字對照
zh_num = {10:'十',9:'九',8:'八',7:'七',6:'六',5:'五',4:'四',3:'三',2:'二',1:'一'}

lines = []
lines.append("# 115 會考版 (105~114)")
lines.append("")
lines.append("## 會考高頻率單字表")
lines.append("")
lines.append("依近10年會考出現次數編排")
lines.append("")
lines.append("> 尊重著作權，請勿轉傳")
lines.append("")
lines.append("Copyright © 2025 Top Academy")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## 目錄")
lines.append("")
for freq in freq_counts:
    if freq > 0:
        zh = zh_num.get(freq, str(freq))
        cnt = len(freq_groups[freq])
        lines.append(f"- {zh}、出現次數：{freq}（共 {cnt} 個）")
lines.append("")
lines.append("---")
lines.append("")

# 各頻率分節
for freq in freq_counts:
    if freq == 0:
        continue
    entries = freq_groups[freq]
    zh = zh_num.get(freq, str(freq))
    lines.append(f"## {zh}、出現次數：{freq}")
    lines.append("")
    lines.append("| 單字 | 詞性 | 中文定義 |")
    lines.append("|------|------|---------|")
    for e in entries:
        word = e['word']
        pos = f"[{e['pos']}]" if e['pos'] else ''
        zh_def = e['zh_definition'] or ''
        # 移除定義中的詞性標記（已在 pos 欄顯示），讓定義欄更乾淨
        import re
        zh_clean = re.sub(r'\[[a-z]+\.?\]', '', zh_def).strip()
        zh_clean = re.sub(r'  +', ' ', zh_clean)
        # Markdown 表格中的 | 需轉義
        zh_clean = zh_clean.replace('|', '\\|')
        lines.append(f"| **{word}** | {pos} | {zh_clean} |")
    lines.append("")

output_path = Path('0resource/top2025.md')
output_path.write_text("\n".join(lines), encoding='utf-8')
print(f"✓ 生成完成：{output_path}")
print(f"  總單字：{sum(len(v) for v in freq_groups.values())}")
