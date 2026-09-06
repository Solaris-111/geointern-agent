"""Batch transcribe internship report requirements."""
import base64, requests, json, sys, os, time, io
from PIL import Image
from pathlib import Path

if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except: sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SRC = Path(r'D:\geointern-agent\实习报告要求')
OUT = Path(r'D:\geointern-agent\实习报告要求\转录_实习报告要求.md')
CKPT = Path(r'D:\geointern-agent\实习报告要求\checkpoint.json')

PROMPT = '逐字转录本页所有文字内容，保留原文格式。如果是表格，转Markdown表格。只输出转录，不加任何说明。'

imgs = sorted(SRC.glob('*.jpg'))
print(f'{len(imgs)} images')

# Load checkpoint
results = {}
if CKPT.exists():
    with open(CKPT, 'r', encoding='utf-8') as f:
        results = json.load(f)

remaining = [p for p in imgs if p.name not in results]
print(f'{len(results)} done, {len(remaining)} remaining')

for i, img_path in enumerate(remaining):
    print(f'[{i+1}/{len(remaining)}] {img_path.name}...', end=' ', flush=True)
    try:
        img = Image.open(img_path)
        if max(img.size) > 2000:
            ratio = 2000 / max(img.size)
            img = img.resize((int(img.size[0]*ratio), int(img.size[1]*ratio)))
        tmp = img_path.with_suffix('.tmp.png')
        img.save(tmp)
        with open(tmp, 'rb') as f:
            b64 = base64.b64encode(f.read()).decode()
        tmp.unlink()

        resp = requests.post(
            'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
            headers={'Authorization': f"Bearer {os.getenv('DASHSCOPE_API_KEY')}"},
            json={'model': 'qwen-vl-max', 'messages': [{'role': 'user', 'content': [
                {'type': 'image_url', 'image_url': {'url': f'data:image/png;base64,{b64}'}},
                {'type': 'text', 'text': PROMPT}
            ]}]},
            timeout=120
        )
        text = resp.json()['choices'][0]['message']['content']
        results[img_path.name] = text
        print(f'OK ({len(text)} chars)', flush=True)

        if (i+1) % 10 == 0:
            with open(CKPT, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False)

        time.sleep(0.3)
    except Exception as e:
        print(f'ERROR: {e}', flush=True)
        results[img_path.name] = f'[失败: {e}]'
        with open(CKPT, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False)

# Write output
with open(OUT, 'w', encoding='utf-8') as f:
    f.write('# 周口店实习报告要求（完整转录）\n\n')
    for name in sorted(results.keys()):
        f.write(f'## {name}\n\n')
        f.write(results[name])
        f.write('\n\n---\n\n')

CKPT.unlink()
print(f'Done: {OUT}')
