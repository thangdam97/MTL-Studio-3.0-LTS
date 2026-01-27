#!/usr/bin/env python3
"""
Schema Manipulator Agent
========================

A utility agent for creating and manipulating semantic metadata schemas
following the V3 enhanced structure with keigo_switch support.

Supported Operations:
- Create new character profiles with full keigo_switch
- Edit existing profiles
- Add/update localization notes
- Validate schema structure
- Sync manifest.json ↔ metadata_en.json
- Transform between schema variants

Usage:
  python schema_manipulator.py --volume <volume_id> --action <action> [options]

Actions:
  show              Show current schema structure
  add-character     Add a new character profile
  edit-character    Edit existing character profile
  add-keigo         Add keigo_switch to character
  validate          Validate schema compatibility
  sync              Sync manifest.json → metadata_en.json
  transform         Transform schema to target variant
  init              Initialize empty enhanced schema

Example:
  python schema_manipulator.py --volume 0019 --action show
  python schema_manipulator.py --volume 0019 --action add-character --name "Charlotte Bennett"
  python schema_manipulator.py --volume 0019 --action validate
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import copy

# Project paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
WORK_DIR = PROJECT_ROOT / "WORK"


class SchemaManipulator:
    """Agent for manipulating semantic metadata schemas."""
    
    # Schema templates
    CHARACTER_PROFILE_TEMPLATE = {
        "full_name": "",
        "nickname": "",
        "age": "",
        "pronouns": "they/them",
        "origin": "",
        "relationship_to_protagonist": "",
        "relationship_to_others": "",
        "personality_traits": "",
        "speech_pattern": "",
        "keigo_switch": {
            "narration": "casual",
            "internal_thoughts": "casual",
            "speaking_to": {},
            "emotional_shifts": {},
            "notes": ""
        },
        "key_traits": "",
        "appearance": "",
        "character_arc": ""
    }
    
    KEIGO_REGISTERS = [
        "very_formal",
        "formal_polite", 
        "polite_formal",
        "respectful_formal",
        "casual_respectful",
        "casual_gentle",
        "casual_bro",
        "casual",
        "very_casual",
        "casual_introspective",
        "warm_big_brother",
        "gentle_sisterly",
        "affectionate_childlike",
        "playful_childlike",
        "teasing_casual",
        "sharp_direct",
        "energetic_friendly"
    ]
    
    EMOTIONAL_SHIFTS = [
        "happy", "sad", "angry", "jealous", "embarrassed",
        "excited", "scared", "worried", "protective", "stubborn",
        "serious", "concerned", "caring"
    ]
    
    LOCALIZATION_TEMPLATE = {
        "british_speech_exception": {
            "character": "",
            "allowed_patterns": [],
            "rationale": "",
            "examples": []
        },
        "all_other_characters": {
            "priority": "SHORT, CONCISE, CONTEMPORARY GRAMMAR",
            "narrator_voice": "",
            "forbidden_patterns": [],
            "preferred_alternatives": {},
            "target_metrics": {
                "contraction_rate": ">95%",
                "ai_ism_density": "<0.3 per 1000 words",
                "sentence_length": "Short and punchy for dialogue",
                "vocabulary": "Contemporary American teen"
            }
        },
        "name_order": {
            "western_characters": {
                "order": "First name first (Western order)",
                "characters": [],
                "examples": []
            },
            "japanese_characters": {
                "order": "Family name first (Japanese order)",
                "characters": [],
                "examples": []
            }
        },
        "dialogue_guidelines": {},
        "volume_specific_notes": {}
    }

    def __init__(self, volume_id: str):
        self.volume_id = volume_id
        self.volume_path = self._resolve_volume_path(volume_id)
        self.manifest_path = self.volume_path / "manifest.json"
        self.metadata_path = self.volume_path / "metadata_en.json"
        self.manifest = None
        self.metadata_en = None
        
    def _resolve_volume_path(self, volume_id: str) -> Path:
        """Resolve volume path from partial ID."""
        # Try exact match first
        for path in WORK_DIR.iterdir():
            if path.is_dir():
                if path.name == volume_id:
                    return path
                # Partial match (last 4 chars)
                if path.name.endswith(volume_id):
                    return path
                # Contains match
                if volume_id in path.name:
                    return path
        raise ValueError(f"Volume not found: {volume_id}")
    
    def load(self) -> bool:
        """Load manifest and metadata files."""
        if not self.manifest_path.exists():
            print(f"❌ manifest.json not found at {self.manifest_path}")
            return False
            
        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            self.manifest = json.load(f)
            
        self.metadata_en = self.manifest.get('metadata_en', {})
        
        # Also load standalone metadata_en.json if exists
        if self.metadata_path.exists():
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                standalone = json.load(f)
                # Merge - manifest takes precedence
                for key in standalone:
                    if key not in self.metadata_en:
                        self.metadata_en[key] = standalone[key]
        
        return True
    
    def save(self) -> None:
        """Save changes to both manifest.json and metadata_en.json."""
        # Update manifest
        self.manifest['metadata_en'] = self.metadata_en
        
        with open(self.manifest_path, 'w', encoding='utf-8') as f:
            json.dump(self.manifest, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved manifest.json")
        
        # Sync to metadata_en.json
        with open(self.metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata_en, f, indent=2, ensure_ascii=False)
        print(f"✓ Synced metadata_en.json")
    
    def detect_schema_variant(self) -> str:
        """Detect which schema variant is in use."""
        if not self.metadata_en:
            return "empty"
        
        # Check schema_version field (Librarian-generated)
        schema_version = self.metadata_en.get('schema_version', '')
        if schema_version == 'v3_enhanced':
            return "v3_enhanced_librarian"
            
        # Check for Enhanced v2.1
        if 'characters' in self.metadata_en and isinstance(self.metadata_en.get('characters'), list):
            return "enhanced_v2.1"
            
        # Check for Legacy V2
        if 'character_profiles' in self.metadata_en or 'localization_notes' in self.metadata_en:
            return "legacy_v2"
            
        # Check for V4 Nested
        char_names = self.metadata_en.get('character_names', {})
        if char_names:
            first_value = next(iter(char_names.values()), None)
            if isinstance(first_value, dict):
                return "v4_nested"
            return "basic"
            
        return "minimal"
    
    def show_schema(self) -> None:
        """Display current schema structure."""
        variant = self.detect_schema_variant()
        
        print("=" * 60)
        print(f"SCHEMA ANALYSIS: {self.volume_id}")
        print("=" * 60)
        print(f"\nDetected Variant: {variant}")
        
        # Show schema note if present (Librarian-generated)
        schema_note = self.metadata_en.get('schema_note', '')
        if schema_note:
            print(f"Note: {schema_note}")
        
        print("-" * 40)
        
        if variant in ("legacy_v2", "v3_enhanced_librarian"):
            profiles = self.metadata_en.get('character_profiles', {})
            print(f"\n📋 Character Profiles: {len(profiles)} entries")
            for name, profile in profiles.items():
                has_keigo = 'keigo_switch' in profile
                keigo_status = "✓ keigo_switch" if has_keigo else "○ no keigo_switch"
                print(f"   • {name} [{keigo_status}]")
                if has_keigo:
                    ks = profile['keigo_switch']
                    print(f"     - narration: {ks.get('narration', 'n/a')}")
                    print(f"     - speaking_to: {len(ks.get('speaking_to', {}))} targets")
                    print(f"     - emotional_shifts: {len(ks.get('emotional_shifts', {}))} states")
            
            loc_notes = self.metadata_en.get('localization_notes', {})
            if loc_notes:
                print(f"\n📝 Localization Notes: Present")
                if 'british_speech_exception' in loc_notes:
                    exc = loc_notes['british_speech_exception']
                    print(f"   • British exception: {exc.get('character', 'N/A')}")
                if 'all_other_characters' in loc_notes:
                    other = loc_notes['all_other_characters']
                    print(f"   • Forbidden patterns: {len(other.get('forbidden_patterns', []))}")
                    print(f"   • Target contraction rate: {other.get('target_metrics', {}).get('contraction_rate', 'N/A')}")
        
        elif variant == "enhanced_v2.1":
            chars = self.metadata_en.get('characters', [])
            print(f"\n📋 Characters: {len(chars)} entries")
            for char in chars:
                print(f"   • {char.get('name_en', 'Unknown')} ({char.get('role', 'unknown')})")
            
            patterns = self.metadata_en.get('dialogue_patterns', {})
            print(f"\n🗣️ Dialogue Patterns: {len(patterns)} entries")
            
            guidelines = self.metadata_en.get('translation_guidelines', {})
            print(f"\n📐 Translation Guidelines: {'Present' if guidelines else 'Missing'}")
        
        elif variant == "v4_nested":
            char_names = self.metadata_en.get('character_names', {})
            print(f"\n📋 Character Names (Nested): {len(char_names)} entries")
            for jp, data in list(char_names.items())[:5]:
                print(f"   • {jp} → {data.get('name_en', 'Unknown')}")
            if len(char_names) > 5:
                print(f"   ... and {len(char_names) - 5} more")
        
        # Chapter info
        chapters = self.metadata_en.get('chapters', {})
        if chapters:
            print(f"\n📚 Chapter Metadata: {len(chapters)} entries")
            for ch_id, ch_data in chapters.items():
                title = ch_data.get('title_en', ['Unknown'])[0] if isinstance(ch_data.get('title_en'), list) else ch_data.get('title_en', 'Unknown')
                print(f"   • {ch_id}: {title}")
        
        print("\n" + "=" * 60)
    
    def add_character(self, name: str, **kwargs) -> Dict[str, Any]:
        """Add a new character profile with keigo_switch."""
        if 'character_profiles' not in self.metadata_en:
            self.metadata_en['character_profiles'] = {}
        
        profile = copy.deepcopy(self.CHARACTER_PROFILE_TEMPLATE)
        profile['full_name'] = name
        
        # Apply any provided kwargs
        for key, value in kwargs.items():
            if key in profile:
                profile[key] = value
        
        self.metadata_en['character_profiles'][name] = profile
        print(f"✓ Added character profile: {name}")
        return profile
    
    def edit_character(self, name: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Edit an existing character profile."""
        profiles = self.metadata_en.get('character_profiles', {})
        
        if name not in profiles:
            print(f"❌ Character not found: {name}")
            return None
        
        for key, value in kwargs.items():
            if key == 'keigo_switch' and isinstance(value, dict):
                # Merge keigo_switch
                if 'keigo_switch' not in profiles[name]:
                    profiles[name]['keigo_switch'] = {}
                profiles[name]['keigo_switch'].update(value)
            else:
                profiles[name][key] = value
        
        print(f"✓ Updated character profile: {name}")
        return profiles[name]
    
    def add_keigo_switch(self, character_name: str, 
                         narration: str = "casual",
                         internal_thoughts: str = "casual",
                         speaking_to: Optional[Dict[str, str]] = None,
                         emotional_shifts: Optional[Dict[str, str]] = None,
                         notes: str = "") -> bool:
        """Add or update keigo_switch for a character."""
        profiles = self.metadata_en.get('character_profiles', {})
        
        if character_name not in profiles:
            print(f"❌ Character not found: {character_name}")
            return False
        
        keigo = {
            "narration": narration,
            "internal_thoughts": internal_thoughts,
            "speaking_to": speaking_to or {},
            "emotional_shifts": emotional_shifts or {},
            "notes": notes
        }
        
        profiles[character_name]['keigo_switch'] = keigo
        print(f"✓ Added keigo_switch to: {character_name}")
        return True
    
    def add_speaking_target(self, character_name: str, target: str, register: str) -> bool:
        """Add a speaking target to character's keigo_switch."""
        profiles = self.metadata_en.get('character_profiles', {})
        
        if character_name not in profiles:
            print(f"❌ Character not found: {character_name}")
            return False
        
        if 'keigo_switch' not in profiles[character_name]:
            profiles[character_name]['keigo_switch'] = copy.deepcopy(
                self.CHARACTER_PROFILE_TEMPLATE['keigo_switch']
            )
        
        profiles[character_name]['keigo_switch']['speaking_to'][target] = register
        print(f"✓ {character_name} → {target}: {register}")
        return True
    
    def add_emotional_shift(self, character_name: str, emotion: str, register: str) -> bool:
        """Add an emotional shift to character's keigo_switch."""
        profiles = self.metadata_en.get('character_profiles', {})
        
        if character_name not in profiles:
            print(f"❌ Character not found: {character_name}")
            return False
        
        if 'keigo_switch' not in profiles[character_name]:
            profiles[character_name]['keigo_switch'] = copy.deepcopy(
                self.CHARACTER_PROFILE_TEMPLATE['keigo_switch']
            )
        
        profiles[character_name]['keigo_switch']['emotional_shifts'][emotion] = register
        print(f"✓ {character_name} [{emotion}]: {register}")
        return True
    
    def init_localization_notes(self, narrator_name: str = "Protagonist",
                                 narrator_voice: str = "Contemporary American teen") -> Dict[str, Any]:
        """Initialize localization notes structure."""
        loc = copy.deepcopy(self.LOCALIZATION_TEMPLATE)
        loc['all_other_characters']['narrator_voice'] = f"{narrator_name} - {narrator_voice}"
        
        self.metadata_en['localization_notes'] = loc
        print(f"✓ Initialized localization_notes")
        return loc
    
    def add_british_exception(self, character: str, 
                              patterns: List[str],
                              rationale: str = "",
                              examples: Optional[List[str]] = None) -> None:
        """Add British speech exception for a character."""
        if 'localization_notes' not in self.metadata_en:
            self.init_localization_notes()
        
        self.metadata_en['localization_notes']['british_speech_exception'] = {
            "character": f"{character} ONLY",
            "allowed_patterns": patterns,
            "rationale": rationale or f"{character} is British - formal patterns are authentic character voice",
            "examples": examples or []
        }
        print(f"✓ Added British exception for: {character}")
    
    def add_forbidden_pattern(self, pattern: str, alternative: str = "") -> None:
        """Add a forbidden pattern to localization notes."""
        if 'localization_notes' not in self.metadata_en:
            self.init_localization_notes()
        
        loc = self.metadata_en['localization_notes']
        if 'all_other_characters' not in loc:
            loc['all_other_characters'] = {"forbidden_patterns": [], "preferred_alternatives": {}}
        
        if pattern not in loc['all_other_characters'].get('forbidden_patterns', []):
            loc['all_other_characters'].setdefault('forbidden_patterns', []).append(pattern)
        
        if alternative:
            loc['all_other_characters'].setdefault('preferred_alternatives', {})[pattern] = alternative
        
        print(f"✓ Forbidden: '{pattern}' → '{alternative or 'avoid'}'")
    
    def validate_schema(self) -> Dict[str, Any]:
        """Validate schema structure and return report."""
        report = {
            "valid": True,
            "variant": self.detect_schema_variant(),
            "issues": [],
            "warnings": [],
            "stats": {}
        }
        
        variant = report["variant"]
        
        if variant == "empty":
            report["issues"].append("No metadata_en found")
            report["valid"] = False
            return report
        
        if variant in ("legacy_v2", "v3_enhanced_librarian"):
            profiles = self.metadata_en.get('character_profiles', {})
            report["stats"]["character_profiles"] = len(profiles)
            
            # Check keigo_switch coverage
            with_keigo = sum(1 for p in profiles.values() if 'keigo_switch' in p)
            report["stats"]["keigo_switch_coverage"] = f"{with_keigo}/{len(profiles)}"
            
            if with_keigo < len(profiles):
                report["warnings"].append(
                    f"Only {with_keigo}/{len(profiles)} characters have keigo_switch"
                )
            
            # Check for required fields
            for name, profile in profiles.items():
                if not profile.get('speech_pattern'):
                    report["warnings"].append(f"{name}: missing speech_pattern")
                if 'keigo_switch' in profile:
                    ks = profile['keigo_switch']
                    if not ks.get('speaking_to'):
                        report["warnings"].append(f"{name}: keigo_switch has no speaking_to targets")
            
            # Check localization notes
            loc = self.metadata_en.get('localization_notes', {})
            report["stats"]["localization_notes"] = "present" if loc else "missing"
            
            if not loc:
                report["warnings"].append("No localization_notes found")
            else:
                if not loc.get('british_speech_exception'):
                    report["warnings"].append("No british_speech_exception defined")
                if not loc.get('all_other_characters', {}).get('forbidden_patterns'):
                    report["warnings"].append("No forbidden_patterns defined")
            
            # Check for unfilled placeholders (Librarian-generated)
            if variant == "v3_enhanced_librarian":
                unfilled_profiles = []
                for name, profile in profiles.items():
                    if "[TO BE FILLED" in str(profile):
                        unfilled_profiles.append(name)
                if unfilled_profiles:
                    report["warnings"].append(
                        f"Unfilled placeholders in profiles: {unfilled_profiles[:3]}{'...' if len(unfilled_profiles) > 3 else ''}"
                    )
                
                # Check chapter title_en placeholders
                chapters_meta = self.metadata_en.get('chapters', {})
                unfilled_titles = [cid for cid, cdata in chapters_meta.items() 
                                   if "[TO BE FILLED" in str(cdata.get('title_en', []))]
                if unfilled_titles:
                    report["warnings"].append(
                        f"Chapter titles need translation: {len(unfilled_titles)} chapters"
                    )
        
        # Check chapter metadata
        chapters = self.metadata_en.get('chapters', {})
        manifest_chapters = self.manifest.get('chapters', [])
        report["stats"]["chapter_metadata"] = len(chapters)
        report["stats"]["manifest_chapters"] = len(manifest_chapters)
        
        if len(chapters) < len(manifest_chapters):
            report["warnings"].append(
                f"Chapter metadata incomplete: {len(chapters)}/{len(manifest_chapters)}"
            )
        
        # Check title_en in manifest chapters
        missing_titles = [ch['id'] for ch in manifest_chapters if not ch.get('title_en')]
        if missing_titles:
            report["warnings"].append(f"Chapters missing title_en: {missing_titles}")
        
        return report
    
    def print_validation_report(self, report: Dict[str, Any]) -> None:
        """Print formatted validation report."""
        print("=" * 60)
        print("SCHEMA VALIDATION REPORT")
        print("=" * 60)
        print(f"\nVariant: {report['variant']}")
        print(f"Status: {'✓ VALID' if report['valid'] else '✗ INVALID'}")
        
        print("\n📊 Statistics:")
        for key, value in report['stats'].items():
            print(f"   {key}: {value}")
        
        if report['issues']:
            print(f"\n❌ Issues ({len(report['issues'])}):")
            for issue in report['issues']:
                print(f"   • {issue}")
        
        if report['warnings']:
            print(f"\n⚠️ Warnings ({len(report['warnings'])}):")
            for warning in report['warnings']:
                print(f"   • {warning}")
        
        if not report['issues'] and not report['warnings']:
            print("\n✓ No issues found!")
        
        print("\n" + "=" * 60)
    
    def sync_metadata(self) -> None:
        """Sync manifest.json metadata_en to standalone file."""
        with open(self.metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata_en, f, indent=2, ensure_ascii=False)
        print(f"✓ Synced to {self.metadata_path}")
    
    def init_enhanced_schema(self) -> None:
        """Initialize a new enhanced V2 schema structure."""
        self.metadata_en['character_profiles'] = {}
        self.metadata_en['localization_notes'] = copy.deepcopy(self.LOCALIZATION_TEMPLATE)
        self.metadata_en['chapters'] = {}
        
        print("✓ Initialized enhanced schema structure")
        print("  Next steps:")
        print("  1. Add characters: --action add-character --name 'Name'")
        print("  2. Add keigo_switch to each character")
        print("  3. Configure localization_notes")
        print("  4. Add chapter metadata")
    
    def apply_keigo_template(self, template: Dict[str, Dict[str, Any]]) -> int:
        """Apply keigo_switch from a template dict. Returns count of applied."""
        profiles = self.metadata_en.get('character_profiles', {})
        applied = 0
        
        for char_name, keigo_data in template.items():
            if char_name in profiles:
                profiles[char_name]['keigo_switch'] = keigo_data
                print(f"✓ Applied keigo_switch to: {char_name}")
                applied += 1
            else:
                print(f"⚠️ Character not found: {char_name}")
        
        return applied
    
    def generate_keigo_template(self) -> Dict[str, Dict[str, Any]]:
        """Generate a template file with empty keigo_switch for all characters."""
        profiles = self.metadata_en.get('character_profiles', {})
        template = {}
        
        for name, profile in profiles.items():
            template[name] = {
                "narration": "casual",
                "internal_thoughts": "casual",
                "speaking_to": {},
                "emotional_shifts": {},
                "notes": f"Auto-generated for {name}"
            }
        
        return template


def apply_keigo_presets(manipulator: SchemaManipulator) -> None:
    """Apply keigo_switch presets based on character archetypes."""
    profiles = manipulator.metadata_en.get('character_profiles', {})
    
    print("\n" + "=" * 60)
    print("BULK KEIGO_SWITCH APPLICATION")
    print("=" * 60)
    
    # Define character archetypes with default keigo patterns
    archetypes = {
        "british_formal": {
            "narration": "formal_polite",
            "internal_thoughts": "formal_polite",
            "notes": "British character - maintains formal register in all contexts"
        },
        "japanese_protagonist": {
            "narration": "casual_introspective", 
            "internal_thoughts": "very_casual",
            "notes": "Japanese protagonist - casual internal voice, adapts to conversation partner"
        },
        "child": {
            "narration": "playful_childlike",
            "internal_thoughts": "playful_childlike", 
            "notes": "Child character - maintains childlike speech regardless of context"
        },
        "best_friend": {
            "narration": "casual_bro",
            "internal_thoughts": "casual_bro",
            "notes": "Best friend character - casual speech with direct serious mode when needed"
        },
        "teacher_mentor": {
            "narration": "teasing_casual",
            "internal_thoughts": "sharp_direct",
            "notes": "Teacher/mentor figure - casual with serious protective mode"
        },
        "neutral": {
            "narration": "casual",
            "internal_thoughts": "casual",
            "notes": "Default neutral register"
        }
    }
    
    print("\nAvailable archetypes:")
    for i, (name, preset) in enumerate(archetypes.items(), 1):
        print(f"  {i}. {name}: {preset['notes']}")
    
    print(f"\nCharacters without keigo_switch ({len([p for p in profiles.values() if 'keigo_switch' not in p])}):")
    
    for name, profile in profiles.items():
        if 'keigo_switch' in profile:
            print(f"  ✓ {name} (already has keigo_switch)")
            continue
        
        print(f"\n  {name}")
        print(f"    Origin: {profile.get('origin', 'Unknown')}")
        print(f"    Speech: {profile.get('speech_pattern', 'N/A')[:50]}...")
        
        choice = input(f"    Archetype (1-{len(archetypes)}, s=skip, q=quit): ").strip().lower()
        
        if choice == 'q':
            break
        if choice == 's':
            continue
        
        try:
            idx = int(choice) - 1
            archetype_name = list(archetypes.keys())[idx]
            preset = archetypes[archetype_name]
            
            manipulator.add_keigo_switch(
                name,
                narration=preset['narration'],
                internal_thoughts=preset['internal_thoughts'],
                notes=preset['notes']
            )
            
            # Ask for speaking_to targets
            add_targets = input("    Add speaking targets? (y/N): ").strip().lower()
            if add_targets == 'y':
                other_chars = [n for n in profiles.keys() if n != name]
                print(f"    Available: {', '.join(other_chars[:5])}...")
                while True:
                    target = input("      Target (empty=done): ").strip()
                    if not target:
                        break
                    register = input(f"      Register for {target}: ").strip()
                    if register:
                        manipulator.add_speaking_target(name, target, register)
        
        except (ValueError, IndexError):
            print("    Invalid choice, skipping")
    
    manipulator.save()
    print("\n✓ Bulk keigo_switch application complete")


def interactive_add_character(manipulator: SchemaManipulator) -> None:
    """Interactive character addition wizard."""
    print("\n" + "=" * 60)
    print("ADD CHARACTER WIZARD")
    print("=" * 60)
    
    name = input("\nCharacter name (full name): ").strip()
    if not name:
        print("❌ Name required")
        return
    
    nickname = input("Nickname (optional): ").strip()
    age = input("Age (e.g., '16-17 (high school)'): ").strip()
    pronouns = input("Pronouns (default: they/them): ").strip() or "they/them"
    origin = input("Origin (e.g., 'Japanese', 'British'): ").strip()
    
    print("\nRelationship to protagonist:")
    rel_protag = input("  ").strip()
    
    print("\nPersonality traits (comma-separated):")
    traits = input("  ").strip()
    
    print("\nSpeech pattern description:")
    speech = input("  ").strip()
    
    # Create profile
    profile = manipulator.add_character(
        name,
        nickname=nickname,
        age=age,
        pronouns=pronouns,
        origin=origin,
        relationship_to_protagonist=rel_protag,
        personality_traits=traits,
        speech_pattern=speech
    )
    
    # Ask about keigo_switch
    add_keigo = input("\nAdd keigo_switch now? (Y/n): ").strip().lower()
    if add_keigo != 'n':
        interactive_add_keigo(manipulator, name)
    
    manipulator.save()


def interactive_add_keigo(manipulator: SchemaManipulator, character_name: str) -> None:
    """Interactive keigo_switch addition."""
    print(f"\n--- KEIGO_SWITCH for {character_name} ---")
    
    print("\nAvailable registers:")
    for i, reg in enumerate(manipulator.KEIGO_REGISTERS[:10], 1):
        print(f"  {i}. {reg}")
    print("  (or type custom)")
    
    narration = input("\nNarration register: ").strip() or "casual"
    internal = input("Internal thoughts register: ").strip() or "casual"
    
    speaking_to = {}
    print("\nAdd speaking targets (empty name to finish):")
    while True:
        target = input("  Target name: ").strip()
        if not target:
            break
        register = input(f"  Register for {target}: ").strip()
        if register:
            speaking_to[target] = register
    
    emotional_shifts = {}
    print("\nAdd emotional shifts (empty emotion to finish):")
    print(f"  Emotions: {', '.join(manipulator.EMOTIONAL_SHIFTS[:8])}...")
    while True:
        emotion = input("  Emotion: ").strip()
        if not emotion:
            break
        register = input(f"  Register when {emotion}: ").strip()
        if register:
            emotional_shifts[emotion] = register
    
    notes = input("\nNotes (optional): ").strip()
    
    manipulator.add_keigo_switch(
        character_name,
        narration=narration,
        internal_thoughts=internal,
        speaking_to=speaking_to,
        emotional_shifts=emotional_shifts,
        notes=notes
    )


def main():
    parser = argparse.ArgumentParser(
        description="Schema Manipulator Agent - Manage semantic metadata schemas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show current schema
  python schema_manipulator.py --volume 0019 --action show
  
  # Validate schema
  python schema_manipulator.py --volume 0019 --action validate
  
  # Add character interactively
  python schema_manipulator.py --volume 0019 --action add-character
  
  # Sync metadata
  python schema_manipulator.py --volume 0019 --action sync
  
  # Initialize new schema
  python schema_manipulator.py --volume 0019 --action init
        """
    )
    
    parser.add_argument('--volume', '-v', required=True, help='Volume ID (full or partial)')
    parser.add_argument('--action', '-a', required=True, 
                        choices=['show', 'add-character', 'edit-character', 'add-keigo',
                                 'validate', 'sync', 'init', 'bulk-keigo', 'export', 'import',
                                 'apply-keigo', 'generate-keigo'],
                        help='Action to perform')
    parser.add_argument('--name', '-n', help='Character name (for add/edit)')
    parser.add_argument('--json', '-j', help='JSON file with data to import/apply')
    parser.add_argument('--output', '-o', help='Output file for export')
    
    args = parser.parse_args()
    
    try:
        manipulator = SchemaManipulator(args.volume)
        
        if not manipulator.load():
            sys.exit(1)
        
        if args.action == 'show':
            manipulator.show_schema()
        
        elif args.action == 'validate':
            report = manipulator.validate_schema()
            manipulator.print_validation_report(report)
            sys.exit(0 if report['valid'] and not report['warnings'] else 1)
        
        elif args.action == 'sync':
            manipulator.sync_metadata()
        
        elif args.action == 'init':
            manipulator.init_enhanced_schema()
            manipulator.save()
        
        elif args.action == 'add-character':
            if args.name:
                manipulator.add_character(args.name)
                manipulator.save()
            else:
                interactive_add_character(manipulator)
        
        elif args.action == 'add-keigo':
            if not args.name:
                print("❌ --name required for add-keigo")
                sys.exit(1)
            interactive_add_keigo(manipulator, args.name)
            manipulator.save()
        
        elif args.action == 'edit-character':
            if not args.name:
                print("❌ --name required for edit-character")
                sys.exit(1)
            # For now, just show the character
            profiles = manipulator.metadata_en.get('character_profiles', {})
            if args.name in profiles:
                print(json.dumps(profiles[args.name], indent=2, ensure_ascii=False))
            else:
                print(f"❌ Character not found: {args.name}")
        
        elif args.action == 'bulk-keigo':
            apply_keigo_presets(manipulator)
        
        elif args.action == 'export':
            output_file = args.output or f"metadata_export_{args.volume}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(manipulator.metadata_en, f, indent=2, ensure_ascii=False)
            print(f"✓ Exported to: {output_file}")
        
        elif args.action == 'import':
            if not args.json:
                print("❌ --json required for import action")
                sys.exit(1)
            with open(args.json, 'r', encoding='utf-8') as f:
                imported = json.load(f)
            # Merge imported data
            for key, value in imported.items():
                if key == 'character_profiles':
                    manipulator.metadata_en.setdefault('character_profiles', {}).update(value)
                elif key == 'localization_notes':
                    manipulator.metadata_en.setdefault('localization_notes', {}).update(value)
                else:
                    manipulator.metadata_en[key] = value
            manipulator.save()
            print(f"✓ Imported from: {args.json}")
        
        elif args.action == 'apply-keigo':
            if not args.json:
                # Default to V3 template
                template_path = SCRIPT_DIR / "templates" / "keigo_v3_template.json"
                if template_path.exists():
                    print(f"Using default template: {template_path}")
                else:
                    print("❌ --json required (no default template found)")
                    sys.exit(1)
            else:
                template_path = Path(args.json)
            
            with open(template_path, 'r', encoding='utf-8') as f:
                template = json.load(f)
            
            applied = manipulator.apply_keigo_template(template)
            manipulator.save()
            print(f"\n✓ Applied keigo_switch to {applied} characters")
        
        elif args.action == 'generate-keigo':
            template = manipulator.generate_keigo_template()
            output_file = args.output or f"keigo_template_{args.volume}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2, ensure_ascii=False)
            print(f"✓ Generated keigo template: {output_file}")
            print("  Edit this file and use --action apply-keigo --json <file> to apply")
    
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nAborted.")
        sys.exit(0)


if __name__ == "__main__":
    main()
