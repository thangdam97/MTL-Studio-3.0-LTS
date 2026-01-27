"""
Per-Chapter Workflow - Incremental Schema Generation with User Review
Integrates schema extraction, user review, and caching between chapters.
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

from pipeline.translator.schema_extractor import SchemaExtractor, ChapterSnapshot
from pipeline.translator.schema_review import SchemaReviewInterface
from pipeline.translator.schema_cache import SchemaCacheManager

logger = logging.getLogger(__name__)


class PerChapterWorkflow:
    """Manages per-chapter schema extraction, review, and caching."""
    
    def __init__(
        self,
        work_dir: Path,
        target_language: str = "EN",
        enable_caching: bool = True,
        gemini_client=None
    ):
        """
        Initialize per-chapter workflow.
        
        Args:
            work_dir: Volume working directory
            target_language: Target language code (EN, VN, etc.)
            enable_caching: Whether to use Gemini context caching
            gemini_client: Gemini client for caching (optional)
        """
        self.work_dir = work_dir
        self.target_language = target_language.upper()
        self.enable_caching = enable_caching
        
        # Initialize components
        self.extractor = SchemaExtractor(work_dir, target_language)
        self.reviewer = SchemaReviewInterface()
        self.cache_manager = SchemaCacheManager(gemini_client) if enable_caching else None
        
        # Tracking
        self.snapshots = {}  # chapter_num -> ChapterSnapshot
        self.current_cache_name = None
        
        # Load manifest for snapshot tracking
        self.manifest_path = work_dir / "manifest.json"
        self.manifest = self._load_manifest()
    
    def process_chapter(
        self,
        chapter_num: int,
        chapter_id: str,
        translation_text: str,
        skip_review: bool = False
    ) -> tuple[bool, Optional[str]]:
        """
        Process a chapter: extract schema, review, cache.
        
        Args:
            chapter_num: Chapter number (1-indexed)
            chapter_id: Chapter identifier (e.g., "chapter_01")
            translation_text: Translated chapter text
            skip_review: Skip user review (auto-approve)
            
        Returns:
            (success: bool, cache_name: Optional[str])
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"  POST-CHAPTER PROCESSING: {chapter_id.upper()}")
        logger.info(f"{'='*60}\n")
        
        # Step 1: Extract schema
        logger.info(f"[1/4] Extracting schema from translation...")
        previous_snapshot = self.snapshots.get(chapter_num - 1) if chapter_num > 1 else None
        
        try:
            snapshot = self.extractor.extract_from_chapter(
                chapter_num=chapter_num,
                chapter_id=chapter_id,
                translation_text=translation_text,
                previous_snapshot=previous_snapshot
            )
        except Exception as e:
            logger.error(f"Schema extraction failed: {e}")
            return False, None
        
        # Step 2: Compute delta if not first chapter
        delta = None
        if previous_snapshot:
            delta = self.extractor.compute_delta(snapshot, previous_snapshot)
            logger.info(f"✓ Delta computed: {len(delta.get('new_characters', []))} new characters, "
                       f"{len(delta.get('changed_relationships', []))} relationship changes")
        
        # Step 3: User review (unless skipped)
        if not skip_review:
            logger.info(f"\n[2/4] User review required...")
            action, reviewed_snapshot = self.reviewer.show_review(
                snapshot=snapshot,
                previous_snapshot=previous_snapshot,
                delta=delta
            )
            
            if action == 'cancel':
                logger.warning("User cancelled pipeline")
                return False, None
            
            elif action == 're-extract':
                logger.info("Re-extracting schema...")
                # Recursive call to retry
                return self.process_chapter(chapter_num, chapter_id, translation_text, skip_review=False)
            
            snapshot = reviewed_snapshot
            logger.info(f"✓ Schema {'approved' if action == 'approve' else 'corrected'}")
        else:
            logger.info(f"\n[2/4] Skipping review (auto-approve enabled)")
            snapshot.reviewed_by_user = False
        
        # Step 4: Save snapshot
        logger.info(f"\n[3/4] Saving snapshot...")
        try:
            self.extractor.save_snapshot(snapshot)
            self.snapshots[chapter_num] = snapshot
            
            # Update manifest to mark snapshot as created
            self._mark_snapshot_created(chapter_id)
            logger.info(f"✓ Snapshot created and tracked in manifest")
        except Exception as e:
            logger.error(f"Failed to save snapshot: {e}")
            return False, None
            self._mark_snapshot_created(chapter_id)
            logger.info(f"✓ Snapshot created and tracked in manifest")
        except Exception as e:
            logger.error(f"Failed to save snapshot: {e}")
            return False, None
        
        # Step 5: Cache for next chapter
        cache_name = None
        if self.enable_caching and self.cache_manager:
            logger.info(f"\n[4/4] Caching schema for Chapter {chapter_num + 1}...")
            try:
                # Invalidate previous cache
                if self.current_cache_name:
                    self.cache_manager.invalidate_cache(self.current_cache_name)
                
                # Create new cache
                cache_name = self.cache_manager.cache_schema(
                    snapshot=snapshot,
                    work_dir=self.work_dir,
                    ttl_hours=2  # 2 hours for user review + next translation
                )
                
                if cache_name:
                    self.current_cache_name = cache_name
                    logger.info(f"✓ Schema cached for next chapter")
                else:
                    logger.warning("Cache creation skipped or failed")
            except Exception as e:
                logger.error(f"Caching failed: {e}")
                # Don't fail the whole process if caching fails
        else:
            logger.info(f"\n[4/4] Caching disabled, skipping...")
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✓ Chapter {chapter_num} processing complete")
        logger.info(f"{'='*60}\n")
        
        return True, cache_name
    
    def get_cache_for_chapter(self, chapter_num: int) -> Optional[str]:
        """
        Get cached content name for a chapter.
        
        Args:
            chapter_num: Chapter number to get cache for
            
        Returns:
            Cache name if available, None otherwise
        """
        if not self.cache_manager:
            return None
        
        return self.cache_manager.get_cached_content_name(self.work_dir, chapter_num)
    
    def load_previous_snapshot(self, chapter_num: int) -> Optional[ChapterSnapshot]:
        """
        Load snapshot from previous chapter.
        
        Args:
            chapter_num: Current chapter number (will load chapter_num - 1)
            
        Returns:
            Previous chapter's snapshot if exists
        """
        if chapter_num <= 1:
            return None
        
        previous_chapter_id = f"chapter_{chapter_num - 1:02d}"
        
        # Try cached snapshot first
        if chapter_num - 1 in self.snapshots:
            return self.snapshots[chapter_num - 1]
        
        # Try loading from disk
        return self.extractor.load_snapshot(previous_chapter_id)
    
    def finalize(self) -> Dict:
        """
        Finalize after all chapters processed.
        
        Returns:
            Summary of schema evolution
        """
        logger.info("\n" + "="*60)
        logger.info("  FINALIZING CONTINUITY PACK")
        logger.info("="*60 + "\n")
        
        # Aggregate all snapshots into continuity pack
        final_snapshot = self.snapshots.get(max(self.snapshots.keys())) if self.snapshots else None
        
        if not final_snapshot:
            logger.warning("No snapshots to finalize")
            return {}
        
        # Save final continuity pack
        continuity_pack_path = self.work_dir / ".context" / "continuity_pack.json"
        
        pack_data = {
            "schema_version": "2.0",
            "volume_id": self.work_dir.name,
            "last_chapter_processed": final_snapshot.chapter_id,
            "target_language": self.target_language,
            "chapter_snapshots": [],
            "final_state": {
                "characters": [
                    {
                        "name": c.name,
                        "japanese_name": c.japanese_name,
                        "gender": c.gender,
                        "role": c.role,
                        "archetype": c.archetype
                    }
                    for c in final_snapshot.characters
                ],
                "relationships": [
                    {
                        "pair": list(r.pair),
                        "type": r.relationship_type,
                        "state": r.state,
                        "pronoun_pair": r.pronoun_pair
                    }
                    for r in final_snapshot.relationships
                ],
                "glossary": [
                    {
                        "japanese": t.japanese,
                        "romanized": t.romanized,
                        "english": t.english,
                        "vietnamese": t.vietnamese,
                        "preserve": t.preserve
                    }
                    for t in final_snapshot.glossary
                ],
                "narrative_flags": final_snapshot.narrative_flags
            }
        }
        
        # Add all chapter snapshots for history
        for chapter_num in sorted(self.snapshots.keys()):
            snapshot = self.snapshots[chapter_num]
            pack_data["chapter_snapshots"].append({
                "chapter_id": snapshot.chapter_id,
                "chapter_num": snapshot.chapter_num,
                "generated_at": snapshot.generated_at,
                "reviewed_by_user": snapshot.reviewed_by_user,
                "user_corrections": snapshot.user_corrections,
                "discoveries": {
                    "characters": len(snapshot.characters),
                    "relationships": len(snapshot.relationships),
                    "glossary_terms": len(snapshot.glossary)
                }
            })
        
        with open(continuity_pack_path, 'w', encoding='utf-8') as f:
            json.dump(pack_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ Continuity pack saved: {continuity_pack_path}")
        logger.info(f"  Final state:")
        logger.info(f"    Characters: {len(final_snapshot.characters)}")
        logger.info(f"    Relationships: {len(final_snapshot.relationships)}")
        logger.info(f"    Glossary terms: {len(final_snapshot.glossary)}")
        logger.info(f"    Snapshots: {len(self.snapshots)}")
        
        # Clean up cache
        if self.current_cache_name and self.cache_manager:
            logger.info("\nCleaning up cache...")
            self.cache_manager.invalidate_cache(self.current_cache_name)
        
        logger.info("\n" + "="*60)
    
    def _load_manifest(self) -> Dict:
        """Load manifest.json."""
        if not self.manifest_path.exists():
            return {}
        
        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_manifest(self) -> None:
        """Save manifest.json."""
        with open(self.manifest_path, 'w', encoding='utf-8') as f:
            json.dump(self.manifest, f, indent=2, ensure_ascii=False)
    
    def _mark_snapshot_created(self, chapter_id: str) -> None:
        """Mark snapshot as created in manifest."""
        chapters = self.manifest.get('chapters', [])
        for chapter in chapters:
            if chapter.get('id') == chapter_id:
                chapter['snapshot_status'] = 'created'
                chapter['snapshot_timestamp'] = datetime.now().isoformat()
                break
        
        self._save_manifest()
    
    def _has_snapshot(self, chapter_id: str) -> bool:
        """Check if snapshot already exists for chapter."""
        # Check manifest flag
        chapters = self.manifest.get('chapters', [])
        for chapter in chapters:
            if chapter.get('id') == chapter_id:
                if chapter.get('snapshot_status') == 'created':
                    return True
        
        # Fallback: check if snapshot file exists
        snapshot_path = self.extractor.context_dir / f"snapshot_{chapter_id}.json"
        return snapshot_path.exists()
        logger.info("✓ Continuity pack finalized")
        logger.info("="*60 + "\n")
        
        return pack_data
