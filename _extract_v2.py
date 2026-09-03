# -*- coding: utf-8 -*-
"""
V2: Smarter terrain extraction.
Problem: simple "first dark pixel" picks up text labels, annotations.
Solution: find the dominant continuous dark feature in upper portion.
"""
from PIL import Image
import numpy as np
import json

img = Image.open(r"E:\成长日志\大三上\周口店大报告图片\1.png").convert("L")
arr = np.array(img).astype(float)
h, w = arr.shape

# Step 1: Invert so dark=high, then find "ridgeline" of darkness
# The terrain is a dark line on light background.
# For each column, don't just take first dark pixel.
# Instead, find the first RUN of dark pixels (at least 3 consecutive).

MIN_RUN = 3
THRESHOLD = 150  # below this = dark

terrain = []
for x in range(w):
    col = arr[:, x]
    dark_mask = col < THRESHOLD

    # Find runs of dark pixels
    found = False
    i = 0
    while i < h:
        if dark_mask[i]:
            run_start = i
            while i < h and dark_mask[i]:
                i += 1
            run_len = i - run_start
            if run_len >= MIN_RUN:
                # Take the TOP of this run (closest to top of image)
                terrain.append((x, run_start))
                found = True
                break
        else:
            i += 1
    if not found:
        terrain.append(None)  # gap

# Step 2: Fill gaps with interpolation
# Convert Nones to NaN for interpolation-friendly format
xs_all = list(range(w))
ys_raw = np.array([t[1] if t else np.nan for t in terrain], dtype=float)

# Step 3: The terrain should be roughly in the upper 40% of the image
# Filter out points that are too low (likely text or other lines)
# First, get a rough estimate of where terrain should be
valid_ys = ys_raw[~np.isnan(ys_raw)]
if len(valid_ys) > 0:
    y_median = np.median(valid_ys)
    y_mad = np.median(np.abs(valid_ys - y_median)) * 1.4826  # robust std

    # Mark points too far from median as outliers
    for i in range(len(ys_raw)):
        if not np.isnan(ys_raw[i]):
            if abs(ys_raw[i] - y_median) > 5 * y_mad:
                ys_raw[i] = np.nan

# Step 4: Interpolate across gaps
valid_mask = ~np.isnan(ys_raw)
if valid_mask.sum() > 2:
    from scipy.interpolate import interp1d
    f = interp1d(np.where(valid_mask)[0], ys_raw[valid_mask],
                 kind='linear', fill_value='extrapolate')
    ys_interp = f(np.arange(w))
else:
    ys_interp = ys_raw.copy()

# Step 5: Smooth (moving average)
window = 11
kernel = np.ones(window) / window
ys_smooth = np.convolve(ys_interp, kernel, mode='same')

# Restore edges
ys_smooth[:window//2] = ys_interp[:window//2]
ys_smooth[-window//2:] = ys_interp[-window//2:]

# Step 6: Scale to meters
# Image is 870x517 pixels.
# From Qwen-VL: section is ~800m long horizontally, x-axis corresponds to image width
# Vertical: estimate ~100m total relief
pixels_to_m_x = 800.0 / w  # meters per pixel horizontally
pixels_to_m_y = 100.0 / (ys_smooth.max() - ys_smooth.min())  # scale so relief = ~100m

# But we want y increasing upward (image y increases downward)
y_min_img = ys_smooth.min()
terrain_meters = []
for x in range(w):
    x_m = x * pixels_to_m_x
    y_m = (ys_smooth[x] - y_min_img) * pixels_to_m_y + 200  # base elevation ~200m
    terrain_meters.append((round(x_m, 1), round(y_m, 1)))

# Step 7: Downsample (too many points for CAD)
step = max(1, len(terrain_meters) // 60)  # ~60 points
terrain_simplified = terrain_meters[::step]
if terrain_simplified[-1] != terrain_meters[-1]:
    terrain_simplified.append(terrain_meters[-1])

# Save
with open("d:/geointern-agent/output/terrain_meters.json", "w") as f:
    json.dump(terrain_simplified, f, ensure_ascii=False)

print(f"Extracted: {len(terrain_simplified)} terrain points")
print(f"X range: {terrain_simplified[0][0]:.0f} - {terrain_simplified[-1][0]:.0f} m")
print(f"Y range: {min(p[1] for p in terrain_simplified):.0f} - {max(p[1] for p in terrain_simplified):.0f} m")

# Preview
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 2, figsize=(16, 10))
ax1, ax2, ax3, ax4 = axes.flatten()

# (1) Raw extraction
ax1.set_title('1. Raw extraction')
for x, t in enumerate(terrain):
    if t:
        ax1.plot(x, t[1], 'k.', markersize=0.5)
ax1.invert_yaxis()

# (2) After outlier removal + interpolation
ax2.set_title('2. Cleaned + interpolated')
ax2.plot(xs_all, ys_smooth, 'b-', linewidth=1)
ax2.invert_yaxis()

# (3) Overlay on original (upper portion zoom)
ax3.set_title('3. Overlay on original')
ax3.imshow(arr, cmap='gray')
ax3.plot(xs_all, ys_smooth, 'r-', linewidth=1.5, alpha=0.7)
ax3.set_ylim(0, h//2)
ax3.invert_yaxis()

# (4) Final terrain in meters
tx = [p[0] for p in terrain_simplified]
ty = [p[1] for p in terrain_simplified]
ax4.set_title('4. Final terrain (meters)')
ax4.plot(tx, ty, 'g-', linewidth=2)
ax4.fill_between(tx, ty, min(ty)-20, alpha=0.3, color='green')
ax4.set_xlabel('Distance (m)')
ax4.set_ylabel('Elevation (m)')
ax4.set_aspect('equal')

plt.tight_layout()
plt.savefig("d:/geointern-agent/output/terrain_v2.png", dpi=150)
print("Preview saved: terrain_v2.png")
