#!/usr/bin/env python3
"""KML → GeoJSON 转换脚本。

把奥维/Google Earth 导出的路线 KML 转成 MapLibre 能直接加载的 GeoJSON。
输出两个文件：
  routes.geojson  — 所有轨迹线（LineString）
  points.geojson  — 所有观察点（Point）

用法：
  python kml_to_geojson.py L03_黄院东山梁.kml [更多.kml ...]
默认输出到 webmap/data/，输出文件会被前端直接引用。
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

KML_NS = "http://www.opengis.net/kml/2.2"
OUT_DIR = Path(__file__).resolve().parent / "webmap" / "data"

POINT_ID_RE = re.compile(r"^(D\d+)")


def find_text(el, name):
    child = el.find(f"{{{KML_NS}}}{name}")
    return child.text.strip() if child is not None and child.text else ""


def parse_coordinates(text):
    coords = []
    for tok in text.strip().split():
        parts = tok.split(",")
        if len(parts) < 2:
            continue
        lon, lat = float(parts[0]), float(parts[1])
        ele = float(parts[2]) if len(parts) > 2 else 0.0
        coords.append([lon, lat, ele])
    return coords


def parse_kml(path):
    root = ET.parse(path).getroot()
    doc = root.find(f"{{{KML_NS}}}Document")
    if doc is None:
        doc = root

    route_name = find_text(doc, "name") or path.stem

    routes, points = [], []
    for pm in doc.iter(f"{{{KML_NS}}}Placemark"):
        name = find_text(pm, "name")
        style = find_text(pm, "styleUrl").lstrip("#").lower()

        line = pm.find(f".//{{{KML_NS}}}LineString/{{{KML_NS}}}coordinates")
        point = pm.find(f".//{{{KML_NS}}}Point/{{{KML_NS}}}coordinates")

        if line is not None:
            coords = parse_coordinates(line.text or "")
            if len(coords) >= 2:
                routes.append({
                    "type": "Feature",
                    "geometry": {"type": "LineString", "coordinates": coords},
                    "properties": {"name": name, "route": route_name},
                })
        elif point is not None:
            coords = parse_coordinates(point.text or "")
            if coords:
                lon, lat, ele = coords[0]
                m = POINT_ID_RE.match(name or "")
                point_id = m.group(1) if m else name
                desc = (name or "").replace(point_id, "", 1).strip()
                points.append({
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [lon, lat, ele]},
                    "properties": {
                        "name": name,
                        "point_id": point_id,
                        "description": desc,
                        "key": "key" in style,
                        "route": route_name,
                        "lng": lon,
                        "lat": lat,
                        "ele": ele,
                    },
                })
    return route_name, routes, points


def main():
    files = [Path(p) for p in sys.argv[1:]]
    if not files:
        print("用法: python kml_to_geojson.py <kml文件> [更多kml...]")
        sys.exit(1)

    all_routes, all_points = [], []
    for f in files:
        name, routes, points = parse_kml(f)
        all_routes.extend(routes)
        all_points.extend(points)
        print(f"  {f.name}: {len(routes)} 条轨迹, {len(points)} 个观察点")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    routes_fc = {"type": "FeatureCollection", "features": all_routes}
    points_fc = {"type": "FeatureCollection", "features": all_points}
    (OUT_DIR / "routes.geojson").write_text(
        json.dumps(routes_fc, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "points.geojson").write_text(
        json.dumps(points_fc, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"输出: {OUT_DIR / 'routes.geojson'}  ({len(all_routes)} 条轨迹)")
    print(f"输出: {OUT_DIR / 'points.geojson'}  ({len(all_points)} 个观察点)")


if __name__ == "__main__":
    main()
