"""
EPUB Extractor - Unpacks EPUB archives to working directory.

Language-agnostic extraction that handles various EPUB structures.
Now uses PublisherProfileManager for publisher detection.
"""

import zipfile
import hashlib
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Tuple
from dataclasses import dataclass, field

from .config import (
    EPUB_CONTENT_DIRS,
    OPF_FILENAMES,
    IMAGE_EXTENSIONS,
    COVER_PATTERNS,
    get_volume_structure,
    get_work_dir,
)
from .publisher_profiles.manager import PublisherProfileManager, get_profile_manager, PublisherProfile


@dataclass
class ExtractionResult:
    """Result of EPUB extraction."""
    volume_id: str
    work_dir: Path
    epub_root: Path
    content_dir: Path
    opf_path: Path
    images: List[Path] = field(default_factory=list)
    success: bool = True
    error: Optional[str] = None
    # New fields for publisher profile integration
    publisher_canonical: str = "Unknown"
    publisher_raw: str = ""
    publisher_profile: Optional[PublisherProfile] = None


class EPUBExtractor:
    """Extracts EPUB archives to structured working directory."""

    def __init__(self, work_base: Path = None):
        """
        Initialize extractor.

        Args:
            work_base: Base working directory (defaults to WORK/)
        """
        self.work_base = Path(work_base) if work_base else get_work_dir()
        self.work_base.mkdir(parents=True, exist_ok=True)

        # Get profile manager for publisher detection
        self._profile_manager = get_profile_manager()

    def _check_existing_translations(self, work_dir: Path) -> Optional[dict]:
        """
        Check if work directory has existing translations.
        
        Returns dict with translation info, or None if no translations found.
        """
        manifest_path = work_dir / "manifest.json"
        vn_dir = work_dir / "VN"
        
        if not manifest_path.exists():
            return None
        
        try:
            with open(manifest_path, encoding='utf-8') as f:
                manifest = json.load(f)
            
            # Check for VN files
            vn_count = 0
            if vn_dir.exists():
                vn_count = len(list(vn_dir.glob("*.md")))
            
            # Check pipeline state
            pipeline_state = manifest.get('pipeline_state', {})
            translator = pipeline_state.get('translator', {})
            translator_status = translator.get('status', 'unknown')
            chapters_completed = translator.get('chapters_completed', 0)
            
            # Only warn if there are actual translations
            if vn_count > 0 or chapters_completed > 0:
                return {
                    'vn_count': vn_count,
                    'translator_status': translator_status,
                    'chapters_completed': chapters_completed
                }
            
            return None
            
        except (json.JSONDecodeError, KeyError):
            return None

    def extract(self, epub_path: Path, volume_id: Optional[str] = None) -> ExtractionResult:
        """
        Extract EPUB to working directory.

        Args:
            epub_path: Path to source EPUB file
            volume_id: Optional custom volume ID (auto-generated if None)

        Returns:
            ExtractionResult with paths and metadata
        """
        epub_path = Path(epub_path)

        if not epub_path.exists():
            return ExtractionResult(
                volume_id="",
                work_dir=Path(),
                epub_root=Path(),
                content_dir=Path(),
                opf_path=Path(),
                success=False,
                error=f"EPUB file not found: {epub_path}"
            )

        # Generate volume ID if not provided
        if volume_id is None:
            volume_id = self._generate_volume_id(epub_path)

        # Create working directory structure
        work_dir = self.work_base / volume_id
        
        # PRE-FLIGHT CHECK: Warn if re-extracting over existing translations
        if work_dir.exists():
            existing_translations = self._check_existing_translations(work_dir)
            if existing_translations:
                print("\n" + "="*70)
                print("⚠️  WARNING: RE-EXTRACTION DETECTED")
                print("="*70)
                print(f"Volume: {volume_id}")
                print(f"Existing translations: {existing_translations['vn_count']} chapters")
                print(f"Translation status: {existing_translations['translator_status']}")
                print("\nRe-extracting will create a NEW directory and LOSE this state.")
                print("\nRecommended actions:")
                print("  1. Cancel and use migration script:")
                print(f"     python scripts/migrate_extraction.py --auto-detect \"{epub_path.stem[:20]}\"")
                print("  2. Continue anyway (creates new volume ID, old extraction preserved)")
                print("="*70)
                
                response = input("\nContinue with re-extraction? [y/N]: ").strip().lower()
                if response not in ['y', 'yes']:
                    return ExtractionResult(
                        volume_id=volume_id,
                        work_dir=work_dir,
                        epub_root=Path(),
                        content_dir=Path(),
                        opf_path=Path(),
                        success=False,
                        error="Re-extraction cancelled by user. Use migration script to preserve translations."
                    )
                
                print("\n⚠️  Proceeding with re-extraction (old directory will be removed)...")
            
            shutil.rmtree(work_dir)

        # Create standard directory structure
        volume_structure = get_volume_structure()
        work_dir.mkdir(parents=True)
        for dir_path in volume_structure.values():
            (work_dir / dir_path).mkdir(parents=True, exist_ok=True)

        # Extract EPUB
        epub_root = work_dir / volume_structure["epub_extracted"]
        try:
            with zipfile.ZipFile(epub_path, 'r') as zf:
                zf.extractall(epub_root)
        except zipfile.BadZipFile as e:
            return ExtractionResult(
                volume_id=volume_id,
                work_dir=work_dir,
                epub_root=epub_root,
                content_dir=Path(),
                opf_path=Path(),
                success=False,
                error=f"Invalid EPUB archive: {e}"
            )

        # Find content directory
        content_dir = self._find_content_dir(epub_root)
        if content_dir is None:
            return ExtractionResult(
                volume_id=volume_id,
                work_dir=work_dir,
                epub_root=epub_root,
                content_dir=Path(),
                opf_path=Path(),
                success=False,
                error="Could not find EPUB content directory"
            )

        # Find OPF file
        opf_path = self._find_opf(epub_root)
        if opf_path is None:
            return ExtractionResult(
                volume_id=volume_id,
                work_dir=work_dir,
                epub_root=epub_root,
                content_dir=content_dir,
                opf_path=Path(),
                success=False,
                error="Could not find OPF file"
            )

        # Catalog images
        images = self._catalog_images(content_dir)

        # Copy cover image to assets
        self._extract_cover(content_dir, work_dir / volume_structure["assets"])

        # Detect publisher from OPF metadata using profile manager
        publisher_canonical, publisher_confidence, publisher_profile = self._detect_publisher(opf_path)
        publisher_raw = self._get_raw_publisher_text(opf_path)

        print(f"[OK] Extracted EPUB to: {work_dir}")
        print(f"     Volume ID: {volume_id}")
        print(f"     Publisher: {publisher_canonical} ({publisher_confidence})")
        print(f"     Content dir: {content_dir.relative_to(work_dir)}")
        print(f"     OPF file: {opf_path.name}")
        print(f"     Images found: {len(images)}")

        return ExtractionResult(
            volume_id=volume_id,
            work_dir=work_dir,
            epub_root=epub_root,
            content_dir=content_dir,
            opf_path=opf_path,
            images=images,
            success=True,
            publisher_canonical=publisher_canonical,
            publisher_raw=publisher_raw,
            publisher_profile=publisher_profile
        )

    def _generate_volume_id(self, epub_path: Path) -> str:
        """Generate unique volume ID from filename and hash."""
        name_part = epub_path.stem.replace(" ", "_")[:30]
        hash_part = hashlib.md5(epub_path.name.encode()).hexdigest()[:6]
        timestamp = datetime.now().strftime("%Y%m%d")
        return f"{name_part}_{timestamp}_{hash_part}"

    def _find_content_dir(self, epub_root: Path) -> Optional[Path]:
        """Find the main content directory in extracted EPUB."""
        # Check common directory names
        for candidate in EPUB_CONTENT_DIRS:
            content_dir = epub_root / candidate
            if content_dir.is_dir():
                return content_dir

        # Check container.xml for rootfile path
        container_path = epub_root / "META-INF" / "container.xml"
        if container_path.exists():
            try:
                from lxml import etree
                tree = etree.parse(str(container_path))
                ns = {'container': 'urn:oasis:names:tc:opendocument:xmlns:container'}
                rootfile = tree.find('.//container:rootfile', ns)
                if rootfile is not None:
                    opf_path = rootfile.get('full-path')
                    if opf_path:
                        content_dir = epub_root / Path(opf_path).parent
                        if content_dir.is_dir():
                            return content_dir
            except Exception:
                pass

        # Fallback: look for any directory containing .opf
        for opf_file in epub_root.rglob("*.opf"):
            return opf_file.parent

        return None

    def _find_opf(self, epub_root: Path) -> Optional[Path]:
        """Find the OPF (Open Packaging Format) file."""
        # Check container.xml first
        container_path = epub_root / "META-INF" / "container.xml"
        if container_path.exists():
            try:
                from lxml import etree
                tree = etree.parse(str(container_path))
                ns = {'container': 'urn:oasis:names:tc:opendocument:xmlns:container'}
                rootfile = tree.find('.//container:rootfile', ns)
                if rootfile is not None:
                    opf_path = rootfile.get('full-path')
                    if opf_path:
                        full_path = epub_root / opf_path
                        if full_path.exists():
                            return full_path
            except Exception:
                pass

        # Fallback: find any .opf file
        opf_files = list(epub_root.rglob("*.opf"))
        if opf_files:
            # Prefer known OPF filenames
            for opf in opf_files:
                if opf.name in OPF_FILENAMES:
                    return opf
            return opf_files[0]

        return None

    def _get_raw_publisher_text(self, opf_path: Path) -> str:
        """Extract raw publisher text from OPF metadata."""
        try:
            from lxml import etree
            tree = etree.parse(str(opf_path))
            ns = {
                'opf': 'http://www.idpf.org/2007/opf',
                'dc': 'http://purl.org/dc/elements/1.1/'
            }
            publisher_elem = tree.find('.//dc:publisher', ns)
            if publisher_elem is not None and publisher_elem.text:
                return publisher_elem.text.strip()
        except Exception:
            pass
        return ""

    def _detect_publisher(self, opf_path: Path) -> Tuple[str, str, Optional[PublisherProfile]]:
        """
        Detect publisher from OPF metadata using PublisherProfileManager.

        Args:
            opf_path: Path to OPF file

        Returns:
            Tuple of (canonical_name, confidence, profile)
        """
        publisher_text = self._get_raw_publisher_text(opf_path)
        return self._profile_manager.detect_publisher(publisher_text)

    def _catalog_images(self, content_dir: Path) -> List[Path]:
        """Find all image files in content directory."""
        images = []

        for ext in IMAGE_EXTENSIONS:
            images.extend(content_dir.rglob(f"*{ext}"))
            images.extend(content_dir.rglob(f"*{ext.upper()}"))

        return sorted(set(images))

    def _extract_cover(self, content_dir: Path, assets_dir: Path) -> Optional[Path]:
        """Extract cover image to assets directory."""
        # Exclude allcover files (horizontal spreads, not single cover)
        def is_allcover(filename: str) -> bool:
            """Check if filename matches allcover pattern."""
            lower_name = filename.lower()
            return 'allcover' in lower_name
        
        for pattern in COVER_PATTERNS:
            for cover_path in content_dir.rglob(pattern):
                # Skip allcover files
                if is_allcover(cover_path.name):
                    continue
                dest = assets_dir / "cover.jpg"
                shutil.copy2(cover_path, dest)
                print(f"     Cover image: {cover_path.name}")
                return dest

        # Look in image subdirectories
        image_dirs = ["image", "images", "Images", "img"]
        for img_dir in image_dirs:
            for pattern in COVER_PATTERNS:
                cover_path = content_dir / img_dir / pattern
                if cover_path.exists() and not is_allcover(cover_path.name):
                    dest = assets_dir / "cover.jpg"
                    shutil.copy2(cover_path, dest)
                    print(f"     Cover image: {cover_path.name}")
                    return dest

        return None


def extract_epub(epub_path: Path, volume_id: str = None, work_base: Path = None) -> ExtractionResult:
    """
    Main function to extract an EPUB file.

    Args:
        epub_path: Path to source EPUB file
        volume_id: Optional custom volume ID
        work_base: Optional custom working directory

    Returns:
        ExtractionResult with extraction details
    """
    extractor = EPUBExtractor(work_base)
    return extractor.extract(epub_path, volume_id)
