"""规范岩性花纹映射表 — 合并自 section_engine.py FGDC_PATTERNS + geo_plotting.py
LITHOLOGY + cross_section_L03/L06 独立映射，以指导书附件一「常见岩石花纹图例」为准。

每个条目:
  hatch:   matplotlib hatch 字符串
  fill:    填充颜色 (B&W 剖面用 white, 彩色图用对应色)
  aliases: 别名列表 (中文简称/英文名)
  category: 岩性大类 (carbonate/clastic/metamorphic/igneous/unconsolidated)
  hatch_lw: 推荐 hatch 线宽 (matplotlib rcParams 值)

用法:
  from lithology_patterns import get_pattern
  pat = get_pattern("灰岩")  # -> {"hatch": "////", "fill": "#ffffff", ...}
  pat = get_pattern("limestone")  # 别名查找也能命中
"""

# ── 岩性大类排序 (图例用) ──────────────────────────────────────────
CATEGORY_ORDER = ["carbonate", "clastic", "metamorphic", "igneous", "unconsolidated"]

CATEGORY_NAMES = {
    "carbonate":      "碳酸盐岩",
    "clastic":        "碎屑岩",
    "metamorphic":    "变质岩",
    "igneous":        "岩浆岩",
    "unconsolidated": "松散堆积物",
}

# ── 规范花纹表 ─────────────────────────────────────────────────────
# 格式: 规范中文名 -> {hatch, fill, aliases, category, hatch_lw}
# 排列顺序同指导书附件一「常见岩石花纹图例」

LITHOLOGY_PATTERNS = {
    # ===== 碳酸盐岩 =====
    "灰岩": {
        "hatch": "////", "fill": "#ffffff", "category": "carbonate",
        "hatch_lw": 0.25,
        "aliases": ["石灰岩", "limestone", "灰岩(砖块纹)", "碳酸盐岩"],
    },
    "泥质灰岩": {
        "hatch": "//..", "fill": "#ffffff", "category": "carbonate",
        "hatch_lw": 0.25,
        "aliases": ["泥质石灰岩", "marly limestone"],
    },
    "硅质灰岩": {
        "hatch": "\\\\", "fill": "#ffffff", "category": "carbonate",
        "hatch_lw": 0.25,
        "aliases": ["siliceous limestone"],
    },
    "白云质灰岩": {
        "hatch": "//x", "fill": "#ffffff", "category": "carbonate",
        "hatch_lw": 0.25,
        "aliases": ["dolomitic limestone"],
    },
    "生物碎屑灰岩": {
        "hatch": "//oO", "fill": "#ffffff", "category": "carbonate",
        "hatch_lw": 0.25,
        "aliases": ["bioclastic limestone", "生屑灰岩"],
    },
    "条带状灰岩": {
        "hatch": "//--", "fill": "#ffffff", "category": "carbonate",
        "hatch_lw": 0.25,
        "aliases": ["纹带灰岩", "banded limestone"],
    },
    "竹叶状灰岩": {
        "hatch": "//OO", "fill": "#ffffff", "category": "carbonate",
        "hatch_lw": 0.25,
        "aliases": ["wormkalk"],
    },
    "豹皮灰岩": {
        "hatch": "//o.", "fill": "#ffffff", "category": "carbonate",
        "hatch_lw": 0.25,
        "aliases": ["leopard limestone", "豹斑灰岩"],
    },
    "鲕粒灰岩": {
        "hatch": "//o", "fill": "#ffffff", "category": "carbonate",
        "hatch_lw": 0.25,
        "aliases": ["oolitic limestone", "鲕状灰岩"],
    },
    "泥质条带灰岩": {
        "hatch": "//--", "fill": "#ffffff", "category": "carbonate",
        "hatch_lw": 0.25,
        "aliases": ["泥质纹带灰岩"],
    },
    "泥灰岩": {
        "hatch": "--//", "fill": "#ffffff", "category": "carbonate",
        "hatch_lw": 0.25,
        "aliases": ["marl", "砂质泥灰岩"],
    },
    "含燧石灰岩": {
        "hatch": "//oO", "fill": "#ffffff", "category": "carbonate",
        "hatch_lw": 0.25,
        "aliases": ["cherty limestone", "燧石灰岩"],
    },
    "白云岩": {
        "hatch": "xx", "fill": "#ffffff", "category": "carbonate",
        "hatch_lw": 0.30,
        "aliases": ["dolomite", "dolostone", "白云石"],
    },
    "含燧石白云岩": {
        "hatch": "xxO", "fill": "#ffffff", "category": "carbonate",
        "hatch_lw": 0.30,
        "aliases": ["燧石白云岩", "cherty dolomite", "含燧白云岩"],
    },
    "大理岩": {
        "hatch": "++", "fill": "#ffffff", "category": "carbonate",
        "hatch_lw": 0.30,
        "aliases": ["marble", "砂糖状大理岩", "硅灰石大理岩"],
    },
    "透闪石大理岩": {
        "hatch": "//++", "fill": "#ffffff", "category": "carbonate",
        "hatch_lw": 0.30,
        "aliases": [],
    },
    "阳起石大理岩": {
        "hatch": "//xx", "fill": "#ffffff", "category": "carbonate",
        "hatch_lw": 0.30,
        "aliases": [],
    },
    "透灰石大理岩": {
        "hatch": "++..", "fill": "#ffffff", "category": "carbonate",
        "hatch_lw": 0.30,
        "aliases": ["透灰石硅灰石大理岩"],
    },

    # ===== 碎屑岩 =====
    "砾岩": {
        "hatch": "oO", "fill": "#ffffff", "category": "clastic",
        "hatch_lw": 0.35,
        "aliases": ["conglomerate", "砂砾岩", "砂砾石"],
    },
    "石英砾岩": {
        "hatch": "oO", "fill": "#ffffff", "category": "clastic",
        "hatch_lw": 0.35,
        "aliases": [],
    },
    "砂岩": {
        "hatch": "..", "fill": "#ffffff", "category": "clastic",
        "hatch_lw": 0.35,
        "aliases": ["sandstone", "中砂岩", "碎屑砂岩"],
    },
    "粗砂岩": {
        "hatch": "o.", "fill": "#ffffff", "category": "clastic",
        "hatch_lw": 0.35,
        "aliases": ["coarse sandstone"],
    },
    "细砂岩": {
        "hatch": "....", "fill": "#ffffff", "category": "clastic",
        "hatch_lw": 0.30,
        "aliases": ["fine sandstone", "粉砂岩", "siltstone"],
    },
    "石英砂岩": {
        "hatch": "o", "fill": "#ffffff", "category": "clastic",
        "hatch_lw": 0.35,
        "aliases": ["quartz sandstone", "变质石英砂岩"],
    },
    "长石砂岩": {
        "hatch": "+.", "fill": "#ffffff", "category": "clastic",
        "hatch_lw": 0.35,
        "aliases": ["长石质砂岩", "长石石英砂岩", "arkose"],
    },
    "复成分砂岩": {
        "hatch": "-|", "fill": "#ffffff", "category": "clastic",
        "hatch_lw": 0.35,
        "aliases": ["lithic sandstone"],
    },
    "泥质砂岩": {
        "hatch": "--..", "fill": "#ffffff", "category": "clastic",
        "hatch_lw": 0.30,
        "aliases": ["muddy sandstone"],
    },
    "页岩": {
        "hatch": "---", "fill": "#ffffff", "category": "clastic",
        "hatch_lw": 0.30,
        "aliases": ["shale", "钙质页岩", "碳质页岩", "炭质页岩"],
    },
    "泥岩": {
        "hatch": "---", "fill": "#ffffff", "category": "clastic",
        "hatch_lw": 0.30,
        "aliases": ["mudstone"],
    },
    "硅质岩": {
        "hatch": "////", "fill": "#ffffff", "category": "clastic",
        "hatch_lw": 0.25,
        "aliases": ["siliceous rock", "硅质"],
    },

    # ===== 变质岩 =====
    "板岩": {
        "hatch": "---", "fill": "#ffffff", "category": "metamorphic",
        "hatch_lw": 0.30,
        "aliases": ["slate", "砂质板岩", "炭质板岩", "红柱石板岩"],
    },
    "千枚岩": {
        "hatch": "||", "fill": "#ffffff", "category": "metamorphic",
        "hatch_lw": 0.30,
        "aliases": ["phyllite", "千枚状板岩", "钙质千枚岩"],
    },
    "片岩": {
        "hatch": "///", "fill": "#ffffff", "category": "metamorphic",
        "hatch_lw": 0.30,
        "aliases": ["schist", "二云片岩", "绿泥片岩", "红柱片岩", "榴云片岩"],
    },
    "硬绿云母片岩": {
        "hatch": "///xx", "fill": "#ffffff", "category": "metamorphic",
        "hatch_lw": 0.30,
        "aliases": [],
    },
    "片麻岩": {
        "hatch": "//--", "fill": "#ffffff", "category": "metamorphic",
        "hatch_lw": 0.30,
        "aliases": ["gneiss", "角闪斜长片麻岩"],
    },
    "浅粒岩": {
        "hatch": "--..", "fill": "#ffffff", "category": "metamorphic",
        "hatch_lw": 0.30,
        "aliases": [],
    },
    "变粒岩": {
        "hatch": "//..", "fill": "#ffffff", "category": "metamorphic",
        "hatch_lw": 0.30,
        "aliases": ["斜长角闪变粒岩", "变质砂岩"],
    },
    "石英岩": {
        "hatch": "o", "fill": "#ffffff", "category": "metamorphic",
        "hatch_lw": 0.35,
        "aliases": ["quartzite"],
    },
    "角岩": {
        "hatch": "xx++", "fill": "#ffffff", "category": "metamorphic",
        "hatch_lw": 0.30,
        "aliases": ["硬绿石角岩", "红柱石角岩", "hornfels"],
    },
    "构造角砾岩": {
        "hatch": "oOxx", "fill": "#ffffff", "category": "metamorphic",
        "hatch_lw": 0.35,
        "aliases": ["角砾岩", "tectonic breccia", "断层角砾岩"],
    },
    "糜棱岩": {
        "hatch": "----", "fill": "#ffffff", "category": "metamorphic",
        "hatch_lw": 0.30,
        "aliases": ["mylonite"],
    },
    "混合岩": {
        "hatch": "//--..", "fill": "#ffffff", "category": "metamorphic",
        "hatch_lw": 0.30,
        "aliases": ["migmatite"],
    },

    # ===== 岩浆岩 =====
    "辉绿岩": {
        "hatch": "xx", "fill": "#ffffff", "category": "igneous",
        "hatch_lw": 0.30,
        "aliases": ["diabase", "辉长岩", "gabbro"],
    },
    "闪长岩": {
        "hatch": "+x", "fill": "#ffffff", "category": "igneous",
        "hatch_lw": 0.40,
        "aliases": ["diorite", "石英闪长岩"],
    },
    "花岗闪长岩": {
        "hatch": "++..", "fill": "#ffffff", "category": "igneous",
        "hatch_lw": 0.40,
        "aliases": ["granodiorite"],
    },
    "花岗岩": {
        "hatch": "++", "fill": "#ffffff", "category": "igneous",
        "hatch_lw": 0.50,
        "aliases": ["granite"],
    },
    "煌斑岩": {
        "hatch": "xx//", "fill": "#ffffff", "category": "igneous",
        "hatch_lw": 0.30,
        "aliases": ["lamprophyre"],
    },
    "玄武岩": {
        "hatch": "xx||", "fill": "#ffffff", "category": "igneous",
        "hatch_lw": 0.40,
        "aliases": ["basalt"],
    },
    "安山岩": {
        "hatch": "+|", "fill": "#ffffff", "category": "igneous",
        "hatch_lw": 0.40,
        "aliases": ["andesite"],
    },
    "流纹岩": {
        "hatch": "//|", "fill": "#ffffff", "category": "igneous",
        "hatch_lw": 0.40,
        "aliases": ["rhyolite"],
    },
    "凝灰岩": {
        "hatch": "...", "fill": "#ffffff", "category": "igneous",
        "hatch_lw": 0.30,
        "aliases": ["tuff"],
    },

    # ===== 松散堆积物 =====
    "粘土": {
        "hatch": "||", "fill": "#ffffff", "category": "unconsolidated",
        "hatch_lw": 0.25,
        "aliases": ["亚粘土"],
    },
    "砂层": {
        "hatch": "....", "fill": "#ffffff", "category": "unconsolidated",
        "hatch_lw": 0.30,
        "aliases": ["砂", "sand"],
    },
    "砾石层": {
        "hatch": "ooo", "fill": "#ffffff", "category": "unconsolidated",
        "hatch_lw": 0.35,
        "aliases": ["砾石", "gravel"],
    },
    "人工堆积": {
        "hatch": "++oO", "fill": "#ffffff", "category": "unconsolidated",
        "hatch_lw": 0.30,
        "aliases": ["填土"],
    },
    "覆盖层": {
        "hatch": "", "fill": "#ffffff", "category": "unconsolidated",
        "hatch_lw": 0.20,
        "aliases": ["浮土", "残坡积物", "洪积物", "第四系冲积物", "灰烬层"],
    },
}

# ── 颜色映射 (geo_plotting.py 原有，彩色图件用) ────────────────────
LITHOLOGY_COLORS = {
    "灰岩": "#A8D0DB", "白云岩": "#C0D8C0", "砂岩": "#E8D8A0",
    "粉砂岩": "#E8D8B0", "细砂岩": "#E8D8B0", "泥岩": "#D8C8A8",
    "页岩": "#C8C0A0", "砾岩": "#E0D0B0", "角砾岩": "#D8C8B8",
    "大理岩": "#E8DCC8", "千枚岩": "#C8C0B0", "板岩": "#B8B0A0",
    "片岩": "#C0B8A8", "片麻岩": "#D8C8C0", "花岗岩": "#F0A0A0",
    "玄武岩": "#909090", "凝灰岩": "#C8C0A0", "花岗闪长岩": "#E8B0B0",
    "闪长岩": "#D8C0B0", "辉绿岩": "#A0B090", "石英岩": "#D8C8A0",
    "硅质岩": "#C0C0C0", "粘土": "#F5F0E0", "砂层": "#F0E8C0",
    "砾石层": "#E8D8B0", "人工堆积": "#E0E0D0", "覆盖层": "#F5F0E5",
}


# ── 查找函数 ────────────────────────────────────────────────────────
def get_pattern(name: str) -> dict | None:
    """按规范名或别名查找花纹。找不到返回 None。"""
    if name in LITHOLOGY_PATTERNS:
        return LITHOLOGY_PATTERNS[name]
    for key, pat in LITHOLOGY_PATTERNS.items():
        if name in pat.get("aliases", []):
            return pat
    return None


def get_hatch(name: str, default: str = "////") -> str:
    """查 hatch 字符串，找不到返回 default。"""
    pat = get_pattern(name)
    return pat["hatch"] if pat else default


def get_category(name: str) -> str | None:
    """查岩性大类。"""
    pat = get_pattern(name)
    return pat["category"] if pat else None


def normalize_name(raw: str) -> str:
    """把用户叫法规范到表里的规范中文名。找不到返回原字符串。"""
    if raw in LITHOLOGY_PATTERNS:
        return raw
    for key, pat in LITHOLOGY_PATTERNS.items():
        if raw in pat.get("aliases", []):
            return key
    return raw


def list_by_category(category: str) -> list[str]:
    """列出某大类下所有岩性名。"""
    return [k for k, v in LITHOLOGY_PATTERNS.items() if v["category"] == category]
