"""
TOC Parser - Parse EPUB navigation documents for chapter ordering.

Supports both EPUB2 (toc.ncx) and EPUB3 (nav.xhtml) navigation formats.
Extracts chapter titles and reading order for the pipeline.
"""

import re
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from lxml import etree

from .config import get_metadata_namespaces


@dataclass
class NavPoint:
    """Represents a navigation point (chapter/section)."""
    id: str
    label: str
    content_src: str
    play_order: int = 0
    level: int = 0
    children: List['NavPoint'] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "label": self.label,
            "content_src": self.content_src,
            "play_order": self.play_order,
            "level": self.level,
            "children": [child.to_dict() for child in self.children],
        }


@dataclass
class TableOfContents:
    """Container for parsed table of contents."""
    title: str = ""
    nav_points: List[NavPoint] = field(default_factory=list)
    source_file: str = ""
    format: str = ""  # "ncx" or "nav"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "title": self.title,
            "format": self.format,
            "source_file": self.source_file,
            "nav_points": [np.to_dict() for np in self.nav_points],
        }

    def get_flat_list(self) -> List[NavPoint]:
        """Get flattened list of all nav points in reading order."""
        result = []
        self._flatten(self.nav_points, result)
        return result

    def _flatten(self, points: List[NavPoint], result: List[NavPoint]):
        """Recursively flatten nav point tree."""
        for point in points:
            result.append(point)
            if point.children:
                self._flatten(point.children, result)

    def get_chapter_order(self) -> List[str]:
        """Get ordered list of content file references."""
        return [np.content_src for np in self.get_flat_list()]


class TOCParser:
    """Parses EPUB navigation documents."""

    # NCX namespace
    NCX_NS = {"ncx": "http://www.daisy.org/z3986/2005/ncx/"}

    # EPUB3 nav namespaces
    XHTML_NS = {"xhtml": "http://www.w3.org/1999/xhtml"}
    EPUB_NS = {"epub": "http://www.idpf.org/2007/ops"}

    def __init__(self, epub_root: Path):
        """
        Initialize parser.

        Args:
            epub_root: Root directory of extracted EPUB
        """
        self.epub_root = Path(epub_root)

    def parse(self) -> TableOfContents:
        """
        Parse TOC from EPUB, trying nav.xhtml first, then toc.ncx.

        Returns:
            TableOfContents object with parsed navigation
        """
        # Try EPUB3 nav.xhtml first
        nav_path = self._find_nav_xhtml()
        if nav_path:
            return self._parse_nav_xhtml(nav_path)

        # Fallback to EPUB2 toc.ncx
        ncx_path = self._find_ncx()
        if ncx_path:
            return self._parse_ncx(ncx_path)

        raise ValueError(f"No navigation document found in {self.epub_root}")

    def _find_nav_xhtml(self) -> Optional[Path]:
        """Find EPUB3 navigation document."""
        # Check common locations
        candidates = [
            "nav.xhtml", "navigation.xhtml",
            "OEBPS/nav.xhtml", "OEBPS/navigation.xhtml",
            "OPS/nav.xhtml", "EPUB/nav.xhtml",
            "item/nav.xhtml",
        ]
        for candidate in candidates:
            path = self.epub_root / candidate
            if path.exists():
                return path

        # Search for nav.xhtml
        for nav_path in self.epub_root.rglob("nav.xhtml"):
            return nav_path

        # Check OPF for nav reference
        return self._find_nav_from_opf()

    def _find_nav_from_opf(self) -> Optional[Path]:
        """Find navigation document referenced in OPF."""
        for opf_path in self.epub_root.rglob("*.opf"):
            try:
                tree = etree.parse(str(opf_path))
                root = tree.getroot()
                ns = {"opf": "http://www.idpf.org/2007/opf"}

                # Find item with properties="nav"
                for item in root.findall(".//opf:item", ns):
                    if "nav" in item.get("properties", ""):
                        href = item.get("href")
                        if href:
                            nav_path = opf_path.parent / href
                            if nav_path.exists():
                                return nav_path

                # Try without namespace
                for item in root.findall(".//item"):
                    if "nav" in item.get("properties", ""):
                        href = item.get("href")
                        if href:
                            nav_path = opf_path.parent / href
                            if nav_path.exists():
                                return nav_path
            except Exception:
                continue
        return None

    def _find_ncx(self) -> Optional[Path]:
        """Find EPUB2 NCX file."""
        candidates = [
            "toc.ncx", "OEBPS/toc.ncx", "OPS/toc.ncx",
            "EPUB/toc.ncx", "item/toc.ncx",
        ]
        for candidate in candidates:
            path = self.epub_root / candidate
            if path.exists():
                return path

        # Search for any .ncx file
        for ncx_path in self.epub_root.rglob("*.ncx"):
            return ncx_path

        return None

    def _parse_nav_xhtml(self, nav_path: Path) -> TableOfContents:
        """
        Parse EPUB3 nav.xhtml navigation document.

        Args:
            nav_path: Path to nav.xhtml

        Returns:
            TableOfContents object
        """
        tree = etree.parse(str(nav_path))
        root = tree.getroot()

        toc = TableOfContents(
            source_file=str(nav_path),
            format="nav"
        )

        # Find nav element with epub:type="toc"
        nav_elem = None
        for nav in root.iter("{http://www.w3.org/1999/xhtml}nav"):
            epub_type = nav.get("{http://www.idpf.org/2007/ops}type", "")
            if "toc" in epub_type:
                nav_elem = nav
                break

        if nav_elem is None:
            # Try without namespace
            for nav in root.iter("nav"):
                epub_type = nav.get("epub:type", nav.get("type", ""))
                if "toc" in epub_type:
                    nav_elem = nav
                    break

        if nav_elem is None:
            # Fallback: just find first nav
            nav_elem = root.find(".//{http://www.w3.org/1999/xhtml}nav")
            if nav_elem is None:
                nav_elem = root.find(".//nav")

        if nav_elem is not None:
            # Extract title from h2 or h1
            for heading in nav_elem.iter():
                if heading.tag.endswith(('h1', 'h2', 'h3')):
                    toc.title = self._get_text(heading)
                    break

            # Find the ol element
            ol_elem = nav_elem.find(".//{http://www.w3.org/1999/xhtml}ol")
            if ol_elem is None:
                ol_elem = nav_elem.find(".//ol")

            if ol_elem is not None:
                toc.nav_points = self._parse_nav_ol(ol_elem, nav_path.parent)

        return toc

    def _parse_nav_ol(self, ol_elem: etree._Element, base_path: Path, level: int = 0) -> List[NavPoint]:
        """Parse ol element from nav.xhtml."""
        nav_points = []
        play_order = 0

        for li in ol_elem:
            if not li.tag.endswith("li"):
                continue

            play_order += 1

            # Find anchor (may be wrapped in span or other elements)
            a_elem = li.find(".//{http://www.w3.org/1999/xhtml}a")
            if a_elem is None:
                a_elem = li.find(".//a")

            if a_elem is not None:
                href = a_elem.get("href", "")
                label = self._get_text(a_elem)

                nav_point = NavPoint(
                    id=f"nav_{play_order}",
                    label=label,
                    content_src=href,
                    play_order=play_order,
                    level=level,
                )

                # Check for nested ol
                nested_ol = li.find("{http://www.w3.org/1999/xhtml}ol")
                if nested_ol is None:
                    nested_ol = li.find("ol")
                if nested_ol is not None:
                    nav_point.children = self._parse_nav_ol(nested_ol, base_path, level + 1)

                nav_points.append(nav_point)

        return nav_points

    def _parse_ncx(self, ncx_path: Path) -> TableOfContents:
        """
        Parse EPUB2 toc.ncx navigation document.

        Args:
            ncx_path: Path to toc.ncx

        Returns:
            TableOfContents object
        """
        tree = etree.parse(str(ncx_path))
        root = tree.getroot()

        toc = TableOfContents(
            source_file=str(ncx_path),
            format="ncx"
        )

        # Extract docTitle
        doc_title = root.find("ncx:docTitle/ncx:text", self.NCX_NS)
        if doc_title is None:
            doc_title = root.find("{http://www.daisy.org/z3986/2005/ncx/}docTitle/{http://www.daisy.org/z3986/2005/ncx/}text")
        if doc_title is not None and doc_title.text:
            toc.title = doc_title.text.strip()

        # Find navMap
        nav_map = root.find("ncx:navMap", self.NCX_NS)
        if nav_map is None:
            nav_map = root.find("{http://www.daisy.org/z3986/2005/ncx/}navMap")

        if nav_map is not None:
            toc.nav_points = self._parse_ncx_navmap(nav_map)

        return toc

    def _parse_ncx_navmap(self, nav_map: etree._Element, level: int = 0) -> List[NavPoint]:
        """Parse navMap element from NCX."""
        nav_points = []
        ncx_ns = "{http://www.daisy.org/z3986/2005/ncx/}"

        for nav_point_elem in nav_map:
            if not nav_point_elem.tag.endswith("navPoint"):
                continue

            # Get attributes
            point_id = nav_point_elem.get("id", "")
            play_order = int(nav_point_elem.get("playOrder", 0))

            # Get label
            label_elem = nav_point_elem.find(f"{ncx_ns}navLabel/{ncx_ns}text")
            if label_elem is None:
                label_elem = nav_point_elem.find("ncx:navLabel/ncx:text", self.NCX_NS)
            label = label_elem.text.strip() if label_elem is not None and label_elem.text else ""

            # Get content src
            content_elem = nav_point_elem.find(f"{ncx_ns}content")
            if content_elem is None:
                content_elem = nav_point_elem.find("ncx:content", self.NCX_NS)
            content_src = content_elem.get("src", "") if content_elem is not None else ""

            nav_point = NavPoint(
                id=point_id,
                label=label,
                content_src=content_src,
                play_order=play_order,
                level=level,
            )

            # Recursively parse nested navPoints
            nav_point.children = self._parse_ncx_navmap(nav_point_elem, level + 1)

            nav_points.append(nav_point)

        return nav_points

    def _get_text(self, elem: etree._Element) -> str:
        """Get all text content from element and its children."""
        return ''.join(elem.itertext()).strip()


def parse_toc(epub_root: Path) -> TableOfContents:
    """
    Main function to parse table of contents from EPUB.

    Args:
        epub_root: Root directory of extracted EPUB

    Returns:
        TableOfContents object
    """
    parser = TOCParser(epub_root)
    return parser.parse()


def get_chapter_order(epub_root: Path) -> List[str]:
    """
    Get ordered list of chapter content files.

    Args:
        epub_root: Root directory of extracted EPUB

    Returns:
        List of content file paths in reading order
    """
    toc = parse_toc(epub_root)
    return toc.get_chapter_order()


def get_chapter_titles(epub_root: Path) -> Dict[str, str]:
    """
    Get mapping of content files to chapter titles.

    Args:
        epub_root: Root directory of extracted EPUB

    Returns:
        Dictionary mapping content_src to label
    """
    toc = parse_toc(epub_root)
    return {np.content_src: np.label for np in toc.get_flat_list()}
