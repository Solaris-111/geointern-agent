"""L03 张夏组 (∈₂z) 信手剖面韵律 — 真实数据"""

import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parent.parent / "core"))

import math
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from geo_plotting import setup_chinese_font, save_figure

setup_chinese_font()

fig, ax = plt.subplots(figsize=(16, 5))

# ═══════════════════════════════════════════
# 张夏组 (∈₂z) — 真实数据
# ═══════════════════════════════════════════
# 指导书: 灰色灰绿色板岩夹中层鲕粒灰岩，~36m
# 往年野簿: 三种岩性(鲕粒灰岩、泥晶灰岩、钙质板岩)→9-11个向上变浅旋回
# 每个旋回: 下部鲕粒灰岩→中上部钙质板岩，总体向上鲕粒灰岩渐变为泥晶灰岩
# 产状: 北东 40-60° 倾角 15-29°（用 D0301 实测）
# 剖面走向: 假设 330° (NW-SE)

true_dip = 22           # 真倾角 °
strike = 50             # 岩层倾向 °
section_bearing = 330   # 剖面走向 °
theta = abs(section_bearing - strike)
theta = min(theta, 360 - theta)  # 取锐角, 剖面线与走向的夹角
apparent_dip = math.degrees(math.atan(math.tan(math.radians(true_dip)) * math.sin(math.radians(theta))))

true_thickness = 36     # 真厚度 m
single_cycle = 3.6      # 单一旋回厚度 m (36m÷10旋回)
n_cycles = int(true_thickness / single_cycle)  # = 10, 宁可少画

# 水平宽度
horizontal_width = true_thickness / math.sin(math.radians(apparent_dip))
cycle_width = single_cycle / math.sin(math.radians(apparent_dip))

print(f"视倾角: {apparent_dip:.1f}°")
print(f"旋回数: {n_cycles}  单一旋回厚度: {single_cycle}m")
print(f"总水平宽度: {horizontal_width:.0f}m  单旋回水平宽: {cycle_width:.1f}m")

x0_offset = 10  # 起始偏移

# ── 组名标注 ──
ax.text(x0_offset + horizontal_width / 2, 38,
        f"张夏组 (∈₂z)\n{true_thickness}m / {n_cycles}个旋回\n"
        f"视倾角 {apparent_dip:.0f}°  水平出露 {horizontal_width:.0f}m",
        fontsize=8, ha='center', va='bottom',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.85))

# ── for 循环: 10个旋回 ──
for c in range(n_cycles):
    x0 = x0_offset + c * cycle_width

    # 旋回内部三段:
    # ① 鲕粒灰岩 (厚层段) — 占 35%
    w1 = cycle_width * 0.35
    ax.add_patch(plt.Rectangle((x0, 0), w1, 25,
                facecolor="#A8D0DB", edgecolor='black', linewidth=0.3, hatch="||"))
    ax.text(x0 + w1/2, 3, "鲕粒\n灰岩", fontsize=5, ha='center', va='bottom')

    # ② 泥晶灰岩 (中层段) — 占 25%
    x1 = x0 + w1
    w2 = cycle_width * 0.25
    ax.add_patch(plt.Rectangle((x1, 0), w2, 25,
                facecolor="#C8D8C8", edgecolor='black', linewidth=0.3, hatch="//"))
    ax.text(x1 + w2/2, 3, "泥晶灰岩", fontsize=5, ha='center', va='bottom')

    # ③ 钙质板岩 (薄层+互层段) — 占 40%
    x2 = x1 + w2
    w3 = cycle_width * 0.40
    # 互层段内部: 薄层板岩(---)和灰岩(||)交替，用组合 hatch 表示
    ax.add_patch(plt.Rectangle((x2, 0), w3, 25,
                facecolor="#D8C8A8", edgecolor='black', linewidth=0.3, hatch="---"))
    ax.text(x2 + w3/2, 3, "钙质\n板岩", fontsize=5, ha='center', va='bottom')

    # 旋回分界线
    if c < n_cycles - 1:
        ax.plot([x0 + cycle_width, x0 + cycle_width], [0, 25],
                'k-', linewidth=0.5)

    # 旋回编号
    ax.text(x0 + cycle_width / 2, 26, f"C{c+1}", fontsize=6,
            ha='center', va='bottom', color='gray')

# ── 粒度箭头（每个旋回内粗→细，整体向上变浅） ──
for c in range(n_cycles):
    x0 = x0_offset + c * cycle_width
    ax.annotate('粗→细', xy=(x0 + cycle_width * 0.15, 30),
                fontsize=5, ha='center', color='darkred')
    ax.annotate('', xy=(x0 + cycle_width * 0.06, 30),
                xytext=(x0 + cycle_width * 0.35, 30),
                arrowprops=dict(arrowstyle='->', color='darkred', lw=0.8))

# ── 整体水深趋势（最右侧） ──
ax.annotate('浅\n↑\n水\n深\n↓\n深', xy=(x0_offset + horizontal_width + 10, 12),
            fontsize=8, ha='center', color='steelblue')
ax.annotate('', xy=(x0_offset + horizontal_width + 10, 2),
            xytext=(x0_offset + horizontal_width + 10, 22),
            arrowprops=dict(arrowstyle='<->', color='steelblue', lw=1))

# ── 上下地层示意 ──
# 下伏: 徐庄组
ax.text(x0_offset - 8, 12, "徐庄组 ∈₂x\n(下伏)",
        fontsize=7, ha='center', rotation=90, color='gray')
# 上覆: 黄院组
ax.text(x0_offset + horizontal_width + 18, 12, "黄院组 ∈₂h\n(上覆)",
        fontsize=7, ha='center', rotation=90, color='gray')

# ── 图名 ──
ax.set_title("张夏组 (∈₂z) 向上变浅沉积旋回 — 信手剖面韵律表示\n"
             f"L03 黄院东山梁  真厚度{true_thickness}m  {n_cycles}个旋回  "
             f"水平比例尺 ~1:{horizontal_width/16*100:.0f}",
             fontsize=11, fontweight='bold')

# ── 图例 ──
legend_items = [
    Patch(facecolor="#A8D0DB", hatch="||", label="鲕粒灰岩 (厚层段)"),
    Patch(facecolor="#C8D8C8", hatch="//", label="泥晶灰岩 (中层段)"),
    Patch(facecolor="#D8C8A8", hatch="---", label="钙质板岩 (薄层/互层段)"),
]
ax.legend(handles=legend_items, loc='upper right', fontsize=7, ncol=3)

# ── 底栏标注 ──
ax.annotate(f"视倾角换算: δ'=arctan(tan{true_dip}°×sin|{section_bearing}°-{strike}°|)={apparent_dip:.1f}°  "
            f"水平宽度={true_thickness}/sin({apparent_dip:.0f}°)={horizontal_width:.0f}m  "
            f"旋回重复=10×  int({true_thickness}/{single_cycle})=10  "
            f"— 宁可少画, 余0m",
            xy=(0.5, -0.08), fontsize=6, ha='center', va='top',
            transform=ax.transAxes, color='gray',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='whitesmoke', alpha=0.7))

ax.set_xlim(-15, x0_offset + horizontal_width + 25)
ax.set_ylim(-4, 42)
ax.axis('off')

save_figure(fig, "demo_rhythm_张夏组_L03.png", dpi=200)
print("完成")
