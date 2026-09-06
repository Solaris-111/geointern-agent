"""
从 potrace DXF 中半自动分离线状要素（地形线、地层界线）和块状要素（文字、花纹）。
原理：potrace 把每条"线"描成了闭合多段线（线的轮廓），线状要素的特征是
细长（长度 >> 宽度），块状要素则是紧凑的。
"""
import ezdxf
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from shapely.geometry import Polygon as ShapelyPolygon, LineString, Point
import json, os

DXF_PATH = r"E:\成长日志\大三上\周口店大报告图片\1_20260716_170053.dxf"
OUT_DIR = r"d:\geointern-agent"
os.makedirs(OUT_DIR, exist_ok=True)

doc = ezdxf.readfile(DXF_PATH)
msp = doc.modelspace()

# ── 1. 提取所有多段线，计算几何特征 ──
features = []
for i, pl in enumerate(msp.query('POLYLINE')):
    pts = np.array([(v.dxf.location.x, v.dxf.location.y) for v in pl.vertices])
    if len(pts) < 3:
        continue

    # 闭合多段线 → shapely polygon
    pg = ShapelyPolygon(pts)
    if not pg.is_valid:
        pg = pg.buffer(0)

    area = pg.area
    perimeter = pg.length
    centroid = pg.centroid
    bounds = pg.bounds  # minx, miny, maxx, maxy
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    bbox_area = width * height

    # 细长度指标
    if bbox_area > 0:
        fill_ratio = area / bbox_area  # 填充率：线状约0.1-0.5，块状约0.8-1.0
    else:
        fill_ratio = 0

    if height > 0:
        aspect = width / height if width > height else height / width
    else:
        aspect = 0

    # thinness = perimeter² / (4π × area)，线状很大，块状接近1
    if area > 0:
        thinness = (perimeter * perimeter) / (4 * np.pi * area)
    else:
        thinness = 0

    features.append({
        'id': i,
        'pts': pts.tolist(),
        'area': area,
        'perimeter': perimeter,
        'width': width,
        'height': height,
        'aspect': aspect,
        'fill_ratio': fill_ratio,
        'thinness': thinness,
        'centroid_x': centroid.x,
        'centroid_y': centroid.y,
        'bounds': list(bounds),
    })

print(f"总计: {len(features)} 条多段线")

# ── 2. 自动分类 ──
# 线状：thinness > 50 且 fill_ratio < 0.5（细长、bbox内填充少）
# 块状：thinness < 20 且 fill_ratio > 0.6
# 中间：待定

line_like = []
block_like = []
uncertain = []

for f in features:
    if f['thinness'] > 50 and f['fill_ratio'] < 0.5:
        line_like.append(f)
    elif f['thinness'] < 20 and f['fill_ratio'] > 0.6:
        block_like.append(f)
    else:
        uncertain.append(f)

print(f"自动分类：线状={len(line_like)}, 块状={len(block_like)}, 待定={len(uncertain)}")

# 对线状进一步细分：按位置（Y坐标）和走向分类
# 上部（Y<400）→ 可能是地形线
# 中部 → 可能是地层界线
# 下部 → 可能是图例/图名区域

upper_lines = [f for f in line_like if f['centroid_y'] < 400]
middle_lines = [f for f in line_like if 400 <= f['centroid_y'] < 750]
lower_lines = [f for f in line_like if f['centroid_y'] >= 750]

print(f"  上部线状(Y<400): {len(upper_lines)}")
print(f"  中部线状(400-750): {len(middle_lines)}")
print(f"  下部线状(>=750): {len(lower_lines)}")

# ── 3. 渲染色标图：每种分类不同颜色 ──
fig, axes = plt.subplots(1, 3, figsize=(24, 10))

colors_map = [
    ('线状要素（共{}条）'.format(len(line_like)), line_like, '#e74c3c', '地形线/地层界线候选'),
    ('块状要素（共{}条）'.format(len(block_like)), block_like, '#3498db', '文字/花纹填充候选'),
    ('待分类（共{}条）'.format(len(uncertain)), uncertain, '#f39c12', '需人工判断'),
]

for ax, (title, items, color, desc) in zip(axes, colors_map):
    for f in items:
        pts = np.array(f['pts'])
        ax.fill(pts[:, 0], pts[:, 1], color=color, alpha=0.6, linewidth=0.2, edgecolor='black')
    ax.set_xlim(0, 1740)
    ax.set_ylim(1034, 0)
    ax.set_aspect('equal')
    ax.set_title(f'{title}\n{desc}', fontsize=11)

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'dxf_classified.png'), dpi=150)
print("已保存: dxf_classified.png")

# ── 4. 单独渲染线状要素，编号标注 ──
fig2, ax2 = plt.subplots(figsize=(18, 12))

# 按长度排序线状要素
line_like_sorted = sorted(line_like, key=lambda f: f['perimeter'], reverse=True)

colors = plt.cm.tab20(np.linspace(0, 1, len(line_like_sorted)))
for i, f in enumerate(line_like_sorted):
    pts = np.array(f['pts'])
    ax2.fill(pts[:, 0], pts[:, 1], color=colors[i % 20], alpha=0.5, linewidth=0.3, edgecolor='black')
    ax2.annotate(str(i + 1),
                 (f['centroid_x'], f['centroid_y']),
                 fontsize=5, ha='center', va='center',
                 bbox=dict(boxstyle='round,pad=0.1', facecolor='white', alpha=0.8))

ax2.set_xlim(0, 1740)
ax2.set_ylim(1034, 0)
ax2.set_aspect('equal')
ax2.set_title(f'线状要素编号（共{len(line_like_sorted)}条，按周长降序）\n红=长，蓝=短', fontsize=12)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'dxf_lines_labeled.png'), dpi=150)
print("已保存: dxf_lines_labeled.png")

# ── 5. 输出线状要素清单 ──
print("\n=== 线状要素清单（前20条）===")
print(f"{'编号':<5} {'周长':<10} {'宽':<8} {'高':<8} {'填充率':<8} {'中心X':<8} {'中心Y':<8} {'位置推测'}")
print("-" * 75)
for i, f in enumerate(line_like_sorted[:20]):
    perimeter = f['perimeter']
    width = f['width']
    height = f['height']
    fill = f['fill_ratio']
    cx = f['centroid_x']
    cy = f['centroid_y']

    if cy < 350:
        pos = '上部→可能地形线'
    elif 350 <= cy < 750:
        pos = '中部→可能地层界线'
    else:
        pos = '下部→图例/图名区'

    print(f"{i+1:<5} {perimeter:<10.1f} {width:<8.1f} {height:<8.1f} {fill:<8.3f} {cx:<8.0f} {cy:<8.0f} {pos}")

# ── 6. 保存特征数据供后续使用 ──
output_json = os.path.join(OUT_DIR, 'dxf_features.json')
with open(output_json, 'w', encoding='utf-8') as f:
    json.dump({
        'line_like': [{'id': x['id'], 'perimeter': x['perimeter'],
                        'centroid_x': x['centroid_x'], 'centroid_y': x['centroid_y'],
                        'width': x['width'], 'height': x['height'],
                        'fill_ratio': x['fill_ratio'], 'thinness': x['thinness']}
                       for x in line_like_sorted],
        'block_like_count': len(block_like),
        'uncertain_count': len(uncertain),
    }, f, ensure_ascii=False, indent=2)
print(f"\n特征数据已保存: {output_json}")
print(f"\n请查看 dxf_classified.png 和 dxf_lines_labeled.png")
print(f"然后在 line_like 清单中指认哪些编号对应地形线、哪些对应地层界线。")
