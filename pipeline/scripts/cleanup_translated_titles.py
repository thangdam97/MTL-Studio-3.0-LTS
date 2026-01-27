#!/usr/bin/env python3
"""
Post-Translation Title Cleanup Script

Cleans up translated chapter markdown files by:
1. Removing incorrect "# Chapter X:" prefixes from titles
2. Removing [ILLUSTRATION: ...] markers from titles
3. Preserving actual content illustration markers in body

Usage:
    python cleanup_translated_titles.py --volume VOLUME_ID [--dry-run]
    python cleanup_translated_titles.py --file CHAPTER_FILE.md [--dry-run]
"""

import argparse
import re
import logging
from pathlib import Path
from typing import List, Tuple

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


class TitleCleanup:
    """Cleans up post-translation artifacts in chapter titles."""
    
    # Pattern: # Chapter 123: Actual Title
    CHAPTER_PREFIX_PATTERN = re.compile(r'^(#\s+)Chapter\s+\d+:\s+(.+)$', re.MULTILINE)
    
    # Pattern: [ILLUSTRATION: filename.jpg] as separate block after title
    # Matches: # Chapter 4\n\n[ILLUSTRATION: m045.jpg]\n
    TITLE_ILLUSTRATION_PATTERN = re.compile(r'^(#[^\n]+)\s*\n\s*\[ILLUSTRATION:[^\]]+\]\s*\n', re.MULTILINE)
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.stats = {
            'files_processed': 0,
            'titles_cleaned': 0,
            'illustrations_removed': 0
        }
    
    def clean_chapter_prefix(self, content: str) -> Tuple[str, int]:
        """
        Remove "# Chapter X:" prefix from titles.
        
        Before: # Chapter 2: Everyone Thinks I'm Dating the Blonde...
        After:  # Everyone Thinks I'm Dating the Blonde...
        
        Returns:
            (cleaned_content, num_changes)
        """
        changes = 0
        
        def replace_prefix(match):
            nonlocal changes
            changes += 1
            heading_marker = match.group(1)  # Keep the "# "
            actual_title = match.group(2)    # Keep the actual title
            return f"{heading_marker}{actual_title}"
        
        cleaned = self.CHAPTER_PREFIX_PATTERN.sub(replace_prefix, content)
        return cleaned, changes
    
    def clean_title_illustrations(self, content: str) -> Tuple[str, int]:
        """
        Remove illustration markers that appear as separate blocks after titles.
        PRESERVES inline illustrations like: # Title [ILLUSTRATION: img.jpg]
        
        Removes:  # Chapter 4
                  
                  [ILLUSTRATION: m045.jpg]
        
        Keeps:    # Chapter 7: Title [ILLUSTRATION: battle.jpg]
        
        Returns:
            (cleaned_content, num_changes)
        """
        changes = 0
        
        def remove_title_illust(match):
            nonlocal changes
            changes += 1
            # Keep the title (group 1), discard the illustration block
            return match.group(1) + '\n\n'
        
        cleaned = self.TITLE_ILLUSTRATION_PATTERN.sub(remove_title_illust, content)
        
        return cleaned, changes
    
    def clean_file(self, file_path: Path) -> bool:
        """
        Clean a single markdown file.
        
        Returns:
            True if changes were made, False otherwise
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            
            # Apply cleanups
            content, prefix_changes = self.clean_chapter_prefix(content)
            content, illust_changes = self.clean_title_illustrations(content)
            
            total_changes = prefix_changes + illust_changes
            
            if total_changes > 0:
                logger.info(f"  {file_path.name}:")
                if prefix_changes > 0:
                    logger.info(f"    - Cleaned {prefix_changes} chapter prefix(es)")
                if illust_changes > 0:
                    logger.info(f"    - Removed {illust_changes} title illustration marker(s)")
                
                if not self.dry_run:
                    file_path.write_text(content, encoding='utf-8')
                    logger.info(f"    ✓ Saved")
                else:
                    logger.info(f"    [DRY RUN] Would save changes")
                
                self.stats['titles_cleaned'] += prefix_changes
                self.stats['illustrations_removed'] += illust_changes
                self.stats['files_processed'] += 1
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"  ✗ Failed to process {file_path.name}: {e}")
            return False
    
    def clean_volume(self, volume_id: str, work_dir: Path = None) -> bool:
        """
        Clean all translated chapters in a volume.
        
        Args:
            volume_id: Volume identifier
            work_dir: Base work directory (defaults to WORK/)
        
        Returns:
            True if successful, False otherwise
        """
        if work_dir is None:
            work_dir = Path(__file__).parent.parent / "WORK"
        
        volume_path = work_dir / volume_id
        if not volume_path.exists():
            logger.error(f"Volume directory not found: {volume_path}")
            return False
        
        # Find translated chapter files
        translated_dir = volume_path / "chapters_translated"
        if not translated_dir.exists():
            logger.warning(f"No translated chapters directory: {translated_dir}")
            return False
        
        chapter_files = sorted(translated_dir.glob("CHAPTER_*_EN.md"))
        
        if not chapter_files:
            logger.warning(f"No translated chapter files found in {translated_dir}")
            return False
        
        logger.info(f"Processing {len(chapter_files)} translated chapters in {volume_id}...")
        
        files_changed = 0
        for chapter_file in chapter_files:
            if self.clean_file(chapter_file):
                files_changed += 1
        
        logger.info(f"\n✓ Cleanup complete:")
        logger.info(f"  Files processed: {self.stats['files_processed']}")
        logger.info(f"  Chapter prefixes cleaned: {self.stats['titles_cleaned']}")
        logger.info(f"  Illustration markers removed: {self.stats['illustrations_removed']}")
        
        if self.dry_run:
            logger.info(f"\n[DRY RUN] No files were modified")
        
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Clean up post-translation artifacts in chapter titles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Clean all chapters in a volume
  python cleanup_translated_titles.py --volume makehero_v1
  
  # Preview changes without modifying files
  python cleanup_translated_titles.py --volume makehero_v1 --dry-run
  
  # Clean a single chapter file
  python cleanup_translated_titles.py --file WORK/makehero_v1/chapters_translated/CHAPTER_01_EN.md
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--volume', help='Volume ID to process')
    group.add_argument('--file', type=Path, help='Single chapter file to process')
    
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview changes without modifying files')
    parser.add_argument('--work-dir', type=Path,
                       help='Base work directory (default: WORK/)')
    
    args = parser.parse_args()
    
    cleanup = TitleCleanup(dry_run=args.dry_run)
    
    if args.file:
        # Clean single file
        if not args.file.exists():
            logger.error(f"File not found: {args.file}")
            return 1
        
        logger.info(f"Processing single file: {args.file}")
        cleanup.clean_file(args.file)
        
        logger.info(f"\n✓ Cleanup complete:")
        logger.info(f"  Chapter prefixes cleaned: {cleanup.stats['titles_cleaned']}")
        logger.info(f"  Illustration markers removed: {cleanup.stats['illustrations_removed']}")
        
    else:
        # Clean volume
        success = cleanup.clean_volume(args.volume, args.work_dir)
        if not success:
            return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
