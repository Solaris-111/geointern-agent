# -*- coding: utf-8 -*-
"""
图2-1 V2: 用图像提取的地形 + Qwen-VL边界位置 重建
"""
import sys, json
sys.path.insert(0, "d:/geointern-agent/references/rag")
from cad_plot import generate_cross_section

# Load extracted terrain
with open("d:/geointern-agent/output/terrain_meters.json", "r") as f:
    terrain = json.load(f)
# Convert back to tuple format
terrain = [(float(p[0]), float(p[1])) for p in terrain]

PROFILE_LENGTH = terrain[-1][0]  # ~800m

# Boundary positions from Qwen-VL (% of total length)
# Jxw/Jxh=15%, Jxh/Jxt1=30%, Jxt1/Jxt2=45%, Jxt2/Jxt3=60%, Jxt3/Qbx=75%, Qbx/Qbc=90%
boundary_pct = {
    "Jxw-Jxh": 0.15,
    "Jxh-Jxt1": 0.30,
    "Jxt1-Jxt2": 0.45,
    "Jxt2-Jxt3": 0.60,
    "Jxt3-Qbx": 0.75,
    "Qbx-Qbc": 0.90,
}

SECTION_AZIMUTH = 60.0
AVG_STRIKE = 330.0

formations = [
    {
        "code": "Jxw",
        "x": 0,
        "dip": 16, "strike": AVG_STRIKE,
        "litho": "limestone",
        "name": "Wumishan Fm"
    },
    {
        "code": "Jxh",
        "x": boundary_pct["Jxw-Jxh"] * PROFILE_LENGTH,
        "dip": 20, "strike": AVG_STRIKE,
        "litho": "slate",
        "name": "Hongshuizhuang Fm"
    },
    {
        "code": "Jxt1",
        "x": boundary_pct["Jxh-Jxt1"] * PROFILE_LENGTH,
        "dip": 22, "strike": AVG_STRIKE,
        "litho": "dolomite",
        "name": "Tieling Fm Mb.1"
    },
    {
        "code": "Jxt2",
        "x": boundary_pct["Jxt1-Jxt2"] * PROFILE_LENGTH,
        "dip": 20, "strike": AVG_STRIKE,
        "litho": "limestone",
        "name": "Tieling Fm Mb.2"
    },
    {
        "code": "Jxt3",
        "x": boundary_pct["Jxt2-Jxt3"] * PROFILE_LENGTH,
        "dip": 20, "strike": AVG_STRIKE,
        "litho": "slate",
        "name": "Tieling Fm Mb.3"
    },
    {
        "code": "Qbx",
        "x": boundary_pct["Jxt3-Qbx"] * PROFILE_LENGTH,
        "dip": 20, "strike": AVG_STRIKE,
        "litho": "shale",
        "name": "Xiamaling Fm"
    },
    {
        "code": "Qbc",
        "x": boundary_pct["Qbx-Qbc"] * PROFILE_LENGTH,
        "dip": 18, "strike": AVG_STRIKE,
        "litho": "conglomerate",
        "name": "Changlongshan Fm"
    },
]

TITLE = "Fig.2-1 Bajiaozhai Yakou - Shuanmazhuang Qiao\nJxw (Wumishan Fm) - Qbc (Changlongshan Fm) Cross-section"

# Generate
out_path = generate_cross_section(
    terrain=terrain,
    formations=formations,
    output="d:/geointern-agent/output/fig2-1_section_v2.dxf",
    title=TITLE,
    azimuth=SECTION_AZIMUTH,
    depth=300,
    scale=1.0,
)

# Save result
with open("d:/geointern-agent/output/result_v2.txt", "w", encoding="utf-8") as f:
    f.write("DXF saved: %s\n" % out_path)
    f.write("Terrain: %d points, %.0f-%.0f m\n" % (
        len(terrain), terrain[0][0], terrain[-1][0]))
    f.write("Formations:\n")
    for fm in formations:
        f.write("  %s at x=%.0fm, dip=%d deg, litho=%s\n" % (
            fm["code"], fm["x"], fm["dip"], fm["litho"]))

print("Done! DXF: %s" % out_path)
