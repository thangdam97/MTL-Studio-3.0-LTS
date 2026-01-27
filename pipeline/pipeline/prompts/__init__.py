"""
Prompts Module - Translation prompt generation and management.

This module provides:
- Name prompt generation from ruby extractor results
- Template loading for irregular name handling
- Prompt injection utilities for Phase 1.5 translation
"""

from .name_prompt_generator import (
    NamePromptGenerator,
    NamePattern,
    generate_name_prompt,
)

__all__ = [
    "NamePromptGenerator",
    "NamePattern",
    "generate_name_prompt",
]
