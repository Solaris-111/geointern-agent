"""地质素描引擎 — 照片 → 铅笔素描 + 矢量线稿"""

import cv2
import numpy as np
import vtracer
import os


def dodge_blend(gray, blur_ksize=31):
    inverted = 255 - gray
    blurred = cv2.GaussianBlur(inverted, (blur_ksize, blur_ksize), 0)
    return cv2.divide(gray, 255 - blurred, scale=256.0)


def sharpen(img, amount=1.2):
    blurred = cv2.GaussianBlur(img, (0, 0), 3)
    return cv2.addWeighted(img, 1.0 + amount, blurred, -amount, 0)


def geo_sketch(photo_path, out_dir, name):
    """
    输入: 露头照片路径
    输出: 两张图
      - {name}_pencil.png   CLAHE+锐化+粗笔触铅笔素描
      - {name}_vector.svg   VTracer binary 原图矢量线稿
    """
    os.makedirs(out_dir, exist_ok=True)

    # === 1. 铅笔素描 ===
    img = cv2.imread(photo_path)
    if img is None:
        raise FileNotFoundError(f"无法读取: {photo_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    sharp = sharpen(enhanced, amount=1.2)
    sketch = dodge_blend(sharp, blur_ksize=31)

    pencil_path = os.path.join(out_dir, f"{name}_pencil.png")
    cv2.imwrite(pencil_path, sketch)
    ps = os.path.getsize(pencil_path)

    # === 2. 矢量线稿 (VTracer binary 原图) ===
    vector_path = os.path.join(out_dir, f"{name}_vector.svg")
    vtracer.convert_image_to_svg_py(
        photo_path,
        vector_path,
        colormode="binary",
        mode="spline",
    )
    vs = os.path.getsize(vector_path)

    print(f"{name}:")
    print(f"  铅笔素描: {pencil_path} ({ps/1024:.0f} KB)")
    print(f"  矢量线稿: {vector_path} ({vs/1024:.0f} KB)")

    return pencil_path, vector_path


# ============================================================
# 批量出图
# ============================================================
if __name__ == "__main__":
    # 已有照片
    photos = {
        "D0601_chert":       "output/D0601_outcrop.jpg",
        "D0605_stromatolite": "output/D0605_outcrop.jpg",
    }

    for name, path in photos.items():
        geo_sketch(path, "output/sketches", name)

    print("\n完成，输出目录: output/sketches/")
