"""
v2: 放宽分类 + 按位置分割 + 交互式输出，让用户指认线条。
思路：potrace 描的闭合轮廓中，"线"的特征是——bbox细长、thinness高。
用复合评分排序，而不是硬阈值。
"""
import ezdxf, numpy as np, json, os
from shapely.geometry import Polygon as ShapelyPolygon
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DXF_PATH = r"E:\成长日志\大三上\周口店大报告图片\1_20260716_170053.dxf"
OUT_DIR = r"d:\geointern-agent"

doc = ezdxf.readfile(DXF_PATH)
msp = doc.modelspace()

# ── 1. 提取特征 ──
features = []
for i, pl in enumerate(msp.query('POLYLINE')):
    pts = np.array([(v.dxf.location.x, v.dxf.location.y) for v in pl.vertices])
    if len(pts) < 3:
        continue
    pg = ShapelyPolygon(pts)
    if not pg.is_valid:
        pg = pg.buffer(0)
    area = pg.area; perimeter = pg.length
    centroid = pg.centroid
    bounds = pg.bounds
    w, h = bounds[2] - bounds[0], bounds[3] - bounds[1]
    bbox_area = w * h
    fill = area / bbox_area if bbox_area > 0 else 0
    aspect = max(w, h) / min(w, h) if min(w, h) > 0 else 0
    thinness = (perimeter * perimeter) / (4 * np.pi * area) if area > 0 else 0

    # 线状评分：thinness高 + aspect高 + fill低 → 更像线
    # 取 log 压一下 thinness 的极端值
    line_score = np.log1p(thinness) * np.log1p(aspect) * (1 - fill)

    features.append({
        'id': i, 'pts': pts.tolist(),
        'area': area, 'perimeter': perimeter,
        'w': w, 'h': h, 'aspect': aspect,
        'fill': fill, 'thinness': thinness,
        'line_score': line_score,
        'cx': centroid.x, 'cy': centroid.y,
        'bounds': list(bounds),
    })

features.sort(key=lambda f: f['line_score'], reverse=True)

print(f"总计: {len(features)} 条多段线")
print(f"line_score 范围: {features[0]['line_score']:.1f} ~ {features[-1]['line_score']:.1f}")

# ── 2. 按 line_score 分层渲染 ──
# Top N → 最可能是线，渲染为醒目颜色
fig, axes = plt.subplots(2, 2, figsize=(22, 18))

groups = [
    ('A组: 最像线 (top 20)', features[:20], '#e74c3c'),
    ('B组: 像线 (top 21-60)', features[20:60], '#e67e22'),
    ('C组: 可能线 (top 61-150)', features[60:150], '#f1c40f'),
    ('D组: 块状/文字/花纹 (其余)', features[150:], '#95a5a6'),
]

for ax, (title, items, color) in zip(axes.flat, groups):
    for f in items:
        pts = np.array(f['pts'])
        ax.fill(pts[:, 0], pts[:, 1], color=color, alpha=0.5, linewidth=0.1, edgecolor='gray')
    ax.set_xlim(0, 1740); ax.set_ylim(1034, 0)
    ax.set_aspect('equal')
    ax.set_title(title + f' ({len(items)}条)', fontsize=10)

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'dxf_score_groups.png'), dpi=150)
print("已保存: dxf_score_groups.png")

# ── 3. 编号标注图（前60条候选线） ──
fig2, ax2 = plt.subplots(figsize=(20, 13))
cmap = plt.cm.tab20
for rank, f in enumerate(features[:60]):
    pts = np.array(f['pts'])
    color = cmap(rank % 20 / 20)
    ax2.fill(pts[:, 0], pts[:, 1], color=color, alpha=0.5, linewidth=0.3, edgecolor='black')
    ax2.annotate(f'#{rank+1}', (f['cx'], f['cy']),
                 fontsize=5, ha='center', va='center',
                 bbox=dict(boxstyle='round,pad=0.1', facecolor='white', alpha=0.85))

ax2.set_xlim(0, 1740); ax2.set_ylim(1034, 0)
ax2.set_aspect('equal')
ax2.set_title('线状候选 Top 60（编号=line_score排名）', fontsize=12)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'dxf_top60_labeled.png'), dpi=150)
print("已保存: dxf_top60_labeled.png")

# ── 4. 按 Y 位置分区域统计 ──
# 根据 Qwen 分析，剖面图上部是地形线和地层分布，下部是图例和图名
zones = [
    ('上部剖面区 Y<350', 0, 350, '地形线 + 地层界线所在地'),
    ('中部剖面区 Y350-700', 350, 700, '地层界线 + 岩性花纹区'),
    ('下部图例区 Y>700', 700, 1034, '图例 + 图名 + 比例尺'),
]

for zname, ymin, ymax, desc in zones:
    zone_items = [f for f in features if ymin <= f['cy'] < ymax]
    top5 = sorted(zone_items, key=lambda f: f['line_score'], reverse=True)[:5]
    print(f"\n{zname} ({desc}) — 共{len(zone_items)}条")
    print(f"  Top 5 线状候选:")
    for j, f in enumerate(top5):
        print(f"    #{features.index(f)+1}: cx={f['cx']:.0f} cy={f['cy']:.0f} "
              f"w={f['w']:.0f} h={f['h']:.0f} line_score={f['line_score']:.1f}")

# ── 5. 交互指认清单 ──
print("\n" + "=" * 70)
print("指认说明：")
print("  查看 dxf_score_groups.png — A组红=最像线, B组橙, C组黄, D组灰")
print("  查看 dxf_top60_labeled.png — 前60条有编号")
print("  对比原始图 1.png，告诉我：")
print("    - 地形线的编号（通常是上部区域一条很长的波浪线）")
print("    - 各地层界线的编号（中部区域，倾斜直线）")
print("    - 画框/辅助线的编号（如果不需要提取可以忽略）")
print("=" * 70)

# 保存Top 60的JSON
output = []
for rank, f in enumerate(features[:60]):
    output.append({
        'rank': rank + 1,
        'id': f['id'],
        'cx': round(f['cx'], 1), 'cy': round(f['cy'], 1),
        'w': round(f['w'], 1), 'h': round(f['h'], 1),
        'thinness': round(f['thinness'], 1),
        'fill': round(f['fill'], 3),
        'line_score': round(f['line_score'], 1),
    })
with open(os.path.join(OUT_DIR, 'dxf_top60.json'), 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print("\nTop 60 候选数据已保存: dxf_top60.json")
