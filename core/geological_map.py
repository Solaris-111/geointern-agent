"""平面地质图 — 区域地质图生成器.

用 shapely 构建地层多边形，matplotlib 渲染。
地表出露界线由 DEM 等高线 + 地层产状推算。

输入格式: 修改 FORMATION_POLYGONS / FAULTS / ATTITUDES 即可生成自己的地质图。
"""

import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Polygon, LineString, Point, box
from shapely import affinity
from scipy.interpolate import griddata
from geo_plotting import (
    setup_chinese_font, LITHOLOGY, AGE_COLORS,
    add_scale_bar, add_north_arrow, add_geological_legend,
    draw_strike_dip, add_text_scale, save_figure,
)

setup_chinese_font()

# ══════════════════════════════════════════════════════════════════
# 数据定义 — 修改这里生成你自己的地质图
# ══════════════════════════════════════════════════════════════════

MAP_EXTENT = (0, 5000, 0, 4000)    # (xmin, xmax, ymin, ymax) 单位: 米

# DEM: 散点高程 → 插值网格
def _make_dem():
    """生成演示用 DEM (太平山地区合成数据)."""
    np.random.seed(42)
    n_pts = 200
    xs = np.random.uniform(MAP_EXTENT[0], MAP_EXTENT[1], n_pts)
    ys = np.random.uniform(MAP_EXTENT[2], MAP_EXTENT[3], n_pts)
    zs = (300 + 150 * np.exp(-((xs - 2500)**2 + (ys - 2000)**2) / 1500**2)
          - 80 * np.exp(-((xs - 3500)**2 + (ys - 2800)**2) / 800**2)
          + 30 * np.sin(xs / 400) * np.cos(ys / 350)
          + np.random.normal(0, 8, n_pts))
    return xs, ys, zs

# 地层多边形 (shapely Polygon, 边界简化)
def _make_formation_polygons():
    """生成演示用地层多边形."""
    polys = []

    # 核部: 马家沟组 O₁m 灰岩 — 背斜核部，在中央出露
    o1m = Point(2600, 2000).buffer(700)
    o1m = o1m.intersection(box(*MAP_EXTENT))
    polys.append(("O₁m", "马家沟组", "灰岩", o1m))

    # 本溪组 C₂b — 白云岩，环绕核部
    c2b_ring = Point(2600, 2000).buffer(1200).difference(Point(2600, 2000).buffer(700))
    c2b_ring = c2b_ring.intersection(box(*MAP_EXTENT))
    polys.append(("C₂b", "本溪组", "白云岩", c2b_ring))

    # 铁岭组 Jxt — 再外围
    jxt_ring = Point(2600, 2000).buffer(1700).difference(Point(2600, 2000).buffer(1200))
    jxt_ring = jxt_ring.intersection(box(*MAP_EXTENT))
    polys.append(("Jxt", "铁岭组", "千枚岩", jxt_ring))

    # 下马岭组 Qbx — 页岩/砂岩，东北区
    qbx = Point(1200, 2600).buffer(900)
    qbx = qbx.intersection(box(*MAP_EXTENT))
    polys.append(("Qbx", "下马岭组", "页岩", qbx))

    # 第四系 Q — 河谷冲积物
    river = LineString([(0, 1200), (1500, 1000), (3200, 800), (4500, 600)])
    q_buf = river.buffer(180)
    q_buf = q_buf.intersection(box(*MAP_EXTENT))
    polys.append(("Qh", "第四系", "第四系冲积物", q_buf))

    # 花岗岩侵入体 γ — 西北角
    granite = Point(800, 3200).buffer(500)
    granite = granite.intersection(box(*MAP_EXTENT))
    polys.append(("γ", "花岗岩体", "花岗岩", granite))

    return polys

# 断层 [(x1,y1, x2,y2, type, name), ...]
MAP_FAULTS = [
    (1800, 800,  3200, 2200, "normal",  "F1 正断层"),
    (1200, 3000, 2200, 1500, "reverse", "F2 逆断层"),
    (3500, 3200, 4200, 800,  "normal",  "F3 正断层"),
]

# 产状 [(x, y, strike°, dip°), ...]
MAP_ATTITUDES = [
    (2200, 1800, 45,  32),
    (2800, 2000, 135, 28),
    (2600, 1400, 90,  35),
    (1800, 2200, 30,  25),
    (3200, 2400, 120, 30),
    (1500, 1500, 75,  22),
    (3400, 1500, 160, 26),
    (1000, 2800, 50,  18),
    (3800, 2800, 140, 20),
]

TITLE = "周口店太平山地区地质图"
FIG_SIZE = (14, 11)

# ══════════════════════════════════════════════════════════════════

def generate():
    xs_dem, ys_dem, zs_dem = _make_dem()
    formations = _make_formation_polygons()

    fig, ax = plt.subplots(figsize=FIG_SIZE)

    # ── DEM 底图 (等高线 + 山体阴影) ──
    xi = np.linspace(MAP_EXTENT[0], MAP_EXTENT[1], 200)
    yi = np.linspace(MAP_EXTENT[2], MAP_EXTENT[3], 200)
    xi_grid, yi_grid = np.meshgrid(xi, yi)
    zi = griddata((xs_dem, ys_dem), zs_dem, (xi_grid, yi_grid), method="cubic")

    # 山体阴影 (简易 hillshade)
    dx, dy = np.gradient(zi, xi[1] - xi[0], yi[1] - yi[0])
    slope = np.pi / 2 - np.arctan(np.sqrt(dx**2 + dy**2))
    aspect = np.arctan2(-dx, dy)
    azimuth = np.radians(315)
    altitude = np.radians(45)
    shade = np.sin(altitude) * np.sin(slope) + np.cos(altitude) * np.cos(slope) * np.cos(azimuth - aspect)
    shade = (shade - shade.min()) / (shade.max() - shade.min()) * 0.35 + 0.65

    ax.imshow(shade, extent=MAP_EXTENT, origin="lower", cmap="Greys_r",
              alpha=0.35, zorder=0)

    # 等高线
    levels = np.arange(100, 550, 20)
    cs = ax.contour(xi, yi, zi, levels=levels, colors="0.6", linewidths=0.4, zorder=1)
    ax.clabel(cs, cs.levels[::3], inline=True, fontsize=5, fmt="%d")

    # ── 地层多边形 ──
    for code, name, lith, geom in formations:
        if geom.is_empty:
            continue
        info = LITHOLOGY.get(lith, {"color": "#E8E0D0", "hatch": ".."})
        if geom.geom_type == "Polygon":
            _fill_polygon(ax, geom, info["color"], info["hatch"])
        elif geom.geom_type == "MultiPolygon":
            for p in geom.geoms:
                if not p.is_empty:
                    _fill_polygon(ax, p, info["color"], info["hatch"])

    # ── 断层 ──
    for x1, y1, x2, y2, ftype, name in MAP_FAULTS:
        ax.plot([x1, x2], [y1, y2], "k-", linewidth=2.2, zorder=3)
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        if ftype == "normal":
            ax.plot([mid_x - 6, mid_x + 6], [mid_y + 30, mid_y - 30], "k-", linewidth=1.2)
        elif ftype == "reverse":
            for off in [-8, 0, 8]:
                ax.plot([mid_x + off - 6, mid_x + off + 6], [mid_y + 30, mid_y - 30], "k-", linewidth=0.7)
        ax.text(mid_x + 40, mid_y, name, fontsize=8, color="darkred",
                fontweight="bold", zorder=5,
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8))

    # ── 产状 ──
    for x, y, strike, dip in MAP_ATTITUDES:
        draw_strike_dip(ax, x, y, strike, dip, length=60, fontsize=7)

    # ── 地层标注 ──
    for code, name, lith, geom in formations:
        if geom.is_empty:
            continue
        if geom.geom_type == "Polygon":
            c = geom.centroid
            if not c.is_empty:
                ax.text(c.x, c.y, f"{code}\n{name}", ha="center", va="center",
                        fontsize=7.5, fontweight="bold",
                        bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8), zorder=4)
        elif geom.geom_type == "MultiPolygon":
            for p in geom.geoms:
                if p.is_empty:
                    continue
                c = p.centroid
                if not c.is_empty:
                    ax.text(c.x, c.y, f"{code}\n{name}", ha="center", va="center",
                            fontsize=6.5, fontweight="bold",
                            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8), zorder=4)

    # ── 坐标网 ──
    ax.set_xlim(MAP_EXTENT[0], MAP_EXTENT[1])
    ax.set_ylim(MAP_EXTENT[2], MAP_EXTENT[3])
    ax.set_xticks(np.arange(0, 5200, 500))
    ax.set_yticks(np.arange(0, 4200, 500))
    ax.set_xticklabels([f"{x/1000:.1f}" for x in np.arange(0, 5200, 500)], fontsize=7)
    ax.set_yticklabels([f"{y/1000:.1f}" for y in np.arange(0, 4200, 500)], fontsize=7)
    ax.grid(True, alpha=0.2, linestyle="--")
    ax.set_xlabel("X / km", fontsize=10)
    ax.set_ylabel("Y / km", fontsize=10)

    # ── 图例 ──
    legend_items = []
    seen = set()
    for code, name, lith, _ in formations:
        if name not in seen:
            seen.add(name)
            info = LITHOLOGY.get(lith, {})
            legend_items.append((f"{code} {name}", info.get("color", "#ccc"), info.get("hatch", "")))
    add_geological_legend(ax, legend_items, loc="lower right", fontsize=7.5, ncol=2)

    # ── 比例尺 & 指北针 ──
    add_scale_bar(ax, length=500, label="500 m", fontsize=9)
    add_north_arrow(ax, x=0.91, y=0.91, size=0.055)

    ax.set_title(TITLE, fontsize=16, fontweight="bold", pad=14)
    return fig


def _fill_polygon(ax, geom, color, hatch):
    x, y = geom.exterior.xy
    ax.fill(x, y, facecolor=color, alpha=0.55, edgecolor="0.3",
            linewidth=0.6, hatch=hatch, zorder=2)


if __name__ == "__main__":
    fig = generate()
    save_figure(fig, "geological_map.png")
    print("平面地质图完成 — 可在 GIS 中叠加坐标网格、添加图框.")
