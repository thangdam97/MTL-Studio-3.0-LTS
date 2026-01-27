#!/usr/bin/env python3
"""Analyze structure patterns across a light novel series."""

import json
import re
from pathlib import Path
from collections import defaultdict

def analyze_volume(work_dir: Path) -> dict:
    """Analyze a single volume's structure."""
    result = {
        'volume_id': work_dir.name,
        'exists': False,
        'images': {},
        'chapters': {},
        'spine_info': {},
        'pre_toc_pages': [],
        'orphan_illustrations': []
    }
    
    if not work_dir.exists():
        return result
    
    result['exists'] = True
    
    # Check manifest
    manifest_path = work_dir / "manifest.json"
    if manifest_path.exists():
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        result['chapters']['count'] = len(manifest.get('chapters', []))
        result['chapters']['ids'] = [ch['id'] for ch in manifest.get('chapters', [])]
        
        # Count illustrations in chapters
        illust_in_chapters = []
        for ch in manifest.get('chapters', []):
            for img in ch.get('illustrations', []):
                if not img.endswith('.png'):  # Skip gaiji
                    illust_in_chapters.append(img)
        result['chapters']['illustrations'] = illust_in_chapters
    
    # Check assets
    assets_dir = work_dir / "assets"
    if assets_dir.exists():
        if (assets_dir / "cover.jpg").exists():
            result['images']['cover'] = 1
        
        kuchie_dir = assets_dir / "kuchie"
        if kuchie_dir.exists():
            result['images']['kuchie'] = len(list(kuchie_dir.glob("*.jpg")))
        
        illust_dir = assets_dir / "illustrations"
        if illust_dir.exists():
            result['images']['illustrations'] = len(list(illust_dir.glob("*.jpg")))
    
    # Check extracted EPUB structure
    extracted_dir = work_dir / "_epub_extracted" / "item"
    if extracted_dir.exists():
        # Count all images in image folder
        image_dir = extracted_dir / "image"
        if image_dir.exists():
            all_images = list(image_dir.glob("*.jpg")) + list(image_dir.glob("*.png"))
            result['spine_info']['total_images'] = len(all_images)
            
            # Categorize
            cover_imgs = [f.name for f in all_images if re.match(r'(?:o_)?cover\.jpe?g', f.name, re.I)]
            kuchie_imgs = [f.name for f in all_images if re.match(r'(?:o_)?(?:kuchie[-_]\d+|k\d+|p00[1-9])(-\d+)?\.jpe?g', f.name, re.I)]
            illust_imgs = [f.name for f in all_images if re.match(r'(?:o_)?(?:i[-_]\d+|img[-_]p\d+|p0[1-9]\d+|p[1-9]\d+|m\d+)\.jpe?g', f.name, re.I)]
            gaiji_imgs = [f.name for f in all_images if f.suffix == '.png']
            other_imgs = [f.name for f in all_images if f.name not in cover_imgs + kuchie_imgs + illust_imgs + gaiji_imgs]
            
            result['spine_info']['cover_images'] = cover_imgs
            result['spine_info']['kuchie_images'] = kuchie_imgs
            result['spine_info']['illustration_images'] = illust_imgs
            result['spine_info']['gaiji_images'] = gaiji_imgs
            result['spine_info']['other_images'] = other_imgs
        
        # Check xhtml structure
        xhtml_dir = extracted_dir / "xhtml"
        if xhtml_dir.exists():
            p_files = sorted([f.name for f in xhtml_dir.glob("p-*.xhtml")])
            result['spine_info']['p_files_count'] = len(p_files)
            
            # Find pre-TOC pages (before first TOC entry)
            toc_path = work_dir / "toc.json"
            if toc_path.exists():
                with open(toc_path, 'r', encoding='utf-8') as f:
                    toc = json.load(f)
                
                # Find first story TOC entry
                first_story_file = None
                for nav in toc.get('nav_points', []):
                    label = nav['label'].lower()
                    if 'プロ' in label or '第' in label or 'chapter' in label:
                        # Extract filename
                        src = nav['content_src'].split('#')[0]
                        if '/' in src:
                            first_story_file = src.split('/')[-1]
                        break
                
                if first_story_file:
                    # Find pages before first story
                    for p_file in p_files:
                        if p_file == first_story_file:
                            break
                        # Check if it has images
                        p_path = xhtml_dir / p_file
                        content = p_path.read_text(encoding='utf-8')
                        img_match = re.search(r'xlink:href="[^"]*/(i-\d+\.jpg)"', content)
                        if img_match:
                            result['pre_toc_pages'].append({
                                'file': p_file,
                                'image': img_match.group(1)
                            })
    
    # Check for orphan illustrations (in spine_info but not in chapters)
    spine_illusts = set(result['spine_info'].get('illustration_images', []))
    chapter_illusts = set(result['chapters'].get('illustrations', []))
    result['orphan_illustrations'] = list(spine_illusts - chapter_illusts)
    
    return result


def main():
    work_dir = Path("WORK")
    series_pattern = "貴族令嬢"
    
    volumes = sorted([d for d in work_dir.iterdir() if d.is_dir() and series_pattern in d.name])
    
    print("=" * 80)
    print(f"SERIES STRUCTURE ANALYSIS: {series_pattern}")
    print("=" * 80)
    print(f"Found {len(volumes)} volumes\n")
    
    all_results = []
    
    for vol_dir in volumes:
        print(f"\n{'─' * 80}")
        print(f"VOLUME: {vol_dir.name}")
        print('─' * 80)
        
        result = analyze_volume(vol_dir)
        all_results.append(result)
        
        if not result['exists']:
            print("  ⚠️  Directory exists but no processed data found")
            continue
        
        # Images
        print(f"\n📷 IMAGES:")
        print(f"   Cover: {result['images'].get('cover', 0)}")
        print(f"   Kuchie: {result['images'].get('kuchie', 0)}")
        print(f"   Illustrations: {result['images'].get('illustrations', 0)}")
        
        # Chapters
        print(f"\n📖 CHAPTERS:")
        print(f"   Total chapters: {result['chapters'].get('count', 0)}")
        print(f"   Chapter IDs: {', '.join(result['chapters'].get('ids', [])[:5])}{'...' if len(result['chapters'].get('ids', [])) > 5 else ''}")
        print(f"   Illustrations in chapters: {len(result['chapters'].get('illustrations', []))}")
        if result['chapters'].get('illustrations'):
            for img in result['chapters'].get('illustrations', []):
                print(f"     - {img}")
        
        # Spine analysis
        if result['spine_info']:
            print(f"\n📚 SPINE ANALYSIS:")
            print(f"   Total images in EPUB: {result['spine_info'].get('total_images', 0)}")
            print(f"   Cover images: {len(result['spine_info'].get('cover_images', []))}")
            print(f"   Kuchie images: {len(result['spine_info'].get('kuchie_images', []))}")
            print(f"   Illustration images: {len(result['spine_info'].get('illustration_images', []))}")
            print(f"   Gaiji (special chars): {len(result['spine_info'].get('gaiji_images', []))}")
            print(f"   Other images: {len(result['spine_info'].get('other_images', []))}")
            
            if result['spine_info'].get('other_images'):
                print(f"     Other: {', '.join(result['spine_info']['other_images'])}")
        
        # Pre-TOC pages
        if result['pre_toc_pages']:
            print(f"\n⚠️  PRE-TOC IMAGE PAGES:")
            for page in result['pre_toc_pages']:
                print(f"   - {page['file']}: {page['image']}")
        
        # Orphan illustrations
        if result['orphan_illustrations']:
            print(f"\n⚠️  ORPHAN ILLUSTRATIONS (in EPUB but not in chapters):")
            for img in result['orphan_illustrations']:
                print(f"   - {img}")
    
    # Summary across all volumes
    print(f"\n\n{'=' * 80}")
    print("SERIES SUMMARY")
    print('=' * 80)
    
    total_kuchie = sum(r['images'].get('kuchie', 0) for r in all_results)
    total_illusts = sum(r['images'].get('illustrations', 0) for r in all_results)
    total_chapters = sum(r['chapters'].get('count', 0) for r in all_results)
    total_orphans = sum(len(r.get('orphan_illustrations', [])) for r in all_results)
    total_pre_toc = sum(len(r.get('pre_toc_pages', [])) for r in all_results)
    
    print(f"\nTotal across {len(volumes)} volumes:")
    print(f"  Kuchie pages: {total_kuchie}")
    print(f"  Story illustrations: {total_illusts}")
    print(f"  Chapters: {total_chapters}")
    print(f"  Orphan illustrations: {total_orphans}")
    print(f"  Pre-TOC image pages: {total_pre_toc}")
    
    # Patterns
    print(f"\n📊 PATTERNS:")
    has_pre_toc = [r['volume_id'] for r in all_results if r.get('pre_toc_pages')]
    has_orphans = [r['volume_id'] for r in all_results if r.get('orphan_illustrations')]
    
    if has_pre_toc:
        print(f"  ⚠️  Volumes with pre-TOC image pages: {len(has_pre_toc)}")
        for vid in has_pre_toc:
            print(f"     - {vid}")
    
    if has_orphans:
        print(f"  ⚠️  Volumes with orphan illustrations: {len(has_orphans)}")
        for vid in has_orphans:
            print(f"     - {vid}")
    
    if not has_pre_toc and not has_orphans:
        print(f"  ✅ No structural issues detected")
    
    print(f"\n{'=' * 80}")


if __name__ == "__main__":
    main()
