#!/usr/bin/env python3
"""
Comprehensive EPUB Library Analysis - INPUT/ folder.
Analyzes raw EPUB files to understand publisher patterns and structure.
"""

import zipfile
import json
from pathlib import Path
from collections import defaultdict, Counter
from lxml import etree
import re

class EPUBAnalyzer:
    """Analyze EPUB file structure and metadata."""
    
    OPF_NS = {"opf": "http://www.idpf.org/2007/opf"}
    DC_NS = {"dc": "http://purl.org/dc/elements/1.1/"}
    NCX_NS = {"ncx": "http://www.daisy.org/z3986/2005/ncx/"}
    XHTML_NS = {"xhtml": "http://www.w3.org/1999/xhtml"}
    EPUB_NS = {"epub": "http://www.idpf.org/2007/ops"}
    
    def __init__(self, epub_path: Path):
        self.epub_path = epub_path
        self.filename = epub_path.name
        
    def analyze(self):
        """Perform comprehensive analysis."""
        try:
            with zipfile.ZipFile(self.epub_path, 'r') as epub:
                return {
                    "filename": self.filename,
                    "metadata": self._extract_metadata(epub),
                    "toc": self._analyze_toc(epub),
                    "spine": self._analyze_spine(epub),
                    "images": self._count_images(epub),
                    "content": self._analyze_content(epub),
                    "structure": self._detect_structure_pattern(epub)
                }
        except Exception as e:
            return {
                "filename": self.filename,
                "error": str(e)
            }
    
    def _find_opf(self, epub):
        """Locate the OPF file."""
        try:
            container = epub.read("META-INF/container.xml")
            tree = etree.fromstring(container)
            rootfile = tree.find(".//{urn:oasis:names:tc:opendocument:xmlns:container}rootfile")
            if rootfile is not None:
                return rootfile.get("full-path")
        except:
            pass
        
        # Fallback: search for .opf files
        for name in epub.namelist():
            if name.endswith('.opf'):
                return name
        return None
    
    def _extract_metadata(self, epub):
        """Extract metadata from OPF."""
        opf_path = self._find_opf(epub)
        if not opf_path:
            return {}
        
        try:
            opf_data = epub.read(opf_path)
            tree = etree.fromstring(opf_data)
            
            metadata = {}
            
            # Dublin Core metadata
            for tag in ["title", "creator", "publisher", "language", "identifier"]:
                elem = tree.find(f".//dc:{tag}", self.DC_NS)
                if elem is not None and elem.text:
                    if tag == "creator":
                        role = elem.get("{http://www.idpf.org/2007/opf}role", "")
                        if role == "aut":
                            metadata["author"] = elem.text.strip()
                        elif role == "ill":
                            metadata["illustrator"] = elem.text.strip()
                    else:
                        metadata[tag] = elem.text.strip()
            
            # Check for modified date
            modified = tree.find(".//opf:meta[@property='dcterms:modified']", self.OPF_NS)
            if modified is not None and modified.text:
                metadata["modified"] = modified.text.strip()
            
            return metadata
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_toc(self, epub):
        """Analyze table of contents structure."""
        # Try EPUB3 nav.xhtml first
        nav_data = self._find_and_read_nav(epub)
        if nav_data:
            return self._parse_nav_xhtml(nav_data)
        
        # Fallback to EPUB2 toc.ncx
        ncx_data = self._find_and_read_ncx(epub)
        if ncx_data:
            return self._parse_ncx(ncx_data)
        
        return {"format": "none", "entries": 0}
    
    def _find_and_read_nav(self, epub):
        """Find and read nav.xhtml."""
        for name in epub.namelist():
            if 'nav.xhtml' in name.lower() or 'navigation' in name.lower():
                try:
                    return epub.read(name)
                except:
                    pass
        return None
    
    def _find_and_read_ncx(self, epub):
        """Find and read toc.ncx."""
        for name in epub.namelist():
            if name.endswith('.ncx'):
                try:
                    return epub.read(name)
                except:
                    pass
        return None
    
    def _parse_nav_xhtml(self, nav_data):
        """Parse EPUB3 nav.xhtml."""
        try:
            tree = etree.fromstring(nav_data)
            nav_elem = tree.find(".//xhtml:nav[@epub:type='toc']", {**self.XHTML_NS, **self.EPUB_NS})
            if nav_elem is None:
                nav_elem = tree.find(".//{http://www.w3.org/1999/xhtml}nav")
            
            if nav_elem is not None:
                entries = len(nav_elem.findall(".//xhtml:li", self.XHTML_NS))
                return {"format": "nav.xhtml", "entries": entries}
        except:
            pass
        return {"format": "nav.xhtml", "entries": 0}
    
    def _parse_ncx(self, ncx_data):
        """Parse EPUB2 toc.ncx."""
        try:
            tree = etree.fromstring(ncx_data)
            navpoints = tree.findall(".//ncx:navPoint", self.NCX_NS)
            return {"format": "toc.ncx", "entries": len(navpoints)}
        except:
            pass
        return {"format": "toc.ncx", "entries": 0}
    
    def _analyze_spine(self, epub):
        """Analyze spine structure."""
        opf_path = self._find_opf(epub)
        if not opf_path:
            return {}
        
        try:
            opf_data = epub.read(opf_path)
            tree = etree.fromstring(opf_data)
            
            spine = tree.find(".//opf:spine", self.OPF_NS)
            if spine is not None:
                items = spine.findall(".//opf:itemref", self.OPF_NS)
                direction = spine.get("page-progression-direction", "ltr")
                return {
                    "items": len(items),
                    "direction": direction
                }
        except:
            pass
        return {"items": 0, "direction": "unknown"}
    
    def _count_images(self, epub):
        """Count and categorize images."""
        images = {
            "total": 0,
            "jpg": 0,
            "png": 0,
            "svg": 0,
            "cover": False,
            "potential_kuchie": 0,
            "potential_illustrations": 0
        }
        
        for name in epub.namelist():
            lower_name = name.lower()
            if any(ext in lower_name for ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg']):
                images["total"] += 1
                
                if '.jpg' in lower_name or '.jpeg' in lower_name:
                    images["jpg"] += 1
                elif '.png' in lower_name:
                    images["png"] += 1
                elif '.svg' in lower_name:
                    images["svg"] += 1
                
                # Detect cover
                if 'cover' in lower_name:
                    images["cover"] = True
                
                # Detect kuchie patterns (p001, p002, k001, etc.)
                if re.search(r'[pk]\d{3}', lower_name):
                    images["potential_kuchie"] += 1
                
                # Detect illustration patterns (m001, i001, insert, illust, etc.)
                if re.search(r'[mi]\d{3}', lower_name) or 'illust' in lower_name or 'insert' in lower_name:
                    images["potential_illustrations"] += 1
        
        return images
    
    def _analyze_content(self, epub):
        """Analyze content file structure."""
        xhtml_files = []
        css_files = []
        fonts = []
        
        for name in epub.namelist():
            lower_name = name.lower()
            if '.xhtml' in lower_name or '.html' in lower_name:
                xhtml_files.append(name)
            elif '.css' in lower_name:
                css_files.append(name)
            elif '.otf' in lower_name or '.ttf' in lower_name or '.woff' in lower_name:
                fonts.append(name)
        
        return {
            "xhtml_files": len(xhtml_files),
            "css_files": len(css_files),
            "fonts": len(fonts),
            "has_ruby": self._check_for_ruby(epub, xhtml_files[:3])  # Sample first 3
        }
    
    def _check_for_ruby(self, epub, sample_files):
        """Check if content uses ruby tags."""
        for file in sample_files:
            try:
                content = epub.read(file).decode('utf-8', errors='ignore')
                if '<ruby' in content or '<rt>' in content:
                    return True
            except:
                pass
        return False
    
    def _detect_structure_pattern(self, epub):
        """Detect publisher-specific structure patterns."""
        patterns = []
        
        # Check directory structure
        namelist = epub.namelist()
        
        if any('OEBPS/' in name for name in namelist):
            patterns.append("OEBPS")
        if any('OPS/' in name for name in namelist):
            patterns.append("OPS")
        if any('item/' in name for name in namelist):
            patterns.append("item")
        if any('xhtml/' in name for name in namelist):
            patterns.append("xhtml")
        
        # Check for specific publisher markers
        for name in namelist:
            if 'overlap' in name.lower():
                patterns.append("Overlap-style")
                break
            if 'hobby' in name.lower() or 'hj' in name.lower():
                patterns.append("HobbyJapan-style")
                break
        
        return patterns

def main():
    input_dir = Path("INPUT")
    epub_files = sorted(input_dir.glob("*.epub"))
    
    print("=" * 80)
    print("COMPREHENSIVE EPUB LIBRARY ANALYSIS")
    print("=" * 80)
    print(f"\n📚 Found {len(epub_files)} EPUB files in INPUT/\n")
    
    results = []
    publishers = Counter()
    toc_formats = Counter()
    image_stats = {"with_kuchie": 0, "with_illustrations": 0, "with_both": 0}
    structure_patterns = Counter()
    languages = Counter()
    
    print("Analyzing EPUBs...")
    for i, epub_path in enumerate(epub_files, 1):
        print(f"  [{i}/{len(epub_files)}] {epub_path.name[:60]}")
        analyzer = EPUBAnalyzer(epub_path)
        result = analyzer.analyze()
        results.append(result)
        
        if "error" not in result:
            # Aggregate statistics
            publisher = result["metadata"].get("publisher", "Unknown")
            publishers[publisher] += 1
            
            toc_fmt = result["toc"].get("format", "none")
            toc_formats[toc_fmt] += 1
            
            if result["images"]["potential_kuchie"] > 0:
                image_stats["with_kuchie"] += 1
            if result["images"]["potential_illustrations"] > 0:
                image_stats["with_illustrations"] += 1
            if result["images"]["potential_kuchie"] > 0 and result["images"]["potential_illustrations"] > 0:
                image_stats["with_both"] += 1
            
            for pattern in result["structure"]:
                structure_patterns[pattern] += 1
            
            lang = result["metadata"].get("language", "unknown")
            languages[lang] += 1
    
    # Generate Report
    print("\n" + "=" * 80)
    print("PUBLISHER DISTRIBUTION")
    print("=" * 80)
    for publisher, count in publishers.most_common():
        print(f"  {publisher}: {count} volumes")
    
    print("\n" + "=" * 80)
    print("NAVIGATION FORMATS")
    print("=" * 80)
    print("\nTOC Format Distribution:")
    for fmt, count in toc_formats.most_common():
        print(f"  {fmt}: {count} volumes ({count/len(epub_files)*100:.1f}%)")
    
    print("\nTOC Entry Statistics:")
    toc_entries = [r["toc"]["entries"] for r in results if "toc" in r and "entries" in r["toc"]]
    if toc_entries:
        print(f"  Average: {sum(toc_entries)/len(toc_entries):.1f} entries")
        print(f"  Range: {min(toc_entries)} - {max(toc_entries)} entries")
    
    print("\n" + "=" * 80)
    print("IMAGE ASSET PATTERNS")
    print("=" * 80)
    print(f"\nVolumes with Kuchie: {image_stats['with_kuchie']}")
    print(f"Volumes with Illustrations: {image_stats['with_illustrations']}")
    print(f"Volumes with Both: {image_stats['with_both']}")
    
    print("\nImage Statistics:")
    total_images = [r["images"]["total"] for r in results if "images" in r]
    if total_images:
        print(f"  Average images per volume: {sum(total_images)/len(total_images):.1f}")
        print(f"  Range: {min(total_images)} - {max(total_images)} images")
    
    jpg_counts = [r["images"]["jpg"] for r in results if "images" in r]
    if jpg_counts:
        print(f"  Average JPG images: {sum(jpg_counts)/len(jpg_counts):.1f}")
    
    print("\n" + "=" * 80)
    print("STRUCTURE PATTERNS")
    print("=" * 80)
    for pattern, count in structure_patterns.most_common():
        print(f"  {pattern}: {count} volumes ({count/len(epub_files)*100:.1f}%)")
    
    print("\n" + "=" * 80)
    print("CONTENT ANALYSIS")
    print("=" * 80)
    ruby_count = sum(1 for r in results if r.get("content", {}).get("has_ruby", False))
    print(f"Volumes with Ruby tags: {ruby_count} ({ruby_count/len(epub_files)*100:.1f}%)")
    
    xhtml_counts = [r["content"]["xhtml_files"] for r in results if "content" in r]
    if xhtml_counts:
        print(f"Average XHTML files per volume: {sum(xhtml_counts)/len(xhtml_counts):.1f}")
    
    spine_items = [r["spine"]["items"] for r in results if "spine" in r and "items" in r["spine"]]
    if spine_items:
        print(f"Average spine items: {sum(spine_items)/len(spine_items):.1f}")
    
    print("\n" + "=" * 80)
    print("LANGUAGE DISTRIBUTION")
    print("=" * 80)
    for lang, count in languages.most_common():
        print(f"  {lang}: {count} volumes")
    
    print("\n" + "=" * 80)
    print("SAMPLE VOLUMES")
    print("=" * 80)
    for result in results[:5]:
        if "error" in result:
            continue
        print(f"\n📖 {result['filename'][:60]}")
        print(f"   Publisher: {result['metadata'].get('publisher', 'Unknown')}")
        print(f"   Author: {result['metadata'].get('author', 'Unknown')}")
        print(f"   TOC: {result['toc']['format']} ({result['toc']['entries']} entries)")
        print(f"   Images: {result['images']['total']} total ({result['images']['jpg']} JPG)")
        print(f"   Structure: {', '.join(result['structure']) if result['structure'] else 'Standard'}")
    
    print("\n" + "=" * 80)
    print(f"✓ Analysis complete - {len(results)} volumes processed")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
