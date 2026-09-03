"""用 Qwen-VL 看图验图"""
import base64, requests, os, io
from PIL import Image

img_path = "field_notebooks/周口店/day1/D0601燧石条带先后关系.jpg"
size_mb = os.path.getsize(img_path) / 1024 / 1024
print(f"原始: {size_mb:.1f} MB")

img = Image.open(img_path)
w, h = img.size
if max(w, h) > 2048:
    ratio = 2048 / max(w, h)
    img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)

buf = io.BytesIO()
img.save(buf, format="JPEG", quality=85)
compressed = buf.getvalue()
print(f"压缩后: {len(compressed)/1024:.0f} KB")

img_b64 = base64.b64encode(compressed).decode()

prompt = """这是一张野外地质野簿上的素描图，主题是"燧石条带先后关系"（图6-1）。

请详细描述：
1. 图中画了什么？（岩层、燧石条带、纹理方向）
2. 图中有什么标注？（文字、箭头、图例、比例尺、方向等）
3. 图的构图是否完整？缺少什么？（指北针、比例尺、图名、图例、地层代号等）
4. 如果有问题，具体指出来——哪条线不对、哪个标注位置不好、缺少什么关键信息

请逐项说明，直接描述，不要加"这张图是..."之类的开场白。"""

resp = requests.post(
    "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {os.getenv('DASHSCOPE_API_KEY')}",
        "Content-Type": "application/json",
    },
    json={
        "model": "qwen-vl-max",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
                {"type": "text", "text": prompt},
            ],
        }],
    },
    timeout=120,
)

if resp.status_code == 200:
    text = resp.json()["choices"][0]["message"]["content"]
    print("\n" + "=" * 60)
    print(text)
else:
    print(f"API error: {resp.status_code}")
