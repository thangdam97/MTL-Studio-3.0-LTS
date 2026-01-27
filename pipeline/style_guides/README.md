# Style Guide System Documentation

## Overview
Style guides provide comprehensive translation guidelines for Vietnamese light novel translation, ensuring consistency, naturalness, and cultural appropriateness.

## Directory Structure
```
style_guides/
├── base_style_vi.json           # Universal Vietnamese rules
├── genres/
│   ├── romcom_school_life_vi.json
│   ├── isekai_fantasy_vi.json (TODO)
│   └── mystery_thriller_vi.json (TODO)
└── publishers/
    ├── overlap_vi.json
    ├── kadokawa_vi.json (TODO)
    └── media_factory_vi.json (TODO)
```

## Loading Hierarchy
1. **Base Style** (base_style_vi.json) - Always loaded first
2. **Genre Style** (e.g., romcom_school_life_vi.json) - Genre-specific rules
3. **Publisher Style** (e.g., overlap_vi.json) - Publisher preferences
4. **Volume Override** (optional) - Series-specific customization

Later styles override earlier ones when conflicts occur.

## Key Features

### 1. Pronoun System (Xưng Hô)
Most critical aspect of Vietnamese translation. Maps character relationships to appropriate pronouns based on:
- Age relative to speaker
- Gender
- Familiarity level (distant → warming → close)
- Social status
- Family relationship

**Example: Male protagonist → Female heroine (same age)**
- Phase 1 (distant): "cậu" / "[name]"
- Phase 2 (warming): "em" / "[name]"  
- Phase 3 (close): "em" (intimate)

### 2. Vocabulary Strategy
- **Primary:** Pure Vietnamese (thuần Việt) for naturalness
- **Secondary:** Sino-Vietnamese (Hán Việt) 15-25% for formality
- **Avoid:** Archaic literary terms, adult vocabulary in teen dialogue

### 3. Cultural Terms
- **Keep romanized:** Technical/unique Japanese terms (-senpai, bento)
- **Translate with context:** Common items (hộp cơm, mì ramen)
- **Always translate:** Basic greetings, common actions

### 4. Dialogue Style
- Teen speech: Natural, can use contractions (ko, thế, z)
- Age-appropriate: Matches character personality
- No MTL artifacts: Must sound like native Vietnamese

## Critical Fixes Addressed

### "Bà Cô" Issue ✅
**Problem:** Using "bà cô" for 30s stepmother
- "Bà" = elderly woman (60+)
- "Cô" = appropriate for 30-40s woman

**Solution:** Style guide maps stepmother → "cô" (NOT "bà cô")

### Pronoun Timing ✅
**Problem:** Using intimate pronouns too early
- "Em" immediately = unnatural for tsundere character

**Solution:** Pronoun evolution map tracks relationship phases

### Over-Sinicization ✅
**Problem:** Too much Hán Việt sounds archaic
- "Mỹ lệ" instead of "đẹp"
- "Ái mộ" instead of "thích"

**Solution:** Vocabulary preference lists enforce modern Vietnamese

## Integration with Pipeline

### 1. Manifest Enhancement
Add to volume manifest.json:
```json
{
  "style_guides": {
    "language": "vi",
    "genre": "romcom_school_life",
    "publisher": "overlap"
  }
}
```

### 2. Translator Prompt
Load and inject style guide into system prompt:
```python
style_guide = load_style_guides(
    base="base_style_vi.json",
    genre="romcom_school_life_vi.json",
    publisher="overlap_vi.json"
)

prompt = f"""
VIETNAMESE TRANSLATION STYLE GUIDE:
{format_guide_for_llm(style_guide)}

Apply these guidelines to maintain consistency and naturalness.
...
"""
```

### 3. Quality Validation
Post-translation checks:
- Pronoun consistency across chapters
- Vocabulary appropriateness
- No forbidden patterns
- Cultural term handling

## Usage Examples

### Good Translation (Following Guide)
```
JP: 彼女は美しかった
BAD: Nàng ta thật mỹ lệ (archaic, Hán Việt heavy)
GOOD: Cô ấy thật xinh đẹp (natural, modern)

JP: 義母のジェシカ
BAD: Bà cô Jessica (too old)
GOOD: Cô Jessica (appropriate age)

JP: ソフィアは言った
Phase 1: Sophia nói (distant, using name)
Phase 3: Em ấy nói (close, using pronoun)
```

## Maintenance

### Adding New Genres
1. Create `genres/[genre_name]_vi.json`
2. Follow romcom template structure
3. Customize pronoun maps, vocabulary, tone
4. Test with sample chapter

### Publisher Profiles
1. Analyze 3-5 volumes from publisher
2. Identify common patterns, tone preferences
3. Create `publishers/[publisher]_vi.json`
4. Document typical genres and archetypes

### Version Control
- Increment version when making breaking changes
- Document changes in git commits
- Test against existing translations

## Future Enhancements
- [ ] Isekai fantasy genre guide
- [ ] Action/battle genre guide
- [ ] Mystery/thriller genre guide
- [ ] KADOKAWA publisher profile
- [ ] Automated style validation tool
- [ ] A/B testing different pronoun strategies
- [ ] Community feedback integration

## References
- Vietnamese pronoun system: [Xưng hô trong tiếng Việt]
- Light novel translation conventions
- Community translation best practices
- Official Vietnamese light novel releases (for benchmarking)
