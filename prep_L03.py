"""L03 黄院东山梁 — Day2 准备
1. 地形剖面 (KML → DEM)
2. 图3-2 府君山组平卧褶皱
3. 图3-3 黄院组等斜平卧褶皱
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import math
import csv
import os

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

OUT = "output/L03_prep"
os.makedirs(OUT, exist_ok=True)


# ============================================================
# 1. 地形剖面
# ============================================================
def load_l03_terrain():
    csv_path = "output/L03_黄院东山梁_profile.csv"
    dists, elevs = [], []
    with open(csv_path, "r", encoding="utf-8") as f:
        for row in csv.reader(f):
            try:
                dists.append(float(row[2]) / 1000)
                elevs.append(float(row[3]))
            except (ValueError, IndexError):
                continue
    return dists, elevs

dists, elevs = load_l03_terrain()
max_dist = dists[-1]
max_e = max(elevs)

# 观察点 (从 KML + 预稿)
# 修正后点位 (距离km, 海拔m从CSV最近采样点读取)
obs_points = [
    (0.000, None, "D0301", "QbC 岩性控制点\n(239高地)"),
    (0.694, None, "D0302", "QbC/QxJ 界线"),
    (0.820, None, "D0303", "QxJ/∈1f 平行不整合\n(房山运动)"),
    (0.924, None, "D0304", "∈1f/∈1+2m 界线"),
    (0.955, None, "D0305", "∈1+2m/∈2x 界线"),
    (1.017, None, "D0306", "∈2x/∈2z 界线"),
    (1.329, None, "D0307", "∈2z/∈2h 界线\n(等斜平卧褶皱)"),
    (1.391, None, "D0308", "∈2h/O1y 界线"),
    (1.487, None, "D0309", "O1y/O1l 界线"),
]

# 从 CSV 查找各点海拔
import csv
csv_dists, csv_elevs = [], []
with open("output/L03_黄院东山梁_profile.csv", "r") as f:
    for row in csv.reader(f):
        try:
            csv_dists.append(float(row[2]) / 1000)
            csv_elevs.append(float(row[3]))
        except (ValueError, IndexError):
            continue

obs_points_fixed = []
for dist, _, pid, ptype in obs_points:
    idx = min(range(len(csv_dists)), key=lambda i: abs(csv_dists[i] - dist))
    elev = csv_elevs[idx]
    obs_points_fixed.append((dist, elev, pid, ptype))
obs_points = obs_points_fixed

fig, ax = plt.subplots(figsize=(16, 5))
ax.fill_between(dists, elevs, 0, alpha=0.18, color="#6b8e5a")
ax.plot(dists, elevs, color="#3d5a2e", linewidth=1.2, zorder=3)

for dist, elev, pid, ptype in obs_points:
    is_unc = "不整合" in ptype
    color = "#c0392b" if is_unc else "#1a1a2e"
    marker = 's' if is_unc else 'o'
    ax.plot(dist, elev, marker=marker, color=color, markersize=8, zorder=5)
    ax.annotate(f"{pid}\n{ptype}", (dist, elev),
               xytext=(0, 22), textcoords="offset points",
               fontsize=6.5, fontweight="bold", color=color, ha="center", zorder=10)

ax.set_xlabel("距离 (km)", fontsize=11, fontweight="bold")
ax.set_ylabel("海拔 (m)", fontsize=11, fontweight="bold")
ax.set_title("L03 黄院东山梁 地形剖面 (探矿所→239→285→281→探槽→探矿所)",
             fontsize=12, fontweight="bold")
ax.set_xlim(0, max_dist)
ax.set_ylim(0, max_e + 60)
ax.grid(True, alpha=0.2, linestyle="--")
plt.tight_layout()
fig.savefig(f"{OUT}/L03_terrain_profile.png", dpi=200, bbox_inches="tight")
plt.close()
print("1/3 地形剖面完成")


# ============================================================
# 2. 图3-2 府君山组大型平卧褶皱 (D0303)
# ============================================================
def draw_recumbent_fold(ax, cx, cy, scale, label, axial_dd, axial_da, hinge_dd, hinge_da,
                        limb1_dd, limb1_da, limb2_dd, limb2_da, formation, location):
    """画平卧褶皱构造示意图"""

    # 轴面 — 近水平 (平卧褶皱特征)
    ap_rad = math.radians(90 - axial_da) if axial_da < 45 else math.radians(10)
    ap_dx = 3.5 * scale * math.cos(ap_rad)
    ap_dy = 3.5 * scale * math.sin(ap_rad)

    # 轴面迹线 (红色虚线)
    ax.plot([cx - ap_dx, cx + ap_dx], [cy - ap_dy, cy + ap_dy],
            color="#e74c3c", linewidth=2.0, linestyle="--", zorder=4)

    # 褶皱形态 — 平卧褶皱: 轴面近水平, 两翼近水平但方向相反
    # 用正弦波叠加在轴面上
    t = np.linspace(-2.8, 2.8, 100)
    fold_amp = 0.8 * scale
    fold_wavelength = 2.0 * scale

    # 沿轴面的坐标
    x_axial = cx + t * scale * math.cos(ap_rad)
    y_axial = cy + t * scale * math.sin(ap_rad)

    # 垂直轴面的偏移 (褶皱形态)
    perp_angle = ap_rad + math.pi / 2
    fold_offset = fold_amp * np.sin(t * 2.5)

    # 核部地层线 (背斜形态)
    x_fold = x_axial + fold_offset * math.cos(perp_angle)
    y_fold = y_axial + fold_offset * math.sin(perp_angle)

    # 画多条地层线表示褶皱形态
    for j, (offset_mult, alpha_val, lw_val, color_val) in enumerate([
        (-1.0, 0.3, 1.2, "#8b7355"),
        (-0.5, 0.5, 1.5, "#6b5b3a"),
        (0.0, 0.7, 2.0, "#3a2a1a"),
        (0.5, 0.5, 1.5, "#6b5b3a"),
        (1.0, 0.3, 1.2, "#8b7355"),
    ]):
        offset = offset_mult * 0.4 * scale
        x_layer = x_axial + (fold_offset + offset) * math.cos(perp_angle)
        y_layer = y_axial + (fold_offset + offset) * math.sin(perp_angle)
        ax.plot(x_layer, y_layer, color=color_val, linewidth=lw_val, alpha=alpha_val, zorder=3)

    # 轴面标签
    ax.annotate(f"轴面: {axial_dd}°∠{axial_da}°",
                (cx + ap_dx * 0.6, cy + ap_dy * 0.6 + 1.2),
                fontsize=8, color="#c0392b", fontweight="bold", ha="center",
                bbox=dict(facecolor="white", edgecolor="#e74c3c", alpha=0.9))

    # 枢纽标签
    ax.annotate(f"枢纽: {hinge_dd}°∠{hinge_da}°",
                (cx + 2.0, cy + 0.5),
                fontsize=7.5, color="#e67e22", fontweight="bold", ha="center",
                bbox=dict(facecolor="white", edgecolor="#e67e22", alpha=0.9))

    # 两翼产状
    ax.annotate(f"SE翼: {limb1_dd}°∠{limb1_da}°",
                (cx - 2.5, cy - 1.5), fontsize=7, color="#2c3e50",
                bbox=dict(facecolor="white", edgecolor="#aaa", alpha=0.85))
    ax.annotate(f"NW翼: {limb2_dd}°∠{limb2_da}°",
                (cx + 1.5, cy + 1.8), fontsize=7, color="#2c3e50",
                bbox=dict(facecolor="white", edgecolor="#aaa", alpha=0.85))

    # 构造要素
    ax.text(cx, cy - 2.5, f"{formation}\n{location}",
            fontsize=8, fontweight="bold", ha="center", color="#1a1a1a",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#faf5eb", edgecolor="#8b7355"))


fig2, ax2 = plt.subplots(figsize=(10, 7))
ax2.set_xlim(-6, 6)
ax2.set_ylim(-6, 6)
ax2.set_aspect("equal")
ax2.axis("off")

draw_recumbent_fold(
    ax2, cx=0, cy=0.5, scale=1.5,
    label="图3-2",
    axial_dd=341, axial_da=27.9,
    hinge_dd=105.1, hinge_da=18.5,
    limb1_dd=43.9, limb1_da=34.7,
    limb2_dd=69.4, limb2_da=22.3,
    formation="府君山组 (∈1f)\n豹皮灰岩 + 纹带灰岩",
    location="D0303 采坑处"
)

ax2.set_title("图3-2  府君山组大型平卧褶皱素描图", fontsize=14, fontweight="bold", pad=10)
ax2.text(0, -4.8, "D0303  黄院东山梁 239高地北东80° | 轴面 341°∠27.9°  枢纽 105.1°∠18.5°",
         ha="center", fontsize=8, color="#888")

# 指北针 + 比例尺
ax2.plot([4.5, 4.5], [-5, -4.2], color="black", linewidth=1.5)
ax2.plot([4.5, 4.2], [-5, -4.6], color="black", linewidth=1)
ax2.plot([4.5, 4.8], [-5, -4.6], color="black", linewidth=1)
ax2.text(4.5, -4.05, "N", ha="center", fontsize=9, fontweight="bold")

fig2.tight_layout()
fig2.savefig(f"{OUT}/图3-2_府君山组平卧褶皱.png", dpi=250, bbox_inches="tight", facecolor="white")
plt.close()
print("2/3 平卧褶皱完成")


# ============================================================
# 3. 图3-3 黄院组等斜平卧褶皱 (D0307)
# ============================================================
fig3, ax3 = plt.subplots(figsize=(10, 7))
ax3.set_xlim(-6, 6)
ax3.set_ylim(-6, 6)
ax3.set_aspect("equal")
ax3.axis("off")

# 等斜褶皱特征: 两翼平行, 轴面倾角更缓
cx3, cy3 = 0, 0.5

# 轴面 (更缓 — 等斜平卧)
ap_rad3 = math.radians(90 - 24)  # 轴面倾角24°
ap_dx3 = 3.5 * 1.5 * math.cos(ap_rad3)
ap_dy3 = 3.5 * 1.5 * math.sin(ap_rad3)
ax3.plot([cx3 - ap_dx3, cx3 + ap_dx3], [cy3 - ap_dy3, cy3 + ap_dy3],
         color="#e74c3c", linewidth=2.0, linestyle="--", zorder=4)

# 等斜褶皱 — 两翼近平行, 同方向倾斜
t3 = np.linspace(-2.8, 2.8, 100)
x_axial3 = cx3 + t3 * 1.5 * math.cos(ap_rad3)
y_axial3 = cy3 + t3 * 1.5 * math.sin(ap_rad3)
perp3 = ap_rad3 + math.pi / 2

# 等斜形态: 更紧的褶皱
fold_offset3 = 0.5 * 1.5 * np.sin(t3 * 2.0)
# 让两翼更平行
fold_offset3 = fold_offset3 * (1 + 0.6 * np.abs(np.cos(t3 * 1.5)))

for j, (om, a, lw, c) in enumerate([
    (-1.0, 0.3, 1.2, "#8b7b65"),
    (-0.5, 0.5, 1.5, "#6b5b45"),
    (0.0, 0.7, 2.0, "#3a2a1a"),
    (0.5, 0.5, 1.5, "#6b5b45"),
    (1.0, 0.3, 1.2, "#8b7b65"),
]):
    off = om * 0.3 * 1.5
    xl = x_axial3 + (fold_offset3 + off) * math.cos(perp3)
    yl = y_axial3 + (fold_offset3 + off) * math.sin(perp3)
    ax3.plot(xl, yl, color=c, linewidth=lw, alpha=a, zorder=3)

# 标注
ax3.annotate("轴面: 41°∠24°",
             (cx3 + ap_dx3 * 0.55, cy3 + ap_dy3 * 0.55 + 1.2),
             fontsize=9, color="#c0392b", fontweight="bold", ha="center",
             bbox=dict(facecolor="white", edgecolor="#e74c3c", alpha=0.9))
ax3.annotate("枢纽: 95°∠6°",
             (cx3 + 2.0, cy3), fontsize=8, color="#e67e22", fontweight="bold",
             ha="center",
             bbox=dict(facecolor="white", edgecolor="#e67e22", alpha=0.9))
ax3.annotate("SE翼 ∥ NW翼\n(等斜特征)",
             (cx3 - 1.8, cy3 + 2.0), fontsize=8, color="#2c3e50", ha="center",
             bbox=dict(boxstyle="round,pad=0.3", facecolor="#faf5eb", edgecolor="#8b7355"))
ax3.text(cx3, cy3 - 2.5, "黄院组 (∈2h)\n泥质条带灰岩",
         fontsize=8, fontweight="bold", ha="center", color="#1a1a1a",
         bbox=dict(boxstyle="round,pad=0.3", facecolor="#faf5eb", edgecolor="#8b7355"))

ax3.set_title("图3-3  黄院组等斜平卧褶皱素描图", fontsize=14, fontweight="bold", pad=10)
ax3.text(0, -4.8, "D0307  281高地北东45°垭口 | 轴面 41°∠24°  枢纽 95°∠6°",
         ha="center", fontsize=8, color="#888")

ax3.plot([4.5, 4.5], [-5, -4.2], color="black", linewidth=1.5)
ax3.plot([4.5, 4.2], [-5, -4.6], color="black", linewidth=1)
ax3.plot([4.5, 4.8], [-5, -4.6], color="black", linewidth=1)
ax3.text(4.5, -4.05, "N", ha="center", fontsize=9, fontweight="bold")

fig3.tight_layout()
fig3.savefig(f"{OUT}/图3-3_黄院组等斜平卧褶皱.png", dpi=250, bbox_inches="tight", facecolor="white")
plt.close()
print("3/3 等斜平卧褶皱完成")

print(f"\n全部完成 → {OUT}/")
for f in sorted(os.listdir(OUT)):
    print(f"  {f} ({os.path.getsize(os.path.join(OUT,f))/1024:.0f} KB)")
