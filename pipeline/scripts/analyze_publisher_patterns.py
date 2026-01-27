#!/usr/bin/env python3
"""
Analyze EPUB structure patterns across multiple publishers.
"""

import json
from pathlib import Path
from collections import defaultdict, Counter

def analyze_volumes():
    work_dir = Path("WORK")
    
    publishers = defaultdict(list)
    toc_formats = Counter()
    nav_patterns = Counter()
    image_patterns = []
    kuchie_volumes = []
    chapter_splits = []
    
    for volume_dir in work_dir.iterdir():
        if not volume_dir.is_dir() or not (volume_dir / "manifest.json").exists():
            continue
        
        try:
            with open(volume_dir / "manifest.json") as f:
                manifest = json.load(f)
            
            # Publisher tracking
            publisher = manifest.get("metadata", {}).get("publisher", "Unknown")
            title = manifest.get("metadata", {}).get("title_ja", volume_dir.name)
            publishers[publisher].append(title[:50])
            
            # TOC format
            toc_fmt = manifest.get("toc", {}).get("format", "unknown")
            toc_formats[toc_fmt] += 1
            
            # Navigation pattern
            toc_items = len(manifest.get("toc", {}).get("chapters", []))
            spine_items = manifest.get("spine", {}).get("total_items", 0)
            if spine_items > 0:
                nav_patterns[f"TOC:{toc_items} Spine:{spine_items}"] += 1
            
            # Image analysis
            illust_count = len(manifest.get("assets", {}).get("illustrations", []))
            kuchie_count = len(manifest.get("assets", {}).get("kuchie", []))
            
            if illust_count > 0 or kuchie_count > 0:
                image_patterns.append({
                    "volume": volume_dir.name[:40],
                    "illustrations": illust_count,
                    "kuchie": kuchie_count,
                    "total": illust_count + kuchie_count
                })
            
            if kuchie_count > 0:
                kuchie_volumes.append(volume_dir.name[:40])
            
            # Chapter structure
            chapters = manifest.get("chapters", [])
            if chapters:
                chapter_splits.append({
                    "volume": volume_dir.name[:40],
                    "chapters": len(chapters),
                    "avg_words": sum(ch.get("word_count", 0) for ch in chapters) // len(chapters) if chapters else 0
                })
        
        except Exception as e:
            print(f"Error processing {volume_dir.name}: {e}")
    
    return {
        "publishers": dict(publishers),
        "toc_formats": dict(toc_formats),
        "nav_patterns": dict(nav_patterns),
        "image_patterns": image_patterns,
        "kuchie_volumes": kuchie_volumes,
        "chapter_splits": chapter_splits,
        "total_volumes": sum(len(v) for v in publishers.values())
    }

if __name__ == "__main__":
    results = analyze_volumes()
    
    print("=" * 70)
    print("EPUB PUBLISHER PATTERN ANALYSIS")
    print("=" * 70)
    
    print(f"\n📚 Total Volumes Processed: {results['total_volumes']}")
    
    print("\n" + "=" * 70)
    print("PUBLISHERS")
    print("=" * 70)
    for pub, volumes in sorted(results["publishers"].items(), key=lambda x: -len(x[1])):
        print(f"\n{pub}: {len(volumes)} volume(s)")
        for vol in volumes[:3]:
            print(f"  • {vol}")
        if len(volumes) > 3:
            print(f"  ... and {len(volumes) - 3} more")
    
    print("\n" + "=" * 70)
    print("NAVIGATION FORMATS")
    print("=" * 70)
    print("\nTOC Formats:")
    for fmt, count in results["toc_formats"].items():
        print(f"  {fmt.upper()}: {count} volumes")
    
    print("\nNavigation Complexity:")
    for pattern, count in sorted(results["nav_patterns"].items())[:5]:
        print(f"  {pattern}: {count} volumes")
    
    print("\n" + "=" * 70)
    print("IMAGE ASSETS")
    print("=" * 70)
    print(f"\nKuchie (Character Art) Presence: {len(results['kuchie_volumes'])} volumes")
    if results["kuchie_volumes"]:
        for vol in results["kuchie_volumes"][:3]:
            print(f"  • {vol}")
    
    print("\nImage Distribution:")
    for img_data in sorted(results["image_patterns"], key=lambda x: -x["total"])[:5]:
        print(f"  {img_data['volume']}")
        print(f"    → {img_data['illustrations']} illustrations, {img_data['kuchie']} kuchie")
    
    print("\n" + "=" * 70)
    print("CHAPTER STRUCTURES")
    print("=" * 70)
    if results["chapter_splits"]:
        avg_chapters = sum(cs["chapters"] for cs in results["chapter_splits"]) / len(results["chapter_splits"])
        avg_words = sum(cs["avg_words"] for cs in results["chapter_splits"]) / len(results["chapter_splits"])
        
        print(f"\nAverage Chapters per Volume: {avg_chapters:.1f}")
        print(f"Average Words per Chapter: {avg_words:.0f}")
        
        print("\nSample Chapter Counts:")
        for cs in sorted(results["chapter_splits"], key=lambda x: -x["chapters"])[:5]:
            print(f"  {cs['volume']}: {cs['chapters']} chapters (~{cs['avg_words']} words/ch)")
    
    print("\n" + "=" * 70)
