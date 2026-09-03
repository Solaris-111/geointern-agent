# -*- coding: utf-8 -*-
"""
从原图1.png中提取地形线和地层界线位置
使用图像处理追踪黑色线条
"""
from PIL import Image
import numpy as np
import json

img = Image.open(r"E:\成长日志\大三上\周口店大报告图片\1.png").convert("L")
arr = np.array(img)
h, w = arr.shape
print(f"Image size: {w}x{h}")

# 图片是白底黑线 — 提取暗像素
# 地形线是最上面那条连续的暗线
dark = arr < 180

# 对每一列找最上面的暗像素（地形线）
terrain_px = []
for x in range(w):
    dark_rows = np.where(dark[:, x])[0]
    if len(dark_rows) > 0:
        # 找第一个黑色run的起始（跳过孤立噪点）
        # 从顶部开始扫描，找第一个至少有连续3个暗像素的行
        y_top = dark_rows[0]
        terrain_px.append((x, y_top))

print(f"Terrain points extracted: {len(terrain_px)}")

# Convert to plain ints
terrain_px = [(int(x), int(y)) for x, y in terrain_px]

# Save pixel coords
with open("d:/geointern-agent/output/terrain_pixels.json", "w") as f:
    json.dump(terrain_px, f)

# Generate preview
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

ax1.imshow(arr, cmap='gray')
ax1.set_title('Original (grayscale)')
ax1.invert_yaxis()

xs, ys = zip(*terrain_px)
ax2.plot(xs, ys, 'k-', linewidth=1)
ax2.invert_yaxis()
ax2.set_aspect('equal')
ax2.set_title('Extracted terrain line')

plt.tight_layout()
plt.savefig("d:/geointern-agent/output/terrain_extract.png", dpi=150)
print("Extraction preview saved")
