"""图2-14 北京猿人洞穴堆积剖面示意图"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(1, 1, figsize=(6, 9))

layers = [
    (0, 4, '1-2层\n含石灰角砾层', 'breccia_lime', '含石灰的角砾层，厚约4m'),
    (4, 3, '3层\n粗角砾岩层', 'breccia_coarse', '含洞顶崩塌大灰岩块\n1966年头盖骨出自此层，厚约3m'),
    (7, 6, '4层\n灰烬层\n(上文化层)', 'ash_upper', '含烧骨、烧石和大的炭块，厚约6m'),
    (13, 1, '5层\n硬灰层', 'hard_ash', '厚约1m'),
    (14, 5, '6层\n角砾岩', 'breccia', '含巨大石灰岩块和动物粪层，厚约5m'),
    (19, 2, '7层\n砂层', 'sand', '厚约2m'),
    (21, 6, '8-9层\n含灰烬角砾层\n(下文化层)', 'ash_lower', '约一半以上北京猿人化石发现于此层，厚约6m'),
    (27, 2, '10层\n红土和灰烬层', 'red_ash', '厚约2m'),
    (29, 2, '11层\n角砾岩层', 'breccia_11', '1929年第一个北京猿人头骨发现层位，厚约2m'),
    (31, 2, '12层\n红砂层', 'red_sand', '厚约2m'),
    (33, 2, '13层\n含动物粪泥沙层', 'silt', '底部为巨砾，厚约2m'),
]

total_depth = 35

# 画洞壁（左侧）
cave_x = np.linspace(-0.3, 0.0, 50)
cave_y = np.linspace(0, total_depth, 50)
# 不规则洞壁
cave_x_wall = -0.15 + 0.08 * np.sin(cave_y * 0.4) + 0.05 * np.sin(cave_y * 0.9)
ax.fill_betweenx(cave_y, -1.0, cave_x_wall, color='0.7', alpha=0.5)
ax.plot(cave_x_wall, cave_y, 'k-', linewidth=1.5)

# 画各层
for bottom, thick, label, style, desc in layers:
    top = bottom + thick
    if style == 'breccia_lime':
        ax.fill_between([0, 1], bottom, top, color='0.9')
        for y in np.linspace(bottom + 0.1, top - 0.1, int(thick * 4)):
            for x in np.linspace(0.1, 0.9, 5):
                if np.random.random() > 0.4:
                    tri = mpatches.Polygon([
                        (x, y), (x + 0.06, y + 0.08), (x - 0.04, y + 0.05)
                    ], facecolor='0.75', edgecolor='0.5', linewidth=0.3)
                    ax.add_patch(tri)
    elif style == 'breccia_coarse':
        ax.fill_between([0, 1], bottom, top, color='0.82')
        for y in np.linspace(bottom + 0.15, top - 0.15, int(thick * 3)):
            for x in np.linspace(0.15, 0.85, 4):
                rect = mpatches.FancyBboxPatch((x, y), 0.1, 0.15,
                    boxstyle='round,pad=0.01', facecolor='0.7', edgecolor='0.4', linewidth=0.5)
                ax.add_patch(rect)
        # 大灰岩块
        big_rect = mpatches.FancyBboxPatch((0.3, bottom + 0.5), 0.4, 0.8,
            boxstyle='round,pad=0.02', facecolor='0.65', edgecolor='0.3', linewidth=1)
        ax.add_patch(big_rect)
        ax.text(0.5, bottom + 0.9, '大灰岩块', ha='center', fontsize=6, color='0.2')
    elif style == 'ash_upper':
        ax.fill_between([0, 1], bottom, top, color='0.55')
        for y in np.linspace(bottom, top, int(thick * 6)):
            ax.plot([0, 1], [y, y], '-', color='0.45', linewidth=0.3)
        # 烧骨标记
        for y in np.linspace(bottom + 0.3, top - 0.3, 3):
            ax.plot(0.3, y, 'k*', markersize=6)
            ax.plot(0.7, y, 'k*', markersize=5)
    elif style == 'hard_ash':
        ax.fill_between([0, 1], bottom, top, color='0.6')
        for y in np.linspace(bottom, top, int(thick * 8)):
            ax.plot([0, 1], [y, y], '-', color='0.5', linewidth=0.5)
    elif style == 'breccia':
        ax.fill_between([0, 1], bottom, top, color='0.85')
        for y in np.linspace(bottom + 0.1, top - 0.1, int(thick * 3)):
            for x in np.linspace(0.1, 0.9, 4):
                tri = mpatches.Polygon([
                    (x, y), (x + 0.08, y + 0.1), (x - 0.03, y + 0.06)
                ], facecolor='0.75', edgecolor='0.5', linewidth=0.3)
                ax.add_patch(tri)
    elif style == 'sand':
        ax.fill_between([0, 1], bottom, top, color='0.92')
        for y in np.linspace(bottom, top, int(thick * 15)):
            for x in np.linspace(0.05, 0.95, 20):
                if np.random.random() > 0.8:
                    ax.plot(x, y, 'k.', markersize=0.3)
    elif style == 'ash_lower':
        ax.fill_between([0, 1], bottom, top, color='0.5')
        for y in np.linspace(bottom, top, int(thick * 6)):
            ax.plot([0, 1], [y, y], '-', color='0.4', linewidth=0.3)
        ax.fill_between([0, 1], bottom + 0.5, bottom + 1.5, color='0.6')
        ax.text(0.5, bottom + thick / 2, '★ 大部分北京猿人\n化石发现于此', ha='center',
                fontsize=7, color='red', fontweight='bold')
    elif style == 'red_ash':
        ax.fill_between([0, 1], bottom, top, color='0.72')
        for y in np.linspace(bottom, top, int(thick * 10)):
            ax.plot([0, 1], [y, y], '-', color='0.55', linewidth=0.5)
    elif style == 'breccia_11':
        ax.fill_between([0, 1], bottom, top, color='0.88')
        ax.text(0.5, bottom + thick / 2, '★ 第一个北京猿人头骨\n(1929年发现)', ha='center',
                fontsize=7, color='red', fontweight='bold')
    elif style == 'red_sand':
        ax.fill_between([0, 1], bottom, top, color='0.78')
        for y in np.linspace(bottom, top, int(thick * 12)):
            for x in np.linspace(0.05, 0.95, 18):
                if np.random.random() > 0.75:
                    ax.plot(x, y, 'k.', markersize=0.4)
    elif style == 'silt':
        ax.fill_between([0, 1], bottom, top, color='0.9')
        ax.text(0.5, bottom + 1.0, '底部巨砾', ha='center', fontsize=7)
        rect = mpatches.FancyBboxPatch((0.25, bottom + 0.1), 0.5, 0.4,
            boxstyle='round,pad=0.02', facecolor='0.7', edgecolor='0.4', linewidth=0.8)
        ax.add_patch(rect)

    # 层边界
    ax.plot([0, 1], [bottom, bottom], 'k-', linewidth=1.2)
    ax.plot([0, 1], [top, top], 'k-', linewidth=1.2)
    ax.plot([0, 0], [bottom, top], 'k-', linewidth=1.2)
    ax.plot([1, 1], [bottom, top], 'k-', linewidth=1.2)

    # 层号标签
    ax.text(1.08, bottom + thick / 2, label, va='center', fontsize=7)

# 围岩标记
ax.text(-0.6, total_depth / 2, '围岩\n马家沟组\n(O₁m)\n厚层碳酸盐岩',
        ha='center', fontsize=8, rotation=90, va='center')

# 设置
ax.set_ylim(total_depth + 0.5, -0.5)
ax.set_xlim(-1.0, 1.8)
ax.set_xticks([])
ax.set_ylabel('深度 (m)', fontsize=10)
ax.set_yticks(np.arange(0, total_depth + 1, 5))

# 方向
ax.annotate('E →', xy=(1.5, -0.2), fontsize=10, fontweight='bold')

ax.set_title('图2-14 北京猿人洞穴堆积剖面示意图', fontsize=12, fontweight='bold', pad=12)

# 图例
legend_elements = [
    mpatches.Patch(facecolor='0.9', edgecolor='black', label='角砾层'),
    mpatches.Patch(facecolor='0.55', edgecolor='black', label='灰烬层'),
    mpatches.Patch(facecolor='0.92', edgecolor='black', label='砂层'),
    mpatches.Patch(facecolor='0.72', edgecolor='black', label='红土层'),
    mpatches.Patch(facecolor='0.7', edgecolor='black', label='围岩(灰岩)'),
]
ax.legend(handles=legend_elements, loc='lower left', fontsize=7, ncol=3,
          bbox_to_anchor=(-0.02, -0.06))

ax.text(0.5, total_depth + 0.8, '比例尺 1:100 (垂直)', ha='center', fontsize=8, style='italic')

plt.tight_layout()
plt.savefig('output/fig2-14_洞穴堆积剖面.png', dpi=200, bbox_inches='tight')
plt.close()
print('图2-14 完成')
