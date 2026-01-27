#!/usr/bin/env python3
"""
Fix VN filename inconsistencies in existing volumes.

This script:
1. Renames VN folder files from _EN.md to _VN.md (if they have _EN suffix)
2. Updates manifest.json vn_file and translated_file fields accordingly
3. Handles volumes with no suffix by adding _VN suffix

Usage:
    python fix_vn_filenames.py                    # Dry run (show what would change)
    python fix_vn_filenames.py --apply            # Actually apply changes
    python fix_vn_filenames.py --volume <id>      # Fix specific volume only
"""

import json
import os
import re
import sys
from pathlib import Path

# Get WORK directory
SCRIPT_DIR = Path(__file__).parent
PIPELINE_DIR = SCRIPT_DIR.parent
WORK_DIR = PIPELINE_DIR / "WORK"


def find_volumes_to_fix():
    """Find volumes with VN folders that need filename fixes."""
    volumes_to_fix = []
    
    for vol_dir in WORK_DIR.iterdir():
        if not vol_dir.is_dir():
            continue
            
        vn_dir = vol_dir / "VN"
        manifest_path = vol_dir / "manifest.json"
        
        if not vn_dir.exists() or not manifest_path.exists():
            continue
        
        # Check if VN folder has files
        vn_files = list(vn_dir.glob("CHAPTER_*.md"))
        if not vn_files:
            continue
        
        # Check filename patterns
        has_en_suffix = any("_EN.md" in f.name for f in vn_files)
        has_vn_suffix = any("_VN.md" in f.name for f in vn_files)
        has_no_suffix = any(re.match(r"CHAPTER_\d+\.md$", f.name) for f in vn_files)
        
        # Needs fix if:
        # - Has _EN suffix (should be _VN)
        # - Has no suffix (should have _VN)
        needs_fix = has_en_suffix or has_no_suffix
        
        if needs_fix:
            volumes_to_fix.append({
                "path": vol_dir,
                "vn_dir": vn_dir,
                "manifest_path": manifest_path,
                "has_en_suffix": has_en_suffix,
                "has_no_suffix": has_no_suffix,
                "files": vn_files,
            })
    
    return volumes_to_fix


def fix_volume(vol_info, dry_run=True):
    """Fix filenames in a single volume."""
    vol_path = vol_info["path"]
    vn_dir = vol_info["vn_dir"]
    manifest_path = vol_info["manifest_path"]
    
    print(f"\n{'='*60}")
    print(f"Volume: {vol_path.name}")
    print(f"{'='*60}")
    
    # Load manifest
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    changes = []
    
    # Process each VN file
    for vn_file in sorted(vol_info["files"]):
        old_name = vn_file.name
        
        # Determine new name
        if "_EN.md" in old_name:
            new_name = old_name.replace("_EN.md", "_VN.md")
        elif re.match(r"CHAPTER_\d+\.md$", old_name):
            new_name = old_name.replace(".md", "_VN.md")
        else:
            continue  # Already correct
        
        if old_name == new_name:
            continue
        
        new_path = vn_dir / new_name
        
        changes.append({
            "old_name": old_name,
            "new_name": new_name,
            "old_path": vn_file,
            "new_path": new_path,
        })
        
        if dry_run:
            print(f"  [DRY] Would rename: {old_name} → {new_name}")
        else:
            vn_file.rename(new_path)
            print(f"  [OK] Renamed: {old_name} → {new_name}")
    
    # Update manifest
    manifest_changed = False
    for chapter in manifest.get("chapters", []):
        old_translated = chapter.get("translated_file", "")
        old_vn = chapter.get("vn_file", "")
        
        # Fix translated_file
        if "_EN.md" in old_translated:
            new_translated = old_translated.replace("_EN.md", "_VN.md")
            if dry_run:
                print(f"  [DRY] Manifest translated_file: {old_translated} → {new_translated}")
            chapter["translated_file"] = new_translated
            manifest_changed = True
        elif re.match(r"CHAPTER_\d+\.md$", old_translated):
            new_translated = old_translated.replace(".md", "_VN.md")
            if dry_run:
                print(f"  [DRY] Manifest translated_file: {old_translated} → {new_translated}")
            chapter["translated_file"] = new_translated
            manifest_changed = True
        
        # Fix vn_file
        if old_vn:
            if "_EN.md" in old_vn:
                new_vn = old_vn.replace("_EN.md", "_VN.md")
                if dry_run:
                    print(f"  [DRY] Manifest vn_file: {old_vn} → {new_vn}")
                chapter["vn_file"] = new_vn
                manifest_changed = True
            elif re.match(r"CHAPTER_\d+\.md$", old_vn):
                new_vn = old_vn.replace(".md", "_VN.md")
                if dry_run:
                    print(f"  [DRY] Manifest vn_file: {old_vn} → {new_vn}")
                chapter["vn_file"] = new_vn
                manifest_changed = True
    
    # Save manifest
    if manifest_changed and not dry_run:
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        print(f"  [OK] Updated manifest.json")
    
    return len(changes)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix VN filename inconsistencies")
    parser.add_argument("--apply", action="store_true", help="Actually apply changes (default: dry run)")
    parser.add_argument("--volume", "-v", type=str, help="Fix specific volume only (by ID or partial name)")
    
    args = parser.parse_args()
    dry_run = not args.apply
    
    if dry_run:
        print("\n" + "="*60)
        print("DRY RUN MODE - No changes will be made")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("APPLY MODE - Changes will be made")
        print("="*60)
    
    # Find volumes to fix
    volumes = find_volumes_to_fix()
    
    if args.volume:
        volumes = [v for v in volumes if args.volume in v["path"].name]
    
    if not volumes:
        print("\nNo volumes found that need fixing.")
        return
    
    print(f"\nFound {len(volumes)} volumes to fix:")
    for v in volumes:
        suffix_type = []
        if v["has_en_suffix"]:
            suffix_type.append("_EN.md")
        if v["has_no_suffix"]:
            suffix_type.append("no suffix")
        print(f"  - {v['path'].name} ({', '.join(suffix_type)})")
    
    # Process each volume
    total_changes = 0
    for vol_info in volumes:
        changes = fix_volume(vol_info, dry_run=dry_run)
        total_changes += changes
    
    print(f"\n{'='*60}")
    print(f"Summary: {total_changes} file renames {'would be' if dry_run else 'were'} applied")
    print(f"{'='*60}")
    
    if dry_run and total_changes > 0:
        print("\nTo apply changes, run:")
        print("  python fix_vn_filenames.py --apply")


if __name__ == "__main__":
    main()
