"""
v2: DXF渲染到像素画布 → 逐像素比对颜色掩码 → 反推每条多段线的颜色
"""
import ezdxf, numpy as np, os
from shapely.geometry import Polygon, Point
from PIL import Image
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DXF_PATH = r"E:\成长日志\大三上\周口店大报告图片\1_20260716_170053.dxf"
PNG_PATH = r"E:\成长日志\大三上\周口店大报告图片\1.png"
OUT_DIR = r"d:\geointern-agent"

# ── 1. 读PNG，构建颜色掩码 ──
img = Image.open(PNG_PATH).convert('RGB')
arr = np.array(img).astype(np.float64)
h, w = arr.shape[:2]  # 517 × 870
print(f"PNG: {w}×{h}")

# 色偏检测（相对于近白背景）
r_arr, g_arr, b_arr = arr[:,:,0], arr[:,:,1], arr[:,:,2]
brightness = (r_arr + g_arr + b_arr) / 3
is_content = brightness < 225  # 比白暗30以上

mask_y = np.zeros((h, w), dtype=np.uint8)
mask_r = np.zeros((h, w), dtype=np.uint8)
mask_b = np.zeros((h, w), dtype=np.uint8)
mask_g = np.zeros((h, w), dtype=np.uint8)
mask_gray = np.zeros((h, w), dtype=np.uint8)

for y in range(h):
    for x in range(w):
        if not is_content[y, x]:
            continue
        r, g, b = r_arr[y,x], g_arr[y,x], b_arr[y,x]
        rg, rb, gb = abs(r-g), abs(r-b), abs(g-b)

        if max(rg, rb, gb) < 12:
            mask_gray[y, x] = 1
        elif rg < 15 and r > b + 6 and g > b + 6:
            mask_y[y, x] = 1
        elif r > g + 8 and r > b + 8:
            mask_r[y, x] = 1
        elif b > r + 8 and b > g + 8:
            mask_b[y, x] = 1
        elif g > r + 8 and g > b + 8:
            mask_g[y, x] = 1
        else:
            mask_gray[y, x] = 1

print(f"颜色掩码: Y={mask_y.sum()} R={mask_r.sum()} B={mask_b.sum()} G={mask_g.sum()} Gray={mask_gray.sum()}")

# ── 2. 将所有多段线渲染到像素画布（每条线不同ID） ──
doc = ezdxf.readfile(DXF_PATH)
msp = doc.modelspace()

# DXF: 1740×1034 → PNG: 870×517, scale = 0.5
scale = 0.5
id_canvas = np.zeros((h, w), dtype=np.int32) - 1  # -1 = 背景

poly_data = {}
poly_idx = 0

for i, pl in enumerate(msp.query('POLYLINE')):
    pts = np.array([(v.dxf.location.x, v.dxf.location.y) for v in pl.vertices])
    if len(pts) < 3:
        continue
    pg = Polygon(pts)
    if not pg.is_valid:
        pg = pg.buffer(0)
    if pg.is_empty:
        continue

    # 缩放坐标
    scaled_pts = pts * scale
    bounds = pg.bounds
    minx, miny = int(bounds[0]*scale), int(bounds[1]*scale)
    maxx, maxy = int(bounds[2]*scale), int(bounds[3]*scale)

    # 在 bbox 内逐像素检查
    for py in range(max(0, miny), min(h, maxy+1)):
        for px in range(max(0, minx), min(w, maxx+1)):
            pt = Point(px, py)
            if pg.contains(Point(px/scale, py/scale)):
                id_canvas[py, px] = poly_idx

    bounds_dxf = pg.bounds
    poly_data[poly_idx] = {
        'id': i,
        'pts': pts.tolist(),
        'area': pg.area,
        'cx': pg.centroid.x,
        'cy': pg.centroid.y,
        'w': bounds_dxf[2]-bounds_dxf[0],
        'h': bounds_dxf[3]-bounds_dxf[1],
    }
    poly_idx += 1

print(f"已渲染 {poly_idx} 条多段线到画布")

# ── 3. 每条多段线统计覆盖的颜色像素 ──
color_counts = defaultdict(lambda: {'yellow':0, 'red':0, 'blue':0, 'green':0, 'gray':0})

for py in range(h):
    for px in range(w):
        pid = id_canvas[py, px]
        if pid < 0:
            continue
        if mask_y[py, px]:    color_counts[pid]['yellow'] += 1
        elif mask_r[py, px]:  color_counts[pid]['red'] += 1
        elif mask_b[py, px]:  color_counts[pid]['blue'] += 1
        elif mask_g[py, px]:  color_counts[pid]['green'] += 1
        elif mask_gray[py, px]: color_counts[pid]['gray'] += 1

# ── 4. 为每条多段线分配颜色 ──
terrain = []; boundaries = []; dip_red = []; dip_blue = []; dip_green = []
gray_items = []; unclassified = []

for pid, pdata in poly_data.items():
    cc = color_counts[pid]
    total = sum(cc.values())
    if total == 0:
        unclassified.append(pdata)
        continue

    # 找最高比例的颜色
    best = max(cc, key=cc.get)
    ratio = cc[best] / total

    pdata['color'] = best
    pdata['color_ratio'] = ratio
    pdata['total_pixels'] = total

    if best == 'yellow':
        # 细分：地形线 vs 地层界线
        cy = pdata['cy']; ww = pdata['w']
        if cy < 350 and ww > 100:
            terrain.append(pdata)
        else:
            boundaries.append(pdata)
    elif best == 'red':
        dip_red.append(pdata)
    elif best == 'blue':
        dip_blue.append(pdata)
    elif best == 'green':
        dip_green.append(pdata)
    else:
        gray_items.append(pdata)

print(f"\n按颜色+渲染分类：")
print(f"  地形线（黄）:   {len(terrain)} 条")
print(f"  地层界线（黄）: {len(boundaries)} 条")
print(f"  产状-红:        {len(dip_red)} 条")
print(f"  产状-蓝:        {len(dip_blue)} 条")
print(f"  产状-绿:        {len(dip_green)} 条")
print(f"  灰/黑(文字图框):{len(gray_items)} 条")
print(f"  未分类:         {len(unclassified)} 条")

# ── 5. 可视化 ──
categories = [
    ('1_地形线(黄)', terrain, '#e6c300'),
    ('2_地层界线(黄)', boundaries, '#b38600'),
    ('3_产状-红', dip_red, '#e74c3c'),
    ('4_产状-蓝', dip_blue, '#3498db'),
    ('5_产状-绿', dip_green, '#2ecc71'),
    ('6_文字/图框(灰)', gray_items, '#999999'),
    ('7_未分类', unclassified, '#cccccc'),
]

fig, axes = plt.subplots(2, 4, figsize=(28, 14))
for ax, (title, items, color) in zip(axes.flat, categories):
    for p in items:
        pts = np.array(p['pts'])
        ax.fill(pts[:, 0], pts[:, 1], color=color, alpha=0.6, linewidth=0.1, edgecolor='#333')
    ax.set_xlim(0, 1740); ax.set_ylim(1034, 0)
    ax.set_aspect('equal')
    ax.set_title(f'{title} ({len(items)}条)', fontsize=10)

if len(categories) < 8:
    axes.flat[-1].set_visible(False)

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'dxf_color_v2_separated.png'), dpi=150)
print("\n已保存: dxf_color_v2_separated.png")

# ── 6. 叠加图 ──
fig2, ax2 = plt.subplots(figsize=(18, 12))
for items, c in [(terrain, '#e6c300'), (boundaries, '#b38600'),
                  (dip_red, '#e74c3c'), (dip_blue, '#3498db'),
                  (dip_green, '#2ecc71'), (gray_items, '#999999')]:
    for p in items:
        pts = np.array(p['pts'])
        ax2.fill(pts[:, 0], pts[:, 1], color=c, alpha=0.5, linewidth=0.1, edgecolor=c)

from matplotlib.patches import Patch
leg = [Patch(facecolor=c, alpha=0.5, label=n) for c, n in [
    ('#e6c300','地形线'),('#b38600','地层界线'),
    ('#e74c3c','产状-红'),('#3498db','产状-蓝'),
    ('#2ecc71','产状-绿'),('#999999','文字/图框')]]
ax2.legend(handles=leg, loc='upper right', fontsize=9)
ax2.set_xlim(0,1740); ax2.set_ylim(1034,0)
ax2.set_aspect('equal')
ax2.set_title('按原始图颜色分离（渲染像素比对）', fontsize=14)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'dxf_color_v2_overlay.png'), dpi=150)
print("已保存: dxf_color_v2_overlay.png")

# ── 7. 各颜色清单 ──
for title, items, c, d in categories:
    if len(items) <= 20:
        print(f"\n{title}:")
        for p in sorted(items, key=lambda x: x.get('total_pixels',0), reverse=True):
            print(f"  #{p['id']}: 面积={p['area']:.0f} 位置=({p['cx']:.0f},{p['cy']:.0f}) "
                  f"总像素={p.get('total_pixels',0)} 色={p.get('color','?')}")

print("\n请查看 dxf_color_v2_overlay.png")
