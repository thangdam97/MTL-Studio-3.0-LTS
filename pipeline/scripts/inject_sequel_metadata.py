#!/usr/bin/env python3
"""
Standalone script to inject sequel metadata into manifest.json.

This script detects if a volume is a sequel, finds the previous volume,
loads its metadata_en.json, and merges character_names and glossary
into the current volume's manifest.json.

Usage:
    python inject_sequel_metadata.py <volume_id>
    
Example:
    python inject_sequel_metadata.py 貴族令嬢。俺にだけなつく2_20260120_2188
"""

import sys
import json
from pathlib import Path

# Add pipeline to path
pipeline_dir = Path(__file__).parent
sys.path.insert(0, str(pipeline_dir))

from pipeline.librarian.metadata_parser import (
    detect_sequel,
    find_previous_volume,
    load_previous_metadata,
    merge_metadata
)

def inject_sequel_metadata(volume_id: str, work_dir: Path = None) -> bool:
    """
    Inject sequel metadata into volume's manifest.json.
    
    Args:
        volume_id: Volume ID (directory name)
        work_dir: WORK directory (defaults to pipeline/WORK)
    
    Returns:
        True if metadata was injected, False otherwise
    """
    if work_dir is None:
        work_dir = pipeline_dir / 'WORK'
    
    volume_dir = work_dir / volume_id
    
    if not volume_dir.exists():
        print(f"❌ Volume directory not found: {volume_dir}")
        return False
    
    manifest_path = volume_dir / 'manifest.json'
    if not manifest_path.exists():
        print(f"❌ Manifest not found: {manifest_path}")
        return False
    
    print("=" * 70)
    print(f"SEQUEL METADATA INJECTION: {volume_id}")
    print("=" * 70)
    
    # Load manifest
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    title = manifest.get('metadata', {}).get('title', '')
    print(f"\nTitle: {title}")
    
    # Find OPF file
    opf_path = None
    epub_extracted = volume_dir / '_epub_extracted'
    for opf_file in epub_extracted.rglob('*.opf'):
        opf_path = opf_file
        break
    
    if not opf_path:
        print("❌ No OPF file found")
        return False
    
    # Detect sequel
    sequel_info = detect_sequel(title, opf_path)
    
    if not sequel_info:
        print("✓ Not a sequel - no previous volume metadata needed")
        return False
    
    series_title, volume_num = sequel_info
    print(f"✓ Detected sequel: '{series_title}' Volume {volume_num}")
    
    # Find previous volume
    previous_volume_dir = find_previous_volume(series_title, volume_num, work_dir)
    
    if not previous_volume_dir:
        print(f"⚠️  Previous volume not found for Volume {volume_num - 1}")
        return False
    
    print(f"✓ Found previous volume: {previous_volume_dir.name}")
    
    # Load previous metadata
    previous_metadata = load_previous_metadata(previous_volume_dir)
    
    if not previous_metadata['character_names'] and not previous_metadata['glossary']:
        print("⚠️  Previous volume has no metadata to inherit")
        return False
    
    # Get current volume's metadata (if any)
    current_metadata = {
        'character_names': manifest.get('metadata_en', {}).get('character_names', {}),
        'glossary': manifest.get('metadata_en', {}).get('glossary', {})
    }
    
    # Merge metadata
    merged = merge_metadata(previous_metadata, current_metadata)
    
    # Inject into manifest
    if 'metadata_en' not in manifest:
        manifest['metadata_en'] = {}
    
    manifest['metadata_en']['character_names'] = merged['character_names']
    manifest['metadata_en']['glossary'] = merged['glossary']
    
    # Save manifest
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Injected continuity data into manifest.json:")
    print(f"  - {len(merged['character_names'])} character names")
    print(f"  - {len(merged['glossary'])} glossary terms")
    
    # Also save to metadata_en.json if it exists
    metadata_en_path = volume_dir / 'metadata_en.json'
    if metadata_en_path.exists():
        with open(metadata_en_path, 'r', encoding='utf-8') as f:
            metadata_en = json.load(f)
        
        metadata_en['character_names'] = merged['character_names']
        metadata_en['glossary'] = merged['glossary']
        
        with open(metadata_en_path, 'w', encoding='utf-8') as f:
            json.dump(metadata_en, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Also updated metadata_en.json")
    
    print("\n" + "=" * 70)
    print("✓ SEQUEL METADATA INJECTION COMPLETE")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python inject_sequel_metadata.py <volume_id>")
        print("\nExample:")
        print("  python inject_sequel_metadata.py 貴族令嬢。俺にだけなつく2_20260120_2188")
        sys.exit(1)
    
    volume_id = sys.argv[1]
    success = inject_sequel_metadata(volume_id)
    sys.exit(0 if success else 1)
