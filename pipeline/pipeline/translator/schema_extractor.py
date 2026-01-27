"""
Schema Extractor - Per-Chapter Continuity Schema Generation
Extracts characters, relationships, glossary, and narrative flags from translations.
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

from pipeline.common.gemini_client import GeminiClient
from pipeline.translator.config import get_model_name

logger = logging.getLogger(__name__)


@dataclass
class Character:
    """Character information extracted from chapter."""
    name: str
    japanese_name: Optional[str] = None
    gender: Optional[str] = None  # "male", "female", "unknown"
    role: Optional[str] = None  # "protagonist", "romantic_lead", "friend", "supporting"
    archetype: Optional[str] = None
    age: Optional[int] = None
    grade: Optional[str] = None
    confidence: float = 0.0  # Detection confidence score


@dataclass
class Relationship:
    """Relationship between two characters."""
    pair: Tuple[str, str]
    relationship_type: str  # "romance_arc", "peer_friendship", "family", etc.
    dynamics: str
    stability: str  # "flat", "evolving", "binary_trigger"
    intimacy: float = 0.0  # RTAS score for VN
    state: str = "unknown"
    pronoun_pair: Optional[str] = None  # For VN: "anh/em", "tớ/cậu", etc.
    confidence: float = 0.0


@dataclass
class GlossaryTerm:
    """Cultural or specialized term."""
    japanese: str
    romanized: Optional[str] = None
    english: Optional[str] = None
    vietnamese: Optional[str] = None
    cultural_context: Optional[str] = None
    preserve: bool = False  # Whether to preserve original


@dataclass
class ChapterSnapshot:
    """Schema snapshot after processing a chapter."""
    chapter_id: str
    chapter_num: int
    generated_at: str
    reviewed_by_user: bool = False
    user_corrections: int = 0
    characters: List[Character] = None
    relationships: List[Relationship] = None
    glossary: List[GlossaryTerm] = None
    narrative_flags: List[str] = None
    
    def __post_init__(self):
        if self.characters is None:
            self.characters = []
        if self.relationships is None:
            self.relationships = []
        if self.glossary is None:
            self.glossary = []
        if self.narrative_flags is None:
            self.narrative_flags = []


class SchemaExtractor:
    """Extract continuity schema from translated chapters."""
    
    # Vietnamese common words that should NOT be treated as character names
    VN_COMMON_WORDS = {
        # Pronouns
        'Anh', 'Chị', 'Em', 'Tôi', 'Mình', 'Bạn', 'Cậu', 'Tớ',
        'Ông', 'Bà', 'Cô', 'Chú', 'Dì', 'Bác',
        # Common sentence starters
        'Nhưng', 'Nếu', 'Khi', 'Vì', 'Để', 'Thế', 'Đó', 'Này',
        'Và', 'Hay', 'Hoặc', 'Còn', 'Với', 'Từ', 'Cho', 'Của',
        # Common words
        'Không', 'Có', 'Là', 'Được', 'Thì', 'Đã', 'Sẽ', 'Đang',
        'Rồi', 'Vẫn', 'Cũng', 'Đều', 'Vậy', 'Thôi', 'Nhé', 'Nào',
        # Question words
        'Gì', 'Ai', 'Đâu', 'Sao', 'Thế', 'Nào', 'Bao', 'Như',
    }
    
    def __init__(self, work_dir: Path, target_language: str = "EN"):
        self.work_dir = work_dir
        self.target_language = target_language.upper()
        self.context_dir = work_dir / ".context"
        self.context_dir.mkdir(exist_ok=True)
        
        # Initialize Gemini client for semantic extraction
        # Use gemini-2.5-flash for fast schema extraction (Phase 1.5 optimization)
        self.gemini_client = GeminiClient(model="gemini-2.5-flash", enable_caching=False)
        
        # Load manifest for volume metadata
        manifest_path = work_dir / "manifest.json"
        self.manifest = {}
        if manifest_path.exists():
            with open(manifest_path, 'r', encoding='utf-8') as f:
                self.manifest = json.load(f)
    
    def _load_character_names_from_manifest(self) -> List[str]:
        """Load character names from manifest's language-specific metadata."""
        if not self.manifest:
            return []
        
        # Try language-specific metadata first
        metadata_key = f'metadata_{self.target_language.lower()}'
        metadata = self.manifest.get(metadata_key, {})
        
        # Fallback to metadata_en if target language metadata not found
        if not metadata:
            metadata = self.manifest.get('metadata_en', {})
        
        character_names = metadata.get('character_names', {})
        
        # Return the translated names (values of the dictionary)
        return list(character_names.values())
    
    def _extract_schema_with_gemini(
        self,
        text: str,
        previous_snapshot: Optional[ChapterSnapshot]
    ) -> Dict[str, any]:
        """
        Use Gemini to semantically extract schema from translated text.
        
        Returns:
            Dictionary with characters, relationships, glossary, narrative_flags
        """
        # Build extraction prompt
        lang_name = "Vietnamese" if self.target_language == 'VN' else "English"
        
        prompt = f"""Extract the following information from this {lang_name} light novel chapter translation.

**CONTEXT**: This is a Japanese light novel (romance/school/slice-of-life genre). Pay close attention to character interactions, emotional dynamics, and story progression.

1. **CHARACTER NAMES**: List all character names that appear in this chapter.
   
   **CRITICAL - JAPANESE NAMING CONVENTIONS**:
   - Japanese names: "Family Given" order (e.g., "Shirasu Yuika" NOT "Yuika Shirasu")
   - **FULL NAME ESTABLISHES IDENTITY**: When a full name is mentioned (e.g., "Shirasu Yuika"), subsequent mentions of EITHER part refer to the SAME person
   - People are addressed by SURNAME in formal settings, GIVEN NAME in intimate settings
   - **CONSOLIDATION RULE**: If text contains "Shirasu Yuika" as full name, then ALL later mentions of "Shirasu" OR "Yuika" refer to this ONE person
   
   **STEP-BY-STEP NAME EXTRACTION**:
   1. **SCAN FOR FULL NAMES FIRST**: Find all full names explicitly stated in the chapter
      - Look for patterns: "Name is [Family Given]", "called [Family Given]", "[Family Given] appeared"
      - Example: "tên là Shirasu Yuika" → Full name is "Shirasu Yuika"
   
   2. **MAP PARTIAL NAMES TO FULL NAMES**: After finding full names, match partial mentions
      - If "Shirasu Yuika" is established, then:
        * Every "Shirasu said/did/thought" → refers to Shirasu Yuika
        * Every "Yuika smiled/replied/blushed" → refers to Shirasu Yuika
        * DO NOT create separate "Shirasu" and "Yuika" characters!
   
   3. **VERIFY WITH DIALOGUE CONTEXT**: Use how characters address each other as confirmation
      - Formal: "Shirasu-san" (classmates) → surname usage
      - Intimate: "Yuika" (lovers/close friends) → given name usage
      - Both patterns for same character = name switch indicating relationship change
   
   **NAME ASSEMBLY OUTPUT**:
   - ALWAYS output FULL NAME in character list (e.g., "Shirasu Yuika")
   - NEVER output partial names as separate characters
   - If only partial name appears and cannot be linked to full name, mark as "[Surname] (full name unknown)"
   
   **FIRST-PERSON NARRATION DETECTION**:
   - If the story uses first-person POV (I/me/my), the narrator IS the protagonist
   - Look for self-introduction patterns: "I—[Name]—", "My name is [Name]", "I'm called [Name]"
   - In Vietnamese: "Tôi—[Name]—", "Tên tôi là [Name]"
   - In English: "I—[Name]—", "My name is [Name]"
   - **If first-person narrator exists but hasn't introduced themselves yet**, use "unknown" as protagonist name placeholder
   
   - For each character, provide: name, gender (if identifiable), role (protagonist/love_interest/friend/supporting)
   - Skip pronouns (anh, chị, em, etc.) and common words
   - Skip single letters or abbreviations unless clearly character names

2. **RELATIONSHIPS**: Analyze character interactions carefully and classify relationship types.
   
   **RELATIONSHIP TYPES** (choose the most accurate):
   - **romance**: Romantic interest, attraction, dating, love confession context, blushing, jealousy, special attention
   - **friendship**: Friends, classmates with friendly bond, mutual support, casual interactions
   - **family**: Siblings, parents, relatives
   - **rivalry**: Competition, antagonism, conflicting goals
   - **mentor_student**: Teacher-student, senpai-kouhai with guidance dynamic
   - **acquaintance**: Just met, minimal interaction, neutral relationship
   
   **DETECTION SIGNALS**:
   - Romance: Physical proximity, blushing, jealousy, special treatment, intimate conversations, emotional reactions
   - Friendship: Casual banter, mutual teasing, shared activities, comfortable interaction
   - Rivalry: Tension, competition, confrontation, opposing views
   - Mentor: Advice-giving, teaching, looking up to someone, respect dynamics
   
   - Use the SAME FULL NAMES from the characters list
   - Only list relationships that are CLEARLY evident in this chapter's interactions
   - If two characters appear but don't interact, DON'T create a relationship entry

3. **GLOSSARY TERMS**: List any Japanese cultural terms, honorifics, or specialized vocabulary that appears.
   - Include: senpai, kouhai, sensei, -san, -kun, -chan, -sama, keigo forms
   - Include: Japanese food, cultural concepts, school terms
   - Format: Japanese term → {lang_name} translation/explanation (if different from original)

4. **NARRATIVE FLAGS**: Identify significant plot developments, emotional beats, and story milestones.
   
   **LOOK FOR** (based on patterns from Japanese romcom light novels):
   
   **Relationship milestones**:
   - first_meeting, saved_by_protagonist, life_debt_acknowledged
   - confession, feelings_realized, mutual_attraction_confirmed
   - first_date, first_kiss, holding_hands, intimate_moment
   - relationship_begins, breakup, reconciliation
   - cohabitation_starts, domestic_routine_established
   - meets_family, relationship_public, wedding_discussion
   
   **Emotional moments**:
   - jealousy_shown, possessive_behavior, love_rival_appears
   - crying_scene, emotional_breakdown, comforted_by_protagonist
   - heartfelt_conversation, opens_up_about_past, vulnerability_shown
   - blushing_moment, embarrassed_reaction, flustered_behavior
   - misunderstanding_occurs, misunderstanding_resolved
   
   **Daily life & intimacy** (romcom staples):
   - cooking_together, shared_meal, breakfast_prepared
   - bath_scene, wardrobe_malfunction, accidental_touch
   - sleepover, falls_asleep_together, morning_after
   - nurse_care, takes_care_when_sick
   - study_session, tutoring_scene
   
   **Social dynamics**:
   - alone_together, private_moment, intimate_setting
   - interrupted_moment, caught_by_others, witnessed_intimacy
   - public_affection, hand_holding_in_public
   - rumors_spread, classmates_gossip, relationship_questioned
   - love_triangle, rival_confrontation
   
   **Plot developments**:
   - secret_revealed, past_trauma_shared, hidden_identity_exposed
   - promise_made, vow_exchanged, commitment_shown
   - decision_made, turning_point, character_takes_action
   - conflict_arises, argument, tension_escalates
   - problem_solved, conflict_resolved, reconciliation
   
   **Character growth**:
   - realization, epiphany, understands_feelings
   - character_opens_up, overcomes_fear, gains_confidence
   - confronts_past, faces_weakness, personal_growth
   
   **Setting/Events** (common in school romcoms):
   - school_festival, cultural_festival, sports_day
   - summer_vacation, beach_trip, hot_springs
   - winter_holiday, christmas_eve, new_years
   - rainy_day, typhoon_day, snow_day
   - sick_day, absent_from_school
   - after_school_alone, weekend_meetup
   
   **CRITERIA**: Only flag events that are NARRATIVELY SIGNIFICANT (not routine daily activities)
   - ✓ YES: "She confessed her feelings" → confession
   - ✓ YES: "She moved in and started cooking for him" → cohabitation_starts, cooking_together
   - ✓ YES: "He saved her from a dangerous situation" → saved_by_protagonist
   - ✓ YES: "They were caught by classmates holding hands" → public_affection, witnessed_intimacy
   - ✗ NO: "They walked to school" → (too routine, skip)
   - ✗ NO: "They ate lunch" → (routine unless emotionally significant context)

Return the results in this exact JSON format:
```json
{{
  "characters": [
    {{"name": "Full Name", "gender": "male/female/unknown", "role": "protagonist/love_interest/friend/supporting"}}
  ],
  "relationships": [
    {{"char1": "Full Name A", "char2": "Full Name B", "type": "romance/friendship/family/rivalry/mentor_student/acquaintance"}}
  ],
  "glossary": [
    {{"japanese": "senpai", "translation": "{lang_name} equivalent or explanation"}}
  ],
  "narrative_flags": ["flag1", "flag2"]
}}
```

Chapter text:
{text[:8000]}"""  # Limit to ~8K chars to avoid token limits
        
        try:
            logger.info("Calling Gemini Flash for semantic schema extraction...")
            response = self.gemini_client.generate(
                prompt,
                temperature=0.3,  # Lower temperature for more deterministic extraction
                max_output_tokens=2000
            )
            
            # Extract text content from GeminiResponse
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Parse JSON from response
            # Try to extract JSON from markdown code blocks
            json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON directly
                json_match = re.search(r'{.*}', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    raise ValueError("No JSON found in Gemini response")
            
            schema_data = json.loads(json_str)
            logger.info("✓ Gemini extracted schema successfully")
            return schema_data
            
        except Exception as e:
            logger.warning(f"Gemini extraction failed: {e}. Falling back to regex method.")
            return None
    
    def extract_from_chapter(
        self,
        chapter_num: int,
        chapter_id: str,
        translation_text: str,
        previous_snapshot: Optional[ChapterSnapshot] = None
    ) -> ChapterSnapshot:
        """
        Extract schema from translated chapter.
        
        Args:
            chapter_num: Chapter number (1-indexed)
            chapter_id: Chapter identifier (e.g., "chapter_01")
            translation_text: Translated chapter content
            previous_snapshot: Previous chapter's snapshot for delta detection
            
        Returns:
            ChapterSnapshot with extracted schema
        """
        logger.info(f"Extracting schema from {chapter_id}...")
        
        # TRY METHOD 1: Gemini-powered semantic extraction (preferred)
        gemini_schema = self._extract_schema_with_gemini(translation_text, previous_snapshot)
        
        if gemini_schema:
            # Parse Gemini results into our dataclasses
            characters = [
                Character(
                    name=c.get('name', ''),
                    gender=c.get('gender', 'unknown'),
                    role=c.get('role', 'supporting'),
                    confidence=0.9  # High confidence from LLM
                )
                for c in gemini_schema.get('characters', [])
            ]
            
            # CRITICAL: Post-process to consolidate partial names
            characters = self._consolidate_partial_names(characters, translation_text)
            
            relationships = [
                Relationship(
                    pair=(r.get('char1', ''), r.get('char2', '')),
                    relationship_type=r.get('type', 'unknown'),
                    dynamics='',
                    stability='flat',
                    confidence=0.85
                )
                for r in gemini_schema.get('relationships', [])
            ]
            
            glossary = [
                GlossaryTerm(
                    japanese=g.get('japanese', ''),
                    romanized=g.get('romanized'),
                    vietnamese=g.get('translation') if self.target_language == 'VN' else None,
                    english=g.get('translation') if self.target_language == 'EN' else None
                )
                for g in gemini_schema.get('glossary', [])
            ]
            
            narrative_flags = gemini_schema.get('narrative_flags', [])
            
            logger.info(f"✓ Gemini extracted: {len(characters)} characters, {len(relationships)} relationships")
        else:
            # FALLBACK METHOD 2: Regex-based extraction
            logger.info("Using fallback regex extraction...")
            characters = self._detect_characters(translation_text, previous_snapshot)
            relationships = self._detect_relationships(characters, translation_text, previous_snapshot)
            glossary = self._extract_glossary_terms(translation_text, previous_snapshot)
            narrative_flags = self._extract_narrative_flags(translation_text, chapter_num)
        
        snapshot = ChapterSnapshot(
            chapter_id=chapter_id,
            chapter_num=chapter_num,
            generated_at=datetime.now().isoformat(),
            characters=characters,
            relationships=relationships,
            glossary=glossary,
            narrative_flags=narrative_flags
        )
        
        logger.info(f"✓ Extracted: {len(characters)} characters, {len(relationships)} relationships, {len(glossary)} terms")
        
        return snapshot
    
    def _detect_characters(
        self,
        text: str,
        previous_snapshot: Optional[ChapterSnapshot]
    ) -> List[Character]:
        """Detect character names and infer basic information."""
        characters = []
        
        # Get previous characters if available
        previous_chars = {}
        if previous_snapshot:
            previous_chars = {c.name: c for c in previous_snapshot.characters}
        
        # STRATEGY 1: Load character names from manifest (already translated and validated)
        manifest_names = self._load_character_names_from_manifest()
        
        # Count occurrences of known names in text
        name_counts = {}
        for name in manifest_names:
            # Count how many times this name appears in the text
            count = len(re.findall(re.escape(name), text, re.IGNORECASE))
            if count > 0:
                name_counts[name] = count
        
        # STRATEGY 2: Regex-based detection for additional names (fallback)
        if self.target_language == 'VN':
            # Vietnamese: Look for proper names (usually 2-3 words, all capitalized)
            # Pattern: Multiple capitalized words that appear together consistently
            name_pattern = r'\b([A-ZĐÂĂÊÔƠƯ][a-zđâăêôơư]+(?:\s+[A-ZĐÂĂÊÔƠƯ][a-zđâăêôơư]+){1,2})\b'
        else:
            # English: Look for capitalized names not at sentence start
            name_pattern = r'(?<=[.!?]\s)([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)'
        
        potential_names = re.findall(name_pattern, text)
        
        # Count occurrences and filter
        for name in potential_names:
            # Skip if already in manifest names
            if name in manifest_names:
                continue
                
            # Filter out Vietnamese common words
            if self.target_language == 'VN':
                # Check if any word in the name is a common word
                words = name.split()
                if any(word in self.VN_COMMON_WORDS for word in words):
                    continue
                # Skip single-word "names" that are too short (likely pronouns)
                if len(words) == 1 and len(name) <= 3:
                    continue
            
            name_counts[name] = name_counts.get(name, 0) + 1
        
        # Consider names that appear 2+ times
        threshold = 2
        significant_names = {name for name, count in name_counts.items() if count >= threshold}
        
        for name in significant_names:
            # Skip if already in previous snapshot
            if name in previous_chars:
                characters.append(previous_chars[name])
                continue
            
            # Infer gender from pronouns used
            gender = self._infer_gender(name, text)
            
            # Infer role from context
            role = self._infer_role(name, text, len(characters))
            
            char = Character(
                name=name,
                gender=gender,
                role=role,
                confidence=min(name_counts[name] / 10.0, 1.0)  # More mentions = higher confidence
            )
            characters.append(char)
        
        return characters
    
    def _infer_gender(self, name: str, text: str) -> str:
        """Infer character gender from pronoun usage."""
        # Look for pronouns near the name
        name_contexts = []
        for match in re.finditer(re.escape(name), text):
            start = max(0, match.start() - 100)
            end = min(len(text), match.end() + 100)
            name_contexts.append(text[start:end].lower())
        
        context = " ".join(name_contexts)
        
        # Count gendered pronouns
        male_pronouns = len(re.findall(r'\b(he|him|his)\b', context))
        female_pronouns = len(re.findall(r'\b(she|her|hers)\b', context))
        
        if male_pronouns > female_pronouns * 2:
            return "male"
        elif female_pronouns > male_pronouns * 2:
            return "female"
        else:
            return "unknown"
    
    def _infer_role(self, name: str, text: str, char_count: int) -> str:
        """Infer character role from context and position."""
        # First character is often protagonist
        if char_count == 0:
            return "protagonist"
        
        # Look for role indicators in context
        name_contexts = []
        for match in re.finditer(re.escape(name), text):
            start = max(0, match.start() - 200)
            end = min(len(text), match.end() + 200)
            name_contexts.append(text[start:end].lower())
        
        context = " ".join(name_contexts)
        
        # Role keywords
        if any(word in context for word in ['friend', 'buddy', 'classmate']):
            return "friend"
        elif any(word in context for word in ['love', 'romantic', 'feelings', 'blush']):
            return "romantic_lead"
        elif any(word in context for word in ['teacher', 'sensei', 'master']):
            return "mentor"
        
        return "supporting"
    
    def _consolidate_partial_names(self, characters: List[Character], text: str) -> List[Character]:
        """
        Post-process character list to consolidate partial names into full names.
        
        Example: If we have "Shirasu" and "Yuika" as separate characters,
        and text contains "Shirasu Yuika", merge them into one "Shirasu Yuika" character.
        """
        logger.info(f"\n🔍 CONSOLIDATION DEBUG: Starting with {len(characters)} characters")
        for i, char in enumerate(characters):
            logger.info(f"  [{i+1}] {char.name} (role={char.role}, conf={char.confidence:.2f})")
        
        if len(characters) <= 1:
            logger.info("  ↳ Only 1 character, skipping consolidation")
            return characters
        
        # Step 1: Find all full names (2-word Japanese names) in the character list
        full_names = []
        partial_names = []
        
        for char in characters:
            name_parts = char.name.split()
            if len(name_parts) == 2:
                # This is a full name (Family Given)
                full_names.append(char)
                logger.info(f"  ✓ Full name found: {char.name}")
            elif len(name_parts) == 1:
                # This might be a partial name
                partial_names.append(char)
                logger.info(f"  ⚠ Partial name found: {char.name}")
            else:
                # Keep as-is (3+ words, non-Japanese, etc.)
                full_names.append(char)
                logger.info(f"  ↳ Keeping as-is: {char.name}")
        
        # Step 2: Try to match partial names to full names
        consolidated = list(full_names)  # Start with full names
        unmatched_partials = []
        
        logger.info(f"\n🔍 CONSOLIDATION: Trying to match {len(partial_names)} partials to {len(full_names)} full names")
        
        for partial in partial_names:
            partial_word = partial.name
            matched = False
            
            logger.info(f"\n  Checking partial: '{partial_word}'")
            
            # Check if this partial matches any full name
            for full_char in full_names:
                full_parts = full_char.name.split()
                if len(full_parts) == 2:
                    surname, given = full_parts
                    
                    logger.info(f"    vs full name '{full_char.name}' (surname='{surname}', given='{given}')")
                    
                    # Check if partial matches either surname or given name
                    if partial_word == surname or partial_word == given:
                        logger.info(f"    ✓ MATCH! Merging '{partial_word}' into '{full_char.name}'")
                        # Merge: Use the role/gender from the more confident source
                        if partial.confidence > full_char.confidence:
                            full_char.role = partial.role
                            full_char.gender = partial.gender
                        # Boost confidence
                        full_char.confidence = min(full_char.confidence + 0.1, 1.0)
                        matched = True
                        logger.info(f"✓ Consolidated '{partial_word}' into '{full_char.name}'")
                        break
            
            if not matched:
                logger.info(f"    ⚠ No match in full names, searching text...")
                # Check if we can find the full name in the text
                # Look for patterns like "Partial1 Partial2" where Partial2 is this partial name
                found_full_name = None
                
                # Try to find "[Word] [partial_word]" pattern in text
                pattern1 = rf'\b([A-ZĐÂĂÊÔƠƯ][a-zđâăêôơư]+)\s+{re.escape(partial_word)}\b'
                match1 = re.search(pattern1, text)
                if match1:
                    found_full_name = f"{match1.group(1)} {partial_word}"
                
                # Try to find "[partial_word] [Word]" pattern in text
                pattern2 = rf'\b{re.escape(partial_word)}\s+([A-ZĐÂĂÊÔƠƯ][a-zđâăêôơư]+)\b'
                match2 = re.search(pattern2, text)
                if match2:
                    found_full_name = f"{partial_word} {match2.group(1)}"
                
                if found_full_name:
                    # Create new full name character
                    partial.name = found_full_name
                    consolidated.append(partial)
                    logger.info(f"✓ Expanded '{partial_word}' to '{found_full_name}' from text")
                else:
                    # Keep partial name as-is
                    unmatched_partials.append(partial)
        
        # Add unmatched partials
        consolidated.extend(unmatched_partials)
        
        # Step 3: Remove duplicates (same name appearing twice)
        seen_names = set()
        final_characters = []
        
        logger.info(f"\n🔍 CONSOLIDATION RESULT: {len(characters)} → {len(consolidated)} characters (before dedup)")
        
        for char in consolidated:
            if char.name not in seen_names:
                seen_names.add(char.name)
                final_characters.append(char)
            else:
                logger.info(f"✓ Removed duplicate character: {char.name}")
        
        logger.info(f"  Final after dedup: {len(final_characters)} characters")
        for i, char in enumerate(final_characters):
            logger.info(f"  [{i+1}] {char.name} (role={char.role}, conf={char.confidence:.2f})")
        
        return final_characters
    
    def _detect_relationships(
        self,
        characters: List[Character],
        text: str,
        previous_snapshot: Optional[ChapterSnapshot]
    ) -> List[Relationship]:
        """Detect relationships between characters."""
        relationships = []
        
        # Get previous relationships if available
        previous_rels = {}
        if previous_snapshot:
            previous_rels = {tuple(sorted(r.pair)): r for r in previous_snapshot.relationships}
        
        # Check each character pair
        for i, char1 in enumerate(characters):
            for char2 in characters[i+1:]:
                pair_key = tuple(sorted([char1.name, char2.name]))
                
                # Check if they interact in the text
                if self._characters_interact(char1.name, char2.name, text):
                    # Check if relationship exists from previous chapter
                    if pair_key in previous_rels:
                        # Use existing relationship
                        relationships.append(previous_rels[pair_key])
                    else:
                        # Create new relationship
                        rel_type = self._classify_relationship(char1, char2, text)
                        rel = Relationship(
                            pair=(char1.name, char2.name),
                            relationship_type=rel_type,
                            dynamics="unknown",
                            stability="flat",
                            confidence=0.5
                        )
                        relationships.append(rel)
        
        return relationships
    
    def _characters_interact(self, name1: str, name2: str, text: str) -> bool:
        """Check if two characters interact in the text."""
        # Look for both names within 500 characters of each other
        positions1 = [m.start() for m in re.finditer(re.escape(name1), text)]
        positions2 = [m.start() for m in re.finditer(re.escape(name2), text)]
        
        for pos1 in positions1:
            for pos2 in positions2:
                if abs(pos1 - pos2) < 500:
                    return True
        
        return False
    
    def _classify_relationship(self, char1: Character, char2: Character, text: str) -> str:
        """Classify the type of relationship between two characters."""
        # Simple classification based on roles and context
        if char1.role == "protagonist" and char2.role == "romantic_lead":
            return "romance_arc"
        elif char1.role == "protagonist" and char2.role == "friend":
            return "peer_friendship"
        elif char1.role == char2.role:
            return "peer"
        else:
            return "acquaintance"
    
    def _extract_glossary_terms(
        self,
        text: str,
        previous_snapshot: Optional[ChapterSnapshot]
    ) -> List[GlossaryTerm]:
        """Extract cultural and specialized terms."""
        terms = []
        
        # Get previous terms
        previous_terms = {}
        if previous_snapshot:
            previous_terms = {t.romanized or t.japanese: t for t in previous_snapshot.glossary}
        
        # Common Japanese honorifics that should be preserved
        honorifics = {
            'senpai': GlossaryTerm(japanese='先輩', romanized='senpai', preserve=True),
            'sensei': GlossaryTerm(japanese='先生', romanized='sensei', preserve=True),
            'kouhai': GlossaryTerm(japanese='後輩', romanized='kouhai', preserve=True),
        }
        
        for term, data in honorifics.items():
            if term.lower() in text.lower():
                if term not in previous_terms:
                    terms.append(data)
        
        # Add previous terms
        terms.extend(previous_terms.values())
        
        return terms
    
    def _extract_narrative_flags(self, text: str, chapter_num: int) -> List[str]:
        """Extract narrative state flags from chapter."""
        flags = []
        
        # Simple keyword-based flag detection
        flag_patterns = {
            'lives_alone': r'\b(?:live|living)\s+alone\b',
            'school_setting': r'\b(?:school|classroom|class)\b',
            'confession': r'\b(?:confess|confession|feelings|love)\b',
            'misunderstanding': r'\b(?:misunderstanding|misunderstood|wrong idea)\b',
        }
        
        for flag_name, pattern in flag_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                flags.append(flag_name)
        
        return flags
    
    def compute_delta(
        self,
        current: ChapterSnapshot,
        previous: ChapterSnapshot
    ) -> Dict:
        """Compute delta between current and previous snapshots."""
        delta = {
            'new_characters': [],
            'changed_relationships': [],
            'new_terms': [],
            'new_flags': []
        }
        
        # Find new characters
        prev_names = {c.name for c in previous.characters}
        for char in current.characters:
            if char.name not in prev_names:
                delta['new_characters'].append(char)
        
        # Find new/changed relationships
        prev_rels = {tuple(sorted(r.pair)): r for r in previous.relationships}
        for rel in current.relationships:
            pair_key = tuple(sorted(rel.pair))
            if pair_key not in prev_rels:
                delta['changed_relationships'].append({
                    'type': 'new',
                    'relationship': rel
                })
            elif prev_rels[pair_key] != rel:
                delta['changed_relationships'].append({
                    'type': 'changed',
                    'from': prev_rels[pair_key],
                    'to': rel
                })
        
        # Find new glossary terms
        prev_terms = {t.romanized or t.japanese for t in previous.glossary}
        for term in current.glossary:
            term_key = term.romanized or term.japanese
            if term_key not in prev_terms:
                delta['new_terms'].append(term)
        
        # Find new narrative flags
        prev_flags = set(previous.narrative_flags)
        for flag in current.narrative_flags:
            if flag not in prev_flags:
                delta['new_flags'].append(flag)
        
        return delta
    
    def save_snapshot(self, snapshot: ChapterSnapshot) -> Path:
        """Save chapter snapshot to disk."""
        snapshot_path = self.context_dir / f"snapshot_{snapshot.chapter_id}.json"
        
        # Convert dataclasses to dicts
        data = {
            'chapter_id': snapshot.chapter_id,
            'chapter_num': snapshot.chapter_num,
            'generated_at': snapshot.generated_at,
            'reviewed_by_user': snapshot.reviewed_by_user,
            'user_corrections': snapshot.user_corrections,
            'characters': [asdict(c) for c in snapshot.characters],
            'relationships': [asdict(r) for r in snapshot.relationships],
            'glossary': [asdict(t) for t in snapshot.glossary],
            'narrative_flags': snapshot.narrative_flags
        }
        
        with open(snapshot_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ Saved snapshot: {snapshot_path.name}")
        return snapshot_path
    
    def load_snapshot(self, chapter_id: str) -> Optional[ChapterSnapshot]:
        """Load chapter snapshot from disk."""
        snapshot_path = self.context_dir / f"snapshot_{chapter_id}.json"
        
        if not snapshot_path.exists():
            return None
        
        with open(snapshot_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert dicts back to dataclasses
        snapshot = ChapterSnapshot(
            chapter_id=data['chapter_id'],
            chapter_num=data['chapter_num'],
            generated_at=data['generated_at'],
            reviewed_by_user=data.get('reviewed_by_user', False),
            user_corrections=data.get('user_corrections', 0),
            characters=[Character(**c) for c in data['characters']],
            relationships=[Relationship(**r) for r in data['relationships']],
            glossary=[GlossaryTerm(**t) for t in data['glossary']],
            narrative_flags=data.get('narrative_flags', [])
        )
        
        return snapshot
