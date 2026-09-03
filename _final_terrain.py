# -*- coding: utf-8 -*-
"""
Final terrain extraction with calibrated scale.
Scale bar: 3 ticks at x=175, 274, 373 px, spacing 99px = 20m
Scale: 4.95 px/m, applied equally to horizontal AND vertical (no V.E.)
"""
from PIL import Image
import numpy as np
import json

PX_PER_M = 4.95  # calibrated from "20 40m" scale bar

img = Image.open(r"E:\成长日志\大三上\周口店大报告图片\1.png").convert("L")
arr = np.array(img)
h, w = arr.shape

# Extract terrain (improved: topmost dark run, filtered)
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

ys_raw = np.array([t[1] if t else np.nan for t in terrain_px], dtype=float)

# Filter: terrain should be in upper portion (y < h*0.65)
valid_ys = ys_raw[~np.isnan(ys_raw)]
y_med = np.median(valid_ys)
y_std = np.std(valid_ys)
for i in range(len(ys_raw)):
    if not np.isnan(ys_raw[i]):
        if ys_raw[i] > h * 0.65 or abs(ys_raw[i] - y_med) > 4 * y_std:
            ys_raw[i] = np.nan

# Interpolate + smooth
valid_mask = ~np.isnan(ys_raw)
from scipy.interpolate import interp1d
valid_idx = np.where(valid_mask)[0]
f = interp1d(valid_idx, ys_raw[valid_mask], kind='linear', fill_value='extrapolate')
ys_interp = f(np.arange(w))

window = 15
kernel = np.ones(window) / window
ys_smooth = np.convolve(ys_interp, kernel, mode='same')
ys_smooth[:window] = ys_interp[:window]
ys_smooth[-window:] = ys_interp[-window:]

# Convert to meters using calibrated scale
# y increases downward in image -> need to flip
y_top_px = ys_smooth.min()
y_bottom_px = ys_smooth.max()

# Area elevation: 150-300m. Set lowest point to ~155m
# Highest point = lowest + relief_px / PX_PER_M
BASE_ELEV = 155.0
relief_m = (y_bottom_px - y_top_px) / PX_PER_M
y_max_elev = BASE_ELEV + relief_m
print(f"Terrain: {y_top_px:.0f}-{y_bottom_px:.0f} px, relief = {relief_m:.1f}m")
print(f"Elevation range: {BASE_ELEV:.0f}-{y_max_elev:.0f}m")

# Downsample for CAD (50-60 points)
step = max(1, w // 55)
terrain_pts = []
for x in range(0, w, step):
    x_m = x / PX_PER_M
    elev_m = BASE_ELEV + (y_bottom_px - ys_smooth[x]) / PX_PER_M
    terrain_pts.append((round(x_m, 1), round(elev_m, 1)))

# Ensure last point
x_last = w - 1
terrain_pts.append((round(x_last / PX_PER_M, 1),
                    round(BASE_ELEV + (y_bottom_px - ys_smooth[x_last]) / PX_PER_M, 1)))

with open("d:/geointern-agent/output/terrain_final.json", "w") as f:
    json.dump(terrain_pts, f, ensure_ascii=False)

print(f"Saved {len(terrain_pts)} points")
print(f"X: 0 - {terrain_pts[-1][0]:.0f} m")
print(f"Elev: {min(p[1] for p in terrain_pts)} - {max(p[1] for p in terrain_pts)} m")

# Preview
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Raw + smooth overlay on image
ax1.imshow(arr, cmap='gray')
ax1.plot(range(w), ys_smooth, 'r-', linewidth=1.5, alpha=0.8)
ax1.axhline(y=435, color='cyan', linewidth=0.5)
# mark tick positions
for tx in [175, 274, 373]:
    ax1.axvline(x=tx, color='cyan', linewidth=0.3, linestyle='--')
ax1.set_ylim(h, 0)
ax1.set_title('Terrain line + scale bar (cyan)')

# Final elevation
tx = [p[0] for p in terrain_pts]
ty = [p[1] for p in terrain_pts]
ax2.plot(tx, ty, 'g-', linewidth=2)
ax2.fill_between(tx, ty, min(ty)-5, alpha=0.2, color='green')
ax2.set_xlabel('Distance (m)')
ax2.set_ylabel('Elevation (m)')
ax2.set_title(f'Profile: {len(terrain_pts)} pts, {terrain_pts[-1][0]:.0f}m wide')
ax2.set_aspect('equal')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("d:/geointern-agent/output/terrain_final.png", dpi=150)
print("Preview: terrain_final.png")
