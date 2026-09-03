# -*- coding: utf-8 -*-
"""
图2-1 最终版: 比例尺标定地形 (198px=40m) + 报告地层数据
"""
import sys, json
sys.path.insert(0, "d:/geointern-agent/references/rag")
from cad_plot import generate_cross_section, apparent_dip

# Load calibrated terrain
with open("d:/geointern-agent/output/terrain_final.json", "r") as f:
    terrain = [(float(p[0]), float(p[1])) for p in json.load(f)]

PROFILE_LENGTH = terrain[-1][0]
print(f"Profile: {PROFILE_LENGTH:.0f}m, {len(terrain)} points")

# Boundary positions from Qwen-VL (% of profile)
# Jxw/Jxh=15%, Jxh/Jxt1=30%, Jxt1/Jxt2=45%, Jxt2/Jxt3=60%, Jxt3/Qbx=75%, Qbx/Qbc=90%
boundary_pct = [0.15, 0.30, 0.45, 0.60, 0.75, 0.90]

SECTION_AZIMUTH = 60.0   # NE, perpendicular to NW-SE strike

formations = [
    {"code": "Jxw",  "x": 0,                              "dip": 16, "strike": 350, "litho": "limestone",    "name": "Wumishan Fm"},
    {"code": "Jxh",  "x": boundary_pct[0] * PROFILE_LENGTH, "dip": 20, "strike": 340, "litho": "slate",        "name": "Hongshuizhuang Fm"},
    {"code": "Jxt1", "x": boundary_pct[1] * PROFILE_LENGTH, "dip": 22, "strike": 328, "litho": "dolomite",      "name": "Tieling Fm Mb.1"},
    {"code": "Jxt2", "x": boundary_pct[2] * PROFILE_LENGTH, "dip": 20, "strike": 335, "litho": "limestone",    "name": "Tieling Fm Mb.2"},
    {"code": "Jxt3", "x": boundary_pct[3] * PROFILE_LENGTH, "dip": 20, "strike": 320, "litho": "slate",        "name": "Tieling Fm Mb.3"},
    {"code": "Qbx",  "x": boundary_pct[4] * PROFILE_LENGTH, "dip": 20, "strike": 327, "litho": "shale",        "name": "Xiamaling Fm"},
    {"code": "Qbc",  "x": boundary_pct[5] * PROFILE_LENGTH, "dip": 18, "strike": 340, "litho": "conglomerate", "name": "Changlongshan Fm"},
]

TITLE = "Fig.2-1 Bajiaozhai Yakou - Shuanmazhuang Qiao\nJxw (Wumishan Fm) - Qbc (Changlongshan Fm)"

out = generate_cross_section(
    terrain=terrain, formations=formations,
    output="d:/geointern-agent/output/fig2-1_v3.dxf",
    title=TITLE, azimuth=SECTION_AZIMUTH, depth=200, scale=1.0,
)

# Info
with open("d:/geointern-agent/output/final_info.txt", "w", encoding="utf-8") as f:
    f.write(f"DXF: {out}\n")
    f.write(f"Profile: {PROFILE_LENGTH:.0f}m\n")
    f.write(f"Elevation: {terrain[0][1]:.0f}-{max(p[1] for p in terrain):.0f}m\n")
    f.write(f"Scale: 4.95 px/m (from '20 40m' scale bar)\n")
    f.write(f"Azimuth: {SECTION_AZIMUTH} deg\n\n")
    f.write("Apparent dips:\n")
    for fm in formations:
        ad = apparent_dip(fm['dip'], fm['strike'], SECTION_AZIMUTH)
        f.write(f"  {fm['code']}: true {fm['dip']} -> apparent {ad:.1f}\n")
    f.write(f"\nFormations:\n")
    for fm in formations:
        f.write(f"  {fm['code']} at x={fm['x']:.0f}m, {fm['litho']}\n")

print("Done:", out)
