"""
Post-Processor Module - Format Normalization and CJK Artifact Cleanup

Automatically cleans up Japanese formatting artifacts and stray CJK characters
that may leak through translation into any target language output.
"""

from .format_normalizer import FormatNormalizer
from .cjk_cleaner import CJKArtifactCleaner

__all__ = ['FormatNormalizer', 'CJKArtifactCleaner']
