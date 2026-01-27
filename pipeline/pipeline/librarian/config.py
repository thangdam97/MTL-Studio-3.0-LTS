"""
Librarian Agent Configuration - EPUB Input Processing Settings.

Language-agnostic configuration for extracting and parsing source EPUBs.
"""

from pathlib import Path
from typing import Dict, Any, List
from ..config import load_config, INPUT_DIR, WORK_DIR, get_target_language


# ============================================================================
# INPUT PROCESSING SETTINGS
# ============================================================================

def get_input_dir() -> Path:
    """Get input directory for source EPUBs."""
    return INPUT_DIR


def get_work_dir() -> Path:
    """Get working directory for extracted content."""
    return WORK_DIR


# ============================================================================
# EPUB PARSING SETTINGS
# ============================================================================

# Common EPUB content directory names
EPUB_CONTENT_DIRS = ["OEBPS", "OPS", "EPUB", "item", "content"]

# Common OPF filenames
OPF_FILENAMES = ["content.opf", "package.opf", "standard.opf"]

# Image file extensions to catalog
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}

# Cover image patterns to search for
COVER_PATTERNS = [
    "cover.jpg", "cover.jpeg", "cover.png",
    "Cover.jpg", "Cover.jpeg", "Cover.png",
    "i-cover.jpg", "i-cover.png",
]


# ============================================================================
# CONTENT EXTRACTION SETTINGS
# ============================================================================

# Ruby tag handling (for CJK languages)
REMOVE_RUBY_TAGS = True

# Vertical text class to remove
REMOVE_VERTICAL_TEXT_CLASS = True

# Scene break marker (generic)
SCENE_BREAK_MARKER = "* * *"

# Illustration placeholder pattern for markdown output
ILLUSTRATION_PLACEHOLDER_PATTERN = r'\[ILLUSTRATION:?\s*"?([^"\]]+)"?\]'


# ============================================================================
# OUTPUT STRUCTURE
# ============================================================================

def get_volume_structure() -> Dict[str, str]:
    """
    Get the standard volume directory structure.
    
    Uses target_language from config.yaml to determine the translated chapters
    directory name (e.g., "EN" for English, "VN" for Vietnamese).

    Returns:
        Dictionary mapping directory purpose to relative path.
    """
    target_lang = get_target_language().upper()  # "en" -> "EN", "vn" -> "VN"
    
    return {
        "source_chapters": "JP",      # Source language chapters (markdown)
        "translated_chapters": target_lang,   # Translated chapters (uses config target_language)
        "qc_reports": "QC",           # Quality control reports (JSON)
        "assets": "assets",           # Images and media
        "kuchie": "assets/kuchie",    # Color illustrations
        "illustrations": "assets/illustrations",  # Chapter illustrations
        "epub_extracted": "_epub_extracted",  # Raw extracted EPUB
    }


# ============================================================================
# CHAPTER FILE PATTERNS
# ============================================================================

def get_chapter_patterns() -> Dict[str, str]:
    """
    Get regex patterns for detecting chapter types.

    Returns:
        Dictionary mapping chapter type to regex pattern.
    """
    return {
        "prologue": r"(?i)(prologue|プロローグ|序章)",
        "chapter": r"(?i)(chapter\s*\d+|第\d+章|chương\s*\d+)",
        "interlude": r"(?i)(interlude|幕間|막간)",
        "epilogue": r"(?i)(epilogue|エピローグ|終章)",
        "afterword": r"(?i)(afterword|あとがき|후기)",
    }


# ============================================================================
# METADATA EXTRACTION
# ============================================================================

# ============================================================================
# PRE-TOC CONTENT DETECTION (Unlisted Opening Hooks)
# ============================================================================

def get_pre_toc_detection_config() -> Dict[str, Any]:
    """
    Configuration for detecting story content that appears before the first
    TOC entry (common in light novels with opening hooks).
    
    This is an EXCEPTIONALLY RARE case - most EPUBs don't have this.
    Enable only if you know your publisher uses this pattern.
    
    Returns:
        Dictionary with detection settings.
    """
    config = load_config()
    
    # Get user config or use defaults
    user_config = config.get("pre_toc_detection", {})
    
    return {
        # Enable/disable detection (default: True for safety)
        "enabled": user_config.get("enabled", True),
        
        # Minimum text length to consider as story content (characters)
        "min_text_length": user_config.get("min_text_length", 50),
        
        # Minimum number of sentences for credit-heavy files
        "min_sentences_after_credits": user_config.get("min_sentences_after_credits", 2),
        
        # Story content markers (dialog, pronouns, etc.)
        "story_markers": {
            "dialog": user_config.get("dialog_markers", ["「", "」", """, """]),
            "pronouns": user_config.get("pronouns", ["俺", "私", "僕", "わたし", "I"]),
        },
        
        # Credit/metadata markers (to filter out)
        "credit_markers": user_config.get("credit_markers", [
            "イラスト", "著者", "発行", "印刷", "装丁", "デザイン",
            "Illustration", "Author", "Published", "Printed"
        ]),
        
        # Files to exclude (patterns)
        "exclude_patterns": user_config.get("exclude_patterns", [
            "fmatter", "kuchie", "cover", "titlepage", "caution"
        ]),
        
        # Title for pre-TOC content chapter
        "chapter_title": user_config.get("chapter_title", "Opening"),
    }


# ============================================================================
# METADATA EXTRACTION
# ============================================================================

def get_metadata_namespaces() -> Dict[str, str]:
    """
    Get XML namespaces used in EPUB metadata.

    Returns:
        Dictionary mapping prefix to namespace URI.
    """
    return {
        "opf": "http://www.idpf.org/2007/opf",
        "dc": "http://purl.org/dc/elements/1.1/",
        "dcterms": "http://purl.org/dc/terms/",
        "container": "urn:oasis:names:tc:opendocument:xmlns:container",
    }
