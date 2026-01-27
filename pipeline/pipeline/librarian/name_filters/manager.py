"""
Name Filter Manager - Loads and manages JSON-based name filter patterns.

Provides runtime loading of filter patterns with support for:
- Base filters (always loaded)
- Genre-specific filters (isekai, school_life, etc.)
- Filter inheritance via 'extends' field
- Caching for performance
"""

import json
import logging
from pathlib import Path
from typing import Dict, Set, Optional, Any, List
from dataclasses import dataclass, field
from functools import lru_cache

logger = logging.getLogger(__name__)


@dataclass
class ConfidenceModifiers:
    """Confidence score adjustments for name classification."""
    boosts: Dict[str, float] = field(default_factory=dict)
    penalties: Dict[str, float] = field(default_factory=dict)
    threshold: float = 0.70


@dataclass
class NameIndicators:
    """Patterns that indicate a term is likely a name."""
    suffixes: Set[str] = field(default_factory=set)
    intro_patterns: List[str] = field(default_factory=list)
    first_person_pronouns: Set[str] = field(default_factory=set)


@dataclass
class LoadedFilters:
    """Container for all loaded filter data."""
    katakana_common_words: Set[str] = field(default_factory=set)
    kanji_stylistic_ruby: Set[str] = field(default_factory=set)
    common_terms: Set[str] = field(default_factory=set)
    name_indicators: NameIndicators = field(default_factory=NameIndicators)
    confidence_modifiers: ConfidenceModifiers = field(default_factory=ConfidenceModifiers)
    loaded_filters: List[str] = field(default_factory=list)


class NameFilterManager:
    """Manages loading and merging of name filter JSON files."""

    def __init__(self, filters_dir: Optional[Path] = None):
        """
        Initialize the filter manager.

        Args:
            filters_dir: Directory containing filter JSON files.
                         Defaults to the name_filters directory.
        """
        if filters_dir is None:
            filters_dir = Path(__file__).parent

        self.filters_dir = filters_dir
        self.genre_filters_dir = filters_dir / "genre_filters"
        self._cache: Dict[str, LoadedFilters] = {}

    def _load_json_file(self, path: Path) -> Optional[Dict[str, Any]]:
        """Load and parse a JSON filter file."""
        if not path.exists():
            logger.warning(f"Filter file not found: {path}")
            return None

        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse filter file {path}: {e}")
            return None

    def _flatten_category_dict(self, data: Dict[str, Any]) -> Set[str]:
        """
        Flatten a categorized dict into a single set.

        Handles structures like:
        {
            "gaming_fantasy": ["スキル", "レベル"],
            "school": ["クラス", "テスト"]
        }
        -> {"スキル", "レベル", "クラス", "テスト"}
        """
        result = set()
        for category, items in data.items():
            if isinstance(items, list):
                result.update(items)
            elif isinstance(items, str):
                result.add(items)
        return result

    def _merge_filters(self, base: LoadedFilters, extension: Dict[str, Any]) -> LoadedFilters:
        """Merge extension filter data into base filters."""
        # Merge katakana common words
        if "katakana_common_words" in extension:
            base.katakana_common_words.update(
                self._flatten_category_dict(extension["katakana_common_words"])
            )

        # Merge kanji stylistic ruby
        if "kanji_stylistic_ruby" in extension:
            base.kanji_stylistic_ruby.update(
                self._flatten_category_dict(extension["kanji_stylistic_ruby"])
            )

        # Merge common terms
        if "common_terms" in extension:
            base.common_terms.update(
                self._flatten_category_dict(extension["common_terms"])
            )

        # Merge name indicators
        if "name_indicators" in extension:
            indicators = extension["name_indicators"]
            if "suffixes" in indicators:
                base.name_indicators.suffixes.update(indicators["suffixes"])
            if "intro_patterns" in indicators:
                base.name_indicators.intro_patterns.extend(indicators["intro_patterns"])
            if "first_person_pronouns" in indicators:
                base.name_indicators.first_person_pronouns.update(
                    indicators["first_person_pronouns"]
                )

        # Merge confidence modifiers (extension overrides base)
        if "confidence_modifiers" in extension:
            mods = extension["confidence_modifiers"]
            if "boosts" in mods:
                base.confidence_modifiers.boosts.update(mods["boosts"])
            if "penalties" in mods:
                base.confidence_modifiers.penalties.update(mods["penalties"])
            if "threshold" in mods:
                base.confidence_modifiers.threshold = mods["threshold"]

        return base

    def _parse_filter_data(self, data: Dict[str, Any]) -> LoadedFilters:
        """Parse raw JSON data into LoadedFilters object."""
        filters = LoadedFilters()

        # Parse katakana common words
        if "katakana_common_words" in data:
            filters.katakana_common_words = self._flatten_category_dict(
                data["katakana_common_words"]
            )

        # Parse kanji stylistic ruby
        if "kanji_stylistic_ruby" in data:
            filters.kanji_stylistic_ruby = self._flatten_category_dict(
                data["kanji_stylistic_ruby"]
            )

        # Parse common terms
        if "common_terms" in data:
            filters.common_terms = self._flatten_category_dict(data["common_terms"])

        # Parse name indicators
        if "name_indicators" in data:
            indicators = data["name_indicators"]
            filters.name_indicators = NameIndicators(
                suffixes=set(indicators.get("suffixes", [])),
                intro_patterns=list(indicators.get("intro_patterns", [])),
                first_person_pronouns=set(indicators.get("first_person_pronouns", []))
            )

        # Parse confidence modifiers
        if "confidence_modifiers" in data:
            mods = data["confidence_modifiers"]
            filters.confidence_modifiers = ConfidenceModifiers(
                boosts=dict(mods.get("boosts", {})),
                penalties=dict(mods.get("penalties", {})),
                threshold=mods.get("threshold", 0.70)
            )

        return filters

    def load_base_filters(self) -> LoadedFilters:
        """Load the base filter set."""
        cache_key = "base"
        if cache_key in self._cache:
            return self._cache[cache_key]

        base_path = self.filters_dir / "base_filters.json"
        data = self._load_json_file(base_path)

        if data is None:
            logger.warning("Base filters not found, returning empty filters")
            return LoadedFilters()

        filters = self._parse_filter_data(data)
        filters.loaded_filters.append("base")

        self._cache[cache_key] = filters
        return filters

    def load_genre_filters(self, genre: str) -> Optional[Dict[str, Any]]:
        """Load a genre-specific filter file."""
        genre_path = self.genre_filters_dir / f"{genre}.json"
        return self._load_json_file(genre_path)

    def load_filters(self, genres: Optional[List[str]] = None) -> LoadedFilters:
        """
        Load filters with optional genre extensions.

        Args:
            genres: List of genre names to load (e.g., ["isekai", "school_life"])

        Returns:
            LoadedFilters with base + genre filters merged
        """
        # Create cache key
        cache_key = "base"
        if genres:
            cache_key = f"base+{'+'.join(sorted(genres))}"

        if cache_key in self._cache:
            return self._cache[cache_key]

        # Start with base filters
        filters = self.load_base_filters()

        # Make a copy to avoid mutating cached base
        import copy
        filters = copy.deepcopy(filters)

        # Load and merge genre filters
        if genres:
            for genre in genres:
                genre_data = self.load_genre_filters(genre)
                if genre_data:
                    # Handle inheritance
                    extends = genre_data.get("meta", {}).get("extends")
                    if extends and extends != "base":
                        # Recursively load parent genre first
                        parent_data = self.load_genre_filters(extends)
                        if parent_data:
                            filters = self._merge_filters(filters, parent_data)
                            filters.loaded_filters.append(extends)

                    filters = self._merge_filters(filters, genre_data)
                    filters.loaded_filters.append(genre)
                else:
                    logger.warning(f"Genre filter not found: {genre}")

        self._cache[cache_key] = filters
        return filters

    def list_available_genres(self) -> List[str]:
        """List all available genre filter files."""
        if not self.genre_filters_dir.exists():
            return []

        return [
            p.stem for p in self.genre_filters_dir.glob("*.json")
        ]

    def get_filter_info(self, genre: Optional[str] = None) -> Dict[str, Any]:
        """Get metadata about a filter file."""
        if genre:
            path = self.genre_filters_dir / f"{genre}.json"
        else:
            path = self.filters_dir / "base_filters.json"

        data = self._load_json_file(path)
        if data:
            return data.get("meta", {})
        return {}

    def clear_cache(self):
        """Clear the filter cache."""
        self._cache.clear()


# Module-level singleton
_filter_manager: Optional[NameFilterManager] = None


def get_filter_manager() -> NameFilterManager:
    """Get the singleton NameFilterManager instance."""
    global _filter_manager
    if _filter_manager is None:
        _filter_manager = NameFilterManager()
    return _filter_manager


def load_filters(genres: Optional[List[str]] = None) -> LoadedFilters:
    """
    Convenience function to load filters.

    Args:
        genres: Optional list of genre names

    Returns:
        LoadedFilters object
    """
    return get_filter_manager().load_filters(genres)
