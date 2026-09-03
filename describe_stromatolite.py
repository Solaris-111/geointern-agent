"""Qwen-VL 描述 D0605 包心菜状叠层石"""
import base64, requests, os, io
from PIL import Image

img_path = "field_notebooks/周口店/day1/D0605包心菜状叠层石.jpg"
img = Image.open(img_path)
w, h = img.size
if max(w, h) > 2048:
    ratio = 2048 / max(w, h)
    img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)

buf = io.BytesIO()
img.save(buf, format="JPEG", quality=85)
img_b64 = base64.b64encode(buf.getvalue()).decode()

prompt = """请像一个沉积地质学家一样详细描述这块叠层石露头照片。

我需要的信息：
1. 叠层石的总体形态——大小、形状（穹状？柱状？包心菜状？）
2. 纹层的特征——同心环状？层状？纹层间距、颜色变化
3. 叠层石和围岩的关系——是孤立产出还是成层分布？顶底界面清晰吗？
4. 叠层石内部结构——有没有明显的明暗纹层交替？每层多厚？
5. 照片中有没有可以作为比例参照的物体？
6. 围岩的岩性是什么？（据野簿记载是铁岭组三段白云岩）
7. 叠层石的保存状态——完整还是被侵蚀？有没有被后期构造破坏？
8. 露头尺度——是手标本大小还是整个露头都可见？

请具体描述，直接输出，不要开场白。"""

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
    with open("output/D0605_stromatolite_description.md", "w", encoding="utf-8") as f:
        f.write(text)
    print("已保存: output/D0605_stromatolite_description.md")
    print("\n" + text)
else:
    print(f"API error: {resp.status_code}")
