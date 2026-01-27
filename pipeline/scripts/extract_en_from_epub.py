#!/usr/bin/env python3
"""Extract English chapter content from built EPUB back to markdown files."""

import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from bs4 import BeautifulSoup
import re

epub_path = Path("OUTPUT/The Noble Lady Who Only Fawns Over Me_EN.epub")
output_dir = Path("WORK/貴族令嬢。俺にだけなつく_20260119_1d74/EN")

print(f"Extracting English translations from: {epub_path.name}")
print(f"Output directory: {output_dir}")

# Create EN directory if it doesn't exist
output_dir.mkdir(exist_ok=True)

# Extract chapters from EPUB
with zipfile.ZipFile(epub_path, 'r') as zf:
    # Find OPF file
    container = ET.fromstring(zf.read('META-INF/container.xml'))
    ns = {'cnt': 'urn:oasis:names:tc:opendocument:xmlns:container'}
    opf_path = container.find('.//cnt:rootfile', ns).get('full-path')
    opf_dir = str(Path(opf_path).parent)
    
    # Parse OPF
    opf = ET.fromstring(zf.read(opf_path))
    opf_ns = {'opf': 'http://www.idpf.org/2007/opf'}
    
    # Get spine order
    spine = opf.find('.//opf:spine', opf_ns)
    manifest = opf.find('.//opf:manifest', opf_ns)
    
    # Build id to href mapping
    id_to_href = {}
    for item in manifest.findall('opf:item', opf_ns):
        id_to_href[item.get('id')] = item.get('href')
    
    # Process spine items
    chapter_count = 0
    for itemref in spine.findall('opf:itemref', opf_ns):
        idref = itemref.get('idref')
        if idref not in id_to_href:
            continue
        
        href = id_to_href[idref]
        
        # Only process chapter files (flexible pattern)
        if not ('chapter' in href.lower() and href.endswith('.xhtml')):
            continue
        
        # Skip kuchie/cover files
        if 'kuchie' in href.lower() or 'cover' in href.lower():
            continue
        
        # Extract chapter number (flexible pattern)
        match = re.search(r'chapter0*(\d+)', href, re.IGNORECASE)
        if not match:
            continue
        
        chapter_num = match.group(1).zfill(2)  # Pad to 2 digits
        chapter_id = f"CHAPTER_{chapter_num}"
        
        # Read XHTML content
        xhtml_path = f"{opf_dir}/{href}"
        xhtml_content = zf.read(xhtml_path).decode('utf-8')
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(xhtml_content, 'html.parser')
        
        # Extract body content
        body = soup.find('body')
        if not body:
            continue
        
        # Convert to markdown-like format
        lines = []
        
        for element in body.descendants:
            if element.name == 'h1':
                lines.append(f"\n# {element.get_text(strip=True)}\n")
            elif element.name == 'h2':
                lines.append(f"\n## {element.get_text(strip=True)}\n")
            elif element.name == 'p':
                # Check if it contains an image
                img = element.find('img')
                if img:
                    src = img.get('src', '')
                    if src:
                        img_name = Path(src).name
                        lines.append(f"\n[ILLUSTRATION: {img_name}]\n")
                else:
                    text = element.get_text(strip=True)
                    if text and text not in ['***', '＊　＊　＊']:
                        lines.append(text + "\n")
            elif element.name == 'hr':
                lines.append("\n***\n")
        
        # Write to markdown file
        output_file = output_dir / f"{chapter_id}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(''.join(lines))
        
        chapter_count += 1
        print(f"  ✓ Extracted {chapter_id}.md")

print(f"\n✅ Extracted {chapter_count} chapters to EN/ folder")
