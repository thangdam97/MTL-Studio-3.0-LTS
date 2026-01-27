#!/usr/bin/env python3
"""
Analyze image filenames across all existing EPUB work directories.
Generates a report of naming patterns and abnormalities.
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set

WORK_DIR = Path("/Users/damminhthang/Documents/WORK/AI_MODULES/MTL_STUDIO/pipeline/WORK")

def analyze_images():
    """Analyze all image files in work directories."""
    
    # Collect all image filenames
    all_images = {
        "cover": [],
        "kuchie": [],
        "illustrations": [],
        "unknown": []
    }
    
    # Pattern statistics
    pattern_stats = defaultdict(int)
    
    # Current patterns
    COVER_PATTERN = re.compile(r'^(cover|i-cover)\.jpe?g$', re.IGNORECASE)
    KUCHIE_PATTERN = re.compile(r'^(kuchie-|k|p00)\d+(-\d+)?\.jpe?g$', re.IGNORECASE)
    ILLUSTRATION_PATTERN = re.compile(r'^(i-|p)\d+\.jpe?g$', re.IGNORECASE)
    
    # Scan all volume directories
    volumes = [d for d in WORK_DIR.iterdir() if d.is_dir() and not d.name.startswith('.')]
    
    print(f"Scanning {len(volumes)} volumes...\n")
    
    for vol_dir in sorted(volumes):
        manifest_path = vol_dir / "manifest.json"
        if not manifest_path.exists():
            continue
            
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        assets = manifest.get('assets', {})
        vol_id = manifest.get('volume_id', vol_dir.name)
        
        # Analyze cover
        cover = assets.get('cover')
        if cover:
            all_images['cover'].append((vol_id, cover))
            if COVER_PATTERN.match(cover):
                pattern_stats['cover_standard'] += 1
            else:
                pattern_stats['cover_nonstandard'] += 1
        
        # Analyze kuchie
        kuchie_list = assets.get('kuchie', [])
        for k in kuchie_list:
            all_images['kuchie'].append((vol_id, k))
            if KUCHIE_PATTERN.match(k):
                pattern_stats['kuchie_standard'] += 1
            else:
                pattern_stats['kuchie_nonstandard'] += 1
        
        # Analyze illustrations
        illust_list = assets.get('illustrations', [])
        for ill in illust_list:
            all_images['illustrations'].append((vol_id, ill))
            
            # Check which patterns match
            matches = []
            if KUCHIE_PATTERN.match(ill):
                matches.append('kuchie')
            if ILLUSTRATION_PATTERN.match(ill):
                matches.append('illustration')
            
            if len(matches) == 0:
                pattern_stats['illust_no_match'] += 1
                all_images['unknown'].append((vol_id, ill))
            elif len(matches) == 1:
                pattern_stats[f'illust_{matches[0]}_only'] += 1
            else:
                pattern_stats['illust_ambiguous'] += 1
                print(f"⚠️  AMBIGUOUS: {ill} in {vol_id[:30]}... matches both patterns")
    
    return all_images, pattern_stats

def extract_filename_patterns(images: List[tuple]) -> Dict[str, int]:
    """Extract and count filename patterns."""
    patterns = defaultdict(int)
    
    for vol_id, filename in images:
        # Extract prefix pattern
        match = re.match(r'^([a-z-]+)', filename, re.IGNORECASE)
        if match:
            prefix = match.group(1)
            patterns[prefix] += 1
        else:
            patterns['<no_prefix>'] += 1
    
    return dict(sorted(patterns.items(), key=lambda x: x[1], reverse=True))

def main():
    print("=" * 70)
    print("IMAGE FILENAME ANALYSIS REPORT")
    print("=" * 70)
    print()
    
    all_images, pattern_stats = analyze_images()
    
    # Summary statistics
    print("SUMMARY STATISTICS")
    print("-" * 70)
    print(f"Total covers:        {len(all_images['cover'])}")
    print(f"Total kuchie:        {len(all_images['kuchie'])}")
    print(f"Total illustrations: {len(all_images['illustrations'])}")
    print(f"Unknown/unmatched:   {len(all_images['unknown'])}")
    print()
    
    # Pattern matching statistics
    print("PATTERN MATCHING STATISTICS")
    print("-" * 70)
    for key, count in sorted(pattern_stats.items()):
        print(f"{key:30s}: {count:4d}")
    print()
    
    # Kuchie filename patterns
    print("KUCHIE FILENAME PATTERNS")
    print("-" * 70)
    kuchie_patterns = extract_filename_patterns(all_images['kuchie'])
    for pattern, count in kuchie_patterns.items():
        print(f"{pattern:20s}: {count:4d}")
    print()
    
    # Illustration filename patterns
    print("ILLUSTRATION FILENAME PATTERNS")
    print("-" * 70)
    illust_patterns = extract_filename_patterns(all_images['illustrations'])
    for pattern, count in illust_patterns.items():
        print(f"{pattern:20s}: {count:4d}")
    print()
    
    # Unknown files
    if all_images['unknown']:
        print("UNKNOWN/UNMATCHED FILES")
        print("-" * 70)
        for vol_id, filename in all_images['unknown']:
            print(f"{filename:30s} in {vol_id[:40]}")
        print()
    
    # Sample filenames for each pattern
    print("SAMPLE FILENAMES BY TYPE")
    print("-" * 70)
    
    print("\nKuchie samples:")
    for vol_id, filename in all_images['kuchie'][:10]:
        print(f"  {filename}")
    
    print("\nIllustration samples:")
    for vol_id, filename in all_images['illustrations'][:15]:
        print(f"  {filename}")
    
    print()
    print("=" * 70)
    print("Analysis complete!")
    print("=" * 70)

if __name__ == "__main__":
    main()
