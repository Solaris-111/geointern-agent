"""柱状图 — 地层综合柱状图生成器.

输入格式: 修改 LAYERS 列表即可生成自己的柱状图。
每层格式: (层底深度m, 厚度m, 岩性名, 描述, 颜色覆盖(可选))
"""

import matplotlib.pyplot as plt
import numpy as np
from geo_plotting import (
    setup_chinese_font, LITHOLOGY, add_scale_bar, add_geological_legend, save_figure,
)

setup_chinese_font()

# ══════════════════════════════════════════════════════════════════
# 数据定义 — 修改这里生成你自己的柱状图
# ══════════════════════════════════════════════════════════════════

# 层厚比例: 地层从顶到底依次排列
LAYERS = [
    # (累计底深m, 厚度m, 岩性名称, 描述文本, 可选覆盖颜色)
    (0.8,  0.8, "亚粘土",        "黄褐色亚粘土，含少量钙质结核"),
    (2.0,  1.2, "砾石层",        "洪积砾石层，砾径2-15cm，\n次圆状，钙质胶结"),
    (2.6,  0.6, "亚粘土",        "棕红色亚粘土，含铁锰结核"),
    (4.2,  1.6, "砂岩",          "灰白色中粗粒砂岩，\n平行层理发育"),
    (5.0,  0.8, "粉砂岩",        "灰色粉砂岩，水平层理"),
    (7.5,  2.5, "灰岩",          "深灰色中厚层灰岩，\n含燧石结核，产蜓类化石"),
    (8.5,  1.0, "页岩",          "黑色炭质页岩，\n产植物化石碎片"),
    (11.5, 3.0, "白云岩",        "灰白色厚层白云岩，\n细晶结构"),
]

TITLE = "周口店太平山综合地层柱状图"
COLUMN_WIDTH = 1.0             # 柱体宽度
FIG_SIZE = (5.5, 9)

# ══════════════════════════════════════════════════════════════════

def draw_lithology_pattern(ax, bottom, top, lith_name, override_color=None):
    """在柱体范围内绘制岩性花纹."""
    info = LITHOLOGY.get(lith_name, {"color": "#E8E0D0", "hatch": ".."})
    color = override_color or info["color"]
    hatch = info["hatch"]
    thickness = top - bottom

    ax.fill_between([0, COLUMN_WIDTH], bottom, top, facecolor=color,
                    alpha=0.55, edgecolor="0.3", linewidth=0.5, hatch=hatch)

    n_grains = int(thickness * 40)
    if n_grains > 150:
        n_grains = 150

    if "角砾" in lith_name or "砾石" in lith_name or "砾岩" in lith_name:
        for _ in range(n_grains):
            cx = np.random.uniform(0.08, COLUMN_WIDTH - 0.08)
            cy = np.random.uniform(bottom + 0.05, top - 0.05)
            r = np.random.uniform(0.02, 0.07)
            circ = plt.Circle((cx, cy), r, facecolor="0.75", edgecolor="0.4",
                              linewidth=0.3, alpha=0.7)
            ax.add_patch(circ)
    elif "砂岩" in lith_name:
        for _ in range(n_grains):
            px = np.random.uniform(0.03, COLUMN_WIDTH - 0.03)
            py = np.random.uniform(bottom + 0.02, top - 0.02)
            ax.plot(px, py, "k.", markersize=np.random.uniform(0.2, 0.6))


def generate():
    total_depth = LAYERS[-1][0]
    fig, ax = plt.subplots(figsize=FIG_SIZE)

    for base, thick, name, desc, *rest in LAYERS:
        override = rest[0] if rest else None
        top = base - thick
        draw_lithology_pattern(ax, top, base, name, override)

        ax.plot([0, 0], [top, base], "k-", linewidth=1.2)
        ax.plot([COLUMN_WIDTH, COLUMN_WIDTH], [top, base], "k-", linewidth=1.2)
        ax.plot([0, COLUMN_WIDTH], [base, base], "k-", linewidth=0.6)
        ax.plot([0, COLUMN_WIDTH], [top, top], "k-", linewidth=0.6)

        mid = (top + base) / 2
        ax.text(COLUMN_WIDTH + 0.12, mid, name, va="center", fontsize=9, fontweight="bold")
        ax.text(COLUMN_WIDTH + 0.70, mid, desc, va="center", fontsize=6.5, color="0.3")

    ax.plot([0, COLUMN_WIDTH], [total_depth - 0.05, total_depth - 0.05], "k-", linewidth=1.2)

    # 粒度曲线
    grain_y = np.linspace(0, total_depth, 20)
    grain_x = COLUMN_WIDTH + 1.55 + np.sin(grain_y / total_depth * np.pi) * 0.25
    ax.plot(grain_x, grain_y, "gray", linewidth=1.5, linestyle="--", alpha=0.6)
    ax.text(COLUMN_WIDTH + 1.60, -0.3, "细", fontsize=8, color="gray", ha="center")
    ax.text(COLUMN_WIDTH + 1.60, total_depth + 0.3, "粗", fontsize=8, color="gray", ha="center")

    # 化石标记
    ax.plot(COLUMN_WIDTH / 2, 6.3, "r*", markersize=10)
    ax.text(COLUMN_WIDTH / 2 + 0.15, 6.3, "蜓类", fontsize=7, color="red")
    ax.plot(COLUMN_WIDTH / 2, 8.0, "r*", markersize=8)
    ax.text(COLUMN_WIDTH / 2 + 0.15, 8.0, "植物碎片", fontsize=7, color="red")

    # 图例
    legend_items = [(name, LITHOLOGY.get(name, {}).get("color", "#E8E0D0"),
                     LITHOLOGY.get(name, {}).get("hatch", ".."))
                    for _, _, name, *_ in LAYERS]
    unique = {}
    for label, c, h in legend_items:
        if label not in unique:
            unique[label] = (c, h)
    add_geological_legend(ax, [(k, v[0], v[1]) for k, v in unique.items()],
                          loc="lower left", fontsize=7, bbox_to_anchor=(0.02, -0.04))

    ax.set_title(TITLE, fontsize=13, fontweight="bold", pad=16)
    ax.set_ylabel("深度 / m", fontsize=10)
    ax.set_xlim(-0.3, COLUMN_WIDTH + 1.9)
    ax.set_ylim(total_depth + 0.6, -0.8)
    ax.set_xticks([])
    ax.invert_yaxis()
    ax.grid(axis="y", alpha=0.15)

    add_scale_bar(ax, length=1.0, label="比例尺 1:200  (垂直)", fontsize=7)
    return fig


if __name__ == "__main__":
    fig = generate()
    save_figure(fig, "columnar_section.png")
