"""Insert geological sketches into the Word report at figure references."""
import sys, io, re
from pathlib import Path
from PIL import Image
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DOCX_PATH = Path(r"C:\Users\asus\Desktop\1111 - 副本.docx")
OUT_PATH = Path(r"C:\Users\asus\Desktop\1111_带图件.docx")
SKETCH_DIR = Path(r"D:\geointern-agent\field_notebooks\周口店\图片")

# Figure mapping: figure_number -> (filename, need_rotation)
# All 28 sketches from the notebook
FIGURE_MAP = {
    # 峨眉山 L01-L05
    '图1-1': ('IMG20260803162420.jpg', True),
    '图1-2': ('IMG20260803162426.jpg', False),
    '图1-3': ('IMG20260803162431.jpg', True),
    '图1-4': ('IMG20260803162444.jpg', True),
    '图2-1': ('IMG20260803162455.jpg', False),
    '图2-2': ('IMG20260803162500.jpg', True),
    '图2-3': ('IMG20260803162505.jpg', True),
    '图2-4': ('IMG20260803162510.jpg', False),
    '图2-5': ('IMG20260803162519.jpg', True),
    '图2-6': ('IMG20260803162533.jpg', True),
    '图4-1': ('IMG20260803162616.jpg', False),
    '图4-2': ('IMG20260803162622.jpg', False),
    '图4-3': ('IMG20260803162631.jpg', True),
    '图5-1': ('IMG20260803162640.jpg', False),
    '图5-2': ('IMG20260803162651.jpg', True),
    '图5-3': ('IMG20260803162700.jpg', False),
    # 周口店 L06-L12
    '图6-1': ('IMG20260803162711.jpg', True),
    '图6-2': ('IMG20260803162731.jpg', True),
    '图6-3': ('IMG20260803162742.jpg', False),
    '图7-1': ('IMG20260803162759.jpg', True),
    '图7-2': ('IMG20260803162811.jpg', False),
    '图7-3': ('IMG20260803162829.jpg', False),
    '图8-3': ('IMG20260803162856.jpg', False),
    '图8-4': ('IMG20260803162902.jpg', True),
    '图9-2': ('IMG20260803162916.jpg', False),
    '图9-3': ('IMG20260803162926.jpg', False),
    '图9-4': ('IMG20260803162942.jpg', False),
    '图10-1': ('IMG20260803163011.jpg', False),
}

def prepare_sketch(filename, rotate=False):
    """Load sketch, rotate if needed, resize, return BytesIO."""
    img = Image.open(SKETCH_DIR / filename)
    if rotate:
        img = img.rotate(-90, expand=True)  # Rotate CW for landscape sketches
    # Resize to fit Word page width (~15cm)
    max_w = 1600
    ratio = max_w / img.size[0]
    img = img.resize((int(img.size[0]*ratio), int(img.size[1]*ratio)))
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    buf = io.BytesIO()
    img.save(buf, 'JPEG', quality=70)
    buf.seek(0)
    # Return dimensions in cm
    w_cm = img.size[0] / 100  # ~16cm max
    h_cm = img.size[1] / 100
    return buf, w_cm, h_cm

# Read docx
doc = Document(DOCX_PATH)

# Find all figure reference paragraphs
# Pattern: (图X-X) or 图X-X or （图X-X）
insertions = []
inserted_figs = set()
for i, p in enumerate(doc.paragraphs):
    text = p.text
    for fig_name, (filename, rotate) in FIGURE_MAP.items():
        if fig_name in text and fig_name not in inserted_figs:
            insertions.append((i, fig_name, filename, rotate))
            inserted_figs.add(fig_name)

# Find the "参考文献" paragraph as insertion point for remaining figures
refs_para_idx = None
for i, p in enumerate(doc.paragraphs):
    if p.text.strip().startswith('## 参考文献'):
        refs_para_idx = i
        break

# For figures not found in text, insert before参考文献 as appendix
appendix_figs = {}
for fig_name, (filename, rotate) in FIGURE_MAP.items():
    if fig_name not in inserted_figs:
        appendix_figs[fig_name] = (filename, rotate)

if appendix_figs and refs_para_idx:
    # Add appendix header before the remaining figures
    # We'll insert them all at the参考文献 position
    for fig_name, (filename, rotate) in appendix_figs.items():
        insertions.append((refs_para_idx, fig_name, filename, rotate))
    print(f"附录插入: {len(appendix_figs)} 张")

# Sort: text-matched first, appendix last
text_insertions = [(idx, fn, fname, rot) for idx, fn, fname, rot in insertions
                   if fn not in appendix_figs]
appendix_insertions = [(idx, fn, fname, rot) for idx, fn, fname, rot in insertions
                       if fn in appendix_figs]
insertions = text_insertions + appendix_insertions

# Report remaining unfound
found_figs = set(fn for _, fn, _, _ in insertions)
still_missing = set(FIGURE_MAP.keys()) - found_figs
if still_missing:
    print(f"仍无法定位: {sorted(still_missing)}")
print(f"总插入: {len(insertions)} 张")

# Process in reverse order (so inserting paragraphs doesn't shift indices)
inserted = 0
for para_idx, fig_name, filename, rotate in reversed(insertions):
    para = doc.paragraphs[para_idx]

    # Prepare sketch image
    try:
        img_buf, w_cm, h_cm = prepare_sketch(filename, rotate)
    except Exception as e:
        print(f"  ERROR loading {filename}: {e}")
        continue

    # Add the sketch inline after the reference paragraph
    # We'll add the image to the current paragraph as an inline shape
    # First add a line break
    run = para.add_run('\n')
    # Add the image
    run = para.add_run()
    try:
        run.add_picture(img_buf, width=Cm(min(w_cm, 15)))
        inserted += 1
        # Add caption
        caption_run = para.add_run(f'\n{fig_name}  {Path(filename).stem}')
        caption_run.font.size = Pt(8)
        caption_run.font.color.rgb = RGBColor(100, 100, 100)
        caption_run.font.italic = True
    except Exception as e:
        print(f"  ERROR inserting {filename}: {e}")

print(f"插入图件: {inserted} 张")

# Save
doc.save(str(OUT_PATH))
size_mb = OUT_PATH.stat().st_size / (1024*1024)
print(f"输出: {OUT_PATH}")
print(f"大小: {size_mb:.1f} MB")
