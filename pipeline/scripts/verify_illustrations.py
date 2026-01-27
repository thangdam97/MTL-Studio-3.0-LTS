#!/usr/bin/env python3
"""Verify that all illustrations in the manifest are present in the EN chapter files."""

import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def verify_illustrations(work_dir: Path):
    """
    Verify illustration placeholders in EN chapter files based on the manifest.

    Args:
        work_dir: The root directory of the novel (e.g., WORK/novel_id).
    """
    manifest_path = work_dir / "manifest.json"
    en_dir = work_dir / "EN"

    if not manifest_path.exists():
        logger.error(f"manifest.json not found in {work_dir}")
        return

    if not en_dir.exists() or not en_dir.is_dir():
        logger.error(f"EN directory not found in {work_dir}")
        return

    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    all_found = True
    total_missing = 0

    logger.info(f"Verifying illustrations for novel: {manifest.get('volume_id', 'Unknown')}")
    logger.info("=" * 70)

    for chapter in manifest.get("chapters", []):
        en_filename = chapter.get("en_file")
        illustrations = chapter.get("illustrations", [])
        
        if not en_filename:
            logger.warning(f"Chapter '{chapter.get('id')}' is missing 'en_file' entry in manifest.")
            continue

        chapter_path = en_dir / en_filename
        if not chapter_path.exists():
            logger.error(f"Chapter file not found: {chapter_path}")
            all_found = False
            total_missing += len(illustrations)
            continue
            
        logger.info(f"Checking {chapter_path.name}...")

        with open(chapter_path, 'r', encoding='utf-8') as f:
            content = f.read()

        chapter_missing = False
        for illus in illustrations:
            placeholder = f"[ILLUSTRATION: {illus}]"
            if placeholder not in content:
                logger.error(f"  ✗ MISSING: {placeholder}")
                all_found = False
                chapter_missing = True
                total_missing += 1
        
        if not chapter_missing:
            logger.info(f"  ✓ OK ({len(illustrations)} illustrations found)")

    logger.info("=" * 70)
    if all_found:
        logger.info("✓ SUCCESS: All illustrations are correctly referenced in the EN chapter files.")
    else:
        logger.error(f"✗ FAILED: A total of {total_missing} illustration reference(s) are missing.")
    logger.info("=" * 70)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Verify illustration placeholders in translated files.")
    parser.add_argument("work_dir", type=str, help="Path to the novel's WORK directory.")
    args = parser.parse_args()
    
    verify_illustrations(Path(args.work_dir))
