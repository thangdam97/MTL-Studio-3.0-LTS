#!/usr/bin/env python3
"""
Fix manifest.json to use normalized illustration filenames.

The manifest currently lists original EPUB filenames (m003.jpg, p011.jpg)
but the actual files in assets/ have been normalized (illust-001.jpg).

This script updates the manifest to match the actual filenames.
"""

import json
import shutil
from pathlib import Path

volume_dir = Path("/Users/damminhthang/Documents/WORK/AI_MODULES/MTL_STUDIO/pipeline/WORK/負けヒロインと俺が付き合っていると周りから勘違いされ、幼馴染みと修羅場になった 1_20260118_07ca")

manifest_path = volume_dir / "manifest.json"
assets_illust_dir = volume_dir / "assets" / "illustrations"
assets_kuchie_dir = volume_dir / "assets" / "kuchie"

print("="*70)
print("MANIFEST FILENAME FIX")
print("="*70)

# Load manifest
with open(manifest_path, 'r', encoding='utf-8') as f:
    manifest = json.load(f)

print("\n[1] CURRENT STATE:")
original_illustrations = manifest.get("assets", {}).get("illustrations", [])
original_kuchie = manifest.get("assets", {}).get("kuchie", [])

print(f"   Manifest lists {len(original_illustrations)} illustrations")
print(f"   Manifest lists {len(original_kuchie)} kuchie")

# Get actual files
actual_illustrations = sorted([f.name for f in assets_illust_dir.glob("*.jpg")])
actual_kuchie = sorted([f.name for f in assets_kuchie_dir.glob("*.jpg")])

print(f"\n   Actual files: {len(actual_illustrations)} illustrations")
print(f"   Actual files: {len(actual_kuchie)} kuchie")

# Update manifest
print("\n[2] UPDATING MANIFEST:")
manifest["assets"]["illustrations"] = actual_illustrations
manifest["assets"]["kuchie"] = actual_kuchie

print(f"   ✓ Updated illustrations list to {len(actual_illustrations)} normalized filenames")
print(f"   ✓ Updated kuchie list to {len(actual_kuchie)} normalized filenames")

# Show sample
print("\n[3] SAMPLE CHANGES:")
print("   Illustrations:")
for orig, new in list(zip(sorted(original_illustrations), actual_illustrations))[:5]:
    print(f"     {orig} → {new}")
if len(actual_illustrations) > 5:
    print(f"     ... and {len(actual_illustrations) - 5} more")

print("\n   Kuchie:")
for orig, new in list(zip(sorted(original_kuchie), actual_kuchie))[:5]:
    print(f"     {orig} → {new}")
if len(actual_kuchie) > 5:
    print(f"     ... and {len(actual_kuchie) - 5} more")

# Save backup
backup_path = manifest_path.with_suffix('.json.bak')
shutil.copy2(manifest_path, backup_path)
print(f"\n[4] BACKUP CREATED:")
print(f"   {backup_path}")

# Save updated manifest
with open(manifest_path, 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print(f"\n[5] MANIFEST UPDATED:")
print(f"   {manifest_path}")

print("\n" + "="*70)
print("✓ MANIFEST FIX COMPLETE")
print("="*70)
print("\nNext step: Rebuild EPUB with Phase 4")
print("  python mtl.py phase4 07ca")
print("="*70 + "\n")
