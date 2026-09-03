"""图2-6 黄院东山梁地层手剖面图"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(1, 1, figsize=(16, 8))

# ===== 地形线 =====
x_terrain = np.array([0, 80, 160, 240, 300, 350, 400, 450, 520, 580, 640, 720, 780, 850, 920, 1000,
                       1060, 1120, 1180, 1240, 1300])
y_terrain = np.array([160, 140, 180, 220, 260, 275, 250, 210, 240, 270, 290, 250, 220, 190, 170, 200,
                       230, 260, 240, 200, 180])

# 平滑地形
from scipy.interpolate import interp1d
f_terrain = interp1d(x_terrain, y_terrain, kind='cubic')
x_smooth = np.linspace(0, 1300, 300)
y_smooth = f_terrain(x_smooth)

ax.plot(x_smooth, y_smooth, 'k-', linewidth=1.5)
ax.fill_between(x_smooth, y_smooth, -10, color='0.92', alpha=0.3)

# 高地标记
high_points = [
    (240, 220, '229高地'),
    (520, 240, '285高地'),
    (580, 270, '281高地'),
]
for x, y, label in high_points:
    ax.plot(x, y, 'k^', markersize=6)
    ax.text(x, y + 12, label, ha='center', fontsize=8, fontweight='bold')

# ===== 地层分界线 (从上到下) =====
strata = [
    # (底部z, 顶部z大致跟随地形, 地层代号, 岩性, 颜色, 花纹)
    {'code': 'Qy', 'name': '景儿峪组', 'lith': '大理岩/钙质板岩', 'z_top': 0, 'z_base': -55, 'color': '#E8DCC8', 'hatch': '//'},
    {'code': 'Qbc', 'name': '长龙山组', 'lith': '变质石英砂岩', 'z_base': -79, 'color': '#D4C5A0', 'hatch': '..'},
    {'code': 'Qbx', 'name': '下马岭组', 'lith': '千枚岩/板岩', 'z_base': -240, 'color': '#C8B890', 'hatch': '---'},
    {'code': 'C₁mn', 'name': '马家沟组', 'lith': '灰岩', 'z_base': -440, 'color': '#A0C8D0', 'hatch': '||'},
    {'code': 'C₂h', 'name': '张夏组', 'lith': '灰岩', 'z_base': -476, 'color': '#8DB8C0', 'hatch': '++'},
    {'code': 'C₂x', 'name': '徐庄组', 'lith': '灰岩', 'z_base': -517, 'color': '#7AA8B0', 'hatch': 'xx'},
    {'code': 'C₂f', 'name': '凤山组', 'lith': '砂岩/页岩', 'z_base': -592, 'color': '#C0B090', 'hatch': '..'},
    {'code': 'O₁m', 'name': '马家沟组(上)', 'lith': '灰岩', 'z_base': -792, 'color': '#90B8C0', 'hatch': '\\\\'},
]

# 计算地层顶部 - 对于每层，顶部要么是上一层的底部，要么是地形线
current_base = 0
for s in strata:
    s['z_top'] = current_base
    current_base = s['z_base']

# 绘制地层
for s in strata:
    # 在地形线以下绘制地层条带
    z_top_adj = s['z_top']
    z_base_adj = s['z_base']

    # 每层在剖面上的表现
    layer_y = np.full_like(x_smooth, z_top_adj)
    # 根据地层倾斜微调
    ax.fill_between(x_smooth, z_top_adj, z_base_adj, color=s['color'], alpha=0.5, hatch=s['hatch'], edgecolor='0.5', linewidth=0.2)

    # 标签
    mid_z = (z_top_adj + z_base_adj) / 2
    ax.text(650, mid_z, f"{s['code']} {s['name']}\n{s['lith']}", ha='left', fontsize=7, va='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='gray'))

# ===== 产状标注 =====
attitudes = [
    (100, -30, '∠30°', 'Qbx'),
    (250, -55, '∠25°', 'Qbc'),
    (400, -80, '∠20°', 'Qy'),
    (550, -170, '∠25°', 'C₂f'),
    (700, -200, '∠30°', 'C₂x'),
    (850, -250, '∠25°', 'C₂h'),
    (1050, -350, '∠20°', 'O₁m'),
]
for x, z, label, code in attitudes:
    # 画小段倾斜线
    ax.plot([x - 15, x + 15], [z + 5, z - 5], 'r-', linewidth=1)
    ax.text(x + 20, z, f'{code} {label}', fontsize=7, color='red')

# ===== 断层 =====
# 285高地附近断层
fault_x = 540
ax.plot([fault_x - 10, fault_x + 10, fault_x], [260, 220, -600], 'k-', linewidth=2)
ax.plot([fault_x - 5, fault_x + 5], [260, 250], 'k-', linewidth=1)
ax.plot([fault_x - 5, fault_x + 5], [220, 210], 'k-', linewidth=1)
# 断层箭头
ax.annotate('', xy=(fault_x + 5, 230), xytext=(fault_x - 5, 240),
            arrowprops=dict(arrowstyle='->', color='k', lw=1.5))
ax.text(fault_x + 15, 235, '断层', fontsize=8, color='red', fontweight='bold')

# 第二处断层
fault2_x = 800
ax.plot([fault2_x, fault2_x - 5, fault2_x + 15], [180, 130, -250], 'k-', linewidth=2)
ax.text(fault2_x + 20, 140, '断层', fontsize=8, color='red', fontweight='bold')

# 第三处
fault3_x = 350
ax.plot([fault3_x, fault3_x + 10, fault3_x - 5], [230, 180, -40], 'k-', linewidth=2)

# ===== 比例尺 =====
ax.plot([20, 120], [-10, -10], 'k-', linewidth=2)
ax.plot([20, 20], [-8, -12], 'k-', linewidth=1.5)
ax.plot([120, 120], [-8, -12], 'k-', linewidth=1.5)
ax.text(70, -15, '100 m', ha='center', fontsize=9)

# 垂直比例尺
ax.text(1250, -5, '垂直比例尺 1:1000', fontsize=8, style='italic', rotation=90, va='bottom')
ax.text(1250, -40, '水平比例尺 1:10000', fontsize=8, style='italic', rotation=90, va='bottom')

# ===== 图例 =====
legend_elements = [
    mpatches.Patch(facecolor='#E8DCC8', alpha=0.6, label='大理岩/钙质板岩'),
    mpatches.Patch(facecolor='#D4C5A0', alpha=0.6, label='变质石英砂岩'),
    mpatches.Patch(facecolor='#C8B890', alpha=0.6, label='千枚岩/板岩'),
    mpatches.Patch(facecolor='#A0C8D0', alpha=0.6, label='灰岩'),
    mpatches.Patch(facecolor='#C0B090', alpha=0.6, label='砂岩/页岩'),
]
ax.legend(handles=legend_elements, loc='upper right', fontsize=7, ncol=2, title='图例')

# ===== 设置 =====
ax.set_title('图2-6 黄院东山梁地层手剖面图', fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('水平距离', fontsize=10)
ax.set_ylabel('高程 h / m', fontsize=10)
ax.set_xlim(0, 1320)
ax.set_ylim(-800, 320)
ax.set_yticks(np.arange(-800, 400, 100))
ax.grid(axis='y', alpha=0.2)

# 方向指示
ax.annotate('剖面方向: 近东西向', xy=(1000, 300), fontsize=9, style='italic')

plt.tight_layout()
plt.savefig('output/fig2-6_黄院东山梁地层剖面.png', dpi=200, bbox_inches='tight')
plt.close()
print('图2-6 完成')
