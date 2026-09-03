"""从照片 EXIF 提取 GPS 坐标，对照 KML 路线文件定位观察点。

用法:
    python photo_gps.py <照片路径> [KML文件路径]

输出: GPS 坐标(度分秒 + 十进制)、海拔、拍摄时间、最近观察点匹配。
"""

import sys
import json
import re
import xml.etree.ElementTree as ET
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from math import radians, sin, cos, sqrt, asin


def _float(v):
    """将 IFDRational 或其他数值转为 float"""
    return float(v)


def dms_to_decimal(dms_tuple, ref):
    """将度分秒元组转为十进制"""
    degrees = _float(dms_tuple[0])
    minutes = _float(dms_tuple[1])
    seconds = _float(dms_tuple[2])
    decimal = degrees + minutes / 60.0 + seconds / 3600.0
    if ref in ('S', 'W'):
        decimal = -decimal
    return decimal


def dms_to_string(dms_tuple, ref):
    """将度分秒元组转为度分秒字符串"""
    d = int(_float(dms_tuple[0]))
    m = int(_float(dms_tuple[1]))
    s = _float(dms_tuple[2])
    return f"{d}°{m}′{s:.2f}″{ref}"


def extract_gps(image_path):
    """从照片 EXIF 提取 GPS 信息和拍摄时间"""
    img = Image.open(image_path)
    exif = img._getexif()
    if not exif:
        return None

    gps_info = {}
    for tag_id, value in exif.items():
        tag = TAGS.get(tag_id, tag_id)
        if tag == 'GPSInfo':
            for gps_key, gps_val in value.items():
                gps_tag = GPSTAGS.get(gps_key, gps_key)
                gps_info[gps_tag] = gps_val

    datetime_str = exif.get(36867) or exif.get(36868) or exif.get(306, '')

    if not gps_info:
        return None

    lat_dms = gps_info.get('GPSLatitude')
    lat_ref = gps_info.get('GPSLatitudeRef', 'N')
    lon_dms = gps_info.get('GPSLongitude')
    lon_ref = gps_info.get('GPSLongitudeRef', 'E')
    altitude = gps_info.get('GPSAltitude', None)

    if not (lat_dms and lon_dms):
        return None

    return {
        'lat_dms': lat_dms,
        'lat_ref': lat_ref,
        'lon_dms': lon_dms,
        'lon_ref': lon_ref,
        'lat_decimal': dms_to_decimal(lat_dms, lat_ref),
        'lon_decimal': dms_to_decimal(lon_dms, lon_ref),
        'lat_string': dms_to_string(lat_dms, lat_ref),
        'lon_string': dms_to_string(lon_dms, lon_ref),
        'altitude': _float(altitude) if altitude else None,
        'datetime': str(datetime_str),
    }


def haversine(lat1, lon1, lat2, lon2):
    """计算两点间距离(m)"""
    R = 6371000
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return R * 2 * asin(sqrt(a))


def parse_kml_points(kml_path):
    """从 KML 提取 Placemark 坐标点"""
    tree = ET.parse(kml_path)
    root = tree.getroot()
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}

    points = []
    for pm in root.iter('{http://www.opengis.net/kml/2.2}Placemark'):
        name = pm.find('kml:name', ns)
        point = pm.find('kml:Point', ns)
        if name is not None and point is not None:
            coords = point.find('kml:coordinates', ns)
            if coords is not None and coords.text:
                parts = coords.text.strip().split(',')
                lon, lat = float(parts[0]), float(parts[1])
                points.append({'name': name.text, 'lat': lat, 'lon': lon})
    return points


def match_point(photo_gps, kml_path):
    """匹配照片到最近的 KML 观察点"""
    points = parse_kml_points(kml_path)
    if not points:
        return []

    results = []
    for p in points:
        dist = haversine(photo_gps['lat_decimal'], photo_gps['lon_decimal'], p['lat'], p['lon'])
        results.append({'name': p['name'], 'lat': p['lat'], 'lon': p['lon'], 'distance_m': dist})
    results.sort(key=lambda x: x['distance_m'])
    return results


def format_output(photo_gps, matches):
    """格式化输出"""
    lines = []
    lines.append(f"GPS: {photo_gps['lat_string']}, {photo_gps['lon_string']}")
    lines.append(f"十进制: {photo_gps['lat_decimal']:.6f}, {photo_gps['lon_decimal']:.6f}")
    if photo_gps['altitude']:
        lines.append(f"海拔: {photo_gps['altitude']:.0f}m")
    lines.append(f"拍摄时间: {photo_gps['datetime']}")
    lines.append("")
    if matches:
        lines.append("最近观察点:")
        for i, m in enumerate(matches[:5]):
            arrow = " ←" if i == 0 else ""
            lines.append(f"  {m['name']} 距离{m['distance_m']:.0f}m{arrow}")
    return "\n".join(lines)


if __name__ == '__main__':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    if len(sys.argv) < 2:
        print("用法: python photo_gps.py <照片路径> [KML文件路径]")
        sys.exit(1)

    image_path = sys.argv[1]
    kml_path = sys.argv[2] if len(sys.argv) > 2 else None

    photo_gps = extract_gps(image_path)
    if not photo_gps:
        print("未找到 GPS 信息。照片可能没有地理标记。")
        sys.exit(1)

    matches = match_point(photo_gps, kml_path) if kml_path else []

    print(format_output(photo_gps, matches))

    # 输出 JSON 供程序读取
    output = {'photo_gps': photo_gps, 'matches': matches[:5]}
    print("\n--- JSON ---")
    print(json.dumps(output, ensure_ascii=False, indent=2, default=str))
