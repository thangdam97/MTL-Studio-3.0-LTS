#!/usr/bin/env python3
"""Sync metadata_en from metadata_en.json to manifest.json"""

import json
from pathlib import Path

work_dir = Path.cwd()

# Load correct metadata_en.json
with open(work_dir / 'metadata_en.json', 'r', encoding='utf-8') as f:
    correct_metadata_en = json.load(f)

# Load manifest.json
with open(work_dir / 'manifest.json', 'r', encoding='utf-8') as f:
    manifest = json.load(f)

# Replace metadata_en in manifest with correct data
manifest['metadata_en'] = correct_metadata_en

# Save updated manifest
with open(work_dir / 'manifest.json', 'w', encoding='utf-8') as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print("✓ Replaced manifest.json metadata_en section")
print(f"  Title: {correct_metadata_en['title_en']}")
print(f"  Chapters: {len(correct_metadata_en['chapters'])}")
print(f"  First: {correct_metadata_en['chapters'][0]['id']} - {correct_metadata_en['chapters'][0]['title_en']}")
print(f"  Last: {correct_metadata_en['chapters'][-1]['id']} - {correct_metadata_en['chapters'][-1]['title_en']}")
