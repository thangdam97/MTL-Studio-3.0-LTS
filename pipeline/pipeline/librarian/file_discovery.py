"""
File Discovery - Language-Agnostic Chapter File Discovery.

Dynamically discovers and maps markdown files to XHTML output files.
Works with any naming pattern (Chapter, Chương, 第章, etc.)
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from .config import get_chapter_patterns


@dataclass
class ChapterInfo:
    """Information about a discovered chapter."""
    filename: str
    filepath: Path
    chapter_type: str  # chapter, interlude, epilogue, prologue, afterword
    number: Optional[int]
    title: str
    xhtml_file: str


class FileDiscovery:
    """Discovers and maps translation files dynamically."""

    # Generic chapter patterns (expanded for multiple languages)
    CHAPTER_PATTERN = re.compile(
        r'^(?:Chapter|Chương|第)\s*(\d+)[_:\s]?\s*(.*)$',
        re.IGNORECASE
    )
    INTERLUDE_PATTERN = re.compile(
        r'^(?:Interlude|Gián[- ]?Khúc|幕間|막간)\s*(\d+)?[_:\s]?\s*(.*)$',
        re.IGNORECASE
    )
    EPILOGUE_PATTERN = re.compile(
        r'^(?:Epilogue|Chương[- ]?Kết|エピローグ|終章)[_:\s]?\s*(.*)$',
        re.IGNORECASE
    )
    PROLOGUE_PATTERN = re.compile(
        r'^(?:Prologue|Lời[- ]?Mở[- ]?Đầu|プロローグ|序章)[_:\s]?\s*(.*)$',
        re.IGNORECASE
    )
    AFTERWORD_PATTERN = re.compile(
        r'^(?:Afterword|Lời[- ]?Bạt|あとがき|後記)[_:\s]?\s*(.*)$',
        re.IGNORECASE
    )

    def __init__(self, source_dir: Path):
        """
        Initialize file discovery.

        Args:
            source_dir: Directory containing markdown files
        """
        self.source_dir = Path(source_dir)

    def discover_all(self) -> List[ChapterInfo]:
        """
        Discover all chapter files and determine reading order.

        Returns:
            List of ChapterInfo objects in reading order
        """
        if not self.source_dir.exists():
            return []

        chapters = []
        interludes = []
        special = []  # prologue, epilogue, afterword

        for md_file in self.source_dir.glob("*.md"):
            info = self._classify_file(md_file)
            if info:
                if info.chapter_type == "chapter":
                    chapters.append(info)
                elif info.chapter_type == "interlude":
                    interludes.append(info)
                else:
                    special.append(info)

        # Sort by number
        chapters.sort(key=lambda x: x.number or 0)
        interludes.sort(key=lambda x: x.number or 0)

        # Build reading order and assign XHTML files
        return self._build_reading_order(chapters, interludes, special)

    def _classify_file(self, filepath: Path) -> Optional[ChapterInfo]:
        """Classify a markdown file by its name."""
        stem = filepath.stem

        # Check chapter pattern
        match = self.CHAPTER_PATTERN.match(stem)
        if match:
            num = int(match.group(1))
            title = match.group(2).strip(' _:')
            return ChapterInfo(
                filename=filepath.name,
                filepath=filepath,
                chapter_type="chapter",
                number=num,
                title=f"Chapter {num}: {title}" if title else f"Chapter {num}",
                xhtml_file=""
            )

        # Check interlude pattern
        match = self.INTERLUDE_PATTERN.match(stem)
        if match:
            num = int(match.group(1)) if match.group(1) else 1
            title = match.group(2).strip(' _:') if match.group(2) else ""
            return ChapterInfo(
                filename=filepath.name,
                filepath=filepath,
                chapter_type="interlude",
                number=num,
                title=f"Interlude {num}: {title}" if title else f"Interlude {num}",
                xhtml_file=""
            )

        # Check epilogue pattern
        match = self.EPILOGUE_PATTERN.match(stem)
        if match:
            title = match.group(1).strip(' _:') if match.group(1) else ""
            return ChapterInfo(
                filename=filepath.name,
                filepath=filepath,
                chapter_type="epilogue",
                number=None,
                title=f"Epilogue: {title}" if title else "Epilogue",
                xhtml_file=""
            )

        # Check prologue pattern
        match = self.PROLOGUE_PATTERN.match(stem)
        if match:
            title = match.group(1).strip(' _:') if match.group(1) else ""
            return ChapterInfo(
                filename=filepath.name,
                filepath=filepath,
                chapter_type="prologue",
                number=None,
                title=f"Prologue: {title}" if title else "Prologue",
                xhtml_file=""
            )

        # Check afterword pattern
        match = self.AFTERWORD_PATTERN.match(stem)
        if match:
            title = match.group(1).strip(' _:') if match.group(1) else ""
            return ChapterInfo(
                filename=filepath.name,
                filepath=filepath,
                chapter_type="afterword",
                number=None,
                title=f"Afterword: {title}" if title else "Afterword",
                xhtml_file=""
            )

        return None

    def _build_reading_order(
        self,
        chapters: List[ChapterInfo],
        interludes: List[ChapterInfo],
        special: List[ChapterInfo]
    ) -> List[ChapterInfo]:
        """
        Build reading order and assign XHTML file indices.

        Standard light novel structure:
        1. Prologue (if exists)
        2. Chapters with interludes interspersed
        3. Epilogue (if exists)
        4. Afterword (if exists)
        """
        ordered = []
        xhtml_index = 1

        # Add prologue first
        prologue = next((s for s in special if s.chapter_type == "prologue"), None)
        if prologue:
            prologue.xhtml_file = f"p-{xhtml_index:03d}.xhtml"
            ordered.append(prologue)
            xhtml_index += 1

        # Interleave chapters and interludes
        interlude_idx = 0
        for chapter in chapters:
            chapter.xhtml_file = f"p-{xhtml_index:03d}.xhtml"
            ordered.append(chapter)
            xhtml_index += 1

            # Check if an interlude comes after this chapter
            # Common patterns: after ch3 (interlude1), after ch5 (interlude2)
            if interlude_idx < len(interludes):
                interlude = interludes[interlude_idx]
                # Insert interlude after certain chapters (configurable)
                if self._should_insert_interlude(chapter.number, interlude.number):
                    interlude.xhtml_file = f"p-{xhtml_index:03d}.xhtml"
                    ordered.append(interlude)
                    xhtml_index += 1
                    interlude_idx += 1

        # Add any remaining interludes
        while interlude_idx < len(interludes):
            interlude = interludes[interlude_idx]
            interlude.xhtml_file = f"p-{xhtml_index:03d}.xhtml"
            ordered.append(interlude)
            xhtml_index += 1
            interlude_idx += 1

        # Add epilogue
        epilogue = next((s for s in special if s.chapter_type == "epilogue"), None)
        if epilogue:
            epilogue.xhtml_file = f"p-{xhtml_index:03d}.xhtml"
            ordered.append(epilogue)
            xhtml_index += 1

        # Add afterword
        afterword = next((s for s in special if s.chapter_type == "afterword"), None)
        if afterword:
            afterword.xhtml_file = f"p-{xhtml_index:03d}.xhtml"
            ordered.append(afterword)
            xhtml_index += 1

        return ordered

    def _should_insert_interlude(self, chapter_num: int, interlude_num: int) -> bool:
        """
        Determine if interlude should be inserted after this chapter.

        Common light novel pattern:
        - Interlude 1 after Chapter 3
        - Interlude 2 after Chapter 5
        """
        # Default pattern (can be customized)
        interlude_positions = {
            1: 3,  # Interlude 1 after Chapter 3
            2: 5,  # Interlude 2 after Chapter 5
        }
        return interlude_positions.get(interlude_num) == chapter_num


def discover_files(source_dir: Path) -> List[ChapterInfo]:
    """
    Main function to discover chapter files.

    Args:
        source_dir: Directory containing markdown files

    Returns:
        List of ChapterInfo objects in reading order
    """
    discovery = FileDiscovery(source_dir)
    return discovery.discover_all()


def build_file_mappings(source_dir: Path) -> Dict[str, str]:
    """
    Build mapping from markdown filename to XHTML filename.

    Args:
        source_dir: Directory containing markdown files

    Returns:
        Dictionary mapping markdown filename to XHTML filename
    """
    chapters = discover_files(source_dir)
    return {ch.filename: ch.xhtml_file for ch in chapters}


def build_title_mappings(source_dir: Path) -> Dict[str, str]:
    """
    Build mapping from XHTML filename to chapter title.

    Args:
        source_dir: Directory containing markdown files

    Returns:
        Dictionary mapping XHTML filename to chapter title
    """
    chapters = discover_files(source_dir)
    return {ch.xhtml_file: ch.title for ch in chapters}


def extract_title_from_filename(filename: str) -> str:
    """
    Extract chapter title from filename.

    Converts "Chapter 1_ A Rare Late-Night Event.md"
    to "Chapter 1: A Rare Late-Night Event"

    Args:
        filename: Markdown filename

    Returns:
        Formatted chapter title
    """
    stem = Path(filename).stem
    # Replace "_ " with ": " for cleaner title
    return stem.replace("_ ", ": ")
