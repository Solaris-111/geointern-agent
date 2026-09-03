"""
GeoIntern-Agent 画图管线
=========================
CLI地质图件生成器——柱状图 / 赤平投影 / 剖面图。

Usage:
  # 柱状图（使用 striplog 生成）
  python plotting.py column --formations '
    [{"name":"峨眉山玄武岩","code":"P2b","thick":258,"litho":"basalt"},
     {"name":"飞仙关组","code":"T1f","thick":200,"litho":"mudstone"},
     {"name":"嘉陵江组","code":"T1j","thick":300,"litho":"limestone"}]
  ' -o column.png

  # 赤平投影（使用 mplstereonet 生成）
  python plotting.py stereonet --strikes 45,120,200,310,80,155 \
    --dips 30,65,45,70,55,40 --type poles -o stereonet.png

  # 剖面图（纯 matplotlib，视倾角投影）
  python plotting.py section \
    --terrain "[0,500,200,520,400,490,600,510,800,480,1000,500]" \
    --formations '[
      {"code":"P2b","x":150,"litho":"basalt","dip":25},
      {"code":"T1f","x":400,"litho":"mudstone","dip":30},
      {"code":"T1j","x":700,"litho":"limestone","dip":35}
    ]' --azimuth 145 --depth 300 -o section.png --title "龙门硐剖面图"

  # 岩性图例
  python plotting.py legend -o legend.png
"""
import sys, json, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'SimSun']
plt.rcParams['axes.unicode_minus'] = False

# ===================================================================
# Shared: Lithology definitions
# ===================================================================

LITHO = {
    "limestone":       ("#B3D9FF", "////",  "灰岩"),
    "dolomite":        ("#D4E4FF", "\\\\",  "白云岩"),
    "sandstone":       ("#F4D03F", "....",  "砂岩"),
    "siltstone":       ("#F5DEB3", ".....", "粉砂岩"),
    "mudstone":        ("#D2B48C", "----",  "泥岩"),
    "shale":           ("#A0522D", "----",  "页岩"),
    "conglomerate":    ("#DAA520", "o...",  "砾岩"),
    "basalt":           ("#666666", "++..",  "玄武岩"),
    "granite":          ("#FFB6C1", "++xx",  "花岗岩"),
    "gabbro":           ("#4A4A4A", "xx..",  "辉长岩"),
    "slate":            ("#708090", "__..",  "板岩"),
    "schist":           ("#A9A9A9", "//..",  "片岩"),
    "gneiss":           ("#C0C0C0", "+//.",  "片麻岩"),
    "marble":           ("#E8E8E8", "/\\.",  "大理岩"),
    "coal":             ("#1A1A1A", "....",  "煤"),
    "default":          ("#D3D3D3", "....",  "未分类"),
}


def _get_litho(key):
    if key in LITHO:
        return LITHO[key]
    return LITHO["default"]


# ===================================================================
# 1. 地层柱状图 (via striplog)
# ===================================================================

def plot_strat_column(formations: list[dict], output: str,
                       title: str = "综合地层柱状图"):
    from striplog import Striplog, Component, Legend

    comps = []
    for fm in formations:
        # Map our litho names to striplog's lexicon
        litho = fm.get('litho', 'default')
        c = Component({
            'lithology': litho,
            'name': fm.get('name', ''),
            'thickness': fm['thick'],
        })
        comps.append(c)

    # Build legend from our lithologies
    names = set(fm.get('litho', 'default') for fm in formations)
    legend_dict = {}
    for name in names:
        color, hatch, label = _get_litho(name)
        legend_dict[name] = {
            'colour': color,
            'hatch': hatch,
            'width': 3,
        }

    legend = Legend(legend_dict)
    s = Striplog(comps, legend=legend)

    fig, ax = plt.subplots(figsize=(3, 8))
    s.plot(ax=ax, legend=legend, ladder=True, aspect=3)
    ax.set_title(title, fontsize=11, fontweight='bold')
    fig.savefig(output, dpi=200, bbox_inches='tight')
    plt.close()
    return output


# ===================================================================
# 2. 赤平投影 (via mplstereonet)
# ===================================================================

def plot_stereonet(strikes: list[float], dips: list[float],
                   output: str, plot_type: str = "poles",
                   title: str = "赤平投影图"):
    import mplstereonet

    if plot_type == 'all':
        fig, axes = plt.subplots(1, 3, figsize=(15, 5),
                                 subplot_kw={'projection': 'stereonet'})
    else:
        fig, ax = plt.subplots(figsize=(6, 6),
                               subplot_kw={'projection': 'stereonet'})
        axes = [ax]

    titles = []
    if plot_type == 'poles':
        titles = ["极点图"]
    elif plot_type == 'contour':
        titles = ["等密图"]
    elif plot_type == 'great_circles':
        titles = ["大圆图"]
    elif plot_type == 'all':
        titles = ["极点图", "等密图", "大圆图"]

    for i, ax in enumerate(axes):
        ax.grid()

    if plot_type in ('poles', 'all'):
        idx = 0
        axes[idx].pole(strikes, dips, 'o', markersize=5, color='steelblue')
        axes[idx].set_title(titles[idx] if idx < len(titles) else "极点图",
                            fontsize=11, fontweight='bold')

    if plot_type in ('contour', 'all'):
        idx = 1 if plot_type == 'all' else 0
        try:
            axes[idx].density_contourf(strikes, dips, cmap='Reds', alpha=0.6)
            axes[idx].density_contour(strikes, dips, colors='black', linewidths=0.5)
        except Exception:
            axes[idx].pole(strikes, dips, 'o', markersize=4, color='steelblue')
        axes[idx].set_title(titles[idx] if idx < len(titles) else "等密图",
                            fontsize=11, fontweight='bold')

    if plot_type in ('great_circles', 'all'):
        idx = 2 if plot_type == 'all' else 0
        for s, d in zip(strikes, dips):
            axes[idx].plane(s, d, color='steelblue', alpha=0.4, linewidth=0.5)
        axes[idx].set_title(titles[idx] if idx < len(titles) else "大圆图",
                            fontsize=11, fontweight='bold')

    fig.suptitle(title, fontsize=13, fontweight='bold', y=1.02)
    plt.tight_layout()
    fig.savefig(output, dpi=200, bbox_inches='tight')
    plt.close()
    return output


# ===================================================================
# 3. 信手剖面图
# ===================================================================

def apparent_dip(true_dip: float, strike: float, profile_azimuth: float) -> float:
    """视倾角计算。α' = arctan(tan(α) × sin(θ))"""
    if true_dip <= 0:
        return 5.0
    theta = math.radians(abs(strike - profile_azimuth) % 180)
    if theta > math.pi / 2:
        theta = math.pi - theta
    return math.degrees(math.atan(math.tan(math.radians(true_dip)) * math.sin(theta)))


def plot_cross_section(terrain: list[tuple], formations: list[dict],
                        output: str, title: str = "信手地质剖面图",
                        azimuth: float = 0.0, depth: float = 300):
    """
    Draw a proper geological cross-section.

    The key: each formation contact drawn at the surface extends underground
    at the APPARENT dip angle. Polygons between contacts are filled with
    lithology patterns.
    """
    xs = np.array([p[0] for p in terrain])
    ys = np.array([p[1] for p in terrain])
    x_min, x_max = xs[0], xs[-1]
    y_min_base = min(ys) - depth

    fig, ax = plt.subplots(figsize=(12, 6))

    # Sort formations by x position (surface order, left to right)
    fms = sorted(formations, key=lambda f: f['x'])

    # Draw terrain
    ax.fill_between(xs, [y_min_base] * len(xs), ys,
                     color='#F5F0E0', alpha=0.3, zorder=1)
    ax.plot(xs, ys, 'k-', linewidth=1.8, zorder=10)

    # Interpolate terrain elevation at any x
    def terrain_y(x):
        if x <= x_min:
            return float(ys[0])
        if x >= x_max:
            return float(ys[-1])
        idx = np.searchsorted(xs, x)
        if idx == 0:
            return float(ys[0])
        if idx >= len(xs):
            return float(ys[-1])
        frac = (x - xs[idx - 1]) / (xs[idx] - xs[idx - 1])
        return float(ys[idx - 1] + frac * (ys[idx] - ys[idx - 1]))

    # Build subsurface polygons
    n = len(fms)
    for i in range(n):
        fm = fms[i]
        x_contact = fm['x']
        y_surface = terrain_y(x_contact)
        app_dip = apparent_dip(fm.get('dip', 30),
                                 fm.get('strike', 0), azimuth)

        # Where is the NEXT contact?
        if i < n - 1:
            next_x = fms[i + 1]['x']
        else:
            next_x = x_max

        # Previous contact (for the left boundary of this unit)
        if i > 0:
            prev_x = fms[i - 1]['x']
            prev_dip = apparent_dip(fms[i - 1].get('dip', 30),
                                     fms[i - 1].get('strike', 0), azimuth)
        else:
            prev_x = x_min
            prev_dip = app_dip  # same as first unit for simplicity

        # Build polygon for this formation unit
        # Top: terrain segment from prev_x to next_x
        # Bottom: projected at apparent dip from each contact
        dip_rad = math.radians(app_dip)
        prev_dip_rad = math.radians(prev_dip)

        # Left boundary: from (prev_x, terrain_y(prev_x)) down at prev_dip
        # Right boundary: from (x_contact, y_surface) down at app_dip

        left_x_top = prev_x
        left_y_top = terrain_y(prev_x)
        right_x_top = next_x
        right_y_top = terrain_y(next_x)

        # Dip lines go leftward (for strata dipping toward viewer/away)
        # Actually for cross-section, dip angle determines the angle of
        # the contact line in the section plane

        # The contact at x_contact dips underground
        # dip direction in section plane determines which way it goes
        # For simplicity, assume strata dip toward increasing x
        dx_contact = depth / math.tan(max(dip_rad, 0.05))
        dy_contact = depth

        # Previous contact also dips
        dx_prev = depth / math.tan(max(prev_dip_rad, 0.05))

        # Polygon vertices (clockwise)
        poly_x = [
            left_x_top,
            right_x_top,
            right_x_top + dx_contact,
            left_x_top + dx_prev,
        ]
        poly_y = [
            left_y_top,
            right_y_top,
            right_y_top - dy_contact,
            left_y_top - dy_contact,
        ]

        # Clip to terrain
        clip_x, clip_y = [], []
        for j in range(4):
            px, py = poly_x[j], poly_y[j]
            ty = terrain_y(px)
            clip_x.append(px)
            clip_y.append(min(py, ty))

        # Draw
        color, hatch, label = _get_litho(fm.get('litho', 'default'))
        ax.fill(clip_x, clip_y, facecolor=color, edgecolor='#333',
                linewidth=0.4, hatch=hatch, alpha=0.75, zorder=2)

        # Label
        cx = (left_x_top + right_x_top) / 2
        cy = terrain_y(cx) - depth * 0.35
        code = fm.get('code', '')
        ax.text(cx, cy, code, fontsize=8, ha='center', va='center',
                fontweight='bold', alpha=0.8, zorder=5)

    # Contact markers on terrain
    for fm in fms:
        x0 = fm['x']
        y0 = terrain_y(x0)
        ax.plot(x0, y0, 'kv', markersize=8, zorder=12, markerfacecolor='white')
        ax.text(x0, y0 + 15, fm.get('code', ''), fontsize=7, ha='center',
                zorder=13, fontweight='bold')

    # Legend
    seen = set()
    patches = []
    for fm in fms:
        litho = fm.get('litho', 'default')
        if litho in seen:
            continue
        seen.add(litho)
        color, hatch, label = _get_litho(litho)
        patches.append(plt.Rectangle((0, 0), 1, 1,
                        facecolor=color, edgecolor='#333',
                        linewidth=0.4, hatch=hatch, label=label))
    ax.legend(handles=patches, fontsize=8, loc='lower right',
              ncol=4, framealpha=0.9)

    # Annotations
    ax.set_xlabel("水平距离 (m)", fontsize=10)
    ax.set_ylabel("高程 (m)", fontsize=10)
    ax.set_title(title, fontsize=13, fontweight='bold')
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min_base, max(ys) * 1.08)

    if azimuth:
        ax.text(0.98, 0.98, f"剖面方向: {azimuth}°",
                transform=ax.transAxes, fontsize=9, ha='right', va='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    plt.tight_layout()
    fig.savefig(output, dpi=200, bbox_inches='tight')
    plt.close()
    return output


# ===================================================================
# 4. 岩性花纹图例
# ===================================================================

def plot_legend(output: str):
    """Generate FGDC lithology pattern legend."""
    keys = list(LITHO.keys())
    keys.remove('default')
    cols = 4
    rows = (len(keys) + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(10, rows * 2))
    axes = axes.flatten() if hasattr(axes, 'flatten') else [axes]

    for i, key in enumerate(keys):
        ax = axes[i]
        color, hatch, label = LITHO[key]
        rect = plt.Rectangle((0.1, 0.2), 0.8, 0.6,
                             facecolor=color, edgecolor='#333',
                             linewidth=0.8, hatch=hatch)
        ax.add_patch(rect)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(label, fontsize=10)
    for i in range(len(keys), len(axes)):
        axes[i].axis('off')

    fig.suptitle("FGDC 标准岩性花纹图例", fontsize=13, fontweight='bold')
    plt.tight_layout()
    fig.savefig(output, dpi=200, bbox_inches='tight')
    plt.close()
    return output


# ===================================================================
# CLI
# ===================================================================

def _parse_comma_or_json(s):
    s = s.strip()
    if s.startswith('['):
        return json.loads(s)
    return [float(x.strip()) for x in s.split(',')]


def cmd_column():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--formations", required=True, help="JSON [{name,code,thick,litho},...]")
    p.add_argument("-o", "--output", default="column.png")
    p.add_argument("-t", "--title", default="综合地层柱状图")
    args = p.parse_args()
    fms = json.loads(args.formations)
    out = plot_strat_column(fms, args.output, args.title)
    print(f"柱状图已保存: {out}")


def cmd_stereonet():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--strikes", required=True)
    p.add_argument("--dips", required=True)
    p.add_argument("--type", default="poles",
                   choices=["poles","contour","great_circles","all"])
    p.add_argument("-o", "--output", default="stereonet.png")
    p.add_argument("-t", "--title", default="赤平投影图")
    args = p.parse_args()
    strikes = _parse_comma_or_json(args.strikes)
    dips = _parse_comma_or_json(args.dips)
    out = plot_stereonet(strikes, dips, args.output, args.type, args.title)
    if out:
        print(f"赤平投影已保存: {out}")


def cmd_section():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--terrain", required=True,
                   help="Flat JSON [x1,y1,x2,y2,...] or [[x,y],...]")
    p.add_argument("--formations", required=True,
                   help="""JSON [{code,x,litho,dip,strike},...]
                   x=contact position on terrain.
                   dip=true dip angle. strike=strike azimuth.""")
    p.add_argument("--azimuth", type=float, default=0.0,
                   help="Profile azimuth (0=N, 90=E)")
    p.add_argument("--depth", type=float, default=300,
                   help="Depth below min elevation")
    p.add_argument("-o", "--output", default="section.png")
    p.add_argument("-t", "--title", default="信手地质剖面图")
    args = p.parse_args()

    t_str = args.terrain.strip()
    if t_str.startswith('[['):
        pts = [(p[0], p[1]) for p in json.loads(t_str)]
    elif t_str.startswith('['):
        nums = json.loads(t_str)
        pts = [(nums[i], nums[i+1]) for i in range(0, len(nums), 2)]
    else:
        nums = [float(x.strip()) for x in t_str.replace(',', ' ').split()]
        pts = [(nums[i], nums[i+1]) for i in range(0, len(nums), 2)]

    fms = json.loads(args.formations)
    out = plot_cross_section(pts, fms, args.output, args.title,
                              args.azimuth, args.depth)
    print(f"剖面图已保存: {out}")


def cmd_legend():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("-o", "--output", default="legend.png")
    args = p.parse_args()
    out = plot_legend(args.output)
    print(f"图例已保存: {out}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("GeoIntern-Agent 画图管线")
        print("  python plotting.py column --formations '<json>' -o column.png")
        print("  python plotting.py stereonet --strikes ... --dips ... -o stereonet.png")
        print("  python plotting.py section --terrain ... --formations ... -o section.png")
        print("  python plotting.py legend -o legend.png")
        sys.exit(0)

    cmds = {
        "column": cmd_column,
        "stereonet": cmd_stereonet,
        "section": cmd_section,
        "legend": cmd_legend,
    }
    cmd = sys.argv[1]
    sys.argv = [sys.argv[0]] + sys.argv[2:]
    if cmd in cmds:
        cmds[cmd]()
    else:
        print(f"Unknown: {cmd}. Available: {list(cmds.keys())}")
