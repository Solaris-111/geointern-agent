"""D0303 景儿峪组钙质板岩平卧褶皱 — 规范地质素描"""

import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parent.parent / "core"))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Polygon
from geo_plotting import (
    setup_chinese_font, LITHOLOGY, add_scale_bar, add_north_arrow,
    add_geological_legend, save_figure
)

setup_chinese_font()

fig, ax = plt.subplots(figsize=(10, 7.5))
ax.set_aspect('equal')

# ── 平卧褶皱层理线 ──
# 用自然弯曲的线条表现岩层转折，左下聚拢、右上散开
n_layers = 10
t = np.linspace(-3.0, 2.5, 400)

# 生成带手绘感的层理线
# 枢纽在左侧，轴面近水平
x_hinge = -0.8
y_hinge = 0.0

# 轻微随机扰动模拟手绘
rng = np.random.default_rng(42)


def bedding_y(t, layer_offset, hinge_x=-0.8):
    """计算平卧褶皱的层理 y 坐标。layer_offset 控制层的位置。"""
    # 枢纽弯曲：在 hinge_x 附近弯曲最强
    hinge_bend = np.exp(-((t - hinge_x) ** 2) / 0.4) * 1.8
    # 两翼分离：远离枢纽后上下分离
    limb_sep = np.tanh((t - hinge_x + 0.2) * 1.2) * 1.0
    # 层间偏移
    y = layer_offset + limb_sep * abs(layer_offset) * 0.4
    # 枢纽处弯曲
    y = y + hinge_bend * layer_offset * 0.7
    return y


for i in range(n_layers):
    off = (i - (n_layers - 1) / 2) * 0.16
    y = bedding_y(t, off)

    # 添加细微手绘抖动
    jitter = rng.normal(0, 0.015, len(t))
    y = y + jitter

    lw = 0.6 + abs(off) * 0.15
    ax.plot(t, y, 'k-', linewidth=lw, alpha=0.8)

# ── 填充岩性花纹 ──
# 用多边形覆盖主要岩层区域，填充板岩花纹
for i in range(n_layers - 1):
    off_bot = (i - (n_layers - 1) / 2) * 0.16
    off_top = (i + 1 - (n_layers - 1) / 2) * 0.16

    y_bot = bedding_y(t, off_bot)
    y_top = bedding_y(t, off_top)

    # 构建多边形
    poly_pts = list(zip(t, y_bot)) + list(zip(t[::-1], y_top[::-1]))
    poly = Polygon(poly_pts, facecolor=LITHOLOGY["板岩"]["color"],
                   edgecolor='none', alpha=0.6, hatch=LITHOLOGY["板岩"]["hatch"])
    ax.add_patch(poly)

# ── 构造标注 ──
# 轴面
ax.axhline(y=0.02, xmin=0.1, xmax=0.28, color='red', linestyle='--', linewidth=1.2)
ax.annotate('轴面 (近水平)', xy=(-0.25, -0.4), fontsize=9, color='red', ha='center',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))

# 枢纽
ax.plot(x_hinge, y_hinge - 0.08, 'k.', markersize=8)
ax.annotate('枢纽\n(Hinge)', xy=(x_hinge - 0.15, -0.7), fontsize=8, ha='center',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='lightyellow', alpha=0.85))

# 两翼标注
ax.annotate('上翼\n(正常翼)', xy=(1.8, 1.4), fontsize=8, ha='center',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='lightblue', alpha=0.75))
ax.annotate('下翼\n(倒转翼)', xy=(-2.0, -1.15), fontsize=8, ha='center',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='lightblue', alpha=0.75))

# 聚拢/散开
ax.annotate('聚拢 ←', xy=(-2.5, -0.25), fontsize=10, ha='center', fontweight='bold',
            color='darkgreen')
ax.annotate('→ 散开', xy=(2.0, -0.1), fontsize=10, ha='center', fontweight='bold',
            color='darkgreen')

# ── 岩性标注框 ──
ax.annotate('岩性: 钙质板岩 (Calcareous Slate)\n'
            '层位: 景儿峪组 (QxJ) 上部\n'
            '构造: 变余泥质结构，板状构造\n'
            '成分: 钙质胶结\n'
            '年代: 新元古代',
            xy=(1.5, 1.8), fontsize=8, ha='left', va='top',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='wheat',
                      edgecolor='gray', alpha=0.9))

# ── 实测数据框 ──
data_text = (
    '实测数据 (往年):\n'
    '  轴面产状: 341°∠28°\n'
    '  枢纽产状: 105°∠19°\n'
    '  上翼: 44°∠35°\n'
    '  下翼: 69°∠22°\n'
    '  褶皱类型: 平卧褶皱'
)
ax.annotate(data_text, xy=(-2.5, 1.8), fontsize=8, ha='left', va='top',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='lightyellow',
                      edgecolor='gray', alpha=0.85))

# ── 标题 ──
ax.set_title('图3-2  景儿峪组（QxJ）钙质板岩平卧褶皱素描\n'
             'D0303  黄院东山梁  周口店',
             fontsize=13, fontweight='bold', pad=12)

# ── 比例尺 ──
scale_x = 1.0
scale_y = -1.85
scale_len = 0.8
ax.plot([scale_x, scale_x + scale_len], [scale_y, scale_y], 'k-', linewidth=2)
ax.plot([scale_x, scale_x], [scale_y - 0.06, scale_y + 0.06], 'k-', linewidth=1)
ax.plot([scale_x + scale_len, scale_x + scale_len],
        [scale_y - 0.06, scale_y + 0.06], 'k-', linewidth=1)
ax.text(scale_x + scale_len / 2, scale_y - 0.15, '~5 m', ha='center', fontsize=8)

# ── 指北针 ──
n_x, n_y = 2.1, 1.9
ax.annotate('N', xy=(n_x, n_y + 0.22), fontsize=11, fontweight='bold', ha='center')
ax.annotate('', xy=(n_x, n_y - 0.1), xytext=(n_x, n_y + 0.15),
            arrowprops=dict(arrowstyle='->', lw=1.5, color='k'))
ax.plot([n_x - 0.1, n_x + 0.1], [n_y + 0.02, n_y + 0.02], 'k-', linewidth=0.8)

# ── 图例 ──
legend_handle = mpatches.Patch(facecolor=LITHOLOGY["板岩"]["color"],
                                edgecolor='black', linewidth=0.5,
                                hatch=LITHOLOGY["板岩"]["hatch"],
                                label='钙质板岩 (QxJ)')
ax.legend(handles=[legend_handle], loc='lower right', fontsize=8, framealpha=0.9)

ax.set_xlim(-2.8, 2.5)
ax.set_ylim(-2.0, 2.3)
ax.axis('off')

plt.tight_layout()
save_figure(fig, 'D0303_景儿峪组平卧褶皱素描.png', dpi=200)
