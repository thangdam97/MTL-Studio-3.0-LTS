"""
EPUB Packager - Creates valid EPUB files from directory structure.

Packages the working directory into a valid EPUB3/EPUB2 file with
correct mimetype placement and compression.
"""

import zipfile
from pathlib import Path
from typing import List


class EPUBPackager:
    """Creates valid EPUB files from directory structure."""

    @staticmethod
    def package_epub(working_dir: Path, output_epub_path: Path) -> None:
        """
        Package a prepared EPUB directory into a .epub file.

        Args:
            working_dir: Directory containing EPUB structure
            output_epub_path: Path where to write the .epub file
        """
        output_epub_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"[INFO] Packaging EPUB: {output_epub_path.name}")

        with zipfile.ZipFile(
            output_epub_path,
            'w',
            zipfile.ZIP_DEFLATED,
        ) as epub_zip:
            # Add mimetype first, uncompressed (EPUB spec requirement)
            EPUBPackager._add_mimetype_first(epub_zip, working_dir)

            # Add all other files, compressed
            EPUBPackager._add_epub_contents(epub_zip, working_dir)

        if not output_epub_path.exists():
            raise IOError(f"Failed to create EPUB file: {output_epub_path}")

        file_size_mb = output_epub_path.stat().st_size / (1024 * 1024)
        print(f"[OK] EPUB created: {output_epub_path.name} ({file_size_mb:.2f} MB)")

    @staticmethod
    def _add_mimetype_first(epub_zip: zipfile.ZipFile, working_dir: Path) -> None:
        """Add mimetype file first (required for EPUB spec)."""
        mimetype_path = working_dir / "mimetype"

        if mimetype_path.exists():
            with open(mimetype_path, 'r', encoding='utf-8') as f:
                mimetype_content = f.read()

            epub_zip.writestr(
                zipfile.ZipInfo('mimetype'),
                mimetype_content,
                compress_type=zipfile.ZIP_STORED,
            )
        else:
            # Create default mimetype if it doesn't exist
            epub_zip.writestr(
                zipfile.ZipInfo('mimetype'),
                'application/epub+zip',
                compress_type=zipfile.ZIP_STORED,
            )

    @staticmethod
    def _add_epub_contents(epub_zip: zipfile.ZipFile, working_dir: Path) -> None:
        """Add all EPUB contents (except mimetype) to the ZIP."""
        for file_path in working_dir.rglob('*'):
            # Skip mimetype (already added) and directories
            if file_path.name == 'mimetype' or file_path.is_dir():
                continue

            relative_path = file_path.relative_to(working_dir)
            arcname = str(relative_path).replace('\\', '/')

            epub_zip.write(file_path, arcname, compress_type=zipfile.ZIP_DEFLATED)

    @staticmethod
    def validate_epub_structure(epub_path: Path) -> bool:
        """
        Validate basic EPUB structure.

        Args:
            epub_path: Path to EPUB file

        Returns:
            True if structure appears valid

        Raises:
            FileNotFoundError: If EPUB file doesn't exist
            ValueError: If structure is invalid
        """
        if not epub_path.exists():
            raise FileNotFoundError(f"EPUB file does not exist: {epub_path}")

        with zipfile.ZipFile(epub_path, 'r') as epub_zip:
            namelist = epub_zip.namelist()

            # Check required files
            required_files = [
                'mimetype',
                'META-INF/container.xml',
            ]

            for req_file in required_files:
                if req_file not in namelist:
                    raise ValueError(f"Missing required file in EPUB: {req_file}")

            # Check that mimetype is first
            if namelist[0] != 'mimetype':
                raise ValueError("mimetype must be first file in EPUB")

            # Find OPF file
            opf_files = [f for f in namelist if f.endswith('.opf')]
            if not opf_files:
                raise ValueError("No OPF file found in EPUB")

            # Check for content files
            xhtml_files = [f for f in namelist if f.endswith('.xhtml')]
            if not xhtml_files:
                raise ValueError("No XHTML content files found in EPUB")

            print(f"[OK] EPUB structure validated ({len(namelist)} files)")
            print(f"     - mimetype at position 0")
            print(f"     - {len(xhtml_files)} content files")
            print(f"     - OPF: {opf_files[0]}")

        return True


def create_epub_file(working_dir: Path, output_path: Path) -> None:
    """
    Main function to create EPUB file from working directory.

    Args:
        working_dir: Working directory with EPUB structure
        output_path: Path to write .epub file
    """
    packager = EPUBPackager()
    packager.package_epub(working_dir, output_path)
    packager.validate_epub_structure(output_path)
