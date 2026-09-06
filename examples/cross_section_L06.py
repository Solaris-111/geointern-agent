"""L06 八角寨-拴马桩桥 信手剖面图 — 薄配置，引擎驱动."""

import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parent.parent / "core"))

from section_engine import SectionEngine, config_L06

engine = SectionEngine(config_L06())
engine.render("output/L06_信手剖面图.png")
