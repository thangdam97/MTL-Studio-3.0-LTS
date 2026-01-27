"""
Image Handler - Extracts and processes illustrations.

Detects full-page illustrations, extracts dimensions, handles orientation,
and creates dedicated insert pages.
"""

import re
import struct
import imghdr
from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass, field
from html import escape

from .config import get_epub_version


def get_jpeg_dimensions(image_path: Path) -> Tuple[int, int]:
    """
    Extract dimensions from JPEG image.

    Args:
        image_path: Path to JPEG image

    Returns:
        Tuple of (width, height)
    """
    try:
        with open(image_path, 'rb') as f:
            head = f.read(24)
            if len(head) != 24:
                return (0, 0)

            if imghdr.what(image_path) == 'jpeg':
                f.seek(0)
                size = 2
                ftype = 0
                while not 0xc0 <= ftype <= 0xcf:
                    f.seek(size, 1)
                    byte = f.read(1)
                    while ord(byte) == 0xff:
                        byte = f.read(1)
                    ftype = ord(byte)
                    size = struct.unpack('>H', f.read(2))[0] - 2
                f.seek(1, 1)
                height, width = struct.unpack('>HH', f.read(4))
                return (width, height)
    except Exception:
        pass

    return (0, 0)


def detect_image_orientation(image_path: Path) -> str:
    """
    Detect if image is portrait or landscape.

    Args:
        image_path: Path to image file

    Returns:
        'portrait' or 'landscape'
    """
    try:
        width, height = get_jpeg_dimensions(image_path)
        if width > 0 and height > 0:
            return 'landscape' if width > height else 'portrait'
    except Exception as e:
        print(f"  [WARN] Could not detect orientation for {image_path.name}: {e}")

    return 'portrait'


def is_scene_break_icon(image_path: Path) -> bool:
    """
    Detect if an image is a scene break icon rather than a full illustration.
    
    Scene break icons are small decorative images used as section dividers.
    They should be converted to text scene breaks (***) instead of <img> tags.
    
    Detection criteria:
    - File size < 10KB (most scene breaks are tiny)
    - Dimensions < 200x200 pixels (small decorative elements)
    - Exclude gaiji files (128x128 special character glyphs)
    
    Args:
        image_path: Path to image file
    
    Returns:
        True if image appears to be a scene break icon
    """
    try:
        # Check file size (scene breaks are typically very small)
        file_size = image_path.stat().st_size
        if file_size > 10240:  # 10KB threshold
            return False
        
        # Gaiji files (inline text glyphs) should NOT be treated as scene breaks
        # Pattern: gaiji-*.png (128x128 special characters like dakuten)
        if image_path.name.startswith('gaiji-'):
            return False
        
        # Check dimensions
        width, height = get_jpeg_dimensions(image_path)
        if width == 0 or height == 0:
            # Can't determine dimensions, assume not a scene break
            return False
        
        # Scene breaks are typically small and roughly square
        max_dimension = max(width, height)
        if max_dimension < 200:  # Small decorative element
            print(f"  [SCENE BREAK] Detected small icon: {image_path.name} ({width}x{height}, {file_size} bytes)")
            return True
        
    except Exception as e:
        print(f"  [WARN] Could not analyze {image_path.name}: {e}")
    
    return False


@dataclass
class ImageInfo:
    """Information about an extracted image."""

    image_filename: str
    source_chapter: str
    insert_number: int
    alt_text: str = ""
    orientation: str = "portrait"

    @property
    def insert_id(self) -> str:
        return f"insert-{self.insert_number:03d}"

    @property
    def xhtml_filename(self) -> str:
        return f"p-insert-{self.insert_number:03d}.xhtml"

    def __repr__(self):
        return f"ImageInfo({self.image_filename} -> {self.xhtml_filename}, {self.orientation})"


class ImageHandler:
    """Handles image extraction and insert page creation."""

    # Pattern to match inline image tags
    IMAGE_PATTERN = re.compile(
        r'<img\s+[^>]*src="[^"]*/(i-\d+\.jpg)"[^>]*>',
        re.IGNORECASE
    )

    # Pattern for full-page illustration filenames
    FULLPAGE_IMAGE_PATTERN = re.compile(r'^i-\d+\.jpg$', re.IGNORECASE)

    @staticmethod
    def scan_for_illustrations(content_dir: Path, chapter_range: range = None) -> List[ImageInfo]:
        """
        Scan EPUB content to find all full-page illustrations.

        Args:
            content_dir: Path to EPUB content directory
            chapter_range: Range of chapter numbers to scan (default: 1-9)

        Returns:
            List of ImageInfo objects for detected illustrations
        """
        if chapter_range is None:
            chapter_range = range(1, 10)

        xhtml_dir = content_dir / "xhtml"
        image_dir = content_dir / "image"

        if not xhtml_dir.exists():
            return []

        images = []
        insert_counter = 1

        for i in chapter_range:
            xhtml_file = xhtml_dir / f"p-{i:03d}.xhtml"
            if not xhtml_file.exists():
                continue

            try:
                content = xhtml_file.read_text(encoding='utf-8')
                matches = ImageHandler.IMAGE_PATTERN.finditer(content)

                for match in matches:
                    image_filename = match.group(1)

                    if ImageHandler.FULLPAGE_IMAGE_PATTERN.match(image_filename):
                        orientation = 'portrait'
                        image_path = image_dir / image_filename

                        if image_path.exists():
                            # Skip scene break icons (convert to *** instead)
                            if is_scene_break_icon(image_path):
                                print(f"  [SKIP] Scene break icon: {image_filename} (will use *** text divider)")
                                continue
                            
                            orientation = detect_image_orientation(image_path)
                            width, height = get_jpeg_dimensions(image_path)
                            rotation_marker = " [ROTATE 90deg]" if orientation == 'landscape' else ""
                            print(f"  -> {image_filename} ({width}x{height}, {orientation.upper()}){rotation_marker}")

                        image_info = ImageInfo(
                            image_filename=image_filename,
                            source_chapter=xhtml_file.name,
                            insert_number=insert_counter,
                            orientation=orientation,
                        )
                        images.append(image_info)
                        insert_counter += 1

            except Exception as e:
                print(f"  [WARN] Error scanning {xhtml_file.name}: {e}")
                continue

        return images

    @staticmethod
    def remove_inline_images(xhtml_content: str) -> str:
        """
        Remove inline full-page illustration tags from chapter content.

        Args:
            xhtml_content: XHTML content with inline images

        Returns:
            XHTML content with full-page images removed
        """
        lines = xhtml_content.split('\n')
        filtered_lines = []

        for line in lines:
            match = ImageHandler.IMAGE_PATTERN.search(line)
            if match and ImageHandler.FULLPAGE_IMAGE_PATTERN.match(match.group(1)):
                continue
            filtered_lines.append(line)

        return '\n'.join(filtered_lines)

    @staticmethod
    def create_insert_page(
        output_path: Path,
        image_info: ImageInfo,
        book_title: str = "Novel",
        lang_code: str = "en"
    ) -> None:
        """
        Create an XHTML insert page for a full-page illustration.

        Args:
            output_path: Path where to write the insert XHTML file
            image_info: Information about the image
            book_title: Book title for metadata
            lang_code: Language code for html attributes
        """
        escaped_title = escape(book_title)
        image_path = f"../image/{image_info.image_filename}"
        alt_text = escape(image_info.alt_text) if image_info.alt_text else ""

        img_class = "insert"
        if image_info.orientation == 'landscape':
            img_class = "insert rotate90"

        epub_version = get_epub_version()

        if epub_version == "EPUB3":
            xhtml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>

<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:epub="http://www.idpf.org/2007/ops"
      lang="{lang_code}"
      xml:lang="{lang_code}">
<head>
  <meta content="text/html; charset=UTF-8" http-equiv="default-style"/>
  <title>{escaped_title}</title>
  <link href="../style/book-style.css" rel="stylesheet" type="text/css"/>
</head>

<body class="nomargin center">
  <section epub:type="bodymatter chapter" id="{image_info.insert_id}">
    <img class="{img_class}" src="{image_path}" alt="{alt_text}"/>
  </section>
</body>
</html>
'''
        else:
            xhtml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">

<html xmlns="http://www.w3.org/1999/xhtml"
      lang="{lang_code}"
      xml:lang="{lang_code}">
<head>
  <meta http-equiv="Content-Type" content="application/xhtml+xml; charset=UTF-8"/>
  <title>{escaped_title}</title>
  <link href="../style/book-style.css" rel="stylesheet" type="text/css"/>
</head>

<body class="nomargin center">
  <div id="{image_info.insert_id}" class="insert-page">
    <img class="{img_class}" src="{image_path}" alt="{alt_text}"/>
  </div>
</body>
</html>
'''

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(xhtml_content, encoding='utf-8')

    @staticmethod
    def create_all_insert_pages(
        images: List[ImageInfo],
        output_xhtml_dir: Path,
        book_title: str = "Novel",
        lang_code: str = "en"
    ) -> int:
        """
        Create all insert pages for detected illustrations.

        Args:
            images: List of ImageInfo objects
            output_xhtml_dir: Directory where to write insert XHTML files
            book_title: Book title for metadata
            lang_code: Language code for html attributes

        Returns:
            Number of insert pages created
        """
        created_count = 0

        for image_info in images:
            output_path = output_xhtml_dir / image_info.xhtml_filename

            try:
                ImageHandler.create_insert_page(output_path, image_info, book_title, lang_code)
                print(f"  [OK] Created {image_info.xhtml_filename} for {image_info.image_filename}")
                created_count += 1
            except Exception as e:
                print(f"  [FAIL] Error creating {image_info.xhtml_filename}: {e}")

        return created_count
