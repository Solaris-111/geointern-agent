# -*- coding: utf-8 -*-
"""Simple DXF preview - geometry only, no CJK needed"""
import matplotlib.pyplot as plt
import numpy as np
import ezdxf

dxf_path = "d:/geointern-agent/output/fig2-1_section_v2.dxf"
doc = ezdxf.readfile(dxf_path)
msp = doc.modelspace()

fig, ax = plt.subplots(1, 1, figsize=(18, 8))
all_x, all_y = [], []

# Hatches
for hatch in msp.query('HATCH'):
    try:
        for path in hatch.paths:
            verts = None
            if hasattr(path, 'vertices'):
                verts = [(v.x, v.y) for v in path.vertices]
            elif hasattr(path, 'polyline_vertices'):
                verts = [(v.x, v.y) for v in path.polyline_vertices]
            if not verts or len(verts) < 3:
                continue
            xs, ys = zip(*verts)
            all_x.extend(xs); all_y.extend(ys)
            color_val = hatch.dxf.color
            if color_val == 2:
                fc = '#f5f0e0'
            elif color_val == 7:
                fc = '#e8e0d0'
            else:
                fc = '#f0ebe0'
            poly = plt.Polygon(list(zip(xs, ys)), closed=True,
                              facecolor=fc, edgecolor='#aaaaaa',
                              linewidth=0.2, alpha=0.6)
            ax.add_patch(poly)
    except:
        pass

# Terrain line
for pline in msp.query('LWPOLYLINE[layer=="TERRAIN"]'):
    pts = [(v[0], v[1]) for v in pline]
    if len(pts) >= 2:
        xs, ys = zip(*pts)
        all_x.extend(xs); all_y.extend(ys)
        ax.plot(xs, ys, 'k-', linewidth=2.5)

# Formation labels
for txt in msp.query('TEXT'):
    try:
        x, y = txt.dxf.insert.x, txt.dxf.insert.y
        text = txt.dxf.text
        ax.text(x, y, text, fontsize=6, ha='center', va='bottom',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))
    except:
        pass

# Contact markers
for circle in msp.query('CIRCLE'):
    try:
        cx, cy, r = circle.dxf.center.x, circle.dxf.center.y, circle.dxf.radius
        c = plt.Circle((cx, cy), r, fill=False, color='red', linewidth=1.5)
        ax.add_patch(c)
    except:
        pass

if all_x and all_y:
    ax.set_xlim(min(all_x) - 30, max(all_x) + 100)
    ax.set_ylim(min(all_y) - 50, max(all_y) + 50)

ax.set_xlabel('Distance (m)')
ax.set_ylabel('Elevation (m)')
ax.set_title('Fig.2-1 V2: Terrain from image + Qwen-VL boundaries')
ax.set_aspect('equal')

plt.tight_layout()
out = "d:/geointern-agent/output/fig2-1_v2_preview.png"
plt.savefig(out, dpi=150, bbox_inches='tight')
plt.close()
print("Preview saved:", out)
