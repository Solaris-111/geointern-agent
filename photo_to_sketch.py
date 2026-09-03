"""照片 → 地质素描线稿 管线测试
VTracer + Canny预处理, 对比多种模式"""

import vtracer
import cv2
import numpy as np
import os

PHOTO = "output/D0601_outcrop.jpg"
OUT_DIR = "output/sketch_test"
os.makedirs(OUT_DIR, exist_ok=True)

# ============================================================
# 方案1: VTracer binary 模式直接用原图
# ============================================================
print("方案1: VTracer binary 原图...")
vtracer.convert_image_to_svg_py(
    PHOTO,
    f"{OUT_DIR}/1_vtracer_binary.svg",
    colormode="binary",
    corner_threshold=60,
    mode="spline",
)

# ============================================================
# 方案2: Canny 边缘检测 → 二值化 → VTracer
# ============================================================
print("方案2: Canny → VTracer...")
img = cv2.imread(PHOTO)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 自适应阈值预处理
blurred = cv2.bilateralFilter(gray, 9, 75, 75)

# Canny 边缘检测
edges_low = cv2.Canny(blurred, 30, 90)
cv2.imwrite(f"{OUT_DIR}/2_canny_low.png", edges_low)

edges_high = cv2.Canny(blurred, 50, 150)
cv2.imwrite(f"{OUT_DIR}/2_canny_high.png", edges_high)

vtracer.convert_image_to_svg_py(
    f"{OUT_DIR}/2_canny_high.png",
    f"{OUT_DIR}/2_canny_vtracer_high.svg",
    colormode="binary",
    corner_threshold=45,
    mode="polygon",
)

# ============================================================
# 方案3: 自适应阈值 → 二值化 → VTracer
# ============================================================
print("方案3: 自适应阈值 → VTracer...")
thresh = cv2.adaptiveThreshold(
    blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    cv2.THRESH_BINARY, 11, 2)
cv2.imwrite(f"{OUT_DIR}/3_adaptive.png", thresh)

vtracer.convert_image_to_svg_py(
    f"{OUT_DIR}/3_adaptive.png",
    f"{OUT_DIR}/3_adaptive_vtracer.svg",
    colormode="binary",
    corner_threshold=50,
    mode="spline",
)

# ============================================================
# 方案4: Sobel 梯度 → VTracer
# ============================================================
print("方案4: Sobel → VTracer...")
sobelx = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=3)
sobely = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=3)
sobel = np.sqrt(sobelx**2 + sobely**2)
sobel = np.uint8(255 * sobel / sobel.max())
_, sobel_bin = cv2.threshold(sobel, 60, 255, cv2.THRESH_BINARY)
cv2.imwrite(f"{OUT_DIR}/4_sobel.png", sobel_bin)

vtracer.convert_image_to_svg_py(
    f"{OUT_DIR}/4_sobel.png",
    f"{OUT_DIR}/4_sobel_vtracer.svg",
    colormode="binary",
    corner_threshold=45,
    mode="spline",
)

# ============================================================
# 汇总
# ============================================================
print(f"\n完成！输出在 {OUT_DIR}/")
for f in sorted(os.listdir(OUT_DIR)):
    size = os.path.getsize(f"{OUT_DIR}/{f}")
    print(f"  {f} ({size/1024:.0f} KB)")
