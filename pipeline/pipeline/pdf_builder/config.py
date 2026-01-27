"""
PDF Builder Configuration.
"""

from pathlib import Path

# Page settings
PAGE_SIZE = 'A5'  # Standard light novel size (148mm × 210mm)
MARGIN_TOP = '20mm'
MARGIN_BOTTOM = '20mm'
MARGIN_LEFT = '15mm'
MARGIN_RIGHT = '15mm'

# Typography
FONT_FAMILY = 'Georgia, "Times New Roman", serif'
FONT_SIZE = '11pt'
LINE_HEIGHT = '1.6'
TEXT_ALIGN = 'justify'

# Paths
def get_output_dir() -> Path:
    """Get OUTPUT directory path."""
    return Path(__file__).parent.parent.parent / "OUTPUT"

def get_work_dir() -> Path:
    """Get WORK directory path."""
    return Path(__file__).parent.parent.parent / "WORK"
