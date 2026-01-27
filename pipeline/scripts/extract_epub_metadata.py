#!/usr/bin/env python3
"""Extract metadata from built EPUB and recreate metadata_en.json."""

import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import json
import re

epub_path = Path("OUTPUT/The Noble Lady Who Only Fawns Over Me_EN.epub")
output_dir = Path("WORK/貴族令嬢。俺にだけなつく_20260119_1d74")

# Extract metadata and TOC from EPUB
with zipfile.ZipFile(epub_path, 'r') as zf:
    # Find OPF file
    container = ET.fromstring(zf.read('META-INF/container.xml'))
    ns = {'cnt': 'urn:oasis:names:tc:opendocument:xmlns:container'}
    opf_path = container.find('.//cnt:rootfile', ns).get('full-path')
    opf_dir = str(Path(opf_path).parent)
    
    # Parse OPF for metadata
    opf = ET.fromstring(zf.read(opf_path))
    opf_ns = {
        'opf': 'http://www.idpf.org/2007/opf',
        'dc': 'http://purl.org/dc/elements/1.1/'
    }
    
    title_en = opf.find('.//dc:title', opf_ns).text
    author_en = opf.find('.//dc:creator', opf_ns).text
    publisher_elem = opf.find('.//dc:publisher', opf_ns)
    publisher_en = publisher_elem.text if publisher_elem is not None else "KADOKAWA"
    
    print(f"Title: {title_en}")
    print(f"Author: {author_en}")
    print(f"Publisher: {publisher_en}")
    
    # Extract TOC
    toc_content = zf.read(f"{opf_dir}/toc.ncx")
    toc = ET.fromstring(toc_content)
    ncx_ns = {'ncx': 'http://www.daisy.org/z3986/2005/ncx/'}
    
    chapters = []
    for navpoint in toc.findall('.//ncx:navPoint', ncx_ns):
        label_elem = navpoint.find('.//ncx:text', ncx_ns)
        content_elem = navpoint.find('.//ncx:content', ncx_ns)
        if label_elem is not None and content_elem is not None:
            src = content_elem.get('src')
            # Extract chapter_XX from src
            match = re.search(r'chapter_(\d+)', src)
            if match:
                chapter_id = f"chapter_{match.group(1)}"
                chapters.append({
                    'id': chapter_id,
                    'title_en': label_elem.text
                })
    
    print(f"\nChapters extracted: {len(chapters)}")
    for ch in chapters[:3]:
        print(f"  {ch['id']}: {ch['title_en']}")

# Create metadata_en.json
metadata = {
    "title_en": title_en,
    "author_en": author_en,
    "illustrator_en": "N/A",
    "publisher_en": publisher_en,
    "chapters": chapters,
    "character_names": {
        "ベレト": "Beret",
        "シア": "Sia",
        "エレナ・ルクレール": "Elena Leclerc",
        "エレナ": "Elena",
        "ルーナ・ペレンメル": "Luna Peremmer",
        "ルーナ": "Luna",
        "アラン": "Alan"
    },
    "glossary": {
        "ギーゼルペイン": "Giselpane",
        "レイヴェルワーツ学園": "Ravelwarts Academy",
        "レイヴェルワーツ": "Ravelwarts",
        "紅花姫": "Crimson Flower Princess"
    },
    "target_language": "en",
    "language_code": "en"
}

# Save metadata_en.json
output_file = output_dir / "metadata_en.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, ensure_ascii=False, indent=2)

print(f"\n✓ Created {output_file}")
print(f"  Title: {metadata['title_en']}")
print(f"  Author: {metadata['author_en']}")
print(f"  Chapters: {len(metadata['chapters'])}")
print(f"  Character names: {len(metadata['character_names'])}")
print(f"  Glossary terms: {len(metadata['glossary'])}")
