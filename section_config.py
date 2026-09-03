"""Section engine 配置数据类 — 类型安全，可序列化."""

from dataclasses import dataclass, field


@dataclass
class ContactConfig:
    """一条地层界线 / 观察点。

    dist_km: 界线在剖面上的位置 (km)
    dd:       倾向 (度), None 表示未实测
    da:       倾角 (度), None 表示未实测
    label:    标注文字 (如 "D0602" 或 "QbC/QxJ 整合")
    contact_type: "conformable" | "unconformity" | "fault"
    is_observed: True = 实测露头, False = 推测/覆盖
    """
    dist_km: float
    dd: float | None = None
    da: float | None = None
    label: str = ""
    contact_type: str = "conformable"
    is_observed: bool = True

    def __post_init__(self):
        valid_types = ("conformable", "unconformity", "fault")
        if self.contact_type not in valid_types:
            raise ValueError(f"contact_type must be one of {valid_types}, got {self.contact_type!r}")


@dataclass
class RhythmLayer:
    """韵律旋回内的一个层段。

    name:       层段名 ("厚层鲕粒灰岩")
    proportion: 占旋回宽度的比例 (0-1), 所有层段和为 1.0
    hatch:      matplotlib hatch 图案 ("||", "---", "//" 等)
    color:      填充色 (可选, 默认从 LITHOLOGY 查找)
    """
    name: str
    proportion: float
    hatch: str = "||"
    color: str = ""


@dataclass
class FormationConfig:
    """一个地层单元。

    code:         地层代号 (如 "QbC", "∈1f")
    name:         组名 (如 "长龙山组")
    top_dist_km:  顶界在剖面上的位置 (km)
    lithology:    岩性名 — 规范中文名或别名, 对应 lithology_patterns.py 中的 key
    thickness_m:  厚度 (m), 用于厚度约束; None 则自动计算
    description:  层内岩性简述 (标注在地下区域)
    rhythm_cycle_m: float | None = None   # 单一旋回真厚度(m), None=无韵律
    rhythm_layers: list | None = None     # [RhythmLayer, ...], 从底到顶
    """
    code: str
    name: str
    top_dist_km: float
    lithology: str = "灰岩"
    thickness_m: float | None = None
    description: str = ""
    rhythm_cycle_m: float | None = None
    rhythm_layers: list | None = None


@dataclass
class FeatureConfig:
    """特殊构造 / 化石 / 现象标注。

    dist_km / elev_m: 标注位置
    text:   标注内容
    color:  文字颜色 (默认黑)
    """
    dist_km: float
    elev_m: float
    text: str
    color: str = "black"


@dataclass
class SectionConfig:
    """信手剖面完整配置。"""
    title: str
    bearing: float                     # 剖面方向 (度)
    h_scale: int = 5000                # 水平比例尺分母
    v_scale: int = 1000                # 垂直比例尺分母
    formations: list[FormationConfig] = field(default_factory=list)
    contacts: list[ContactConfig] = field(default_factory=list)
    features: list[FeatureConfig] = field(default_factory=list)
    figsize: tuple[float, float] = (16, 9)
    depth_m: float | None = None       # None = 自动计算
    dpi: int = 350
    csv_path: str = ""                 # 地形 CSV 路径 (可延迟加载)

    @property
    def ve(self) -> float:
        """垂直放大倍数。"""
        return self.h_scale / self.v_scale

    @property
    def total_thickness_m(self) -> float:
        """所有有厚度数据的地层厚度之和。"""
        return sum(f.thickness_m for f in self.formations if f.thickness_m)
