
"""
Qwen-VL-Max 批量转录工具
用法: python qwen_vl_batch.py <pdf_path> [-o output.md] [--dpi 200] [--delay 1.5]
"""
import base64, requests, json, time, sys, os
from pathlib import Path
import fitz
from PIL import Image
import io

API_KEY = os.getenv("DASHSCOPE_API_KEY")
API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
MODEL = "qwen-vl-max"

PROMPT_TEXT = "请逐字转录本页的地质实习报告内容，忽略页眉页脚和页码，只输出文字。"
PROMPT_FIGURE = "请转录本页内容并描述图中地质信息（岩性、构造、产状、比例尺、图例、地层代号等）。"

# Page ranges with figures (customize per document)
FIGURE_PAGES = set()

def call_vl(image_bytes, prompt):
    img_b64 = base64.b64encode(image_bytes).decode()
    resp = requests.post(API_URL,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={"model": MODEL, "messages": [{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
            {"type": "text", "text": prompt}
        ]}]}, timeout=120)
    data = resp.json()
    return data["choices"][0]["message"]["content"]

def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("pdf", help="PDF file path")
    p.add_argument("-o", "--output", default=None)
    p.add_argument("--dpi", type=int, default=200)
    p.add_argument("--delay", type=float, default=1.5)
    args = p.parse_args()

    if args.output is None:
        args.output = Path(args.pdf).stem + "_QwenVL转录.md"

    doc = fitz.open(args.pdf)
    total = len(doc)
    results = []
    for pi in range(total):
        pg = pi + 1
        is_fig = pg in FIGURE_PAGES
        prompt = PROMPT_FIGURE if is_fig else PROMPT_TEXT
        print(f"[{pg}/{total}] {'FIG' if is_fig else 'TXT'} ... ", end="", flush=True)

        pix = doc[pi].get_pixmap(dpi=args.dpi)
        img_bytes = pix.tobytes("png")
        try:
            text = call_vl(img_bytes, prompt)
            results.append((pg, text))
            print(f"OK ({len(text)} chars)")
        except Exception as e:
            print(f"FAIL: {e}")
            results.append((pg, f"[ERROR: {e}]"))

        if pi < total - 1:
            time.sleep(args.delay)
    doc.close()

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(f"# {Path(args.pdf).stem} (Qwen-VL-Max 转录)\n\n")
        for pg, txt in results:
            f.write(f"## Page {pg}\n\n{txt}\n\n---\n\n")
    print(f"Done: {args.output}")

if __name__ == "__main__":
    main()
