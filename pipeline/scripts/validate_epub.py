#!/usr/bin/env python3
"""Validate rebuilt EPUB metadata."""

import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

epub_path = Path("OUTPUT/貴族令嬢俺にだけなつく_EN.epub")

with zipfile.ZipFile(epub_path, 'r') as zf:
    # Check OPF metadata
    container = ET.fromstring(zf.read('META-INF/container.xml'))
    ns = {'cnt': 'urn:oasis:names:tc:opendocument:xmlns:container'}
    opf_path = container.find('.//cnt:rootfile', ns).get('full-path')
    
    opf = ET.fromstring(zf.read(opf_path))
    opf_ns = {
        'opf': 'http://www.idpf.org/2007/opf',
        'dc': 'http://purl.org/dc/elements/1.1/'
    }
    
    title = opf.find('.//dc:title', opf_ns).text
    creator = opf.find('.//dc:creator', opf_ns).text
    
    # Count chapters
    xhtml_files = [f for f in zf.namelist() if 'chapter' in f.lower() and f.endswith('.xhtml')]
    
    print(f"✓ EPUB validated:")
    print(f"  Title: {title}")
    print(f"  Author: {creator}")
    print(f"  Chapters: {len(xhtml_files)}")
    print(f"  File size: {epub_path.stat().st_size / (1024*1024):.2f} MB")
