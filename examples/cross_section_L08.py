"""L08 太平山向斜中段北翼 信手构造地层剖面图."""
import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parent.parent / "core"))

from section_config import (SectionConfig, FormationConfig, ContactConfig,
                            FeatureConfig)
from section_engine import SectionEngine

cfg = SectionConfig(
    title="太平山向斜中段北翼信手构造地层剖面图\n大砾岩山—太平山梁 (1:2000)",
    bearing=185, h_scale=2000, v_scale=1000, depth_m=80,
    csv_path="output/L08_太平山向斜中段北翼_profile.csv",
    formations=[
        FormationConfig("O2m", "马家沟组", 0.000, lithology="灰岩",
                       description="灰岩、糜棱岩化角砾状灰岩、大理岩\n钙质千枚岩 未测至底"),
        FormationConfig("C2b", "本溪组", 0.035, lithology="砾岩",
                       thickness_m=10.6,
                       description='底部"三好"砾岩->硬绿泥石角岩\n->粉砂质板岩 向上变细旋回'),
        FormationConfig("C3t", "太原组", 0.066, lithology="砂岩",
                       thickness_m=47.2,
                       description="变质岩屑砂岩 页岩夹红柱石角岩\n层内3向斜3背斜 岩层重复出现"),
        FormationConfig("P1s", "山西组", 0.251, lithology="砂岩",
                       thickness_m=61.8,
                       description="变质砂岩+碳质板岩\n两个向上变细旋回 含植物化石"),
    ],
    contacts=[
        ContactConfig(0.000, dd=175, da=20, label="剖面起点",
                     is_observed=False),
        ContactConfig(0.035, dd=180, da=20, label="D0801 O2m/C2b",
                     contact_type="unconformity"),
        ContactConfig(0.066, dd=175, da=15, label="D0802 C2b/C3t",
                     contact_type="fault"),
        ContactConfig(0.251, dd=190, da=30, label="D0803 C3t/P1s",
                     contact_type="fault"),
        ContactConfig(0.375, dd=185, da=25, label="D0804 P1s/P1y"),
    ],
    features=[
        # D0801 平行不整合
        FeatureConfig(0.035, 151, "P.U.\n(O2m/C2b)", color="red"),
        # O2m 内部: 闪长玢岩脉
        FeatureConfig(0.015, 133, "闪长玢岩脉\n(近东西向)", color="darkgreen"),
        # C2b 底部: 三姑砾岩标志层
        FeatureConfig(0.038, 139, "三姑砾岩\n(底砾岩标志层)", color="darkgreen"),
        # 大砾岩山顶
        FeatureConfig(0.050, 138, "大砾岩山顶\n(~194m)", color="grey"),
        # C3t 内部: 层内褶皱带
        FeatureConfig(0.150, 130, "C3t层内褶皱带\n3向斜3背斜相间\n砂岩多次重复", color="darkgreen"),
        # 201.2高地
        FeatureConfig(0.151, 127, "201.2高地", color="grey"),
        # C3t/P1s 附近: 花岗斑杂岩 + 横断层
        FeatureConfig(0.251, 147, "花岗斑杂岩脉\n+横断层", color="darkgreen"),
        # P1s 内部: 植物化石
        FeatureConfig(0.310, 160, "植物化石\n(碳质板岩中)", color="darkgreen"),
        # 260.9高地
        FeatureConfig(0.370, 180, "260.9高地", color="grey"),
        # D0804 不对称褶皱 + 豆腐块砾岩
        FeatureConfig(0.375, 190, "不对称褶皱\n+豆腐块砾岩陡坎", color="darkgreen"),
    ],
)

engine = SectionEngine(cfg)
engine.render("output/L08_信手剖面图.png")
