"""D0605 包心菜状叠层石 照片→素描线稿"""

import vtracer
import cv2
import numpy as np
import os

PHOTO = "output/D0605_outcrop.jpg"
OUT_DIR = "output/sketch_test/D0605"
os.makedirs(OUT_DIR, exist_ok=True)

img = cv2.imread(PHOTO)
if img is None:
    print("读取图片失败")
    exit(1)

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blurred = cv2.bilateralFilter(gray, 9, 75, 75)

# ---- Canny 高阈值 (主干线条) ----
print("Canny high...")
edges_high = cv2.Canny(blurred, 50, 150)
cv2.imwrite(f"{OUT_DIR}/canny_high.png", edges_high)
vtracer.convert_image_to_svg_py(
    f"{OUT_DIR}/canny_high.png",
    f"{OUT_DIR}/canny_high.svg",
    colormode="binary", corner_threshold=45, mode="spline",
)

# ---- Canny 低阈值 (更多细节) ----
print("Canny low...")
edges_low = cv2.Canny(blurred, 30, 90)
cv2.imwrite(f"{OUT_DIR}/canny_low.png", edges_low)
vtracer.convert_image_to_svg_py(
    f"{OUT_DIR}/canny_low.png",
    f"{OUT_DIR}/canny_low.svg",
    colormode="binary", corner_threshold=45, mode="spline",
)

# ---- Sobel ----
print("Sobel...")
sobelx = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=3)
sobely = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=3)
sobel = np.sqrt(sobelx**2 + sobely**2)
sobel = np.uint8(255 * sobel / sobel.max())
_, sobel_bin = cv2.threshold(sobel, 60, 255, cv2.THRESH_BINARY)
cv2.imwrite(f"{OUT_DIR}/sobel.png", sobel_bin)
vtracer.convert_image_to_svg_py(
    f"{OUT_DIR}/sobel.png",
    f"{OUT_DIR}/sobel.svg",
    colormode="binary", corner_threshold=45, mode="spline",
)

# ---- VTracer binary 原图 ----
print("VTracer binary...")
vtracer.convert_image_to_svg_py(
    PHOTO,
    f"{OUT_DIR}/vtracer_binary.svg",
    colormode="binary", corner_threshold=60, mode="spline",
)

print(f"\n完成 → {OUT_DIR}/")
for f in sorted(os.listdir(OUT_DIR)):
    size = os.path.getsize(f"{OUT_DIR}/{f}")
    print(f"  {f} ({size/1024:.0f} KB)")
