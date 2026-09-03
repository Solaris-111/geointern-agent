"""一次性修复 section_engine.py — 包含所有改动."""
import re as _re

with open('section_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# === 1. 删图例 ===
content = content.replace(
    'gs = fig.add_gridspec(2, 1, height_ratios=[5, 1], hspace=0.12)\n'
    '        ax = fig.add_subplot(gs[0])\n'
    '        ax_legend = fig.add_subplot(gs[1])\n'
    '        ax_legend.axis("off")',
    'gs = fig.add_gridspec(1, 1)\n'
    '        ax = fig.add_subplot(gs[0])'
)
content = content.replace(
    '        # 12. 图例\n'
    '        gp.draw_section_legend(ax_legend, cfg.formations,\n'
    '                              contacts=contacts, bearing=cfg.bearing)',
    '        # 12. 图例(已禁用)\n'
    '        pass'
)

# === 2. 地层填充 → 韵律for循环 ===
content = content.replace(
    '        # 2. 地层填充\n'
    '        for i in range(len(contacts) - 1):\n'
    '            if i >= len(cfg.formations):\n'
    '                break\n'
    '            poly = self._build_polygon(i)\n'
    '            if poly is not None:\n'
    '                gp.draw_formation_fill(ax, poly[0], poly[1],\n'
    '                                       cfg.formations[i].lithology)',
    '        # 2. 地层填充 → 韵律线\n'
    '        for i in range(len(contacts) - 1):\n'
    '            if i >= len(cfg.formations):\n'
    '                break\n'
    '            fm = cfg.formations[i]\n'
    '            poly = self._build_polygon(i)\n'
    '            if poly is not None:\n'
    '                self._draw_rhythm_fill(ax, i, fm, poly)'
)

# === 3. 接触界线 → 红色 ===
old_contacts = (
    '        # 3. 接触界线\n'
    '        for i, ct in enumerate(contacts):\n'
    '            ye = self._get_elev(ct.dist_km)\n'
    '            xb, yb = self._line_underground(ct.dist_km, self._app_dips[i])\n'
    '            if ct.contact_type == "unconformity":\n'
    '                gp.draw_unconformity_wave(ax, ct.dist_km, ye, xb, yb)\n'
    '            else:\n'
    '                gp.draw_contact_line(ax, ct.dist_km, ye, xb, yb,\n'
    '                                    contact_type=ct.contact_type,\n'
    '                                    is_observed=ct.is_observed)'
)
new_contacts = (
    '        # 3. 接触界线(红色)\n'
    '        for i, ct in enumerate(contacts):\n'
    '            ye = self._get_elev(ct.dist_km)\n'
    '            xb, yb = self._line_underground(ct.dist_km, self._app_dips[i])\n'
    '            lw = 1.2 if ct.is_observed else 0.6\n'
    '            ls = "-" if ct.is_observed else "--"\n'
    '            ax.plot([ct.dist_km, xb], [ye, yb], color="red",\n'
    '                    linewidth=lw, linestyle=ls, zorder=5)\n'
    '            if ct.contact_type == "unconformity":\n'
    '                ax.plot(ct.dist_km, ye, marker="v", color="red",'
)
content = content.replace(old_contacts, new_contacts + '\n'
                         '                        markersize=6, zorder=5)')

# === 4. 添加 numpy import ===
content = content.replace(
    'import math, csv',
    'import math, csv\nimport numpy as np'
)

# === 5. 添加 RhythmLayer import ===
content = content.replace(
    'from section_config import SectionConfig, ContactConfig, FormationConfig, FeatureConfig',
    'from section_config import (SectionConfig, ContactConfig, FormationConfig,\n'
    '                            FeatureConfig, RhythmLayer)'
)

# === 6. 在 _build_polygon 和 render 之间插入新方法 ===
marker = '    # ── 渲染 ───────────────────────────────────────────────────────\n    def render(self, out_path: str):'

new_methods = '''    # ── 韵律填充 ────────────────────────────────────────────────────
    def _auto_rhythm(self, fm):
        """自动检测韵律层段."""
        import re
        from lithology_patterns import LITHOLOGY_PATTERNS, LITHOLOGY_COLORS

        text = fm.lithology
        if fm.description:
            text += " " + fm.description
        text = text.replace("\\n", " ")

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
        y_bot = min(y_seg) - self.cfg.depth_m

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
'''

content = content.replace(marker, new_methods + marker)

with open('section_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("All fixes applied successfully.")
