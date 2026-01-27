#!/usr/bin/env python3
"""Analyze rebuilt EPUB structure and verify illustration references."""

import zipfile
import re
from pathlib import Path

epub_path = Path("/Users/damminhthang/Documents/WORK/AI_MODULES/MTL_STUDIO/pipeline/OUTPUT/Everyone Thinks Im Dating the Losing Heroine Kicki_EN.epub")

print("="*70)
print("EPUB BUILD ANALYSIS - POST-REPAIR")
print("="*70)

if not epub_path.exists():
    print(f"\n✗ EPUB not found: {epub_path}")
    exit(1)

file_size_mb = epub_path.stat().st_size / (1024 * 1024)
print(f"\n📦 EPUB File: {epub_path.name}")
print(f"   Size: {file_size_mb:.2f} MB")

with zipfile.ZipFile(epub_path, 'r') as epub:
    all_files = epub.namelist()
    
    # Categorize files
    images = [f for f in all_files if f.endswith(('.jpg', '.jpeg', '.png', '.gif'))]
    xhtml = [f for f in all_files if f.endswith('.xhtml')]
    chapters = [f for f in xhtml if 'chapter' in f.lower()]
    
    print(f"\n📊 FILE COUNTS:")
    print(f"   Total files: {len(all_files)}")
    print(f"   Images: {len(images)}")
    print(f"   XHTML files: {len(xhtml)}")
    print(f"   Chapter files: {len(chapters)}")
    
    print(f"\n🖼️  IMAGE FILES IN EPUB:")
    if images:
        for img in sorted(images):
            print(f"   ✓ {img}")
    else:
        print("   ✗ NO IMAGES FOUND!")
    
    print(f"\n📄 CHAPTER FILES:")
    for ch in sorted(chapters)[:10]:
        print(f"   - {ch}")
    if len(chapters) > 10:
        print(f"   ... and {len(chapters) - 10} more")
    
    # Check image references in chapters
    print(f"\n{'='*70}")
    print("IMAGE REFERENCE VERIFICATION")
    print("="*70)
    
    all_img_refs = []
    for chapter in sorted(chapters):
        content = epub.read(chapter).decode('utf-8')
        img_tags = re.findall(r'<img[^>]+src="([^"]+)"[^>]*>', content)
        
        if img_tags:
            print(f"\n📖 {chapter}:")
            for src in img_tags:
                all_img_refs.append(src)
                # Extract just the filename
                filename = src.split('/')[-1]
                
                # Check if this file exists in EPUB
                full_path = f"OEBPS/Images/{filename}"
                exists = full_path in all_files
                status = "✓" if exists else "✗"
                
                print(f"   {status} {src} {'(FOUND)' if exists else '(NOT FOUND!)'}")
    
    if not all_img_refs:
        print("\n⚠️  No image references found in any chapters")
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print("="*70)
    
    # Count unique referenced files
    unique_refs = set([ref.split('/')[-1] for ref in all_img_refs])
    available_imgs = set([img.split('/')[-1] for img in images])
    
    print(f"\n📊 Statistics:")
    print(f"   Images in EPUB: {len(images)}")
    print(f"   Unique image references: {len(unique_refs)}")
    print(f"   Total image references: {len(all_img_refs)}")
    
    # Check for broken references
    broken = unique_refs - available_imgs
    if broken:
        print(f"\n✗ BROKEN REFERENCES ({len(broken)}):")
        for ref in sorted(broken):
            print(f"   - {ref}")
    else:
        print(f"\n✓ ALL IMAGE REFERENCES VALID!")
    
    # Check for unused images
    unused = available_imgs - unique_refs
    if unused:
        print(f"\n⚠️  UNUSED IMAGES ({len(unused)}):")
        for img in sorted(unused):
            print(f"   - {img}")

print(f"\n{'='*70}\n")
