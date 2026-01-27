"""
EPUB3 Navigation Generator - Creates nav.xhtml navigation document.

Generates the EPUB3 navigation document with:
- Table of Contents (toc nav)
- Landmarks (for semantic navigation)
"""

from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional
from html import escape


@dataclass
class TOCEntry:
    """Entry for table of contents navigation."""
    label: str
    href: str
    children: List['TOCEntry'] = field(default_factory=list)

    def to_html(self, indent: int = 3) -> str:
        """Generate HTML list item for this entry."""
        spaces = "      " * indent
        if self.children:
            children_html = "\n".join(child.to_html(indent + 1) for child in self.children)
            return f'''{spaces}<li>
{spaces}  <a href="{self.href}">{escape(self.label)}</a>
{spaces}  <ol>
{children_html}
{spaces}  </ol>
{spaces}</li>'''
        else:
            return f'{spaces}<li><a href="{self.href}">{escape(self.label)}</a></li>'


@dataclass
class Landmark:
    """Landmark entry for EPUB3 navigation."""
    epub_type: str    # "cover", "toc", "bodymatter", "backmatter"
    href: str
    title: str

    def to_html(self) -> str:
        """Generate HTML list item for this landmark."""
        return f'        <li><a epub:type="{self.epub_type}" href="{self.href}">{escape(self.title)}</a></li>'


class NavGenerator:
    """Generates EPUB3 nav.xhtml navigation documents."""

    def __init__(self, lang_code: str = "en"):
        """
        Initialize nav generator.

        Args:
            lang_code: Language code for HTML attributes
        """
        self.lang_code = lang_code

    def generate(
        self,
        output_path: Path,
        book_title: str,
        toc_entries: List[TOCEntry],
        landmarks: Optional[List[Landmark]] = None,
        toc_title: str = "Table of Contents"
    ) -> None:
        """
        Generate nav.xhtml file.

        Args:
            output_path: Path to write nav.xhtml
            book_title: Book title for <title> element
            toc_entries: List of TOC entries
            landmarks: List of landmarks (optional)
            toc_title: Title for TOC section
        """
        nav_content = self._build_nav(book_title, toc_entries, landmarks, toc_title)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(nav_content, encoding="utf-8")

    def _build_nav(
        self,
        book_title: str,
        toc_entries: List[TOCEntry],
        landmarks: Optional[List[Landmark]],
        toc_title: str
    ) -> str:
        """Build complete nav.xhtml document."""
        toc_html = self._build_toc_section(toc_entries, toc_title)
        landmarks_html = self._build_landmarks_section(landmarks) if landmarks else ""

        return f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>

<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:epub="http://www.idpf.org/2007/ops"
      lang="{self.lang_code}"
      xml:lang="{self.lang_code}">
<head>
  <meta charset="UTF-8"/>
  <title>{escape(book_title)}</title>
  <link href="../Styles/stylesheet.css" rel="stylesheet" type="text/css"/>
</head>

<body>
{toc_html}
{landmarks_html}
</body>
</html>
'''

    def _build_toc_section(self, entries: List[TOCEntry], toc_title: str) -> str:
        """Build table of contents nav section."""
        entries_html = "\n".join(entry.to_html(indent=1) for entry in entries)

        return f'''  <nav epub:type="toc" id="toc">
    <h1>{escape(toc_title)}</h1>
    <ol>
{entries_html}
    </ol>
  </nav>'''

    def _build_landmarks_section(self, landmarks: List[Landmark]) -> str:
        """Build landmarks nav section."""
        if not landmarks:
            return ""

        landmarks_html = "\n".join(lm.to_html() for lm in landmarks)

        return f'''
  <nav epub:type="landmarks" hidden="">
    <h2>Landmarks</h2>
    <ol>
{landmarks_html}
    </ol>
  </nav>'''


def generate_nav(
    output_path: Path,
    book_title: str,
    toc_entries: List[TOCEntry],
    landmarks: Optional[List[Landmark]] = None,
    lang_code: str = "en",
    toc_title: str = "Table of Contents"
) -> None:
    """
    Main function to generate nav.xhtml file.

    Args:
        output_path: Path to write nav.xhtml
        book_title: Book title
        toc_entries: List of TOC entries
        landmarks: List of landmarks (optional)
        lang_code: Language code
        toc_title: Title for TOC section
    """
    generator = NavGenerator(lang_code)
    generator.generate(output_path, book_title, toc_entries, landmarks, toc_title)


def create_toc_entries_from_chapters(
    chapters: List[dict],
    include_cover: bool = True,
    include_toc: bool = False
) -> List[TOCEntry]:
    """
    Create TOC entries from chapter list.

    Args:
        chapters: List of chapter dicts with 'title', 'xhtml_filename'
        include_cover: Include cover in TOC
        include_toc: Include TOC page itself in TOC

    Returns:
        List of TOCEntry objects
    """
    entries = []

    # Cover
    if include_cover:
        entries.append(TOCEntry(
            label="Cover",
            href="cover.xhtml"
        ))

    # TOC page
    if include_toc:
        entries.append(TOCEntry(
            label="Table of Contents",
            href="toc.xhtml"
        ))

    # Chapters
    for i, chapter in enumerate(chapters):
        title = chapter.get('title', f'Chapter {i+1}')
        filename = chapter.get('xhtml_filename', f'chapter{i+1:03d}.xhtml')

        entries.append(TOCEntry(
            label=title,
            href=filename
        ))

    return entries


def create_default_landmarks(first_chapter_href: str = "chapter001.xhtml") -> List[Landmark]:
    """
    Create default landmarks for an EPUB.

    Args:
        first_chapter_href: Href to first chapter

    Returns:
        List of standard landmarks
    """
    return [
        Landmark(epub_type="cover", href="cover.xhtml", title="Cover"),
        Landmark(epub_type="toc", href="nav.xhtml", title="Table of Contents"),
        Landmark(epub_type="bodymatter", href=first_chapter_href, title="Start of Content"),
    ]
