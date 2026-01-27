"""
EPUB Structure Creator - Industry-standard OEBPS directory structure.

Creates the directory structure following Yen Press / J-Novel Club standards:
- OEBPS/ content root (not item/)
- Standard subdirectories: Text/, Images/, Styles/, Fonts/
"""

import shutil
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class EPUBPaths:
    """Container for all EPUB structure paths."""
    root: Path              # build_dir/
    mimetype: Path          # build_dir/mimetype
    meta_inf: Path          # build_dir/META-INF/
    container: Path         # build_dir/META-INF/container.xml
    oebps: Path             # build_dir/OEBPS/
    package_opf: Path       # build_dir/OEBPS/package.opf
    toc_ncx: Path           # build_dir/OEBPS/toc.ncx
    text_dir: Path          # build_dir/OEBPS/Text/
    images_dir: Path        # build_dir/OEBPS/Images/
    styles_dir: Path        # build_dir/OEBPS/Styles/
    fonts_dir: Path         # build_dir/OEBPS/Fonts/


# container.xml template - points to OEBPS/package.opf
CONTAINER_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/package.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
'''


class EPUBStructure:
    """Creates industry-standard EPUB directory structure."""

    def __init__(self, build_dir: Path):
        """
        Initialize with build directory path.

        Args:
            build_dir: Directory where EPUB will be built
        """
        self.build_dir = Path(build_dir)

    def create_structure(self) -> EPUBPaths:
        """
        Create complete OEBPS directory structure.

        Returns:
            EPUBPaths object with all path references
        """
        # Create paths object
        paths = EPUBPaths(
            root=self.build_dir,
            mimetype=self.build_dir / "mimetype",
            meta_inf=self.build_dir / "META-INF",
            container=self.build_dir / "META-INF" / "container.xml",
            oebps=self.build_dir / "OEBPS",
            package_opf=self.build_dir / "OEBPS" / "package.opf",
            toc_ncx=self.build_dir / "OEBPS" / "toc.ncx",
            text_dir=self.build_dir / "OEBPS" / "Text",
            images_dir=self.build_dir / "OEBPS" / "Images",
            styles_dir=self.build_dir / "OEBPS" / "Styles",
            fonts_dir=self.build_dir / "OEBPS" / "Fonts",
        )

        # Create directories
        self.build_dir.mkdir(parents=True, exist_ok=True)
        paths.meta_inf.mkdir(exist_ok=True)
        paths.oebps.mkdir(exist_ok=True)
        paths.text_dir.mkdir(exist_ok=True)
        paths.images_dir.mkdir(exist_ok=True)
        paths.styles_dir.mkdir(exist_ok=True)
        paths.fonts_dir.mkdir(exist_ok=True)

        # Create mimetype file (no newline at end - EPUB spec)
        paths.mimetype.write_text("application/epub+zip", encoding="utf-8")

        # Create container.xml
        paths.container.write_text(CONTAINER_XML, encoding="utf-8")

        return paths

    def clean_build_dir(self) -> None:
        """Remove existing build directory if present."""
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)


def create_epub_structure(build_dir: Path, clean: bool = True) -> EPUBPaths:
    """
    Main function to create EPUB directory structure.

    Args:
        build_dir: Directory where EPUB will be built
        clean: If True, remove existing build directory first

    Returns:
        EPUBPaths object with all path references
    """
    structure = EPUBStructure(build_dir)

    if clean:
        structure.clean_build_dir()

    return structure.create_structure()
