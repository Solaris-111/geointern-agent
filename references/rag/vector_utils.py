"""
矢量 DXF 分析工具
从 img2dxf 矢量化 DXF 中提取地形线、比例尺、地层界线位置。
"""
import ezdxf
import numpy as np
from collections import defaultdict


def extract_terrain_from_vector(dxf_path, x_bins=200):
    """
    从矢量化 DXF 提取地形线。
    原理: 矢量化图中地形线是最上方的连续边缘。

    Returns: [(x_px, y_px), ...] 像素坐标的地形线
    """
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()

    # 收集所有顶点坐标
    all_pts = []
    for poly in msp.query('POLYLINE'):
        for pt in poly.points():
            all_pts.append((pt[0], pt[1]))

    xs = np.array([p[0] for p in all_pts])
    ys = np.array([p[1] for p in all_pts])

    x_min, x_max = xs.min(), xs.max()
    y_min, y_max = ys.min(), ys.max()
    print(f"Vector extent: x=[{x_min:.0f}, {x_max:.0f}], y=[{y_min:.0f}, {y_max:.0f}]")

    # 将 x 分成 bins, 每个 bin 取最大的 y (最上面的顶点 = 地形线)
    bin_width = (x_max - x_min) / x_bins
    terrain = []
    for i in range(x_bins):
        x0 = x_min + i * bin_width
        x1 = x0 + bin_width
        mask = (xs >= x0) & (xs < x1)
        if mask.any():
            terrain.append((float((x0 + x1) / 2), float(ys[mask].max())))

    # 降采样 + 平滑
    if len(terrain) > 80:
        step = len(terrain) // 60
        terrain = [terrain[i] for i in range(0, len(terrain), step)]
        # 确保最后一个点
        xs_all = np.array([p[0] for p in all_pts])
        x_last = xs_all.max()
        y_at_last = ys[xs_all >= x_last - bin_width].max() if (xs_all >= x_last - bin_width).any() else terrain[-1][1]
        terrain.append((float(x_last), float(y_at_last)))

    return terrain, (x_min, x_max, y_min, y_max)


def find_scale_bar(dxf_path):
    """
    在矢量化 DXF 中找比例尺 "20 40m"。
    矢量化后的比例尺文字会被描成小多边形, 比例尺线是长水平线。

    Returns: {px_per_m, tick_px_positions, ...} or None
    """
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()

    # 收集所有顶点, 找底部的水平长线段
    all_pts = []
    for poly in msp.query('POLYLINE'):
        pts = list(poly.points())
        if len(pts) == 2:  # 线段
            all_pts.append(pts)

    if not all_pts:
        return None

    # 找 y 在底部 30% 区域内的水平线段
    all_y = [p[0][1] for p in all_pts] + [p[1][1] for p in all_pts]
    y_bot = np.percentile(all_y, 30)

    h_lines = []
    for pts in all_pts:
        y_avg = (pts[0][1] + pts[1][1]) / 2
        if y_avg < y_bot:
            dy = abs(pts[0][1] - pts[1][1])
            if dy < 5:  # 近似水平
                h_lines.append({
                    'y': y_avg,
                    'x1': pts[0][0], 'x2': pts[1][0],
                    'length': abs(pts[0][0] - pts[1][0])
                })

    if not h_lines:
        return None

    # 找等间距的水平线段簇 (比例尺刻度线)
    h_lines.sort(key=lambda l: l['y'])
    for i in range(len(h_lines) - 2):
        y_gap = abs(h_lines[i + 1]['y'] - h_lines[i]['y'])
        if y_gap < 3:  # 同一行的线段
            continue

    # 简单策略: 找同一 y 附近有多条等间距短线的行
    from collections import Counter
    y_groups = defaultdict(list)
    for hl in h_lines:
        y_key = round(hl['y'] / 10) * 10
        y_groups[y_key].append(hl)

    best_ticks = None
    for y_key, lines in y_groups.items():
        if 3 <= len(lines) <= 5:
            lines.sort(key=lambda l: l['x1'])
            centers = [(l['x1'] + l['x2']) / 2 for l in lines]
            gaps = [centers[j + 1] - centers[j] for j in range(len(centers) - 1)]
            if gaps and max(gaps) - min(gaps) < min(gaps) * 0.3:  # 等间距
                best_ticks = centers
                break

    if best_ticks and len(best_ticks) >= 3:
        span = best_ticks[-1] - best_ticks[0]
        px_per_m = span / 40.0  # 假设 3 条刻度线 = 0m, 20m, 40m
        return {
            'px_per_m': px_per_m,
            'span_px': span,
            'tick_centers': best_ticks,
        }

    return None


def extract_boundary_positions(dxf_path, terrain, extent):
    """
    找地层界线在地形线上的位置。
    原理: 地层界线是从地形线向下延伸的近似竖直线段。
    在矢量化图中, 这些表现为与地形线相交的向下线段。

    Returns: [x_px, ...] 接触点的 x 像素坐标
    """
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()
    x_min, x_max, y_min, y_max = extent

    # 地形插值
    t_xs = np.array([p[0] for p in terrain])
    t_ys = np.array([p[1] for p in terrain])

    def terrain_y(x):
        return np.interp(x, t_xs, t_ys)

    # 找接近竖直的线段 (角度 > 60°)
    vertical_segs = []
    for poly in msp.query('POLYLINE'):
        pts = list(poly.points())
        if len(pts) >= 2:
            for j in range(len(pts) - 1):
                dx = abs(pts[j][0] - pts[j + 1][0])
                dy = abs(pts[j][1] - pts[j + 1][1])
                if dy > dx * 1.5 and dy > 10:  # 接近竖直
                    vertical_segs.append({
                        'x': (pts[j][0] + pts[j + 1][0]) / 2,
                        'y_top': max(pts[j][1], pts[j + 1][1]),
                        'y_bot': min(pts[j][1], pts[j + 1][1]),
                    })

    if not vertical_segs:
        return []

    # 找从地形线附近开始的竖直线段
    candidates = []
    for vs in vertical_segs:
        ty = terrain_y(vs['x'])
        if abs(vs['y_top'] - ty) < 30:  # 线段顶端接近地形
            candidates.append(vs)

    # 按 x 聚类, 每个聚类的中心 = 一个接触点
    if not candidates:
        return []

    candidates.sort(key=lambda c: c['x'])
    boundaries = []
    used = set()
    for i, c in enumerate(candidates):
        if i in used:
            continue
        cluster = [c]
        used.add(i)
        for j in range(i + 1, len(candidates)):
            if j in used:
                continue
            if abs(candidates[j]['x'] - c['x']) < 15:
                cluster.append(candidates[j])
                used.add(j)
        if len(cluster) >= 2:  # 至少2条线段支持
            avg_x = sum(v['x'] for v in cluster) / len(cluster)
            boundaries.append(avg_x)

    boundaries.sort()
    return boundaries


def calibrate_from_vector(dxf_path):
    """
    从矢量 DXF 一步完成标定: 提取地形 + 比例尺 + 界线位置。
    返回可喂给 generate_cross_section 的数据。
    """
    terrain, extent = extract_terrain_from_vector(dxf_path)
    scale_info = find_scale_bar(dxf_path)
    boundaries = extract_boundary_positions(dxf_path, terrain, extent)

    x_min, x_max, y_min, y_max = extent

    if scale_info:
        px_per_m = scale_info['px_per_m']
    else:
        # fallback: 用 image 标定方法
        px_per_m = (x_max - x_min) / 200.0
        scale_info = {'px_per_m': px_per_m, 'fallback': True}

    # 换算地形为实际坐标 (m)
    y_ref = y_max  # 地形最高点
    terrain_m = []
    for x_px, y_px in terrain:
        x_m = (x_px - x_min) / px_per_m
        elev_m = 150.0 + (y_ref - y_px) / px_per_m  # 假设最低点 ~150m
        terrain_m.append((round(x_m, 1), round(elev_m, 1)))

    return {
        'terrain': terrain_m,
        'px_per_m': px_per_m,
        'scale_info': scale_info,
        'boundaries_px': boundaries,
        'extent': extent,
    }


if __name__ == '__main__':
    import sys, json
    path = sys.argv[1] if len(sys.argv) > 1 else r"E:\成长日志\大三上\周口店大报告图片\1_20260716_170053.dxf"

    result = calibrate_from_vector(path)
    print(f"px_per_m: {result['px_per_m']:.2f}")
    print(f"Terrain: {len(result['terrain'])} pts, X: {result['terrain'][0][0]:.0f}-{result['terrain'][-1][0]:.0f}m")
    print(f"Boundaries found: {len(result['boundaries_px'])} at px:", [f'{b:.0f}' for b in result['boundaries_px']])

    with open('d:/geointern-agent/output/vector_cal.json', 'w') as f:
        json.dump({k: v for k, v in result.items() if k != 'extent'},
                  f, ensure_ascii=False, indent=2, default=str)
    print("Saved to vector_cal.json")
