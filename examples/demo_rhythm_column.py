"""地层韵律柱状图 — for 循环驱动旋回重复."""

import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parent.parent / "core"))

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from geo_plotting import setup_chinese_font, LITHOLOGY, save_figure

setup_chinese_font()


def draw_rhythm_column(rhythm_template, n_cycles, rhythm_name="",
                        grain_direction="fining_up", figsize=(6, 10)):
    """
    for 循环绘制地层韵律柱状图。

    rhythm_template: [(岩性名, 单层厚度m, 颜色, 花纹), ...]  从底到顶
    n_cycles: 旋回重复次数
    grain_direction: "fining_up"(向上变细) / "coarsening_up"(向上变粗)
    """
    fig, ax = plt.subplots(figsize=figsize)

    # —— 计算总高度 ——
    cycle_height = sum(layer[1] for layer in rhythm_template)
    total_height = cycle_height * n_cycles

    # —— for 循环逐旋回、逐层画 ——
    y_bottom = 0
    cycle_boundaries = [0]  # 记录每个旋回底界的 y 坐标

    for c in range(n_cycles):
        y_layer = y_bottom
        for litho_name, thickness, color, hatch in rhythm_template:
            rect = mpatches.Rectangle((0, y_layer), 3, thickness,
                                       facecolor=color, edgecolor='black',
                                       linewidth=0.5, hatch=hatch)
            ax.add_patch(rect)
            y_layer += thickness

        # 旋回之间的分隔线
        if c < n_cycles - 1:
            ax.plot([-0.3, 3.3], [y_layer, y_layer], 'k-', linewidth=1.2)

        y_bottom = y_layer
        cycle_boundaries.append(y_bottom)

    # —— 岩性标注（每个旋回标一次，在第一个旋回标） ——
    y0 = 0
    for litho_name, thickness, color, hatch in rhythm_template:
        label = LITHOLOGY.get(litho_name, {}).get("desc", litho_name)
        ax.text(3.15, y0 + thickness / 2, f"{litho_name}\n{thickness}m",
                fontsize=7, va='center')
        y0 += thickness

    # —— 旋回编号 ——
    for c in range(n_cycles):
        y_mid = cycle_boundaries[c] + cycle_height / 2
        ax.text(-0.6, y_mid, f"旋回{c+1}", fontsize=8, ha='right', va='center',
                fontweight='bold')

    # —— 粒度变化箭头（右侧） ——
    arrow_x = 3.7
    for c in range(n_cycles):
        y_bot = cycle_boundaries[c]
        y_top = cycle_boundaries[c + 1]
        y_mid = (y_bot + y_top) / 2

        # 三角箭头
        if grain_direction == "fining_up":
            ax.annotate('', xy=(arrow_x, y_bot + 0.2), xytext=(arrow_x, y_top - 0.2),
                        arrowprops=dict(arrowstyle='<->', color='gray', lw=1.2))
            ax.text(arrow_x + 0.3, y_mid, '细\n↑\n↓\n粗', fontsize=6, ha='left',
                    va='center', color='gray')
        else:
            ax.annotate('', xy=(arrow_x, y_bot + 0.2), xytext=(arrow_x, y_top - 0.2),
                        arrowprops=dict(arrowstyle='<->', color='gray', lw=1.2))
            ax.text(arrow_x + 0.3, y_mid, '粗\n↑\n↓\n细', fontsize=6, ha='left',
                    va='center', color='gray')

    # —— 水深标注（最右侧） ——
    water_x = 4.5
    ax.annotate('浅 ←', xy=(water_x, total_height), fontsize=8, ha='center', color='steelblue')
    ax.annotate('深 ←', xy=(water_x, 0), fontsize=8, ha='center', color='steelblue')
    ax.annotate('', xy=(water_x, 0.5), xytext=(water_x, total_height - 0.5),
                arrowprops=dict(arrowstyle='<->', color='steelblue', lw=1))

    # —— 图名 ——
    title = f'{rhythm_name}\n{n_cycles} 个旋回 × {cycle_height:.1f}m/旋回  总厚 {total_height:.1f}m'
    ax.set_title(title, fontsize=12, fontweight='bold')

    ax.set_xlim(-1.5, 5.5)
    ax.set_ylim(0, total_height * 1.02)
    ax.axis('off')

    plt.tight_layout()
    return fig, ax


# ═══════════════════════════════════════════════
# 示例：L03 张夏组 向上变浅旋回
# ═══════════════════════════════════════════════

# 每个旋回: 鲕粒灰岩(底) → 泥晶灰岩 → 钙质板岩(顶)
zhangxia_template = [
    ("灰岩",   4.0, "#A8D0DB", "||"),   # 底部鲕粒灰岩
    ("页岩",   6.0, "#C8C0A0", "---"),  # 中部钙质板岩
    ("泥岩",   2.0, "#D8C8A8", "---"),  # 顶部泥质沉积
]

fig, ax = draw_rhythm_column(
    zhangxia_template,
    n_cycles=10,
    rhythm_name="张夏组 (∈₂z) 向上变浅沉积旋回 — L03 黄院东山梁",
    grain_direction="fining_up"
)

save_figure(fig, "demo_rhythm_张夏组.png", dpi=200)
print("完成")
