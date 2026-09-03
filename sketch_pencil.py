"""OpenCV 铅笔素描 — dodge-blend + pencilSketch 对比"""

import cv2
import numpy as np
import os

def dodge_blend(gray, blur_ksize=21):
    """经典 dodge-blend 铅笔素描"""
    inverted = 255 - gray
    blurred = cv2.GaussianBlur(inverted, (blur_ksize, blur_ksize), 0)
    result = cv2.divide(gray, 255 - blurred, scale=256.0)
    return result


def pencil_sketch_manual(img_path, out_dir, name):
    """多组参数: 不同模糊核 → 不同笔触粗细"""
    os.makedirs(out_dir, exist_ok=True)
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 轻微降噪
    gray = cv2.bilateralFilter(gray, 7, 50, 50)

    # dodge-blend 三组笔触
    for ksize, label in [(11, "fine"), (21, "medium"), (31, "bold")]:
        sketch = dodge_blend(gray, ksize)
        cv2.imwrite(f"{out_dir}/dodge_{label}.png", sketch)

    # OpenCV 内置 pencilSketch
    gray_out, color_out = cv2.pencilSketch(img, sigma_s=60, sigma_r=0.07, shade_factor=0.05)
    cv2.imwrite(f"{out_dir}/cv2_pencil_gray.png", gray_out)
    cv2.imwrite(f"{out_dir}/cv2_pencil_color.png", color_out)

    # pencilSketch 变体 — 更深的笔触
    gray_out2, _ = cv2.pencilSketch(img, sigma_s=40, sigma_r=0.05, shade_factor=0.03)
    cv2.imwrite(f"{out_dir}/cv2_pencil_dark.png", gray_out2)

    # 混合: Canny 边缘 + dodge-blend 纹理 (结构线条 + 铅笔质感)
    edges = cv2.Canny(gray, 40, 120)
    edge_dilated = cv2.dilate(edges, None, iterations=1)
    sketch_base = dodge_blend(gray, 21)
    # 把边缘叠加到素描上
    combined = sketch_base.copy()
    combined[edge_dilated > 0] = 0  # 边缘位置加深
    cv2.imwrite(f"{out_dir}/canny_overlay.png", combined)

    # 打印文件大小
    for f in sorted(os.listdir(out_dir)):
        size = os.path.getsize(f"{out_dir}/{f}")
        print(f"  {f} ({size/1024:.0f} KB)")


print("=== D0601 燧石条带 ===")
pencil_sketch_manual("output/D0601_outcrop.jpg", "output/sketch_test/D0601_pencil", "D0601")

print("\n=== D0605 叠层石 ===")
pencil_sketch_manual("output/D0605_outcrop.jpg", "output/sketch_test/D0605_pencil", "D0605")
