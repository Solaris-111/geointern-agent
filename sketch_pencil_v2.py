"""铅笔素描 v2 — 对比度增强 + 锐化 + 粗笔触"""

import cv2
import numpy as np
import os


def dodge_blend(gray, blur_ksize=31):
    inverted = 255 - gray
    blurred = cv2.GaussianBlur(inverted, (blur_ksize, blur_ksize), 0)
    return cv2.divide(gray, 255 - blurred, scale=256.0)


def sharpen(img, amount=1.5):
    blurred = cv2.GaussianBlur(img, (0, 0), 3)
    return cv2.addWeighted(img, 1.0 + amount, blurred, -amount, 0)


def pipeline(img_path, out_dir, name):
    os.makedirs(out_dir, exist_ok=True)
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # CLAHE 对比度增强
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # 锐化
    sharp = sharpen(enhanced, amount=1.2)

    # 组合1: CLAHE + sharpen → dodge bold
    sketch = dodge_blend(sharp, blur_ksize=31)
    cv2.imwrite(f"{out_dir}/enhanced_sharp_bold.png", sketch)

    # 组合2: 更重锐化
    sharp2 = sharpen(enhanced, amount=2.0)
    sketch2 = dodge_blend(sharp2, blur_ksize=31)
    cv2.imwrite(f"{out_dir}/enhanced_sharp2_bold.png", sketch2)

    # 组合3: CLAHE only → dodge bold
    sketch3 = dodge_blend(enhanced, blur_ksize=31)
    cv2.imwrite(f"{out_dir}/enhanced_bold.png", sketch3)

    # 组合4: 原图 + 极粗笔触 (k=41)
    sketch4 = dodge_blend(gray, blur_ksize=41)
    cv2.imwrite(f"{out_dir}/raw_bold41.png", sketch4)

    # 组合5: CLAHE + 中笔触 (k=21) — 对比看增强效果
    sketch5 = dodge_blend(sharp, blur_ksize=21)
    cv2.imwrite(f"{out_dir}/enhanced_sharp_medium.png", sketch5)

    # 组合6: 纯粗笔触 k=31 原始 (对比基线)
    sketch6 = dodge_blend(gray, blur_ksize=31)
    cv2.imwrite(f"{out_dir}/raw_bold31.png", sketch6)

    for f in sorted(os.listdir(out_dir)):
        size = os.path.getsize(f"{out_dir}/{f}")
        print(f"  {f} ({size/1024:.0f} KB)")


print("=== D0601 ===")
pipeline("output/D0601_outcrop.jpg", "output/sketch_test/D0601_pencil_v2", "D0601")
print("\n=== D0605 ===")
pipeline("output/D0605_outcrop.jpg", "output/sketch_test/D0605_pencil_v2", "D0605")
