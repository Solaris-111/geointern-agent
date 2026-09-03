"""图5-1 164背斜联合剖面图"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

fig = plt.figure(figsize=(14, 10))

# ===== 上部：横剖面 =====
ax1 = plt.subplot(2, 1, 1)

# 地形线 - 背斜隆起
x_cross = np.linspace(-600, 600, 300)
# 模拟背斜地表形态
y_cross = 50 + 80 * np.exp(-(x_cross / 300)**2) + 5 * np.sin(x_cross / 50)

# 地表线
ax1.plot(x_cross, y_cross, 'k-', linewidth=1.5)
ax1.fill_between(x_cross, y_cross, -200, color='0.9', alpha=0.3)

# 背斜核部 - O₁m 马家沟组灰岩
# 褶皱轴面
fold_axis = 0  # 背斜核部在x=0

# 绘制地层: O₁m 核部, C₂b 两翼
# 上翼线 (背斜顶部形态)
z_fold_top = -50 - 60 * np.exp(-(x_cross / 250)**2)
z_O1m_base = -120 - 50 * np.exp(-(x_cross / 280)**2)
z_C2b_base = -200 - 30 * np.exp(-(x_cross / 300)**2)

# O₁m 灰岩 - 核部
ax1.fill_between(x_cross, y_cross - 5, z_O1m_base, color='#B0D0D8', alpha=0.6, hatch='||||', edgecolor='0.4', linewidth=0.1)
ax1.text(-80, -30, 'O₁m\n马家沟组\n灰岩', ha='center', fontsize=8, fontweight='bold', va='center',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

# C₂b 本溪组 - 两翼
# 左翼
ax1.fill_between(x_cross, z_O1m_base, z_C2b_base, color='#D0C8A0', alpha=0.5, hatch='----', edgecolor='0.4', linewidth=0.1)
ax1.text(-350, -160, 'C₂b\n本溪组\n白云岩', ha='center', fontsize=8, va='center',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
# 右翼
ax1.text(350, -160, 'C₂b\n本溪组\n白云岩', ha='center', fontsize=8, va='center',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

# 产状标注
attitudes_upper = [
    (-400, -10, '∠10°∠21°'),
    (400, -10, '∠150°∠14°'),
    (0, -230, '∠246°∠29°'),
]
for x, z, label in attitudes_upper:
    sx = np.cos(np.radians(30)) * 25
    sy = np.sin(np.radians(30)) * 8
    if x < 0:
        sx = -sx
    ax1.plot([x - sx, x + sx], [z - 5, z + 5], 'r-', linewidth=1.2)
    ax1.text(x + (15 if x < 400 else -50), z + 8, label, fontsize=7, color='red')

# 观测点标注
ax1.plot(0, -80, 'ko', markersize=6)
ax1.text(0, -72, 'D₁S₀₂', ha='center', fontsize=7, color='blue')
ax1.plot(-300, -130, 'ko', markersize=5)
ax1.text(-300, -122, 'D₁S₀₁', ha='center', fontsize=7, color='blue')
ax1.plot(300, -130, 'ko', markersize=5)
ax1.text(300, -122, 'D₁S₀₃', ha='center', fontsize=7, color='blue')

# 背斜轴面虚线
ax1.plot([0, 0], [60, -250], 'k--', linewidth=1, alpha=0.5)

# 背斜标签
ax1.annotate('164背斜', xy=(0, 55), xytext=(80, 70), fontsize=11, ha='center', fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='gray', lw=1.2),
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))

# 比例尺
bar_x = x_cross[-1] - 150
ax1.plot([bar_x, bar_x + 100], [-180, -180], 'k-', linewidth=2)
ax1.plot([bar_x, bar_x], [-178, -182], 'k-', linewidth=1)
ax1.plot([bar_x + 100, bar_x + 100], [-178, -182], 'k-', linewidth=1)
ax1.text(bar_x + 50, -185, '500 m', ha='center', fontsize=9)

# 方向
ax1.annotate('S →', xy=(x_cross[-1] + 30, 30), fontsize=10, fontweight='bold')

# 图例
legend_upper = [
    mpatches.Patch(facecolor='#B0D0D8', alpha=0.6, label='灰岩 O₁m'),
    mpatches.Patch(facecolor='#D0C8A0', alpha=0.5, label='白云岩 C₂b'),
]
ax1.legend(handles=legend_upper, loc='lower left', fontsize=8)

ax1.set_title('164背斜联合剖面图 — 横剖面', fontsize=11, fontweight='bold')
ax1.set_ylabel('高程 / m', fontsize=9)
ax1.set_xlim(-650, 650)
ax1.set_ylim(-250, 110)
ax1.set_yticks(np.arange(-200, 120, 50))
ax1.grid(axis='y', alpha=0.2)

# ===== 下部：纵剖面 =====
ax2 = plt.subplot(2, 1, 2)

# 地形线
x_long = np.linspace(-500, 500, 300)
y_long = 30 + 25 * np.exp(-(x_long / 350)**2) + 3 * np.sin(x_long / 60)

ax2.plot(x_long, y_long, 'k-', linewidth=1.5)
ax2.fill_between(x_long, y_long, -120, color='0.9', alpha=0.3)

# 地层
z_top_long = -20 - 30 * np.exp(-(x_long / 280)**2)
z_mid_long = -50 - 20 * np.exp(-(x_long / 300)**2)
z_bot_long = -80 - 10 * np.exp(-(x_long / 320)**2)

ax2.fill_between(x_long, y_long - 3, z_top_long, color='#B0D0D8', alpha=0.5, hatch='||||', edgecolor='0.4', linewidth=0.1)
ax2.fill_between(x_long, z_top_long, z_mid_long, color='#C0C8B0', alpha=0.4, hatch='....', edgecolor='0.4', linewidth=0.1)
ax2.fill_between(x_long, z_mid_long, z_bot_long, color='#D0C8A0', alpha=0.4, hatch='----', edgecolor='0.4', linewidth=0.1)

# 标签
ax2.text(-100, -35, 'O₁m 灰岩', fontsize=8, ha='center')
ax2.text(-200, -65, 'C₂b 白云岩', fontsize=8, ha='center')
ax2.text(150, -55, 'C₂b 白云岩', fontsize=8, ha='center')

# 产状
ax2.plot([-150, -100], [-45, -55], 'r-', linewidth=1.2)
ax2.text(-140, -40, '∠88°∠25°', fontsize=7, color='red')
ax2.plot([200, 250], [-40, -50], 'r-', linewidth=1.2)
ax2.text(210, -35, '∠215°∠29°', fontsize=7, color='red')

# 连接虚线
for label, ax_obj in [('上部横剖面', ax1), ('下部纵剖面', ax2)]:
    pass  # Connected by figure layout

ax2.set_title('164背斜联合剖面图 — 纵剖面', fontsize=11, fontweight='bold')
ax2.set_xlabel('水平距离', fontsize=9)
ax2.set_ylabel('高程 / m', fontsize=9)
ax2.set_xlim(-550, 550)
ax2.set_ylim(-100, 70)
ax2.set_yticks(np.arange(-100, 80, 25))
ax2.grid(axis='y', alpha=0.2)

fig.suptitle('图5-1 164背斜联合剖面图', fontsize=14, fontweight='bold', y=0.98)

plt.tight_layout()
plt.savefig('output/fig5-1_164背斜联合剖面.png', dpi=200, bbox_inches='tight')
plt.close()
print('图5-1 完成')
