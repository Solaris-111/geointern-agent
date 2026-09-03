"""
v4: 不对多边形填充采样，而是对每条多段线的轮廓做缓冲带（±3像素），
    看缓冲带内有哪些颜色。这样"描边轮廓"就能和"线条颜色"对上。
"""
import ezdxf, numpy as np, os
from shapely.geometry import Polygon, LineString, Point
from shapely import buffer as shapely_buffer
from PIL import Image, ImageEnhance
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DXF_PATH = r"E:\成长日志\大三上\周口店大报告图片\1_20260716_170053.dxf"
PNG_PATH = r"E:\成长日志\大三上\周口店大报告图片\1.png"
OUT_DIR = r"d:\geointern-agent"

# ── 1. 增强 PNG + 颜色掩码 ──
img = Image.open(PNG_PATH).convert('RGB')
img = ImageEnhance.Contrast(img).enhance(3.0)
img = ImageEnhance.Color(img).enhance(5.0)
arr = np.array(img).astype(np.float64)
h, w = arr.shape[:2]
print(f"PNG: {w}×{h}")

r_arr, g_arr, b_arr = arr[:,:,0], arr[:,:,1], arr[:,:,2]

mask_y = np.zeros((h, w), dtype=np.uint8)
mask_r = np.zeros((h, w), dtype=np.uint8)
mask_b = np.zeros((h, w), dtype=np.uint8)
mask_g = np.zeros((h, w), dtype=np.uint8)
mask_gray = np.zeros((h, w), dtype=np.uint8)

for y in range(h):
    for x in range(w):
        r, g, b = r_arr[y,x], g_arr[y,x], b_arr[y,x]
        if r > 240 and g > 240 and b > 240:
            continue
        if abs(r-g) < 30 and r > b+30 and g > b+30 and r > 80:
            mask_y[y,x] = 1
        elif r > g+40 and r > b+40 and r > 100:
            mask_r[y,x] = 1
        elif b > r+20 and b > g+20 and b > 80:
            mask_b[y,x] = 1
        elif g > r+40 and g > b+40 and g > 80:
            mask_g[y,x] = 1
        elif max(r,g,b) < 200:
            mask_gray[y,x] = 1

print(f"掩码: Y={mask_y.sum()} R={mask_r.sum()} B={mask_b.sum()} G={mask_g.sum()} Gray={mask_gray.sum()}")

# ── 2. 读 DXF，对每条多段线做缓冲带 ──
doc = ezdxf.readfile(DXF_PATH)
msp = doc.modelspace()
scale = 0.5

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

    # 对多边形边界做缓冲（±2 DXF单位 = ±1像素）
    boundary = pg.boundary
    buffered = boundary.buffer(3.0)  # 3 DXF units ≈ 1.5 px
    if buffered.is_empty:
        continue

    bounds_dxf = buffered.bounds
    poly_data[poly_idx] = {
        'id': i, 'pts': pts.tolist(),
        'area': pg.area, 'cx': pg.centroid.x, 'cy': pg.centroid.y,
        'w': bounds_dxf[2]-bounds_dxf[0], 'h': bounds_dxf[3]-bounds_dxf[1],
        'buffer_geom': buffered,
    }
    poly_idx += 1

print(f"缓冲带: {poly_idx} 条")

# ── 3. 渲染缓冲带到画布（每个多段线一个ID） ──
id_canvas = np.full((h, w), -1, dtype=np.int32)

for pid, pdata in poly_data.items():
    buffered = pdata['buffer_geom']
    bounds = buffered.bounds
    minx = max(0, int(bounds[0]*scale))
    miny = max(0, int(bounds[1]*scale))
    maxx = min(w-1, int(bounds[2]*scale))
    maxy = min(h-1, int(bounds[3]*scale))

    for py in range(miny, maxy+1):
        for px in range(minx, maxx+1):
            if buffered.contains(Point(px/scale, py/scale)):
                # 如果已有其他多段线占用，保留面积更小的（更精确的）
                if id_canvas[py, px] == -1:
                    id_canvas[py, px] = pid
                # 否则不覆盖（先到先得）

# ── 4. 统计颜色 ──
color_counts = defaultdict(lambda: {'yellow':0,'red':0,'blue':0,'green':0,'gray':0})
for py in range(h):
    for px in range(w):
        pid = id_canvas[py, px]
        if pid < 0: continue
        if mask_y[py,px]:    color_counts[pid]['yellow'] += 1
        elif mask_r[py,px]:  color_counts[pid]['red'] += 1
        elif mask_b[py,px]:  color_counts[pid]['blue'] += 1
        elif mask_g[py,px]:  color_counts[pid]['green'] += 1
        elif mask_gray[py,px]: color_counts[pid]['gray'] += 1

# ── 5. 分类 ──
terrain = []; boundaries = []; dip_red = []; dip_blue = []; dip_green = []
gray_items = []; unclassified = []

for pid, pdata in poly_data.items():
    cc = color_counts[pid]
    total = sum(cc.values())
    if total < 2:
        unclassified.append(pdata)
        continue

    best = max(cc, key=cc.get)
    ratio = cc[best] / total
    pdata['color'] = best
    pdata['total_pixels'] = total

    if best == 'yellow':
        cy = pdata['cy']; ww = pdata['w']
        if cy < 350 and ww > 80:
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

print(f"\n分类结果：")
print(f"  地形线（黄）:   {len(terrain)}")
print(f"  地层界线（黄）: {len(boundaries)}")
print(f"  产状-红:        {len(dip_red)}")
print(f"  产状-蓝:        {len(dip_blue)}")
print(f"  产状-绿:        {len(dip_green)}")
print(f"  灰/黑:          {len(gray_items)}")
print(f"  未分类:         {len(unclassified)}")

# ── 6. 可视化 ──
categories = [
    ('地形线(黄)', terrain, '#e6c300'),
    ('地层界线(黄)', boundaries, '#b38600'),
    ('产状-红', dip_red, '#e74c3c'),
    ('产状-蓝', dip_blue, '#3498db'),
    ('产状-绿', dip_green, '#2ecc71'),
    ('文字图框(灰)', gray_items, '#999999'),
]

fig, axes = plt.subplots(2, 3, figsize=(22, 15))
for ax, (title, items, color) in zip(axes.flat, categories):
    for p in items:
        pts = np.array(p['pts'])
        ax.fill(pts[:, 0], pts[:, 1], color=color, alpha=0.6, linewidth=0.1, edgecolor='#333')
    ax.set_xlim(0, 1740); ax.set_ylim(1034, 0)
    ax.set_aspect('equal')
    ax.set_title(f'{title} ({len(items)}条)', fontsize=11)

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'dxf_v4_buffer.png'), dpi=150)
print("\n已保存: dxf_v4_buffer.png")

# 叠加图
fig2, ax2 = plt.subplots(figsize=(18, 12))
for items, c in [(terrain, '#e6c300'), (boundaries, '#cc8800'),
                  (dip_red, '#e74c3c'), (dip_blue, '#3498db'),
                  (dip_green, '#2ecc71'), (gray_items, '#aaaaaa')]:
    for p in items:
        pts = np.array(p['pts'])
        ax2.fill(pts[:, 0], pts[:, 1], color=c, alpha=0.5, linewidth=0.1, edgecolor=c)

from matplotlib.patches import Patch
leg = [Patch(facecolor=c, alpha=0.5, label=n) for c,n in [
    ('#e6c300','地形线'),('#cc8800','地层界线'),
    ('#e74c3c','产状-红'),('#3498db','产状-蓝'),
    ('#2ecc71','产状-绿'),('#aaaaaa','文字/图框')]]
ax2.legend(handles=leg, loc='upper right', fontsize=9)
ax2.set_xlim(0,1740); ax2.set_ylim(1034,0); ax2.set_aspect('equal')
ax2.set_title('v4 缓冲带匹配颜色', fontsize=14)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'dxf_v4_overlay.png'), dpi=150)
print("已保存: dxf_v4_overlay.png")

for title, items, c in categories:
    print(f"\n{title} ({len(items)}):")
    for p in sorted(items, key=lambda x: x.get('total_pixels',0), reverse=True)[:8]:
        print(f"  #{p['id']}: pos=({p['cx']:.0f},{p['cy']:.0f}) 像素={p.get('total_pixels',0)}")

print("\n请查看输出图")
