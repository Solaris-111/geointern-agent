"""L03 KML → 地形剖面 (坐标修正后)"""

import xml.etree.ElementTree as ET
import math, csv, requests, os

KML_NS = "http://www.opengis.net/kml/2.2"

def parse_kml(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()
    ns = {"kml": KML_NS}
    track = []
    coords_elem = root.find(".//kml:LineString/kml:coordinates", ns)
    if coords_elem is not None and coords_elem.text:
        for line in coords_elem.text.strip().split():
            parts = line.split(",")
            if len(parts) >= 2:
                track.append((float(parts[0]), float(parts[1])))
    points = []
    for pm in root.findall(".//kml:Placemark", ns):
        pm_name = pm.find("kml:name", ns)
        pm_point = pm.find(".//kml:Point/kml:coordinates", ns)
        if pm_name is not None and pm_point is not None and pm_point.text:
            label = pm_name.text
            parts = pm_point.text.strip().split(",")
            lat, lon = float(parts[1]), float(parts[0])
            if "行进路线" not in label:
                points.append({"name": label, "lon": lon, "lat": lat})
    return track, points

def interpolate_track(track, spacing_m=50):
    def haversine(lon1, lat1, lon2, lat2):
        R = 6371000
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    segments = []
    total = 0
    for i in range(len(track)-1):
        d = haversine(track[i][0], track[i][1], track[i+1][0], track[i+1][1])
        segments.append((track[i], track[i+1], d))
        total += d
    samples = [(track[0][0], track[0][1], 0.0)]
    cumulative, target = 0, spacing_m
    for p1, p2, seg_len in segments:
        while target < cumulative + seg_len and target <= total:
            frac = (target - cumulative) / seg_len
            samples.append((p1[0]+frac*(p2[0]-p1[0]), p1[1]+frac*(p2[1]-p1[1]), target))
            target += spacing_m
        cumulative += seg_len
    samples.append((track[-1][0], track[-1][1], total))
    return samples, total

def get_elevations(samples, batch_size=100):
    elevations = []
    for i in range(0, len(samples), batch_size):
        batch = samples[i:i+batch_size]
        locations = "|".join(f"{lat},{lon}" for lon, lat, _ in batch)
        try:
            resp = requests.get("https://api.opentopodata.org/v1/srtm30m",
                              params={"locations": locations}, timeout=60)
            if resp.status_code == 200:
                results = resp.json().get("results", [])
                for j, r in enumerate(results):
                    idx = i + j
                    lon, lat, dist = samples[idx]
                    elevations.append((lon, lat, dist, r["elevation"]))
            else:
                for j in range(len(batch)):
                    idx = i + j
                    elevations.append((*samples[idx][:2], samples[idx][2], None))
        except Exception:
            for j in range(len(batch)):
                idx = i + j
                elevations.append((*samples[idx][:2], samples[idx][2], None))
        if i + batch_size < len(samples):
            print(f"  {min(i+batch_size, len(samples))}/{len(samples)}...", end=" ", flush=True)
    return elevations

# Main
track, pts = parse_kml("L03_黄院东山梁.kml")
print(f"轨迹点: {len(track)}, 观察点: {len(pts)}")
print(f"D0301 新坐标: {track[0][1]:.6f}°N, {track[0][0]:.6f}°E")

samples, total_dist = interpolate_track(track, spacing_m=50)
print(f"总距离: {total_dist/1000:.2f} km, 采样: {len(samples)}")

print("查询高程...", end=" ", flush=True)
elevations = get_elevations(samples)
valid = sum(1 for _, _, _, e in elevations if e is not None)
print(f"\n有效: {valid}/{len(elevations)}")

os.makedirs("output", exist_ok=True)
with open("output/L03_黄院东山梁_profile.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["lon", "lat", "cum_dist_m", "elevation_m", "point_label"])
    for lon, lat, dist, elev in elevations:
        w.writerow([lon, lat, f"{dist:.1f}", f"{elev}" if elev else "", ""])

print("CSV 已更新: output/L03_黄院东山梁_profile.csv")

# 统计
valid_elevs = [e for _, _, _, e in elevations if e is not None]
print(f"海拔: {min(valid_elevs):.0f} - {max(valid_elevs):.0f} m, 高差 {max(valid_elevs)-min(valid_elevs):.0f} m")
