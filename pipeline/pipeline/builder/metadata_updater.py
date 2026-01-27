"""
Metadata Updater - Language-Agnostic EPUB Metadata Processing.

Updates OPF and navigation files with target language metadata.
Handles manifest entries, spine order, and navigation documents.
"""

import re
from pathlib import Path
from typing import List, Dict, Optional

from .config import get_epub_version, DISCARD_XHTML_FILES, get_fonts_to_embed, get_spine_direction


class MetadataUpdater:
    """Updates EPUB metadata files."""

    @staticmethod
    def update_opf_file(
        opf_path: Path,
        target_lang: str,
        source_lang: str = "ja",
        book_title: str = "",
        detected_images: Optional[List] = None,
        chapter_order: Optional[List[str]] = None
    ) -> None:
        """
        Update OPF manifest and spine for translated EPUB.

        Args:
            opf_path: Path to OPF file
            target_lang: Target language code (e.g., 'en', 'vi')
            source_lang: Source language code (e.g., 'ja')
            book_title: Translated book title
            detected_images: List of image info objects for insert pages
            chapter_order: List of chapter IDs in reading order
        """
        with open(opf_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        epub_version = get_epub_version()

        # Convert OPF version if needed
        if epub_version == "EPUB2":
            content = MetadataUpdater._convert_to_epub2_opf(content)

        # Update language attributes
        content = MetadataUpdater._update_language_in_opf(content, source_lang, target_lang)
        content = MetadataUpdater._update_dc_language(content, source_lang, target_lang)

        # Update reading direction
        content = MetadataUpdater._update_spine_direction(content, source_lang)

        # Update book title if provided
        if book_title:
            content = MetadataUpdater._update_book_title(content, book_title)

        # Add font manifest entries
        content = MetadataUpdater._add_font_manifest_entries(content)

        # Add insert page manifest entries if images detected
        if detected_images:
            content = MetadataUpdater._add_insert_manifest_entries(content, detected_images)

        # Remove discard files from manifest
        content = MetadataUpdater._remove_discard_files_from_manifest(content)

        # Update spine order
        if chapter_order:
            content = MetadataUpdater._update_spine_order(content, chapter_order, detected_images)

        if content != original_content:
            with open(opf_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] Updated OPF file: {opf_path.name}")
        else:
            print(f"- No changes needed in OPF file")

    @staticmethod
    def _convert_to_epub2_opf(content: str) -> str:
        """Convert OPF 3.0 to OPF 2.0 format."""
        content = re.sub(r'version="3\.0"', 'version="2.0"', content)
        content = re.sub(r'(\s+properties="nav")', '', content)
        return content

    @staticmethod
    def _update_language_in_opf(content: str, source_lang: str, target_lang: str) -> str:
        """Update xml:lang attribute in package element."""
        content = re.sub(
            rf'<package\s+([^>]*)xml:lang="{source_lang}"',
            rf'<package \1xml:lang="{target_lang}"',
            content,
        )
        return content

    @staticmethod
    def _update_spine_direction(content: str, source_lang: str) -> str:
        """Update page-progression-direction based on source language."""
        target_direction = get_spine_direction(source_lang)

        # If source was RTL (Japanese vertical), change to LTR
        if 'page-progression-direction="rtl"' in content:
            content = re.sub(
                r'page-progression-direction="rtl"',
                f'page-progression-direction="{target_direction}"',
                content,
            )

        return content

    @staticmethod
    def _update_dc_language(content: str, source_lang: str, target_lang: str) -> str:
        """Update dc:language element."""
        content = re.sub(
            rf'<dc:language>{source_lang}</dc:language>',
            f'<dc:language>{target_lang}</dc:language>',
            content,
        )
        return content

    @staticmethod
    def _update_book_title(content: str, title: str) -> str:
        """Update book title in OPF file."""
        title_pattern = r'<dc:title[^>]*>[^<]*</dc:title>'
        replacement = f'<dc:title id="title">{title}</dc:title>'
        content = re.sub(title_pattern, replacement, content, count=1)
        return content

    @staticmethod
    def _add_font_manifest_entries(content: str) -> str:
        """Add manifest entries for embedded fonts."""
        manifest_close_pattern = r'(</manifest>)'

        fonts_to_embed = get_fonts_to_embed()
        font_entries = []
        for font_filename, font_info in fonts_to_embed.items():
            entry = (
                f'    <item media-type="application/vnd.ms-opentype" '
                f'id="{font_info["id"]}" '
                f'href="fonts/{font_filename}"/>'
            )
            font_entries.append(entry)

        if font_entries:
            all_entries = '\n'.join(font_entries)
            replacement = f'{all_entries}\n  </manifest>'
            content = re.sub(manifest_close_pattern, replacement, content)

        return content

    @staticmethod
    def _add_insert_manifest_entries(content: str, detected_images: List) -> str:
        """Add manifest entries for insert pages."""
        if not detected_images:
            return content

        manifest_close_pattern = r'</manifest>'
        insert_entries = []

        for img in detected_images:
            item_id = f"p-{img.insert_id}"
            href = f"xhtml/{img.xhtml_filename}"
            entry = f'    <item media-type="application/xhtml+xml" id="{item_id}" href="{href}"/>'
            insert_entries.append(entry)

        if insert_entries:
            all_entries = '\n'.join(insert_entries)
            replacement = f'{all_entries}\n  </manifest>'
            content = re.sub(manifest_close_pattern, replacement, content)

        return content

    @staticmethod
    def _remove_discard_files_from_manifest(content: str) -> str:
        """Remove entries for discarded XHTML files from manifest."""
        for filename in DISCARD_XHTML_FILES:
            pattern = rf'<item[^>]*href="xhtml/{re.escape(filename)}"[^>]*/>'
            content = re.sub(pattern, '', content)
        return content

    @staticmethod
    def _update_spine_order(
        content: str,
        chapter_order: List[str],
        detected_images: Optional[List] = None
    ) -> str:
        """Update spine order with chapters and insert pages."""
        spine_item_refs = []

        # Group images by source chapter
        images_by_chapter = {}
        if detected_images:
            for img in detected_images:
                chapter = img.source_chapter.replace('.xhtml', '')
                if chapter not in images_by_chapter:
                    images_by_chapter[chapter] = []
                images_by_chapter[chapter].append(img)

        # Build spine with chapters and interleaved inserts
        for chapter_id in chapter_order:
            spine_item_refs.append(f'<itemref idref="{chapter_id}"/>')

            if chapter_id in images_by_chapter:
                for img in images_by_chapter[chapter_id]:
                    insert_id = f"p-{img.insert_id}"
                    spine_item_refs.append(f'<itemref idref="{insert_id}"/>')

        new_spine_content = '\n    '.join(spine_item_refs)

        spine_pattern = r'<spine[^>]*>(.*?)</spine>'

        def replace_spine(match):
            spine_start = match.group(0)[:match.group(0).index('>') + 1]
            return f'{spine_start}\n    {new_spine_content}\n  </spine>'

        content = re.sub(spine_pattern, replace_spine, content, flags=re.DOTALL)

        return content

    @staticmethod
    def update_navigation_file(
        nav_path: Path,
        target_lang: str,
        source_lang: str = "ja",
        chapter_title_map: Optional[Dict[str, str]] = None,
        toc_title: str = "Table of Contents",
        cover_title: str = "Cover"
    ) -> None:
        """
        Update navigation document with target language metadata.

        Args:
            nav_path: Path to navigation XHTML file
            target_lang: Target language code
            source_lang: Source language code
            chapter_title_map: Dictionary mapping XHTML filename to chapter title
            toc_title: Translated title for TOC
            cover_title: Translated title for cover
        """
        with open(nav_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Update language attribute
        content = re.sub(
            rf'xml:lang="{source_lang}"',
            f'xml:lang="{target_lang}"',
            content,
        )
        content = re.sub(
            rf'lang="{source_lang}"',
            f'lang="{target_lang}"',
            content,
        )

        # Update TOC heading
        content = re.sub(
            r'<h1[^>]*>[^<]*</h1>',
            f'<h1 lang="{target_lang}">{toc_title}</h1>',
            content,
            count=1
        )

        # Update cover link text
        cover_pattern = r'(<a\s+href="xhtml/p-cover\.xhtml"[^>]*>)[^<]*</a>'
        content = re.sub(cover_pattern, rf'\1{cover_title}</a>', content)

        # Update chapter title links
        if chapter_title_map:
            for xhtml_file, title in chapter_title_map.items():
                chapter_id = xhtml_file.replace('.xhtml', '')
                pattern = rf'(<a\s+href="xhtml/{re.escape(chapter_id)}\.xhtml[^>]*>)[^<]*</a>'
                content = re.sub(pattern, rf'\1{title}</a>', content)

        # Remove discard file references
        for filename in DISCARD_XHTML_FILES:
            pattern = rf'<li>\s*<a\s+href="xhtml/{re.escape(filename)}"[^>]*>[^<]*</a>\s*</li>'
            content = re.sub(pattern, '', content)

        if content != original_content:
            with open(nav_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] Updated navigation file: {nav_path.name}")
        else:
            print(f"- No changes needed in navigation file")


def update_all_metadata(
    item_dir: Path,
    target_lang: str,
    source_lang: str = "ja",
    book_title: str = "",
    toc_title: str = "Table of Contents",
    cover_title: str = "Cover",
    chapter_title_map: Optional[Dict[str, str]] = None,
    detected_images: Optional[List] = None,
    chapter_order: Optional[List[str]] = None
) -> None:
    """
    Main function to update all metadata files.

    Args:
        item_dir: Item directory for EPUB contents
        target_lang: Target language code
        source_lang: Source language code
        book_title: Translated book title
        toc_title: Translated TOC title
        cover_title: Translated cover title
        chapter_title_map: Dictionary mapping XHTML filename to chapter title
        detected_images: List of image info objects
        chapter_order: List of chapter IDs in reading order
    """
    print("[INFO] Updating EPUB metadata...")

    opf_path = item_dir / "standard.opf"
    if opf_path.exists():
        MetadataUpdater.update_opf_file(
            opf_path, target_lang, source_lang, book_title,
            detected_images, chapter_order
        )

    nav_path = item_dir / "navigation-documents.xhtml"
    if nav_path.exists():
        MetadataUpdater.update_navigation_file(
            nav_path, target_lang, source_lang,
            chapter_title_map, toc_title, cover_title
        )

    print("[OK] Metadata update complete.")
