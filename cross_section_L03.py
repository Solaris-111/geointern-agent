"""L03 黄院东山梁 信手剖面图 — 裁剪版，从D0302景儿峪组开始."""
from section_config import (SectionConfig, FormationConfig, ContactConfig,
                            FeatureConfig, RhythmLayer)
from section_engine import SectionEngine

# Terrain CSV already shifted: origin = D0302 (原0.694km → 现0.000km)
cfg = SectionConfig(
    title="黄院东山梁景儿峪组(QxJ)—亮甲山组(O1l)信手剖面图",
    bearing=89, h_scale=5000, v_scale=1000, depth_m=120,
    csv_path="output/L03_黄院东山梁_profile.csv",
    formations=[
        FormationConfig("QxJ",   "景儿峪组",   0.000, lithology="大理岩",
                       description="大理岩+钙质板岩"),
        FormationConfig("E1f",   "府君山组",   0.120, lithology="豹皮灰岩",
                       description="豹皮灰岩+纹带灰岩 大型平卧褶皱"),
        FormationConfig("E1+2m", "馒头毛庄组", 0.224, lithology="千枚状板岩",
                       description="千枚状板岩 大理岩透镜体"),
        FormationConfig("E2x",   "徐庄组",     0.255, lithology="鲕粒灰岩",
                       description="灰岩+板岩夹鲕粒灰岩 孔雀石薄膜"),
        FormationConfig("E2z",   "张夏组",     0.317, lithology="鲕粒灰岩",
                       thickness_m=36, rhythm_cycle_m=3.6,
                       rhythm_layers=[
                           RhythmLayer("鲕粒灰岩", 0.35, "||", "#A8D0DB"),
                           RhythmLayer("泥晶灰岩", 0.25, "//", "#C8D8C8"),
                           RhythmLayer("钙质板岩", 0.40, "---", "#D8C8A8"),
                       ]),
        FormationConfig("E2h",   "黄院组",     0.629, lithology="泥质条带灰岩",
                       description="灰黄色薄层泥质条带灰岩 条带宽1-2cm"),
        FormationConfig("O1y",   "冶里组",     0.691, lithology="泥质纹带灰岩",
                       description="底部泥质纹带灰岩 灰色中厚层灰岩"),
        FormationConfig("O1l",   "亮甲山组",   0.787, lithology="白云岩",
                       description="灰白色中厚层白云岩 刀砍纹发育"),
    ],
    contacts=[
        ContactConfig(0.000, dd=50, da=20, label="D0302 QbC/QxJ"),
        ContactConfig(0.120, dd=50, da=20, label="D0303 P.U.",
                     contact_type="unconformity"),
        ContactConfig(0.224, dd=50, da=20, label="D0304"),
        ContactConfig(0.255, dd=50, da=20, label="D0305"),
        ContactConfig(0.317, dd=50, da=20, label="D0306"),
        ContactConfig(0.629, dd=50, da=20, label="D0307"),
        ContactConfig(0.691, dd=50, da=20, label="D0308"),
        ContactConfig(0.787, dd=50, da=20, label="D0309 O1l未测至顶"),
    ],
    features=[
        FeatureConfig(0.120, 185, "平行不整合 (P.U.)", color="red"),
    ],
)

engine = SectionEngine(cfg)
engine.render("output/L03_信手剖面图.png")
