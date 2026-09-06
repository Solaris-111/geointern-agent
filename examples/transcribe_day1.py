"""压缩野簿照片并用 Qwen-VL 逐页转录"""

import base64
import requests
import json
import os
import glob
from PIL import Image
import io

API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
API_KEY = os.getenv("DASHSCOPE_API_KEY")

PROMPT = """请逐字转录这页野外地质实习野簿的内容。

要求：
1. 所有文字逐字抄录，包括页眉的日期、天气、路线编号等
2. 产状数据精确转录（倾向∠倾角格式）
3. 地层代号保持原样（如 P₂β、T₁f、∈₁f 等）
4. 如果有素描图，描述图中画了什么（岩性、构造、标注）
5. 点号、GPS坐标、点性——这些是重点，不要遗漏
6. 忽略页边距之外的背景（桌面等）
7. 直接输出转录内容，不要加"这一页是..."之类的说明"""


def compress_image(img_path, max_size_mb=2.0, max_dim=2048):
    """压缩图片到指定大小以下"""
    img = Image.open(img_path)

    # 缩小尺寸
    w, h = img.size
    if max(w, h) > max_dim:
        ratio = max_dim / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)

    # 逐步降低质量直到满足大小要求
    quality = 85
    while True:
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality)
        size_mb = len(buf.getvalue()) / 1024 / 1024
        if size_mb <= max_size_mb or quality <= 20:
            return buf.getvalue()
        quality -= 10


def main():
    img_dir = "field_notebooks/周口店/day1"
    out_dir = "output/day1_transcripts"
    os.makedirs(out_dir, exist_ok=True)

    images = sorted(glob.glob(f"{img_dir}/*.jpg"))

    all_text = []

    for i, img_path in enumerate(images):
        fname = os.path.basename(img_path)
        print(f"\n[{i+1}/{len(images)}] {fname} ", end="", flush=True)

        # 压缩
        compressed = compress_image(img_path, max_size_mb=1.5)
        img_b64 = base64.b64encode(compressed).decode()
        print(f"压缩后 {len(compressed)/1024:.0f}KB ", end="", flush=True)

        # 调用 Qwen-VL
        try:
            resp = requests.post(
                API_URL,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "qwen-vl-max",
                    "messages": [{
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
                            {"type": "text", "text": PROMPT},
                        ],
                    }],
                },
                timeout=120,
            )

            if resp.status_code == 200:
                result = resp.json()
                text = result["choices"][0]["message"]["content"]
                print("OK")

                # 保存单页转录
                page_num = i + 1
                with open(f"{out_dir}/page{page_num:02d}.md", "w", encoding="utf-8") as f:
                    f.write(f"# 第{page_num}页 — {fname}\n\n{text}")

                all_text.append(f"\n## 第{page_num}页 ({fname})\n\n{text}")
            else:
                print(f"API错误: {resp.status_code} {resp.text[:200]}")

        except Exception as e:
            print(f"失败: {e}")

    # 汇总
    full_path = f"{out_dir}/full_transcript.md"
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(f"# Day1 野簿转录汇总\n\n")
        f.write(f"共 {len(images)} 页，转录 {len(all_text)} 页\n")
        f.write("".join(all_text))

    print(f"\n完成！转录文件在 {out_dir}/")


if __name__ == "__main__":
    main()
