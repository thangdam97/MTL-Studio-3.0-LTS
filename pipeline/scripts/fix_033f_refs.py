#!/usr/bin/env python3
"""
Fix chapter image references to match normalized filenames.
Maps old filenames (p023.jpg) to new normalized filenames (illust-001.jpg).
"""

import json
import re
from pathlib import Path
from typing import Dict

def fix_volume_033f():
    """Fix image references in volume 033f."""
    vol_dir = Path("/Users/damminhthang/Documents/WORK/AI_MODULES/MTL_STUDIO/pipeline/WORK/学年一の金髪碧眼美少女に勉強を教えることになりました（ブレイブ文庫）１_20260118_033f")
    
    manifest_path = vol_dir / "manifest.json"
    with open(manifest_path) as f:
        manifest = json.load(f)
    
    # Create mapping from old to new filenames
    # Based on the assets section which is already normalized
    old_to_new = {
        "p023.jpg": "illust-001.jpg",
        "p048.jpg": "illust-002.jpg",
        "p107.jpg": "illust-003.jpg",
        "p144.jpg": "illust-004.jpg",
        "p201.jpg": "illust-005.jpg",
        "p213.jpg": "illust-006.jpg",
        "p224.jpg": "illust-007.jpg",
    }
    
    print("=" * 70)
    print("FIXING IMAGE REFERENCES FOR VOLUME 033f")
    print("=" * 70)
    
    # Update chapter markdown files
    en_dir = vol_dir / "EN"
    total_updates = 0
    
    for md_file in en_dir.glob("CHAPTER_*.md"):
        content = md_file.read_text(encoding='utf-8')
        original_content = content
        file_updates = 0
        
        for old_name, new_name in old_to_new.items():
            if old_name in content:
                content = content.replace(
                    f'src="../assets/illustrations/{old_name}"',
                    f'src="../assets/illustrations/{new_name}"'
                )
                if content != original_content:
                    file_updates += 1
                    print(f"  {md_file.name}: {old_name} -> {new_name}")
                    original_content = content
        
        if file_updates > 0:
            md_file.write_text(content, encoding='utf-8')
            total_updates += file_updates
    
    # Update manifest chapter illustrations
    manifest_updates = 0
    for chapter in manifest.get('chapters', []):
        illust_list = chapter.get('illustrations', [])
        if illust_list:
            new_illust_list = []
            for old_name in illust_list:
                if old_name in old_to_new:
                    new_name = old_to_new[old_name]
                    new_illust_list.append(new_name)
                    manifest_updates += 1
                    print(f"  Manifest {chapter['id']}: {old_name} -> {new_name}")
                else:
                    new_illust_list.append(old_name)
            chapter['illustrations'] = new_illust_list
    
    if manifest_updates > 0:
        # Backup manifest
        backup_path = manifest_path.with_suffix('.json.bak2')
        import shutil
        shutil.copy2(manifest_path, backup_path)
        
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        print(f"\n  ✅ Created backup: {backup_path.name}")
        print(f"  ✅ Updated manifest.json")
    
    total_updates += manifest_updates
    
    print("\n" + "=" * 70)
    print(f"Total updates: {total_updates}")
    print("=" * 70)
    
    return total_updates

if __name__ == "__main__":
    fix_volume_033f()
