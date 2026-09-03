"""图6-2 D0605 包心菜状叠层石 素描图"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

fig, ax = plt.subplots(figsize=(10, 9))
ax.set_xlim(0, 14)
ax.set_ylim(0, 16)
ax.set_aspect("equal")
ax.axis("off")

# ============================================================
# 围岩 — 铁岭组三段白云岩, 层理缓倾
# ============================================================

dip_angle = np.radians(12)
for i in range(10):
    y0 = 14.5 - i * 1.5
    x_vals = np.linspace(0.5, 13.5, 60)
    y_vals = y0 - (x_vals - 0.5) * np.tan(dip_angle)
    y_vals += 0.06 * np.sin(x_vals * 2.5 + i * 0.8)
    ax.plot(x_vals, y_vals, color="#9a9a9a", linewidth=0.6, alpha=0.5)

# 围岩填充 (浅灰色白云岩)
bg_rect = plt.Rectangle((0.5, 1), 13, 14, facecolor="#f2efe8", edgecolor="none", alpha=0.3, zorder=0)
ax.add_patch(bg_rect)

# ============================================================
# 叠层石主体 — 穹状/包心菜状, 宽50-60cm 高30-40cm
# ============================================================

# 外轮廓
theta = np.linspace(0, np.pi, 60)
cx, cy = 7, 9.5
rx, ry = 3.2, 2.4
outline_x = cx + rx * np.cos(theta)
outline_y = cy + ry * np.sin(theta) - ry

# 微调成穹状 (底部稍宽)
outline_y += 0.3 * (1 - abs(outline_x - cx) / rx)

# 画外轮廓
ax.fill(outline_x, outline_y, facecolor="#e8e0d5", edgecolor="#6b5b4f", linewidth=2.0, alpha=0.85, zorder=2)

# ============================================================
# 同心纹层 — 明暗交替, 1-2mm间距, 中心向外辐射
# ============================================================

# 多条同心弧线
n_laminae = 28
for k in range(1, n_laminae + 1):
    # 从外向内收缩
    frac = 1 - k * 0.032
    rxk = rx * frac
    ryk = ry * frac
    lam_x = cx + rxk * np.cos(theta)
    lam_y = cy + ryk * np.sin(theta) - ry * frac

    # 明暗交替: 偶数层深色(暗层=有机质), 奇数层浅色(明层=碳酸盐)
    if k % 3 == 0:
        color, alpha, lw = "#4a3a2a", 0.7, 0.6
    elif k % 3 == 1:
        color, alpha, lw = "#c4b8a8", 0.5, 0.4
    else:
        color, alpha, lw = "#8a7a6a", 0.6, 0.5

    ax.plot(lam_x, lam_y, color=color, linewidth=lw, alpha=alpha, zorder=3)

# 最外层加粗
outer_theta = np.linspace(0, np.pi, 80)
outer_x = cx + rx * np.cos(outer_theta)
outer_y = cy + ry * np.sin(outer_theta) - ry
outer_y += 0.3 * (1 - abs(outer_x - cx) / rx)
ax.plot(outer_x, outer_y, color="#5a4a3a", linewidth=2.2, zorder=4)

# ============================================================
# 内部生长结构 — 微小凸起指示生长方向
# ============================================================

# 中心顶部小凸起
bump_x = np.linspace(cx - 1.2, cx + 1.2, 30)
bump_y = cy - 1.2 + 0.4 * np.exp(-((bump_x - cx) ** 2) / 0.4)
bump_y += 0.1 * np.sin(bump_x * 5)
ax.fill(bump_x, bump_y, facecolor="#e8e0d5", edgecolor="#6b5b4f", linewidth=1.0, zorder=5)

# 内部纹层跟随凸起
for k in range(1, 6):
    frac = 1 - k * 0.04
    bx = cx + (bump_x - cx) * frac
    by = cy - 2.4 + (bump_y - (cy - 2.4)) * frac + k * 0.08
    color = "#4a3a2a" if k % 2 == 0 else "#c4b8a8"
    ax.plot(bx, by, color=color, linewidth=0.5, alpha=0.7, zorder=5)

# ============================================================
# 叠层石与围岩的接触界线 (底界清晰)
# ============================================================

base_x = np.linspace(cx - rx - 0.3, cx + rx + 0.3, 50)
base_y_base = cy - ry - 0.1
base_y = np.full_like(base_x, base_y_base)
# 稍微不平整
base_y += 0.08 * np.sin(base_x * 3)
ax.plot(base_x, base_y, color="#8b4513", linewidth=1.8, linestyle="-", zorder=4)
# 顶界 (轻微侵蚀)
top_mid = cy - ry + 2 * ry * 0.85
top_line_x = np.linspace(cx - rx * 0.7, cx + rx * 0.7, 30)
top_line_y = np.full_like(top_line_x, cy - 0.3)
top_line_y -= 0.05 * abs(top_line_x - cx)
ax.plot(top_line_x, top_line_y, color="#8b4513", linewidth=1.3, linestyle=":", alpha=0.7, zorder=4)
ax.annotate("轻微侵蚀", (cx + 1.5, top_line_y[0] - 0.4), fontsize=6.5,
            color="#a0522d", style="italic", ha="center")

# ============================================================
# 标注
# ============================================================

# 叠层石名称
ax.annotate("包心菜状叠层石\n(cabbage-like stromatolite)",
            xy=(cx, cy + 0.5), fontsize=10, fontweight="bold",
            color="#3a2a1a", ha="center", zorder=10,
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
                     edgecolor="#8b7355", alpha=0.9))

# 明暗纹层标注
ax.annotate("明暗纹层交替\n明层: 浅色碳酸盐\n暗层: 富有机质\n间距1-2mm, 同心环状",
            xy=(10.5, 7.5), fontsize=7.5, color="#4a3a2a", ha="left",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#faf5eb",
                     edgecolor="#8b7355", alpha=0.9))
ax.plot([10.0, 8.8], [7.8, 8.5], color="#8b7355", linewidth=0.8)

# 围岩标注
ax.annotate("围岩: 铁岭组三段\n(JxT³) 白云岩\n浅灰-灰白色\n致密, 具层理",
            xy=(2, 5.5), fontsize=7.5, color="#666", ha="left",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                     edgecolor="#aaa", alpha=0.85))

# 底界标注
ax.annotate("底界清晰\n与下伏白云岩\n接触界线明显",
            xy=(cx - 2, base_y_base - 0.8), fontsize=7, color="#8b4513",
            ha="center",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#faf5eb",
                     edgecolor="#8b7355", alpha=0.85))
ax.plot([cx - 0.5, cx - 1.5], [base_y_base, base_y_base - 0.4],
        color="#8b4513", linewidth=0.6)

# 生长方向小箭头
for ax_pos in [cx - 1.5, cx, cx + 1.5]:
    arrow_y_base = cy - ry + 0.5
    ax.annotate("",
                xy=(ax_pos, cy - ry + 2.2),
                xytext=(ax_pos, arrow_y_base),
                arrowprops=dict(arrowstyle="->", color="#8b4513", lw=1.0,
                               connectionstyle="arc3,rad=0"))
ax.text(cx, cy - ry + 0.15, "生长方向↑", fontsize=7, color="#8b4513",
        ha="center", fontstyle="italic")

# 露头背景标注
ax.annotate("露头面积约1-2m²\n叠层石位于中部偏下\n孤立产出",
            xy=(12, 12.5), fontsize=7, color="#888", ha="right",
            style="italic")

# ============================================================
# 图框
# ============================================================

# 图号标题
ax.text(7, 15.6, "图6-2  包心菜状叠层石素描图", ha="center", fontsize=13,
        fontweight="bold",
        bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.4"))

ax.text(7, 14.8, "D0605  铁岭组上段 (JxT³)  包心菜状叠层石 (cabbage-like stromatolite)",
        ha="center", fontsize=8.5, color="#555")

# 比例尺
scale_x, scale_y = 1.5, 14.2
bar_cm = 2.5
ax.plot([scale_x, scale_x + bar_cm], [scale_y, scale_y], color="black", linewidth=2)
ax.plot([scale_x, scale_x], [scale_y - 0.2, scale_y + 0.2], color="black", linewidth=1.5)
ax.plot([scale_x + bar_cm, scale_x + bar_cm], [scale_y - 0.2, scale_y + 0.2], color="black", linewidth=1.5)
ax.text(scale_x + bar_cm / 2, scale_y - 0.5, "~20 cm", ha="center", fontsize=8)

# 指北针
nx, ny = 12.5, 14.2
ax.plot([nx, nx], [ny, ny + 0.7], color="black", linewidth=1.5)
ax.plot([nx, nx - 0.18], [ny, ny + 0.25], color="black", linewidth=1.2)
ax.plot([nx, nx + 0.18], [ny, ny + 0.25], color="black", linewidth=1.2)
ax.text(nx, ny + 0.85, "N", ha="center", fontsize=9, fontweight="bold")

# 叠层石放大框 — 局部纹层细节
detail_box = plt.Rectangle((cx - 1.0, cy - 1.5), 2.0, 1.5,
                           facecolor="none", edgecolor="#c0392b", linewidth=1.2,
                           linestyle="--", zorder=10)
ax.add_patch(detail_box)

# 放大区域
magnify_x, magnify_y = 1.5, 2.2
mag_w, mag_h = 3.0, 2.5
ax.add_patch(plt.Rectangle((magnify_x, magnify_y), mag_w, mag_h,
                           facecolor="white", edgecolor="#c0392b",
                           linewidth=1.2, zorder=11))

# 放大框内画纹层细节
mag_cx = magnify_x + mag_w / 2
mag_cy = magnify_y + mag_h / 2
for m in range(1, 14):
    frac_m = 0.9 - m * 0.055
    detail_x = mag_cx + (mag_w * 0.4) * np.cos(np.linspace(0, np.pi, 30)) * frac_m
    detail_y = mag_cy + (mag_h * 0.35) * np.sin(np.linspace(0, np.pi, 30)) * frac_m - mag_h * 0.2 * frac_m
    if m % 3 == 0:
        c, a = "#4a3a2a", 0.8
    elif m % 3 == 1:
        c, a = "#c4b8a8", 0.6
    else:
        c, a = "#8a7a6a", 0.7
    ax.plot(detail_x, detail_y, color=c, linewidth=0.5, alpha=a, zorder=12)

ax.text(mag_cx, magnify_y + mag_h + 0.15, "纹层放大 (明暗交替 1-2mm)",
        ha="center", fontsize=7, color="#c0392b", fontweight="bold", zorder=12)

# 连接线
ax.plot([cx + 1.0, magnify_x + mag_w / 2], [cy - 1.5, magnify_y + mag_h],
        color="#c0392b", linewidth=0.8, linestyle=":", zorder=10)

# ============================================================
# 底部
# ============================================================
ax.text(7, 0.6,
        "露头位置: 周口店 周张公路7.4km处  |  坐标: 39°39′21″N 115°53′10″E  |  JxT³ 铁岭组上段",
        ha="center", fontsize=7, color="#999")

fig.tight_layout(pad=0.5)
fig.savefig("output/图6-2_包心菜状叠层石.png", dpi=250, bbox_inches="tight",
            facecolor="white", edgecolor="none")
plt.close()
print("已保存: output/图6-2_包心菜状叠层石.png")
