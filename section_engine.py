"""信手剖面图引擎 v2.0 — 地质正确、单遍渲染、规范输出.

用法:
    from section_config import SectionConfig, FormationConfig, ContactConfig, FeatureConfig
    from section_engine import SectionEngine

    cfg = SectionConfig(
        title="黄院东山梁信手剖面图", bearing=89, h_scale=5000, v_scale=1000,
        formations=[FormationConfig("QbC", "长龙山组", 0.0, lithology="变质石英砂岩"), ...],
        contacts=[ContactConfig(0.0, dd=50, da=20, label="D0301"), ...],
        features=[FeatureConfig(0.82, 185, "平行不整合"), ...],
        csv_path="output/L03_黄院东山梁_profile.csv",
    )
    SectionEngine(cfg).render("output/L03_section.png")
"""

import math, csv
import numpy as np
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from lithology_patterns import get_pattern
from section_config import (SectionConfig, ContactConfig, FormationConfig,
                            FeatureConfig, RhythmLayer)
import geo_plotting as gp

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


class SectionEngine:
    def __init__(self, config: SectionConfig):
        self.cfg = config
        self.terrain_dists: np.ndarray | None = None
        self.terrain_elevs: np.ndarray | None = None
        self._app_dips: list[float] = []       # per-contact apparent dips

    # ── 数据加载 ───────────────────────────────────────────────────
    def load_terrain(self, csv_path: str | None = None):
        path = csv_path or self.cfg.csv_path
        if not path:
            raise ValueError("csv_path 未指定")
        dists, elevs = [], []
        with open(path, "r", encoding="utf-8") as f:
            for row in csv.reader(f):
                try:
                    dists.append(float(row[2]) / 1000)
                    elevs.append(float(row[3]))
                except (ValueError, IndexError):
                    continue
        self.terrain_dists = np.array(dists)
        self.terrain_elevs = np.array(elevs)

    # ── 视倾角 ─────────────────────────────────────────────────────
    def _apparent_dip(self, dd: float, da: float) -> float:
        """真倾角 → 视倾角 (沿剖面方向)."""
        bearing = self.cfg.bearing
        angle = min(abs(bearing - dd) % 180, 180 - (abs(bearing - dd) % 180))
        return math.degrees(
            math.atan(math.tan(math.radians(da)) * math.cos(math.radians(angle)))
        )

    def _compute_all_apparent_dips(self):
        """为每条界线独立计算视倾角。无实测数据的界线从相邻实测界线内插。"""
        contacts = self.cfg.contacts
        n = len(contacts)

        # 收集有实测产状的索引
        measured = [(i, contacts[i].dd, contacts[i].da)
                    for i in range(n) if contacts[i].dd is not None and contacts[i].da is not None]

        self._app_dips = []
        for i in range(n):
            if contacts[i].dd is not None and contacts[i].da is not None:
                self._app_dips.append(self._apparent_dip(contacts[i].dd, contacts[i].da))
            elif measured:
                # 找最近的实测点
                nearest_idx = min(measured, key=lambda m: abs(m[0] - i))
                app = self._apparent_dip(nearest_idx[1], nearest_idx[2])
                self._app_dips.append(app)
            else:
                # 没有任何实测数据，用默认值 50°∠20°
                self._app_dips.append(self._apparent_dip(50, 20))

    # ── 辅助 ───────────────────────────────────────────────────────
    def _depth(self) -> float:
        if self.cfg.depth_m is not None:
            return self.cfg.depth_m
        thick = self.cfg.total_thickness_m
        return max(thick * 1.5, 80) if thick > 0 else 120

    def _get_elev(self, dist_km: float) -> float:
        if self.terrain_dists is None:
            return 100
        idx = np.argmin(np.abs(self.terrain_dists - dist_km))
        return float(self.terrain_elevs[idx])

    def _line_underground(self, dist_km: float, app_dip: float) -> tuple[float, float]:
        """界线向地下延伸 — 返回 (x_bot, y_bot)."""
        depth = self._depth()
        if app_dip < 0.5:
            app_dip = 0.5  # 避免除零
        dx = (depth / math.tan(math.radians(app_dip))) / 1000
        return dist_km + dx, self._get_elev(dist_km) - depth

    # ── 多边形构建 ─────────────────────────────────────────────────
    def _build_polygon(self, i: int) -> tuple[list[float], list[float]] | None:
        """构建第 i 个地层单元的多边形。

        顶 = 地形段 (contacts[i].dist ~ contacts[i+1].dist)
        左界 = contacts[i] 以 app_dips[i] 向地下延伸
        右界 = contacts[i+1] 以 app_dips[i+1] 向地下延伸
        底 = 左右下端点连线
        """
        contacts = self.cfg.contacts
        dists = self.terrain_dists
        elevs = self.terrain_elevs

        if i >= len(contacts) - 1:
            return None

        left = contacts[i]
        right = contacts[i + 1]
        xl, xr = left.dist_km, right.dist_km

        xl_bot, yl_bot = self._line_underground(xl, self._app_dips[i])
        xr_bot, yr_bot = self._line_underground(xr, self._app_dips[i + 1])

        mask = (dists >= xl) & (dists <= xr)
        x_seg = list(dists[mask])
        y_seg = list(elevs[mask])

        if len(x_seg) < 2:
            return None

        poly_x = x_seg + [xr_bot, xl_bot]
        poly_y = y_seg + [yr_bot, yl_bot]
        return poly_x, poly_y

    # ── 韵律填充 ────────────────────────────────────────────────────
    def _auto_rhythm(self, fm):
        """自动检测韵律层段."""
        import re
        from lithology_patterns import LITHOLOGY_PATTERNS, LITHOLOGY_COLORS

        text = fm.lithology
        if fm.description:
            text += " " + fm.description
        text = text.replace("\n", " ")

        parts = re.split(r"[夹与和+/]", text)
        parts = [p.strip() for p in parts if p.strip()]

        skip = {
            "薄层", "中层", "厚层", "块状", "条带", "纹带", "泥质", "钙质", "硅质",
            "白云质", "含", "下部", "上部", "顶部", "底部", "斑点状", "砂糖状",
            "变质", "豹皮", "千枚状", "鲕粒", "砂质", "板状", "片状", "致密",
            "透镜体", "0.5mm", "9-11个旋回", "~1mm", "覆盖", "大部分", "为主",
        }
        lith_names = [p for p in parts if p not in skip and len(p) > 1]

        def _match_lith(name):
            if name in LITHOLOGY_PATTERNS:
                return name
            for key in LITHOLOGY_PATTERNS:
                if name.endswith(key) or key in name:
                    return key
            return None

        resolved = []
        for n in lith_names:
            m = _match_lith(n)
            if m:
                resolved.append(m)
            elif len(n) > 2:
                resolved.append(n)

        seen = set()
        resolved = [x for x in resolved if not (x in seen or seen.add(x))]

        if len(resolved) <= 1:
            main = resolved[0] if resolved else "灰岩"
            pat = LITHOLOGY_PATTERNS.get(main, {"hatch": "||"})
            color = LITHOLOGY_COLORS.get(main, "#C8C8C8")
            hatch = pat.get("hatch", "||")
            return [
                RhythmLayer("厚层", 0.55, hatch, color),
                RhythmLayer("薄层", 0.45, hatch, self._lighten(color)),
            ]

        n = len(resolved)
        share = 1.0 / n
        layers = []
        for name in resolved:
            pat = LITHOLOGY_PATTERNS.get(name, {"hatch": "||"})
            color = LITHOLOGY_COLORS.get(name, "#CCCCCC")
            layers.append(RhythmLayer(name, share, pat.get("hatch", "||"), color))

        return layers

    def _lighten(self, hex_color):
        """颜色变浅 30%."""
        c = hex_color.lstrip("#")
        r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
        r = min(255, r + (255 - r) * 3 // 10)
        g = min(255, g + (255 - g) * 3 // 10)
        b = min(255, b + (255 - b) * 3 // 10)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _draw_rhythm_fill(self, ax, i: int, fm, poly):
        """组内画平行旋回线: N条斜线, 平行于组界线."""

        import math

        x_seg, y_seg = poly[0], poly[1]
        xl, xr = x_seg[0], x_seg[-1]
        total_width = xr - xl
        y_bot = min(y_seg) - self._depth()

        # 旋回数
        cycle_m = fm.rhythm_cycle_m if fm.rhythm_cycle_m else 3.0
        if fm.thickness_m:
            n_cycles = int(fm.thickness_m / cycle_m)
        else:
            app_dip = abs(self._app_dips[i]) if i < len(self._app_dips) else 25
            dip_rad = math.radians(max(app_dip, 5))
            est_thickness = total_width * 1000 * math.sin(dip_rad)
            n_cycles = int(est_thickness / cycle_m)
        if n_cycles < 2:
            n_cycles = 2

        # 斜率: dx_per_m = 米→公里 / tan(视倾角)
        app_dip = abs(self._app_dips[i]) if i < len(self._app_dips) else 20
        dip_rad = math.radians(max(app_dip, 5))
        dx_per_m = 0.001 / math.tan(dip_rad)

        # for 循环画平行斜线 (半长)
        cycle_width = total_width / n_cycles
        for c in range(1, n_cycles):
            x_top = xl + c * cycle_width
            y_top = float(np.interp(x_top, self.terrain_dists, self.terrain_elevs))
            half_depth = (y_top - y_bot) * 0.25
            x_bot = x_top + half_depth * dx_per_m
            y_mid = y_top - half_depth
            ax.plot([x_top, x_bot], [y_top, y_mid],
                    "k-", linewidth=0.6, alpha=0.7, zorder=1.5)

        # 标注
        mid_x = (xl + xr) / 2
        ax.text(mid_x, y_bot - 3,
                f"{fm.name}  {n_cycles}条", fontsize=5,
                ha="center", va="top", color="gray",
                bbox=dict(boxstyle="round,pad=0.1", facecolor="white", alpha=0.7))

    # ── 渲染 ───────────────────────────────────────────────────────
    # ── 渲染 ───────────────────────────────────────────────────────
    def render(self, out_path: str):
        if self.terrain_dists is None:
            self.load_terrain()
        if not self._app_dips:
            self._compute_all_apparent_dips()

        cfg = self.cfg
        contacts = cfg.contacts
        dists = self.terrain_dists
        elevs = self.terrain_elevs
        max_dist = dists[-1]
        max_e = float(max(elevs))
        min_e = float(min(elevs))
        depth = self._depth()
        y_bottom = min(0, min_e - depth - 30)
        y_top = max_e + 60

        # ── 画布 ──
        fig = plt.figure(figsize=cfg.figsize, facecolor="white")
        gs = fig.add_gridspec(1, 1)
        ax = fig.add_subplot(gs[0])

        # 1. 地形
        gp.draw_terrain(ax, dists, elevs, y_bottom)

        # 2. 地层填充 → 韵律线
        for i in range(len(contacts) - 1):
            if i >= len(cfg.formations):
                break
            fm = cfg.formations[i]
            poly = self._build_polygon(i)
            if poly is not None:
                self._draw_rhythm_fill(ax, i, fm, poly)

        # 3. 接触界线(红色)
        for i, ct in enumerate(contacts):
            ye = self._get_elev(ct.dist_km)
            xb, yb = self._line_underground(ct.dist_km, self._app_dips[i])
            lw = 1.2 if ct.is_observed else 0.6
            ls = "-" if ct.is_observed else "--"
            ax.plot([ct.dist_km, xb], [ye, yb], color="red",
                    linewidth=lw, linestyle=ls, zorder=5)
            if ct.contact_type == "unconformity":
                ax.plot(ct.dist_km, ye, marker="v", color="red",
                        markersize=6, zorder=5)
            # 点号
            if ct.label and ct.label.startswith("D"):
                short = ct.label.split(" ")[0] if " " in ct.label else ct.label
                gp.draw_point_label(ax, ct.dist_km, ye + 10, short)

        # 4. 产状
        for ct in contacts:
            if ct.dd is not None and ct.da is not None:
                ye = self._get_elev(ct.dist_km)
                gp.draw_attitude_label(ax, ct.dist_km, ye - 12, ct.dd, ct.da)

        # 5. 地层代号
        for i in range(len(contacts) - 1):
            if i >= len(cfg.formations):
                break
            fm = cfg.formations[i]
            xl, xr = contacts[i].dist_km, contacts[i + 1].dist_km
            cx = (xl + xr) / 2
            mask = (dists >= xl) & (dists <= xr)
            if mask.any():
                cy = float(np.median(elevs[mask])) - depth * 0.2
                gp.draw_formation_label(ax, cx, cy, fm.code, fm.name,
                                       block_width=xr - xl)
                # 岩性描述 (块体下部)
                if fm.description:
                    cy_desc = float(np.median(elevs[mask])) - depth * 0.55
                    gp.draw_formation_description(ax, cx, cy_desc, fm.description)

        # 6. 特殊构造
        for ft in cfg.features:
            gp.draw_feature_label(ax, ft.dist_km, ft.elev_m, ft.text,
                                 color=ft.color)

        # 7. 海拔标尺
        gp.draw_altitude_scale(ax)

        # 8. 水平比例尺
        bar_km = max(round(max_dist / 4, 1), 0.1)
        bar_w = max_dist * 0.25
        bar_h = (y_top - y_bottom) * 0.012
        gp.draw_horizontal_scale_bar(ax, max_dist * 0.65, y_top * 0.82,
                                     bar_km, bar_w, bar_h)

        # 9. 端点标签
        gp.draw_endpoint_labels(ax, 0, max_dist, y_bottom)

        # 10. 方向箭头
        arrow_h = (y_top - y_bottom) * 0.05
        gp.draw_section_north_arrow(ax, max_dist * 0.02, y_top * 0.85,
                                    cfg.bearing, arrow_h, max_dist * 0.012)

        # 11. 图名
        gp.draw_section_title(ax, cfg.title)

        # 坐标轴
        gp.setup_section_axes(ax, max_dist, y_bottom, y_top)

        # 12. 图例(已禁用)
        pass

        # 13. 底部信息
        gp.draw_section_footer(fig, cfg.h_scale, cfg.v_scale, cfg.ve,
                              cfg.bearing, contacts)

        fig.savefig(out_path, dpi=cfg.dpi, bbox_inches="tight",
                   facecolor="white", edgecolor="none")
        plt.close()
        print(f"[section_engine] {out_path}")

    # ── 不整合符号 ─────────────────────────────────────────────────
    def _draw_unconformity_wave(self, ax, x: float, y_surf: float):
        """在地表画锯齿/波浪线(不整合符号)，向地下画虚线。"""
        depth = self._depth()
        # 找该界线对应的视倾角
        for i, ct in enumerate(self.cfg.contacts):
            if abs(ct.dist_km - x) < 1e-6:
                app = self._app_dips[i]
                break
        else:
            app = self._apparent_dip(50, 20)

        xb, yb = self._line_underground(x, app)

        # 地表波浪线 (~4个周期, 振幅约1.5%的 y 范围)
        n_waves = 5
        wave_dx = 0.012  # km, ~= 12m 在 1:5000 比例尺
        t = np.linspace(0, 2 * np.pi * n_waves, n_waves * 12)
        wave_x = x + t / (2 * np.pi * n_waves) * wave_dx * n_waves
        wave_y = y_surf + np.sin(t) * 2.5
        ax.plot(wave_x, wave_y, color="black", linewidth=1.5, zorder=6)

        # 地下: 粗虚线
        ax.plot([x, xb], [y_surf, yb], color="black",
               linewidth=1.5, linestyle="--", zorder=5)


# ═══════════════════════════════════════════════════════════════════
# L03 配置
# ═══════════════════════════════════════════════════════════════════
def config_L03() -> SectionConfig:
    return SectionConfig(
        title="黄院东山梁长龙山组(QbC)—亮甲山组(O1l)信手剖面图",
        bearing=89, h_scale=5000, v_scale=1000,
        depth_m=120,
        csv_path="output/L03_黄院东山梁_profile.csv",
        formations=[
            FormationConfig("QbC",   "长龙山组",   0.000, lithology="变质石英砂岩",
                           description="变质石英砂岩+砂质板岩\n向上变细, 大部分覆盖"),
            FormationConfig("QxJ",   "景儿峪组",   0.694, lithology="大理岩",
                           description="大理岩 (砂糖状风化)\n+钙质板岩"),
            FormationConfig("E1f",   "府君山组",   0.820, lithology="豹皮灰岩",
                           description="豹皮灰岩+纹带灰岩\n大型平卧褶皱"),
            FormationConfig("E1+2m", "馒头毛庄组", 0.924, lithology="千枚状板岩",
                           description="千枚状板岩\n大理岩透镜体"),
            FormationConfig("E2x",   "徐庄组",     0.955, lithology="鲕粒灰岩",
                           description="灰岩+板岩夹鲕粒灰岩\n鲕粒~1mm, 孔雀石薄膜"),
            FormationConfig("E2z",   "张夏组",     1.017, lithology="鲕粒灰岩",
                           description="鲕粒灰岩 0.5mm\n泥质条带, 9-11个旋回"),
            FormationConfig("E2h",   "黄院组",     1.329, lithology="泥质条带灰岩",
                           description="泥质条带灰岩 条带1-2cm\n等斜平卧褶皱"),
            FormationConfig("O1y",   "冶里组",     1.391, lithology="泥质纹带灰岩",
                           description="泥质纹带灰岩\n白云质灰岩"),
            FormationConfig("O1l",   "亮甲山组",   1.487, lithology="白云岩",
                           description="白云岩 刀砍纹发育"),
        ],
        contacts=[
            ContactConfig(0.000, dd=50, da=20, label="D0301"),
            ContactConfig(0.694, dd=50, da=20, label="D0302"),
            ContactConfig(0.820, dd=50, da=20, label="D0303 平行不整合", contact_type="unconformity"),
            ContactConfig(0.924, dd=50, da=20, label="D0304"),
            ContactConfig(0.955, dd=50, da=20, label="D0305"),
            ContactConfig(1.017, dd=50, da=20, label="D0306"),
            ContactConfig(1.329, dd=50, da=20, label="D0307"),
            ContactConfig(1.391, dd=50, da=20, label="D0308"),
            ContactConfig(1.487, dd=50, da=20, label="D0309"),
        ],
        features=[
            FeatureConfig(0.82, 185, "平行不整合 (房山运动) 间断约2亿年", color="#c0392b"),
            FeatureConfig(0.87, 160, "大型平卧褶皱 (府君山组内)", color="#e67e22"),
            FeatureConfig(1.36, 140, "等斜平卧褶皱 (黄院组内)", color="#e67e22"),
        ],
    )


# ═══════════════════════════════════════════════════════════════════
# L06 配置
# ═══════════════════════════════════════════════════════════════════
def config_L06() -> SectionConfig:
    return SectionConfig(
        title="八角寨—拴马桩桥信手剖面图",
        bearing=70, h_scale=20000, v_scale=4000,
        depth_m=120,
        csv_path="output/L02_八角寨-拴马庄桥_profile.csv",
        formations=[
            FormationConfig("JxW5", "雾迷山组五段", 0.00, lithology="含燧石白云岩",
                           description="浅灰中厚层含燧石条带白云岩\n锥状/柱状叠层石, A/B韵律互层"),
            FormationConfig("JxH",  "洪水庄组",     0.60, lithology="千枚岩",
                           description="褐色含锰板岩\n下部夹变质细砂岩, 上部白云岩透镜体"),
            FormationConfig("JxT1", "铁岭组一段",   1.30, lithology="白云岩",
                           description="灰色中厚层-巨厚层白云岩\n斜层理+羽状交错层理"),
            FormationConfig("JxT2", "铁岭组二段",   1.75, lithology="白云质灰岩",
                           description="深灰薄层白云质灰岩夹黑色板岩\n单层5-20cm, 劈理化"),
            FormationConfig("JxT3", "铁岭组三段",   2.15, lithology="白云岩",
                           description="灰白中厚层白云岩\n顶部包心菜状叠层石"),
            FormationConfig("QbX",  "下马岭组",     2.60, lithology="千枚状板岩",
                           description="底:铁质古风化壳50-60cm\n下部:含磁铁矿千枚状板岩\n上部:炭质千枚岩"),
            FormationConfig("QbC",  "长龙山组",     3.55, lithology="变质石英砂岩",
                           description="底部厚层-巨厚层变质石英砂岩\n发育斜层理, 磨圆分选好"),
        ],
        contacts=[
            ContactConfig(0.00, dd=50, da=20, label="D0601 岩性控制点"),
            ContactConfig(0.60, dd=50, da=20, label="D0602 整合"),
            ContactConfig(1.30, dd=50, da=20, label="D0603 整合"),
            ContactConfig(1.75, dd=50, da=20, label="D0604 整合"),
            ContactConfig(2.15, dd=50, da=20, label="D0605 整合"),
            ContactConfig(2.60, dd=55, da=22, label="D0606 平行不整合", contact_type="unconformity"),
            ContactConfig(3.55, dd=50, da=20, label="D0607 整合"),
        ],
        features=[
            FeatureConfig(2.10, 195, "包心菜状叠层石"),
            FeatureConfig(2.60, 185, "平行不整合 古风化壳 50-60cm (芹峪运动)", color="#c0392b"),
        ],
    )


# ═══════════════════════════════════════════════════════════════════
# 入口
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import os
    os.makedirs("output", exist_ok=True)

    print("=== L03 黄院东山梁 ===")
    SectionEngine(config_L03()).render("output/L03_标准剖面图.png")

    print("=== L06 八角寨-拴马桩桥 ===")
    SectionEngine(config_L06()).render("output/L06_标准剖面图.png")

    print("完成 — L03 + L06 信手剖面图 v2.0")
