"""Clean up the requirements transcript."""
import re, json
from pathlib import Path

SRC = Path(r'D:\geointern-agent\实习报告要求\转录_实习报告要求.md')
OUT = Path(r'D:\geointern-agent\实习报告要求\周口店实习报告要求_整理版.md')

with open(SRC, 'r', encoding='utf-8') as f:
    content = f.read()

# === 1. Split into pages ===
pages = re.split(r'\n## (IMG\d+\.jpg)\n\n', content)
# pages[0] = header, pages[1]=name1, pages[2]=content1, pages[3]=name2, ...
header = pages[0]
page_data = []
for i in range(1, len(pages), 2):
    name = pages[i]
    text = pages[i+1] if i+1 < len(pages) else ''
    page_data.append({'file': name, 'text': text.strip()})

print(f'Total pages: {len(page_data)}')

# === 2. Extract page numbers from footers ===
for p in page_data:
    m = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日.*?(周口店实习队|地科院).*?(\d+)\s*$', p['text'], re.MULTILINE)
    if m:
        p['page'] = int(m.group(5))
    else:
        p['page'] = None

# === 3. Clean each page ===
for p in page_data:
    t = p['text']

    # Remove page footer lines
    t = re.sub(r'\n?\d{4}年\d{1,2}月\d{1,2}日.*?(?:周口店实习队|地科院).*?\d*\s*$', '', t, flags=re.MULTILINE)
    t = re.sub(r'\n?\d{4}年\d{1,2}月\d{1,2}日.*?(?:周口店实习队|地科院).*$', '', t, flags=re.MULTILINE)
    t = re.sub(r'\n?\d{4}年\d{1,2}月\S+\s*$', '', t, flags=re.MULTILINE)

    # Remove standalone note lines that are just editorial comments
    t = re.sub(r'\n注：.*?(?:应描述清楚|应交代).*?\？\n', '\n', t)

    # Fix ◆ characters
    t = t.replace('◆', '-')

    # Remove classroom discipline section (not relevant)
    if '学生课堂听课及教室学习规范' in t:
        t = re.sub(r'学生课堂听课及教室学习规范.*?中国地质大学\n?', '', t, flags=re.DOTALL)

    # Remove empty lines with just whitespace
    t = re.sub(r'\n{4,}', '\n\n\n', t)

    p['text'] = t.strip()

# === 4. Remove wrong-document pages ===
page_data = [p for p in page_data if '中国地质大学(武汉)' not in p['text']]
page_data = [p for p in page_data if '2016年8月' not in p['text']]
print(f'After removing foreign docs: {len(page_data)} pages')

# === 5. Detect and remove near-duplicate pages ===
# (e.g. 新元古界 appeared twice)
seen_sigs = {}
deduped = []
for p in page_data:
    sig = p['text'][:80] if len(p['text']) > 80 else p['text']
    if sig in seen_sigs:
        # Keep the one with more content
        prev = seen_sigs[sig]
        if len(p['text']) > len(prev['text']):
            deduped = [d for d in deduped if d is not prev]
            deduped.append(p)
            seen_sigs[sig] = p
    else:
        seen_sigs[sig] = p
        deduped.append(p)
page_data = deduped
print(f'After dedup: {len(page_data)} pages')

# === 6. Sort by page number ===
numbered = [p for p in page_data if p['page'] is not None]
unnumbered = [p for p in page_data if p['page'] is None]
numbered.sort(key=lambda p: p['page'])

# Remove duplicates with same page number (keep longer)
final = []
for p in numbered:
    existing = [f for f in final if f['page'] == p['page']]
    if existing:
        if len(p['text']) > len(existing[0]['text']):
            final = [f for f in final if f['page'] != p['page']]
            final.append(p)
    else:
        final.append(p)

print(f'After page-num dedup: {len(final)} numbered pages')
print(f'Unnumbered pages: {len(unnumbered)}')

# === 7. Write output ===
with open(OUT, 'w', encoding='utf-8') as f:
    f.write('# 周口店实习报告要求（整理版）\n\n')
    f.write('> 页码已按原稿顺序排列，重复页和噪音已清除\n\n')
    f.write('---\n\n')

    for p in final:
        f.write(f'## 第{p["page"]}页 ({p["file"]})\n\n')
        f.write(p['text'])
        f.write('\n\n---\n\n')

    if unnumbered:
        f.write('\n# 附录：未编号页\n\n')
        for p in unnumbered:
            f.write(f'## {p["file"]}\n\n')
            f.write(p['text'])
            f.write('\n\n---\n\n')

print(f'Output: {OUT}')

# === 8. Print page sequence ===
pages_seq = [p['page'] for p in final]
print(f'Page sequence: {pages_seq}')
print(f'Missing pages: {[i for i in range(min(pages_seq), max(pages_seq)+1) if i not in pages_seq]}')
