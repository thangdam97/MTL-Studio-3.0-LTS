"""
Font Processor - Embeds fonts into EPUB.

Copies font files to EPUB directory and generates @font-face CSS declarations.
"""

import shutil
from pathlib import Path
from typing import Optional

from .config import get_fonts_to_embed, get_fonts_config, FONT_FACE_CSS_TEMPLATE


class FontProcessor:
    """Handles font processing and embedding."""

    @staticmethod
    def copy_fonts_to_epub(working_dir: Path, source_fonts_dir: Path) -> Path:
        """
        Copy font files to EPUB fonts directory.

        Args:
            working_dir: Working directory for EPUB contents
            source_fonts_dir: Directory containing source font files

        Returns:
            Path to fonts directory in EPUB
        """
        fonts_config = get_fonts_config()
        if not fonts_config.get('enabled', True):
            print("[INFO] Font embedding disabled in configuration")
            return working_dir / "fonts"

        fonts_dir = working_dir / "fonts"
        fonts_dir.mkdir(parents=True, exist_ok=True)

        fonts_to_embed = get_fonts_to_embed()

        print("[INFO] Copying fonts to EPUB...")
        for font_filename in fonts_to_embed.keys():
            source_path = source_fonts_dir / font_filename
            dest_path = fonts_dir / font_filename

            if not source_path.exists():
                print(f"  [WARN] Font file not found: {source_path}")
                continue

            shutil.copy2(source_path, dest_path)
            size_kb = dest_path.stat().st_size / 1024
            print(f"  [OK] Copied {font_filename} ({size_kb:.1f} KB)")

        return fonts_dir

    @staticmethod
    def generate_font_css() -> str:
        """
        Generate @font-face CSS declarations for all fonts.

        Returns:
            CSS string with @font-face rules
        """
        fonts_to_embed = get_fonts_to_embed()
        css_declarations = ['@charset "UTF-8";\n']

        for filename, font_info in fonts_to_embed.items():
            css_decl = FONT_FACE_CSS_TEMPLATE.format(
                font_family=font_info["font_family"],
                filename=filename,
                font_weight=font_info["font_weight"],
                font_style=font_info["font_style"],
            )
            css_declarations.append(css_decl)

        return '\n'.join(css_declarations)

    @staticmethod
    def create_fonts_css_file(working_dir: Path) -> Path:
        """
        Create fonts.css file with @font-face declarations.

        Args:
            working_dir: Working directory for EPUB contents

        Returns:
            Path to created fonts.css file
        """
        fonts_css_path = working_dir / "style" / "fonts.css"
        fonts_css_path.parent.mkdir(parents=True, exist_ok=True)

        css_content = FontProcessor.generate_font_css()

        with open(fonts_css_path, 'w', encoding='utf-8') as f:
            f.write(css_content)

        print(f"[OK] Created fonts.css: {fonts_css_path}")
        return fonts_css_path

    @staticmethod
    def calculate_total_font_size(source_fonts_dir: Path) -> float:
        """
        Calculate total size of all fonts to embed.

        Args:
            source_fonts_dir: Directory containing source font files

        Returns:
            Total size in MB
        """
        fonts_to_embed = get_fonts_to_embed()
        total_bytes = 0

        for font_filename in fonts_to_embed.keys():
            font_path = source_fonts_dir / font_filename
            if font_path.exists():
                total_bytes += font_path.stat().st_size

        return total_bytes / (1024 * 1024)

    @staticmethod
    def validate_fonts(source_fonts_dir: Path) -> bool:
        """
        Validate that all required fonts exist.

        Args:
            source_fonts_dir: Directory containing source font files

        Returns:
            True if all fonts found

        Raises:
            FileNotFoundError: If any font is missing
        """
        fonts_to_embed = get_fonts_to_embed()
        missing_fonts = []

        for font_filename in fonts_to_embed.keys():
            font_path = source_fonts_dir / font_filename
            if not font_path.exists():
                missing_fonts.append(font_filename)

        if missing_fonts:
            raise FileNotFoundError(
                f"Missing font files: {', '.join(missing_fonts)}"
            )

        return True


def copy_fonts_to_output(working_dir: Path, source_fonts_dir: Path) -> Path:
    """Main function to copy fonts to EPUB directory."""
    return FontProcessor.copy_fonts_to_epub(working_dir, source_fonts_dir)


def create_font_css_file(working_dir: Path) -> Path:
    """Main function to create fonts.css file."""
    return FontProcessor.create_fonts_css_file(working_dir)
