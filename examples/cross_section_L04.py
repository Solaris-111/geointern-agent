"""L04 太平山南坡 实测剖面预览图 (1:1000) — O₁m→P₁y 上古生界完整序列."""
import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parent.parent / "core"))

from section_config import (SectionConfig, FormationConfig, ContactConfig,
                            FeatureConfig)
from section_engine import SectionEngine

# 剖面方向 S→N (方位角 ~0°), 1:1000 实测比例
cfg = SectionConfig(
    title="太平山南坡实测地层剖面图\n下奥陶统马家沟组(O₁m)—下二叠统杨家屯组(P₁y)",
    bearing=0, h_scale=1000, v_scale=1000,
    depth_m=100,
    csv_path="output/L04_太平山南坡_profile.csv",
    formations=[
        # O₁m 马家沟组 — 顶部 (平行不整合面之下)
        FormationConfig("O₁m",  "马家沟组",   0.000, lithology="灰岩",
                       description="顶部: 岩溶角砾岩+角砾状灰岩\n构造剪切劈理化发育"),
        # C₂b 本溪组 — 底部热变质角岩→唐山灰岩→压力影板岩
        FormationConfig("C₂b",  "本溪组",     0.005, lithology="角岩",
                       thickness_m=62.5,
                       description='硬绿泥石角岩+红柱石角岩(底)\n→杂色板岩→唐山灰岩(纺锤蜓)\n→压力影板岩(黄铁矿+石英充填)'),
        # C₃t 太原组 — 三段
        FormationConfig("C₃t",  "太原组",     0.066, lithology="砂岩",
                       thickness_m=79,
                       description="底部: 变质岩屑杂砂岩(陡坎)\n中部: 炭质板岩(植物化石)\n顶部: 杂色板岩夹石英砂岩(含煤线)"),
        # P₁s 山西组 — 砂岩-板岩-砂岩-板岩 两个旋回
        FormationConfig("P₁s",  "山西组",     0.145, lithology="砂岩",
                       thickness_m=49,
                       description="岩屑砂岩(含燧石角砾)\n→炭质板岩夹煤层→变质砂岩\n→炭质板岩夹煤线 两个向上变细旋回"),
        # P₁y 杨家屯组 — 巨厚碎屑岩
        FormationConfig("P₁y",  "杨家屯组",   0.206, lithology="砾岩",
                       thickness_m=100,
                       description='"豆腐块砂岩"含砾岩屑砂岩\n斜层理发育→变质角砾岩\n→砂质板岩(劈理化)'),
    ],
    contacts=[
        ContactConfig(0.000, dd=25,  da=28, label="剖面起点\nO₁m顶部",
                     is_observed=False),
        ContactConfig(0.005, dd=0,   da=20, label="D0402 O₁m/C₂b",
                     contact_type="unconformity"),
        ContactConfig(0.066, dd=0,   da=20, label="D0403 C₂b/C₃t"),
        ContactConfig(0.145, dd=0,   da=20, label="D0404 C₃t/P₁s"),
        ContactConfig(0.206, dd=0,   da=20, label="D0405 P₁s/P₁y"),
        ContactConfig(0.405, dd=0,   da=20, label="剖面终点\nP₁y未测至顶",
                     is_observed=False),
    ],
    features=[
        FeatureConfig(0.005, 150, "平行不整合\n(缺失 O₃+S+D+C₁)\n~1.4亿年间断", color="red"),
        FeatureConfig(0.035, 145, "硬绿泥石角岩\n(热接触变质)", color="darkgreen"),
        FeatureConfig(0.052, 148, "唐山灰岩\n纺锤蜓 2m", color="darkgreen"),
        FeatureConfig(0.100, 165, "炭质板岩\n含植物化石", color="darkgreen"),
        FeatureConfig(0.170, 190, "炭质板岩夹煤层\n山西式铁矿", color="darkgreen"),
        FeatureConfig(0.240, 195, '"豆腐块砂岩"\n斜层理发育', color="darkgreen"),
    ],
)

engine = SectionEngine(cfg)
engine.render("output/L04_实测剖面图.png")
