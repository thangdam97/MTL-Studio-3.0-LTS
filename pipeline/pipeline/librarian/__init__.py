"""
Librarian Agent - EPUB extraction and content cataloging.

Responsible for:
1. Extracting source EPUBs to working directory
2. Parsing OPF metadata (title, author, language, TOC)
3. Converting XHTML chapters to markdown
4. Cataloging images and assets
5. Generating manifest.json for pipeline state

Language-agnostic - works with any source language.
"""

# EPUB Extraction
from .epub_extractor import EPUBExtractor, ExtractionResult, extract_epub

# Metadata Parsing
from .metadata_parser import MetadataParser, BookMetadata, parse_metadata, find_and_parse_metadata

# TOC Parsing
from .toc_parser import TOCParser, TableOfContents, NavPoint, parse_toc, get_chapter_order, get_chapter_titles

# Spine Parsing (reading order)
from .spine_parser import SpineParser, Spine, SpineItem, parse_spine, get_reading_order

# Content Parsing (markdown)
from .content_parser import ContentParser, ParsedContent, parse_content_file, parse_all_content_files

# XHTML to Markdown Conversion
from .xhtml_to_markdown import (
    XHTMLToMarkdownConverter,
    ConvertedChapter,
    convert_xhtml_to_markdown,
    convert_all_chapters
)

# Image Extraction
from .image_extractor import ImageExtractor, ImageInfo, catalog_images, extract_images_to_assets

# File Discovery
from .file_discovery import FileDiscovery, ChapterInfo, discover_files, build_file_mappings, build_title_mappings

# Main Agent
from .agent import LibrarianAgent, Manifest, ChapterEntry, run_librarian

__version__ = "1.0.0"

__all__ = [
    # EPUB Extraction
    "EPUBExtractor",
    "ExtractionResult",
    "extract_epub",
    # Metadata
    "MetadataParser",
    "BookMetadata",
    "parse_metadata",
    "find_and_parse_metadata",
    # TOC
    "TOCParser",
    "TableOfContents",
    "NavPoint",
    "parse_toc",
    "get_chapter_order",
    "get_chapter_titles",
    # Spine
    "SpineParser",
    "Spine",
    "SpineItem",
    "parse_spine",
    "get_reading_order",
    # Content Parsing
    "ContentParser",
    "ParsedContent",
    "parse_content_file",
    "parse_all_content_files",
    # XHTML Conversion
    "XHTMLToMarkdownConverter",
    "ConvertedChapter",
    "convert_xhtml_to_markdown",
    "convert_all_chapters",
    # Images
    "ImageExtractor",
    "ImageInfo",
    "catalog_images",
    "extract_images_to_assets",
    # File Discovery
    "FileDiscovery",
    "ChapterInfo",
    "discover_files",
    "build_file_mappings",
    "build_title_mappings",
    # Agent
    "LibrarianAgent",
    "Manifest",
    "ChapterEntry",
    "run_librarian",
]
