"""
Publisher Profiles Module - Runtime pattern loading and matching.

Provides publisher-specific configuration for:
- Image classification patterns
- TOC handling strategies
- Chapter detection methods
"""

from .manager import (
    PublisherProfileManager,
    get_profile_manager,
    PublisherProfile,
    ContentConfig,
    PatternMatch,
    MismatchReport,
)

__all__ = [
    "PublisherProfileManager",
    "get_profile_manager",
    "PublisherProfile",
    "ContentConfig",
    "PatternMatch",
    "MismatchReport",
]
