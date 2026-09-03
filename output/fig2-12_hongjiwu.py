"""图2-12 上更新统洪积物结构柱状图"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(1, 1, figsize=(4, 7))

# 地层数据: (底深度, 厚度, 岩性名, 花纹样式, 粒度粗→细 0-10)
layers = [
    (0.0, 0.6, '亚粘土', 'dots', 2),
    (0.6, 0.8, '砾石层\n(含卵石)', 'gravel', 9),
    (1.4, 0.4, '亚粘土', 'dots', 2),
    (1.8, 0.8, '砂砾石', 'sand_gravel', 6),
    (2.6, 0.5, '亚粘土', 'dots', 2),
    (3.0, 1.0, '中粗粒砂岩', 'sandstone', 7),
]

# 画柱状图
for bottom, thick, name, pattern, grain in layers:
    top = bottom + thick
    if pattern == 'dots':
        # 亚粘土: 细点
        for y in np.linspace(bottom, top, int(thick * 30)):
            for x in np.linspace(0.05, 0.95, 15):
                if np.random.random() > 0.7:
                    ax.plot(x, y, 'k.', markersize=0.5)
    elif pattern == 'gravel':
        # 砾石层: 圆圈+点
        ax.fill_between([0, 1], bottom, top, color='0.85')
        for y in np.linspace(bottom + 0.05, top - 0.05, int(thick * 8)):
            for x in np.linspace(0.1, 0.9, 6):
                r = np.random.uniform(0.02, 0.06)
                circle = mpatches.Circle((x + np.random.uniform(-0.03, 0.03), y), r,
                                         facecolor='0.7', edgecolor='0.4', linewidth=0.5)
                ax.add_patch(circle)
    elif pattern == 'sand_gravel':
        # 砂砾石: 不规则点+小圈
        ax.fill_between([0, 1], bottom, top, color='0.88')
        for y in np.linspace(bottom, top, int(thick * 20)):
            for x in np.linspace(0.05, 0.95, 10):
                if np.random.random() > 0.6:
                    ax.plot(x, y, 'k.', markersize=0.8)
    elif pattern == 'sandstone':
        # 中粗粒砂岩: 细密点
        for y in np.linspace(bottom, top, int(thick * 25)):
            for x in np.linspace(0.05, 0.95, 20):
                if np.random.random() > 0.6:
                    ax.plot(x, y, 'k.', markersize=0.3)

    # 边框
    ax.plot([0, 0], [bottom, top], 'k-', linewidth=1.2)
    ax.plot([1, 1], [bottom, top], 'k-', linewidth=1.2)
    ax.plot([0, 1], [bottom, bottom], 'k-', linewidth=0.8)
    ax.plot([0, 1], [top, top], 'k-', linewidth=0.8)

    # 岩性标签
    ax.text(1.05, bottom + thick / 2, name, va='center', fontsize=8)

# 底部封口
ax.plot([0, 1], [3.5, 3.5], 'k-', linewidth=1.2)
# 顶部
ax.plot([0, 1], [0, 0], 'k-', linewidth=1.2)

# 左侧厚度标注
ax.set_ylabel('厚度 / m', fontsize=10)
ax.set_xlim(-0.2, 1.6)
ax.set_ylim(4.0, -0.2)

# 右侧粒度箭头
ax2 = ax.twiny()
ax2.set_xlim(ax.get_xlim())
ax2.set_xticks([])
# 画粒度指示箭头在右侧
ax.annotate('', xy=(1.35, 4.0), xytext=(1.35, -0.15),
            arrowprops=dict(arrowstyle='->', color='gray', lw=1.5))
ax.text(1.42, 3.5, '细', fontsize=8, color='gray')
ax.text(1.42, 0.2, '粗', fontsize=8, color='gray')

# 图例
legend_elements = [
    mpatches.Patch(facecolor='white', edgecolor='black', label='亚粘土'),
    mpatches.Patch(facecolor='0.85', edgecolor='black', label='砾石层'),
    mpatches.Patch(facecolor='0.88', edgecolor='black', label='砂砾石'),
    mpatches.Patch(facecolor='white', edgecolor='black', label='中粗粒砂岩'),
]
ax.legend(handles=legend_elements, loc='lower left', fontsize=7, ncol=2,
          bbox_to_anchor=(-0.05, -0.08))

ax.set_title('图2-12 上更新统洪积物结构柱状图', fontsize=12, fontweight='bold', pad=12)
ax.set_xticks([])
ax.set_yticks(np.arange(0, 4.5, 0.5))

ax.text(0.5, 4.15, '比例尺 1:100', ha='center', fontsize=8, style='italic')

plt.tight_layout()
plt.savefig('output/fig2-12_洪积物柱状图.png', dpi=200, bbox_inches='tight')
plt.close()
print('图2-12 完成')
