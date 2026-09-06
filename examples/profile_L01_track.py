"""L01 踏勘地形剖面 — 仅地形线, 无地层."""
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# 加载数据
dists, elevs = [], []
with open("output/L01_踏勘_profile.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    next(reader)  # skip header
    for row in reader:
        dists.append(float(row[2]))
        elevs.append(float(row[3]))

dists = np.array(dists) / 1000  # m → km
elevs = np.array(elevs)

# 截取 1.2km → 1.92km 段
mask = (dists >= 1.2) & (dists <= 1.92)
# 保留绝对距离, X轴显示实际里程
dists = dists[mask]
elevs = elevs[mask]

# 移动平均平滑 (窗口=5, 约25m)
window = 5
elevs_smooth = np.convolve(elevs, np.ones(window)/window, mode='same')
elevs_smooth[:window//2] = elevs[:window//2]
elevs_smooth[-window//2:] = elevs[-window//2:]
elevs = elevs_smooth

fig, ax = plt.subplots(figsize=(14, 5))

# 地形填充
ax.fill_between(dists, elevs, 0, facecolor="#E8E0D0", edgecolor="none", zorder=0)
ax.plot(dists, elevs, 'k-', linewidth=1.5, zorder=2)

# 标注起点
ax.annotate(f"{dists[0]:.0f}m {elevs[0]:.0f}m", xy=(dists[0], elevs[0]),
            fontsize=8, ha='left', va='top', color='blue')
ax.annotate(f"D0101 {elevs[-1]:.0f}m", xy=(dists[-1], elevs[-1]),
            xytext=(dists[-1]-0.08, elevs[-1]+12),
            fontsize=9, ha='center', va='bottom', color='red', fontweight='bold')

# 刻度
ax.set_xlabel("水平距离 (km)", fontsize=10)
ax.set_ylabel("海拔 (m)", fontsize=10)
ax.set_title("L01 大砾岩山上坡段 地形剖面 — 2026-07-26", fontsize=13, fontweight='bold')

# 比例尺
bar_x = dists[0] + (dists[-1]-dists[0]) * 0.6
bar_len = 0.2  # km = 200m
bar_y = 10
ax.plot([bar_x, bar_x + bar_len], [bar_y, bar_y], 'k-', linewidth=2)
ax.plot([bar_x, bar_x], [bar_y-3, bar_y+3], 'k-', linewidth=1)
ax.plot([bar_x + bar_len, bar_x + bar_len], [bar_y-3, bar_y+3], 'k-', linewidth=1)
ax.text(bar_x + bar_len/2, bar_y - 8, "200 m", ha='center', fontsize=8)

# 底部标注
ax.text(0.5, -0.12, f"段长 {(dists[-1]-dists[0]):.0f}m | 海拔 {elevs.min():.0f}→{elevs.max():.0f}m",
        transform=ax.transAxes, ha='center', fontsize=8, color='gray')

ax.set_xlim(dists[0], dists[-1])
ax.set_ylim(0, elevs.max() * 1.18)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig("output/L01_踏勘地形剖面.png", dpi=200, bbox_inches='tight')
plt.close()
print(f"Done: {dists[-1]:.2f} km, elev {elevs.min():.0f}-{elevs.max():.0f}m")
