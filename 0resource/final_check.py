import json
with open('output/vocab.cleaned.json', encoding='utf-8') as f:
    data = json.load(f)
has_def = sum(1 for e in data if e['zh_definition'])
print(f'總單字: {len(data)}')
print(f'有中文定義: {has_def} ({has_def/len(data)*100:.1f}%)')
print(f'無定義(專有名詞等): {len(data)-has_def}')
print()
high = sorted(data, key=lambda e: -(e['frequency'] or 0))[:5]
for e in high:
    freq = e['frequency']
    word = e['word']
    zh = e['zh_definition']
    print(f'freq={freq:2d}  {word:14} | {zh}')
