#!/usr/bin/env python3
"""
Standalone script to format scene breaks in existing translated files.
Can be run on individual files or entire directories.

Usage:
    python format_scene_breaks.py <file_or_directory>
    python format_scene_breaks.py WORK/volume_name/EN/
    python format_scene_breaks.py WORK/volume_name/EN/CHAPTER_01.md
"""

import sys
import argparse
import logging
from pathlib import Path
from pipeline.translator.scene_break_formatter import SceneBreakFormatter

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def format_directory(directory: Path, recursive: bool = False) -> dict:
    """
    Format all markdown files in a directory.
    
    Args:
        directory: Directory to process
        recursive: Whether to process subdirectories
        
    Returns:
        Dictionary with statistics
    """
    stats = {
        'files_processed': 0,
        'files_modified': 0,
        'total_replacements': 0,
        'errors': 0
    }
    
    # Find all markdown files
    pattern = "**/*.md" if recursive else "*.md"
    md_files = list(directory.glob(pattern))
    
    if not md_files:
        logger.warning(f"No markdown files found in {directory}")
        return stats
    
    logger.info(f"Found {len(md_files)} markdown file(s) to process")
    
    for md_file in md_files:
        stats['files_processed'] += 1
        count = SceneBreakFormatter.format_file(md_file)
        
        if count is None:
            stats['errors'] += 1
        elif count > 0:
            stats['files_modified'] += 1
            stats['total_replacements'] += count
    
    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Format scene breaks in translated markdown files"
    )
    parser.add_argument(
        "path",
        type=str,
        help="Path to file or directory to process"
    )
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Process directories recursively"
    )
    
    args = parser.parse_args()
    path = Path(args.path)
    
    if not path.exists():
        logger.error(f"Path not found: {path}")
        sys.exit(1)
    
    # Process based on path type
    if path.is_file():
        if path.suffix.lower() != '.md':
            logger.error(f"Not a markdown file: {path}")
            sys.exit(1)
        
        count = SceneBreakFormatter.format_file(path)
        if count is None:
            logger.error("Processing failed")
            sys.exit(1)
        elif count > 0:
            logger.info(f"✓ Successfully formatted {count} scene break(s)")
        else:
            logger.info("✓ No scene breaks found")
    
    elif path.is_dir():
        stats = format_directory(path, args.recursive)
        
        logger.info("\n" + "="*50)
        logger.info("SUMMARY")
        logger.info("="*50)
        logger.info(f"Files processed:     {stats['files_processed']}")
        logger.info(f"Files modified:      {stats['files_modified']}")
        logger.info(f"Total replacements:  {stats['total_replacements']}")
        logger.info(f"Errors:              {stats['errors']}")
        logger.info("="*50)
        
        if stats['errors'] > 0:
            sys.exit(1)
    
    else:
        logger.error(f"Invalid path type: {path}")
        sys.exit(1)


if __name__ == "__main__":
    main()
