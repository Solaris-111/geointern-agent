"""从奥维 ovkml 提取轨迹 → 地形剖面 CSV."""
import xml.etree.ElementTree as ET
import math, csv, sys

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

ns = {
    'kml': 'http://www.opengis.net/kml/2.2',
    'gx': 'http://www.google.com/kml/ext/2.2'
}

path = sys.argv[1] if len(sys.argv) > 1 else r"F:\奥维地图\2026-07-26 大砾岩山.ovkml"
tree = ET.parse(path)
root = tree.getroot()

# Find gx:Track coordinates
tracks = root.findall('.//gx:Track', ns)
if not tracks:
    print("No gx:Track found")
    sys.exit(1)

track = tracks[0]
coords = track.findall('gx:coord', ns)
whens = track.findall('kml:when', ns) if track.findall('kml:when', ns) else track.findall('when')

print(f"Track points: {len(coords)}")

# Extract coordinates: lon,lat,elev
points = []
for i, c in enumerate(coords):
    parts = c.text.strip().split()
    lon, lat, elev = float(parts[0]), float(parts[1]), float(parts[2])
    time_str = whens[i].text if i < len(whens) else ''
    points.append((lon, lat, elev, time_str))

# Compute cumulative distance
rows = [['lon', 'lat', 'cum_dist_m', 'elevation_m', 'time']]
cum_dist = 0
prev_lat, prev_lon = points[0][1], points[0][0]
for i, (lon, lat, elev, t) in enumerate(points):
    if i == 0:
        dist = 0
    else:
        dist = haversine(prev_lat, prev_lon, lat, lon)
        cum_dist += dist
    rows.append([str(lon), str(lat), f"{cum_dist:.1f}", str(elev), t])
    prev_lat, prev_lon = lat, lon

out_path = path.replace('.ovkml', '_profile.csv')
with open(out_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(rows)

print(f"Total distance: {cum_dist:.0f}m")
print(f"Elevation range: {min(p[2] for p in points):.0f}m - {max(p[2] for p in points):.0f}m")
print(f"Saved: {out_path}")
print(f"Data rows: {len(rows)-1}")
