"""自定义岩性图案渲染 — 绕过 matplotlib hatch 密度不可调的硬限制.

为周口店最常见的 6 种岩性提供 clipped primitive 渲染:
  灰岩 — 砖块纹 (水平线 + 交错短竖线)
  白云岩 — X 交叉纹
  砂岩 — 均匀随机点纹
  泥岩 — 水平平行虚线
  砾岩 — 大小不一的圆圈
  大理岩 — 方格纹

用法:
    from pattern_primitives import fill_primitive
    fill_primitive(ax, poly_x, poly_y, "灰岩")
"""

import numpy as np
import matplotlib
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.collections import LineCollection, PathCollection
from matplotlib.transforms import Affine2D


# ── 密度参数 ───────────────────────────────────────────────────────
# 所有参数单位: 数据坐标 (km / m)

_PARAMS = {
    "灰岩": {
        "h_spacing": 0.015,    # 水平线间距 (km, ~= 15m @ 1:1000)
        "v_dash_len": 0.008,   # 竖线长度
        "v_dash_spacing": 0.030,  # 竖线水平间距
        "lw": 0.4,
    },
    "白云岩": {
        "spacing": 0.025,      # X 标记间距
        "size": 0.006,         # X 半边长
        "lw": 0.4,
    },
    "砂岩": {
        "density": 100,        # 每 km² 点数
        "size": 0.5,           # 点半径 (points)
        "lw": 0.3,
    },
    "泥岩": {
        "h_spacing": 0.012,    # 水平线间距
        "dash_len": 0.020,     # 虚线长度
        "gap_len": 0.008,      # 虚线间隙
        "lw": 0.35,
    },
    "砾岩": {
        "density": 40,         # 每 km² 圆圈数
        "min_radius": 0.002,   # 最小半径
        "max_radius": 0.007,   # 最大半径
        "lw": 0.5,
    },
    "大理岩": {
        "spacing": 0.022,      # 方格间距
        "size": 0.005,         # 方格半边长
        "lw": 0.35,
    },
}


def fill_primitive(ax, poly_x, poly_y, lithology: str):
    """为多边形填充自定义岩性图案."""
    fn = _DISPATCH.get(lithology)
    if fn is None:
        return  # 不在此 6 种内，fallback 到标准 hatch
    fn(ax, poly_x, poly_y)


def _make_clip(ax, poly_x, poly_y):
    """创建 clip path."""
    verts = list(zip(poly_x, poly_y))
    codes = [Path.MOVETO] + [Path.LINETO] * (len(verts) - 1) + [Path.CLOSEPOLY]
    verts.append(verts[0])
    return Path(verts, codes)


def _clip_bounds(poly_x, poly_y):
    """多边形包围盒."""
    return min(poly_x), max(poly_x), min(poly_y), max(poly_y)


# ═══════════════════════════════════════════════════════════════════
# 灰岩 — 砖块纹
# ═══════════════════════════════════════════════════════════════════

def _fill_limestone(ax, poly_x, poly_y):
    """水平平行线 + 交错短竖线 → 砖块效果."""
    p = _PARAMS["灰岩"]
    xmin, xmax, ymin, ymax = _clip_bounds(poly_x, poly_y)
    clip = _make_clip(ax, poly_x, poly_y)

    # 水平线
    h_lines = []
    y = ymin
    while y <= ymax:
        h_lines.append([(xmin, y), (xmax, y)])
        y += p["h_spacing"]

    # 交错短竖线 (奇数行和偶数行错开)
    for row, y_line in enumerate(np.arange(ymin, ymax, p["h_spacing"])):
        offset = p["v_dash_spacing"] / 2 if row % 2 == 1 else 0
        x = xmin + offset
        while x <= xmax:
            h_lines.append([(x, y_line - p["v_dash_len"] / 2),
                           (x, y_line + p["v_dash_len"] / 2)])
            x += p["v_dash_spacing"]

    if h_lines:
        lc = LineCollection(h_lines, colors="#333333", linewidths=p["lw"],
                           clip_path=PathPatch(clip, transform=ax.transData))
        ax.add_collection(lc)


# ═══════════════════════════════════════════════════════════════════
# 白云岩 — X 交叉纹
# ═══════════════════════════════════════════════════════════════════

def _fill_dolomite(ax, poly_x, poly_y):
    """均匀分布的 X 标记."""
    p = _PARAMS["白云岩"]
    xmin, xmax, ymin, ymax = _clip_bounds(poly_x, poly_y)
    clip = _make_clip(ax, poly_x, poly_y)

    lines = []
    s = p["spacing"]
    half = p["size"]
    for cx in np.arange(xmin, xmax, s):
        for cy in np.arange(ymin, ymax, s):
            lines.append([(cx - half, cy - half), (cx + half, cy + half)])
            lines.append([(cx + half, cy - half), (cx - half, cy + half)])

    if lines:
        lc = LineCollection(lines, colors="#333333", linewidths=p["lw"],
                           clip_path=PathPatch(clip, transform=ax.transData))
        ax.add_collection(lc)


# ═══════════════════════════════════════════════════════════════════
# 砂岩 — 均匀随机点纹
# ═══════════════════════════════════════════════════════════════════

def _fill_sandstone(ax, poly_x, poly_y):
    """密集的均匀分布小圆点."""
    p = _PARAMS["砂岩"]
    xmin, xmax, ymin, ymax = _clip_bounds(poly_x, poly_y)
    clip = _make_clip(ax, poly_x, poly_y)

    area = (xmax - xmin) * (ymax - ymin)
    n_points = max(30, int(area * p["density"]))

    # Poisson-disc 近似: 网格抖动
    grid_n = int(np.ceil(np.sqrt(n_points * 1.5)))
    xs = np.linspace(xmin, xmax, grid_n)
    ys = np.linspace(ymin, ymax, grid_n)
    rng = np.random.RandomState(42)

    points = []
    for x in xs:
        for y in ys:
            dx = (xs[1] - xs[0]) * 0.4 * (rng.random() - 0.5)
            dy = (ys[1] - ys[0]) * 0.4 * (rng.random() - 0.5)
            px, py = x + dx, y + dy
            # 粗略多边形包含测试 (用 bounding box 近似)
            if xmin <= px <= xmax and ymin <= py <= ymax:
                points.append((px, py))

    if points:
        pc = PathCollection(
            [Path.circle((px, py), p["size"] * 0.001) for px, py in points[:n_points]],
            facecolors="#333333", edgecolors="none",
            clip_path=PathPatch(clip, transform=ax.transData),
        )
        ax.add_collection(pc)


# ═══════════════════════════════════════════════════════════════════
# 泥岩 — 水平平行虚线
# ═══════════════════════════════════════════════════════════════════

def _fill_mudstone(ax, poly_x, poly_y):
    """水平平行虚线."""
    p = _PARAMS["泥岩"]
    xmin, xmax, ymin, ymax = _clip_bounds(poly_x, poly_y)
    clip = _make_clip(ax, poly_x, poly_y)

    lines = []
    y = ymin
    while y <= ymax:
        x = xmin
        while x <= xmax:
            lines.append([(x, y), (min(x + p["dash_len"], xmax), y)])
            x += p["dash_len"] + p["gap_len"]
        y += p["h_spacing"]

    if lines:
        lc = LineCollection(lines, colors="#333333", linewidths=p["lw"],
                           clip_path=PathPatch(clip, transform=ax.transData))
        ax.add_collection(lc)


# ═══════════════════════════════════════════════════════════════════
# 砾岩 — 大小不一的圆圈
# ═══════════════════════════════════════════════════════════════════

def _fill_conglomerate(ax, poly_x, poly_y):
    """随机分布的大小不一圆圈."""
    p = _PARAMS["砾岩"]
    xmin, xmax, ymin, ymax = _clip_bounds(poly_x, poly_y)
    clip = _make_clip(ax, poly_x, poly_y)

    area = (xmax - xmin) * (ymax - ymin)
    n = max(10, int(area * p["density"]))
    rng = np.random.RandomState(42)

    circles = []
    for _ in range(n * 2):  # 多生成一些，clip 会裁掉外面的
        cx = xmin + rng.random() * (xmax - xmin)
        cy = ymin + rng.random() * (ymax - ymin)
        r = p["min_radius"] + rng.random() * (p["max_radius"] - p["min_radius"])
        circles.append(Path.circle((cx, cy), r))

    if circles:
        pc = PathCollection(
            circles[:n],
            facecolors="none", edgecolors="#333333", linewidths=p["lw"],
            clip_path=PathPatch(clip, transform=ax.transData),
        )
        ax.add_collection(pc)


# ═══════════════════════════════════════════════════════════════════
# 大理岩 — 方格纹
# ═══════════════════════════════════════════════════════════════════

def _fill_marble(ax, poly_x, poly_y):
    """均匀网格小方块 (偶填奇空交替)."""
    p = _PARAMS["大理岩"]
    xmin, xmax, ymin, ymax = _clip_bounds(poly_x, poly_y)
    clip = _make_clip(ax, poly_x, poly_y)

    s = p["spacing"]
    h = p["size"]

    # 填充方块 + 空心方块
    filled_rects = []
    empty_rects = []
    for cx in np.arange(xmin, xmax, s):
        for cy in np.arange(ymin, ymax, s):
            verts = [(cx - h, cy - h), (cx + h, cy - h),
                    (cx + h, cy + h), (cx - h, cy + h), (cx - h, cy - h)]
            if (round(cx / s) + round(cy / s)) % 2 == 0:
                filled_rects.append(verts)
            else:
                empty_rects.append(verts)

    # 填充方块 (facecolor=灰色, 有边框)
    if filled_rects:
        from matplotlib.patches import Polygon as MplPoly
        for verts in filled_rects:
            poly = MplPoly(verts, facecolor="#e0e0e0", edgecolor="#333333",
                         linewidth=p["lw"], clip_path=PathPatch(clip, transform=ax.transData))
            ax.add_patch(poly)

    # 空心方块 (只有边框)
    if empty_rects:
        from matplotlib.patches import Polygon as MplPoly
        for verts in empty_rects:
            poly = MplPoly(verts, facecolor="none", edgecolor="#333333",
                         linewidth=p["lw"], clip_path=PathPatch(clip, transform=ax.transData))
            ax.add_patch(poly)


# ── 调度 ───────────────────────────────────────────────────────────
_DISPATCH = {
    "灰岩":   _fill_limestone,
    "石灰岩": _fill_limestone,
    "limestone": _fill_limestone,
    "白云岩": _fill_dolomite,
    "dolomite": _fill_dolomite,
    "砂岩":   _fill_sandstone,
    "sandstone": _fill_sandstone,
    "泥岩":   _fill_mudstone,
    "mudstone": _fill_mudstone,
    "砾岩":   _fill_conglomerate,
    "conglomerate": _fill_conglomerate,
    "大理岩": _fill_marble,
    "marble": _fill_marble,
}
