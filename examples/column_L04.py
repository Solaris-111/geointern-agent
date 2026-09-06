"""L04 太平山南坡 综合地层柱状图 — O₁m→P₁y 上古生界完整序列.
数据来源: 往年周口店报告附图III 实测剖面逐层厚度数据.
"""
import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parent.parent / "core"))

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os
from geo_plotting import setup_chinese_font, save_figure
from lithology_patterns import LITHOLOGY_PATTERNS, LITHOLOGY_COLORS

setup_chinese_font()

# 岩性花纹映射 (同 lithology_patterns 规范)
LITHOLOGY = LITHOLOGY_PATTERNS

# ══════════════════════════════════════════════════════════════════
# 数据: (累计底深m, 厚度m, 岩性, 描述, 地层代号, 接触面标注)
# 从老(底)到新(顶) — 柱状图底部=最老地层
# ══════════════════════════════════════════════════════════════════

LAYERS = [
    # ── O₁m 马家沟组 (顶部, 仅出露不整合面以下部分) ──
    (0.0,   6.0, "灰岩",       "灰色中厚层角砾状灰岩\n构造剪切劈理化", "O₁m"),
    # ── 平行不整合 ──
    # ── C₂b 本溪组 (~62.5m) ──
    (6.0,   6.0, "角岩",       "白灰色红柱石角岩\n斑状变晶结构 块状构造", "C₂b"),
    (12.0,  2.5, "角岩",       "黑绿色硬绿泥石角岩\n鳞片变晶+角岩结构 比重大", "C₂b"),
    (14.5,  5.5, "角岩",       "灰色红柱石角岩\n柱状红柱石断面方形", "C₂b"),
    (20.0, 12.5, "板岩",       "黄色粉砂质板岩\n变余砂状结构 板状构造", "C₂b"),
    (32.5,  2.0, "灰岩",       "灰色唐山灰岩\n生物碎屑灰岩 产纺锤蜓*Fusulina* sp.", "C₂b"),
    (34.5, 11.0, "板岩",       "深灰色压力影板岩\n黄铁矿+石英方解石低压充填", "C₂b"),
    (45.5, 17.0, "板岩",       "灰黄色钙质板岩\n(C₂b顶部, 向上变细)", "C₂b"),
    # ── C₃t 太原组 (~79m) ──
    (62.5,  9.0, "砂岩",       "黑灰色岩屑砂岩\n中细粒变质岩屑杂砂岩 地貌小陡坎", "C₃t"),
    (71.5, 32.0, "砂岩",       "紫红色砂岩与板岩互层\n红柱石角岩夹层", "C₃t"),
    (103.5, 5.0, "板岩",       "黄色钙质板岩\n(第二旋回开始)", "C₃t"),
    (108.5, 0.5, "页岩",       "黑色炭质板岩", "C₃t"),
    (109.0, 3.0, "板岩",       "黄色钙质板岩", "C₃t"),
    (112.0, 0.5, "页岩",       "黑色炭质板岩", "C₃t"),
    (112.5, 5.5, "板岩",       "黄色钙质板岩", "C₃t"),
    (118.0, 0.5, "页岩",       "黑色炭质板岩", "C₃t"),
    (118.5, 4.0, "板岩",       "黄色钙质板岩", "C₃t"),
    (122.5, 0.5, "页岩",       "黑色炭质板岩", "C₃t"),
    (123.0, 3.0, "板岩",       "黄色钙质板岩", "C₃t"),
    (126.0, 11.0, "板岩",      "钙质板岩与炭质板岩互层\n(第一旋回)", "C₃t"),
    (137.0, 4.5, "页岩",       "黑色炭质板岩\n(C₃t顶部, 不含煤线)", "C₃t"),
    # ── P₁s 山西组 (~49m) ──
    (141.5, 9.0, "砂岩",       "红褐色砂岩\n含燧石角砾 细粒砂状结构", "P₁s"),
    (150.5, 22.0, "页岩",      "黑色厚层炭质板岩\n含煤层 植物化石", "P₁s"),
    (172.5, 7.0, "砂岩",       "青黑色砂岩\n细粒砂状结构 块状构造", "P₁s"),
    (179.5, 11.0, "页岩",      "灰黑色炭质板岩\n含煤线", "P₁s"),
    # ── P₁y 杨家屯组 (~100m, 未全测) ──
    (190.5, 20.0, "砾岩",      '变质含砾岩屑砂岩\n"豆腐块砂岩" 斜层理发育', "P₁y"),
    (210.5, 30.0, "角砾岩",    "变质角砾岩\n变余砾状结构", "P₁y"),
    (240.5, 50.0, "板岩",      "灰色砂质板岩\n劈理化发育 (顶未测至)", "P₁y"),
]

TITLE = "太平山南坡综合地层柱状图"
SUBTITLE = "下奥陶统马家沟组(O₁m) — 下二叠统杨家屯组(P₁y)  总厚 ~290m  比例尺 1:2000"

COLUMN_WIDTH = 1.6
FIG_SIZE = (7.5, 18)

# ══════════════════════════════════════════════════════════════════

def draw_lithology_pattern(ax, bottom, top, lith_name, override_color=None):
    """在柱体范围内绘制岩性花纹."""
    info = LITHOLOGY.get(lith_name, {"hatch": ".."})
    hatch = info.get("hatch", "..")
    color = override_color or LITHOLOGY_COLORS.get(lith_name, "#E8E0D0")
    thickness = top - bottom

    ax.fill_between([0, COLUMN_WIDTH], bottom, top, facecolor=color,
                    alpha=0.55, edgecolor="0.3", linewidth=0.5, hatch=hatch)

    n_grains = int(thickness * 20)
    if n_grains > 120:
        n_grains = 120

    if "角砾" in lith_name or "砾石" in lith_name or "砾岩" in lith_name:
        for _ in range(n_grains):
            cx = np.random.uniform(0.10, COLUMN_WIDTH - 0.10)
            cy = np.random.uniform(bottom + 0.08, top - 0.08)
            r = np.random.uniform(0.03, 0.09)
            circ = plt.Circle((cx, cy), r, facecolor="0.75", edgecolor="0.4",
                              linewidth=0.3, alpha=0.7)
            ax.add_patch(circ)
    elif "砂岩" in lith_name:
        for _ in range(n_grains):
            px = np.random.uniform(0.04, COLUMN_WIDTH - 0.04)
            py = np.random.uniform(bottom + 0.03, top - 0.03)
            ax.plot(px, py, "k.", markersize=np.random.uniform(0.3, 0.8))


def generate():
    total_depth = LAYERS[-1][0]  # 最后一个层底的深度 = 总厚
    fig, ax = plt.subplots(figsize=FIG_SIZE)

    # 收集地层代号区间
    fm_ranges = {}  # code → (top_depth, bottom_depth)
    prev_code = None

    for base, thick, name, desc, code in LAYERS:
        top = base - thick
        draw_lithology_pattern(ax, top, base, name)

        ax.plot([0, 0], [top, base], "k-", linewidth=1.2)
        ax.plot([COLUMN_WIDTH, COLUMN_WIDTH], [top, base], "k-", linewidth=1.2)
        ax.plot([0, COLUMN_WIDTH], [base, base], "k-", linewidth=0.5)
        ax.plot([0, COLUMN_WIDTH], [top, top], "k-", linewidth=0.5)

        mid = (top + base) / 2
        ax.text(COLUMN_WIDTH + 0.15, mid, name, va="center", fontsize=8.5, fontweight="bold")
        ax.text(COLUMN_WIDTH + 0.85, mid, desc, va="center", fontsize=6.2, color="0.3")

        # 追踪组边界
        if code != prev_code:
            if prev_code is not None and prev_code in fm_ranges:
                fm_ranges[prev_code] = (fm_ranges[prev_code][0], base)
            fm_ranges[code] = (top, None)
        prev_code = code

    # 最后一个组
    if prev_code in fm_ranges:
        fm_ranges[prev_code] = (fm_ranges[prev_code][0], total_depth)

    # ── 组间接触界线 (粗线) ──
    fm_boundaries = []
    prev_code = None
    for base, thick, name, desc, code in LAYERS:
        if code != prev_code and prev_code is not None:
            fm_boundaries.append((base - thick, code, prev_code))
        prev_code = code

    for bnd_depth, new_code, old_code in fm_boundaries:
        ax.plot([0, COLUMN_WIDTH], [bnd_depth, bnd_depth], "k-", linewidth=1.6)

    # 平行不整合标注 (O₁m/C₂b)
    unconformity_depth = 6.0
    ax.plot([0, COLUMN_WIDTH], [unconformity_depth, unconformity_depth],
            "k-", linewidth=2.5)
    # 锯齿符号
    for wx in np.linspace(0.05, COLUMN_WIDTH - 0.05, 15):
        ax.plot(wx, unconformity_depth, "k^", markersize=3)
    ax.text(COLUMN_WIDTH + 0.15, unconformity_depth,
            "— — 平行不整合 — —\n(缺失 O₃+S+D+C₁)", fontsize=7,
            color="red", va="center", fontweight="bold")

    # ── 地层代号标记 (右侧) ──
    for code, (top_d, bot_d) in fm_ranges.items():
        mid = (top_d + bot_d) / 2
        ax.text(-0.55, mid, code, fontsize=9, fontweight="bold",
                ha="right", va="center")

    # ── 组名标记 (左侧) ──
    fm_names = {
        "O₁m": "马家沟组\n(顶部)",
        "C₂b": "本溪组",
        "C₃t": "太原组",
        "P₁s": "山西组",
        "P₁y": "杨家屯组\n(未测至顶)",
    }
    for code, (top_d, bot_d) in fm_ranges.items():
        mid = (top_d + bot_d) / 2
        h = bot_d - top_d
        name_text = fm_names.get(code, code)
        if h > 20:  # 空间够才标
            ax.text(-0.55, mid, name_text, fontsize=6.5, color="gray",
                    ha="right", va="center")

    # ── 粒度曲线 ──
    grain_y = np.linspace(0, total_depth, 50)
    grain_x = COLUMN_WIDTH + 1.75 + np.sin(grain_y / total_depth * np.pi * 2.5) * 0.3
    ax.plot(grain_x, grain_y, "gray", linewidth=1.5, linestyle="--", alpha=0.5)
    ax.text(COLUMN_WIDTH + 1.80, -1.5, "细←", fontsize=7, color="gray", ha="center")
    ax.text(COLUMN_WIDTH + 1.80, total_depth + 1.5, "→粗", fontsize=7, color="gray", ha="center")

    # ── 化石标记 ──
    ax.plot(COLUMN_WIDTH / 2, 33.5, "r*", markersize=12)
    ax.text(COLUMN_WIDTH / 2 + 0.25, 33.5, "蜓类\n*Fusulina*", fontsize=7, color="red",
            style="italic")
    ax.plot(COLUMN_WIDTH / 2, 74, "r*", markersize=8)
    ax.text(COLUMN_WIDTH / 2 + 0.25, 74, "植物化石", fontsize=7, color="red")
    ax.plot(COLUMN_WIDTH / 2, 162, "r*", markersize=8)
    ax.text(COLUMN_WIDTH / 2 + 0.25, 162, "植物化石\n(煤线)", fontsize=7, color="red")

    # ── 沉积旋回箭头 ──
    for cyc_top, cyc_label, cyc_color in [
        (6.0, "C₂b: 向上变细\n4个旋回", "#2c3e50"),
        (62.5, "C₃t: 钙质-炭质\n多旋回互层", "#2c3e50"),
        (141.5, "P₁s: 砂岩-板岩\n2个旋回", "#2c3e50"),
    ]:
        ax.annotate(cyc_label, xy=(COLUMN_WIDTH + 0.15, cyc_top),
                   fontsize=6, color=cyc_color, va="top", ha="left",
                   bbox=dict(boxstyle="round,pad=0.15", facecolor="lightyellow", alpha=0.6))

    # ── 图例 ──
    legend_items = [(name, LITHOLOGY_COLORS.get(name, "#E8E0D0"),
                     LITHOLOGY.get(name, {}).get("hatch", ".."))
                    for _, _, name, *_ in LAYERS]
    unique = {}
    for label, c, h in legend_items:
        if label not in unique:
            unique[label] = (c, h)
    # inline legend
    handles = []
    for label, (color, hatch) in unique.items():
        patch = mpatches.Patch(facecolor=color, alpha=0.55, edgecolor="0.3",
                               linewidth=0.5, hatch=hatch, label=label)
        handles.append(patch)
    ax.legend(handles=handles, loc="lower left", fontsize=6.5,
              ncol=2, bbox_to_anchor=(0.02, -0.02), framealpha=0.8)

    # ── 标题与轴 ──
    ax.set_title(TITLE, fontsize=14, fontweight="bold", pad=20)
    ax.text(0.5, -0.03, SUBTITLE, transform=ax.transAxes, ha="center",
            fontsize=8, color="gray")
    ax.set_ylabel("累计厚度 / m", fontsize=10)
    ax.set_xlim(-0.8, COLUMN_WIDTH + 2.2)
    ax.set_ylim(total_depth + 5, -5)
    ax.set_xticks([])
    ax.invert_yaxis()
    ax.grid(axis="y", alpha=0.12)

    # ── 比例尺 ──
    bar_len = 20  # m
    bar_y = total_depth + 15
    bar_x_start = COLUMN_WIDTH + 0.3
    ax.plot([bar_x_start, bar_x_start + bar_len / total_depth * 20],
            [bar_y, bar_y], "k-", linewidth=2)
    ax.text(bar_x_start + bar_len / total_depth * 10, bar_y - 2,
            f"{bar_len} m", fontsize=7, ha="center")
    ax.text(bar_x_start + bar_len / total_depth * 10, bar_y - 5,
            "1:2000", fontsize=6, ha="center", color="gray")
    return fig


if __name__ == "__main__":
    fig = generate()
    save_figure(fig, "L04_地层柱状图.png")
    print("Done → output/L04_地层柱状图.png")
