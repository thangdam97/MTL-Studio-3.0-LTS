"""
NCX Generator - Creates EPUB2-compatible toc.ncx navigation.

Generates NCX (Navigation Control file for XML) for backward
compatibility with older e-readers that don't support EPUB3 navigation.
"""

from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional
from html import escape


@dataclass
class NavPoint:
    """Navigation point for NCX navMap."""
    id: str
    label: str
    src: str           # Relative path from NCX location
    play_order: int
    children: List['NavPoint'] = field(default_factory=list)

    def to_xml(self, indent: int = 2) -> str:
        """Generate XML element for this nav point."""
        spaces = "  " * indent
        lines = [f'{spaces}<navPoint id="{self.id}" playOrder="{self.play_order}">']
        lines.append(f'{spaces}  <navLabel>')
        lines.append(f'{spaces}    <text>{escape(self.label)}</text>')
        lines.append(f'{spaces}  </navLabel>')
        lines.append(f'{spaces}  <content src="{self.src}"/>')

        # Nested nav points
        for child in self.children:
            lines.append(child.to_xml(indent + 1))

        lines.append(f'{spaces}</navPoint>')

        return "\n".join(lines)


class NCXGenerator:
    """Generates EPUB2-compatible toc.ncx files."""

    def __init__(self):
        """Initialize NCX generator."""
        pass

    def generate(
        self,
        output_path: Path,
        book_title: str,
        identifier: str,
        nav_points: List[NavPoint],
        depth: int = 1
    ) -> None:
        """
        Generate complete toc.ncx file.

        Args:
            output_path: Path to write toc.ncx
            book_title: Book title for docTitle
            identifier: Unique identifier (same as OPF)
            nav_points: List of navigation points
            depth: Maximum nesting depth
        """
        ncx_content = self._build_ncx(book_title, identifier, nav_points, depth)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(ncx_content, encoding="utf-8")

    def _build_ncx(
        self,
        book_title: str,
        identifier: str,
        nav_points: List[NavPoint],
        depth: int
    ) -> str:
        """Build complete NCX document."""
        nav_map = self._build_nav_map(nav_points)

        return f'''<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="{escape(identifier)}"/>
    <meta name="dtb:depth" content="{depth}"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
  </head>
  <docTitle>
    <text>{escape(book_title)}</text>
  </docTitle>
  <navMap>
{nav_map}
  </navMap>
</ncx>
'''

    def _build_nav_map(self, nav_points: List[NavPoint]) -> str:
        """Build navMap content from navigation points."""
        return "\n".join(np.to_xml(indent=2) for np in nav_points)

    @staticmethod
    def create_nav_point(
        nav_id: str,
        label: str,
        src: str,
        play_order: int,
        children: Optional[List[NavPoint]] = None
    ) -> NavPoint:
        """
        Helper to create a NavPoint.

        Args:
            nav_id: Unique ID for the nav point
            label: Display label
            src: Relative path to content
            play_order: Reading order (1-based)
            children: Nested nav points

        Returns:
            NavPoint instance
        """
        return NavPoint(
            id=nav_id,
            label=label,
            src=src,
            play_order=play_order,
            children=children or []
        )


def generate_ncx(
    output_path: Path,
    book_title: str,
    identifier: str,
    nav_points: List[NavPoint]
) -> None:
    """
    Main function to generate toc.ncx file.

    Args:
        output_path: Path to write toc.ncx
        book_title: Book title
        identifier: Unique identifier
        nav_points: List of navigation points
    """
    generator = NCXGenerator()
    generator.generate(output_path, book_title, identifier, nav_points)


def create_nav_points_from_chapters(
    chapters: List[dict],
    include_cover: bool = True,
    include_toc: bool = True
) -> List[NavPoint]:
    """
    Create NCX nav points from chapter list.

    Args:
        chapters: List of chapter dictionaries with 'id', 'title', 'filename'
        include_cover: Include cover in navigation
        include_toc: Include TOC in navigation

    Returns:
        List of NavPoint objects
    """
    nav_points = []
    play_order = 1

    # Cover
    if include_cover:
        nav_points.append(NavPoint(
            id="nav_cover",
            label="Cover",
            src="Text/cover.xhtml",
            play_order=play_order
        ))
        play_order += 1

    # TOC
    if include_toc:
        nav_points.append(NavPoint(
            id="nav_toc",
            label="Table of Contents",
            src="Text/nav.xhtml",
            play_order=play_order
        ))
        play_order += 1

    # Chapters
    for i, chapter in enumerate(chapters):
        chapter_id = chapter.get('id', f'chapter_{i+1:02d}')
        title = chapter.get('title', f'Chapter {i+1}')
        filename = chapter.get('xhtml_filename', f'chapter{i+1:03d}.xhtml')

        nav_points.append(NavPoint(
            id=f"nav_{chapter_id}",
            label=title,
            src=f"Text/{filename}",
            play_order=play_order
        ))
        play_order += 1

    return nav_points
