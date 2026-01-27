"""
Schema Review Interface - Interactive CLI for User Review
Presents extracted schema and allows user corrections before caching.
"""

import json
import logging
import readline  # Enable delete key, arrow keys, and input history
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import asdict

from pipeline.translator.schema_extractor import (
    ChapterSnapshot, Character, Relationship, GlossaryTerm
)

logger = logging.getLogger(__name__)


class SchemaReviewInterface:
    """Interactive CLI for reviewing extracted schemas."""
    
    def __init__(self):
        self.colors = {
            'header': '\033[95m',
            'blue': '\033[94m',
            'cyan': '\033[96m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'red': '\033[91m',
            'bold': '\033[1m',
            'underline': '\033[4m',
            'end': '\033[0m'
        }
    
    def colorize(self, text: str, color: str) -> str:
        """Add color to text if terminal supports it."""
        return f"{self.colors.get(color, '')}{text}{self.colors['end']}"
    
    def show_review(
        self,
        snapshot: ChapterSnapshot,
        previous_snapshot: Optional[ChapterSnapshot] = None,
        delta: Optional[Dict] = None
    ) -> Tuple[str, ChapterSnapshot]:
        """
        Show schema review interface.
        
        Returns:
            (action, updated_snapshot) where action is:
            - 'approve': User approved schema as-is
            - 'corrected': User made corrections
            - 're-extract': Re-run extraction
            - 'cancel': Cancel and stop pipeline
        """
        print("\n" + "="*60)
        print(self.colorize(f"  SCHEMA REVIEW: {snapshot.chapter_id.upper()}", 'bold'))
        print("="*60 + "\n")
        
        # Show what was extracted
        if previous_snapshot:
            self._show_delta(snapshot, previous_snapshot, delta)
        else:
            self._show_full_schema(snapshot)
        
        # Show action menu
        print("\n" + "="*60)
        print("Actions:")
        print("  [A] Approve - Save and continue to next chapter")
        print("  [E] Edit - Make corrections to detected schema")
        print("  [R] Re-extract - Run extraction again")
        print("  [V] View Full - See complete schema details")
        print("  [C] Cancel - Stop pipeline")
        print("="*60 + "\n")
        
        # Get user choice
        while True:
            choice = input("Your choice: ").strip().upper()
            
            if choice == 'A':
                snapshot.reviewed_by_user = True
                return 'approve', snapshot
            
            elif choice == 'E':
                updated_snapshot = self._edit_schema(snapshot)
                updated_snapshot.reviewed_by_user = True
                updated_snapshot.user_corrections += 1
                return 'corrected', updated_snapshot
            
            elif choice == 'R':
                return 're-extract', snapshot
            
            elif choice == 'V':
                self._show_full_schema(snapshot)
                print("\nPress Enter to return to menu...")
                input()
                continue
            
            elif choice == 'C':
                confirm = input("Are you sure you want to cancel? (y/N): ").strip().lower()
                if confirm == 'y':
                    return 'cancel', snapshot
                continue
            
            else:
                print("Invalid choice. Please enter A, E, R, V, or C.")
    
    def _show_delta(
        self,
        current: ChapterSnapshot,
        previous: ChapterSnapshot,
        delta: Optional[Dict]
    ):
        """Show changes from previous chapter."""
        if not delta:
            return
        
        # New characters
        if delta['new_characters']:
            print(self.colorize("┌─ NEW CHARACTERS ─────────────────────────────────────┐", 'cyan'))
            for char in delta['new_characters']:
                print(f"│                                                       │")
                print(f"│  • {self.colorize(char.name, 'bold')}")
                print(f"│    Gender: {char.gender or 'unknown'} (confidence: {char.confidence:.2f})")
                print(f"│    Role: {char.role or 'unknown'}")
                if char.archetype:
                    print(f"│    Archetype: {char.archetype}")
            print("└───────────────────────────────────────────────────────┘\n")
        
        # Changed relationships
        if delta['changed_relationships']:
            print(self.colorize("┌─ RELATIONSHIP CHANGES ───────────────────────────────┐", 'yellow'))
            for change in delta['changed_relationships']:
                if change['type'] == 'new':
                    rel = change['relationship']
                    print(f"│                                                       │")
                    print(f"│  NEW: {rel.pair[0]} ↔ {rel.pair[1]}")
                    print(f"│    Type: {rel.relationship_type}")
                    print(f"│    Dynamics: {rel.dynamics}")
                    if rel.pronoun_pair:
                        print(f"│    VN Pair: {rel.pronoun_pair}")
                elif change['type'] == 'changed':
                    old = change['from']
                    new = change['to']
                    print(f"│                                                       │")
                    print(f"│  CHANGED: {new.pair[0]} ↔ {new.pair[1]}")
                    print(f"│    WAS: {old.state} (intimacy: {old.intimacy})")
                    print(f"│    NOW: {new.state} (intimacy: {new.intimacy})")
                    if old.pronoun_pair != new.pronoun_pair:
                        print(f"│    Pronoun: {old.pronoun_pair} → {new.pronoun_pair}")
            print("└───────────────────────────────────────────────────────┘\n")
        
        # New glossary terms
        if delta['new_terms']:
            print(self.colorize("┌─ NEW GLOSSARY TERMS ─────────────────────────────────┐", 'green'))
            for term in delta['new_terms']:
                print(f"│                                                       │")
                print(f"│  {term.romanized or term.japanese}")
                if term.english:
                    print(f"│    EN: {term.english}")
                if term.vietnamese:
                    print(f"│    VN: {term.vietnamese}")
                if term.preserve:
                    print(f"│    {self.colorize('⚠ PRESERVE (do not translate)', 'yellow')}")
            print("└───────────────────────────────────────────────────────┘\n")
        
        # New narrative flags
        if delta['new_flags']:
            print(self.colorize("┌─ NEW NARRATIVE FLAGS ────────────────────────────────┐", 'blue'))
            for flag in delta['new_flags']:
                print(f"│  • {flag}")
            print("└───────────────────────────────────────────────────────┘\n")
    
    def _show_full_schema(self, snapshot: ChapterSnapshot):
        """Show complete schema details."""
        print("\n" + self.colorize("FULL SCHEMA", 'bold'))
        print("─" * 60)
        
        # Characters
        print(f"\n{self.colorize('CHARACTERS', 'cyan')} ({len(snapshot.characters)}):")
        for i, char in enumerate(snapshot.characters, 1):
            print(f"  {i}. {char.name}")
            print(f"     Gender: {char.gender or 'unknown'}")
            print(f"     Role: {char.role or 'unknown'}")
            if char.japanese_name:
                print(f"     Japanese: {char.japanese_name}")
            print(f"     Confidence: {char.confidence:.2f}")
            print()
        
        # Relationships
        print(f"{self.colorize('RELATIONSHIPS', 'yellow')} ({len(snapshot.relationships)}):")
        for i, rel in enumerate(snapshot.relationships, 1):
            print(f"  {i}. {rel.pair[0]} ↔ {rel.pair[1]}")
            print(f"     Type: {rel.relationship_type}")
            print(f"     Stability: {rel.stability}")
            if rel.pronoun_pair:
                print(f"     VN Pair: {rel.pronoun_pair}")
            print()
        
        # Glossary
        print(f"{self.colorize('GLOSSARY', 'green')} ({len(snapshot.glossary)}):")
        for i, term in enumerate(snapshot.glossary, 1):
            print(f"  {i}. {term.romanized or term.japanese}")
            if term.english:
                print(f"     EN: {term.english}")
            if term.vietnamese:
                print(f"     VN: {term.vietnamese}")
            print()
        
        # Narrative flags
        print(f"{self.colorize('NARRATIVE FLAGS', 'blue')} ({len(snapshot.narrative_flags)}):")
        for flag in snapshot.narrative_flags:
            print(f"  • {flag}")
        print()
    
    def _edit_schema(self, snapshot: ChapterSnapshot) -> ChapterSnapshot:
        """Interactive editor for schema corrections."""
        print("\n" + "="*60)
        print(self.colorize("  SCHEMA EDITOR", 'bold'))
        print("="*60 + "\n")
        
        print("What would you like to edit?")
        print("  [1] Character genders")
        print("  [2] Character roles")
        print("  [3] Relationship types")
        print("  [4] Add/remove characters")
        print("  [5] Add/remove relationships")
        print("  [0] Done editing")
        print()
        
        while True:
            choice = input("Edit option: ").strip()
            
            if choice == '0':
                break
            
            elif choice == '1':
                self._edit_character_genders(snapshot)
            
            elif choice == '2':
                self._edit_character_roles(snapshot)
            
            elif choice == '3':
                self._edit_relationships(snapshot)
            
            elif choice == '4':
                self._edit_character_list(snapshot)
            
            elif choice == '5':
                self._edit_relationship_list(snapshot)
            
            else:
                print("Invalid option.")
        
        return snapshot
    
    def _edit_character_genders(self, snapshot: ChapterSnapshot):
        """Edit character genders."""
        print("\n" + self.colorize("Edit Character Genders", 'cyan'))
        print("─" * 60)
        
        for i, char in enumerate(snapshot.characters, 1):
            print(f"{i}. {char.name}: {char.gender or 'unknown'}")
        
        print("\nEnter character number to edit (0 to cancel):")
        try:
            choice = int(input().strip())
            if choice == 0:
                return
            
            if 1 <= choice <= len(snapshot.characters):
                char = snapshot.characters[choice - 1]
                print(f"\nCurrent gender: {char.gender or 'unknown'}")
                print("New gender (male/female/unknown):")
                new_gender = input().strip().lower()
                
                if new_gender in ['male', 'female', 'unknown']:
                    char.gender = new_gender
                    print(f"✓ Updated {char.name} gender to: {new_gender}")
                else:
                    print("Invalid gender. Not updated.")
        except ValueError:
            print("Invalid input.")
    
    def _edit_character_roles(self, snapshot: ChapterSnapshot):
        """Edit character roles."""
        print("\n" + self.colorize("Edit Character Roles", 'cyan'))
        print("─" * 60)
        
        for i, char in enumerate(snapshot.characters, 1):
            print(f"{i}. {char.name}: {char.role or 'unknown'}")
        
        print("\nEnter character number to edit (0 to cancel):")
        try:
            choice = int(input().strip())
            if choice == 0:
                return
            
            if 1 <= choice <= len(snapshot.characters):
                char = snapshot.characters[choice - 1]
                print(f"\nCurrent role: {char.role or 'unknown'}")
                print("Roles: protagonist, romantic_lead, friend, mentor, supporting")
                print("New role:")
                new_role = input().strip().lower()
                
                char.role = new_role
                print(f"✓ Updated {char.name} role to: {new_role}")
        except ValueError:
            print("Invalid input.")
    
    def _edit_relationships(self, snapshot: ChapterSnapshot):
        """Edit relationship types."""
        print("\n" + self.colorize("Edit Relationships", 'yellow'))
        print("─" * 60)
        
        for i, rel in enumerate(snapshot.relationships, 1):
            print(f"{i}. {rel.pair[0]} ↔ {rel.pair[1]}: {rel.relationship_type}")
        
        print("\nEnter relationship number to edit (0 to cancel):")
        try:
            choice = int(input().strip())
            if choice == 0:
                return
            
            if 1 <= choice <= len(snapshot.relationships):
                rel = snapshot.relationships[choice - 1]
                print(f"\nCurrent type: {rel.relationship_type}")
                print("Types: romance_arc, peer_friendship, family, mentor, acquaintance")
                print("New type:")
                new_type = input().strip().lower().replace(' ', '_')
                
                rel.relationship_type = new_type
                print(f"✓ Updated relationship to: {new_type}")
        except ValueError:
            print("Invalid input.")
    
    def _edit_character_list(self, snapshot: ChapterSnapshot):
        """Add or remove characters."""
        print("\n" + self.colorize("Add/Remove Characters", 'cyan'))
        print("─" * 60)
        print("[A] Add character")
        print("[R] Remove character")
        print("[0] Cancel")
        
        choice = input().strip().upper()
        
        if choice == 'A':
            print("\nCharacter name:")
            name = input().strip()
            if name:
                char = Character(name=name, gender='unknown', role='supporting', confidence=1.0)
                snapshot.characters.append(char)
                print(f"✓ Added character: {name}")
        
        elif choice == 'R':
            for i, char in enumerate(snapshot.characters, 1):
                print(f"{i}. {char.name}")
            print("\nEnter character number to remove:")
            try:
                idx = int(input().strip()) - 1
                if 0 <= idx < len(snapshot.characters):
                    removed = snapshot.characters.pop(idx)
                    print(f"✓ Removed character: {removed.name}")
            except ValueError:
                print("Invalid input.")
    
    def _edit_relationship_list(self, snapshot: ChapterSnapshot):
        """Add or remove relationships."""
        print("\n" + self.colorize("Add/Remove Relationships", 'yellow'))
        print("─" * 60)
        print("[A] Add relationship")
        print("[R] Remove relationship")
        print("[0] Cancel")
        
        choice = input().strip().upper()
        
        if choice == 'A':
            print("\nAvailable characters:")
            for i, char in enumerate(snapshot.characters, 1):
                print(f"{i}. {char.name}")
            
            print("\nFirst character number:")
            try:
                idx1 = int(input().strip()) - 1
                print("Second character number:")
                idx2 = int(input().strip()) - 1
                
                if 0 <= idx1 < len(snapshot.characters) and 0 <= idx2 < len(snapshot.characters):
                    char1 = snapshot.characters[idx1].name
                    char2 = snapshot.characters[idx2].name
                    
                    rel = Relationship(
                        pair=(char1, char2),
                        relationship_type='acquaintance',
                        dynamics='unknown',
                        stability='flat',
                        confidence=1.0
                    )
                    snapshot.relationships.append(rel)
                    print(f"✓ Added relationship: {char1} ↔ {char2}")
            except ValueError:
                print("Invalid input.")
        
        elif choice == 'R':
            for i, rel in enumerate(snapshot.relationships, 1):
                print(f"{i}. {rel.pair[0]} ↔ {rel.pair[1]}")
            print("\nEnter relationship number to remove:")
            try:
                idx = int(input().strip()) - 1
                if 0 <= idx < len(snapshot.relationships):
                    removed = snapshot.relationships.pop(idx)
                    print(f"✓ Removed relationship: {removed.pair[0]} ↔ {removed.pair[1]}")
            except ValueError:
                print("Invalid input.")


def quick_approve_prompt() -> bool:
    """Quick yes/no approval prompt."""
    while True:
        response = input("Approve schema? (Y/n): ").strip().lower()
        if response in ['', 'y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        print("Please enter Y or N.")
