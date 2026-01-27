"""
Spine Parser - Extract reading order from EPUB OPF spine.

Parses the spine element from OPF files to get the actual reading order,
which includes all content files (not just those in the TOC).

This is critical for EPUBs where:
- Illustrations are standalone XHTML files
- Chapter content is split across multiple XHTML files
- Reading order differs from TOC navigation order
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from lxml import etree


@dataclass
class SpineItem:
    """Represents a spine item (content file in reading order)."""
    idref: str                    # ID reference to manifest item
    href: str                     # Actual file path from manifest
    linear: bool = True           # Whether item is in linear reading order
    properties: List[str] = field(default_factory=list)  # rendition properties
    is_illustration: bool = False # Detected as illustration-only page

    def to_dict(self) -> Dict[str, Any]:
        return {
            "idref": self.idref,
            "href": self.href,
            "linear": self.linear,
            "properties": self.properties,
            "is_illustration": self.is_illustration,
        }


@dataclass
class Spine:
    """Container for parsed spine."""
    items: List[SpineItem] = field(default_factory=list)
    page_progression: str = "ltr"  # ltr or rtl
    source_file: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "page_progression": self.page_progression,
            "source_file": self.source_file,
            "items": [item.to_dict() for item in self.items],
        }

    def get_reading_order(self) -> List[str]:
        """Get ordered list of file hrefs in reading order."""
        return [item.href for item in self.items if item.linear]

    def get_content_files(self) -> List[str]:
        """Get non-illustration content files."""
        return [item.href for item in self.items if item.linear and not item.is_illustration]

    def get_illustration_files(self) -> List[str]:
        """Get illustration-only files."""
        return [item.href for item in self.items if item.is_illustration]


class SpineParser:
    """Parses EPUB OPF spine for reading order."""

    OPF_NS = {"opf": "http://www.idpf.org/2007/opf"}

    def __init__(self, opf_path: Path):
        """
        Initialize parser.

        Args:
            opf_path: Path to OPF file
        """
        self.opf_path = Path(opf_path)
        self.opf_dir = self.opf_path.parent

    def parse(self) -> Spine:
        """
        Parse spine from OPF file.

        Returns:
            Spine object with reading order
        """
        tree = etree.parse(str(self.opf_path))
        root = tree.getroot()

        spine = Spine(source_file=str(self.opf_path))

        # Build manifest lookup (idref -> href)
        manifest_map = self._parse_manifest(root)

        # Find spine element
        spine_elem = root.find("opf:spine", self.OPF_NS)
        if spine_elem is None:
            spine_elem = root.find("{http://www.idpf.org/2007/opf}spine")
        if spine_elem is None:
            spine_elem = root.find("spine")

        if spine_elem is None:
            raise ValueError(f"No spine element found in {self.opf_path}")

        # Get page progression direction
        spine.page_progression = spine_elem.get("page-progression-direction", "ltr")

        # Parse itemrefs (use findall to avoid iteration issues with lxml)
        itemrefs = spine_elem.findall("opf:itemref", self.OPF_NS)
        if not itemrefs:
            itemrefs = spine_elem.findall("{http://www.idpf.org/2007/opf}itemref")
        if not itemrefs:
            itemrefs = spine_elem.findall("itemref")

        for itemref in itemrefs:
            idref = itemref.get("idref", "")
            if not idref:
                continue

            # Look up href from manifest
            manifest_info = manifest_map.get(idref, {})
            href = manifest_info.get("href", "")
            properties_str = manifest_info.get("properties", "")

            # Parse itemref attributes
            linear = itemref.get("linear", "yes") != "no"
            item_properties = itemref.get("properties", "").split()

            # Detect illustration-only pages
            is_illustration = self._is_illustration_page(
                href,
                properties_str,
                item_properties
            )

            item = SpineItem(
                idref=idref,
                href=href,
                linear=linear,
                properties=item_properties,
                is_illustration=is_illustration,
            )
            spine.items.append(item)

        return spine

    def _parse_manifest(self, root: etree._Element) -> Dict[str, Dict[str, str]]:
        """Parse manifest to build id -> href/properties mapping."""
        manifest_map = {}

        # Find manifest element
        manifest = root.find("opf:manifest", self.OPF_NS)
        if manifest is None:
            manifest = root.find("{http://www.idpf.org/2007/opf}manifest")
        if manifest is None:
            manifest = root.find("manifest")

        if manifest is None:
            return manifest_map

        # Use findall to get all item children (avoids iteration issues with lxml)
        items = manifest.findall("opf:item", self.OPF_NS)
        if not items:
            items = manifest.findall("{http://www.idpf.org/2007/opf}item")
        if not items:
            items = manifest.findall("item")

        for item in items:
            item_id = item.get("id", "")
            href = item.get("href", "")
            media_type = item.get("media-type", "")
            properties = item.get("properties", "")

            if item_id:
                manifest_map[item_id] = {
                    "href": href,
                    "media_type": media_type,
                    "properties": properties,
                }

        return manifest_map

    def _is_illustration_page(
        self,
        href: str,
        manifest_props: str,
        itemref_props: List[str]
    ) -> bool:
        """
        Detect if a spine item is an illustration-only page.

        Heuristics:
        - Has 'svg' in manifest properties (SVG wrapper for image)
        - Has 'rendition:layout-pre-paginated' (fixed layout = usually image)
        - Small file that contains only an SVG/image element

        Args:
            href: File path
            manifest_props: Properties from manifest item
            itemref_props: Properties from spine itemref

        Returns:
            True if likely an illustration-only page
        """
        # Check manifest properties for SVG
        if "svg" in manifest_props:
            # SVG pages are typically illustration wrappers
            # But we need to verify by checking file size or content
            file_path = self.opf_dir / href
            if file_path.exists():
                # Small SVG-property files are illustration pages
                if file_path.stat().st_size < 2000:
                    return True

        # Check itemref for pre-paginated layout (common for illustrations)
        for prop in itemref_props:
            if "pre-paginated" in prop:
                # Pre-paginated items that are small are likely illustrations
                file_path = self.opf_dir / href
                if file_path.exists() and file_path.stat().st_size < 2000:
                    return True

        return False

    def detect_illustration_pages(self, spine: Spine) -> None:
        """
        Post-process spine to detect illustration pages by content analysis.

        This does deeper inspection for cases where manifest properties
        don't clearly indicate illustration pages.

        Args:
            spine: Spine object to update in place
        """
        from bs4 import BeautifulSoup

        for item in spine.items:
            if item.is_illustration:
                continue  # Already detected

            file_path = self.opf_dir / item.href
            if not file_path.exists():
                continue

            # Check file size first (quick filter)
            if file_path.stat().st_size > 2000:
                continue  # Too large to be illustration-only

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                soup = BeautifulSoup(content, 'xml')
                body = soup.find('body')

                if body is None:
                    continue

                # Check if body contains only SVG with image
                svg = body.find('svg')
                if svg:
                    # Check if SVG contains only an image element
                    image = svg.find('image')
                    if image:
                        # Check if there's no other significant content
                        text = body.get_text(strip=True)
                        if not text:
                            item.is_illustration = True

            except Exception:
                continue


def parse_spine(opf_path: Path) -> Spine:
    """
    Main function to parse spine from OPF file.

    Args:
        opf_path: Path to OPF file

    Returns:
        Spine object with reading order
    """
    parser = SpineParser(opf_path)
    spine = parser.parse()
    parser.detect_illustration_pages(spine)
    return spine


def get_reading_order(opf_path: Path) -> List[str]:
    """
    Get ordered list of content files from OPF spine.

    Args:
        opf_path: Path to OPF file

    Returns:
        List of file paths in reading order
    """
    spine = parse_spine(opf_path)
    return spine.get_reading_order()
