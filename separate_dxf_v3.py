"""
v3 fix: 用多边形最远两点定中心线方向 + 放宽阈值 + 细化6类
"""
import ezdxf, numpy as np, json, os
from shapely.geometry import Polygon, LineString, Point
from scipy.spatial import ConvexHull
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DXF_PATH = r"E:\成长日志\大三上\周口店大报告图片\1_20260716_170053.dxf"
OUT_DIR = r"d:\geointern-agent"

doc = ezdxf.readfile(DXF_PATH)
msp = doc.modelspace()

# ── 1. 提取并计算中心线 ──
polys = []
for i, pl in enumerate(msp.query('POLYLINE')):
    pts = np.array([(v.dxf.location.x, v.dxf.location.y) for v in pl.vertices])
    if len(pts) < 3:
        continue
    pg = Polygon(pts)
    if not pg.is_valid:
        pg = pg.buffer(0)
    if pg.is_empty:
        continue

    area = pg.area; perimeter = pg.length
    bounds = pg.bounds  # minx, miny, maxx, maxy
    w, h = bounds[2] - bounds[0], bounds[3] - bounds[1]
    bbox_area = w * h
    fill = area / bbox_area if bbox_area > 0 else 0

    # 找多边形上距离最远的两个点 → 这两个点确定主方向
    # 先取凸包减少点数
    try:
        hull = ConvexHull(pts)
        hull_pts = pts[hull.vertices]
    except:
        hull_pts = pts

    max_dist = 0; p1_idx, p2_idx = 0, 0
    for a in range(len(hull_pts)):
        for b in range(a+1, len(hull_pts)):
            d = np.sum((hull_pts[a] - hull_pts[b]) ** 2)
            if d > max_dist:
                max_dist = d
                p1_idx, p2_idx = a, b

    p1, p2 = hull_pts[p1_idx], hull_pts[p2_idx]
    cl_vec = p2 - p1
    cl_length = np.sqrt(max_dist)
    if cl_length > 0:
        angle = np.degrees(np.arctan2(abs(cl_vec[1]), abs(cl_vec[0])))  # 0-90
    else:
        angle = 0

    # 中心点
    centroid = pg.centroid
    cx, cy = centroid.x, centroid.y

    # 笔触宽度 ≈ area / cl_length (对细长形状有效)
    stroke_width = area / cl_length if cl_length > 0 else np.sqrt(area)

    polys.append({
        'id': i, 'pts': pts.tolist(),
        'area': area, 'perimeter': perimeter,
        'w': w, 'h': h, 'aspect': max(w,h)/min(w,h) if min(w,h)>0 else 99,
        'fill': fill,
        'cl_length': cl_length,
        'cl_angle': angle,
        'stroke_width': stroke_width,
        'cx': cx, 'cy': cy,
        'bounds': list(bounds),
        'p1': p1.tolist(), 'p2': p2.tolist(),
    })

print(f"总计: {len(polys)} 条多段线")

# ── 2. 分类 ──
terrain = []
boundaries = []
dip_symbols = []
legend_boxes = []
title_text = []
orientation_mark = []  # 方位标记（如右上角65°箭头）
unknown = []

for p in polys:
    cl = p['cl_length']; cy = p['cy']; angle = p['cl_angle']
    sw = p['stroke_width']; fill = p['fill']; area = p['area']

    # 图名/文字: 极小面积、紧实
    if area < 200 and fill > 0.5 and cl < 40:
        title_text.append(p)
    # 产状符号: 短线段，散布在上部(Y<680)，有一定倾斜
    elif 15 < cl < 140 and cy < 680 and sw < 15:
        dip_symbols.append(p)
    # 地形线: 上部(Y<380)，长曲线(>100)，水平为主
    elif cy < 380 and cl > 100:
        terrain.append(p)
    # 地层界线: 中部(280<Y<700)，中等长度(>80)，倾斜
    elif 280 < cy < 700 and cl > 80:
        boundaries.append(p)
    # 图例框: 下部(Y>650)，矩形，较长
    elif cy > 650 and (fill > 0.5 or cl > 80):
        legend_boxes.append(p)
    # 方位标记: 右上角
    elif cy < 300 and cl < 60 and cy < 350:
        orientation_mark.append(p)
    else:
        unknown.append(p)

print(f"\n自动分类结果：")
print(f"  地形线:      {len(terrain)} 条")
print(f"  地层界线:    {len(boundaries)} 条")
print(f"  产状符号:    {len(dip_symbols)} 条")
print(f"  图例框:      {len(legend_boxes)} 条")
print(f"  图名/文字:   {len(title_text)} 条")
print(f"  方位标记:    {len(orientation_mark)} 条")
print(f"  未分类:      {len(unknown)} 条")

# ── 3. 对大量未分类项做第二轮分配（放宽） ──
still_unknown = []
for p in unknown:
    cl = p['cl_length']; cy = p['cy']; angle = p['cl_angle']
    sw = p['stroke_width']; area = p['area']; fill = p['fill']

    if area < 200 and fill > 0.4:
        title_text.append(p)
    elif cy < 400 and cl > 60:
        terrain.append(p)
    elif 300 < cy < 720 and cl > 50:
        boundaries.append(p)
    elif cy > 650 and cl > 40:
        legend_boxes.append(p)
    elif cl < 100 and cy < 680:
        dip_symbols.append(p)
    else:
        still_unknown.append(p)

unknown = still_unknown

print(f"\n第二轮分配后：")
print(f"  地形线:      {len(terrain)} 条")
print(f"  地层界线:    {len(boundaries)} 条")
print(f"  产状符号:    {len(dip_symbols)} 条")
print(f"  图例框:      {len(legend_boxes)} 条")
print(f"  图名/文字:   {len(title_text)} 条")
print(f"  方位标记:    {len(orientation_mark)} 条")
print(f"  未分类:      {len(unknown)} 条")

# ── 4. 渲染 6 类分色 ──
categories = [
    ('地形线', terrain, '#e74c3c', '上部波浪曲线'),
    ('地层界线', boundaries, '#2ecc71', '中部倾斜线'),
    ('产状符号', dip_symbols, '#3498db', '短线段/箭头'),
    ('图例框', legend_boxes, '#f39c12', '下部矩形框'),
    ('图名/文字', title_text, '#9b59b6', '文字轮廓'),
    ('方位标记', orientation_mark, '#1abc9c', '右上角箭头等'),
]

fig, axes = plt.subplots(2, 3, figsize=(22, 14))
for ax, (title, items, color, desc) in zip(axes.flat, categories):
    for p in items:
        pts = np.array(p['pts'])
        ax.fill(pts[:, 0], pts[:, 1], color=color, alpha=0.5, linewidth=0.1, edgecolor='#333')
        # 画中心线
        ax.plot([p['p1'][0], p['p2'][0]], [p['p1'][1], p['p2'][1]],
                'w-', linewidth=0.5, alpha=0.6)
    ax.set_xlim(0, 1740); ax.set_ylim(1034, 0)
    ax.set_aspect('equal')
    ax.set_title(f'{title} ({len(items)}条) — {desc}', fontsize=10)

# 未分类单独一张
if unknown:
    uax = axes.flat[5]  # 替换第6个子图
    uax.clear()
    for p in unknown:
        pts = np.array(p['pts'])
        uax.fill(pts[:, 0], pts[:, 1], color='#95a5a6', alpha=0.5, linewidth=0.1, edgecolor='#333')
    uax.set_xlim(0, 1740); uax.set_ylim(1034, 0)
    uax.set_aspect('equal')
    uax.set_title(f'未分类 ({len(unknown)}条)', fontsize=10)

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'dxf_v3_6classes.png'), dpi=150)
print("\n已保存: dxf_v3_6classes.png")

# ── 5. 叠加图 ──
fig2, ax2 = plt.subplots(figsize=(18, 12))
all_cats = categories + ([('未分类', unknown, '#95a5a6', '')] if unknown else [])
for title, items, color, desc in all_cats:
    for p in items:
        pts = np.array(p['pts'])
        ax2.fill(pts[:, 0], pts[:, 1], color=color, alpha=0.4, linewidth=0.1, edgecolor=color)

from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=c, alpha=0.5, label=f'{t} ({len(it)})')
                   for t, it, c, d in all_cats]
ax2.legend(handles=legend_elements, loc='upper right', fontsize=9)
ax2.set_xlim(0, 1740); ax2.set_ylim(1034, 0)
ax2.set_aspect('equal')
ax2.set_title('叠加分类 — 对比原始 1.png 检查', fontsize=14)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'dxf_v3_overlay.png'), dpi=150)
print("已保存: dxf_v3_overlay.png")

# ── 6. 清单 ──
for title, items, color, desc in categories:
    print(f"\n{'='*60}")
    print(f"{title} ({len(items)}条):")
    for p in sorted(items, key=lambda x: (x['cx'], x['cl_length']), reverse=False)[:12]:
        idx = polys.index(p) + 1
        print(f"  #{idx}: 长={p['cl_length']:.0f} 角={p['cl_angle']:.0f}° "
              f"pos=({p['cx']:.0f},{p['cy']:.0f}) 笔宽={p['stroke_width']:.1f}")

if unknown:
    print(f"\n{'='*60}")
    print(f"未分类 ({len(unknown)}条) — 前15条:")
    for p in sorted(unknown, key=lambda x: x['cl_length'], reverse=True)[:15]:
        idx = polys.index(p) + 1
        print(f"  #{idx}: 长={p['cl_length']:.0f} 角={p['cl_angle']:.0f}° "
              f"pos=({p['cx']:.0f},{p['cy']:.0f})")

print(f"\n请查看 dxf_v3_6classes.png 和 dxf_v3_overlay.png")
print(f"告诉我哪些编号需要改正分类。")
