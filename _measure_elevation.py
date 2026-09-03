# -*- coding: utf-8 -*-
"""
用图上水平比例尺作标尺，量测地形线的高程。
原理：水平比例尺标注"20 40m" -> 量像素长 -> px/m换算 -> 应用到垂直方向
"""
from PIL import Image
import numpy as np
import json

img = Image.open(r"E:\成长日志\大三上\周口店大报告图片\1.png").convert("L")
arr = np.array(img)
h, w = arr.shape
print(f"Image: {w}x{h}")

# ═══ Step 1: 找到比例尺 ═══
# 比例尺在底部，是一条水平线段 + "20 40m"文字
# 扫描底部区域找最长的水平暗线
bottom_region = arr[int(h*0.75):, :]
dark = bottom_region < 150

# 找水平方向的长连续暗像素（比例尺线）
from collections import Counter
candidate_rows = []
for y_rel in range(bottom_region.shape[0]):
    run = 0
    max_run = 0
    for x in range(w):
        if dark[y_rel, x]:
            run += 1
            max_run = max(max_run, run)
        else:
            run = 0
    if max_run > 50:  # 至少50像素长的水平线
        candidate_rows.append((y_rel + int(h*0.75), max_run))

candidate_rows.sort(key=lambda x: -x[1])
print(f"Top 5 longest horizontal dark runs: {candidate_rows[:5]}")

# ═══ Step 2: 精确量比例尺 ═══
# 人工指定——Qwen-VL说比例尺标注"20 40m"，线段两端约代表0到40m
# 我们需要知道比例尺线段起止像素位置

# 找底部最长的水平线段
scale_y = None
scale_x_start = None
scale_x_end = None

for y_abs, run_len in candidate_rows[:3]:
    # 找该行中最长的连续暗像素段
    row_data = arr[y_abs, :]
    dark_row = row_data < 150

    best_start, best_len = 0, 0
    i = 0
    while i < w:
        if dark_row[i]:
            start = i
            while i < w and dark_row[i]:
                i += 1
            length = i - start
            if length > best_len:
                best_start, best_len = start, length
        else:
            i += 1

    if best_len > 100:  # 比例尺应该很长
        scale_y = y_abs
        # 找比例尺线段的确切端点
        # 扩到线段两端暗色交界处
        scale_x_start = best_start
        scale_x_end = best_start + best_len
        print(f"Scale bar found: y={scale_y}, x={scale_x_start}-{scale_x_end}, length={best_len}px")
        break

if scale_x_start is None:
    # Fallback: 假设比例尺在底部约85%的位置，宽度约40%的图像宽度
    scale_x_start = int(w * 0.15)
    scale_x_end = int(w * 0.55)
    scale_y = int(h * 0.88)
    print(f"Scale bar FALLBACK: y={scale_y}, x={scale_x_start}-{scale_x_end}")

scale_px = scale_x_end - scale_x_start
# 比例尺标注"20 40m" — 线段0-20-40m，总长40m
scale_meters = 40.0
px_per_m = scale_px / scale_meters
print(f"Scale: {scale_px}px = {scale_meters}m, {px_per_m:.2f} px/m")

# ═══ Step 3: 提取地形线并换算高程 ═══
# 改进的地形提取：找最上方的连续暗线
THRESHOLD = 150
MIN_RUN = 3

terrain_px = []
for x in range(w):
    col = arr[:, x]
    dark_mask = col < THRESHOLD
    found = False
    i = 0
    while i < h:
        if dark_mask[i]:
            run_start = i
            while i < h and dark_mask[i]:
                i += 1
            if (i - run_start) >= MIN_RUN:
                terrain_px.append((x, run_start))
                found = True
                break
        else:
            i += 1
    if not found:
        terrain_px.append(None)

# 清理异常点
ys_raw = np.array([t[1] if t else np.nan for t in terrain_px], dtype=float)
valid_mask = ~np.isnan(ys_raw)

if valid_mask.sum() > 0:
    # 地形线应在上半部分（y < h*0.6）
    # 过滤太低的点（可能是图例、文字等）
    for i in range(len(ys_raw)):
        if not np.isnan(ys_raw[i]) and ys_raw[i] > h * 0.65:
            ys_raw[i] = np.nan

    # 二次过滤：中位数附近的点
    valid_ys = ys_raw[~np.isnan(ys_raw)]
    y_med = np.median(valid_ys)
    y_std = np.std(valid_ys)
    for i in range(len(ys_raw)):
        if not np.isnan(ys_raw[i]):
            if abs(ys_raw[i] - y_med) > 4 * y_std:
                ys_raw[i] = np.nan

# 插值 + 平滑
valid_mask = ~np.isnan(ys_raw)
if valid_mask.sum() > 2:
    from scipy.interpolate import interp1d
    valid_idx = np.where(valid_mask)[0]
    f = interp1d(valid_idx, ys_raw[valid_mask], kind='linear', fill_value='extrapolate')
    ys_interp = f(np.arange(w))

    # 平滑
    window = 15
    kernel = np.ones(window) / window
    ys_smooth = np.convolve(ys_interp, kernel, mode='same')
    ys_smooth[:window] = ys_interp[:window]
    ys_smooth[-window:] = ys_interp[-window:]
else:
    print("ERROR: not enough valid terrain points")
    exit(1)

# ═══ Step 4: 换算为实际高程 ═══
# 垂直方向也用同样的 px/m（假设无垂直放大）
# 高程基准：区域高程150-300m，曲线最低点 ~150m
y_min_px = np.nanmin(ys_smooth)
y_max_px = np.nanmax(ys_smooth)
relief_px = y_max_px - y_min_px
relief_m = relief_px / px_per_m
print(f"Relief: {relief_px:.0f}px = {relief_m:.1f}m")

# 用区域已知高程范围约束
# 报告: "高程一般为150-300m"
# 设剖面最低点海拔 ~150m
BASE_ELEV = 150.0

# 降采样到60个点
step = max(1, w // 60)
terrain_meters = []
for x in range(0, w, step):
    x_m = x / px_per_m  # 水平距离
    elev_m = BASE_ELEV + (y_max_px - ys_smooth[x]) / px_per_m  # 反转y轴（图上y向下）
    terrain_meters.append((round(x_m, 1), round(elev_m, 1)))

# 确保最后一个点
x_last = w - 1
x_last_m = x_last / px_per_m
elev_last_m = BASE_ELEV + (y_max_px - ys_smooth[x_last]) / px_per_m
if abs(terrain_meters[-1][0] - x_last_m) > 5:
    terrain_meters.append((round(x_last_m, 1), round(elev_last_m, 1)))

# 保存
with open("d:/geointern-agent/output/terrain_calibrated.json", "w") as f:
    json.dump(terrain_meters, f, ensure_ascii=False)

print(f"Terrain points: {len(terrain_meters)}")
print(f"X: {terrain_meters[0][0]:.0f} - {terrain_meters[-1][0]:.0f} m")
print(f"Elev: {min(p[1] for p in terrain_meters):.0f} - {max(p[1] for p in terrain_meters):.0f} m")

# 预览
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 2, figsize=(16, 10))
ax1, ax2, ax3, ax4 = axes.flatten()

# (1) 比例尺位置
ax1.imshow(arr, cmap='gray')
ax1.axhline(y=scale_y, color='r', linewidth=1)
ax1.axvline(x=scale_x_start, color='r', linewidth=0.5)
ax1.axvline(x=scale_x_end, color='r', linewidth=0.5)
ax1.set_title(f'1. Scale bar location (red line, {scale_px}px = {scale_meters}m)')
ax1.invert_yaxis()

# (2) 原始提取
ax2.set_title('2. Raw terrain (after cleanup)')
for x, t in enumerate(terrain_px):
    if t:
        ax2.plot(x, t[1], 'k.', markersize=0.3)
ax2.invert_yaxis()

# (3) 平滑后
ax3.set_title('3. Smoothed terrain')
ax3.plot(range(w), ys_smooth, 'b-', linewidth=1)
ax3.invert_yaxis()

# (4) 最终高程
tx = [p[0] for p in terrain_meters]
ty = [p[1] for p in terrain_meters]
ax4.set_title('4. Calibrated elevation profile')
ax4.plot(tx, ty, 'g-', linewidth=2)
ax4.fill_between(tx, ty, min(ty)-10, alpha=0.2, color='green')
ax4.set_xlabel('Distance (m)')
ax4.set_ylabel('Elevation (m)')
ax4.set_aspect('equal')

plt.tight_layout()
plt.savefig("d:/geointern-agent/output/elevation_calibrated.png", dpi=150)
print("Preview saved: elevation_calibrated.png")
