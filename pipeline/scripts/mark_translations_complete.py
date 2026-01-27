#!/usr/bin/env python3
"""Mark all chapters as translated in manifest."""

import json
from datetime import datetime
from pathlib import Path
import sys

def main():
    work_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    manifest_path = work_dir / 'manifest.json'
    
    # Load manifest
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    # Update translator state
    manifest['pipeline_state']['translator']['status'] = 'completed'
    manifest['pipeline_state']['translator']['chapters_completed'] = len(manifest['chapters'])
    manifest['pipeline_state']['translator']['timestamp'] = datetime.now().isoformat()
    
    # Update all chapters to completed
    for chapter in manifest['chapters']:
        chapter['translation_status'] = 'completed'
    
    # Save manifest
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Marked {len(manifest['chapters'])} chapters as completed")
    print(f"  Translator status: {manifest['pipeline_state']['translator']['status']}")
    print(f"  Chapters completed: {manifest['pipeline_state']['translator']['chapters_completed']}/{manifest['pipeline_state']['translator']['chapters_total']}")

if __name__ == '__main__':
    main()
