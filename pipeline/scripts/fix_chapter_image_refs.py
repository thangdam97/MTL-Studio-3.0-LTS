#!/usr/bin/env python3
"""
Update chapter markdown files to use normalized image filenames.

This script updates image references in chapter markdown files to match
the normalized filenames (illust-XXX.jpg instead of pXXX.jpg).
"""

import json
import re
from pathlib import Path
from typing import Dict, List

WORK_DIR = Path("/Users/damminhthang/Documents/WORK/AI_MODULES/MTL_STUDIO/pipeline/WORK")

def create_filename_mapping(manifest: dict) -> Dict[str, str]:
    """Create mapping from old filenames to normalized filenames."""
    mapping = {}
    
    # Map illustrations
    illust_list = manifest.get('assets', {}).get('illustrations', [])
    for i, old_name in enumerate(illust_list):
        ext = Path(old_name).suffix
        new_name = f"illust-{i+1:03d}{ext}"
        mapping[old_name] = new_name
    
    # Map kuchie
    kuchie_list = manifest.get('assets', {}).get('kuchie', [])
    for i, old_name in enumerate(kuchie_list):
        ext = Path(old_name).suffix
        new_name = f"kuchie-{i+1:03d}{ext}"
        mapping[old_name] = new_name
    
    return mapping

def update_chapter_images(vol_dir: Path, mapping: Dict[str, str], dry_run: bool = True) -> int:
    """Update image references in chapter markdown files."""
    en_dir = vol_dir / "EN"
    if not en_dir.exists():
        return 0
    
    updates_made = 0
    
    for md_file in en_dir.glob("CHAPTER_*.md"):
        content = md_file.read_text(encoding='utf-8')
        original_content = content
        
        # Find all image tags
        img_pattern = re.compile(r'<img[^>]+src="\.\./(assets/illustrations|assets/kuchie)/([^"]+)"[^>]*>')
        
        def replace_image(match):
            nonlocal updates_made
            full_tag = match.group(0)
            img_type = match.group(1)  # assets/illustrations or assets/kuchie
            old_filename = match.group(2)
            
            if old_filename in mapping:
                new_filename = mapping[old_filename]
                new_tag = full_tag.replace(old_filename, new_filename)
                updates_made += 1
                print(f"    {md_file.name}: {old_filename} -> {new_filename}")
                return new_tag
            return full_tag
        
        content = img_pattern.sub(replace_image, content)
        
        if content != original_content and not dry_run:
            md_file.write_text(content, encoding='utf-8')
    
    return updates_made

def update_manifest_illustrations(manifest_path: Path, mapping: Dict[str, str], dry_run: bool = True) -> int:
    """Update illustration references in chapter metadata within manifest."""
    with open(manifest_path) as f:
        manifest = json.load(f)
    
    updates_made = 0
    
    for chapter in manifest.get('chapters', []):
        illust_list = chapter.get('illustrations', [])
        if illust_list:
            new_illust_list = []
            for old_name in illust_list:
                if old_name in mapping:
                    new_name = mapping[old_name]
                    new_illust_list.append(new_name)
                    updates_made += 1
                    print(f"    Manifest chapter {chapter['id']}: {old_name} -> {new_name}")
                else:
                    new_illust_list.append(old_name)
            chapter['illustrations'] = new_illust_list
    
    if updates_made > 0 and not dry_run:
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    return updates_made

def fix_volume_references(vol_dir: Path, dry_run: bool = True) -> int:
    """Fix image references in a single volume."""
    manifest_path = vol_dir / "manifest.json"
    if not manifest_path.exists():
        return 0
    
    with open(manifest_path) as f:
        manifest = json.load(f)
    
    vol_id = manifest.get('volume_id', vol_dir.name)
    
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Processing: {vol_id[:60]}")
    print("-" * 70)
    
    # Create mapping from manifest
    mapping = create_filename_mapping(manifest)
    
    if not mapping:
        print("  No mapping needed (already normalized)")
        return 0
    
    # Update chapter markdown files
    chapter_updates = update_chapter_images(vol_dir, mapping, dry_run)
    
    # Update manifest chapter illustrations
    manifest_updates = update_manifest_illustrations(manifest_path, mapping, dry_run)
    
    total_updates = chapter_updates + manifest_updates
    
    if total_updates == 0:
        print("  No updates needed")
    
    return total_updates

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Update chapter image references to normalized filenames")
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without applying')
    parser.add_argument('--apply', action='store_true', help='Apply changes')
    parser.add_argument('--volume-id', type=str, help='Fix specific volume by ID')
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.apply:
        print("ERROR: Must specify either --dry-run or --apply")
        parser.print_help()
        return 1
    
    dry_run = args.dry_run
    
    print("=" * 70)
    print(f"CHAPTER IMAGE REFERENCE FIX {'(DRY RUN)' if dry_run else '(APPLY)'}")
    print("=" * 70)
    
    # Find volumes to process
    if args.volume_id:
        volumes = [d for d in WORK_DIR.iterdir() 
                   if d.is_dir() and args.volume_id in d.name]
        if not volumes:
            print(f"ERROR: No volume found matching ID: {args.volume_id}")
            return 1
    else:
        volumes = [d for d in WORK_DIR.iterdir() 
                   if d.is_dir() and not d.name.startswith('.')]
    
    print(f"\nFound {len(volumes)} volume(s) to process")
    
    total_updates = 0
    
    for vol_dir in sorted(volumes):
        updates = fix_volume_references(vol_dir, dry_run)
        total_updates += updates
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total references {'to be ' if dry_run else ''}updated: {total_updates}")
    
    if dry_run:
        print("\n⚠️  This was a DRY RUN. No files were changed.")
        print("   Run with --apply to apply changes.")
    else:
        print("\n✅ References updated successfully!")
    
    print("=" * 70)
    
    return 0

if __name__ == "__main__":
    exit(main())
