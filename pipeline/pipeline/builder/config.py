"""
Builder Agent Configuration - EPUB output settings.

Language-agnostic configuration for EPUB building.
Language-specific settings (titles, TOC labels) come from manifest.json.
"""

from pathlib import Path
from typing import Dict, Any, List
from ..config import load_config, TEMPLATES_DIR


# ============================================================================
# EPUB FORMAT SETTINGS
# ============================================================================

def get_epub_version() -> str:
    """
    Get EPUB version from configuration.

    Returns:
        'EPUB2' or 'EPUB3'
    """
    config = load_config()
    version = config.get('builder', {}).get('epub_version', '3.0')
    # Normalize version string
    if version in ('3.0', '3', 'EPUB3'):
        return 'EPUB3'
    elif version in ('2.0', '2', 'EPUB2'):
        return 'EPUB2'
    return 'EPUB3'  # Default to EPUB3


def get_css_template_path() -> Path:
    """Get path to CSS template."""
    config = load_config()
    css_path = config.get('builder', {}).get('css_template', 'templates/styles/main.css')
    return Path(css_path)


# ============================================================================
# FONT CONFIGURATION
# ============================================================================

def get_fonts_config() -> Dict[str, Any]:
    """Get font embedding configuration."""
    config = load_config()
    return config.get('builder', {}).get('fonts', {'enabled': True})


def get_fonts_to_embed() -> Dict[str, Dict[str, str]]:
    """
    Get font definitions for embedding.

    Returns:
        Dictionary mapping font filename to font metadata.
    """
    return {
        "GoogleSans-Regular.ttf": {
            "font_family": "Google Sans",
            "font_weight": "normal",
            "font_style": "normal",
            "id": "google-sans-regular",
        },
        "GoogleSans-Bold.ttf": {
            "font_family": "Google Sans",
            "font_weight": "bold",
            "font_style": "normal",
            "id": "google-sans-bold",
        },
        "GoogleSans-Italic.ttf": {
            "font_family": "Google Sans",
            "font_weight": "normal",
            "font_style": "italic",
            "id": "google-sans-italic",
        },
        "GoogleSans-BoldItalic.ttf": {
            "font_family": "Google Sans",
            "font_weight": "bold",
            "font_style": "italic",
            "id": "google-sans-bolditalic",
        },
    }


# Font CSS template
FONT_FACE_CSS_TEMPLATE = """@font-face {{
  font-family: "{font_family}";
  src: url("../fonts/{filename}") format("truetype");
  font-weight: {font_weight};
  font-style: {font_style};
}}
"""


# ============================================================================
# IMAGE PROCESSING
# ============================================================================

def get_image_config() -> Dict[str, Any]:
    """Get image processing configuration."""
    config = load_config()
    return config.get('builder', {}).get('images', {
        'cover_max_width': 1600,
        'illustration_max_width': 1200,
        'quality': 85
    })


# ============================================================================
# XHTML STRUCTURE SETTINGS
# ============================================================================

# Files to discard from source EPUB (front/back matter to regenerate)
DISCARD_XHTML_FILES = {
    "p-titlepage.xhtml",
    "p-toc-001.xhtml",
    "p-toc-002.xhtml",
    "p-caution.xhtml",
    "p-colophon.xhtml",
    "p-colophon2.xhtml",
    "p-allcover-001.xhtml",
    "p-bookwalker.xhtml",
}


# ============================================================================
# SPINE DIRECTION
# ============================================================================

def get_spine_direction(source_lang: str) -> str:
    """
    Determine spine direction based on source language.

    Args:
        source_lang: Source language code (e.g., 'ja', 'zh', 'ar')

    Returns:
        'ltr' for left-to-right, 'rtl' for right-to-left
    """
    # RTL languages
    rtl_languages = {'ar', 'he', 'fa', 'ur'}

    # Vertical/RTL traditional (Japanese can be either, default to LTR for translation)
    if source_lang in rtl_languages:
        return 'rtl'

    return 'ltr'


# ============================================================================
# CSS FONT REPLACEMENTS
# ============================================================================

# Japanese font families to replace with target font
FONT_FAMILY_REPLACEMENTS = {
    "serif-ja": "Google Sans",
    "serif-ja-v": "Google Sans",
    "sans-serif-ja": "Google Sans",
    "sans-serif-ja-v": "Google Sans",
}


# ============================================================================
# PARAGRAPH FORMATTING
# ============================================================================

# Collapse consecutive blank lines
COLLAPSE_BLANK_LINES = True

# Keep 1 in N consecutive blank lines (1=all, 2=every other)
BLANK_LINE_FREQUENCY = 2
