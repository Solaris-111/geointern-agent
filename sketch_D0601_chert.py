"""图6-1 D0601 燧石条带先后关系 素描图"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

fig, ax = plt.subplots(figsize=(10, 8))
ax.set_xlim(0, 14)
ax.set_ylim(0, 16)
ax.set_aspect("equal")
ax.axis("off")

# ============================================================
# 岩层 — 碳酸盐岩 (白云岩), 层面向右下缓倾, 层面间距5-10cm
# ============================================================

# 层面线: 从左上到右下, 倾角约30°
dip_angle = np.radians(30)
bedding_lines = []

for i in range(18):
    y0 = 15 - i * 0.9  # 层面间距 ~0.9 (代表5-10cm)
    # 每层面略有起伏
    x_vals = np.linspace(1, 13, 80)
    y_vals = y0 - (x_vals - 1) * np.tan(dip_angle)
    # 加微量波浪模拟手绘
    y_vals += 0.08 * np.sin(x_vals * 3 + i * 0.7) + 0.05 * np.sin(x_vals * 7 + i * 1.3)
    ax.plot(x_vals, y_vals, color="#4a4a4a", linewidth=0.8, alpha=0.7)
    bedding_lines.append((x_vals, y_vals))

# ============================================================
# 第一期燧石条带 — 顺层, 灰白色, 1-2cm厚, 中部偏下位置
# ============================================================

# 沿第5-6条层面之间 (y约10-11)
gen1_positions = [6, 7, 8]  # 对应 bedding 行号
for bi in gen1_positions:
    if bi < len(bedding_lines):
        xv, yv = bedding_lines[bi]
        # 在层面间填充条带
        ax.fill_between(xv, yv - 0.15, yv + 0.05, color="#d5c4a1", alpha=0.7, linewidth=0)
        ax.plot(xv, yv, color="#b8a070", linewidth=1.8, alpha=0.9)
        ax.plot(xv, yv - 0.15, color="#b8a070", linewidth=1.8, alpha=0.9)

# ============================================================
# 第二期燧石条带 — 穿层, 不规则脉状, 灰黑色, 0.5-4cm
# 斜切第一期和层面
# ============================================================

# 主穿层脉
gen2_x = np.array([3.0, 4.5, 5.5, 7.0, 8.2, 9.5, 10.8, 12.0])
gen2_y = np.array([13.5, 12.0, 11.0, 9.5, 8.3, 7.0, 5.5, 4.5])
# 加不规则度
np.random.seed(42)
for j in range(3):
    offset_y = j * 0.08 - 0.08
    y_j = gen2_y + offset_y + 0.03 * np.sin(gen2_x * 2)
    ax.fill_between(gen2_x, y_j - 0.2, y_j + 0.2, color="#5a5a5a", alpha=0.5, linewidth=0)

ax.plot(gen2_x, gen2_y, color="#2a2a2a", linewidth=2.0, alpha=0.9)

# 分支脉 (X形交叉)
branch_x = np.array([5.5, 6.2, 7.8, 8.8])
branch_y = np.array([11.0, 10.3, 9.2, 8.3])
ax.plot(branch_x, branch_y, color="#2a2a2a", linewidth=1.5, alpha=0.8)
ax.fill_between(branch_x, branch_y - 0.12, branch_y + 0.12, color="#4a4a4a", alpha=0.4, linewidth=0)

# ============================================================
# 第三期燧石条带 — 裂隙充填, 黑灰色, 0.3-1cm, 最细, 切穿前两期
# ============================================================

gen3_lines = [
    ([4.0, 5.5, 6.8, 8.2, 9.5], [14.0, 12.5, 11.0, 9.5, 8.0]),
    ([7.0, 8.5, 9.8, 10.5], [13.5, 12.0, 10.8, 9.8]),
    ([2.5, 3.8, 5.2, 6.5], [12.0, 11.0, 9.8, 8.5]),
]

for gx, gy in gen3_lines:
    gx = np.array(gx)
    gy = np.array(gy)
    gy += 0.02 * np.sin(gx * 4)
    ax.plot(gx, gy, color="#1a1a1a", linewidth=1.2, alpha=0.95)
    ax.fill_between(gx, gy - 0.06, gy + 0.06, color="#1a1a1a", alpha=0.6, linewidth=0)

# ============================================================
# 标注 — 引线 + 文字
# ============================================================

ann_style = dict(fontsize=9, fontweight="bold", ha="left", va="center")

# 第一期标注
ax.annotate("① 顺层燧石条带\n  (沉积/成岩期)\n  厚1-2cm, 与层面∥",
            xy=(2.2, 10.8), fontsize=8, color="#8b7355", ha="left",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#faf5eb", edgecolor="#c4a870", alpha=0.9))
ax.plot([2.3, 1.8], [10.6, 10.4], color="#8b7355", linewidth=0.8)

# 第二期标注
ax.annotate("② 穿层燧石脉\n  (构造-热液期)\n  厚0.5-4cm\n  斜切①和层面",
            xy=(9.5, 7.0), fontsize=8, color="#4a4a4a", ha="left",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#f5f5f5", edgecolor="#888", alpha=0.9))
ax.plot([9.2, 9.8], [6.8, 8.0], color="#666", linewidth=0.8)

# 第三期标注
ax.annotate("③ 裂隙充填燧石脉\n  (晚期构造-热液)\n  厚0.3-1cm\n  切穿①和②",
            xy=(8.5, 12.0), fontsize=8, color="#1a1a1a", ha="left",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#f0f0f0", edgecolor="#555", alpha=0.9))
ax.plot([8.5, 8.0], [11.9, 12.2], color="#555", linewidth=0.8)

# 层面标注
ax.annotate("层面 S0\n白云岩, 单层5-10cm",
            xy=(12.5, 10.5), fontsize=8, color="#666", ha="left", style="italic",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#aaa", alpha=0.85))
ax.plot([12.3, 11.8], [10.5, 10.3], color="#999", linewidth=0.6)

# 切割关系标注
ax.annotate("③切②", xy=(7.5, 9.0), fontsize=7, color="#c0392b", fontweight="bold",
            ha="center", bbox=dict(facecolor="white", alpha=0.8, edgecolor="none", pad=1))
ax.annotate("②切①", xy=(5.8, 10.2), fontsize=7, color="#c0392b", fontweight="bold",
            ha="center", bbox=dict(facecolor="white", alpha=0.8, edgecolor="none", pad=1))

# ============================================================
# 比例尺
# ============================================================

# 10cm 比例尺
scale_x, scale_y = 10.5, 14.5
ax.plot([scale_x, scale_x + 3], [scale_y, scale_y], color="black", linewidth=2)
ax.plot([scale_x, scale_x], [scale_y - 0.15, scale_y + 0.15], color="black", linewidth=1.5)
ax.plot([scale_x + 3, scale_x + 3], [scale_y - 0.15, scale_y + 0.15], color="black", linewidth=1.5)
ax.text(scale_x + 1.5, scale_y - 0.4, "~10 cm", ha="center", fontsize=8, color="black")

# 指北针
north_x, north_y = 12.5, 14.5
ax.plot([north_x, north_x], [north_y, north_y + 0.8], color="black", linewidth=1.5)
ax.plot([north_x, north_x - 0.2], [north_y, north_y + 0.3], color="black", linewidth=1.2)
ax.plot([north_x, north_x + 0.2], [north_y, north_y + 0.3], color="black", linewidth=1.2)
ax.text(north_x, north_y + 0.95, "N", ha="center", fontsize=9, fontweight="bold")

# ============================================================
# 标题和图号
# ============================================================

ax.text(7, 15.8, "图6-1  燧石条带先后关系素描图", ha="center", fontsize=13, fontweight="bold",
        bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.4"))

ax.text(7, 15.0, "D0601  雾迷山组第五段 (JxW⁵)  白云岩中燧石条带",
        ha="center", fontsize=9, color="#555")

# ============================================================
# 图例
# ============================================================

legend_y = 1.5
legend_items = [
    ("#d5c4a1", "第一期 顺层燧石"),
    ("#6a6a6a", "第二期 穿层燧石脉"),
    ("#1a1a1a", "第三期 裂隙充填燧石"),
]

for i, (color, label) in enumerate(legend_items):
    lx = 2 + i * 4
    ax.add_patch(plt.Rectangle((lx, legend_y), 0.6, 0.3, facecolor=color, edgecolor="#333", linewidth=0.5))
    ax.text(lx + 0.8, legend_y + 0.15, label, fontsize=7.5, va="center")

# ============================================================
# 底部说明
# ============================================================

ax.text(7, 0.6,
        "露头位置: 周口店 八角寨西坡 周张公路垭口  |  坐标: 39°39′19″N 115°52′36″E  |  视向: NW",
        ha="center", fontsize=7, color="#999")

fig.tight_layout(pad=0.5)
fig.savefig("output/图6-1_燧石条带先后关系.png", dpi=250, bbox_inches="tight",
            facecolor="white", edgecolor="none")
plt.close()
print("已保存: output/图6-1_燧石条带先后关系.png")
