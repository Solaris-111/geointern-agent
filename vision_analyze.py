import base64, requests, json, sys, os
from PIL import Image

image_paths = sys.argv[1:] if len(sys.argv) > 1 else [r"D:\geointern-agent\识图素材\26-7-23\_resized.jpg"]

prompt = """请逐字转录这两页《周口店地质实习指导书》的内容（第四章 p81-p82，路线1 踏勘路线）。

要求:
1. 逐字转录正文，保留原文格式
2. 特别关注: 路线名称、路线走向、观察点列表、每个点的点位和点性、任务清单
3. 如果有表格，转换为 Markdown 表格
4. 不确定的字用 [?] 标注

这是写野簿预稿的权威来源，必须准确。"""

content_blocks = []
for path in image_paths:
    if not os.path.exists(path):
        print(f"File not found: {path}")
        continue
    # Resize if needed
    img = Image.open(path)
    if max(img.size) > 1500:
        ratio = 1500 / max(img.size)
        img = img.resize((int(img.size[0]*ratio), int(img.size[1]*ratio)))
    tmp = path.replace('.png', '_tmp.png')
    img.save(tmp)
    with open(tmp, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode()
    content_blocks.append({'type': 'image_url', 'image_url': {'url': f'data:image/png;base64,{b64}'}})

content_blocks.append({'type': 'text', 'text': prompt})

resp = requests.post(
    'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
    headers={'Authorization': f"Bearer {os.getenv('DASHSCOPE_API_KEY')}"},
    json={
        'model': 'qwen-vl-max',
        'messages': [{'role': 'user', 'content': content_blocks}]
    }
)

result = resp.json()
content = result['choices'][0]['message']['content']
with open('vision_output.txt', 'w', encoding='utf-8') as f:
    f.write(content)
print("Done. Output saved to vision_output.txt")
