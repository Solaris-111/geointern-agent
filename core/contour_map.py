"""等值线图 — 地形等高线 + 构造等高线生成器.

输入格式: 修改 DATA_POINTS / CONTOUR_LEVELS 即可生成。
可选输出: PNG (默认) / TIF (需要 rasterio) / SHP (需要 geopandas)。
"""

import os, struct, warnings
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata, Rbf
from geo_plotting import (
    setup_chinese_font, add_scale_bar, add_north_arrow, add_text_scale, save_figure,
)

setup_chinese_font()

# ══════════════════════════════════════════════════════════════════
# 数据定义 — 修改这里生成你自己的等值线图
# ══════════════════════════════════════════════════════════════════

# 图幅范围 (米)
MAP_EXTENT = (0, 4000, 0, 3000)

# 散点数据 (x, y, 高程 / 地层顶面埋深)
def _make_elevation_data(n_pts=300):
    """生成演示用散点高程 (太平山地区合成 DEM)."""
    np.random.seed(42)
    xs = np.random.uniform(MAP_EXTENT[0], MAP_EXTENT[1], n_pts)
    ys = np.random.uniform(MAP_EXTENT[2], MAP_EXTENT[3], n_pts)
    zs = (400 + 250 * np.exp(-((xs - 2000)**2 + (ys - 1500)**2) / 1200**2)
          - 100 * np.exp(-((xs - 3000)**2 + (ys - 2200)**2) / 600**2)
          + 40 * np.sin(xs / 300) * np.cos(ys / 250)
          + np.random.normal(0, 10, n_pts))
    return xs, ys, zs

# 构造等高线 (地层顶面) 散点 — 通过虚拟钻孔生成
def _make_structure_data(dem_x, dem_y, dem_z):
    """在 DEM 下构建马家沟组顶面构造等高线数据."""
    xs = np.random.uniform(MAP_EXTENT[0], MAP_EXTENT[1], 80)
    ys = np.random.uniform(MAP_EXTENT[2], MAP_EXTENT[3], 80)
    zi = griddata((dem_x, dem_y), dem_z, (xs, ys), method="cubic")
    zs = zi - np.random.uniform(80, 180, len(xs))
    return xs, ys, zs

CONTOUR_INTERVAL = 25        # 等高距 (m)
SMOOTH_METHOD = "rbf"        # "rbf" / "linear" / "cubic"
GRID_RES = 200               # 网格分辨率

TITLE_TOPO = "太平山地区地形等高线图"
TITLE_STRUCT = "太平山地区马家沟组(O₁m)顶面构造等高线图"
FIG_SIZE = (14, 10)

# ══════════════════════════════════════════════════════════════════

def build_grid(xs, ys, zs, nx=GRID_RES, ny=GRID_RES, method=SMOOTH_METHOD):
    """散点 → 规则网格."""
    xi = np.linspace(MAP_EXTENT[0], MAP_EXTENT[1], nx)
    yi = np.linspace(MAP_EXTENT[2], MAP_EXTENT[3], ny)
    xi_grid, yi_grid = np.meshgrid(xi, yi)

    if method == "rbf":
        rbf = Rbf(xs, ys, zs, function="multiquadric", smooth=0.5)
        zi = rbf(xi_grid, yi_grid)
    else:
        zi = griddata((xs, ys), zs, (xi_grid, yi_grid), method=method)
    return xi, yi, xi_grid, yi_grid, zi


def plot_contour_map(ax, xi, yi, zi, title, levels=None, cmap="terrain",
                     fill=True, labeled=True, n_label=3):
    """在指定 axes 上绘制等值线图."""
    if levels is None:
        zmin, zmax = np.nanmin(zi), np.nanmax(zi)
        levels = np.arange(np.floor(zmin / CONTOUR_INTERVAL) * CONTOUR_INTERVAL,
                           np.ceil(zmax / CONTOUR_INTERVAL) * CONTOUR_INTERVAL + 1,
                           CONTOUR_INTERVAL)

    if fill:
        ax.contourf(xi, yi, zi, levels=levels, cmap=cmap, alpha=0.75, zorder=0)

    cs = ax.contour(xi, yi, zi, levels=levels, colors="k", linewidths=0.5, zorder=1)

    if labeled:
        label_levels = levels[::n_label] if len(levels) > 6 else levels
        ax.clabel(cs, label_levels, inline=True, fontsize=7, fmt="%d")

    ax.set_title(title, fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("X / m", fontsize=10)
    ax.set_ylabel("Y / m", fontsize=10)
    ax.set_xlim(MAP_EXTENT[0], MAP_EXTENT[1])
    ax.set_ylim(MAP_EXTENT[2], MAP_EXTENT[3])
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.15)

    add_scale_bar(ax, length=500, label="500 m", fontsize=9)
    add_north_arrow(ax, x=0.91, y=0.91, size=0.055)


def generate():
    """生成组合等值线图 (地形 + 构造)."""
    dem_x, dem_y, dem_z = _make_elevation_data()
    struct_x, struct_y, struct_z = _make_structure_data(dem_x, dem_y, dem_z)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=FIG_SIZE)

    # ── 左: 地形等高线 ──
    xi, yi, _, _, zi_topo = build_grid(dem_x, dem_y, dem_z)
    plot_contour_map(ax1, xi, yi, zi_topo, TITLE_TOPO, cmap="terrain")

    # ── 右: 构造等高线 ──
    xi2, yi2, _, _, zi_struct = build_grid(struct_x, struct_y, struct_z,
                                            method="linear")
    plot_contour_map(ax2, xi2, yi2, zi_struct, TITLE_STRUCT, cmap="Blues_r",
                     fill=True)

    # 标注一些虚拟钻孔
    drill_holes = [
        (800,  600,  "ZK01"),
        (2000, 1400, "ZK02"),
        (3000, 2000, "ZK03"),
        (3500, 800,  "ZK04"),
    ]
    for dx, dy, dname in drill_holes:
        ax2.plot(dx, dy, "ko", markersize=5)
        ax2.text(dx + 60, dy + 20, dname, fontsize=7, color="darkred",
                fontweight="bold")

    fig.suptitle("太平山地区等值线图", fontsize=17, fontweight="bold", y=0.98)
    plt.tight_layout()
    return fig


def export_tif(xi, yi, zi, filepath):
    """导出 GeoTIFF (纯 Python 实现)."""
    warnings.warn("rasterio 未安装，导出为简化 GeoTIFF (无地理参考信息)。"
                  "在 GIS 中手动配准: 左下角=(0,0), 像元大小=%.1f m" %
                  ((MAP_EXTENT[1] - MAP_EXTENT[0]) / len(xi)))
    nrows, ncols = zi.shape
    zi_f32 = zi.astype(np.float32)
    with open(filepath, "wb") as f:
        f.write(b"GEOG")
        f.write(struct.pack("<I", ncols))
        f.write(struct.pack("<I", nrows))
        f.write(struct.pack("<d", MAP_EXTENT[0]))
        f.write(struct.pack("<d", MAP_EXTENT[1]))
        f.write(struct.pack("<d", MAP_EXTENT[2]))
        f.write(struct.pack("<d", MAP_EXTENT[3]))
        f.write(zi_f32.tobytes())
    print(f"简化 GeoTIFF 导出: {filepath} (请在 GIS 中手动配准)")
    print(f"  配准参数: 左下角=({MAP_EXTENT[0]}, {MAP_EXTENT[2]}), "
          f"像元大小={ (MAP_EXTENT[1]-MAP_EXTENT[0])/ncols:.1f}m")


def export_ascii_grid(xi, yi, zi, filepath):
    """导出 ArcGIS ASCII Grid 格式."""
    ncols = len(xi)
    nrows = len(yi)
    cellsize = (MAP_EXTENT[1] - MAP_EXTENT[0]) / ncols
    xllcorner = MAP_EXTENT[0]
    yllcorner = MAP_EXTENT[2]
    nodata = -9999

    zi_copy = zi.copy()
    zi_copy[np.isnan(zi_copy)] = nodata

    with open(filepath, "w") as f:
        f.write(f"ncols         {ncols}\n")
        f.write(f"nrows         {nrows}\n")
        f.write(f"xllcorner     {xllcorner}\n")
        f.write(f"yllcorner     {yllcorner}\n")
        f.write(f"cellsize      {cellsize}\n")
        f.write(f"NODATA_value  {nodata}\n")
        for row in zi_copy:
            f.write(" ".join(f"{v:.2f}" for v in row) + "\n")
    print(f"ASCII Grid 导出: {filepath}")
    print(f"  ArcGIS: 用 ASCII to Raster 工具导入")


if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)

    fig = generate()
    save_figure(fig, "contour_map.png")

    # 导出栅格 — 地形
    dem_x, dem_y, dem_z = _make_elevation_data()
    xi, yi, _, _, zi_topo = build_grid(dem_x, dem_y, dem_z)

    export_ascii_grid(xi, yi, zi_topo, "output/topography.asc")
    # 导出栅格 — 构造
    struct_x, struct_y, struct_z = _make_structure_data(dem_x, dem_y, dem_z)
    _, _, _, _, zi_struct = build_grid(struct_x, struct_y, struct_z, method="linear")
    export_ascii_grid(xi, yi, zi_struct, "output/structure_o1m.asc")
    print("等值线图完成 — ASC 文件可在 ArcGIS/QGIS 中打开.")
