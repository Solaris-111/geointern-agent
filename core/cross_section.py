"""剖面图 — 地质信手剖面/实测剖面图生成器.

输入格式: 修改 TERRAIN_POINTS / FORMATIONS / FAULTS / ATTITUDES 即可生成自己的剖面。
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d
from geo_plotting import (
    setup_chinese_font, LITHOLOGY, add_scale_bar, add_geological_legend,
    draw_vertical_attitude, draw_fault_line, add_text_box, save_figure,
)

setup_chinese_font()

# ══════════════════════════════════════════════════════════════════
# 数据定义 — 修改这里生成你自己的剖面
# ══════════════════════════════════════════════════════════════════

# 地形控制点 (水平距离 m, 高程 m)
TERRAIN_POINTS = [
    (0,   185), (80,  200), (160, 230), (240, 255),
    (320, 270), (400, 260), (480, 240), (560, 250),
    (640, 275), (720, 290), (800, 270), (880, 240),
    (960, 210), (1040, 200), (1120, 215), (1200, 240),
    (1280, 230), (1360, 200), (1440, 180), (1520, 175),
    (1600, 190),
]

# 地层 (从上到下，从新到老排列)
FORMATIONS = [
    {"code": "Qy",  "name": "景儿峪组", "lith": "大理岩",          "z_top": 0,    "z_base": -80},
    {"code": "Qbc", "name": "长龙山组", "lith": "砂岩",            "z_top": -80,  "z_base": -150},
    {"code": "Qbx", "name": "下马岭组", "lith": "页岩",            "z_top": -150, "z_base": -280},
    {"code": "Jxt", "name": "铁岭组",   "lith": "白云岩",          "z_top": -280, "z_base": -380},
    {"code": "Jxh", "name": "洪水庄组", "lith": "千枚岩",          "z_top": -380, "z_base": -480},
    {"code": "O₁m", "name": "马家沟组", "lith": "灰岩",            "z_top": -480, "z_base": -700},
]

# 断层 [(x1,y1, x2,y2, type), ...]  type: normal/reverse/strike-slip
FAULTS = [
    (540, 240, 540, -420, "normal"),
    (900, 265, 900, -500, "reverse"),
    (1280, 230, 1280, -550, "normal"),
]

# 产状 [(x, z, 倾角°), ...] (剖面方向假定近 E-W)
ATTITUDES = [
    (200,  210,  28),
    (380,  255,  32),
    (650,  265,  25),
    (780,  280,  20),
    (1000, 240,  30),
    (1150, 210,  35),
    (1400, 195,  22),
]

# 观测点 [(x, z, 编号), ...]
OBSERVATION_POINTS = [
    (300,  248, "D001"),
    (700,  282, "D002"),
    (1050, 215, "D003"),
]

TITLE = "太平山—龙骨山地质信手剖面图"
AZIMUTH = "剖面方向: 105° (近E-W)"
FIG_SIZE = (18, 8)
DEPTH_EXAG = 1.0              # 垂直放大系数 (1.0 = 真比例)

# ══════════════════════════════════════════════════════════════════

def generate():
    xs = np.array([p[0] for p in TERRAIN_POINTS])
    ys = np.array([p[1] for p in TERRAIN_POINTS])
    f_terrain = interp1d(xs, ys, kind="cubic")
    x_smooth = np.linspace(xs.min(), xs.max(), 400)
    y_smooth = f_terrain(x_smooth)

    fig, ax = plt.subplots(figsize=FIG_SIZE)

    # 地形线
    ax.plot(x_smooth, y_smooth, "k-", linewidth=1.8)
    ax.fill_between(x_smooth, y_smooth, -800, color="0.93", alpha=0.2)

    # 地层
    for fm in FORMATIONS:
        info = LITHOLOGY.get(fm["lith"], {"color": "#E8E0D0", "hatch": ".."})
        z_top = fm["z_top"] * DEPTH_EXAG
        z_base = fm["z_base"] * DEPTH_EXAG
        ax.fill_between(x_smooth, z_top, z_base, facecolor=info["color"],
                        alpha=0.45, hatch=info["hatch"], edgecolor="0.4", linewidth=0.1)
        mid_z = (z_top + z_base) / 2
        ax.text(80, mid_z, f"{fm['code']}\n{fm['name']}\n{fm['lith']}",
                fontsize=7.5, va="center", ha="left",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                           alpha=0.85, edgecolor="gray"))

    # 断层
    for x1, y1, x2, y2, ftype in FAULTS:
        y2_adj = y2 * DEPTH_EXAG
        draw_fault_line(ax, x1, y1, x2, y2_adj, fault_type=ftype, linewidth=2.2)
        ax.text(x1 + 15, (y1 + y2_adj) / 2,
                "正断层" if ftype == "normal" else "逆断层",
                fontsize=8, color="darkred", fontweight="bold")

    # 产状
    for x, z, dip in ATTITUDES:
        z_adj = z * DEPTH_EXAG if z < min(ys) else z
        draw_vertical_attitude(ax, x, z_adj, 0, dip, length=22)

    # 观测点
    for x, z, label in OBSERVATION_POINTS:
        ax.plot(x, z, "ko", markersize=5)
        ax.text(x, z + 12, label, fontsize=7, ha="center", color="blue",
                fontweight="bold")

    # 高地标注
    peaks = [(240, 255, "太平山"), (720, 290, "龙骨山"), (1200, 240, "285高地")]
    for px, py, plabel in peaks:
        ax.plot(px, py, "k^", markersize=7)
        ax.text(px, py + 15, plabel, ha="center", fontsize=9, fontweight="bold")

    # 图例
    legend_items = []
    for fm in FORMATIONS:
        name = fm["name"]
        info = LITHOLOGY.get(fm["lith"], {})
        if name not in [l[0] for l in legend_items]:
            legend_items.append((name, info.get("color", "#ccc"), info.get("hatch", "")))
    add_geological_legend(ax, legend_items, loc="lower left", fontsize=7, ncol=2,
                          bbox_to_anchor=(0.02, -0.06))

    ax.set_title(TITLE, fontsize=15, fontweight="bold", pad=14)
    ax.set_xlabel("水平距离 / m", fontsize=11)
    ax.set_ylabel("高程 / m", fontsize=11)
    ax.set_xlim(-20, max(xs) + 80)
    y_min = min(fm["z_base"] for fm in FORMATIONS) * DEPTH_EXAG - 20
    y_max = max(ys) + 50
    ax.set_ylim(y_min, y_max)
    ax.grid(axis="y", alpha=0.15)

    add_scale_bar(ax, length=100, label="100 m", fontsize=9)
    ax.text(0.98, 0.95, f"{AZIMUTH}\n垂直=水平 (1:1)" if DEPTH_EXAG == 1.0
            else f"{AZIMUTH}\n垂直放大 {DEPTH_EXAG:.1f}x",
            transform=ax.transAxes, fontsize=8, style="italic",
            ha="right", va="top",
            bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.6))

    return fig


if __name__ == "__main__":
    fig = generate()
    save_figure(fig, "cross_section.png")
