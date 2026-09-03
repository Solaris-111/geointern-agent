"""图2-13 周口店三级阶地剖面示意图"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(1, 1, figsize=(12, 5))

# 手控定义地形关键点
points = [
    (0, 58), (40, 56), (80, 54),    # T3 顶部
    (100, 46), (120, 36),            # T3 陡坎
    (140, 34), (180, 32), (210, 30), # T2 顶部
    (230, 24), (250, 16),            # T2 陡坎
    (280, 14), (340, 12), (380, 10), # T1 顶部
    (410, 6), (430, 0),              # T1 陡坎
    (480, -4), (540, -6), (600, -8), # 河床
]

xs = np.array([p[0] for p in points])
ys = np.array([p[1] for p in points])

# 平滑插值
from scipy.interpolate import interp1d
f = interp1d(xs, ys, kind='quadratic')
x_smooth = np.linspace(0, 600, 500)
y_smooth = f(x_smooth)

# 基岩线 (地表下 5-10m)
bedrock = y_smooth - np.linspace(5, 10, len(y_smooth))

# 地表
ax.plot(x_smooth, y_smooth, 'k-', linewidth=1.8)
ax.fill_between(x_smooth, y_smooth, bedrock, color='0.85', alpha=0.4)

# 基岩
ax.fill_between(x_smooth, bedrock, -25, color='0.65', alpha=0.3, hatch='//', edgecolor='0.4', linewidth=0.05)
ax.plot(x_smooth, bedrock, 'k--', linewidth=0.8, alpha=0.6)

# T3
ax.fill_between(x_smooth[:110], y_smooth[:110], bedrock[:110],
                color='0.75', alpha=0.7, hatch='...')
ax.text(50, 61, 'T3', fontsize=15, fontweight='bold', ha='center')
ax.text(50, 46, '洪积物', fontsize=9, ha='center')
ax.text(50, 40, '(据矿所\n办公楼)', fontsize=7, ha='center', style='italic', color='0.3')

# T2
ax.fill_between(x_smooth[130:240], y_smooth[130:240], bedrock[130:240],
                color='0.78', alpha=0.7, hatch='...')
ax.text(190, 37, 'T2', fontsize=15, fontweight='bold', ha='center')
ax.text(190, 24, '洪积物', fontsize=9, ha='center')

# T1
ax.fill_between(x_smooth[270:400], y_smooth[270:400], bedrock[270:400],
                color='0.82', alpha=0.7, hatch='..')
ax.text(345, 17, 'T1', fontsize=15, fontweight='bold', ha='center')
ax.text(345, 7, '细砂', fontsize=9, ha='center')

# 周口河
ax.fill_between(x_smooth[430:], y_smooth[430:], -25, color='0.5', alpha=0.6)
ax.text(510, -2, '周口河', fontsize=12, ha='center', fontweight='bold')

# 169高地
ax.annotate('169高地', xy=(540, y_smooth[450]), xytext=(540, 18),
            fontsize=9, ha='center',
            arrowprops=dict(arrowstyle='->', color='gray', lw=1.2))

# 产状 115度
ax.text(560, -7, '115°', fontsize=9, color='darkred', fontweight='bold')

# 比例尺
ax.plot([15, 95], [-22, -22], 'k-', linewidth=2)
ax.plot([15, 15], [-21, -23], 'k-', linewidth=1.5)
ax.plot([95, 95], [-21, -23], 'k-', linewidth=1.5)
ax.text(55, -24, '0    40    80 m', ha='center', fontsize=9)

# 图例
legend = [
    mpatches.Patch(facecolor='0.75', alpha=0.7, label='洪积物 (T3, T2)'),
    mpatches.Patch(facecolor='0.82', alpha=0.7, label='细砂 (T1)'),
    mpatches.Patch(facecolor='0.65', alpha=0.3, label='基岩'),
    mpatches.Patch(facecolor='0.5', alpha=0.6, label='河床沉积'),
]
ax.legend(handles=legend, loc='lower right', fontsize=8)

ax.set_title('图2-13 周口店三级阶地剖面示意图', fontsize=13, fontweight='bold', pad=12)
ax.set_xlabel('水平距离 / m', fontsize=10)
ax.set_ylabel('高程 / m', fontsize=10)
ax.set_xlim(-5, 620)
ax.set_ylim(-30, 70)
ax.set_yticks(np.arange(-20, 80, 20))
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('output/fig2-13_三级阶地剖面.png', dpi=200, bbox_inches='tight')
plt.close()
print('图2-13 完成')
