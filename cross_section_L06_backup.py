"""L06 八角寨-拴马桩桥 信手剖面图 — 薄配置，引擎驱动."""

from section_engine import SectionEngine, config_L06

engine = SectionEngine(config_L06())
engine.render("output/L06_信手剖面图.png")
