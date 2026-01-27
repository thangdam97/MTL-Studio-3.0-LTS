#!/usr/bin/env python3
"""
Extraction Migration Utility

Handles re-extraction scenarios by preserving translation progress and state
when librarian needs to re-run (pattern fixes, publisher profile updates, etc.)

Usage:
    python scripts/migrate_extraction.py --old WORK/volume_old --new WORK/volume_new
    python scripts/migrate_extraction.py --auto-detect volume_title

Features:
- Automatic old extraction detection (finds most recent matching volume)
- VN folder preservation (copy translated chapters)
- Manifest state migration (pipeline_state, vn_file references, translated flags)
- Atomic updates with rollback on failure
- Validation before allowing next phase

Integration:
- Phase 1 now warns when re-extracting over existing translations
- Recommends using this script instead of losing progress
- Cancel extraction and run this script to migrate state to new extraction
"""

import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Tuple

class MigrationError(Exception):
    """Raised when migration fails."""
    pass

class ExtractionMigrator:
    """Handles migration from old to new extraction."""
    
    def __init__(self, old_dir: Path, new_dir: Path, verbose: bool = True):
        self.old_dir = Path(old_dir)
        self.new_dir = Path(new_dir)
        self.verbose = verbose
        self.backup_suffix = f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def log(self, msg: str, level: str = "INFO"):
        """Print log message."""
        if self.verbose:
            prefix = {
                "INFO": "ℹ️ ",
                "SUCCESS": "✅",
                "WARNING": "⚠️ ",
                "ERROR": "❌"
            }.get(level, "  ")
            print(f"{prefix} {msg}")
    
    def validate_directories(self) -> None:
        """Ensure source and target directories exist and are valid."""
        if not self.old_dir.exists():
            raise MigrationError(f"Old extraction not found: {self.old_dir}")
        
        if not self.new_dir.exists():
            raise MigrationError(f"New extraction not found: {self.new_dir}")
        
        old_manifest = self.old_dir / "manifest.json"
        new_manifest = self.new_dir / "manifest.json"
        
        if not old_manifest.exists():
            raise MigrationError(f"Old manifest not found: {old_manifest}")
        
        if not new_manifest.exists():
            raise MigrationError(f"New manifest not found: {new_manifest}")
    
    def backup_new_manifest(self) -> Path:
        """Backup new manifest before modification."""
        manifest_path = self.new_dir / "manifest.json"
        backup_path = self.new_dir / f"manifest.json{self.backup_suffix}"
        shutil.copy2(manifest_path, backup_path)
        self.log(f"Backed up new manifest: {backup_path.name}")
        return backup_path
    
    def load_manifests(self) -> Tuple[Dict, Dict]:
        """Load old and new manifests."""
        with open(self.old_dir / "manifest.json", encoding='utf-8') as f:
            old_manifest = json.load(f)
        
        with open(self.new_dir / "manifest.json", encoding='utf-8') as f:
            new_manifest = json.load(f)
        
        return old_manifest, new_manifest
    
    def copy_vn_folder(self) -> Optional[Path]:
        """Copy VN folder from old to new extraction."""
        old_vn = self.old_dir / "VN"
        new_vn = self.new_dir / "VN"
        
        if not old_vn.exists():
            self.log("No VN folder in old extraction - skipping", "WARNING")
            return None
        
        if new_vn.exists():
            self.log("VN folder already exists in new extraction - backing up", "WARNING")
            backup_vn = self.new_dir / f"VN{self.backup_suffix}"
            shutil.move(str(new_vn), str(backup_vn))
        
        shutil.copytree(old_vn, new_vn)
        vn_files = list(new_vn.glob("*.md"))
        self.log(f"Copied VN folder: {len(vn_files)} chapters", "SUCCESS")
        return new_vn
    
    def migrate_chapter_metadata(self, old_manifest: Dict, new_manifest: Dict) -> int:
        """Migrate chapter-level metadata (vn_file, translated flags)."""
        migrated = 0
        
        if len(old_manifest['chapters']) != len(new_manifest['chapters']):
            self.log(
                f"Chapter count mismatch: old={len(old_manifest['chapters'])}, new={len(new_manifest['chapters'])}",
                "WARNING"
            )
        
        for i in range(min(len(old_manifest['chapters']), len(new_manifest['chapters']))):
            old_ch = old_manifest['chapters'][i]
            new_ch = new_manifest['chapters'][i]
            
            # Migrate vn_file reference
            if 'vn_file' in old_ch:
                new_ch['vn_file'] = old_ch['vn_file']
                migrated += 1
            
            # Migrate translated flag
            if old_ch.get('translated', False):
                new_ch['translated'] = True
        
        self.log(f"Migrated metadata for {migrated} chapters", "SUCCESS")
        return migrated
    
    def migrate_pipeline_state(self, old_manifest: Dict, new_manifest: Dict) -> None:
        """Migrate pipeline_state from old to new manifest."""
        # Get old state (try both 'state' and 'pipeline_state' for compatibility)
        old_state = old_manifest.get('pipeline_state') or old_manifest.get('state')
        
        if not old_state:
            self.log("No pipeline state in old manifest - initializing fresh", "WARNING")
            return
        
        # Ensure new manifest has pipeline_state (not 'state')
        if 'pipeline_state' not in new_manifest:
            new_manifest['pipeline_state'] = {}
        
        # Migrate librarian state (preserve timestamp from new extraction)
        new_manifest['pipeline_state']['librarian'] = {
            'status': 'completed',
            'timestamp': new_manifest['pipeline_state']['librarian'].get('timestamp', 
                                                                          datetime.now().isoformat()),
            'chapters_completed': new_manifest['pipeline_state']['librarian'].get('chapters_completed', 
                                                                                   len(new_manifest['chapters'])),
            'chapters_total': len(new_manifest['chapters'])
        }
        
        # Migrate translator state (preserve from old)
        old_translator = old_state.get('translator', {})
        translated_count = sum(1 for ch in new_manifest['chapters'] if ch.get('translated', False))
        
        new_manifest['pipeline_state']['translator'] = {
            'status': 'completed' if translated_count == len(new_manifest['chapters']) else 'in_progress',
            'chapters_completed': translated_count,
            'chapters_total': len(new_manifest['chapters']),
            'timestamp': old_translator.get('timestamp') or old_translator.get('completed_at', 
                                                                                datetime.now().isoformat())
        }
        
        # Preserve critics/builder state if they exist
        for stage in ['critics', 'builder']:
            if stage in old_state:
                new_manifest['pipeline_state'][stage] = old_state[stage]
        
        # Remove legacy 'state' field if it exists
        if 'state' in new_manifest:
            del new_manifest['state']
        
        self.log(f"Migrated pipeline state: translator {translated_count}/{len(new_manifest['chapters'])} chapters", 
                 "SUCCESS")
    
    def save_manifest(self, manifest: Dict) -> None:
        """Save updated manifest atomically."""
        manifest_path = self.new_dir / "manifest.json"
        temp_path = self.new_dir / "manifest.json.tmp"
        
        # Write to temp file first
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        # Atomic replace
        temp_path.replace(manifest_path)
        self.log("Saved updated manifest", "SUCCESS")
    
    def validate_migration(self) -> bool:
        """Validate migration was successful."""
        manifest_path = self.new_dir / "manifest.json"
        
        with open(manifest_path, encoding='utf-8') as f:
            manifest = json.load(f)
        
        # Check pipeline_state exists
        if 'pipeline_state' not in manifest:
            self.log("Validation failed: no pipeline_state in manifest", "ERROR")
            return False
        
        # Check translator status
        translator = manifest['pipeline_state'].get('translator', {})
        if translator.get('chapters_completed', 0) == 0:
            self.log("Validation failed: no chapters marked as translated", "ERROR")
            return False
        
        # Check VN files exist
        vn_dir = self.new_dir / "VN"
        if vn_dir.exists():
            vn_files = list(vn_dir.glob("*.md"))
            expected = sum(1 for ch in manifest['chapters'] if ch.get('vn_file'))
            
            if len(vn_files) != expected:
                self.log(
                    f"Validation warning: {len(vn_files)} VN files found, {expected} expected",
                    "WARNING"
                )
        
        self.log("Migration validated successfully", "SUCCESS")
        return True
    
    def rollback(self, backup_path: Path) -> None:
        """Rollback changes on failure."""
        manifest_path = self.new_dir / "manifest.json"
        backup_path.replace(manifest_path)
        self.log("Rolled back changes", "WARNING")
    
    def migrate(self) -> bool:
        """Execute full migration with rollback on failure."""
        try:
            self.log("Starting extraction migration...")
            self.log(f"  Old: {self.old_dir.name}")
            self.log(f"  New: {self.new_dir.name}")
            
            # Step 1: Validate
            self.validate_directories()
            
            # Step 2: Backup
            backup_path = self.backup_new_manifest()
            
            try:
                # Step 3: Load manifests
                old_manifest, new_manifest = self.load_manifests()
                
                # Step 4: Copy VN folder
                self.copy_vn_folder()
                
                # Step 5: Migrate chapter metadata
                self.migrate_chapter_metadata(old_manifest, new_manifest)
                
                # Step 6: Migrate pipeline state
                self.migrate_pipeline_state(old_manifest, new_manifest)
                
                # Step 7: Save
                self.save_manifest(new_manifest)
                
                # Step 8: Validate
                if not self.validate_migration():
                    raise MigrationError("Migration validation failed")
                
                self.log("Migration completed successfully!", "SUCCESS")
                return True
                
            except Exception as e:
                self.log(f"Migration failed: {e}", "ERROR")
                self.rollback(backup_path)
                raise
        
        except MigrationError as e:
            self.log(str(e), "ERROR")
            return False

def find_old_extraction(work_dir: Path, title_fragment: str) -> Optional[Path]:
    """Find most recent extraction matching title fragment."""
    candidates = []
    
    for candidate in work_dir.iterdir():
        if not candidate.is_dir():
            continue
        
        if title_fragment.lower() in candidate.name.lower():
            manifest = candidate / "manifest.json"
            if manifest.exists():
                mtime = manifest.stat().st_mtime
                candidates.append((mtime, candidate))
    
    if not candidates:
        return None
    
    # Return most recent
    candidates.sort(reverse=True)
    return candidates[0][1]

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate extraction progress to new Phase 1 run")
    parser.add_argument("--old", help="Old extraction directory")
    parser.add_argument("--new", help="New extraction directory")
    parser.add_argument("--auto-detect", help="Auto-detect old extraction by title fragment")
    parser.add_argument("--work-dir", default="WORK", help="Work directory (default: WORK)")
    parser.add_argument("--quiet", action="store_true", help="Suppress output")
    
    args = parser.parse_args()
    
    work_dir = Path(args.work_dir)
    
    if args.auto_detect:
        # Find latest extraction matching title
        old_dir = find_old_extraction(work_dir, args.auto_detect)
        if not old_dir:
            print(f"❌ No old extraction found matching: {args.auto_detect}")
            return 1
        
        # Find new extraction (most recent)
        all_dirs = sorted(
            [d for d in work_dir.iterdir() 
             if d.is_dir() and args.auto_detect.lower() in d.name.lower()],
            key=lambda d: (d / "manifest.json").stat().st_mtime if (d / "manifest.json").exists() else 0,
            reverse=True
        )
        
        if len(all_dirs) < 2:
            print(f"❌ Need at least 2 extractions to migrate")
            return 1
        
        new_dir = all_dirs[0]
        old_dir = all_dirs[1]
        
        print(f"Auto-detected:")
        print(f"  Old: {old_dir.name}")
        print(f"  New: {new_dir.name}")
        
    elif args.old and args.new:
        old_dir = Path(args.old)
        new_dir = Path(args.new)
    else:
        parser.print_help()
        return 1
    
    migrator = ExtractionMigrator(old_dir, new_dir, verbose=not args.quiet)
    success = migrator.migrate()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
