"""
地质剖面图 DXF 生成器 v2.0
===========================
图面质量控制：SPLINE 地形、线宽层次、自适应尺寸、颜色语义。

Usage:
  from cad_plot import generate_cross_section, calibrate_from_image
"""

import math, ezdxf
from ezdxf import units, zoom
from ezdxf.math import Vec3

# ═══════════════════════════════════════════════════════════════
# 配置
# ═══════════════════════════════════════════════════════════════

# 线宽 (mm * 100)
LW_TERRAIN   = 60   # 地形线 — 最粗
LW_BOUNDARY  = 50   # 地层界线 — 粗
LW_DIPLINE   = 15   # 地下延伸线
LW_INTERNAL  = 9    # 层内分层线

# 颜色
CLR_TERRAIN  = 7
CLR_BOUNDARY = 7    # 界线用黑色，醒目
CLR_DIPLINE  = 8
CLR_HATCH    = 8
CLR_INTERNAL = 9
CLR_ATTITUDE = 5
CLR_LABEL    = 7
CLR_LEGEND   = 7
CLR_SCALE    = 7

# ── FGDC / AutoCAD hatch → 岩性 ──────────────────────────────
LITHO_HATCH = {
    "limestone":    ("ANSI37", 0.7, 0,   "灰岩"),
    "dolomite":     ("ANSI37", 0.6, 45,  "白云岩"),
    "sandstone":    ("AR-SAND", 0.8, 0,  "砂岩"),
    "siltstone":    ("ANSI31", 2.0, 45,  "粉砂岩"),
    "mudstone":     ("ANSI31", 2.0, 0,   "泥岩"),
    "shale":        ("ANSI31", 1.5, 0,   "页岩/千枚岩"),
    "slate":        ("ANSI31", 3.0, 90,  "板岩"),
    "phyllite":     ("ANSI31", 2.0, 60,  "千枚岩"),
    "conglomerate": ("GRAVEL", 1.0, 0,   "砾岩"),
    "basalt":       ("ANSI33", 1.5, 0,   "玄武岩"),
    "granite":      ("ANSI33", 2.0, 45,  "花岗岩"),
    "marble":       ("ANSI36", 1.5, 45,  "大理岩"),
    "default":      ("ANSI31", 1.0, 45,  "未知"),
}

FORMATION_NAMES = {
    'Jxw':  '雾迷山组',  'Jxh':  '洪水庄组',
    'Jxt1': '铁岭组一段', 'Jxt2': '铁岭组二段', 'Jxt3': '铁岭组三段',
    'Qbx':  '下马岭组',  'Qbc':  '长龙山组',
}

# ═══════════════════════════════════════════════════════════════
# 工具
# ═══════════════════════════════════════════════════════════════

def apparent_dip(true_dip, strike, azimuth):
    """视倾角"""
    if true_dip <= 0: return 5.0
    theta = abs(strike - azimuth) % 180
    if theta > 90: theta = 180 - theta
    if theta < 0.5: return 1.0
    return math.degrees(math.atan(
        math.tan(math.radians(true_dip)) * math.sin(math.radians(theta))
    ))


def _interp(terrain, x):
    xs, ys = [p[0] for p in terrain], [p[1] for p in terrain]
    if x <= xs[0]: return ys[0]
    if x >= xs[-1]: return ys[-1]
    for i in range(len(xs) - 1):
        if xs[i] <= x <= xs[i + 1]:
            f = (x - xs[i]) / (xs[i + 1] - xs[i]) if xs[i + 1] != xs[i] else 0
            return ys[i] + f * (ys[i + 1] - ys[i])
    return min(ys)


# ═══════════════════════════════════════════════════════════════
# 主函数
# ═══════════════════════════════════════════════════════════════

def generate_cross_section(terrain, formations, output, title="",
                            azimuth=0.0, depth=300, scale=1.0):
    """
    Parameters
    ----------
    terrain : [(x_m, elev_m), ...]
    formations : [{code, x, dip, strike, litho}, ...]
    output : .dxf path
    title : 图名
    azimuth : 剖面方位角 (0=N)
    depth : 地下延伸 (m)
    scale : 1.0 = 1 绘图单位 = 1m
    """
    doc = ezdxf.new(setup=True, units=units.M)
    msp = doc.modelspace()

    # ── 字体 ───────────────────────────────────────────
    cn = doc.styles.add("CN", font="SimSun")
    cn.dxf.width = 0.85

    # ── 自适应尺寸 ─────────────────────────────────────
    xs_all = [p[0] for p in terrain]
    ys_all = [p[1] for p in terrain]
    x_min, x_max = xs_all[0], xs_all[-1]
    y_min, y_max = min(ys_all), max(ys_all)
    y_bot = y_min - depth
    drawing_w = x_max - x_min
    drawing_h = depth + (y_max - y_min)

    # 文字/符号自适应大小
    ref = max(drawing_w, drawing_h)
    TXT_S  = ref * 0.010   # 小字: 产状
    TXT_M  = ref * 0.014   # 中字: 代号、标注
    TXT_L  = ref * 0.020   # 大字: 图名
    TXT_XL = ref * 0.026   # 特大: 图名标题
    HM     = ref * 0.003   # 接触标记大小
    NLAYER = 4             # 内部分层线条数

    fms = sorted(formations, key=lambda f: f['x'])
    avg_w = drawing_w / max(len(fms), 1)

    def _t(text, h, layer="LABEL", clr=CLR_LABEL):
        t = msp.add_text(text, dxfattribs={
            'layer': layer, 'height': h * scale, 'style': 'CN', 'color': clr})
        return t

    # ── 图层 (含线宽) ─────────────────────────────────
    _layer = lambda name, clr, lw: doc.layers.add(
        name, color=clr, lineweight=lw)
    _layer("TERRAIN",  CLR_TERRAIN,  LW_TERRAIN)
    _layer("BOUNDARY", CLR_BOUNDARY, LW_BOUNDARY)
    _layer("DIPLINE",  CLR_DIPLINE,  LW_DIPLINE)
    _layer("HATCH",    CLR_HATCH,    0)
    _layer("INTERNAL", CLR_INTERNAL, LW_INTERNAL)
    _layer("ATTITUDE", CLR_ATTITUDE, 0)
    _layer("LABEL",    CLR_LABEL,    0)
    _layer("LEGEND",   CLR_LEGEND,   0)
    _layer("SCALE",    CLR_SCALE,    0)

    # ═══════════════════════════════════════════════════════
    # ZONE 1: 剖面图主体
    # ═══════════════════════════════════════════════════════

    # ── 1a. 地形线 (SPLINE 平滑) ──
    fit_pts = [Vec3(x, y, 0) for x, y in terrain]
    if len(fit_pts) > 3:
        msp.add_spline(fit_pts, dxfattribs={
            'layer': 'TERRAIN', 'color': CLR_TERRAIN})
    else:
        msp.add_lwpolyline([(x, y) for x, y in terrain],
                           dxfattribs={'layer': 'TERRAIN'})

    # ── 1b. 预计算所有地层 ──
    n = len(fms)
    fm_data = []
    for i in range(n):
        fm = fms[i]
        left_x = fm['x']
        left_y = _interp(terrain, left_x)
        left_dip = apparent_dip(fm.get('dip', 20), fm.get('strike', 0), azimuth)
        if i < n - 1:
            right_x = fms[i + 1]['x']
            right_dip = apparent_dip(fms[i + 1].get('dip', 20),
                                     fms[i + 1].get('strike', 0), azimuth)
        else:
            right_x = x_max; right_dip = left_dip
        right_y = _interp(terrain, right_x)
        dx_l = depth / math.tan(max(math.radians(left_dip), 0.02))
        dx_r = depth / math.tan(max(math.radians(right_dip), 0.02))
        poly = [
            (left_x, left_y), (right_x, right_y),
            (right_x + dx_r, right_y - depth),
            (left_x + dx_l, left_y - depth),
        ]
        fm_data.append({
            'code': fm.get('code', ''),
            'litho': fm.get('litho', 'default'),
            'dip': fm.get('dip', 20), 'strike': fm.get('strike', 0),
            'left_x': left_x, 'left_y': left_y,
            'right_x': right_x, 'right_y': right_y,
            'dx_l': dx_l, 'dx_r': dx_r,
            'poly': poly,
            'width': right_x - left_x,
        })

    # ── PASS 1: 花纹填充 ──
    for i, d in enumerate(fm_data):
        pname, psc, pang, _ = LITHO_HATCH.get(d['litho'], LITHO_HATCH["default"])
        if i > 0 and d['litho'] == fm_data[i - 1]['litho']:
            pang = (pang + 30) % 90
        adj = psc * scale * (0.5 + d['width'] / avg_w * 0.3)
        h = msp.add_hatch(color=CLR_HATCH, dxfattribs={'layer': 'HATCH'})
        h.paths.add_polyline_path(d['poly'] + [d['poly'][0]], is_closed=True)
        h.set_pattern_fill(pname, scale=adj, angle=pang)

        # 内部分层线
        for li in range(1, NLAYER + 1):
            frac = li / (NLAYER + 1) + (i % 3 - 1) * 0.03
            frac = max(0.05, min(0.95, frac))
            lx1 = d['left_x'] + d['dx_l'] * frac
            ly1 = d['left_y'] - depth * frac
            lx2 = d['right_x'] + d['dx_r'] * frac
            ly2 = d['right_y'] - depth * frac
            msp.add_lwpolyline(
                [(lx1, ly1), ((lx1 + lx2) / 2, (ly1 + ly2) / 2), (lx2, ly2)],
                dxfattribs={'layer': 'INTERNAL', 'linetype': 'DASHED'}
            )

    # ── PASS 2: 地层界线 (粗线压花纹) ──
    for i, d in enumerate(fm_data):
        msp.add_line((d['left_x'], d['left_y']),
                     (d['left_x'] + d['dx_l'], d['left_y'] - depth),
                     dxfattribs={'layer': 'BOUNDARY'})
    # 最后一层右边界
    dl = fm_data[-1]
    msp.add_line((dl['right_x'], dl['right_y']),
                 (dl['right_x'] + dl['dx_r'], dl['right_y'] - depth),
                 dxfattribs={'layer': 'BOUNDARY'})

    # ── 底部截断线 (封底) ──
    bot_y = y_bot
    left_bot_x = fm_data[0]['left_x'] + fm_data[0]['dx_l']
    right_bot_x = fm_data[-1]['right_x'] + fm_data[-1]['dx_r']
    msp.add_line((left_bot_x, bot_y), (right_bot_x, bot_y),
                 dxfattribs={'layer': 'BOUNDARY'})

    # ── PASS 3: 地下标注区 ──
    # 每个地层在底部下方延伸引线，标注代号 + 产状
    annot_y = y_bot - drawing_h * 0.04
    prev_label_right = -999

    for i, d in enumerate(fm_data):
        # 地下中点 (底部截断线处)
        bx = (d['left_x'] + d['dx_l'] + d['right_x'] + d['dx_r']) / 2
        by = bot_y

        # 引线：从底部中点垂直向下到标注区
        msp.add_line((bx, by), (bx, annot_y),
                     dxfattribs={'layer': 'ATTITUDE', 'color': CLR_ATTITUDE})

        # 产状 + 代号，分行排
        dip_dir = (d['strike'] + 90) % 360
        label_line1 = d['code']
        label_line2 = f"{int(dip_dir)}°∠{int(d['dip'])}°"

        # 避让：如果跟前一个标签太近，往下错开
        tx = bx - TXT_M * 1.5
        ty = annot_y - TXT_M * 1.5
        if tx < prev_label_right:
            ty -= TXT_M * 2.5  # 错开一行
        t1 = _t(label_line1, TXT_M, "ATTITUDE", CLR_ATTITUDE)
        t1.set_placement((tx, ty))
        t2 = _t(label_line2, TXT_S, "ATTITUDE", CLR_ATTITUDE)
        t2.set_placement((tx, ty - TXT_M * 1.2))
        prev_label_right = tx + len(label_line1) * TXT_M * 0.6

    # 地表接触标记 + 产状 (地上，小字)
    for i, d in enumerate(fm_data):
        tri = HM
        msp.add_lwpolyline([
            (d['left_x'], d['left_y']),
            (d['left_x'] - tri, d['left_y'] + tri * 1.5),
            (d['left_x'] + tri, d['left_y'] + tri * 1.5),
            (d['left_x'], d['left_y']),
        ], dxfattribs={'layer': 'BOUNDARY'}, close=True)

    # 最后一层右端接触标记
    dl = fm_data[-1]
    msp.add_lwpolyline([
        (dl['right_x'], dl['right_y']),
        (dl['right_x'] - tri, dl['right_y'] + tri * 1.5),
        (dl['right_x'] + tri, dl['right_y'] + tri * 1.5),
        (dl['right_x'], dl['right_y']),
    ], dxfattribs={'layer': 'BOUNDARY'}, close=True)

    # 产状小字标在地表接触点上方
    for i, d in enumerate(fm_data):
        dip_dir = (d['strike'] + 90) % 360
        att_str = f"{int(dip_dir)}°∠{int(d['dip'])}°"
        t = _t(att_str, TXT_S * 0.8, "ATTITUDE", CLR_ATTITUDE)
        t.set_placement((d['left_x'] + HM, d['left_y'] + HM * 2))

    # ── 1c. 比例尺 ──
    bar_y = y_bot + drawing_h * 0.03
    bar_x0 = x_min + drawing_w * 0.03
    bar_len = max(20, round(drawing_w * 0.25 / 10) * 10)
    bar_x1 = bar_x0 + bar_len
    msp.add_line((bar_x0, bar_y), (bar_x1, bar_y),
                 dxfattribs={'layer': 'SCALE'})
    for tick_m in [0, bar_len // 2, bar_len]:
        tx = bar_x0 + tick_m
        msp.add_line((tx, bar_y), (tx, bar_y + HM * 2),
                     dxfattribs={'layer': 'SCALE'})
    t = _t(f"0      {bar_len // 2}      {bar_len}m", TXT_S, "SCALE")
    t.set_placement((bar_x0, bar_y - TXT_S * 1.3))

    # ── 1d. 剖面方位 ──
    az_x = x_max - drawing_w * 0.05
    az_y = y_max + drawing_h * 0.015
    az_len = min(drawing_w * 0.06, 20) * scale
    msp.add_line((az_x - az_len, az_y), (az_x + az_len, az_y),
                 dxfattribs={'layer': 'LABEL'})
    arr_s = az_len * 0.25
    msp.add_lwpolyline([
        (az_x + az_len, az_y),
        (az_x + az_len - arr_s, az_y - arr_s * 0.6),
        (az_x + az_len - arr_s, az_y + arr_s * 0.6),
    ], dxfattribs={'layer': 'LABEL'}, close=True)
    t = _t(f"{int(azimuth)}°", TXT_S, "LABEL")
    t.set_placement((az_x + az_len + HM, az_y - TXT_S * 0.4))

    # ═══════════════════════════════════════════════════════
    # ZONE 2: 图例
    # ═══════════════════════════════════════════════════════
    gap_zone = drawing_h * 0.06
    leg_y0 = y_bot - gap_zone
    box_w, box_h = drawing_w * 0.025, drawing_w * 0.012
    gap_x = drawing_w * 0.008

    # Row 1: 岩性花纹
    seen = []
    for fm in fms:
        if fm.get('litho') not in seen:
            seen.append(fm.get('litho', 'default'))

    total_w1 = len(seen) * (box_w + gap_x) - gap_x
    lx = (x_min + x_max) / 2 - total_w1 / 2
    for litho in seen:
        pname, psc, pang, label = LITHO_HATCH.get(litho, LITHO_HATCH["default"])
        rect = [(lx, leg_y0), (lx + box_w, leg_y0),
                (lx + box_w, leg_y0 - box_h), (lx, leg_y0 - box_h), (lx, leg_y0)]
        h = msp.add_hatch(color=CLR_LEGEND, dxfattribs={'layer': 'LEGEND'})
        h.paths.add_polyline_path(rect, is_closed=True)
        h.set_pattern_fill(pname, scale=psc * scale * 0.35, angle=pang)
        t = _t(label, TXT_S, "LEGEND")
        t.set_placement((lx + box_w / 2 - TXT_S * 1.2, leg_y0 - box_h - TXT_S * 0.8))
        lx += box_w + gap_x

    # Row 2: 地层代号 + 中文名 (纯文本)
    row_gap = drawing_h * 0.025
    leg_y1 = leg_y0 - box_h - row_gap
    parts = []
    for fm in fms:
        cn_name = FORMATION_NAMES.get(fm['code'], fm['code'])
        parts.append(f"{fm['code']} {cn_name}")
    row2 = "    ".join(parts)
    t = _t(row2, TXT_S, "LEGEND")
    t.set_placement(((x_min + x_max) / 2 - len(row2) * TXT_S * 0.18, leg_y1))

    # ═══════════════════════════════════════════════════════
    # ZONE 3: 图名
    # ═══════════════════════════════════════════════════════
    title_gap = drawing_h * 0.03
    title_y = leg_y1 - title_gap
    t = _t(title, TXT_L, "LABEL")
    t.set_placement(((x_min + x_max) / 2 - len(title) * TXT_L * 0.18, title_y))

    # ── 保存 ───────────────────────────────────────────
    zoom.extents(msp)
    doc.saveas(output)
    return output


# ═══════════════════════════════════════════════════════════════
# 图像标定 (不变)
# ═══════════════════════════════════════════════════════════════

def calibrate_from_image(image_path, scale_meters=40.0):
    from PIL import Image
    import numpy as np
    img = Image.open(image_path).convert("L")
    arr = np.array(img); h, w = arr.shape
    best = None
    for y in range(int(h * 0.7), h):
        row = arr[y, :]; dark = row < 150
        segs, i = [], 0
        while i < w:
            if dark[i]:
                s = i
                while i < w and dark[i]: i += 1
                if 20 < i - s < 150: segs.append((s, i - s))
            else: i += 1
        if 2 <= len(segs) <= 4:
            centers = [s[0] + s[1] // 2 for s in segs]
            gaps = [centers[j + 1] - centers[j] for j in range(len(centers) - 1)]
            if gaps:
                avg = sum(gaps) / len(gaps)
                dev = max(abs(g - avg) for g in gaps) / avg if avg > 0 else 1
                if dev < 0.3 and len(segs) >= 3:
                    score = len(segs) * (1 - dev)
                    if best is None or score > best[0]:
                        best = (score, y, centers)
    if best is None:
        return {"px_per_m": w / 200.0, "fallback": True, "image_w": w, "image_h": h}
    span = best[2][-1] - best[2][0]
    return {"px_per_m": span / scale_meters, "scale_y": best[1],
            "tick_xs": best[2], "span_px": span, "scale_meters": scale_meters,
            "image_w": w, "image_h": h, "fallback": False}


def extract_terrain_from_image(image_path, px_per_m, base_elevation=150.0):
    from PIL import Image
    import numpy as np
    from scipy.interpolate import interp1d
    img = Image.open(image_path).convert("L")
    arr = np.array(img); h, w = arr.shape
    raw = []
    for x in range(w):
        col = arr[:, x]; dark = col < 150; i = 0
        while i < h:
            if dark[i]:
                s = i
                while i < h and dark[i]: i += 1
                if i - s >= 3: raw.append((x, s)); break
            else: i += 1
        if len(raw) <= x: raw.append(None)
    ys = np.array([t[1] if t else np.nan for t in raw], dtype=float)
    v = ys[~np.isnan(ys)]; med, std = np.median(v), np.std(v)
    for i in range(len(ys)):
        if not np.isnan(ys[i]) and (ys[i] > h * 0.65 or abs(ys[i] - med) > 4 * std):
            ys[i] = np.nan
    vi = np.where(~np.isnan(ys))[0]
    f = interp1d(vi, ys[vi], kind='linear', fill_value='extrapolate')
    ys_i = f(np.arange(w))
    win = 15; kernel = np.ones(win) / win
    ys_s = np.convolve(ys_i, kernel, mode='same')
    ys_s[:win] = ys_i[:win]; ys_s[-win:] = ys_i[-win:]
    y_bot = np.nanmax(ys_s)
    step = max(1, w // 55)
    pts = []
    for x in range(0, w, step):
        pts.append((round(x / px_per_m, 1),
                     round(base_elevation + (y_bot - ys_s[x]) / px_per_m, 1)))
    xl = w - 1
    pts.append((round(xl / px_per_m, 1),
                round(base_elevation + (y_bot - ys_s[xl]) / px_per_m, 1)))
    return pts


# ── CLI ───────────────────────────────────────────────────────
def cmd_section():
    import argparse, json
    p = argparse.ArgumentParser()
    p.add_argument("--terrain", required=True)
    p.add_argument("--formations", required=True)
    p.add_argument("--azimuth", type=float, default=0.0)
    p.add_argument("--depth", type=float, default=300)
    p.add_argument("--scale", type=float, default=1.0)
    p.add_argument("-o", "--output", default="section.dxf")
    p.add_argument("-t", "--title", default="Geological Cross-Section")
    args = p.parse_args()
    ts = args.terrain.strip()
    if ts.startswith("[["): pts = [(p[0], p[1]) for p in json.loads(ts)]
    elif ts.startswith("["): nums = json.loads(ts); pts = [(nums[i], nums[i+1]) for i in range(0, len(nums), 2)]
    else: nums = [float(x) for x in ts.replace(",", " ").split()]; pts = [(nums[i], nums[i+1]) for i in range(0, len(nums), 2)]
    fms = json.loads(args.formations)
    out = generate_cross_section(pts, fms, args.output, args.title, args.azimuth, args.depth, args.scale)
    print("DXF saved:", out)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("CAD Geological Cross-Section Generator v2.0")
        sys.exit(0)
    if sys.argv[1] == "section":
        sys.argv = [sys.argv[0]] + sys.argv[2:]; cmd_section()
    else: print("Unknown:", sys.argv[1])
