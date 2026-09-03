"""Fix: add import re to _auto_rhythm."""
with open('section_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = 'from lithology_patterns import LITHOLOGY_PATTERNS, LITHOLOGY_COLORS'
new = 'import re\n        from lithology_patterns import LITHOLOGY_PATTERNS, LITHOLOGY_COLORS'
content = content.replace(old, new)

with open('section_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Done")
