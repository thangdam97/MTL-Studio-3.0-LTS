"""
Image Analysis Module for EPUB Builder.

Provides utilities for analyzing image dimensions and orientation
to support horizontal kuchi-e auto-rotation and proper image handling.
"""

from pathlib import Path
from typing import Dict, List, Tuple

try:
    from PIL import Image
except ImportError:
    raise ImportError(
        "PIL (Pillow) is required for image analysis. "
        "Install it with: pip install Pillow"
    )


def get_image_dimensions(image_path: Path) -> Tuple[int, int]:
    """
    Extract width and height from an image file using PIL.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Tuple of (width, height) in pixels
        
    Raises:
        FileNotFoundError: If image file doesn't exist
        PIL.UnidentifiedImageError: If file is not a valid image
    """
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    with Image.open(image_path) as img:
        return img.size


def is_horizontal(width: int, height: int) -> bool:
    """
    Determine if image is landscape orientation.
    
    Args:
        width: Image width in pixels
        height: Image height in pixels
        
    Returns:
        True if width > height (landscape), False otherwise (portrait/square)
    """
    return width > height


def analyze_kuchie_images(
    assets_dir: Path,
    kuchie_list: List[str]
) -> Dict[str, dict]:
    """
    Batch analyze all kuchi-e images and return metadata.
    
    Args:
        assets_dir: Base assets directory containing kuchie/ subdirectory
        kuchie_list: List of kuchi-e image filenames
        
    Returns:
        Dictionary mapping filename to metadata dict with keys:
        - 'width': Image width in pixels
        - 'height': Image height in pixels
        - 'is_horizontal': Boolean indicating landscape orientation
        
    Example:
        >>> metadata = analyze_kuchie_images(Path("assets"), ["kuchie-001.jpg"])
        >>> metadata["kuchie-001.jpg"]
        {'width': 1443, 'height': 2048, 'is_horizontal': False}
    """
    metadata = {}
    
    for kuchie in kuchie_list:
        kuchie_path = assets_dir / "kuchie" / kuchie
        
        if not kuchie_path.exists():
            # Try without kuchie subdirectory
            kuchie_path = assets_dir / kuchie
        
        if kuchie_path.exists():
            try:
                width, height = get_image_dimensions(kuchie_path)
                metadata[kuchie] = {
                    'width': width,
                    'height': height,
                    'is_horizontal': is_horizontal(width, height)
                }
            except Exception as e:
                print(f"     [WARNING] Failed to analyze {kuchie}: {e}")
                # Provide default metadata for failed images
                metadata[kuchie] = {
                    'width': 1443,
                    'height': 2048,
                    'is_horizontal': False
                }
        else:
            print(f"     [WARNING] Kuchie image not found: {kuchie}")
    
    return metadata


def get_orientation_label(is_horizontal: bool) -> str:
    """
    Get human-readable orientation label.
    
    Args:
        is_horizontal: Boolean indicating landscape orientation
        
    Returns:
        "horizontal" or "vertical"
    """
    return "horizontal" if is_horizontal else "vertical"
