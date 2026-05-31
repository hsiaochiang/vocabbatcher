import json
with open('output/vocab.raw.json', encoding='utf-8') as f:
    data = json.load(f)
no_def = [e for e in data if e['zh_definition'] is None]
print(f'無定義: {len(no_def)} 筆')
for e in no_def:
    print(f"  {e['word']:14} freq={e['frequency']} page={e['source_page']}")
