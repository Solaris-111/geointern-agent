"""三维地质模型 — 地表 DEM + 地下地层界面三维可视化.

技术: gempy (隐式建模) 为主，matplotlib 3D 块体图为 fallback。

输入格式: 修改 FORMATIONS / DRILL_HOLES 或 INTERFACE_POINTS。
"""

import os, sys
import numpy as np
import matplotlib.pyplot as plt
from geo_plotting import setup_chinese_font, save_figure

setup_chinese_font()

# ══════════════════════════════════════════════════════════════════
# 数据定义
# ══════════════════════════════════════════════════════════════════

# 地层序列 (从顶到底)
FORMATIONS = ["第四系", "景儿峪组", "长龙山组", "下马岭组", "铁岭组", "洪水庄组", "马家沟组"]
FM_COLORS = {
    "第四系":    "#F5F0E0",
    "景儿峪组":  "#E8DCC8",
    "长龙山组":  "#D4C5A0",
    "下马岭组":  "#C8B890",
    "铁岭组":    "#C8B080",
    "洪水庄组":  "#B8A870",
    "马家沟组":  "#A0C8D0",
}

# 范围 (米)
EXTENT = (0, 3000, 0, 2500, -600, 350)   # xmin, xmax, ymin, ymax, zmin, zmax

# ── 界面点 (x, y, z) 每个地层的底部控制点 ──
INTERFACE_POINTS = {
    "第四系": [   # 地表附近
        (500, 400, 280), (1500, 500, 310), (2500, 600, 290),
        (800, 1500, 300), (2000, 1600, 330), (1200, 2200, 290),
        (2600, 2000, 310), (400, 2000, 260), (2800, 1200, 300),
    ],
    "景儿峪组": [
        (600, 500, 180), (1500, 600, 200), (2500, 700, 190),
        (800, 1500, 200), (2000, 1600, 210), (1200, 2200, 180),
        (2600, 2000, 200), (500, 2000, 160),
    ],
    "长龙山组": [
        (600, 500, 80), (1500, 600, 100), (2500, 700, 90),
        (800, 1500, 100), (2000, 1600, 110), (1200, 2200, 80),
        (2600, 2000, 100), (500, 2000, 60),
    ],
    "下马岭组": [
        (600, 500, -30), (1500, 600, -10), (2500, 700, -20),
        (800, 1500, -10), (2000, 1600, 0), (1200, 2200, -30),
        (2600, 2000, -10), (500, 2000, -50),
    ],
    "铁岭组": [
        (600, 500, -150), (1500, 600, -130), (2500, 700, -140),
        (800, 1500, -130), (2000, 1600, -120), (1200, 2200, -160),
        (2600, 2000, -140),
    ],
    "洪水庄组": [
        (600, 500, -270), (1500, 600, -250), (2500, 700, -260),
        (800, 1500, -260), (2000, 1600, -240), (1200, 2200, -280),
        (2600, 2000, -260),
    ],
    "马家沟组": [
        (600, 500, -400), (1500, 600, -380), (2500, 700, -390),
        (800, 1500, -390), (2000, 1600, -370), (1200, 2200, -410),
        (2600, 2000, -400),
    ],
}

TITLE = "太平山地区三维地质模型"
FIG_SIZE = (16, 7)

# ══════════════════════════════════════════════════════════════════
# 方案 A: GemPy 隐式建模
# ══════════════════════════════════════════════════════════════════

def model_with_gempy():
    """使用 GemPy 进行隐式三维地质建模."""
    try:
        import gempy as gp
        import gempy_viewer as gpv
    except ImportError:
        print("GemPy 不可用，回退到 matplotlib 3D 块体图.")
        return None

    print("使用 GemPy 进行隐式建模...")

    model = gp.data.GeoModel()
    gp.init_data(model, extent=list(EXTENT), resolution=[50, 50, 50])

    # 添加地层序列
    gp.add_surface_points(model, x=[], y=[], z=[], formation=[])
    elements = []
    for fm_name in reversed(FORMATIONS):
        pts = INTERFACE_POINTS.get(fm_name, [])
        elements.append([fm_name] + [pts] if pts else [fm_name, []])
        gp.map_stack_to_surfaces(model, {"Strata": [fm_name]})

    # 简化: 创建 surface points
    x_all, y_all, z_all, fm_all = [], [], [], []
    for fm_name in FORMATIONS:
        pts = INTERFACE_POINTS.get(fm_name, [])
        for px, py, pz in pts:
            x_all.append(px)
            y_all.append(py)
            z_all.append(pz)
            fm_all.append(fm_name)

    if len(x_all) > 0:
        model.structural_frame.add_surface_points(
            X=np.array(x_all), Y=np.array(y_all), Z=np.array(z_all),
            formation_names=fm_all
        )

    # 计算
    try:
        gp.compute_model(model)
        # 3D 可视化
        plot = gpv.plot_3d(model, show=False)
        fig = plot.fig
        fig.suptitle(TITLE, fontsize=15, fontweight="bold")
        return fig
    except Exception as e:
        print(f"GemPy 计算失败: {e}")
        return None


# ══════════════════════════════════════════════════════════════════
# 方案 B: matplotlib 3D 块体图 (fallback)
# ══════════════════════════════════════════════════════════════════

def model_with_matplotlib():
    """使用 matplotlib 3D 生成多层块体模型."""
    from scipy.interpolate import Rbf

    print("使用 matplotlib 3D 生成块体模型...")

    xi = np.linspace(EXTENT[0], EXTENT[1], 60)
    yi = np.linspace(EXTENT[2], EXTENT[3], 60)
    XI, YI = np.meshgrid(xi, yi)

    # 为每个地层界面插值
    surfaces = {}
    for fm_name in FORMATIONS:
        pts = INTERFACE_POINTS.get(fm_name, [])
        if not pts:
            continue
        px, py, pz = zip(*pts)
        rbf = Rbf(np.array(px), np.array(py), np.array(pz),
                  function="multiquadric", smooth=0.5)
        surfaces[fm_name] = rbf(XI, YI)

    fig = plt.figure(figsize=FIG_SIZE)

    # ── 子图 1: 三维爆炸视图 ──
    ax1 = fig.add_subplot(1, 2, 1, projection="3d")
    z_offset = 0
    for i, fm_name in enumerate(reversed(FORMATIONS)):
        if fm_name not in surfaces:
            continue
        color = FM_COLORS.get(fm_name, "#CCCCCC")
        zi = surfaces[fm_name] + z_offset
        ax1.plot_surface(XI, YI, zi, color=color, alpha=0.7, edgecolor="0.3",
                         linewidth=0.05, rstride=2, cstride=2)
        # 侧面
        for edge_x, edge_y, edge_fn in [
            (XI[0, :],  YI[0, :],  lambda: XI[0, :]),
            (XI[-1, :], YI[-1, :], lambda: XI[-1, :]),
            (XI[:, 0],  YI[:, 0],  lambda: XI[:, 0]),
            (XI[:, -1], YI[:, -1], lambda: XI[:, -1]),
        ]:
            ax1.plot(edge_x, edge_y, zi[0, :] if edge_fn().shape == XI[0, :].shape else zi[:, 0],
                     color="0.4", linewidth=0.3, alpha=0.5)

        mid_x, mid_y = 2800, 2500
        mid_z = surfaces[fm_name].mean() + z_offset
        ax1.text(mid_x, mid_y, mid_z, fm_name, fontsize=7, ha="center",
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.7))
        z_offset += 50

    ax1.set_xlabel("X / m"); ax1.set_ylabel("Y / m"); ax1.set_zlabel("Z / m")
    ax1.set_title("地层界面 (爆炸视图)", fontsize=11, fontweight="bold")
    # 调整视角避免 label 重叠
    ax1.view_init(elev=25, azim=-55)

    # ── 子图 2: 块体剖面 ──
    ax2 = fig.add_subplot(1, 2, 2, projection="3d")

    # 地表
    dem_z = None
    for fm_name in FORMATIONS:
        if fm_name in surfaces:
            dem_z = surfaces[fm_name]
            break
    if dem_z is not None:
        ax2.plot_surface(XI, YI, dem_z, color="#E8D8B0", alpha=0.5,
                         edgecolor="0.5", linewidth=0.05, rstride=3, cstride=3)

    # 在剖面位置绘制各地层
    section_y = 1200  # 剖面 Y 坐标
    section_idx = np.argmin(np.abs(yi - section_y))

    for i, fm_name in enumerate(reversed(FORMATIONS)):
        if fm_name not in surfaces:
            continue
        color = FM_COLORS.get(fm_name, "#CCCCCC")
        zi = surfaces[fm_name]
        if i < len(FORMATIONS) - 2:
            zi_below = surfaces.get(list(reversed(FORMATIONS))[i + 1], zi - 100)
        else:
            zi_below = zi - 200

        # 在剖面位置绘制垂直条带
        for sx in np.linspace(EXTENT[0] + 200, EXTENT[1] - 200, 20):
            six = np.argmin(np.abs(xi - sx))
            ax2.plot([sx, sx], [section_y, section_y],
                     [zi_below[section_idx, six], zi[section_idx, six]],
                     color=color, linewidth=4, alpha=0.6, solid_capstyle="butt")

    # 剖面线
    ax2.plot([EXTENT[0], EXTENT[1]], [section_y, section_y],
             [dem_z[section_idx, 0], dem_z[section_idx, -1]],
             "r-", linewidth=2.5, label=f"剖面 Y={section_y}m")

    ax2.set_xlabel("X / m"); ax2.set_ylabel("Y / m"); ax2.set_zlabel("Z / m")
    ax2.set_title("块体模型 + 剖面线", fontsize=11, fontweight="bold")
    ax2.legend(fontsize=8)
    ax2.view_init(elev=25, azim=-55)

    fig.suptitle(TITLE, fontsize=16, fontweight="bold", y=0.96)
    plt.tight_layout()
    return fig


# ══════════════════════════════════════════════════════════════════

def generate():
    os.makedirs("output", exist_ok=True)

    # gempy 2026 API 不兼容，直接使用 matplotlib 3D 块体图
    # 如需 gempy，请参考: https://docs.gempy.org
    return model_with_matplotlib()


if __name__ == "__main__":
    fig = generate()
    if fig is not None:
        save_figure(fig, "geological_3d.png")
        print("三维模型完成 — 可在 GIS/Paraview 中进一步渲染.")
    else:
        print("三维建模失败，请检查依赖.")
