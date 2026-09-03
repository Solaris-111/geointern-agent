"""L04 地形剖面生成 — 从KML坐标查询SRTM高程，生成密集地形CSV."""
import xml.etree.ElementTree as ET
import math, csv, sys, time
import urllib.request, json

KML_PATH = "L04_太平山南坡.kml"
OUT_PATH = "output/L04_太平山南坡_profile.csv"

# ── KML 提取 ──────────────────────────────────────────────────────────
ns = {'kml': 'http://www.opengis.net/kml/2.2'}
tree = ET.parse(KML_PATH)
root = tree.getroot()

# 收集所有 Placemark 坐标 (含轨迹 + 观察点)
coords = []
placemarks = root.findall('.//kml:Placemark', ns)
for pm in placemarks:
    name_el = pm.find('kml:name', ns)
    name = name_el.text if name_el is not None else ''
    # LineString
    ls = pm.find('.//kml:LineString/kml:coordinates', ns)
    if ls is not None and ls.text:
        for line in ls.text.strip().split():
            parts = line.strip().split(',')
            if len(parts) >= 2:
                coords.append((float(parts[0]), float(parts[1]), name))
    # Point
    pt = pm.find('.//kml:Point/kml:coordinates', ns)
    if pt is not None and pt.text:
        parts = pt.text.strip().split(',')
        if len(parts) >= 2:
            label = name.split('|')[0].strip() if '|' in name else name
            coords.append((float(parts[0]), float(parts[1]), label))

print(f"提取到 {len(coords)} 个点")

# ── 沿剖面插值 ──────────────────────────────────────────────────────────
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def bearing(lat1, lon1, lat2, lon2):
    """方位角 (度)."""
    dlon = math.radians(lon2 - lon1)
    lat1r = math.radians(lat1)
    lat2r = math.radians(lat2)
    x = math.sin(dlon) * math.cos(lat2r)
    y = math.cos(lat1r)*math.sin(lat2r) - math.sin(lat1r)*math.cos(lat2r)*math.cos(dlon)
    return (math.degrees(math.atan2(x, y)) + 360) % 360

# 对轨迹点按 lat 排序 (S→N 剖面，lat从小到大)
track_pts = [(lon, lat, name) for lon, lat, name in coords
             if not name.startswith('D04')]
d_pts = [(lon, lat, name) for lon, lat, name in coords
         if name.startswith('D04')]

# 把 D 点也加入，整体按 lat 排
all_pts = coords.copy()
all_pts.sort(key=lambda x: x[1])  # 按纬度从南到北

# 沿路径插值
STEP_M = 15  # 每15m一个采样点
interp = []
cum = 0.0
prev_lat, prev_lon = all_pts[0][1], all_pts[0][0]
interp.append((all_pts[0][0], all_pts[0][1], 0.0, all_pts[0][2]))

for i in range(1, len(all_pts)):
    lon, lat, name = all_pts[i]
    dist = haversine(prev_lat, prev_lon, lat, lon)
    n_steps = max(1, int(dist / STEP_M))
    for s in range(1, n_steps + 1):
        frac = s / n_steps
        ilat = prev_lat + (lat - prev_lat) * frac
        ilon = prev_lon + (lon - prev_lon) * frac
        cum += dist / n_steps
        label = name if s == n_steps else ''
        interp.append((ilon, ilat, cum, label))
    prev_lat, prev_lon = lat, lon

print(f"插值后 {len(interp)} 个采样点, 总长 {cum:.0f}m")

# ── SRTM 高程查询 (Open-Elevation API) ─────────────────────────────────
def query_elevations_opentopo(points, batch_size=100):
    """OpenTopography API 查询 SRTM 高程 (免费, 无需key)."""
    elevations = {}
    for batch_start in range(0, len(points), batch_size):
        batch = points[batch_start:batch_start + batch_size]
        loc_str = '|'.join(f'{lat},{lon}' for lon, lat, *_ in batch)
        url = f'https://api.opentopodata.org/v1/srtm30m?locations={loc_str}'
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'GeoIntern/1.0'})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
            for j, r in enumerate(data.get('results', [])):
                idx = batch_start + j
                elevations[idx] = r['elevation']
            print(f"  batch {batch_start//batch_size + 1}: {len(batch)} 点 OK")
        except Exception as e:
            print(f"  batch {batch_start//batch_size + 1} FAILED: {e}")
        time.sleep(0.5)
    return elevations

def query_elevations(points, batch_size=100):
    """Try multiple SRTM APIs in order."""
    # Try OpenTopoData first
    print("  Trying opentopodata.org...")
    elevs = query_elevations_opentopo(points, batch_size)
    if elevs:
        return elevs
    # Fallback
    print("  All APIs failed, using known elevations + interpolation")
    return {}

print("查询 SRTM 高程...")
elev_dict = query_elevations(interp)

# ── Fallback: 已知野外高程 ──────────────────────────────────────────────
KNOWN_ELEV = {
    'D0401': 163,   # 162.9高地
    'D0402': 150,   # 鞍部探槽
    'D0403': 170,   # 南洛凹南山梁
    'D0404': 192,   # 190-195m
    'D0405': 218,   # 215-220m
}

# ── 写入 CSV ──────────────────────────────────────────────────────────
with open(OUT_PATH, 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f)
    w.writerow(['lon', 'lat', 'cum_dist_m', 'elevation_m', 'point_label'])
    last_elev = 150  # default starting elevation
    for i, (lon, lat, cum_dist, label) in enumerate(interp):
        if label in KNOWN_ELEV:
            last_elev = KNOWN_ELEV[label]
            elev = last_elev
        elif elev_dict and i in elev_dict and elev_dict[i] > 0:
            elev = elev_dict[i]
            last_elev = elev
        else:
            elev = last_elev
        w.writerow([f'{lon:.6f}', f'{lat:.6f}', f'{cum_dist:.1f}', f'{elev:.0f}', label])

print(f"Done → {OUT_PATH}")
if elev_dict:
    print(f"Elevation range: {min(elev_dict.values()):.0f} - {max(elev_dict.values()):.0f}m")
else:
    print("Using estimated elevations (known field points)")
