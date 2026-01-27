# QC Assessment Rubric (Unified EN/VN Standard)

## Overview

This rubric covers quality assessment for both JP-EN and JP-VN light novel translations.
Sections marked **[GLOBAL]** apply to all languages. Language-specific sections are marked **[EN]** or **[VN]**.

---

## 1. Semantic Accuracy [GLOBAL] (Weight: 40%)

**Goal**: 1:1 fidelity with author intent, not necessarily 1:1 literal word mapping.

### CRITICAL FAIL
- Missing sentences or entire lines
- Mistranslations that invert meaning (e.g., "I like it" vs "I hate it")
- Hallucinated content not present in source
- Misidentified speaker (attributing dialogue to wrong character)

### MAJOR ISSUE
- Nuance lost (e.g., sarcastic tone translated as sincere)
- Tense confusion (past vs present)
- Ambiguous pronouns resolved incorrectly

### MINOR ISSUE
- Slight precision loss in descriptive adjectives
- Omitted honorifics where context implies them (if style guide allows)

---

## 2. Character Voice & Consistency [GLOBAL] (Weight: 30%)

**Goal**: Distinct, consistent voices matching established archetype profiles.

### CRITICAL FAIL

**[EN]**
- Ojou-sama character speaking in slang ("Hey", "Yeah")
- Delinquent/rough character speaking in polite Victorian English
- Inconsistent honorific variation ("Senpai" in one line, "Senior" in next)

**[VN]**
- Family pronouns violated (using tao/may or to/cau for siblings)
- OJOU archetype using GYARU particles (nha, ne instead of thua, a)
- Pronoun pair inconsistency within same scene (To-Cau suddenly becomes Em-Anh without RTAS trigger)

### MAJOR ISSUE

**[EN]**
- Voice drift (character sounds generic for a paragraph)
- "Translationese" sentence structures affecting flow

**[VN]**
- Particle mismatch with archetype (warm particles for KUUDERE)
- Mixed TSUN/DERE particles in same dialogue without state transition
- Rhythm mismatch (Staccato archetype with Legato sentences)

---

## 3. Stylistic Flow & Localization (Weight: 20%)

**Goal**: Natural prose that flows well for a native reader.

### CRITICAL FAIL [GLOBAL]
- Unreadable grammar or broken syntax
- "Word salad" (incoherent sentence structure)

### MAJOR ISSUE

**[EN] AI-isms to Eliminate**
- "A sense of [emotion]" → Use direct emotion
- "In a [adj] manner" → Use adverb
- "Indeed", "Quite", "Rather" in casual dialogue
- "I shall", "procure", "inquire" for teen characters
- Passive voice overuse where active is stronger
- Low contraction rate in casual dialogue (< 80%)

**[VN] Translationese to Eliminate**
- "Mot cam giac [emotion]" → Use direct emotion
- "Mot cach [adj]" → Use adverb or restructure
- "Viec" as unnecessary subject
- Passive constructions (bi/duoc ... boi)
- Japanese structure carry-over (SOV word order)
- Literal interjection translation (ee → "Ee" instead of "A")

---

## 4. Terminology & Continuity [GLOBAL] (Weight: 10%)

**Goal**: Consistency with project glossary.

### CRITICAL FAIL
- Wrong term for key concepts (e.g., "Magic" instead of "Mana" if defined)
- Wrong character name spelling
- Name order violation (Given-Surname instead of Surname-Given)

### MAJOR ISSUE

**[EN]**
- Hepburn romanization inconsistency ("Yuki" vs "Yuuki")

**[VN]**
- Han-Viet ratio violation for genre (>50% Han-Viet in slice-of-life)
- Inconsistent term translation (ma phap vs phep thuat for same concept)

---

## 5. Pronoun & Hierarchy System [VN ONLY] (Weight: Additional Critical Check)

**Goal**: Correct Vietnamese pronoun usage following priority hierarchy.

### Priority Order
1. **FAMILY_OVERRIDE** (Absolute) - Cannot be overridden
2. **ARCHETYPE_VOICE_LOCK** (If pair != empty)
3. **UNKNOWN_HIERARCHY** (If age/rank unclear)
4. **RTAS_PAIR_MAP** (Default selection)

### CRITICAL FAIL
- Family pronouns violated (tao/may for siblings)
- Archetype pair ignored (OJOU using To-Cau instead of Ta-Nguoi/Em-Anh)
- Hierarchy assumed without explicit Japanese markers
- **Pronoun pairing not semantically justified or inconsistent based on RTAS Pronouns Pairing table**

### MAJOR ISSUE
- RTAS threshold ignored (still using -san at RTAS 4.5)
- First-person lock violated (mixing toi/minh without narrative override)
- Unknown hierarchy using wrong default (adult context with To-Cau)

### Validation Checklist
- [ ] Family relationships use correct Vietnamese pronouns
- [ ] Archetype pairs match character profile
- [ ] RTAS thresholds respected (4.0 for honorific switch)
- [ ] First-person consistent throughout chapter
- [ ] Unknown hierarchy uses formal neutral

---

## 6. Safety & Content Warnings [GLOBAL]

**Policy**: Block ONLY if generated content is illegal/explicit non-consensual sexual violence involving minors.
**ALLOW**: Fictional violence, standard trope fan-service, and mature themes if present in source.

### FLAG
- If content is heavily sanitized/bowdlerized against instructions
- If "clinical framing" instructions were ignored for sensitive scenes
- If safety markers appear: [FLAGGED:], [UNTRANSLATABLE:], [Content warning:]

---

## Scoring Summary

| Category | Weight | Critical Fail | Major Issue | Minor Issue |
|----------|--------|---------------|-------------|-------------|
| Semantic Accuracy | 40% | -20 pts | -10 pts | -2 pts |
| Character Voice | 30% | -20 pts | -10 pts | -2 pts |
| Stylistic Flow | 20% | -20 pts | -10 pts | -2 pts |
| Terminology | 10% | -20 pts | -10 pts | -2 pts |
| [VN] Pronouns | Critical | -20 pts | -10 pts | -2 pts |

**Pass Threshold**: 85%
**Revision Required**: 70-84%
**Reject**: <70%

---

## Quick Reference: Language-Specific Checks

### English (EN)
| Check | Pattern | Fix |
|-------|---------|-----|
| AI-ism | "a sense of" | Direct emotion |
| AI-ism | "in a [adj] manner" | Adverb |
| Formality | "shall/procure/inquire" | will/get/ask |
| Contraction | Full forms in dialogue | Use contractions 80%+ |

### Vietnamese (VN)
| Check | Pattern | Fix |
|-------|---------|-----|
| Translationese | "mot cam giac" | Direct emotion |
| Translationese | "mot cach" | Adverb |
| Pronouns | tao/may for family | anh/chi/em |
| Particles | Wrong archetype | Match profile |
| Han-Viet | >50% in school_life | Reduce ratio |

---

*Version: 2.0 (Unified EN/VN)*
*Last Updated: 2026-01-22*
