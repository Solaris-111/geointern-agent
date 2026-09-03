# -*- coding: utf-8 -*-
"""将DXF渲染为PNG预览图"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import ezdxf
import numpy as np

dxf_path = "d:/geointern-agent/output/fig2-1_section.dxf"
doc = ezdxf.readfile(dxf_path)
msp = doc.modelspace()

fig, ax = plt.subplots(1, 1, figsize=(18, 10))
ax.set_aspect('equal')

# Collect entities for bounds
all_x, all_y = [], []

# Draw hatches (FILLS layer)
for hatch in msp.query('HATCH[layer=="FILLS"]'):
    try:
        for path in hatch.paths:
            if hasattr(path, 'vertices'):
                verts = [(v.x, v.y) for v in path.vertices]
            elif hasattr(path, 'polyline_vertices'):
                verts = [(v.x, v.y) for v in path.polyline_vertices]
            else:
                continue
            if len(verts) < 3:
                continue
            xs, ys = zip(*verts)
            all_x.extend(xs)
            all_y.extend(ys)

            # Determine color
            color = hatch.dxf.color
            fc = '#e8e0d0'  # default
            if color == 2:
                fc = '#f5f0e0'  # yellow-ish base
            else:
                fc = '#f0ebe0'

            poly = plt.Polygon(list(zip(xs, ys)), closed=True,
                              facecolor=fc, edgecolor='#888888',
                              linewidth=0.3, alpha=0.7)
            ax.add_patch(poly)
    except Exception as e:
        pass

# Draw polylines (TERRAIN)
for pline in msp.query('LWPOLYLINE[layer=="TERRAIN"]'):
    try:
        pts = [(v[0], v[1]) for v in pline]
        if len(pts) < 2:
            continue
        xs, ys = zip(*pts)
        all_x.extend(xs)
        all_y.extend(ys)
        ax.plot(xs, ys, 'k-', linewidth=2.5, label='Terrain')
    except Exception as e:
        pass

# Draw lines
for line in msp.query('LINE'):
    try:
        xs = [line.dxf.start.x, line.dxf.end.x]
        ys = [line.dxf.start.y, line.dxf.end.y]
        ax.plot(xs, ys, 'k-', linewidth=1.0)
        all_x.extend(xs)
        all_y.extend(ys)
    except Exception as e:
        pass

# Draw text labels
for txt in msp.query('TEXT'):
    try:
        x, y = txt.dxf.insert.x, txt.dxf.insert.y
        text = txt.dxf.text
        ax.text(x, y, text, fontsize=7, ha='center', va='bottom')
    except Exception as e:
        pass

# Draw circles (contact markers)
for circle in msp.query('CIRCLE[layer=="BOUNDARIES"]'):
    try:
        c = plt.Circle((circle.dxf.center.x, circle.dxf.center.y),
                       circle.dxf.radius, fill=False, color='red', linewidth=1.5)
        ax.add_patch(c)
    except Exception as e:
        pass

# Set bounds
if all_x and all_y:
    ax.set_xlim(min(all_x) - 30, max(all_x) + 100)
    ax.set_ylim(min(all_y) - 50, max(all_y) + 50)

# Legend for lithologies
legend_patches = [
    mpatches.Patch(facecolor='#f0ebe0', edgecolor='gray', label='Ground'),
]
ax.legend(handles=legend_patches, loc='upper right', fontsize=8)

ax.set_xlabel('Distance (m)')
ax.set_ylabel('Elevation (m)')
ax.set_title('Fig 2-1: Bajiaozhai Yakou - Shuanmazhuang Qiao Section', fontsize=12)

plt.tight_layout()
out = "d:/geointern-agent/output/fig2-1_preview.png"
plt.savefig(out, dpi=150, bbox_inches='tight')
plt.close()
print("Preview saved:", out)
