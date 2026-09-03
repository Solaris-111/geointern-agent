"""图5-5 下马岭组叠瓦状断层剖面"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(1, 1, figsize=(14, 8))

# 地表线
x_surface = np.linspace(0, 800, 200)
y_surface = 20 + 15 * np.sin(x_surface / 100) + 3 * np.sin(x_surface / 30)
y_surface = y_surface - y_surface[0] + 60

ax.plot(x_surface, y_surface, 'k-', linewidth=1.8)
ax.fill_between(x_surface, y_surface, -150, color='0.93', alpha=0.3)

# ===== 地层和断层 =====

# 马家沟组 O₁m - 灰岩 (最南/右侧)
om_x = np.linspace(520, 780, 100)
ax.fill_between(om_x, -5, -100, color='#A8C8D4', alpha=0.6, hatch='||||', edgecolor='0.3', linewidth=0.1)
ax.text(650, -50, 'O₁m\n马家沟组\n灰岩', ha='center', fontsize=8, fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.85))

# 寒武系 ∈
cam_x = np.linspace(400, 560, 100)
ax.fill_between(cam_x, -5, -100, color='#C0B8A0', alpha=0.5, hatch='....', edgecolor='0.3', linewidth=0.1)
ax.text(480, -50, '∈\n寒武系', ha='center', fontsize=8, fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.85))

# 长龙山组 Qbc
qbc_x = np.linspace(280, 430, 100)
ax.fill_between(qbc_x, -5, -100, color='#D0C8A8', alpha=0.5, hatch='..', edgecolor='0.3', linewidth=0.1)
ax.text(355, -50, 'Qbc\n长龙山组\n砂岩/页岩', ha='center', fontsize=8,
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.85))

# 下马岭组 Qbx
qbx_x = np.linspace(150, 310, 100)
ax.fill_between(qbx_x, -5, -100, color='#D8C898', alpha=0.5, hatch='---', edgecolor='0.3', linewidth=0.1)
ax.text(230, -50, 'Qbx\n下马岭组\n泥岩/砂岩', ha='center', fontsize=8,
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.85))

# 铁岭组 Jxt
jxt_x = np.linspace(30, 180, 100)
ax.fill_between(jxt_x, -5, -100, color='#C8B080', alpha=0.5, hatch='\\\\', edgecolor='0.3', linewidth=0.1)
ax.text(105, -50, 'Jxt\n铁岭组', ha='center', fontsize=8,
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.85))

# 洪水庄组 Jxh
jxh_x = np.linspace(-50, 60, 100)
ax.fill_between(jxh_x, -5, -100, color='#B8A870', alpha=0.5, hatch='//', edgecolor='0.3', linewidth=0.1)
ax.text(5, -50, 'Jxh\n洪水庄组', ha='center', fontsize=8,
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.85))

# ===== 断层 =====
# 正断层体系，倾向南(右)，高角度

faults = [
    (80, 60, 66, '∠66°', '断层1'),
    (210, 65, 60, '∠60°', '断层2'),
    (340, 62, 60, '∠60°', '断层3'),
    (470, 58, 56, '∠56°', '断层4'),
    (590, 55, 50, '∠50°', '断层5'),
]

for x_top, y_top, dip, label, name in faults:
    # 断层面: 倾向南(右)，倾角 dip
    dx = (150) * np.cos(np.radians(dip))
    dy = -(150) * np.sin(np.radians(dip))
    ax.plot([x_top - dx*0.1, x_top + dx*0.9], [y_top - dy*0.1, y_top + dy*0.9], 'k-', linewidth=2)

    # 断层箭头 (上盘下降方向)
    mid_x = x_top + dx * 0.4
    mid_y = y_top + dy * 0.4
    ax.annotate('', xy=(mid_x + 8, mid_y - 5), xytext=(mid_x - 5, mid_y + 3),
                arrowprops=dict(arrowstyle='->', color='k', lw=1.5))

    # 倾角标签
    ax.text(x_top + 5, y_top - 25, label, fontsize=7, color='red')

    # 断层名称
    ax.text(x_top - 15, y_top + 8, name, fontsize=7, color='blue')

# ===== 产状标注 =====
attitudes = [
    (100, 30, 'Jxt\n152°∠60°'),
    (250, 35, 'Qbx\n160°∠66°'),
    (370, 30, 'Qbc\n170°∠60°'),
    (520, 28, '∈\n175°∠55°'),
    (680, 25, 'O₁m\n185°∠27°'),
]
for x, y, label in attitudes:
    ax.text(x, y, label, fontsize=6, color='red', ha='center',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))

# ===== 断层带阴影 =====
for x_top, y_top, dip, _, _ in faults:
    dx = (150) * np.cos(np.radians(dip))
    dy = -(150) * np.sin(np.radians(dip))
    # 断层破碎带
    ax.fill_between([x_top - 8, x_top + 12], [y_top, y_top], [-100, -100],
                    color='0.5', alpha=0.15)

# ===== 叠瓦状标注 =====
ax.annotate('叠瓦状正断层系统', xy=(300, -90), xytext=(350, -130),
            fontsize=12, ha='center', fontweight='bold', color='darkred',
            arrowprops=dict(arrowstyle='->', color='darkred', lw=1.5),
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

# ===== 比例尺 =====
ax.plot([620, 720], [-145, -145], 'k-', linewidth=2)
ax.plot([620, 620], [-143, -147], 'k-', linewidth=1)
ax.plot([720, 720], [-143, -147], 'k-', linewidth=1)
ax.text(670, -148, '100 m', ha='center', fontsize=9)

# ===== 图例 =====
legend_elements = [
    mpatches.Patch(facecolor='#A8C8D4', alpha=0.6, label='灰岩 (O₁m)'),
    mpatches.Patch(facecolor='#D0C8A8', alpha=0.5, label='砂岩/页岩 (Qbc)'),
    mpatches.Patch(facecolor='#D8C898', alpha=0.5, label='泥岩/砂岩 (Qbx)'),
    mpatches.Patch(facecolor='#C8B080', alpha=0.5, label='火山/变质岩 (Jxt)'),
    mpatches.Patch(facecolor='#B8A870', alpha=0.5, label='千枚岩 (Jxh)'),
    plt.Line2D([0], [0], color='k', linewidth=2, label='正断层'),
]
ax.legend(handles=legend_elements, loc='lower left', fontsize=7, ncol=3,
          bbox_to_anchor=(0.02, -0.08))

# ===== 设置 =====
ax.set_title('图5-5 下马岭组叠瓦状正断层剖面', fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('水平距离', fontsize=10)
ax.set_ylabel('高程 / m', fontsize=10)
ax.set_xlim(-30, 810)
ax.set_ylim(-155, 80)
ax.set_yticks(np.arange(-150, 90, 30))
ax.grid(axis='y', alpha=0.2)

# 方向标注
ax.annotate('剖面走向: 170° (近东西向)\n断层倾向: S (南)', xy=(600, 60),
            fontsize=9, style='italic',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))

ax.text(400, -5, '比例尺 1:1000', fontsize=8, style='italic', ha='center')

plt.tight_layout()
plt.savefig('output/fig5-5_叠瓦状断层剖面.png', dpi=200, bbox_inches='tight')
plt.close()
print('图5-5 完成')
