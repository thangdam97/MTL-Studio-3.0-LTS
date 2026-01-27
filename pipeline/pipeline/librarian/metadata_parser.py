"""
Metadata Parser - Extract book metadata from EPUB OPF files.

Parses content.opf/package.opf to extract title, author, publisher,
ISBN, language, and other Dublin Core metadata.
"""

from pathlib import Path
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, field
from lxml import etree

from .config import get_metadata_namespaces, OPF_FILENAMES


@dataclass
class BookMetadata:
    """Container for extracted book metadata."""
    title: str = ""
    title_sort: str = ""
    author: str = ""
    author_sort: str = ""
    publisher: str = ""
    language: str = ""
    isbn: str = ""
    series: str = ""
    series_index: Optional[int] = None
    description: str = ""
    subjects: List[str] = field(default_factory=list)
    publication_date: str = ""
    modified_date: str = ""
    identifier: str = ""
    source_file: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary for JSON serialization."""
        return {
            "title": self.title,
            "title_sort": self.title_sort,
            "author": self.author,
            "author_sort": self.author_sort,
            "publisher": self.publisher,
            "language": self.language,
            "isbn": self.isbn,
            "series": self.series,
            "series_index": self.series_index,
            "description": self.description,
            "subjects": self.subjects,
            "publication_date": self.publication_date,
            "modified_date": self.modified_date,
            "identifier": self.identifier,
            "source_file": self.source_file,
        }


class MetadataParser:
    """Parses EPUB OPF files to extract book metadata."""

    def __init__(self):
        """Initialize parser with XML namespaces."""
        self.ns = get_metadata_namespaces()

    def parse_opf(self, opf_path: Path) -> BookMetadata:
        """
        Parse OPF file and extract metadata.

        Args:
            opf_path: Path to OPF file

        Returns:
            BookMetadata object with extracted information
        """
        if not opf_path.exists():
            raise ValueError(f"OPF file not found: {opf_path}")

        tree = etree.parse(str(opf_path))
        root = tree.getroot()

        metadata = BookMetadata(source_file=str(opf_path))

        # Find metadata element
        meta_elem = root.find("opf:metadata", self.ns)
        if meta_elem is None:
            # Try without namespace prefix
            meta_elem = root.find("metadata")
        if meta_elem is None:
            # Try with default namespace
            meta_elem = root.find("{http://www.idpf.org/2007/opf}metadata")

        if meta_elem is None:
            print(f"[WARN] No metadata element found in {opf_path}")
            return metadata

        # Extract Dublin Core elements
        metadata.title = self._get_dc_text(meta_elem, "title")
        metadata.author = self._get_dc_text(meta_elem, "creator")
        metadata.publisher = self._get_dc_text(meta_elem, "publisher")
        metadata.language = self._get_dc_text(meta_elem, "language")
        metadata.description = self._get_dc_text(meta_elem, "description")
        metadata.publication_date = self._get_dc_text(meta_elem, "date")
        metadata.identifier = self._get_dc_text(meta_elem, "identifier")

        # Extract subjects (can be multiple)
        metadata.subjects = self._get_dc_texts(meta_elem, "subject")

        # Extract ISBN from identifier
        metadata.isbn = self._extract_isbn(meta_elem)

        # Extract sort titles/authors from meta elements
        metadata.title_sort = self._get_meta_content(meta_elem, "calibre:title_sort") or metadata.title
        metadata.author_sort = self._get_meta_content(meta_elem, "calibre:author_sort") or metadata.author

        # Extract series information
        metadata.series = self._get_meta_content(meta_elem, "calibre:series") or ""
        series_idx = self._get_meta_content(meta_elem, "calibre:series_index")
        if series_idx:
            try:
                metadata.series_index = int(float(series_idx))
            except ValueError:
                pass

        # Extract modified date (EPUB3)
        metadata.modified_date = self._get_dcterms_text(meta_elem, "modified")

        return metadata

    def _get_dc_text(self, meta_elem: etree._Element, name: str) -> str:
        """Get text content of a Dublin Core element."""
        # Try with dc: namespace
        elem = meta_elem.find(f"dc:{name}", self.ns)
        if elem is None:
            # Try with full namespace
            elem = meta_elem.find(f"{{http://purl.org/dc/elements/1.1/}}{name}")
        if elem is not None and elem.text:
            return elem.text.strip()
        return ""

    def _get_dc_texts(self, meta_elem: etree._Element, name: str) -> List[str]:
        """Get text content of all matching Dublin Core elements."""
        results = []
        # Try with dc: namespace
        for elem in meta_elem.findall(f"dc:{name}", self.ns):
            if elem.text:
                results.append(elem.text.strip())
        if not results:
            # Try with full namespace
            for elem in meta_elem.findall(f"{{http://purl.org/dc/elements/1.1/}}{name}"):
                if elem.text:
                    results.append(elem.text.strip())
        return results

    def _get_dcterms_text(self, meta_elem: etree._Element, name: str) -> str:
        """Get text content of a dcterms element."""
        elem = meta_elem.find(f"dcterms:{name}", self.ns)
        if elem is None:
            elem = meta_elem.find(f"{{http://purl.org/dc/terms/}}{name}")
        if elem is None:
            # EPUB3 uses meta element with property
            for meta in meta_elem.findall("meta"):
                if meta.get("property") == f"dcterms:{name}":
                    if meta.text:
                        return meta.text.strip()
            for meta in meta_elem.findall("{http://www.idpf.org/2007/opf}meta"):
                if meta.get("property") == f"dcterms:{name}":
                    if meta.text:
                        return meta.text.strip()
        if elem is not None and elem.text:
            return elem.text.strip()
        return ""

    def _get_meta_content(self, meta_elem: etree._Element, name: str) -> str:
        """Get content attribute from meta element with given name."""
        # EPUB2 style: <meta name="..." content="..."/>
        for meta in meta_elem.findall("meta"):
            if meta.get("name") == name:
                return meta.get("content", "")
        for meta in meta_elem.findall("{http://www.idpf.org/2007/opf}meta"):
            if meta.get("name") == name:
                return meta.get("content", "")

        # EPUB3 style: <meta property="...">value</meta>
        for meta in meta_elem.findall("meta"):
            if meta.get("property") == name and meta.text:
                return meta.text.strip()
        for meta in meta_elem.findall("{http://www.idpf.org/2007/opf}meta"):
            if meta.get("property") == name and meta.text:
                return meta.text.strip()

        return ""

    def _extract_isbn(self, meta_elem: etree._Element) -> str:
        """Extract ISBN from identifier elements."""
        # Look for identifier with ISBN scheme
        for elem in meta_elem.findall("dc:identifier", self.ns):
            scheme = elem.get("{http://www.idpf.org/2007/opf}scheme", "")
            if scheme.upper() == "ISBN":
                return elem.text.strip() if elem.text else ""
            # Check text content for ISBN pattern
            if elem.text and ("978" in elem.text or "979" in elem.text):
                text = elem.text.strip()
                # Clean ISBN (remove hyphens)
                isbn = ''.join(c for c in text if c.isdigit())
                if len(isbn) in (10, 13):
                    return isbn

        # Try with full namespace
        for elem in meta_elem.findall("{http://purl.org/dc/elements/1.1/}identifier"):
            scheme = elem.get("{http://www.idpf.org/2007/opf}scheme", "")
            if scheme.upper() == "ISBN":
                return elem.text.strip() if elem.text else ""
            if elem.text and ("978" in elem.text or "979" in elem.text):
                text = elem.text.strip()
                isbn = ''.join(c for c in text if c.isdigit())
                if len(isbn) in (10, 13):
                    return isbn

        return ""


# Sequel Detection Functions

def detect_sequel_from_opf(opf_path: Path) -> Optional[tuple[str, int]]:
    """
    Detect sequel from OPF series metadata (EPUB 3 standard).
    
    Returns:
        (series_title, volume_number) if sequel, None otherwise
    """
    try:
        tree = etree.parse(str(opf_path))
        root = tree.getroot()
        ns = {'opf': 'http://www.idpf.org/2007/opf'}
        
        # Look for belongs-to-collection
        collection = root.find('.//opf:meta[@property="belongs-to-collection"]', ns)
        if collection is not None and collection.text:
            series_title = collection.text.strip()
            
            # Look for group-position
            position = root.find('.//opf:meta[@property="group-position"]', ns)
            if position is not None and position.text:
                try:
                    volume_num = int(position.text.strip())
                    if volume_num > 1:
                        return (series_title, volume_num)
                except ValueError:
                    pass
        
        return None
    except Exception:
        return None


def detect_sequel_from_title(title: str) -> Optional[tuple[str, int]]:
    """
    Detect sequel from title parsing (fallback for Japanese light novels).
    
    Returns:
        (series_title, volume_number) if sequel, None otherwise
    """
    import re
    
    # Pattern 1: Japanese numerals (２, ３, etc.)
    japanese_nums = {
        '２': 2, '３': 3, '４': 4, '５': 5, '６': 6,
        '７': 7, '８': 8, '９': 9, '１０': 10
    }
    for jp_num, vol_num in japanese_nums.items():
        if jp_num in title:
            series_title = title.replace(jp_num, '').strip()
            return (series_title, vol_num)
    
    # Pattern 2: Arabic numerals at end (2, 3, etc.)
    match = re.search(r'(\d+)$', title)
    if match:
        vol_num = int(match.group(1))
        if vol_num > 1:
            series_title = title[:match.start()].strip()
            return (series_title, vol_num)
    
    # Pattern 3: "Vol.X" or "Volume X"
    match = re.search(r'(?:Vol\.|Volume)\s*(\d+)', title, re.IGNORECASE)
    if match:
        vol_num = int(match.group(1))
        if vol_num > 1:
            series_title = re.sub(r'(?:Vol\.|Volume)\s*\d+', '', title, flags=re.IGNORECASE).strip()
            return (series_title, vol_num)
    
    return None


def detect_sequel(title: str, opf_path: Path) -> Optional[tuple[str, int]]:
    """
    Detect if this is a sequel using hybrid approach.
    
    1. Try OPF series metadata (EPUB 3 standard)
    2. Fall back to title parsing (for Japanese light novels)
    
    Returns:
        (series_title, volume_number) if sequel, None otherwise
    """
    # Try OPF metadata first (most reliable)
    sequel_info = detect_sequel_from_opf(opf_path)
    if sequel_info:
        print(f"[INFO] Detected sequel from OPF metadata: {sequel_info}")
        return sequel_info
    
    # Fall back to title parsing (for KADOKAWA light novels)
    sequel_info = detect_sequel_from_title(title)
    if sequel_info:
        print(f"[INFO] Detected sequel from title parsing: {sequel_info}")
        return sequel_info
    
    return None


def find_previous_volume(series_title: str, current_volume_num: int, work_dir: Path) -> Optional[Path]:
    """
    Find previous volume directory in WORK folder.
    
    Args:
        series_title: Base series title without volume number
        current_volume_num: Current volume number
        work_dir: WORK directory path
    
    Returns:
        Path to previous volume directory, or None if not found
    """
    if current_volume_num <= 1:
        return None
    
    target_volume_num = current_volume_num - 1
    
    # Search for directories matching series title
    for volume_dir in work_dir.iterdir():
        if not volume_dir.is_dir():
            continue
        
        # Skip if directory doesn't contain series title
        if series_title not in volume_dir.name:
            continue
        
        # Load manifest to check volume number
        manifest_path = volume_dir / 'manifest.json'
        if not manifest_path.exists():
            continue
        
        try:
            import json
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            title = manifest.get('metadata', {}).get('title', '')
            sequel_info = detect_sequel_from_title(title)
            
            if target_volume_num == 1:
                # Looking for Volume 1 - should have no sequel indicator
                if not sequel_info:
                    return volume_dir
            else:
                # Looking for Volume 2+ - check volume number
                if sequel_info:
                    _, vol_num = sequel_info
                    if vol_num == target_volume_num:
                        return volume_dir
        except Exception:
            continue
    
    return None


def load_previous_metadata(previous_volume_dir: Path) -> Dict[str, Any]:
    """
    Load character_names and glossary from previous volume's metadata_en.json.
    
    Args:
        previous_volume_dir: Path to previous volume directory
    
    Returns:
        Dict with 'character_names' and 'glossary' keys
    """
    import json
    
    metadata_path = previous_volume_dir / 'metadata_en.json'
    
    if not metadata_path.exists():
        print(f"[WARN] Previous volume metadata not found: {metadata_path}")
        return {'character_names': {}, 'glossary': {}}
    
    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        character_names = metadata.get('character_names', {})
        glossary = metadata.get('glossary', {})
        
        print(f"[INFO] Loaded from previous volume: {len(character_names)} names, {len(glossary)} glossary terms")
        
        return {
            'character_names': character_names,
            'glossary': glossary
        }
    except Exception as e:
        print(f"[ERROR] Failed to load previous metadata: {e}")
        return {'character_names': {}, 'glossary': {}}


def merge_metadata(previous: Dict, current: Dict) -> Dict:
    """
    Merge previous volume metadata with current volume metadata.
    Current volume takes precedence for conflicts.
    
    Args:
        previous: Metadata from previous volume
        current: Metadata from current volume
    
    Returns:
        Merged metadata dict
    """
    merged_names = {
        **previous.get('character_names', {}),
        **current.get('character_names', {})
    }
    
    merged_glossary = {
        **previous.get('glossary', {}),
        **current.get('glossary', {})
    }
    
    print(f"[INFO] Merged metadata: {len(merged_names)} names, {len(merged_glossary)} glossary terms")
    
    return {
        'character_names': merged_names,
        'glossary': merged_glossary
    }


def parse_metadata(opf_path: Path) -> BookMetadata:
    """
    Main function to parse metadata from OPF file.

    Args:
        opf_path: Path to OPF file

    Returns:
        BookMetadata object with extracted information
    """
    parser = MetadataParser()
    return parser.parse_opf(opf_path)


def find_and_parse_metadata(epub_root: Path) -> BookMetadata:
    """
    Find OPF file in extracted EPUB and parse metadata.

    Args:
        epub_root: Root directory of extracted EPUB

    Returns:
        BookMetadata object with extracted information
    """
    # Find OPF file
    for opf_name in OPF_FILENAMES:
        for opf_path in epub_root.rglob(opf_name):
            return parse_metadata(opf_path)

    # Fallback: find any .opf file
    opf_files = list(epub_root.rglob("*.opf"))
    if opf_files:
        return parse_metadata(opf_files[0])

    raise ValueError(f"No OPF file found in {epub_root}")
