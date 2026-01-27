#!/usr/bin/env python3
"""
Scan all EPUB files in INPUT directory and extract publisher information.
"""

import zipfile
import tempfile
import shutil
from pathlib import Path
from collections import defaultdict
from lxml import etree
from typing import Dict, List, Tuple

def extract_epub_metadata(epub_path: Path) -> Dict:
    """Extract metadata from an EPUB file without full extraction."""

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        try:
            # Extract EPUB
            with zipfile.ZipFile(epub_path, 'r') as zf:
                zf.extractall(temp_path)

            # Find OPF file via container.xml
            container_path = temp_path / "META-INF" / "container.xml"
            opf_path = None

            if container_path.exists():
                tree = etree.parse(str(container_path))
                ns = {'container': 'urn:oasis:names:tc:opendocument:xmlns:container'}
                rootfile = tree.find('.//container:rootfile', ns)
                if rootfile is not None:
                    opf_rel_path = rootfile.get('full-path')
                    if opf_rel_path:
                        opf_path = temp_path / opf_rel_path

            # Fallback: find any .opf file
            if opf_path is None or not opf_path.exists():
                opf_files = list(temp_path.rglob("*.opf"))
                if opf_files:
                    opf_path = opf_files[0]

            if opf_path is None or not opf_path.exists():
                return {
                    "title": epub_path.stem,
                    "publisher": "Unknown",
                    "publisher_ja": "Unknown",
                    "error": "No OPF file found"
                }

            # Parse OPF metadata
            tree = etree.parse(str(opf_path))
            ns = {
                'opf': 'http://www.idpf.org/2007/opf',
                'dc': 'http://purl.org/dc/elements/1.1/'
            }

            # Extract metadata
            title = ""
            publisher = ""

            # Get title
            title_elem = tree.find('.//dc:title', ns)
            if title_elem is not None and title_elem.text:
                title = title_elem.text.strip()
            else:
                title = epub_path.stem

            # Get publisher
            publisher_elem = tree.find('.//dc:publisher', ns)
            if publisher_elem is not None and publisher_elem.text:
                publisher = publisher_elem.text.strip()
            else:
                publisher = "Unknown"

            # Map publisher to canonical forms
            publisher_en = map_publisher_name(publisher)

            # Get sample image filenames from content directory
            content_dir = opf_path.parent
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            images = []

            for ext in image_extensions:
                images.extend(content_dir.rglob(f"*{ext}"))
                images.extend(content_dir.rglob(f"*{ext.upper()}"))

            # Get first 5 image names as samples
            image_samples = [img.name for img in sorted(images)[:5]]

            return {
                "title": title,
                "publisher": publisher,
                "publisher_en": publisher_en,
                "image_count": len(images),
                "image_samples": image_samples,
                "opf_location": str(opf_path.relative_to(temp_path))
            }

        except Exception as e:
            return {
                "title": epub_path.stem,
                "publisher": "Unknown",
                "publisher_ja": "Unknown",
                "error": str(e)
            }

def map_publisher_name(publisher: str) -> str:
    """Map Japanese publisher names to canonical English names."""

    publisher_lower = publisher.lower()

    # Define publisher mappings
    mappings = {
        'KADOKAWA': ['kadokawa', '角川', '株式会社kadokawa', 'kadokawa corporation'],
        'Overlap': ['overlap', 'オーバーラップ', '株式会社オーバーラップ'],
        'SB Creative': ['sb creative', 'sbクリエイティブ', '株式会社sbクリエイティブ', 'sbcreative'],
        'Hifumi Shobo': ['hifumi', '一二三書房', '株式会社一二三書房', '123書房'],
        'Hobby Japan': ['hobby japan', 'ホビージャパン', '株式会社ホビージャパン', 'hj'],
        'Shueisha': ['shueisha', '集英社', '株式会社集英社'],
        'Kodansha': ['kodansha', '講談社', '株式会社講談社'],
        'AlphaPolis': ['alphapolis', 'アルファポリス', '株式会社アルファポリス'],
        'Fujimi Shobo': ['fujimi', '富士見書房', 'fujimi shobo'],
        'GA Bunko': ['ga bunko', 'gaブンコ', 'ga文庫'],
        'MF Bunko': ['mf bunko', 'mfブンコ', 'mf文庫'],
        'Dengeki Bunko': ['dengeki', '電撃文庫', '電撃'],
        'Gagaga Bunko': ['gagaga', 'ガガガ文庫'],
        'Sneaker Bunko': ['sneaker', 'スニーカー文庫'],
        'Famitsu Bunko': ['famitsu', 'ファミ通文庫'],
        'Brave Bunko': ['brave', 'ブレイブ文庫'],
    }

    # Check for matches
    for canonical, variants in mappings.items():
        for variant in variants:
            if variant in publisher_lower:
                return canonical

    # Return original if no match
    return publisher

def analyze_image_patterns(image_names: List[str]) -> Dict:
    """Analyze naming patterns in image filenames."""

    patterns = {
        'numbered': 0,
        'prefixed': 0,
        'cover': 0,
        'illustration': 0,
        'kuchie': 0,
        'other': 0
    }

    for name in image_names:
        name_lower = name.lower()

        if 'cover' in name_lower or 'hyou' in name_lower:
            patterns['cover'] += 1
        elif 'kuchie' in name_lower or '口絵' in name:
            patterns['kuchie'] += 1
        elif 'illust' in name_lower or 'img' in name_lower:
            patterns['illustration'] += 1
        elif any(char.isdigit() for char in name) and name[0].isdigit():
            patterns['numbered'] += 1
        elif '_' in name or '-' in name:
            patterns['prefixed'] += 1
        else:
            patterns['other'] += 1

    return patterns

def main():
    """Main function to scan all EPUBs and generate report."""

    input_dir = Path("/Users/damminhthang/Documents/WORK/AI_MODULES/MTL_STUDIO/pipeline/INPUT")
    epub_files = list(input_dir.glob("*.epub"))

    print(f"Found {len(epub_files)} EPUB files in INPUT directory")
    print("=" * 80)

    # Group by publisher
    publishers = defaultdict(list)
    all_image_samples = defaultdict(list)

    for i, epub_path in enumerate(epub_files, 1):
        print(f"\n[{i}/{len(epub_files)}] Processing: {epub_path.name[:60]}")

        metadata = extract_epub_metadata(epub_path)

        if "error" in metadata:
            print(f"  ⚠ Error: {metadata['error']}")

        publisher_en = metadata.get("publisher_en", "Unknown")
        publisher_ja = metadata.get("publisher", "Unknown")

        print(f"  Publisher: {publisher_ja} ({publisher_en})")
        print(f"  Title: {metadata.get('title', 'Unknown')[:60]}")
        print(f"  Images: {metadata.get('image_count', 0)}")

        # Group data
        publishers[publisher_en].append({
            "title": metadata.get("title", "Unknown"),
            "publisher_ja": publisher_ja,
            "image_count": metadata.get("image_count", 0),
            "image_samples": metadata.get("image_samples", []),
            "filename": epub_path.name
        })

        # Collect image samples
        for img in metadata.get("image_samples", []):
            all_image_samples[publisher_en].append(img)

    # Generate report
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("EPUB PUBLISHER SCAN REPORT")
    report_lines.append("=" * 80)
    report_lines.append(f"\nTotal EPUBs scanned: {len(epub_files)}")
    report_lines.append(f"Publishers found: {len(publishers)}")
    report_lines.append(f"\nScan Date: {Path(__file__).stat().st_mtime}")

    # Publisher breakdown
    report_lines.append("\n" + "=" * 80)
    report_lines.append("PUBLISHER BREAKDOWN")
    report_lines.append("=" * 80)

    for publisher_en in sorted(publishers.keys(), key=lambda x: len(publishers[x]), reverse=True):
        books = publishers[publisher_en]
        report_lines.append(f"\n{publisher_en}")
        report_lines.append("-" * 80)

        # Get Japanese name (take first occurrence)
        publisher_ja = books[0]["publisher_ja"] if books else "Unknown"
        report_lines.append(f"Japanese Name: {publisher_ja}")
        report_lines.append(f"Number of EPUBs: {len(books)}")

        # Total images
        total_images = sum(book["image_count"] for book in books)
        avg_images = total_images / len(books) if books else 0
        report_lines.append(f"Total Images: {total_images} (avg {avg_images:.1f} per book)")

        # Sample titles
        report_lines.append(f"\nSample Titles:")
        for book in books[:3]:
            report_lines.append(f"  • {book['title'][:70]}")
        if len(books) > 3:
            report_lines.append(f"  ... and {len(books) - 3} more")

        # Image naming patterns
        all_images = []
        for book in books:
            all_images.extend(book["image_samples"])

        if all_images:
            report_lines.append(f"\nSample Image Filenames ({len(all_images)} samples):")
            for img in sorted(set(all_images))[:10]:
                report_lines.append(f"  • {img}")

            # Analyze patterns
            patterns = analyze_image_patterns(all_images)
            report_lines.append(f"\nImage Naming Patterns:")
            for pattern, count in sorted(patterns.items(), key=lambda x: -x[1]):
                if count > 0:
                    report_lines.append(f"  {pattern}: {count} images")

    # Summary statistics
    report_lines.append("\n" + "=" * 80)
    report_lines.append("SUMMARY STATISTICS")
    report_lines.append("=" * 80)

    total_images = sum(sum(book["image_count"] for book in books) for books in publishers.values())
    report_lines.append(f"\nTotal Images Across All EPUBs: {total_images}")
    report_lines.append(f"Average Images per EPUB: {total_images / len(epub_files):.1f}")

    # Top publishers by volume count
    report_lines.append(f"\nTop Publishers by Volume Count:")
    for publisher_en, books in sorted(publishers.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
        report_lines.append(f"  {publisher_en}: {len(books)} volumes")

    # Write report
    output_path = Path("/private/tmp/claude/-Users-damminhthang-Documents-WORK-AI-MODULES-MTL-STUDIO/314b8654-1807-4f2d-b206-e5cd9ca8beca/scratchpad/publisher_scan.txt")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    report_text = "\n".join(report_lines)
    output_path.write_text(report_text, encoding='utf-8')

    print("\n" + "=" * 80)
    print(f"Report saved to: {output_path}")
    print("=" * 80)

    # Also print to console
    print("\n" + report_text)

if __name__ == "__main__":
    main()
