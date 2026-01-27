#!/usr/bin/env python3
"""Fix name/location inconsistencies in Volume 2 EN chapters."""

import re
from pathlib import Path

WORK_DIR = Path("WORK/貴族令嬢。俺にだけなつく2_20260120_20f7/EN")

# Replacements to make (order matters!)
REPLACEMENTS = [
    ("Beleth Centford", "Beret Sandford"),
    ("Beleth Sanford", "Beret Sandford"),
    ("Beleth-sama", "Beret-sama"),
    ("Beleth", "Beret"),
    ("Rayvelwarts", "Ravelwarts"),
    ("Ravenwarts", "Ravelwarts"),
]

def fix_file(filepath):
    """Apply replacements to a single file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    for old, new in REPLACEMENTS:
        content = content.replace(old, new)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    fixed_count = 0
    for md_file in sorted(WORK_DIR.glob("CHAPTER_*.md")):
        if fix_file(md_file):
            print(f"✅ Fixed: {md_file.name}")
            fixed_count += 1
        else:
            print(f"⚪ No changes: {md_file.name}")
    
    print(f"\n📊 Fixed {fixed_count} files")
    
    # Verify
    print("\n🔍 Verification:")
    errors = []
    for md_file in sorted(WORK_DIR.glob("CHAPTER_*.md")):
        content = md_file.read_text(encoding='utf-8')
        for old, _ in REPLACEMENTS:
            if old in content:
                count = content.count(old)
                errors.append(f"  ❌ {md_file.name}: '{old}' found {count}x")
    
    if errors:
        print("⚠️  Remaining errors:")
        for err in errors[:10]:
            print(err)
    else:
        print("✅ All corrections verified! No errors remain.")
        
        # Count correct usages
        beret_files = sum(1 for f in WORK_DIR.glob("CHAPTER_*.md") if "Beret" in f.read_text())
        ravelwarts_files = sum(1 for f in WORK_DIR.glob("CHAPTER_*.md") if "Ravelwarts" in f.read_text())
        print(f"\n📈 Correct usage:")
        print(f"  'Beret' appears in {beret_files} files")
        print(f"  'Ravelwarts' appears in {ravelwarts_files} files")

if __name__ == "__main__":
    main()
