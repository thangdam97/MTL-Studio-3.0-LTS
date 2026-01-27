#!/usr/bin/env python3
"""Analyze raw EPUB structure patterns across a series."""

import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict
import re

def extract_epub_structure(epub_path: Path) -> dict:
    """Extract key structural information from raw EPUB."""
    result = {
        'title': epub_path.stem,
        'size_mb': epub_path.stat().st_size / (1024 * 1024),
        'images': [],
        'xhtml_files': [],
        'spine_order': [],
        'toc_entries': [],
        'image_patterns': defaultdict(int)
    }
    
    try:
        with zipfile.ZipFile(epub_path, 'r') as zf:
            # Find OPF file
            container = ET.fromstring(zf.read('META-INF/container.xml'))
            ns = {'cnt': 'urn:oasis:names:tc:opendocument:xmlns:container'}
            opf_path = container.find('.//cnt:rootfile', ns).get('full-path')
            opf_dir = str(Path(opf_path).parent)
            
            # Parse OPF
            opf = ET.fromstring(zf.read(opf_path))
            opf_ns = {
                'opf': 'http://www.idpf.org/2007/opf',
                'dc': 'http://purl.org/dc/elements/1.1/'
            }
            
            # Get title
            title = opf.find('.//dc:title', opf_ns)
            if title is not None:
                result['title'] = title.text
            
            # Get manifest items
            manifest = opf.find('.//opf:manifest', opf_ns)
            id_to_href = {}
            for item in manifest.findall('opf:item', opf_ns):
                item_id = item.get('id')
                href = item.get('href')
                media_type = item.get('media-type', '')
                id_to_href[item_id] = href
                
                if 'image' in media_type:
                    result['images'].append(href)
                    # Categorize by pattern
                    filename = Path(href).name
                    if re.match(r'cover\.jpe?g', filename, re.I):
                        result['image_patterns']['cover'] += 1
                    elif re.match(r'kuchie[-_]\d+', filename, re.I):
                        result['image_patterns']['kuchie'] += 1
                    elif re.match(r'i[-_]\d+\.jpe?g', filename, re.I):
                        result['image_patterns']['i-pattern'] += 1
                    elif re.match(r'illust[-_]\d+', filename, re.I):
                        result['image_patterns']['illust-pattern'] += 1
                    elif filename.endswith('.png'):
                        result['image_patterns']['gaiji'] += 1
                    else:
                        result['image_patterns']['other'] += 1
                
                elif 'xhtml' in media_type:
                    result['xhtml_files'].append(href)
            
            # Get spine order
            spine = opf.find('.//opf:spine', opf_ns)
            for itemref in spine.findall('opf:itemref', opf_ns):
                idref = itemref.get('idref')
                if idref in id_to_href:
                    result['spine_order'].append(id_to_href[idref])
            
            # Try to find TOC
            toc_candidates = ['toc.ncx', 'navigation-documents.xhtml', 'nav.xhtml']
            for toc_name in toc_candidates:
                toc_path = f"{opf_dir}/{toc_name}" if opf_dir != '.' else toc_name
                try:
                    toc_content = zf.read(toc_path)
                    if 'ncx' in toc_name:
                        # NCX format
                        toc = ET.fromstring(toc_content)
                        ncx_ns = {'ncx': 'http://www.daisy.org/z3986/2005/ncx/'}
                        for navpoint in toc.findall('.//ncx:navPoint', ncx_ns):
                            label = navpoint.find('.//ncx:text', ncx_ns)
                            content = navpoint.find('.//ncx:content', ncx_ns)
                            if label is not None and content is not None:
                                result['toc_entries'].append({
                                    'label': label.text,
                                    'src': content.get('src')
                                })
                    else:
                        # NAV format
                        toc = ET.fromstring(toc_content)
                        # Try both with and without namespace
                        for a_tag in toc.findall('.//{http://www.w3.org/1999/xhtml}a'):
                            result['toc_entries'].append({
                                'label': a_tag.text or '',
                                'src': a_tag.get('href', '')
                            })
                        if not result['toc_entries']:
                            for a_tag in toc.findall('.//a'):
                                result['toc_entries'].append({
                                    'label': a_tag.text or '',
                                    'src': a_tag.get('href', '')
                                })
                    break
                except:
                    continue
            
    except Exception as e:
        result['error'] = str(e)
    
    return result


def main():
    input_dir = Path("INPUT")
    series_pattern = "貴族令嬢"
    
    epubs = sorted([f for f in input_dir.glob("*.epub") if series_pattern in f.name])
    
    print("=" * 80)
    print(f"RAW EPUB STRUCTURE ANALYSIS: {series_pattern}")
    print("=" * 80)
    print(f"Found {len(epubs)} EPUB files\n")
    
    all_results = []
    
    for epub_path in epubs:
        print(f"\n{'─' * 80}")
        print(f"VOLUME: {epub_path.name}")
        print('─' * 80)
        
        result = extract_epub_structure(epub_path)
        all_results.append(result)
        
        if 'error' in result:
            print(f"  ⚠️  Error: {result['error']}")
            continue
        
        print(f"\n📦 FILE INFO:")
        print(f"   Size: {result['size_mb']:.2f} MB")
        print(f"   Title: {result['title']}")
        
        print(f"\n📄 CONTENT:")
        print(f"   XHTML files: {len(result['xhtml_files'])}")
        print(f"   Spine items: {len(result['spine_order'])}")
        print(f"   TOC entries: {len(result['toc_entries'])}")
        
        print(f"\n🖼️  IMAGES ({len(result['images'])} total):")
        for pattern, count in sorted(result['image_patterns'].items()):
            print(f"   {pattern}: {count}")
        
        # Analyze spine structure
        print(f"\n📚 SPINE STRUCTURE:")
        spine_files = [Path(s).name for s in result['spine_order']]
        p_files = [f for f in spine_files if f.startswith('p-')]
        print(f"   p-*.xhtml files: {len(p_files)}")
        if p_files:
            print(f"   Range: {p_files[0]} → {p_files[-1]}")
        
        # Analyze TOC structure
        if result['toc_entries']:
            print(f"\n📖 TOC STRUCTURE:")
            # Find first story entry
            first_story = None
            for i, entry in enumerate(result['toc_entries']):
                label = entry['label'].lower()
                if 'プロ' in label or '第' in label or 'chapter' in label:
                    first_story = entry
                    src_file = entry['src'].split('#')[0].split('/')[-1]
                    print(f"   First story entry: {entry['label']} → {src_file}")
                    
                    # Count files before first story in spine
                    try:
                        first_idx = spine_files.index(src_file)
                        pre_story = spine_files[:first_idx]
                        pre_p_files = [f for f in pre_story if f.startswith('p-')]
                        if pre_p_files:
                            print(f"   Pre-story pages: {len(pre_p_files)} ({', '.join(pre_p_files)})")
                    except ValueError:
                        pass
                    break
            
            # Check for common patterns
            labels = [e['label'] for e in result['toc_entries']]
            chapter_count = sum(1 for l in labels if '第' in l or 'chapter' in l.lower())
            has_prologue = any('プロ' in l for l in labels)
            has_epilogue = any('エピ' in l for l in labels)
            has_intermission = any('幕間' in l for l in labels)
            
            print(f"   Chapters: {chapter_count}")
            print(f"   Has prologue: {'✓' if has_prologue else '✗'}")
            print(f"   Has epilogue: {'✓' if has_epilogue else '✗'}")
            print(f"   Has intermission: {'✓' if has_intermission else '✗'}")
    
    # Series-wide analysis
    print(f"\n\n{'=' * 80}")
    print("SERIES-WIDE PATTERNS")
    print('=' * 80)
    
    if all_results:
        avg_size = sum(r.get('size_mb', 0) for r in all_results) / len(all_results)
        avg_images = sum(len(r.get('images', [])) for r in all_results) / len(all_results)
        avg_xhtml = sum(len(r.get('xhtml_files', [])) for r in all_results) / len(all_results)
        
        print(f"\nAVERAGE PER VOLUME:")
        print(f"  File size: {avg_size:.2f} MB")
        print(f"  Images: {avg_images:.1f}")
        print(f"  XHTML files: {avg_xhtml:.1f}")
        
        # Image pattern consistency
        print(f"\nIMAGE PATTERN CONSISTENCY:")
        all_patterns = set()
        for r in all_results:
            all_patterns.update(r.get('image_patterns', {}).keys())
        
        for pattern in sorted(all_patterns):
            counts = [r.get('image_patterns', {}).get(pattern, 0) for r in all_results]
            min_c, max_c = min(counts), max(counts)
            avg_c = sum(counts) / len(counts)
            print(f"  {pattern}: min={min_c}, max={max_c}, avg={avg_c:.1f}")
            if min_c == max_c:
                print(f"    → ✓ Consistent across all volumes")
            else:
                print(f"    → ⚠️ Varies by volume")
        
        # TOC structure consistency
        print(f"\nTOC STRUCTURE:")
        toc_counts = [len(r.get('toc_entries', [])) for r in all_results]
        print(f"  Entries per volume: {toc_counts}")
        if len(set(toc_counts)) == 1:
            print(f"  → ✓ Consistent TOC size")
        else:
            print(f"  → ⚠️ Variable TOC size (expected for different chapter counts)")
    
    print(f"\n{'=' * 80}")


if __name__ == "__main__":
    main()
