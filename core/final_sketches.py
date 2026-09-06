"""铅笔素描 + 地质标注 → 最终图件"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def anno_sketch(pencil_path, out_path, title, subtitle, annotations, legend_items,
                gps="", scale_text="~10 cm", figsize=(12, 9)):
    """在铅笔素描上叠加标注"""
    img = plt.imread(pencil_path)
    h, w = img.shape[:2]

    fig, ax = plt.subplots(figsize=figsize)
    ax.imshow(img, cmap="gray", extent=[0, w, 0, h])
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")

    # 标注
    for (x, y, text, color, fontsize, style, box_color) in annotations:
        kw = dict(fontsize=fontsize, color=color, ha="center", va="center", zorder=10)
        if style == "bold":
            kw["fontweight"] = "bold"
        elif style == "italic":
            kw["fontstyle"] = "italic"
        if box_color:
            kw["bbox"] = dict(boxstyle="round,pad=0.3", facecolor=box_color,
                             edgecolor=color, alpha=0.88, linewidth=0.7)
        ax.text(x, y, text, **kw)

    # 标题
    ax.text(w/2, h + h*0.03, title, ha="center", fontsize=16, fontweight="bold",
            transform=ax.transData, color="#1a1a1a")
    ax.text(w/2, h + h*0.005, subtitle, ha="center", fontsize=10,
            transform=ax.transData, color="#555")

    # 比例尺 (左下角)
    sx, sy = w * 0.06, h * 0.05
    bar_w = w * 0.2
    ax.plot([sx, sx + bar_w], [sy, sy], color="black", linewidth=2.5, clip_on=False)
    ax.plot([sx, sx], [sy - h*0.003, sy + h*0.003], color="black", linewidth=2, clip_on=False)
    ax.plot([sx + bar_w, sx + bar_w], [sy - h*0.003, sy + h*0.003], color="black", linewidth=2, clip_on=False)
    ax.text(sx + bar_w/2, sy - h*0.015, scale_text, ha="center", fontsize=9, color="black")

    # 指北针 (右下角)
    nx, ny = w * 0.92, h * 0.08
    ax.plot([nx, nx], [ny, ny + h*0.04], color="black", linewidth=2, clip_on=False)
    ax.plot([nx, nx - w*0.008], [ny, ny + h*0.015], color="black", linewidth=1.5, clip_on=False)
    ax.plot([nx, nx + w*0.008], [ny, ny + h*0.015], color="black", linewidth=1.5, clip_on=False)
    ax.text(nx, ny + h*0.048, "N", ha="center", fontsize=10, fontweight="bold", color="black")

    # GPS 脚注
    if gps:
        ax.text(w/2, -h*0.025, gps, ha="center", fontsize=7, color="#999", transform=ax.transData)

    plt.tight_layout(pad=0.5)
    fig.savefig(out_path, dpi=250, bbox_inches="tight", facecolor="white", edgecolor="none")
    plt.close()
    print(f"  → {out_path}")


# ============================================================
# 图6-1 燧石条带先后关系
# ============================================================
print("图6-1 燧石条带先后关系...")

anno_sketch(
    "output/sketches/D0601_chert_pencil.png",
    "output/sketches/图6-1_燧石条带先后关系_标注.png",
    title="图6-1  燧石条带先后关系素描图",
    subtitle="D0601  雾迷山组第五段 (JxW⁵)  白云岩中燧石条带",
    annotations=[
        (750, 850, "① 顺层燧石条带\n(沉积/成岩期)", "#8b6914", 11, "bold", "#faf5eb"),
        (750, 550, "② 穿层燧石脉\n(构造-热液期)", "#4a4a4a", 11, "bold", "#f5f5f5"),
        (1150, 800, "③ 裂隙充填燧石脉\n(晚期构造-热液)", "#1a1a1a", 11, "bold", "#f0f0f0"),
        (400, 300, "白云岩层面\n单层 5-10cm", "#888", 9, "italic", "white"),
        (850, 500, "② 切割 ①", "#c0392b", 9, "bold", "white"),
        (1050, 700, "③ 切割 ②", "#c0392b", 9, "bold", "white"),
    ],
    legend_items=[],
    gps="露头位置: 周口店 八角寨西坡 周张公路垭口  |  坐标: 39°39′19″N 115°52′36″E  |  视向: NW",
    scale_text="~10 cm",
)

# ============================================================
# 图6-2 包心菜状叠层石
# ============================================================
print("图6-2 包心菜状叠层石...")

anno_sketch(
    "output/sketches/D0605_stromatolite_pencil.png",
    "output/sketches/图6-2_包心菜状叠层石_标注.png",
    title="图6-2  包心菜状叠层石素描图",
    subtitle="D0605  铁岭组上段 (JxT³)  包心菜状叠层石 (cabbage-like stromatolite)",
    annotations=[
        (816, 750, "包心菜状叠层石\n(cabbage-like stromatolite)\n宽 ~50-60cm  高 ~30-40cm",
         "#3a2a1a", 11, "bold", "#faf5eb"),
        (816, 480, "同心纹层 明暗交替\n明层: 浅色碳酸盐\n暗层: 富有机质\n间距 1-2mm",
         "#4a3a2a", 9, "normal", "#faf5eb"),
        (250, 600, "围岩: JxT³ 白云岩\n浅灰-灰白色\n致密, 具层理",
         "#666", 8, "italic", "white"),
        (816, 1020, "底界清晰\n与下伏白云岩接触",
         "#8b4513", 8, "normal", "#faf5eb"),
        (500, 900, "生长方向 ↑", "#8b4513", 8, "italic", None),
        (1200, 300, "露头面积约 1-2m²\n叠层石孤立产出", "#888", 7, "italic", None),
    ],
    legend_items=[],
    gps="露头位置: 周口店 周张公路7.4km处  |  坐标: 39°39′21″N 115°53′10″E  |  JxT³ 铁岭组上段",
    scale_text="~20 cm",
)

print("\n完成！")
