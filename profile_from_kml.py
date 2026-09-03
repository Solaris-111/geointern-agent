"""从 KML 路线生成地形剖面图"""

import xml.etree.ElementTree as ET
import math
import json
import sys
import requests
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from io import StringIO

# 设置中文字体
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Noto Sans SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# KML namespace
KML_NS = "http://www.opengis.net/kml/2.2"


def parse_kml(filepath):
    """解析 KML，返回 (路线名, 轨迹坐标列表, 观察点列表)"""
    tree = ET.parse(filepath)
    root = tree.getroot()
    ns = {"kml": KML_NS}

    doc_name = root.find(".//kml:Document/kml:name", ns)
    route_name = doc_name.text if doc_name is not None else "Unknown"

    # 提取轨迹
    coords_elem = root.find(".//kml:LineString/kml:coordinates", ns)
    track = []
    if coords_elem is not None and coords_elem.text:
        for line in coords_elem.text.strip().split():
            parts = line.split(",")
            if len(parts) >= 2:
                track.append((float(parts[0]), float(parts[1])))

    # 提取观察点
    points = []
    for pm in root.findall(".//kml:Placemark", ns):
        pm_name = pm.find("kml:name", ns)
        pm_point = pm.find(".//kml:Point/kml:coordinates", ns)
        pm_desc = pm.find("kml:description", ns)
        if pm_name is not None and pm_point is not None and pm_point.text:
            label = pm_name.text
            parts = pm_point.text.strip().split(",")
            lat, lon = float(parts[1]), float(parts[0])
            desc = pm_desc.text if pm_desc is not None else ""
            # 跳过路线本身
            if "行进路线" not in label:
                points.append({"name": label, "lon": lon, "lat": lat, "desc": desc})

    return route_name, track, points


def interpolate_track(track, spacing_m=50):
    """沿轨迹等距采样，返回 [(lon, lat, cum_dist_m), ...]"""
    if len(track) < 2:
        return []

    def haversine(lon1, lat1, lon2, lat2):
        R = 6371000
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # 计算每段长度
    segments = []
    total = 0
    for i in range(len(track) - 1):
        d = haversine(track[i][0], track[i][1], track[i + 1][0], track[i + 1][1])
        segments.append((track[i], track[i + 1], d))
        total += d

    # 等距采样
    samples = [(track[0][0], track[0][1], 0.0)]
    cumulative = 0
    target = spacing_m

    for p1, p2, seg_len in segments:
        while target < cumulative + seg_len and target <= total:
            frac = (target - cumulative) / seg_len
            lon = p1[0] + frac * (p2[0] - p1[0])
            lat = p1[1] + frac * (p2[1] - p1[1])
            samples.append((lon, lat, target))
            target += spacing_m
        cumulative += seg_len

    # 终点
    samples.append((track[-1][0], track[-1][1], total))

    return samples, total


def get_elevations(samples, batch_size=100):
    """通过 OpenTopoData API 获取高程"""
    elevations = []
    total = len(samples)

    for i in range(0, total, batch_size):
        batch = samples[i : i + batch_size]
        locations = "|".join(f"{lat},{lon}" for lon, lat, _ in batch)

        try:
            resp = requests.get(
                "https://api.opentopodata.org/v1/srtm30m",
                params={"locations": locations},
                timeout=60,
            )
            if resp.status_code == 200:
                results = resp.json().get("results", [])
                for j, r in enumerate(results):
                    idx = i + j
                    lon, lat, dist = samples[idx]
                    elevations.append((lon, lat, dist, r["elevation"]))
            else:
                print(f"  API error: HTTP {resp.status_code}")
                # 填充 NaN
                for j in range(len(batch)):
                    idx = i + j
                    lon, lat, dist = samples[idx]
                    elevations.append((lon, lat, dist, None))
        except Exception as e:
            print(f"  API request failed: {e}")
            for j in range(len(batch)):
                idx = i + j
                lon, lat, dist = samples[idx]
                elevations.append((lon, lat, dist, None))

        if i + batch_size < total:
            print(f"  {min(i + batch_size, total)}/{total}...", end=" ", flush=True)

    return elevations


def find_point_distance(track, point):
    """找到观察点在轨迹上的累计距离"""
    def haversine(lon1, lat1, lon2, lat2):
        R = 6371000
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    best_dist = 0
    best_i = 0
    best_d = float("inf")
    cum = 0

    for i in range(len(track) - 1):
        d = haversine(track[i][0], track[i][1], point[0], point[1])
        if d < best_d:
            best_d = d
            best_dist = cum + d
            best_i = i
        cum += haversine(track[i][0], track[i][1], track[i + 1][0], track[i + 1][1])

    return best_dist


def plot_profile(route_name, elevations, points, track, total_dist_m, out_path):
    """画地形剖面图"""
    # 过滤无效高程
    valid = [(d, e) for _, _, d, e in elevations if e is not None]
    if not valid:
        print("  没有有效高程数据")
        return

    dists = [v[0] / 1000 for v in valid]  # 转 km
    elevs = [v[1] for v in valid]

    fig, ax = plt.subplots(figsize=(14, 5))

    # 地形填充
    ax.fill_between(dists, elevs, min(elevs) - 10, alpha=0.3, color="#4a90d9")
    ax.plot(dists, elevs, color="#2c5f8a", linewidth=1.5)

    # 标观察点
    y_min, y_max = min(elevs), max(elevs)
    y_range = y_max - y_min
    y_pad = y_range * 0.06

    for i, pt in enumerate(points):
        pt_dist = find_point_distance(track, (pt["lon"], pt["lat"]))
        pt_km = pt_dist / 1000

        # 找最近采样点的高程
        nearest_elev = None
        best_d = float("inf")
        for _, _, d, e in elevations:
            if e is not None and abs(d - pt_dist) < best_d:
                best_d = abs(d - pt_dist)
                nearest_elev = e

        if nearest_elev and 0 <= pt_km <= max(dists):
            # 提取简短标签
            label = pt["name"].split(" ")[0] if pt["name"] else ""
            # 把 emoji 前缀去掉
            if label.startswith("⚠"):
                label = label[2:].strip()

            ax.axvline(x=pt_km, color="#e74c3c", linestyle="--", linewidth=0.8, alpha=0.7)
            offset = y_range * 0.04 * (1 if i % 2 == 0 else -1) + y_range * 0.04
            ax.annotate(
                label,
                (pt_km, nearest_elev),
                xytext=(0, 15 if i % 2 == 0 else -25),
                textcoords="offset points",
                fontsize=7,
                color="#c0392b",
                ha="center",
                rotation=45,
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8, edgecolor="#e74c3c"),
            )

    ax.set_xlabel("距离 (km)", fontsize=11)
    ax.set_ylabel("海拔 (m)", fontsize=11)
    ax.set_title(f"{route_name} 地形剖面", fontsize=13, fontweight="bold")

    # 底部标注观察点编号
    point_labels = []
    point_positions = []
    for pt in points:
        pt_dist = find_point_distance(track, (pt["lon"], pt["lat"]))
        pt_km = pt_dist / 1000
        if 0 <= pt_km <= max(dists):
            label = pt["name"].split(" ")[0]
            if label.startswith("⚠"):
                label = label[2:].strip()
            point_labels.append(label)
            point_positions.append(pt_km)

    # 纵轴反转（高程通常是左边低右边高…不反转，保持正常）
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, max(dists))
    ax.tick_params(labelsize=9)

    plt.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close()
    print(f"  剖面图已保存: {out_path}")


def save_csv(elevations, points, track, out_path):
    """导出 CSV 数据"""
    rows = ["lon,lat,cum_dist_m,elevation_m,point_label"]
    point_map = {}
    for pt in points:
        d = find_point_distance(track, (pt["lon"], pt["lat"]))
        point_map[d] = pt["name"].split(" ")[0]

    for lon, lat, dist, elev in elevations:
        label = ""
        for pd_, pn in point_map.items():
            if abs(dist - pd_) < 30:
                label = pn
                break
        rows.append(f"{lon},{lat},{dist:.1f},{elev if elev else ''},{label}")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(rows))
    print(f"  数据已导出: {out_path}")


def main():
    kml_dir = "d:/geointern-agent"
    out_dir = "d:/geointern-agent/output"

    import os
    os.makedirs(out_dir, exist_ok=True)

    files = [
        f"{kml_dir}/L02_八角寨-拴马庄桥.kml",
        f"{kml_dir}/L03_黄院东山梁.kml",
    ]

    for fpath in files:
        if not os.path.exists(fpath):
            print(f"文件不存在: {fpath}")
            continue

        print(f"\n{'='*60}")
        print(f"处理: {os.path.basename(fpath)}")

        route_name, track, points = parse_kml(fpath)
        print(f"  路线: {route_name}")
        print(f"  轨迹点数: {len(track)}, 观察点: {len(points)}")

        if len(track) < 2:
            print("  轨迹点不足，跳过")
            continue

        print("  等距采样...")
        samples, total_dist = interpolate_track(track, spacing_m=50)
        print(f"  总距离: {total_dist/1000:.2f} km, 采样点: {len(samples)}")

        print("  查询高程...")
        elevations = get_elevations(samples)
        valid_count = sum(1 for _, _, _, e in elevations if e is not None)
        print(f"\n  有效高程: {valid_count}/{len(elevations)}")

        # 出图
        safe_name = os.path.basename(fpath).replace(".kml", "")
        plot_profile(
            route_name,
            elevations,
            points,
            track,
            total_dist,
            f"{out_dir}/{safe_name}_profile.png",
        )
        save_csv(elevations, points, track, f"{out_dir}/{safe_name}_profile.csv")

    print(f"\n完成！图片和CSV在 {out_dir}/")


if __name__ == "__main__":
    main()
