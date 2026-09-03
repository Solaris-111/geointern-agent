"""Clean up full_transcript.md: fix OCR errors, remove clutter, add section markers."""
import re
from pathlib import Path

TRANSCRIPT = Path(r"D:\geointern-agent\field_notebooks\周口店\full_transcript.md")
BACKUP = Path(r"D:\geointern-agent\field_notebooks\周口店\full_transcript_backup.md")

# Backup original
import shutil
shutil.copy(TRANSCRIPT, BACKUP)
print(f"Backup: {BACKUP}")

with open(TRANSCRIPT, 'r', encoding='utf-8') as f:
    content = f.read()

# ============================================================
# 1. Fix title
# ============================================================
content = content.replace(
    "# 野簿完整转录（峨眉山  + 周口店）",
    "# 野簿完整转录\n\n> 峨眉山 · 北戴河 · 周口店"
)

# ============================================================
# 2. Remove double separators
# ============================================================
content = re.sub(r'---\n\n---', '---', content)
# Clean up triple+ dashes at section ends
content = re.sub(r'\n---\n---\n', '\n---\n', content)

# ============================================================
# 3. Remove printed notebook headers (野簿印刷页眉)
# ============================================================
content = re.sub(r'\n中华人民共和国[ 　]*部?\n', '\n', content)
content = re.sub(r'\n中华人民共和国[ 　]*\n部[ 　]*\n', '\n', content)

# ============================================================
# 4. Remove AI hallucinated sketch descriptions
# ============================================================
# Pattern: [素描图描述：...], [图中为...], [图示为...], [图中...], （素描图描述）... etc.
content = re.sub(
    r'\n\[素描图描述：[^\]]*\][ \t]*\n?',
    '\n[素描图，详见原照片]\n',
    content
)
content = re.sub(
    r'\n\[图中为[^\]]*\][ \t]*\n?',
    '\n[素描图，详见原照片]\n',
    content
)
content = re.sub(
    r'\n\[图示为[^\]]*\][ \t]*\n?',
    '\n[素描图，详见原照片]\n',
    content
)
content = re.sub(
    r'\n\[左侧[^\]]*素描[^\]]*\][ \t]*\n?',
    '\n[素描图，详见原照片]\n',
    content
)
content = re.sub(
    r'\n\[图中[^\]]*素描图[^\]]*\]\n?',
    '\n[素描图，详见原照片]\n',
    content
)
content = re.sub(
    r'\n\[右页[^\]]*\]\n?',
    '',
    content
)
# Remove "（注：右侧页面内容不完整，部分字迹模糊）"
content = content.replace(
    '（注：右侧页面内容不完整，部分字迹模糊）',
    ''
)
# Remove standalone "（素描图描述）"
content = re.sub(r'\n（素描图描述）\n', '\n[素描图]\n', content)

# ============================================================
# 5. Fix place name OCR errors
# ============================================================
replacements = [
    # Place names
    ('待音电站', '清音电站'),
    ('龙门铜电站', '龙门洞电站'),
    ('龙门石园电站', '龙门洞电站'),
    ('四龙山', '回龙山'),
    ('掩断山', '挖断山'),
    ('万岩寺', '万年寺'),
    ('青音湖', '清音阁'),
    ('黄港大桥', '黄湾大桥'),
    ('石门石同向家店', '龙门洞向家店 [?]'),
    ('黄院东山梁237高地', '黄院东山梁 237高地'),
    ('双高坡', '双高坡 [?]'),

    # Stratigraphic names
    ('气东川组', '东川组'),
    ('露口坡组', '雷口坡组'),
    ('徐家河组', '须家河组'),
    ('富厄坝组', '雷口坡组'),

    # Sedimentary structures
    ('鱼荷模', '重荷模'),
    ('鱼脊棱', '沟模'),
    ('鱼眼构造', '鸟眼构造'),
    ('付养层理', '包卷层理'),
    ('火造构造', '火焰构造'),
    ('鱼脊模', '重荷模 [?]'),

    # Local names
    ('普贤段', '普贤船'),
    ('鲁贤船', '普贤船'),
    ('鲁贤缸', '普贤船 [?]'),
    ('普贤缸', '普贤船'),
    ('普贤段', '普贤船'),

    # Stratigraphic codes for 峨眉山
    ('P₃c', 'P₂β [?]'),  # 峨眉山玄武岩 correct code
    ('P₃e', 'P₂β [?]'),
    ('P₂e', 'P₂β'),

    # Rock/mineral names
    ('长在山组', '长龙山组'),
    ('元甲山组', '亮甲山组'),

    # Route numbers
    ('路线号 Lb', '路线号 L06'),
    ('路线号 Lb\n', '路线号 L06\n'),

    # Dates
    ('2027年', '2026年'),

    # Misc
    ('清日析分界面', '清晰分界面 [?]'),
    ('鱼骨状交错层理', '交错层理'),
    ('鱼骨状', '鱼骨状 [?]'),
    ('四溪沟', '四溪沟 [?]'),
    ('四溪组', '四溪沟剖面 [?]'),
    ('本川组', '东川组'),
]

for old, new in replacements:
    content = content.replace(old, new)

# ============================================================
# 6. Add section markers between实习区
# ============================================================

# 峨眉山 starts at the beginning
content = content.replace(
    '## IMG20260803162415.jpg',
    '# 一、峨眉山\n\n## IMG20260803162415.jpg'
)

# 北戴河 section: between IMG20260803162637.jpg and IMG20260803162703.jpg
# Find the boundary: after L05 路线小结, before 周口店 L06
content = content.replace(
    '## IMG20260803162637.jpg',
    '# 二、北戴河\n\n## IMG20260803162637.jpg'
)

# 周口店 section
content = content.replace(
    '## IMG20260803162703.jpg',
    '# 三、周口店\n\n## IMG20260803162703.jpg'
)

# Add L06 sub-header (day1 already has detailed transcript)
content = content.replace(
    '路线号 L06\n',
    '路线号 L06（已另有 day1 详细转录）\n'
)

# ============================================================
# 7. Clean up blank lines
# ============================================================
# Reduce triple+ blank lines to double
content = re.sub(r'\n{4,}', '\n\n\n', content)

# ============================================================
# 8. Mark unclear pages
# ============================================================
# Pages that are obviously garbled / too sparse
sparse_pages = {
    'IMG20260803162602.jpg': '[本页几乎空白，仅印刷页眉]',
    'IMG20260803162444.jpg': '[本页内容碎片化，详见原照片]',
}
for fname, note in sparse_pages.items():
    pattern = re.compile(
        r'(## ' + re.escape(fname) + r'\n\n).*?(?=\n---\n## )',
        re.DOTALL
    )
    content = pattern.sub(r'\1' + note + '\n', content)

# Write cleaned file
with open(TRANSCRIPT, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Cleaned: {TRANSCRIPT}")
print(f"Backup at: {BACKUP}")
