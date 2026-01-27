"""
Continuity Pack Manager
Detects and manages cross-volume continuity for series translation.
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Import common_terms from JSON filters for filtering non-character names
try:
    from pipeline.librarian.name_filters import load_filters
    _filters = load_filters()
    COMMON_TERMS = _filters.common_terms
except ImportError:
    # Fallback if import fails
    COMMON_TERMS = set()
    logger = logging.getLogger(__name__)
    logger.warning("Could not import common_terms from name_filters")

logger = logging.getLogger(__name__)


@dataclass
class ContinuityPack:
    """Continuity pack from a previous volume."""
    volume_id: str
    series_title: str
    volume_number: int
    roster: Dict[str, str]  # Character names and spellings
    relationships: Dict[str, str]  # Character relationships
    glossary: Dict[str, str]  # Specialized terminology
    narrative_flags: List[str]  # Active plot states
    
    def to_dict(self) -> Dict:
        return {
            "volume_id": self.volume_id,
            "series_title": self.series_title,
            "volume_number": self.volume_number,
            "roster": self.roster,
            "relationships": self.relationships,
            "glossary": self.glossary,
            "narrative_flags": self.narrative_flags
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ContinuityPack':
        return cls(
            volume_id=data["volume_id"],
            series_title=data["series_title"],
            volume_number=data["volume_number"],
            roster=data.get("roster", {}),
            relationships=data.get("relationships", {}),
            glossary=data.get("glossary", {}),
            narrative_flags=data.get("narrative_flags", [])
        )


class ContinuityPackManager:
    """Manages continuity packs for series translation."""
    
    def __init__(self, work_dir: Path):
        self.work_dir = work_dir
        self.continuity_dir = work_dir / ".context"
        self.continuity_dir.mkdir(exist_ok=True)
        self.pack_file = self.continuity_dir / "continuity_pack.json"
    
    def _is_likely_character_name(self, jp_name: str) -> bool:
        """
        Filter out common words that are not character names.
        Uses same logic as ruby_extractor to maintain consistency.
        
        Args:
            jp_name: Japanese name to check
            
        Returns:
            True if likely a character name, False otherwise
        """
        # Filter out common terms
        if jp_name in COMMON_TERMS:
            return False
        
        # Very short names (1 char) are usually not full names
        if len(jp_name) <= 1:
            return False
        
        # Check for katakana (often used for names)
        katakana_pattern = re.compile(r'[\u30A0-\u30FF]')
        if katakana_pattern.search(jp_name):
            return True  # Katakana strongly indicates a name
        
        # Check for name suffixes (くん, ちゃん, さん, etc.)
        name_suffixes = ['くん', 'ちゃん', 'たん', 'さん', 'sama', '様', '殿', '氏']
        if any(jp_name.endswith(suffix) for suffix in name_suffixes):
            return True
        
        # Check for Chinese character names (2-3 kanji is typical)
        kanji_pattern = re.compile(r'[\u4E00-\u9FFF]')
        kanji_count = len(kanji_pattern.findall(jp_name))
        
        # Names are typically 2-4 kanji
        if 2 <= kanji_count <= 4 and len(jp_name) == kanji_count:
            return True
        
        # Default to False for safety (avoid clutter)
        return False
    
    def detect_series_info(self, manifest: Dict) -> Tuple[Optional[str], Optional[int]]:
        """
        Detect series title and volume number from manifest.
        
        Returns:
            (series_title, volume_number) or (None, None) if not detected
        """
        title = manifest.get("metadata", {}).get("title", "")
        title_en = manifest.get("metadata_en", {}).get("title_en", "")
        
        # Try to extract volume number from title
        # Common patterns: "Title Vol. 1", "Title Volume 1", "Title 1", "Title V1"
        patterns = [
            r'(.+?)\s+(?:Vol\.?|Volume)\s*(\d+)',
            r'(.+?)\s+V(\d+)',
            r'(.+?)\s+(\d+)$',
        ]
        
        for pattern in patterns:
            # Try English title first
            if title_en:
                match = re.search(pattern, title_en, re.IGNORECASE)
                if match:
                    series_title = match.group(1).strip()
                    volume_num = int(match.group(2))
                    return series_title, volume_num
            
            # Try Japanese title
            if title:
                match = re.search(pattern, title, re.IGNORECASE)
                if match:
                    series_title = match.group(1).strip()
                    volume_num = int(match.group(2))
                    return series_title, volume_num
        
        # Check for Japanese volume indicators (巻)
        if title:
            match = re.search(r'(.+?)\s*(\d+)巻', title)
            if match:
                series_title = match.group(1).strip()
                volume_num = int(match.group(2))
                return series_title, volume_num
        
        return None, None
    
    def find_previous_volume(self, series_title: str, current_volume: int) -> Optional[Path]:
        """
        Find the previous volume in the series.
        
        Prefers sequential order (N-1), but falls back to nearest preceding volume
        to handle gaps in processing (e.g., V1, V3, V5 available but V2, V4 missing).
        
        Args:
            series_title: Series title
            current_volume: Current volume number
            
        Returns:
            Path to previous volume directory, or None if not found
        """
        if current_volume <= 1:
            return None
        
        # Search WORK directory for matching volumes
        work_base = self.work_dir.parent
        candidates = []
        
        for volume_dir in work_base.iterdir():
            if not volume_dir.is_dir():
                continue
            
            manifest_path = volume_dir / "manifest.json"
            if not manifest_path.exists():
                continue
            
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                
                prev_series, prev_volume = self.detect_series_info(manifest)
                
                # Check if this is from the same series and has a lower volume number
                if prev_series and prev_volume and prev_volume < current_volume:
                    if self._fuzzy_match_title(series_title, prev_series):
                        candidates.append((prev_volume, volume_dir))
            
            except Exception as e:
                logger.debug(f"Error reading manifest from {volume_dir}: {e}")
                continue
        
        if not candidates:
            return None
        
        # Sort by volume number (descending) to get closest preceding volume
        candidates.sort(reverse=True)
        
        # Prefer sequential N-1 if available
        for vol_num, vol_dir in candidates:
            if vol_num == current_volume - 1:
                logger.info(f"Found sequential previous volume (V{vol_num}): {vol_dir.name}")
                return vol_dir
        
        # Fallback: Use highest available preceding volume
        closest_vol, closest_dir = candidates[0]
        logger.info(f"Found nearest previous volume (V{closest_vol}, gap detected): {closest_dir.name}")
        return closest_dir
    
    def _fuzzy_match_title(self, title1: str, title2: str) -> bool:
        """Fuzzy match two series titles."""
        # Normalize titles
        t1 = title1.lower().strip()
        t2 = title2.lower().strip()
        
        # Exact match
        if t1 == t2:
            return True
        
        # Remove common suffixes/prefixes
        for suffix in [' series', ' light novel', ' ln']:
            t1 = t1.replace(suffix, '')
            t2 = t2.replace(suffix, '')
        
        # Check if one contains the other (for subtitle variations)
        if t1 in t2 or t2 in t1:
            return True
        
        return False
    
    def load_continuity_pack(self, volume_dir: Path) -> Optional[ContinuityPack]:
        """
        Load continuity pack from a volume directory.
        
        Args:
            volume_dir: Path to volume directory
            
        Returns:
            ContinuityPack or None if not found
        """
        pack_path = volume_dir / ".context" / "continuity_pack.json"
        
        if not pack_path.exists():
            logger.debug(f"No continuity pack found at {pack_path}")
            return None
        
        try:
            with open(pack_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return ContinuityPack.from_dict(data)
        
        except Exception as e:
            logger.error(f"Error loading continuity pack from {pack_path}: {e}")
            return None
    
    def save_continuity_pack(self, pack: ContinuityPack):
        """Save continuity pack to current volume."""
        try:
            with open(self.pack_file, 'w', encoding='utf-8') as f:
                json.dump(pack.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved continuity pack to {self.pack_file}")
        
        except Exception as e:
            logger.error(f"Error saving continuity pack: {e}")
    
    def extract_continuity_from_volume(self, volume_dir: Path, manifest: Dict, target_language: str = 'en') -> ContinuityPack:
        """
        Extract continuity pack from a completed volume.
        
        Args:
            volume_dir: Path to volume directory
            manifest: Volume manifest
            target_language: Target language code (en, vn, etc.)
            
        Returns:
            ContinuityPack
        """
        series_title, volume_num = self.detect_series_info(manifest)
        
        # Load character names and glossary from metadata_{language}.json (preferred)
        metadata_lang_path = volume_dir / f"metadata_{target_language}.json"
        roster = {}
        glossary = {}
        
        if metadata_lang_path.exists():
            try:
                with open(metadata_lang_path, 'r', encoding='utf-8') as f:
                    metadata_lang = json.load(f)
                    roster = metadata_lang.get('character_names', {})
                    glossary = metadata_lang.get('glossary', {})
                    logger.info(f"Loaded {len(roster)} character names from metadata_{target_language}.json")
                    logger.info(f"Loaded {len(glossary)} glossary terms from metadata_{target_language}.json")
            except Exception as e:
                logger.warning(f"Error loading metadata_{target_language}.json: {e}")
        
        # Fallback to manifest.json if metadata_{language}.json not found
        if not roster:
            metadata_key = f'metadata_{target_language}'
            roster = manifest.get(metadata_key, {}).get('character_names', {})
            if not roster:
                # Last resort: try metadata_en
                roster = manifest.get('metadata_en', {}).get('character_names', {})
            if roster:
                logger.info(f"Loaded {len(roster)} character names from manifest.json (fallback)")
        
        if not glossary:
            metadata_key = f'metadata_{target_language}'
            glossary = manifest.get(metadata_key, {}).get('glossary', {})
            if not glossary:
                # Last resort: try metadata_en
                glossary = manifest.get('metadata_en', {}).get('glossary', {})
            if glossary:
                logger.info(f"Loaded {len(glossary)} glossary terms from manifest.json (fallback)")
        
        # Placeholder for relationships and narrative flags
        # These would ideally be extracted from context or manually curated
        relationships = {}
        narrative_flags = []
        
        pack = ContinuityPack(
            volume_id=manifest.get("volume_id", "unknown"),
            series_title=series_title or "Unknown Series",
            volume_number=volume_num or 1,
            roster=roster,
            relationships=relationships,
            glossary=glossary,
            narrative_flags=narrative_flags
        )
        
        return pack
    
    def format_continuity_for_prompt(self, pack: ContinuityPack) -> str:
        """
        Format continuity pack for injection into translation prompt.
        
        Args:
            pack: ContinuityPack
            
        Returns:
            Formatted string for prompt
        """
        lines = []
        lines.append("[CONTINUITY_PACK]")
        lines.append(f"Series: {pack.series_title}")
        lines.append(f"Previous Volume: {pack.volume_number}")
        lines.append("")
        
        if pack.roster:
            lines.append("ROSTER (Character Names):")
            for jp_name, en_name in pack.roster.items():
                lines.append(f"  {jp_name} → {en_name}")
            lines.append("")
        
        if pack.relationships:
            lines.append("RELATIONSHIPS:")
            for key, value in pack.relationships.items():
                lines.append(f"  {key}: {value}")
            lines.append("")
        
        if pack.glossary:
            lines.append("GLOSSARY (Specialized Terms):")
            for jp_term, en_term in pack.glossary.items():
                lines.append(f"  {jp_term} → {en_term}")
            lines.append("")
        
        if pack.narrative_flags:
            lines.append("NARRATIVE_FLAGS (Active Plot States):")
            for flag in pack.narrative_flags:
                lines.append(f"  - {flag}")
            lines.append("")
        
        lines.append("[/CONTINUITY_PACK]")
        
        return "\n".join(lines)


def detect_and_offer_continuity(work_dir: Path, manifest: Dict, target_language: str = 'en') -> Optional[ContinuityPack]:
    """
    LEGACY SYSTEM - DISABLED
    
    This function previously detected sequel volumes and injected continuity packs
    from .context directories. This has been disabled in favor of the v3 enhanced
    schema system which provides richer character_profiles via manifest.json.
    
    The v3 schema stores:
    - character_profiles with keigo_switch, relationship_to_others, speech_pattern
    - inherited_from field for tracking volume lineage  
    - volume_specific_notes for sequel context
    
    These provide superior continuity tracking compared to the legacy .context files.
    
    Args:
        work_dir: Current volume work directory (unused)
        manifest: Current volume manifest (unused)
        target_language: Target language code (unused)
        
    Returns:
        None - Legacy continuity system disabled
    """
    # Check if v3 schema is present
    metadata_en = manifest.get('metadata_en', {})
    schema_version = metadata_en.get('schema_version', '')
    character_profiles = metadata_en.get('character_profiles', {})
    
    if schema_version == 'v3_enhanced' and character_profiles:
        logger.info("="*60)
        logger.info("LEGACY CONTINUITY SYSTEM DISABLED")
        logger.info("="*60)
        logger.info(f"✓ V3 enhanced schema detected: {len(character_profiles)} character profiles")
        inherited_from = metadata_en.get('inherited_from', 'N/A')
        if inherited_from != 'N/A':
            logger.info(f"✓ Schema inherited from: {inherited_from}")
        logger.info("✓ Using v3 character_profiles for continuity (richer context)")
        logger.info("✓ Legacy .context directory files will be ignored")
        logger.info("="*60)
    else:
        logger.info("Legacy continuity system disabled. V3 schema preferred.")
        logger.info("To enable continuity, populate character_profiles in manifest.json metadata_en")
    
    return None
