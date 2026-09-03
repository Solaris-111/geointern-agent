"""L01 大砾岩山上坡段 信手剖面图 — 含地层."""
import csv, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from section_config import (SectionConfig, FormationConfig, ContactConfig,
                            FeatureConfig, RhythmLayer)
from section_engine import SectionEngine

# 加载轨迹 → CSV (section_engine 需要)
dists_m, elevs = [], []
with open("output/L01_踏勘_profile.csv", "r") as f:
    next(f)
    for row in csv.reader(f):
        d = float(row[2])
        if 1200 <= d <= 1920:
            dists_m.append(d)
            elevs.append(float(row[3]))

# 写入临时 CSV (section_engine 需要 km 单位)
with open("output/_L01_segment_profile.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["lon","lat","cum_dist_m","elevation_m","point_label"])
    for i, (d, e) in enumerate(zip(dists_m, elevs)):
        # dist in km = cum_dist_m / 1000
        w.writerow(["", "", f"{d/1000:.6f}", f"{e:.1f}", ""])

# 剖面走向: 从轨迹起终点计算
dlat = dists_m[-1] / 1000 * math.sin(math.radians(30))  # rough
bearing = 345  # NW-SE, roughly

# 接触点位置 (km) — 从地形特征和你的描述估算
# 轨�� 1.2km=1200m → 1.92km=1920m → 转为km: 1.200→1.920
# 大砾岩山顶 (本溪组) 在 260m 最高点, 约 1.914km
# 馒毛组/马家沟组 约在 1.2km 起点
# 马家沟组/本溪组 (平行不整合) 约在大砾岩山半坡

contacts = [
    ContactConfig(1.200, dd=10, da=21, label="D0101 馒毛组/马家沟组", is_observed=False),
    ContactConfig(1.400, dd=10, da=21, label="马家沟组(O1m)", is_observed=False),
    ContactConfig(1.600, dd=30, da=45, label="本溪组/马家沟组 P.U.", contact_type="unconformity", is_observed=True),
    ContactConfig(1.750, dd=30, da=45, label="太原组(C2t) 三个包包", is_observed=True),
    ContactConfig(1.830, dd=191, da=78, label="山西组(P1s)", is_observed=False),
    ContactConfig(1.920, dd=191, da=78, label="D0102 大砾岩山 本溪组", is_observed=True),
]

formations = [
    FormationConfig("E1+2m", "馒毛组",     1.200, lithology="千枚状板岩",
                   description="千枚状板岩 基底"),
    FormationConfig("O1m",   "马家沟组",   1.400, lithology="灰岩",
                   description="灰岩夹白云岩 164背斜核部", thickness_m=50),
    FormationConfig("C2b",   "本溪组",     1.600, lithology="页岩",
                   description="页岩 红柱石角岩 三好砾岩", thickness_m=30),
    FormationConfig("C2t",   "太原组",     1.750, lithology="粉砂岩",
                   description="粉砂岩 红柱石角岩 三个包包",
                   thickness_m=79, rhythm_cycle_m=10,
                   rhythm_layers=[
                       RhythmLayer("粉砂岩", 0.40, "....", "#E8D8B0"),
                       RhythmLayer("红柱石角岩", 0.30, "||", "#D0C0B0"),
                       RhythmLayer("板岩", 0.30, "---", "#C8C0A0"),
                   ]),
    FormationConfig("P1s",   "山西组",     1.830, lithology="砂岩",
                   description="岩屑杂砂岩 炭质板岩 含煤", thickness_m=49),
    FormationConfig("C2b",   "本溪组(顶)", 1.920, lithology="页岩",
                   description="大砾岩山顶 本溪组 260m"),
]

cfg = SectionConfig(
    title="L01 大砾岩山上坡段 信手剖面图 (2026-07-26)",
    bearing=bearing, h_scale=2000, v_scale=2000, depth_m=80,
    csv_path="output/_L01_segment_profile.csv",
    formations=formations,
    contacts=contacts,
    features=[
        FeatureConfig(1.600, 200, "平行不整合 (P.U.)", color="red"),
        FeatureConfig(1.750, 230, "三个包包", color="darkgreen"),
    ],
    figsize=(16, 6),
)

engine = SectionEngine(cfg)
engine.render("output/L01_信手剖面图.png")
print("Done: L01_信手剖面图.png")
