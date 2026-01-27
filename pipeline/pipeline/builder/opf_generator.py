"""
OPF Generator - Creates industry-standard package.opf files.

Generates EPUB 3.0 compliant OPF (Open Packaging Format) files
following Yen Press / J-Novel Club conventions.
"""

import uuid
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Optional
from html import escape


@dataclass
class BookMetadata:
    """Book metadata for OPF generation."""
    title: str
    author: str
    language: str = "en"
    publisher: str = ""
    identifier: str = ""  # UUID or ISBN
    date: str = ""
    rights: str = ""
    series: str = ""
    series_index: Optional[int] = None
    translator: str = ""
    illustrator: str = ""

    def __post_init__(self):
        """Generate identifier if not provided."""
        if not self.identifier:
            self.identifier = f"urn:uuid:{uuid.uuid4()}"
        if not self.date:
            self.date = datetime.now().strftime("%Y-%m-%d")


@dataclass
class ManifestItem:
    """Item entry for OPF manifest."""
    id: str
    href: str
    media_type: str
    properties: Optional[str] = None  # "nav", "cover-image", etc.

    def to_xml(self) -> str:
        """Generate XML element for this item."""
        props = f' properties="{self.properties}"' if self.properties else ""
        return f'    <item id="{self.id}" href="{self.href}" media-type="{self.media_type}"{props}/>'


@dataclass
class SpineItem:
    """Item entry for OPF spine."""
    idref: str
    linear: str = "yes"  # "yes" or "no"

    def to_xml(self) -> str:
        """Generate XML element for this item."""
        linear_attr = f' linear="{self.linear}"' if self.linear != "yes" else ""
        return f'    <itemref idref="{self.idref}"{linear_attr}/>'


class OPFGenerator:
    """Generates EPUB 3.0 compliant package.opf files."""

    def __init__(self, epub_version: str = "3.0"):
        """
        Initialize OPF generator.

        Args:
            epub_version: EPUB version (default: "3.0")
        """
        self.epub_version = epub_version

    def generate(
        self,
        output_path: Path,
        metadata: BookMetadata,
        manifest_items: List[ManifestItem],
        spine_items: List[SpineItem],
        cover_image_id: Optional[str] = None
    ) -> None:
        """
        Generate complete package.opf file.

        Args:
            output_path: Path to write package.opf
            metadata: Book metadata
            manifest_items: List of manifest entries
            spine_items: List of spine entries
            cover_image_id: ID of cover image for meta tag
        """
        opf_content = self._build_opf(
            metadata, manifest_items, spine_items, cover_image_id
        )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(opf_content, encoding="utf-8")

    def _build_opf(
        self,
        metadata: BookMetadata,
        manifest_items: List[ManifestItem],
        spine_items: List[SpineItem],
        cover_image_id: Optional[str]
    ) -> str:
        """Build complete OPF document."""
        metadata_section = self._build_metadata_section(metadata, cover_image_id)
        manifest_section = self._build_manifest_section(manifest_items)
        spine_section = self._build_spine_section(spine_items)

        return f'''<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf"
         xmlns:dc="http://purl.org/dc/elements/1.1/"
         version="{self.epub_version}"
         unique-identifier="pub-id"
         xml:lang="{metadata.language}">

{metadata_section}

{manifest_section}

{spine_section}

</package>
'''

    def _build_metadata_section(
        self,
        metadata: BookMetadata,
        cover_image_id: Optional[str]
    ) -> str:
        """Build Dublin Core metadata section."""
        lines = ["  <metadata>"]

        # Required elements
        lines.append(f'    <dc:identifier id="pub-id">{escape(metadata.identifier)}</dc:identifier>')
        lines.append(f'    <dc:title>{escape(metadata.title)}</dc:title>')
        lines.append(f'    <dc:language>{metadata.language}</dc:language>')

        # Creator (author)
        if metadata.author:
            lines.append(f'    <dc:creator id="creator01">{escape(metadata.author)}</dc:creator>')
            lines.append('    <meta refines="#creator01" property="role" scheme="marc:relators">aut</meta>')

        # Illustrator
        if metadata.illustrator:
            lines.append(f'    <dc:creator id="creator02">{escape(metadata.illustrator)}</dc:creator>')
            lines.append('    <meta refines="#creator02" property="role" scheme="marc:relators">ill</meta>')

        # Translator
        if metadata.translator:
            lines.append(f'    <dc:creator id="creator03">{escape(metadata.translator)}</dc:creator>')
            lines.append('    <meta refines="#creator03" property="role" scheme="marc:relators">trl</meta>')

        # Publisher
        if metadata.publisher:
            lines.append(f'    <dc:publisher>{escape(metadata.publisher)}</dc:publisher>')

        # Date
        if metadata.date:
            lines.append(f'    <dc:date>{metadata.date}</dc:date>')

        # Rights
        if metadata.rights:
            lines.append(f'    <dc:rights>{escape(metadata.rights)}</dc:rights>')

        # Series metadata (calibre compatible)
        if metadata.series:
            lines.append(f'    <meta property="belongs-to-collection" id="series01">{escape(metadata.series)}</meta>')
            lines.append('    <meta refines="#series01" property="collection-type">series</meta>')
            if metadata.series_index is not None:
                lines.append(f'    <meta refines="#series01" property="group-position">{metadata.series_index}</meta>')

        # Modified timestamp (required for EPUB3)
        modified = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        lines.append(f'    <meta property="dcterms:modified">{modified}</meta>')

        # Cover image meta
        if cover_image_id:
            lines.append(f'    <meta name="cover" content="{cover_image_id}"/>')

        lines.append("  </metadata>")

        return "\n".join(lines)

    def _build_manifest_section(self, items: List[ManifestItem]) -> str:
        """Build manifest with all resources."""
        lines = ["  <manifest>"]

        for item in items:
            lines.append(item.to_xml())

        lines.append("  </manifest>")

        return "\n".join(lines)

    def _build_spine_section(
        self,
        items: List[SpineItem],
        toc_id: str = "ncx"
    ) -> str:
        """Build spine in reading order."""
        lines = [f'  <spine toc="{toc_id}" page-progression-direction="ltr">']

        for item in items:
            lines.append(item.to_xml())

        lines.append("  </spine>")

        return "\n".join(lines)


def generate_opf(
    output_path: Path,
    metadata: BookMetadata,
    manifest_items: List[ManifestItem],
    spine_items: List[SpineItem],
    cover_image_id: Optional[str] = None
) -> None:
    """
    Main function to generate package.opf file.

    Args:
        output_path: Path to write package.opf
        metadata: Book metadata
        manifest_items: List of manifest entries
        spine_items: List of spine entries
        cover_image_id: ID of cover image for meta tag
    """
    generator = OPFGenerator()
    generator.generate(output_path, metadata, manifest_items, spine_items, cover_image_id)
