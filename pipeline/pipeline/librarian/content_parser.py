"""
Content Parser - Language-Agnostic Markdown Content Extraction.

Parses markdown files to extract clean content, skipping analysis logs
and translator notes. Works with any source/target language.
"""

from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class ParsedContent:
    """Container for extracted content."""
    main_title: str           # First # heading
    chapter_title: str        # First ## heading (if exists)
    paragraphs: List[str]     # Content paragraphs
    raw_content: str          # Full content text for reference


class ContentParser:
    """Parses markdown files and extracts clean content."""

    def __init__(
        self,
        skip_lines: int = 0,
        end_marker: Optional[str] = None
    ):
        """
        Initialize parser with language-specific settings.

        Args:
            skip_lines: Number of lines to skip at start (analysis header)
            end_marker: Optional marker indicating end of content
        """
        self.skip_lines = skip_lines
        self.end_marker = end_marker

    def parse_file(self, filepath: Path) -> ParsedContent:
        """
        Parse a markdown file and extract content.

        Args:
            filepath: Path to markdown file

        Returns:
            ParsedContent object with extracted content

        Raises:
            ValueError: If file format is unexpected
        """
        if not filepath.exists():
            raise ValueError(f"File does not exist: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Smart detection: Check if first non-empty line is a heading
        skip_lines = self._detect_skip_lines(lines)
        content_lines = lines[skip_lines:]

        # Find end marker if specified
        end_line_idx = len(content_lines)
        if self.end_marker:
            for idx, line in enumerate(content_lines):
                if self.end_marker in line:
                    end_line_idx = idx
                    break

        content_lines = content_lines[:end_line_idx]
        content_text = ''.join(content_lines).strip()

        if not content_text:
            raise ValueError(f"No content found in {filepath}")

        return self._parse_content(content_text)

    def _detect_skip_lines(self, lines: List[str]) -> int:
        """
        Auto-detect how many lines to skip based on content.

        Args:
            lines: All lines from file

        Returns:
            Number of lines to skip
        """
        for line in lines[:5]:  # Check first 5 lines
            stripped = line.strip()
            if stripped:  # First non-empty line
                if stripped.startswith('#'):
                    # No analysis header, starts with heading
                    return 0
                else:
                    # Has analysis header, skip configured lines
                    return self.skip_lines
        return 0

    def _parse_content(self, content_text: str) -> ParsedContent:
        """
        Parse the content text to extract structure.

        Args:
            content_text: Raw content text

        Returns:
            ParsedContent object with parsed structure
        """
        lines = content_text.split('\n')

        main_title = ""
        chapter_title = ""
        content_start_idx = 0

        # Find main title (first # heading)
        for idx, line in enumerate(lines):
            line_stripped = line.strip()
            if line_stripped.startswith('# ') and not main_title:
                main_title = self._clean_title(line_stripped[2:])
                content_start_idx = idx + 1
                break

        # Find chapter title (first ## heading after main title)
        for idx in range(content_start_idx, len(lines)):
            line_stripped = lines[idx].strip()
            if line_stripped.startswith('## ') and not chapter_title:
                chapter_title = self._clean_title(line_stripped[3:])
                content_start_idx = idx + 1
                break

        # Extract paragraphs from remaining content
        paragraphs = self._extract_paragraphs(lines[content_start_idx:])

        return ParsedContent(
            main_title=main_title,
            chapter_title=chapter_title,
            paragraphs=paragraphs,
            raw_content=content_text,
        )

    def _clean_title(self, title: str) -> str:
        """Remove markdown formatting from title."""
        title = title.strip()
        # Strip bold/italic markers
        title = title.replace('**', '').replace('*', '')
        title = title.replace('__', '').replace('_', '')
        return title

    def _extract_paragraphs(self, lines: List[str]) -> List[str]:
        """
        Extract paragraphs from lines, handling blank lines and markers.

        Args:
            lines: List of content lines

        Returns:
            List of paragraph strings (including blank line markers)
        """
        paragraphs = []
        current_paragraph = []

        for line in lines:
            line_stripped = line.rstrip()

            if not line_stripped:
                # Blank line - paragraph separator
                if current_paragraph:
                    paragraphs.append(''.join(current_paragraph).strip())
                    current_paragraph = []
                paragraphs.append("<blank>")
            elif line_stripped.startswith('#'):
                # Skip remaining headings
                if current_paragraph:
                    paragraphs.append(''.join(current_paragraph).strip())
                    current_paragraph = []
            else:
                current_paragraph.append(line_stripped + ' ')

        # Add final paragraph
        if current_paragraph:
            paragraphs.append(''.join(current_paragraph).strip())

        # Filter consecutive blank markers and trailing blanks
        return self._filter_blanks(paragraphs)

    def _filter_blanks(self, paragraphs: List[str]) -> List[str]:
        """Remove consecutive and trailing blank markers."""
        filtered = []
        for para in paragraphs:
            if para == "<blank>":
                if filtered and filtered[-1] != "<blank>":
                    filtered.append(para)
            else:
                filtered.append(para)

        # Remove trailing blanks
        while filtered and filtered[-1] == "<blank>":
            filtered.pop()

        return filtered

    @staticmethod
    def extract_chapter_title(filepath: Path) -> str:
        """
        Extract only the chapter title (## heading) from a markdown file.

        Args:
            filepath: Path to markdown file

        Returns:
            Chapter title string (without markdown formatting)
        """
        if not filepath.exists():
            return ""

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line_stripped = line.strip()
                    if line_stripped.startswith('## '):
                        title = line_stripped[3:].strip()
                        title = title.replace('**', '').replace('*', '')
                        return title
        except Exception:
            pass

        return ""


def parse_content_file(
    filepath: Path,
    skip_lines: int = 0,
    end_marker: str = None
) -> ParsedContent:
    """
    Main function to parse a content file.

    Args:
        filepath: Path to markdown file
        skip_lines: Lines to skip at start
        end_marker: Optional end marker

    Returns:
        ParsedContent object
    """
    parser = ContentParser(skip_lines, end_marker)
    return parser.parse_file(filepath)


def parse_all_content_files(
    content_dir: Path,
    pattern: str = "*.md",
    skip_lines: int = 0,
    end_marker: str = None
) -> dict:
    """
    Parse all markdown files in a directory.

    Args:
        content_dir: Directory containing markdown files
        pattern: Glob pattern for files
        skip_lines: Lines to skip at start
        end_marker: Optional end marker

    Returns:
        Dictionary mapping filename to ParsedContent objects
    """
    parser = ContentParser(skip_lines, end_marker)
    contents = {}

    for filepath in sorted(content_dir.glob(pattern)):
        try:
            contents[filepath.name] = parser.parse_file(filepath)
            print(f"[OK] Parsed {filepath.name}")
        except ValueError as e:
            print(f"[FAIL] Error parsing {filepath.name}: {e}")
            raise

    return contents
