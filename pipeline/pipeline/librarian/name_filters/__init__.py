"""
Name Filters Module - JSON-based filter patterns for name extraction.

Provides:
- Base filters for common non-name terms
- Genre-specific filters (isekai, school_life, etc.)
- Filter manager for loading and merging patterns
"""

from .manager import (
    NameFilterManager,
    LoadedFilters,
    ConfidenceModifiers,
    NameIndicators,
    get_filter_manager,
    load_filters,
)

__all__ = [
    "NameFilterManager",
    "LoadedFilters",
    "ConfidenceModifiers",
    "NameIndicators",
    "get_filter_manager",
    "load_filters",
]
