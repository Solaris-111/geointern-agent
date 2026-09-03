"""用 Qwen-VL 详细描述露头结构"""
import base64, requests, os, io
from PIL import Image

img_path = "field_notebooks/周口店/day1/D0601燧石条带先后关系.jpg"
img = Image.open(img_path)
w, h = img.size
if max(w, h) > 2048:
    ratio = 2048 / max(w, h)
    img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)

buf = io.BytesIO()
img.save(buf, format="JPEG", quality=85)
img_b64 = base64.b64encode(buf.getvalue()).decode()

prompt = """请像一个构造地质学家一样详细描述这个露头照片。

我需要的信息：
1. 岩层总体产状（大致倾向和倾角，目估即可）
2. 燧石条带的数量、形态、厚度（哪些是顺层贯入的？哪些是后期穿层的？）
3. 燧石条带和层面的关系——哪条在先哪条在后？有没有切割关系？
4. 各组燧石条带可以分为几期？它们的先后顺序是什么？
5. 有没有被错断或褶皱变形的条带？
6. 岩层的颜色、岩性外观（白云岩？灰岩？）
7. 照片中可以作为比例参照的物体（素描本大概 A5 大小）

请尽可能具体地描述每条燧石条带的特征和它们之间的切割/包裹关系。按从早到晚的顺序排列。

直接输出描述，不要开场白。"""

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
    with open("output/D0601_outcrop_description.md", "w", encoding="utf-8") as f:
        f.write(text)
    print("已保存: output/D0601_outcrop_description.md")
    print("\n" + text)
else:
    print(f"API error: {resp.status_code}")
