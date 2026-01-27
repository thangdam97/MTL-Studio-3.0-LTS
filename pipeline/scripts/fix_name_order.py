#!/usr/bin/env python3
"""
Name Order Validator and Fixer
Automatically converts character names from Western order (Given + Family) 
to Japanese order (Family + Given) in metadata files.

Usage:
    python fix_name_order.py [volume_path]
    python fix_name_order.py --all  # Process all volumes in WORK/
"""

import json
import re
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime


class NameOrderFixer:
    def __init__(self, work_dir: Path = None):
        if work_dir is None:
            self.work_dir = Path(__file__).parent.parent / "WORK"
        else:
            self.work_dir = Path(work_dir)
        
        # Common Japanese family names for validation
        self.common_family_names = {
            "Ninomiya", "Shinonome", "Nakamura", "Seno", "Matsumoto", 
            "Ueno", "Enomoto", "Saito", "Tanaka", "Suzuki", "Watanabe",
            "Yamamoto", "Kobayashi", "Sato", "Takahashi", "Ito", "Yoshida",
            "Yamada", "Sasaki", "Yamaguchi", "Kato", "Inoue", "Kimura",
            "Hayashi", "Shimizu", "Mori", "Ikeda", "Hashimoto", "Ishikawa",
            "Fujita", "Ogawa", "Goto", "Okada", "Hasegawa", "Murakami",
            "Kondo", "Ishii", "Maeda", "Fujii", "Nishimura", "Fukuda"
        }
        
        # Common Japanese given names for detection
        self.common_given_names = {
            "Daigo", "Sena", "Yuki", "Ayuka", "China", "Saki", "Shiori",
            "Haruto", "Sota", "Yuto", "Hinata", "Riku", "Akira", "Kaito",
            "Sakura", "Hana", "Yui", "Aoi", "Rin", "Mei", "Mio", "Nana"
        }
        
        self.fixes_made = []
        self.errors = []
    
    def is_western_order(self, name_en: str, name_jp: str) -> Tuple[bool, str, str]:
        """
        Detect if English name uses Western order (Given + Family).
        Returns: (is_western, family_name, given_name)
        """
        parts = name_en.strip().split()
        if len(parts) != 2:
            return False, "", ""
        
        first, last = parts[0], parts[1]
        
        # Check if last part is a known family name
        if last in self.common_family_names:
            # Western order detected: "Daigo Ninomiya" (Given + Family)
            return True, last, first
        
        # Check if first part is a known family name
        if first in self.common_family_names:
            # Japanese order: "Ninomiya Daigo" (Family + Given)
            return False, first, last
        
        # Heuristic: If first part is a known given name, likely Western order
        if first in self.common_given_names and last not in self.common_given_names:
            return True, last, first
        
        return False, "", ""
    
    def fix_metadata_file(self, metadata_path: Path, dry_run: bool = False) -> Dict:
        """Fix name order in a metadata_en.json file."""
        print(f"\n{'[DRY RUN] ' if dry_run else ''}Checking: {metadata_path.parent.name}")
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        changes = {
            "file": str(metadata_path),
            "glossary_fixes": [],
            "character_fixes": []
        }
        
        # Check glossary section
        if "glossary" in data:
            for name_jp, name_en in data["glossary"].items():
                is_western, family, given = self.is_western_order(name_en, name_jp)
                if is_western:
                    correct_order = f"{family} {given}"
                    changes["glossary_fixes"].append({
                        "japanese": name_jp,
                        "old": name_en,
                        "new": correct_order
                    })
                    print(f"  ❌ Glossary: {name_jp}")
                    print(f"     {name_en} → {correct_order}")
                    if not dry_run:
                        data["glossary"][name_jp] = correct_order
        
        # Check characters array
        if "characters" in data:
            for char in data["characters"]:
                if "name_jp" in char and "name_en" in char:
                    name_jp = char["name_jp"]
                    name_en = char["name_en"]
                    is_western, family, given = self.is_western_order(name_en, name_jp)
                    if is_western:
                        correct_order = f"{family} {given}"
                        changes["character_fixes"].append({
                            "japanese": name_jp,
                            "old": name_en,
                            "new": correct_order,
                            "role": char.get("role", "unknown")
                        })
                        print(f"  ❌ Character: {name_jp} ({char.get('role', 'unknown')})")
                        print(f"     {name_en} → {correct_order}")
                        if not dry_run:
                            char["name_en"] = correct_order
        
        # Save changes
        if not dry_run and (changes["glossary_fixes"] or changes["character_fixes"]):
            # Backup original
            backup_path = metadata_path.with_suffix('.json.bak')
            shutil.copy2(metadata_path, backup_path)
            print(f"  💾 Backup: {backup_path.name}")
            
            # Write corrected data
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"  ✅ Fixed: {len(changes['glossary_fixes'])} glossary + {len(changes['character_fixes'])} characters")
        
        elif changes["glossary_fixes"] or changes["character_fixes"]:
            print(f"  ⚠️  Would fix: {len(changes['glossary_fixes'])} glossary + {len(changes['character_fixes'])} characters")
        else:
            print(f"  ✅ No issues found")
        
        return changes
    
    def process_volume(self, volume_path: Path, dry_run: bool = False) -> Dict:
        """Process a single volume directory."""
        metadata_path = volume_path / "metadata_en.json"
        
        if not metadata_path.exists():
            print(f"⚠️  No metadata_en.json in {volume_path.name}")
            return None
        
        try:
            changes = self.fix_metadata_file(metadata_path, dry_run=dry_run)
            if changes and (changes["glossary_fixes"] or changes["character_fixes"]):
                self.fixes_made.append(changes)
            return changes
        except Exception as e:
            error_msg = f"Error processing {volume_path.name}: {e}"
            print(f"❌ {error_msg}")
            self.errors.append(error_msg)
            return None
    
    def process_all_volumes(self, pattern: str = "*", dry_run: bool = False):
        """Process all volumes matching pattern."""
        print(f"{'='*70}")
        print(f"Name Order Validator - {'DRY RUN MODE' if dry_run else 'LIVE MODE'}")
        print(f"{'='*70}")
        print(f"Workspace: {self.work_dir}")
        print(f"Pattern: {pattern}")
        print()
        
        volumes = sorted(self.work_dir.glob(f"{pattern}"))
        volumes = [v for v in volumes if v.is_dir() and not v.name.startswith('.')]
        
        print(f"Found {len(volumes)} volumes to check")
        
        for volume_path in volumes:
            self.process_volume(volume_path, dry_run=dry_run)
        
        self.print_summary()
    
    def print_summary(self):
        """Print summary of all changes."""
        print(f"\n{'='*70}")
        print("SUMMARY")
        print(f"{'='*70}")
        
        total_glossary = sum(len(f["glossary_fixes"]) for f in self.fixes_made)
        total_characters = sum(len(f["character_fixes"]) for f in self.fixes_made)
        
        print(f"Volumes processed: {len(self.fixes_made)}")
        print(f"Total glossary fixes: {total_glossary}")
        print(f"Total character fixes: {total_characters}")
        print(f"Errors: {len(self.errors)}")
        
        if self.errors:
            print("\nErrors encountered:")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.fixes_made:
            print("\nDetailed Changes:")
            for change in self.fixes_made:
                vol_name = Path(change["file"]).parent.name
                print(f"\n📚 {vol_name}")
                
                if change["glossary_fixes"]:
                    print("  Glossary:")
                    for fix in change["glossary_fixes"]:
                        print(f"    {fix['japanese']}: {fix['old']} → {fix['new']}")
                
                if change["character_fixes"]:
                    print("  Characters:")
                    for fix in change["character_fixes"]:
                        print(f"    {fix['japanese']} ({fix['role']}): {fix['old']} → {fix['new']}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Fix name order in metadata files (Western → Japanese order)"
    )
    parser.add_argument(
        "path",
        nargs="?",
        help="Path to specific volume or '--all' for all volumes"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes"
    )
    parser.add_argument(
        "--pattern",
        default="学年一*",
        help="Volume name pattern (default: 学年一*)"
    )
    parser.add_argument(
        "--work-dir",
        help="Custom WORK directory path"
    )
    
    args = parser.parse_args()
    
    fixer = NameOrderFixer(work_dir=args.work_dir)
    
    if args.path == "--all" or args.path is None:
        fixer.process_all_volumes(pattern=args.pattern, dry_run=args.dry_run)
    else:
        volume_path = Path(args.path)
        if not volume_path.exists():
            print(f"❌ Path not found: {volume_path}")
            return 1
        fixer.process_volume(volume_path, dry_run=args.dry_run)
        fixer.print_summary()
    
    return 0


if __name__ == "__main__":
    exit(main())
