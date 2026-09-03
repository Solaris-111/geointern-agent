# -*- coding: utf-8 -*-
"""
图2-1 八角寨垭口—拴马庄桥 地层剖面图 DXF生成
基于 Qwen-VL 识别的图像信息重建
"""
import sys, math
sys.path.insert(0, "d:/geointern-agent/references/rag")
from cad_plot import generate_cross_section, LITHO_HATCH, apparent_dip

# ═══════════════════════════════════════════════════════════
# 数据（从图2-1 Qwen-VL识别提取 + 报告文本）
# ═══════════════════════════════════════════════════════════

# 剖面方位角：倾向NE(50-80°)，走向NW-SE，剖面大致垂直走向→NE-SW向
SECTION_AZIMUTH = 60.0

# 地层平均走向 ≈ 倾向-90° ≈ 330°
AVG_STRIKE = 330.0

# 地形剖面 [x(m), elevation(m)]
# 八角寨垭口(左) → 拴马庄桥(右)，约800m
# 构造两个山脊+一个谷地，展示单斜地层的地形效应
terrain = [
    (0, 260),     # 起点：八角寨垭口
    (60, 275),
    (120, 295),   # 第一个山脊
    (180, 285),
    (240, 265),   # 谷地（在这里地层看起来"下凹"→伪向斜）
    (300, 255),
    (360, 270),
    (420, 290),   # 第二个山脊
    (480, 300),
    (540, 285),
    (600, 265),
    (660, 250),   # 右侧谷地
    (720, 245),
    (780, 250),   # 终点：拴马庄桥
]

# 地层界线及参数
# x: 地形线上出露位置, code: 地层代号, dip: 真倾角, litho: 岩性key
formations = [
    {
        "code": "Jxw",
        "x": 20,
        "dip": 16,
        "strike": AVG_STRIKE,
        "litho": "dolomite",
        "name": "雾迷山组"
    },
    {
        "code": "Jxh",
        "x": 130,
        "dip": 20,
        "strike": AVG_STRIKE,
        "litho": "slate",
        "name": "洪水庄组"
    },
    {
        "code": "Jxt¹",
        "x": 220,
        "dip": 22,
        "strike": AVG_STRIKE,
        "litho": "dolomite",
        "name": "铁岭组一段"
    },
    {
        "code": "Jxt²",
        "x": 310,
        "dip": 20,
        "strike": AVG_STRIKE,
        "litho": "limestone",
        "name": "铁岭组二段"
    },
    {
        "code": "Jxt³",
        "x": 400,
        "dip": 20,
        "strike": AVG_STRIKE,
        "litho": "slate",
        "name": "铁岭组三段"
    },
    {
        "code": "Qbx",
        "x": 510,
        "dip": 20,
        "strike": AVG_STRIKE,
        "litho": "shale",
        "name": "下马岭组"
    },
    {
        "code": "Qbc",
        "x": 650,
        "dip": 18,
        "strike": AVG_STRIKE,
        "litho": "conglomerate",
        "name": "长龙山组"
    },
]

TITLE = "图2-1 八角寨垭口—拴马庄桥 雾迷山组(Jxw)—长龙山组(Qbc)地层剖面图"

# ── 生成 ───────────────────────────────────────────────────
if __name__ == "__main__":
    out = "d:/geointern-agent/output/fig2-1_section.dxf"

    out_path = generate_cross_section(
        terrain=terrain,
        formations=formations,
        output=out,
        title=TITLE,
        azimuth=SECTION_AZIMUTH,
        depth=300,
        scale=1.0,
    )
    # Write result to file to avoid encoding issues
    with open("d:/geointern-agent/output/result.txt", "w", encoding="utf-8") as f:
        f.write("DXF saved: %s\n" % out_path)
        f.write("Open with AutoCAD / LibreCAD / QGIS\n")
    print("Done! See output/result.txt")
