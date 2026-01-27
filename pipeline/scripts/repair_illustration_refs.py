#!/usr/bin/env python3
"""
Repair Script: Fix Illustration Filename References

PROBLEM:
- Librarian renames images: p011.jpg → illust-001.jpg
- But markdown files still reference: [ILLUSTRATION: p011.jpg]
- Builder generates: <img src="../Images/p011.jpg"> ← FILE NOT FOUND!
- Result: Corrupted EPUB with missing images

SOLUTION:
This script repairs existing volumes by:
1. Reading the manifest to get original filenames  
2. Mapping to actual normalized filenames in assets
3. Updating all markdown illustration references

Usage:
  python scripts/repair_illustration_refs.py VOLUME_ID
  python scripts/repair_illustration_refs.py --all
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.config import WORK_DIR, ILLUSTRATION_PLACEHOLDER_PATTERN


def build_filename_mapping(volume_dir: Path) -> Dict[str, str]:
    """
    Build mapping from original filenames to normalized filenames.
    
    Returns:
        Dict mapping original filename -> normalized filename
    """
    manifest_path = volume_dir / "manifest.json"
    if not manifest_path.exists():
        print(f"✗ Manifest not found: {manifest_path}")
        return {}
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    # Get original filenames from manifest
    original_illustrations = manifest.get("assets", {}).get("illustrations", [])
    original_kuchie = manifest.get("assets", {}).get("kuchie", [])
    
    # Get actual files in assets
    mapping = {}
    
    # Map illustrations
    assets_illust_dir = volume_dir / "assets" / "illustrations"
    if assets_illust_dir.exists():
        actual_files = sorted([f for f in assets_illust_dir.glob("*.jpg")])
        
        # Assume sorted order matches
        for i, (orig, actual) in enumerate(zip(sorted(original_illustrations), actual_files)):
            mapping[orig] = actual.name
            print(f"  {orig} → {actual.name}")
    
    # Map kuchie
    assets_kuchie_dir = volume_dir / "assets" / "kuchie"
    if assets_kuchie_dir.exists():
        actual_files = sorted([f for f in assets_kuchie_dir.glob("*.jpg")])
        
        for i, (orig, actual) in enumerate(zip(sorted(original_kuchie), actual_files)):
            mapping[orig] = actual.name
            print(f"  {orig} → {actual.name}")
    
    return mapping


def update_markdown_files(volume_dir: Path, filename_mapping: Dict[str, str], dry_run: bool = False):
    """Update illustration references in markdown files."""
    updated_files = []
    updated_count = 0
    
    # Dynamically find language directories (JP, EN, VN, etc.)
    # Look for directories that contain markdown files
    lang_dirs = [d for d in volume_dir.iterdir() 
                 if d.is_dir() 
                 and d.name.isupper() 
                 and len(d.name) == 2 
                 and list(d.glob("*.md"))]
    
    for md_dir in lang_dirs:
        
        for md_file in md_dir.glob("*.md"):
            try:
                content = md_file.read_text(encoding='utf-8')
                original_content = content
                file_updated = False
                
                # Find all illustration placeholders
                for match in re.finditer(ILLUSTRATION_PLACEHOLDER_PATTERN, content):
                    original_filename = match.group(1)
                    
                    # Check if we have a mapping for this filename
                    if original_filename in filename_mapping:
                        normalized_filename = filename_mapping[original_filename]
                        # Replace this specific occurrence
                        old_placeholder = match.group(0)
                        new_placeholder = f"[ILLUSTRATION: {normalized_filename}]"
                        content = content.replace(old_placeholder, new_placeholder)
                        updated_count += 1
                        file_updated = True
                
                # Write back if changed
                if content != original_content:
                    if not dry_run:
                        md_file.write_text(content, encoding='utf-8')
                    updated_files.append(md_file)
                    status = "[DRY-RUN]" if dry_run else "[UPDATED]"
                    print(f"    {status} {md_file.relative_to(volume_dir)}")
                    
            except Exception as e:
                print(f"    [ERROR] Failed to process {md_file.name}: {e}")
    
    return updated_files, updated_count


def repair_volume(volume_dir: Path, dry_run: bool = False):
    """Repair a single volume."""
    print(f"\n{'='*70}")
    print(f"REPAIRING: {volume_dir.name}")
    print(f"{'='*70}")
    
    # Build filename mapping
    print("\n[1] Building filename mapping...")
    mapping = build_filename_mapping(volume_dir)
    
    if not mapping:
        print("  ✗ No mapping found - volume may already be correct or has issues")
        return False
    
    print(f"  ✓ Found {len(mapping)} filename mappings")
    
    # Update markdown files
    print("\n[2] Updating markdown files...")
    updated_files, updated_count = update_markdown_files(volume_dir, mapping, dry_run)
    
    if updated_files:
        print(f"  ✓ Updated {updated_count} references in {len(updated_files)} files")
        if dry_run:
            print(f"  ℹ DRY RUN - no files were modified")
        return True
    else:
        print(f"  ✓ No updates needed - references already correct")
        return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Repair illustration filename references in volumes")
    parser.add_argument("volume_id", nargs="?", help="Volume ID to repair (or --all)")
    parser.add_argument("--all", action="store_true", help="Repair all volumes")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without modifying files")
    
    args = parser.parse_args()
    
    work_dir = Path(WORK_DIR)
    
    if args.all:
        print("Repairing all volumes...")
        volumes = [d for d in work_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
        
        repaired = 0
        for vol_dir in volumes:
            if repair_volume(vol_dir, args.dry_run):
                repaired += 1
        
        print(f"\n{'='*70}")
        print(f"SUMMARY: Repaired {repaired} of {len(volumes)} volumes")
        print(f"{'='*70}\n")
    
    elif args.volume_id:
        # Find volume directory
        vol_dir = None
        for candidate in work_dir.iterdir():
            if candidate.is_dir() and args.volume_id in candidate.name:
                vol_dir = candidate
                break
        
        if not vol_dir:
            print(f"✗ Volume not found: {args.volume_id}")
            print(f"  Looking in: {work_dir}")
            return 1
        
        repair_volume(vol_dir, args.dry_run)
    
    else:
        parser.print_help()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
