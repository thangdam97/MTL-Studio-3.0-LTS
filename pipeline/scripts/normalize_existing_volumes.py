#!/usr/bin/env python3
"""
Normalize image filenames in existing EPUB work directories.

This script renames images to the standardized format:
- cover.jpg
- kuchie-001.jpg, kuchie-002.jpg, ...
- illust-001.jpg, illust-002.jpg, ...

Usage:
    python3 normalize_existing_volumes.py --dry-run          # Preview changes
    python3 normalize_existing_volumes.py --apply            # Apply changes
    python3 normalize_existing_volumes.py --volume-id 033f --apply  # Specific volume
"""

import json
import shutil
import argparse
from pathlib import Path
from typing import Dict, List, Tuple

WORK_DIR = Path("/Users/damminhthang/Documents/WORK/AI_MODULES/MTL_STUDIO/pipeline/WORK")

def normalize_filename(image_type: str, index: int, original_ext: str = ".jpg") -> str:
    """Generate standardized filename (same logic as ImageExtractor)."""
    if image_type == "cover":
        return f"cover{original_ext}"
    elif image_type == "kuchie":
        return f"kuchie-{index+1:03d}{original_ext}"
    elif image_type == "illustration":
        return f"illust-{index+1:03d}{original_ext}"
    return f"unknown-{index+1:03d}{original_ext}"

def normalize_volume(vol_dir: Path, dry_run: bool = True) -> Tuple[int, int]:
    """
    Normalize image filenames in a single volume.
    
    Returns:
        Tuple of (files_renamed, errors)
    """
    manifest_path = vol_dir / "manifest.json"
    if not manifest_path.exists():
        return (0, 1)
    
    # Read manifest
    with open(manifest_path) as f:
        manifest = json.load(f)
    
    assets = manifest.get('assets', {})
    vol_id = manifest.get('volume_id', vol_dir.name)
    
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Processing: {vol_id[:60]}")
    print("-" * 70)
    
    files_renamed = 0
    errors = 0
    updated_manifest = False
    
    # Normalize kuchie
    kuchie_list = assets.get('kuchie', [])
    if kuchie_list:
        kuchie_dir = vol_dir / "assets" / "kuchie"
        new_kuchie_list = []
        
        for i, old_name in enumerate(kuchie_list):
            old_path = kuchie_dir / old_name
            if not old_path.exists():
                print(f"  ⚠️  Missing: {old_name}")
                errors += 1
                new_kuchie_list.append(old_name)
                continue
            
            ext = Path(old_name).suffix
            new_name = normalize_filename("kuchie", i, ext)
            new_path = kuchie_dir / new_name
            
            if old_name != new_name:
                print(f"  {'[DRY] ' if dry_run else ''}Kuchie: {old_name} -> {new_name}")
                if not dry_run:
                    old_path.rename(new_path)
                files_renamed += 1
                updated_manifest = True
            
            new_kuchie_list.append(new_name)
        
        assets['kuchie'] = new_kuchie_list
    
    # Normalize illustrations
    illust_list = assets.get('illustrations', [])
    if illust_list:
        illust_dir = vol_dir / "assets" / "illustrations"
        new_illust_list = []
        
        for i, old_name in enumerate(illust_list):
            old_path = illust_dir / old_name
            if not old_path.exists():
                print(f"  ⚠️  Missing: {old_name}")
                errors += 1
                new_illust_list.append(old_name)
                continue
            
            ext = Path(old_name).suffix
            new_name = normalize_filename("illustration", i, ext)
            new_path = illust_dir / new_name
            
            if old_name != new_name:
                print(f"  {'[DRY] ' if dry_run else ''}Illust: {old_name} -> {new_name}")
                if not dry_run:
                    old_path.rename(new_path)
                files_renamed += 1
                updated_manifest = True
            
            new_illust_list.append(new_name)
        
        assets['illustrations'] = new_illust_list
    
    # Update manifest if changes were made
    if updated_manifest and not dry_run:
        # Create backup
        backup_path = manifest_path.with_suffix('.json.bak')
        shutil.copy2(manifest_path, backup_path)
        print(f"  ✅ Created backup: {backup_path.name}")
        
        # Write updated manifest
        manifest['assets'] = assets
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        print(f"  ✅ Updated manifest.json")
    
    return (files_renamed, errors)

def main():
    parser = argparse.ArgumentParser(description="Normalize image filenames in EPUB work directories")
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without applying')
    parser.add_argument('--apply', action='store_true', help='Apply normalization changes')
    parser.add_argument('--volume-id', type=str, help='Normalize specific volume by ID')
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.apply:
        print("ERROR: Must specify either --dry-run or --apply")
        parser.print_help()
        return 1
    
    dry_run = args.dry_run
    
    print("=" * 70)
    print(f"IMAGE FILENAME NORMALIZATION {'(DRY RUN)' if dry_run else '(APPLY)'}")
    print("=" * 70)
    
    # Find volumes to process
    if args.volume_id:
        # Find volume by partial ID
        volumes = [d for d in WORK_DIR.iterdir() 
                   if d.is_dir() and args.volume_id in d.name]
        if not volumes:
            print(f"ERROR: No volume found matching ID: {args.volume_id}")
            return 1
    else:
        # Process all volumes
        volumes = [d for d in WORK_DIR.iterdir() 
                   if d.is_dir() and not d.name.startswith('.')]
    
    print(f"\nFound {len(volumes)} volume(s) to process")
    
    total_renamed = 0
    total_errors = 0
    
    for vol_dir in sorted(volumes):
        renamed, errors = normalize_volume(vol_dir, dry_run)
        total_renamed += renamed
        total_errors += errors
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Files {'to be ' if dry_run else ''}renamed: {total_renamed}")
    print(f"Errors: {total_errors}")
    
    if dry_run:
        print("\n⚠️  This was a DRY RUN. No files were changed.")
        print("   Run with --apply to apply changes.")
    else:
        print("\n✅ Normalization complete!")
        print("   Manifest backups saved as manifest.json.bak")
    
    print("=" * 70)
    
    return 0

if __name__ == "__main__":
    exit(main())
