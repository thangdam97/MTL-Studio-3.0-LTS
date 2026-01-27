# Modular Publisher Profile System - Design Document

**Author:** Claude (Design Draft)
**Date:** 2026-01-21
**Status:** Draft for Review

---

## 1. Executive Summary

This document proposes refactoring the Librarian's pattern handling from **hardcoded Python constants** to a **runtime-loaded JSON database** with automatic mismatch detection and user-guided pattern learning.

### Current State
- Image patterns hardcoded in `image_extractor.py`
- Publisher detection hardcoded in `epub_extractor.py`
- JSON profiles exist but are **documentation-only** (not loaded at runtime)

### Proposed State
- Single unified `publisher_database.json` loaded at runtime
- Pattern matching driven by database, not code
- Unknown patterns trigger warnings + optional learning
- Backward-compatible API (no breaking changes to agent.py)

---

## 2. Goals & Non-Goals

### Goals
1. **Modularity** - Add new publishers without code changes
2. **Learning** - Detect and catalog unknown patterns with user confirmation
3. **Transparency** - Clear warnings when encountering mismatches
4. **Maintainability** - Single source of truth for all patterns
5. **Backward Compatibility** - Existing pipeline code unchanged

### Non-Goals
- Auto-accepting unknown patterns (too risky)
- Machine learning for pattern inference
- Breaking existing manifest.json structure
- Changing downstream agent interfaces

---

## 3. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     PUBLISHER PROFILE SYSTEM                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐    ┌──────────────────────────────────┐   │
│  │ publisher_db.json│───▶│      PublisherProfileManager     │   │
│  │ (confirmed)      │    │  ┌────────────────────────────┐  │   │
│  └──────────────────┘    │  │ - load_database()          │  │   │
│                          │  │ - get_publisher(name)      │  │   │
│  ┌──────────────────┐    │  │ - detect_publisher(opf)    │  │   │
│  │ unconfirmed.json │───▶│  │ - match_image(filename)    │  │   │
│  │ (pending review) │    │  │ - report_mismatch()        │  │   │
│  └──────────────────┘    │  │ - confirm_pattern()        │  │   │
│                          │  └────────────────────────────┘  │   │
│                          └──────────────────────────────────┘   │
│                                       │                          │
│                    ┌──────────────────┼──────────────────┐      │
│                    ▼                  ▼                  ▼      │
│           ┌─────────────┐    ┌─────────────┐    ┌───────────┐  │
│           │EPUBExtractor│    │ImageExtract.│    │ agent.py  │  │
│           │  (detect)   │    │ (classify)  │    │(orchestr.)│  │
│           └─────────────┘    └─────────────┘    └───────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Database Schema

### 4.1 Main Database: `publisher_database.json`

```json
{
  "$schema": "./publisher_schema.json",
  "version": "2.0",
  "last_updated": "2026-01-21T00:00:00Z",

  "publishers": {
    "KADOKAWA": {
      "canonical_name": "KADOKAWA",
      "aliases": [
        "KADOKAWA",
        "角川",
        "株式会社KADOKAWA",
        "KADOKAWA CORPORATION",
        "株式会社ＫＡＤＯＫＡＷＡ"
      ],
      "country": "JP",
      "confidence": "confirmed",

      "image_patterns": {
        "exclude": [
          {
            "pattern": "^gaiji[-_].*\\.(jpe?g|png)$",
            "flags": "i",
            "description": "Special character glyphs (not illustrations)"
          }
        ],
        "cover": [
          {
            "pattern": "^(i[-_])?cover\\.(jpe?g|png)$",
            "flags": "i",
            "priority": 1
          },
          {
            "pattern": "^allcover[-_]\\d+\\.jpe?g$",
            "flags": "i",
            "priority": 2
          }
        ],
        "kuchie": [
          {
            "pattern": "^kuchie[-_]\\d+\\.jpe?g$",
            "flags": "i",
            "priority": 1
          },
          {
            "pattern": "^k\\d{3}\\.jpe?g$",
            "flags": "i",
            "priority": 2
          },
          {
            "pattern": "^p00[1-9]\\.jpe?g$",
            "flags": "i",
            "priority": 3,
            "note": "p001-p009 reserved for kuchie"
          }
        ],
        "illustration": [
          {
            "pattern": "^i[-_]\\d+\\.jpe?g$",
            "flags": "i",
            "priority": 1
          },
          {
            "pattern": "^p0[1-9]\\d\\.jpe?g$",
            "flags": "i",
            "priority": 2,
            "note": "p010+ are illustrations"
          },
          {
            "pattern": "^p[1-9]\\d+\\.jpe?g$",
            "flags": "i",
            "priority": 3
          }
        ]
      },

      "content_patterns": {
        "filename": "\\d+\\.xhtml",
        "chapter_merging": false,
        "nav_structure": "li > a"
      },

      "metadata": {
        "spine_progression": "rtl",
        "typical_images": 23
      }
    },

    "Media Factory": {
      "canonical_name": "Media Factory",
      "aliases": [
        "Media Factory",
        "メディアファクトリー",
        "株式会社メディアファクトリー"
      ],
      "country": "JP",
      "confidence": "confirmed",

      "image_patterns": {
        "cover": [
          {
            "pattern": "^o_hyoushi\\.jpe?g$",
            "flags": "i",
            "priority": 1,
            "note": "hyoushi = 表紙 (cover)"
          },
          {
            "pattern": "^cover\\.jpe?g$",
            "flags": "i",
            "priority": 2
          }
        ],
        "kuchie": [
          {
            "pattern": "^o_kuchie_\\d+\\.jpe?g$",
            "flags": "i",
            "priority": 1
          }
        ],
        "illustration": [
          {
            "pattern": "^o_p\\d{3,}\\.jpe?g$",
            "flags": "i",
            "priority": 1
          }
        ]
      },

      "content_patterns": {
        "filename": "a_\\d+_\\d+\\.xhtml",
        "chapter_merging": true,
        "nav_structure": "li > span > a",
        "has_visual_toc": true
      }
    }
  },

  "fallback_patterns": {
    "description": "Generic patterns used when publisher is unknown",
    "image_patterns": {
      "exclude": [
        {"pattern": "^gaiji[-_].*\\.(jpe?g|png)$", "flags": "i"}
      ],
      "cover": [
        {"pattern": "^(o_|i[-_])?cover\\.(jpe?g|png)$", "flags": "i"},
        {"pattern": "^(o_)?hyoushi\\.(jpe?g|png)$", "flags": "i"},
        {"pattern": "^frontcover\\.(jpe?g|png)$", "flags": "i"}
      ],
      "kuchie": [
        {"pattern": "^(o_)?kuchie[-_]\\d+\\.jpe?g$", "flags": "i"},
        {"pattern": "^k\\d{3}\\.jpe?g$", "flags": "i"},
        {"pattern": "^p00[1-9](-\\d+)?\\.jpe?g$", "flags": "i"}
      ],
      "illustration": [
        {"pattern": "^(o_)?i[-_]\\d+\\.jpe?g$", "flags": "i"},
        {"pattern": "^(o_)?p0[1-9]\\d+\\.jpe?g$", "flags": "i"},
        {"pattern": "^m\\d{3}\\.jpe?g$", "flags": "i"}
      ]
    }
  }
}
```

### 4.2 Unconfirmed Patterns: `unconfirmed_patterns.json`

```json
{
  "version": "1.0",
  "patterns": [
    {
      "id": "unc_001",
      "detected_at": "2026-01-21T14:30:00Z",
      "source_epub": "新しい小説_v1.epub",
      "publisher_detected": "Unknown",
      "publisher_from_opf": "新興出版社",

      "unmatched_images": [
        {
          "filename": "illust_ch3.jpg",
          "suggested_type": "illustration",
          "reason": "Contains 'illust' keyword",
          "dimensions": [800, 1200]
        }
      ],

      "suggested_patterns": [
        {
          "type": "illustration",
          "pattern": "^illust_ch\\d+\\.jpe?g$",
          "based_on": ["illust_ch1.jpg", "illust_ch2.jpg", "illust_ch3.jpg"]
        }
      ],

      "status": "pending_review",
      "reviewed_by": null,
      "reviewed_at": null
    }
  ]
}
```

---

## 5. Core Components

### 5.1 `PublisherProfileManager` Class

```python
# publisher_profiles/manager.py

from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
import re
from datetime import datetime


@dataclass
class PatternMatch:
    """Result of pattern matching."""
    matched: bool
    image_type: Optional[str]  # cover, kuchie, illustration, exclude
    pattern_used: Optional[str]
    publisher: Optional[str]
    confidence: str  # confirmed, fallback, unmatched


@dataclass
class MismatchReport:
    """Report for unmatched files."""
    filename: str
    suggested_type: Optional[str]
    suggested_pattern: Optional[str]
    reason: str


class PublisherProfileManager:
    """
    Manages publisher profiles and pattern matching.

    Responsibilities:
    - Load/save publisher database
    - Detect publisher from OPF metadata
    - Match image filenames to types
    - Track and report mismatches
    - Support pattern confirmation workflow
    """

    def __init__(self, profiles_dir: Path = None):
        """
        Initialize manager.

        Args:
            profiles_dir: Directory containing JSON profiles.
                         Defaults to this module's directory.
        """
        self.profiles_dir = profiles_dir or Path(__file__).parent
        self.db_path = self.profiles_dir / "publisher_database.json"
        self.unconfirmed_path = self.profiles_dir / "unconfirmed_patterns.json"

        self._database: Dict = {}
        self._compiled_patterns: Dict[str, Dict[str, List[re.Pattern]]] = {}
        self._session_mismatches: List[MismatchReport] = []

        self.load_database()

    def load_database(self) -> None:
        """Load publisher database and compile patterns."""
        if self.db_path.exists():
            with open(self.db_path, 'r', encoding='utf-8') as f:
                self._database = json.load(f)
        else:
            # Create minimal database if none exists
            self._database = self._create_minimal_database()
            self.save_database()

        self._compile_all_patterns()

    def save_database(self) -> None:
        """Save publisher database to disk."""
        self._database["last_updated"] = datetime.now().isoformat()
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self._database, f, indent=2, ensure_ascii=False)

    def _compile_all_patterns(self) -> None:
        """Pre-compile regex patterns for performance."""
        self._compiled_patterns = {}

        # Compile publisher-specific patterns
        for pub_name, pub_data in self._database.get("publishers", {}).items():
            self._compiled_patterns[pub_name] = self._compile_publisher_patterns(
                pub_data.get("image_patterns", {})
            )

        # Compile fallback patterns
        fallback = self._database.get("fallback_patterns", {})
        self._compiled_patterns["__fallback__"] = self._compile_publisher_patterns(
            fallback.get("image_patterns", {})
        )

    def _compile_publisher_patterns(
        self,
        pattern_config: Dict
    ) -> Dict[str, List[re.Pattern]]:
        """Compile patterns for a single publisher."""
        compiled = {}

        for image_type in ["exclude", "cover", "kuchie", "illustration"]:
            compiled[image_type] = []
            for pattern_def in pattern_config.get(image_type, []):
                flags = 0
                if "i" in pattern_def.get("flags", ""):
                    flags |= re.IGNORECASE

                try:
                    compiled[image_type].append(
                        re.compile(pattern_def["pattern"], flags)
                    )
                except re.error as e:
                    print(f"[WARNING] Invalid pattern: {pattern_def['pattern']} - {e}")

        return compiled

    # =========================================================================
    # PUBLISHER DETECTION
    # =========================================================================

    def detect_publisher(self, opf_publisher_text: str) -> Tuple[str, str]:
        """
        Detect canonical publisher name from OPF metadata.

        Args:
            opf_publisher_text: Raw publisher text from dc:publisher

        Returns:
            Tuple of (canonical_name, confidence)
            confidence is 'confirmed' or 'unknown'
        """
        if not opf_publisher_text:
            return ("Unknown", "unknown")

        text_lower = opf_publisher_text.lower()

        for pub_name, pub_data in self._database.get("publishers", {}).items():
            for alias in pub_data.get("aliases", []):
                if alias.lower() in text_lower:
                    return (pub_name, "confirmed")

        # No match found - this is a potential new publisher
        self._report_unknown_publisher(opf_publisher_text)
        return (opf_publisher_text, "unknown")

    def _report_unknown_publisher(self, publisher_text: str) -> None:
        """Log unknown publisher for potential addition."""
        print(f"[WARNING] Unknown publisher: '{publisher_text}'")
        print(f"          Consider adding to publisher_database.json")

    # =========================================================================
    # IMAGE PATTERN MATCHING
    # =========================================================================

    def match_image(
        self,
        filename: str,
        publisher: str = None
    ) -> PatternMatch:
        """
        Match image filename to type using publisher patterns.

        Args:
            filename: Image filename (e.g., 'i-003.jpg')
            publisher: Publisher name (uses fallback if None/unknown)

        Returns:
            PatternMatch with classification result
        """
        # Get patterns to use
        if publisher and publisher in self._compiled_patterns:
            patterns = self._compiled_patterns[publisher]
            pattern_source = publisher
        else:
            patterns = self._compiled_patterns.get("__fallback__", {})
            pattern_source = "fallback"

        # Check exclusion first
        for pattern in patterns.get("exclude", []):
            if pattern.match(filename):
                return PatternMatch(
                    matched=True,
                    image_type="exclude",
                    pattern_used=pattern.pattern,
                    publisher=pattern_source,
                    confidence="confirmed"
                )

        # Check each type in priority order
        for image_type in ["cover", "kuchie", "illustration"]:
            for pattern in patterns.get(image_type, []):
                if pattern.match(filename):
                    return PatternMatch(
                        matched=True,
                        image_type=image_type,
                        pattern_used=pattern.pattern,
                        publisher=pattern_source,
                        confidence="confirmed" if pattern_source != "fallback" else "fallback"
                    )

        # No match - report mismatch
        self._track_mismatch(filename, publisher)

        return PatternMatch(
            matched=False,
            image_type=None,
            pattern_used=None,
            publisher=pattern_source,
            confidence="unmatched"
        )

    def _track_mismatch(self, filename: str, publisher: str) -> None:
        """Track unmatched filename for later review."""
        suggested = self._suggest_type(filename)

        report = MismatchReport(
            filename=filename,
            suggested_type=suggested[0],
            suggested_pattern=suggested[1],
            reason=suggested[2]
        )

        self._session_mismatches.append(report)

        print(f"[WARNING] Unmatched image: {filename}")
        if suggested[0]:
            print(f"          Suggested type: {suggested[0]} (pattern: {suggested[1]})")

    def _suggest_type(self, filename: str) -> Tuple[Optional[str], Optional[str], str]:
        """
        Suggest image type based on heuristics.

        Returns:
            Tuple of (suggested_type, suggested_pattern, reason)
        """
        lower = filename.lower()

        # Cover heuristics
        if "cover" in lower or "hyoushi" in lower:
            return ("cover", f"^.*cover.*$", "Contains 'cover' keyword")

        # Kuchie heuristics
        if "kuchie" in lower or lower.startswith("k0"):
            return ("kuchie", None, "Contains 'kuchie' or 'k0' prefix")

        # Illustration heuristics
        if "illust" in lower or lower.startswith("i-") or lower.startswith("i_"):
            base = filename.rsplit('.', 1)[0]
            pattern = f"^{re.escape(base[:-1])}\\d+\\.jpe?g$"
            return ("illustration", pattern, "Contains illustration indicator")

        # Generic numbered pattern
        if re.match(r'^[a-z]?\d+\.jpe?g$', lower, re.IGNORECASE):
            return ("illustration", None, "Numbered filename pattern")

        return (None, None, "No heuristic match")

    # =========================================================================
    # MISMATCH REPORTING & CONFIRMATION
    # =========================================================================

    def get_session_mismatches(self) -> List[MismatchReport]:
        """Get all mismatches from current session."""
        return self._session_mismatches

    def clear_session_mismatches(self) -> None:
        """Clear session mismatch tracking."""
        self._session_mismatches = []

    def save_unconfirmed_patterns(
        self,
        source_epub: str,
        publisher_text: str
    ) -> None:
        """
        Save session mismatches to unconfirmed patterns file.

        Args:
            source_epub: Name of source EPUB file
            publisher_text: Publisher text from OPF
        """
        if not self._session_mismatches:
            return

        # Load existing unconfirmed
        unconfirmed = {"version": "1.0", "patterns": []}
        if self.unconfirmed_path.exists():
            with open(self.unconfirmed_path, 'r', encoding='utf-8') as f:
                unconfirmed = json.load(f)

        # Generate new entry
        entry = {
            "id": f"unc_{len(unconfirmed['patterns']) + 1:03d}",
            "detected_at": datetime.now().isoformat(),
            "source_epub": source_epub,
            "publisher_from_opf": publisher_text,
            "unmatched_images": [
                {
                    "filename": m.filename,
                    "suggested_type": m.suggested_type,
                    "suggested_pattern": m.suggested_pattern,
                    "reason": m.reason
                }
                for m in self._session_mismatches
            ],
            "status": "pending_review"
        }

        unconfirmed["patterns"].append(entry)

        with open(self.unconfirmed_path, 'w', encoding='utf-8') as f:
            json.dump(unconfirmed, f, indent=2, ensure_ascii=False)

        print(f"[INFO] Saved {len(self._session_mismatches)} unconfirmed patterns")
        print(f"       Review: {self.unconfirmed_path}")

    def confirm_pattern(
        self,
        publisher: str,
        image_type: str,
        pattern: str,
        note: str = None
    ) -> bool:
        """
        Add a confirmed pattern to the database.

        Args:
            publisher: Publisher canonical name
            image_type: cover, kuchie, illustration, or exclude
            pattern: Regex pattern string
            note: Optional note about the pattern

        Returns:
            True if added successfully
        """
        if publisher not in self._database.get("publishers", {}):
            print(f"[ERROR] Unknown publisher: {publisher}")
            return False

        if image_type not in ["cover", "kuchie", "illustration", "exclude"]:
            print(f"[ERROR] Invalid image type: {image_type}")
            return False

        # Validate pattern compiles
        try:
            re.compile(pattern)
        except re.error as e:
            print(f"[ERROR] Invalid regex: {e}")
            return False

        # Add to database
        pub_patterns = self._database["publishers"][publisher].setdefault(
            "image_patterns", {}
        )
        type_patterns = pub_patterns.setdefault(image_type, [])

        new_pattern = {
            "pattern": pattern,
            "flags": "i",
            "priority": len(type_patterns) + 1
        }
        if note:
            new_pattern["note"] = note

        type_patterns.append(new_pattern)

        # Save and recompile
        self.save_database()
        self._compile_all_patterns()

        print(f"[OK] Added pattern to {publisher}/{image_type}: {pattern}")
        return True

    # =========================================================================
    # UTILITY
    # =========================================================================

    def get_publisher_info(self, publisher: str) -> Optional[Dict]:
        """Get full publisher configuration."""
        return self._database.get("publishers", {}).get(publisher)

    def list_publishers(self) -> List[str]:
        """List all known publishers."""
        return list(self._database.get("publishers", {}).keys())

    def _create_minimal_database(self) -> Dict:
        """Create minimal database structure."""
        return {
            "version": "2.0",
            "publishers": {},
            "fallback_patterns": {
                "image_patterns": {
                    "exclude": [],
                    "cover": [{"pattern": "^cover\\.(jpe?g|png)$", "flags": "i"}],
                    "kuchie": [],
                    "illustration": []
                }
            }
        }
```

---

## 6. Integration Points

### 6.1 Modified `ImageExtractor`

```python
# image_extractor.py (modified)

from .publisher_profiles.manager import PublisherProfileManager, PatternMatch

class ImageExtractor:
    """Extracts and catalogs images using publisher profiles."""

    def __init__(self, content_dir: Path, publisher: str = None):
        self.content_dir = Path(content_dir)
        self.image_dir = self._find_image_dir()
        self.publisher = publisher

        # Load profile manager
        self._profile_manager = PublisherProfileManager()

    def _classify_image(self, img_path: Path) -> Optional[ImageInfo]:
        """Classify image using profile manager."""
        filename = img_path.name

        match = self._profile_manager.match_image(filename, self.publisher)

        if not match.matched or match.image_type == "exclude":
            return None

        width, height = get_jpeg_dimensions(img_path)

        return ImageInfo(
            filename=filename,
            filepath=img_path,
            image_type=match.image_type,
            width=width,
            height=height,
            orientation=detect_orientation(img_path)
        )

    def get_mismatches(self) -> List:
        """Get any unmatched images from this session."""
        return self._profile_manager.get_session_mismatches()

    def save_mismatches(self, epub_name: str, publisher_text: str) -> None:
        """Save mismatches for later review."""
        self._profile_manager.save_unconfirmed_patterns(epub_name, publisher_text)
```

### 6.2 Modified `EPUBExtractor`

```python
# epub_extractor.py (modified)

from .publisher_profiles.manager import PublisherProfileManager

class EPUBExtractor:

    def __init__(self, work_base: Path = None):
        self.work_base = Path(work_base) if work_base else get_work_dir()
        self.work_base.mkdir(parents=True, exist_ok=True)

        # Load profile manager
        self._profile_manager = PublisherProfileManager()

    def _detect_publisher(self, opf_path: Path) -> Tuple[str, str]:
        """Detect publisher using profile manager."""
        publisher_text = self._extract_publisher_text(opf_path)
        return self._profile_manager.detect_publisher(publisher_text)

    def _extract_publisher_text(self, opf_path: Path) -> str:
        """Extract raw publisher text from OPF."""
        # ... existing XML parsing code ...
        pass
```

### 6.3 Modified `LibrarianAgent`

```python
# agent.py (modified excerpt)

class LibrarianAgent:

    def process_epub(self, epub_path: Path, ...) -> Manifest:
        # ... existing code ...

        # Step 5: Extract images (now with publisher context)
        image_extractor = ImageExtractor(
            extraction.content_dir,
            publisher=metadata.publisher  # Pass detected publisher
        )

        output_paths, filename_mapping = image_extractor.copy_to_assets(assets_dir)

        # Check for mismatches and warn user
        mismatches = image_extractor.get_mismatches()
        if mismatches:
            print(f"\n[WARNING] {len(mismatches)} images did not match known patterns:")
            for m in mismatches[:5]:  # Show first 5
                print(f"  - {m.filename}")
            if len(mismatches) > 5:
                print(f"  ... and {len(mismatches) - 5} more")

            # Save for later review
            image_extractor.save_mismatches(
                epub_path.name,
                metadata.raw_publisher_text
            )

        # ... rest of processing ...
```

---

## 7. Migration Strategy

### Phase 1: Create Unified Database (Non-Breaking)
1. Merge existing JSON profiles into `publisher_database.json`
2. Add fallback patterns (current hardcoded patterns)
3. Create `PublisherProfileManager` class
4. Add `unconfirmed_patterns.json` structure

### Phase 2: Wire Integration (Low Risk)
1. Modify `ImageExtractor` to use profile manager
2. Modify `EPUBExtractor` to use profile manager
3. Add mismatch tracking to `LibrarianAgent`
4. Keep hardcoded patterns as fallback during transition

### Phase 3: Remove Hardcoding (Final)
1. Remove `GAIJI_PATTERN`, `COVER_PATTERN`, etc. from `image_extractor.py`
2. Remove `publisher_map` from `epub_extractor.py`
3. All patterns now served from database
4. Delete individual `*.json` profile files (now consolidated)

### Phase 4: CLI Tooling (Enhancement)
1. Add `mtl profile list` - List known publishers
2. Add `mtl profile show <publisher>` - Show publisher patterns
3. Add `mtl profile review` - Interactive review of unconfirmed patterns
4. Add `mtl profile add <publisher> <type> <pattern>` - Add confirmed pattern

---

## 8. File Structure After Implementation

```
pipeline/librarian/publisher_profiles/
├── README.md                      # Documentation
├── DESIGN_MODULAR_PROFILES.md     # This document
├── manager.py                     # PublisherProfileManager class
├── publisher_database.json        # Main pattern database (runtime)
├── publisher_schema.json          # JSON Schema for validation
├── unconfirmed_patterns.json      # Pending patterns for review
└── validate_profiles.py           # Validation script
```

---

## 9. User Workflow

### Normal Operation (Known Publisher)
```
1. User runs: mtl phase1 INPUT/novel.epub
2. Librarian detects: Publisher = KADOKAWA (confirmed)
3. Images classified using KADOKAWA patterns
4. All images match → Processing continues normally
```

### Unknown Publisher
```
1. User runs: mtl phase1 INPUT/novel.epub
2. Librarian detects: Publisher = "新興出版社" (unknown)
3. [WARNING] Unknown publisher: '新興出版社'
4. Falls back to generic patterns
5. Some images don't match → Warnings shown
6. [WARNING] Unmatched image: custom_illust_01.jpg
7. Patterns saved to unconfirmed_patterns.json
8. Processing continues with available images
```

### Pattern Confirmation
```
1. User reviews unconfirmed_patterns.json
2. User runs: mtl profile add "新興出版社" illustration "^custom_illust_\\d+\\.jpe?g$"
3. Pattern added to database
4. Future EPUBs from this publisher work correctly
```

---

## 10. Testing Strategy

### Unit Tests
- Pattern compilation and matching
- Publisher detection from various alias formats
- Mismatch tracking and reporting
- Database save/load cycle

### Integration Tests
- Process EPUB with known publisher
- Process EPUB with unknown publisher
- Verify mismatch warnings appear
- Verify unconfirmed patterns saved

### Regression Tests
- All existing test EPUBs still process correctly
- Image classification results unchanged for known publishers
- No performance degradation

---

## 11. Open Questions

1. **Auto-suggest patterns?** Should the system auto-generate pattern suggestions based on multiple similar filenames?

2. **Pattern inheritance?** Should unknown publishers inherit from a "most similar" known publisher?

3. **Confidence scores?** Should pattern matches include confidence scores for QC reporting?

4. **Remote sync?** Should unconfirmed patterns be uploadable to a shared repository?

---

## 12. Appendix: Current Hardcoded Patterns

### From `image_extractor.py`
```python
GAIJI_PATTERN = re.compile(r'^gaiji[-_].*\.(jpe?g|png)$', re.IGNORECASE)
KUCHIE_PATTERN = re.compile(r'^(o_)?(?:kuchie[-_]\d+|k\d+|p00[1-9])(-\d+)?\.jpe?g$', re.IGNORECASE)
ILLUSTRATION_PATTERN = re.compile(r'^(o_)?(?:i[-_]\d+|img[-_]p\d+|p0[1-9]\d+|p[1-9]\d+|m\d+)\.jpe?g$', re.IGNORECASE)
COVER_PATTERN = re.compile(r'^(o_|i[-_])?(?:cover|hyoushi|hyousi|frontcover|front[-_]cover|h1)\.(jpe?g|png)$', re.IGNORECASE)
```

### From `epub_extractor.py`
```python
publisher_map = {
    'KADOKAWA': ['KADOKAWA', '角川', '株式会社KADOKAWA', 'KADOKAWA CORPORATION'],
    'Overlap': ['Overlap', 'オーバーラップ', '株式会社オーバーラップ'],
    'SB Creative': ['SB Creative', 'SBクリエイティブ', '株式会社SBクリエイティブ', 'SBCreative Corp.'],
    'Hifumi Shobo': ['Hifumi Shobo', '一二三書房', '株式会社一二三書房'],
    'Hobby Japan': ['Hobby Japan', 'ホビージャパン', '株式会社ホビージャパン'],
}
```

---

*End of Design Document*
