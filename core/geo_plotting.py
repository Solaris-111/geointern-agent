"""地质绘图公共工具模块 v2.0 — 比例尺、指北针、产状符号、图例、剖面渲染.

所有信手剖面渲染函数集中在此。section_engine 只负责地质计算和组装，不画共享元素。
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as ticker
from matplotlib.patches import Polygon as MplPolygon
from lithology_patterns import get_pattern, get_category, LITHOLOGY_COLORS

# ── 自定义图案 (优先于标准 hatch) ─────────────────────────────────
_PRIMITIVE_SET = {"灰岩", "白云岩", "砂岩", "泥岩", "砾岩", "大理岩",
                  "石灰岩", "limestone", "dolomite", "sandstone",
                  "mudstone", "conglomerate", "marble"}


def setup_chinese_font():
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    np.random.seed(42)


# ═══════════════════════════════════════════════════════════════════
# 地形
# ═══════════════════════════════════════════════════════════════════

def draw_terrain(ax, dists, elevs, y_bottom, **kwargs):
    """地形填充 + 地形线."""
    lw = kwargs.get("linewidth", 1.5)
    ax.fill_between(dists, elevs, y_bottom, facecolor="white", edgecolor="none", zorder=0)
    ax.plot(dists, elevs, color="black", linewidth=lw, zorder=3)


# ═══════════════════════════════════════════════════════════════════
# 地层填充
# ═══════════════════════════════════════════════════════════════════

def draw_formation_fill(ax, poly_x, poly_y, lithology: str, **kwargs):
    """单遍填充一个地层多边形 — 优先用自定义图案, fallback 到标准 hatch."""
    # 先填白底
    ax.fill(poly_x, poly_y, facecolor="white", edgecolor="#555555",
           linewidth=0.3, alpha=1.0, zorder=kwargs.get("zorder", 1))

    # 自定义图案 (6种常见岩性)
    if lithology in _PRIMITIVE_SET:
        try:
            from pattern_primitives import fill_primitive
            fill_primitive(ax, poly_x, poly_y, lithology)
            return
        except ImportError:
            pass

    # 标准 hatch fallback
    pat = get_pattern(lithology)
    if pat is None:
        pat = get_pattern("灰岩")

    hatch_lw = pat.get("hatch_lw", 0.3)
    with plt.rc_context({"hatch.linewidth": hatch_lw, "hatch.color": "#333333"}):
        ax.fill(poly_x, poly_y, facecolor="none",
                edgecolor="#555555", linewidth=0.3,
                hatch=pat["hatch"], alpha=1.0, zorder=kwargs.get("zorder", 1) + 0.5)


# ═══════════════════════════════════════════════════════════════════
# 接触界线
# ═══════════════════════════════════════════════════════════════════

def draw_contact_line(ax, x_top, y_top, x_bot, y_bot, contact_type="conformable",
                      is_observed=True, **kwargs):
    """画一条接触界线。

    实测整合:   实线 1.2pt 黑色
    推测整合:   虚线 0.6pt 黑色
    不整合:     地表锯齿 + 地下粗虚线 (需单独调用 draw_unconformity_wave)
    """
    if contact_type == "unconformity":
        draw_unconformity_wave(ax, x_top, y_top, x_bot, y_bot)
        return

    if is_observed:
        ax.plot([x_top, x_bot], [y_top, y_bot], color="black",
               linewidth=0.8, linestyle="-", zorder=kwargs.get("zorder", 5))
    else:
        ax.plot([x_top, x_bot], [y_top, y_bot], color="black",
               linewidth=0.5, linestyle="--", zorder=kwargs.get("zorder", 5))


def draw_unconformity_wave(ax, x, y_surf, x_bot=None, y_bot=None):
    """不整合符号: 地表锯齿线 + 地下粗虚线."""
    n_waves = 5
    wave_dx = 0.012
    t = np.linspace(0, 2 * np.pi * n_waves, n_waves * 12)
    wave_x = x + t / (2 * np.pi * n_waves) * wave_dx * n_waves
    wave_y = y_surf + np.sin(t) * 2.5
    ax.plot(wave_x, wave_y, color="black", linewidth=1.5, zorder=6)

    if x_bot is not None and y_bot is not None:
        ax.plot([x, x_bot], [y_surf, y_bot], color="black",
               linewidth=1.5, linestyle="--", zorder=5)


# ═══════════════════════════════════════════════════════════════════
# 产状标注
# ═══════════════════════════════════════════════════════════════════

def draw_attitude_label(ax, x, y, dd, da, **kwargs):
    """产状标注 — 标准格式 `dd ∠ da` (空格∠空格, 无°符号)."""
    fontsize = kwargs.get("fontsize", 6.5)
    ax.annotate(f"{dd} ∠ {da}",
               (x, y), fontsize=fontsize, color="black",
               ha="center", fontweight="bold", zorder=kwargs.get("zorder", 10),
               bbox=dict(facecolor="white", edgecolor="black",
                        linewidth=0.4, pad=1.5, alpha=0.9))


# ═══════════════════════════════════════════════════════════════════
# 观察点标注
# ═══════════════════════════════════════════════════════════════════

def draw_point_label(ax, x, y, label, **kwargs):
    """观察点号标注 (沿地形线)."""
    fontsize = kwargs.get("fontsize", 7)
    color = kwargs.get("color", "black")
    ax.annotate(label, (x, y), fontsize=fontsize,
               fontweight="bold", color=color, ha="center",
               zorder=kwargs.get("zorder", 10))


# ═══════════════════════════════════════════════════════════════════
# 特殊构造标注
# ═══════════════════════════════════════════════════════════════════

def draw_feature_label(ax, x, y, text, **kwargs):
    """特殊构造/化石等标注."""
    fontsize = kwargs.get("fontsize", 7)
    color = kwargs.get("color", "black")
    ax.annotate(text, (x, y), fontsize=fontsize, color=color, ha="center",
               fontstyle="italic",
               zorder=kwargs.get("zorder", 12),
               bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                        edgecolor="black", linewidth=0.5, alpha=0.92))


# ═══════════════════════════════════════════════════════════════════
# 地层代号标注
# ═══════════════════════════════════════════════════════════════════

def draw_formation_label(ax, x, y, code, name, **kwargs):
    """地层代号+名称 (块体内部)."""
    block_w = kwargs.get("block_width", 0.5)
    fontsize = kwargs.get("fontsize", 6 if block_w < 0.1 else 7)
    label = code if block_w < 0.1 else f"{code}\n{name}"
    ax.text(x, y, label, fontsize=fontsize, fontweight="bold",
           ha="center", va="center", color="#1a1a1a",
           zorder=kwargs.get("zorder", 12),
           bbox=dict(facecolor="white", edgecolor="none", alpha=0.75, pad=1))


def draw_formation_description(ax, x, y, description, **kwargs):
    """地层内部岩性描述 (块体中部偏下)."""
    if not description:
        return
    fontsize = kwargs.get("fontsize", 5.8)
    ax.text(x, y, description, fontsize=fontsize, color="#2c3e50",
           ha="center", va="center", linespacing=1.2,
           zorder=kwargs.get("zorder", 11),
           bbox=dict(boxstyle="round,pad=0.35", facecolor="white",
                    edgecolor="#aaa", alpha=0.85, linewidth=0.5))


# ═══════════════════════════════════════════════════════════════════
# 比例尺 & 方向
# ═══════════════════════════════════════════════════════════════════

def draw_horizontal_scale_bar(ax, x, y, bar_km, bar_w, bar_h, **kwargs):
    """线段式水平比例尺."""
    n_seg = 4
    seg_w = bar_w / n_seg
    for s in range(n_seg):
        color = "black" if s % 2 == 0 else "white"
        ax.add_patch(plt.Rectangle((x + s * seg_w, y), seg_w, bar_h,
                     facecolor=color, edgecolor="black", linewidth=0.5,
                     zorder=20, clip_on=False))
    ax.text(x, y - bar_h * 1.5,
           f"0       {bar_km/2}       {bar_km} km",
           fontsize=7, ha="left", color="black")


def draw_altitude_scale(ax, step=50):
    """左侧 y 轴海拔标尺."""
    ax.yaxis.set_major_locator(ticker.MultipleLocator(step))
    ax.tick_params(axis="y", labelsize=8, colors="#444")
    ax.set_ylabel("m", fontsize=9, color="#444")


def draw_endpoint_labels(ax, x_left, x_right, y_bottom, label_left="A", label_right="A'"):
    """剖面端点标签."""
    for label, x_pos in [(label_left, x_left), (label_right, x_right)]:
        ax.annotate(label, (x_pos, y_bottom + 10), fontsize=10,
                   fontweight="bold", ha="center", va="bottom", color="black", zorder=20)
        ax.plot([x_pos, x_pos], [y_bottom, y_bottom + 6], "k-", linewidth=1.0, zorder=20)


def draw_section_north_arrow(ax, x, y, bearing, arrow_h, head_w):
    """剖面方向箭头."""
    ax.arrow(x, y, 0, arrow_h, head_width=head_w,
            head_length=arrow_h * 0.3, fc="black", ec="black",
            linewidth=0.8, zorder=20, clip_on=False)
    ax.text(x, y + arrow_h * 1.3, f"{bearing}°",
           fontsize=8, ha="center", fontweight="bold", color="black")


# ═══════════════════════════════════════════════════════════════════
# 图名 & 图例 & 底部信息
# ═══════════════════════════════════════════════════════════════════

def draw_section_title(ax, title):
    ax.set_title(title, fontsize=14, fontweight="bold", color="black", pad=12)


def draw_section_legend(ax_legend, formations, contacts=None, bearing=None, **kwargs):
    """底部图例 — 双行格式 (上行图案+编号, 下行文字说明), 含产状/方向."""
    # 按岩性去重并按类别排序
    seen = {}
    for fm in formations:
        name = fm.lithology
        if name not in seen:
            pat = get_pattern(name)
            if pat:
                seen[name] = pat

    n_items = len(seen)
    if n_items == 0:
        return

    items = list(seen.items())
    # 最多两行, 每行最多 8 个
    max_per_row = min(8, max(4, n_items))
    n_rows = min(2, int(np.ceil(n_items / max_per_row)))
    per_row = int(np.ceil(n_items / n_rows))

    box_w = 0.88 / per_row
    box_h = 0.32 / n_rows

    for j, (lith_name, pat) in enumerate(items):
        row = j // per_row
        col = j % per_row

        # 图案框位置
        bx = 0.06 + col * box_w
        by = 0.72 - row * box_h * 1.15

        # 编号
        ax_legend.text(bx - 0.003, by + box_h * 0.62, f"({j + 1})",
                     fontsize=5.5, color="#555", ha="right", va="center",
                     transform=ax_legend.transAxes)

        # 图案符号 (小方框)
        rect = mpatches.Rectangle(
            (bx, by), 0.025, box_h * 0.55,
            facecolor=pat["fill"], edgecolor="black",
            linewidth=0.4, hatch=pat["hatch"],
            transform=ax_legend.transAxes,
        )
        ax_legend.add_patch(rect)

        # 文字说明 (图案下方)
        ax_legend.text(bx + 0.0125, by - 0.02, lith_name,
                     fontsize=6, color="black", ha="center", va="top",
                     transform=ax_legend.transAxes)

    # 补充项目: 产状、方向
    extra_y = 0.72 - n_rows * box_h * 1.15 - 0.04
    extra_idx = n_items + 1

    # 产状 (如果有)
    if contacts:
        measured = [(c.dd, c.da) for c in contacts if c.dd is not None and c.da is not None]
        if measured:
            dd, da = measured[0]
            ax_legend.text(0.06, extra_y, f"({extra_idx}) 产状: {dd}°/∠{da}°",
                         fontsize=6.5, color="black", va="center",
                         transform=ax_legend.transAxes)
            extra_idx += 1

    # 方向
    if bearing is not None:
        ax_legend.text(0.35, extra_y, f"({extra_idx}) 剖面方向: {bearing}°",
                     fontsize=6.5, color="black", va="center",
                     transform=ax_legend.transAxes)

    # 图例标题
    ax_legend.text(0.5, 0.97, "图例 (岩性花纹及标记)",
                 fontsize=8, fontweight="bold", ha="center", color="black",
                 transform=ax_legend.transAxes)


def draw_section_footer(fig, h_scale, v_scale, ve, bearing, contacts):
    """底部信息栏."""
    measured_atts = [(c.dd, c.da) for c in contacts
                     if c.dd is not None and c.da is not None]
    if measured_atts:
        att_str = "  ".join(f"{dd}°/{da}°" for dd, da in measured_atts[:4])
    else:
        att_str = "—"

    fig.text(0.5, 0.005,
            f"H 1:{h_scale}  V 1:{v_scale} (x{ve:.0f})  |  "
            f"剖面方向 {bearing}°  |  "
            f"产状 {att_str}  |  "
            f"GeoIntern-Agent",
            ha="center", fontsize=7, color="#888")


# ═══════════════════════════════════════════════════════════════════
# 坐标轴清理
# ═══════════════════════════════════════════════════════════════════

def setup_section_axes(ax, x_max, y_bottom, y_top):
    ax.set_xlim(0, x_max * 1.02)
    ax.set_ylim(y_bottom, y_top)
    ax.set_xlabel("")
    ax.tick_params(axis="x", labelsize=8, colors="#555")
    ax.grid(False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def save_figure(fig, filename, dpi=350, output_dir="output"):
    import os
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, filename)
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="white", edgecolor="none")
    plt.close(fig)
    print(f"[geo_plotting] {path}")
    return path
