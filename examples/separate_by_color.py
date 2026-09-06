"""
用相对色偏检测分离颜色。图面近白，线条颜色淡，需要灵敏度。
黄色 → R≈G > B (即使值很接近)
红色 → R > G 且 R > B
蓝色 → B > R 且 B > G
绿色 → G > R 且 G > B
"""
import ezdxf, numpy as np, os, json
from shapely.geometry import Polygon, Point
from scipy.spatial import ConvexHull
from PIL import Image
from collections import Counter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DXF_PATH = r"E:\成长日志\大三上\周口店大报告图片\1_20260716_170053.dxf"
PNG_PATH = r"E:\成长日志\大三上\周口店大报告图片\1.png"
OUT_DIR = r"d:\geointern-agent"

# ── 1. 读取 PNG ──
img = Image.open(PNG_PATH).convert('RGB')
arr = np.array(img).astype(np.float64)
h, w = arr.shape[:2]
print(f"PNG: {w}×{h}")

# ── 2. 找背景色（最高频颜色） ──
quantized = (arr // 16) * 16
flat = [tuple(q) for q in quantized.reshape(-1, 3)]
bg_color = Counter(flat).most_common(1)[0][0]
print(f"背景色: RGB{bg_color}")

# ── 3. 色偏检测：相对于背景，哪个通道偏低最少的就是色调方向 ──
# 策略：对于"非背景"像素（明显偏离背景的暗像素），看色偏方向

r_arr = arr[:,:,0]; g_arr = arr[:,:,1]; b_arr = arr[:,:,2]

# 亮度阈值：比背景暗 15 以上的才算"有内容"
brightness = (r_arr + g_arr + b_arr) / 3
bg_brightness = sum(bg_color) / 3
is_content = brightness < (bg_brightness - 15)

print(f"有内容像素: {is_content.sum()} ({is_content.sum()/(w*h)*100:.1f}%)")

# 对内容像素做色偏分类
mask_yellow = np.zeros((h, w), dtype=bool)
mask_red = np.zeros((h, w), dtype=bool)
mask_blue = np.zeros((h, w), dtype=bool)
mask_green = np.zeros((h, w), dtype=bool)
mask_gray = np.zeros((h, w), dtype=bool)

for y in range(h):
    for x in range(w):
        if not is_content[y, x]:
            continue
        r, g, b = r_arr[y,x], g_arr[y,x], b_arr[y,x]
        rg_diff = abs(r - g)
        rb_diff = abs(r - b)
        gb_diff = abs(g - b)
        min_diff = min(rg_diff, rb_diff, gb_diff)

        # 灰度：三个通道接近 (最大差 < 12)
        if max(rg_diff, rb_diff, gb_diff) < 12:
            mask_gray[y, x] = True
        # 黄色：R≈G 且都 > B (B明显偏低)
        elif rg_diff < 15 and r > b + 8 and g > b + 8:
            mask_yellow[y, x] = True
        # 红色：R 明显 > G 且 R 明显 > B
        elif r > g + 10 and r > b + 10:
            mask_red[y, x] = True
        # 蓝色：B 明显 > R 且 B 明显 > G
        elif b > r + 10 and b > g + 10:
            mask_blue[y, x] = True
        # 绿色：G 明显 > R 且 G 明显 > B
        elif g > r + 10 and g > b + 10:
            mask_green[y, x] = True
        else:
            mask_gray[y, x] = True  # 默认归灰

print(f"黄色: {mask_yellow.sum()}")
print(f"红色: {mask_red.sum()}")
print(f"蓝色: {mask_blue.sum()}")
print(f"绿色: {mask_green.sum()}")
print(f"灰色: {mask_gray.sum()}")

# ── 4. DXF 多段线按颜色掩码分类 ──
doc = ezdxf.readfile(DXF_PATH)
msp = doc.modelspace()

# DXF → PNG 坐标映射：DXF Y 向下=PNG Y 向下
# PNG 更小，需要缩放: scale = 870/1740 = 0.5, 517/1034 = 0.5
scale_x = w / 1740.0
scale_y = h / 1034.0

def dxf_to_png(dxf_x, dxf_y):
    """DXF坐标 → PNG像素坐标"""
    px = int(dxf_x * scale_x)
    py = int(dxf_y * scale_y)
    return max(0, min(w-1, px)), max(0, min(h-1, py))

def classify_by_color(pg):
    """对多边形采样，判断主颜色"""
    centroid = pg.centroid
    sample_pts = [dxf_to_png(centroid.x, centroid.y)]

    # 轮廓采样
    ext = list(pg.exterior.coords)
    step = max(1, len(ext) // 12)
    for j in range(0, len(ext), step):
        sample_pts.append(dxf_to_png(ext[j][0], ext[j][1]))

    # 内部网格采样
    bounds = pg.bounds
    for fx in np.linspace(bounds[0], bounds[2], 5):
        for fy in np.linspace(bounds[1], bounds[3], 5):
            pt = Point(fx, fy)
            if pg.contains(pt) or pg.touches(pt):
                sample_pts.append(dxf_to_png(fx, fy))

    counts = {k:0 for k in ['yellow','red','blue','green','gray']}
    for spx, spy in sample_pts:
        if mask_yellow[spy, spx]: counts['yellow'] += 1
        elif mask_red[spy, spx]: counts['red'] += 1
        elif mask_blue[spy, spx]: counts['blue'] += 1
        elif mask_green[spy, spx]: counts['green'] += 1
        elif mask_gray[spy, spx]: counts['gray'] += 1

    total = sum(counts.values())
    return counts, total

yellow_items = []
red_items = []
blue_items = []
green_items = []
gray_items = []

for i, pl in enumerate(msp.query('POLYLINE')):
    pts = np.array([(v.dxf.location.x, v.dxf.location.y) for v in pl.vertices])
    if len(pts) < 3:
        continue
    pg = Polygon(pts)
    if not pg.is_valid:
        pg = pg.buffer(0)
    if pg.is_empty:
        continue

    counts, total = classify_by_color(pg)
    if total == 0:
        continue

    centroid = pg.centroid
    pdata = {
        'id': i, 'pts': pts.tolist(),
        'cx': centroid.x, 'cy': centroid.y,
        'area': pg.area,
        'color_counts': counts, 'total_samples': total,
    }

    # 找最高比例的颜色
    best_color = max(counts, key=counts.get)
    best_ratio = counts[best_color] / total if total > 0 else 0

    if best_ratio < 0.15:
        continue  # 太不确定，跳过

    if best_color == 'yellow':
        yellow_items.append(pdata)
    elif best_color == 'red':
        red_items.append(pdata)
    elif best_color == 'blue':
        blue_items.append(pdata)
    elif best_color == 'green':
        green_items.append(pdata)
    else:
        gray_items.append(pdata)

print(f"\n按颜色分类：")
print(f"  黄色: {len(yellow_items)} 条")
print(f"  红色: {len(red_items)} 条")
print(f"  蓝色: {len(blue_items)} 条")
print(f"  绿色: {len(green_items)} 条")
print(f"  灰色: {len(gray_items)} 条")

# ── 5. 黄色中细分地形线 vs 地层界线 ──
terrain_lines = []
formation_lines = []

for p in yellow_items:
    pts = np.array(p['pts'])
    cy = p['cy']
    bounds = Polygon(pts).bounds
    ww, hh = bounds[2]-bounds[0], bounds[3]-bounds[1]

    try:
        hull = ConvexHull(pts)
        hp = pts[hull.vertices]
    except:
        hp = pts
    max_d = 0
    for a in range(len(hp)):
        for b in range(a+1, len(hp)):
            d = np.sum((hp[a]-hp[b])**2)
            if d > max_d: max_d = d
    cl_length = np.sqrt(max_d)

    # 多边形面积小、在上部、长条形 → 地形线
    # 在中部、倾斜 → 地层界线
    if cy < 380 and (cl_length > 80 or ww > 150):
        terrain_lines.append(p)
    else:
        formation_lines.append(p)

print(f"  地形线:    {len(terrain_lines)} 条")
print(f"  地层界线:  {len(formation_lines)} 条")

# ── 6. 可视化 ──
categories = [
    ('地形线（黄）', terrain_lines, '#e6c300'),
    ('地层界线（黄）', formation_lines, '#b38600'),
    ('产状-红', red_items, '#e74c3c'),
    ('产状-蓝', blue_items, '#3498db'),
    ('产状-绿', green_items, '#2ecc71'),
    ('灰/黑（文字图框）', gray_items, '#777777'),
]

fig, axes = plt.subplots(2, 3, figsize=(22, 15))
for ax, (title, items, color) in zip(axes.flat, categories):
    for p in items:
        pts = np.array(p['pts'])
        ax.fill(pts[:, 0], pts[:, 1], color=color, alpha=0.6, linewidth=0.15, edgecolor='#333')
    ax.set_xlim(0, 1740); ax.set_ylim(1034, 0)
    ax.set_aspect('equal')
    ax.set_title(f'{title}\n({len(items)}条)', fontsize=11)

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'dxf_by_color.png'), dpi=150)
print("\n已保存: dxf_by_color.png")

# ── 7. 叠加图 ──
fig2, ax2 = plt.subplots(figsize=(18, 12))
color_map = [
    (terrain_lines, '#e6c300'),
    (formation_lines, '#b38600'),
    (red_items, '#e74c3c'),
    (blue_items, '#3498db'),
    (green_items, '#2ecc71'),
    (gray_items, '#999999'),
]
for items, c in color_map:
    for p in items:
        pts = np.array(p['pts'])
        ax2.fill(pts[:, 0], pts[:, 1], color=c, alpha=0.5, linewidth=0.1, edgecolor=c)

from matplotlib.patches import Patch
leg = [Patch(facecolor=c, alpha=0.5, label=n) for c, n in [
    ('#e6c300', '地形线'), ('#b38600', '地层界线'),
    ('#e74c3c', '产状-红'), ('#3498db', '产状-蓝'),
    ('#2ecc71', '产状-绿'), ('#999999', '文字/图框')]]
ax2.legend(handles=leg, loc='upper right', fontsize=9)
ax2.set_xlim(0, 1740); ax2.set_ylim(1034, 0)
ax2.set_aspect('equal')
ax2.set_title('按原始图颜色分离（色偏检测）', fontsize=14)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'dxf_by_color_overlay.png'), dpi=150)
print("已保存: dxf_by_color_overlay.png")
print("请打开查看")
