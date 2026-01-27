# Name Filters System

JSON-based filter patterns for character name extraction from ruby-annotated Japanese EPUB content.

## Architecture

### Separation of Concerns
- **Filter patterns** = **data** (stored in JSON)
- **Filter logic** = **code** (in `ruby_extractor.py`)

This separation enables:
- ✅ Easy updates without touching Python code
- ✅ Publisher-specific overrides
- ✅ User customization for domain-specific terms
- ✅ Genre-specific filter sets (isekai vs school life)
- ✅ Consistency with existing publisher profile system

## Directory Structure

```
pipeline/librarian/name_filters/
├── __init__.py              # Public API exports
├── manager.py               # Filter loading & merging logic
├── schema.json              # JSON schema for validation
├── base_filters.json        # Default exclusions (always loaded)
└── genre_filters/           # Genre-specific overrides
    ├── isekai.json         # Fantasy/isekai specific terms
    └── school_life.json    # School romance specific terms
```

## Filter Types

### 1. Katakana Common Words (`katakana_common_words`)
**Purpose:** Katakana sequences that are NOT character names.

**Categories:**
- `gaming_fantasy`: RPG/isekai terms (スキル, レベル, ダンジョン)
- `school_daily_life`: School/daily terms (クラス, テスト, スマホ)
- `technology`: Tech terms (パソコン, インターネット)
- `food_drink`: Food/drink (コーヒー, パン, カレー)
- `fashion_appearance`: Fashion (スカート, シャツ, メイク)
- `media_entertainment`: Media (アニメ, ゲーム, ドラマ)
- `general`: Miscellaneous (タイプ, ストレス, イケメン)

**Example:**
```json
"katakana_common_words": {
  "gaming_fantasy": [
    "スキル", "ステータス", "レベル", "ポイント"
  ]
}
```

**Usage:** Prevents false positives like "スキル" being classified as a character name.

---

### 2. Kanji Stylistic Ruby (`kanji_stylistic_ruby`)
**Purpose:** Kanji words that commonly get stylistic katakana ruby (NOT kira-kira names).

**Categories:**
- `food_cooking`: Food terms with ruby (出汁→ダシ, 豆腐→トーフ)
- `sensory`: Sensory words (臭い→スメル, 音→サウンド)
- `weapons_tools`: Weapons with English ruby (刃→ブレード, 剣→ソード)
- `body_emotion`: Body/emotion (心→ハート, 血→ブラッド)
- `abstract_concepts`: Abstract (愛→ラブ, 絆→ボンド, 世界→ワールド)
- `general`: Locations/nature (家, 森, 風, 炎)

**Example:**
```json
"kanji_stylistic_ruby": {
  "weapons_tools": ["刃", "剣", "槍", "弓", "盾"],
  "abstract_concepts": ["愛", "恋", "絆", "運命"]
}
```

**Usage:** Distinguishes stylistic ruby (出汁→ダシ) from true kira-kira names (愛梨→ラブリ).

---

### 3. Common Terms (`common_terms`)
**Purpose:** Japanese words that are NOT character names.

**Categories:**
- `pronouns`: Pronouns (貴方, 彼女, 自分)
- `family_terms`: Family roles (祖母, 叔父, 従兄)
- `titles_roles`: Titles/occupations (先生, 社長, 殿下)
- `temporal`: Time expressions (今日, 明日, 昨日)
- `locations`: Places (学校, 病院, 実家)
- `emotions_states`: Emotional states (態度, 気持, 様子)
- `body_parts`: Body parts (頭, 顔, 手, 心臓)
- `compound_words`: Complex compounds (惚気, 顛末, 狼狽)
- `action_state`: Action/state verbs (躊躇, 哄笑, 罵倒)
- `general`: Miscellaneous (不憫, 馬鹿, 阿呆)

**Example:**
```json
"common_terms": {
  "pronouns": ["貴方", "彼女", "彼氏"],
  "family_terms": ["祖母", "祖父", "義母"]
}
```

**Usage:** Excludes common words from name extraction even if they have hiragana ruby.

---

### 4. Name Indicators (`name_indicators`)
**Purpose:** Patterns that BOOST confidence a term is a character name.

**Fields:**
- `suffixes`: Name suffixes (さん, くん, 様, 先生, 先輩)
- `intro_patterns`: Self-introduction patterns (と申します, という, の名は)
- `first_person_pronouns`: First-person pronouns (俺, 私, 僕, あたし)

**Example:**
```json
"name_indicators": {
  "suffixes": [
    "さん", "くん", "君", "ちゃん", "様", "殿",
    "先生", "先輩", "後輩"
  ],
  "intro_patterns": [
    "と申します", "といいます", "という",
    "と呼ばれ", "の名は"
  ],
  "first_person_pronouns": [
    "俺", "私", "僕", "あたし", "わたし"
  ]
}
```

**Usage:**
- Suffix detection: "九条さん" → "九条" is a name (confidence +0.50)
- Intro patterns: "九条といいます" → "九条" is a name (confidence +0.98)
- First-person intro: "俺、九条才斗" → "九条才斗" is a name (confidence +0.95)

---

### 5. Confidence Modifiers (`confidence_modifiers`)
**Purpose:** Fine-tune confidence scoring.

**Fields:**
- `boosts`: Positive adjustments
- `penalties`: Negative adjustments
- `threshold`: Minimum confidence for name acceptance (default: 0.70)

**Example:**
```json
"confidence_modifiers": {
  "boosts": {
    "name_suffix_present": 0.30,
    "intro_pattern_match": 0.25,
    "first_person_intro": 0.25,
    "pov_marker": 0.30,
    "four_char_full_name": 0.35
  },
  "penalties": {
    "five_plus_chars": -0.25,
    "common_word_match": -0.50
  },
  "threshold": 0.70
}
```

**Usage:** Adjust scoring algorithm without code changes.

---

## Usage

### Basic Usage (Base Filters Only)

```python
from pipeline.librarian.ruby_extractor import RubyExtractor

# Uses base_filters.json only
extractor = RubyExtractor()
```

**Loads:** 170 katakana words, 89 kanji stylistic ruby, 216 common terms

---

### Genre-Specific Usage

```python
from pipeline.librarian.ruby_extractor import RubyExtractor

# Load base + isekai genre filters
extractor = RubyExtractor(genres=["isekai"])

# Load base + school_life genre filters
extractor = RubyExtractor(genres=["school_life"])

# Load multiple genres (merged)
extractor = RubyExtractor(genres=["isekai", "school_life"])
```

**Effect:** Genre filters extend/override base filters.

---

### Direct Filter Access

```python
from pipeline.librarian.name_filters import load_filters

# Load filters manually
filters = load_filters(genres=["isekai"])

# Access filter data
print(filters.katakana_common_words)  # Set of katakana terms
print(filters.name_indicators.suffixes)  # Set of name suffixes
print(filters.confidence_modifiers.threshold)  # 0.70
print(filters.loaded_filters)  # ['base', 'isekai']
```

---

## Creating Custom Filters

### Genre Filter Template

**File:** `genre_filters/my_genre.json`

```json
{
  "meta": {
    "name": "My Genre Filters",
    "version": "1.0",
    "description": "Custom filters for my genre",
    "extends": "base"
  },
  "katakana_common_words": {
    "my_category": [
      "カスタム", "ワード", "リスト"
    ]
  },
  "kanji_stylistic_ruby": {
    "my_category": ["魔法", "技"]
  },
  "common_terms": {
    "my_category": ["勇者", "魔王"]
  },
  "name_indicators": {
    "suffixes": ["殿"],
    "intro_patterns": ["なり"],
    "first_person_pronouns": ["拙者"]
  },
  "confidence_modifiers": {
    "boosts": {
      "custom_pattern": 0.20
    },
    "threshold": 0.65
  }
}
```

**Key Points:**
- `extends`: Inherit from another filter (usually "base")
- Categories: Can add new categories or extend existing ones
- Merge behavior: Lists are ADDED to base (not replaced)

---

### Filter Inheritance

**Example:** `genre_filters/fantasy_school.json`

```json
{
  "meta": {
    "name": "Fantasy School Filters",
    "version": "1.0",
    "extends": "school_life"
  },
  "katakana_common_words": {
    "fantasy_additions": [
      "マジック", "エンチャント", "ルーン"
    ]
  }
}
```

**Load Order:**
1. `base_filters.json` (always loaded first)
2. `school_life.json` (because of `"extends": "school_life"`)
3. `fantasy_school.json` (your custom filter)

**Result:** All three filter sets are merged together.

---

## Schema Validation

**File:** `schema.json`

Defines the structure for all filter JSON files using JSON Schema Draft 2020-12.

**Validation Tools:**
```bash
# Install jsonschema validator
pip install jsonschema

# Validate a filter file
python -m pipeline.librarian.name_filters.manager validate my_filter.json
```

**Schema ensures:**
- ✅ Required fields present
- ✅ Correct data types (arrays, objects, strings)
- ✅ Version format valid (e.g., "1.0")
- ✅ Extends field references valid parent

---

## Performance Considerations

### Caching
The `NameFilterManager` caches loaded filter sets:

```python
# First load: Reads from disk
filters1 = load_filters(genres=["isekai"])  # ~10ms

# Second load: Returns cached version
filters2 = load_filters(genres=["isekai"])  # <1ms (cached)
```

**Cache keys:** `"base"`, `"base+isekai"`, `"base+isekai+school_life"`

### Clear Cache
```python
from pipeline.librarian.name_filters import get_filter_manager

manager = get_filter_manager()
manager.clear_cache()
```

**When to clear:**
- After editing filter JSON files
- During development/testing
- Hot-reloading scenarios

### Memory Footprint
- Base filters: ~2KB (170 katakana + 89 kanji + 216 terms)
- Each genre filter: ~500-1000 bytes
- Total: <5KB for typical usage

---

## Filter Management API

### List Available Genres

```python
from pipeline.librarian.name_filters import get_filter_manager

manager = get_filter_manager()
genres = manager.list_available_genres()
# Returns: ['isekai', 'school_life', ...]
```

---

### Get Filter Metadata

```python
from pipeline.librarian.name_filters import get_filter_manager

manager = get_filter_manager()

# Get base filter info
info = manager.get_filter_info()
# Returns: {"name": "Base Name Filters", "version": "1.0", ...}

# Get genre filter info
info = manager.get_filter_info(genre="isekai")
# Returns: {"name": "Isekai Genre Filters", "version": "1.0", ...}
```

---

## Examples

### Example 1: Detecting Kira-Kira Names

**Input:** `<ruby>愛梨<rt>ラブリ</rt></ruby>`

**Filter Check:**
1. ✅ Has kanji: "愛梨"
2. ✅ Has katakana ruby: "ラブリ"
3. ✅ 2 kanji, 4 katakana (typical length)
4. ❌ NOT in `katakana_common_words` (not "スキル" or "レベル")
5. ❌ NOT in `kanji_stylistic_ruby` (not "出汁→ダシ")
6. ✅ NOT single kanji (single kanji with katakana = stylistic)

**Result:** Classified as **kira-kira name** (confidence: 0.98)

---

### Example 2: Excluding Common Katakana

**Input:** Katakana sequence "スキル" appears 20 times

**Filter Check:**
1. ✅ Katakana only: "スキル"
2. ✅ Appears 20 times (high frequency)
3. ❌ FOUND in `katakana_common_words["gaming_fantasy"]`

**Result:** **Excluded** (confidence: 0.0)

---

### Example 3: Name Suffix Boost

**Context:** "九条さんは"

**Filter Check:**
1. Extract ruby: "九条" (kanji) + "くじょう" (ruby)
2. Find suffix: "さん" immediately after "九条"
3. ✅ "さん" is in `name_indicators.suffixes`

**Result:** **High confidence name** (confidence: 0.98)

---

### Example 4: First-Person Introduction

**Context:** "俺、九条才斗は"

**Filter Check:**
1. Pattern: "俺、九条才斗"
2. ✅ "俺" is in `name_indicators.first_person_pronouns`
3. ✅ Matches pattern: `{pronoun}、{kanji}`

**Result:** **Very high confidence name** (confidence: 0.95)

---

## Customization Strategies

### Strategy 1: Publisher-Specific Filters

Create publisher-specific filter files:

```
genre_filters/
├── kadokawa.json
├── shueisha.json
└── kodansha.json
```

Load based on publisher:
```python
publisher = "kadokawa"
extractor = RubyExtractor(genres=[publisher])
```

---

### Strategy 2: Work-Type Filters

Create filters for different LN types:

```
genre_filters/
├── isekai.json           # Fantasy/isekai
├── school_life.json      # School romance
├── mystery.json          # Mystery/detective
├── sci_fi.json          # Sci-fi
└── action.json          # Action/battle
```

---

### Strategy 3: User Customization

Allow users to override filters:

```python
import json
from pathlib import Path

# User provides custom filter file
user_filter_path = Path("~/.mtl_studio/custom_filters.json")

# Load user filters as genre
if user_filter_path.exists():
    # Copy to genre_filters directory
    import shutil
    shutil.copy(user_filter_path, 
                "pipeline/librarian/name_filters/genre_filters/user_custom.json")
    
    # Load with custom genre
    extractor = RubyExtractor(genres=["base", "isekai", "user_custom"])
```

---

## Troubleshooting

### Issue: Names Being Excluded

**Symptom:** A valid character name is not being extracted.

**Debug Steps:**

1. Check if name is in `common_terms`:
   ```python
   filters = load_filters()
   print("雪乃" in filters.common_terms)  # Should be False
   ```

2. Check confidence threshold:
   ```python
   print(filters.confidence_modifiers.threshold)  # Default: 0.70
   ```

3. Lower threshold temporarily:
   ```json
   "confidence_modifiers": {
     "threshold": 0.60
   }
   ```

---

### Issue: Non-Names Being Extracted

**Symptom:** Common words are being classified as character names.

**Solutions:**

1. Add to `katakana_common_words`:
   ```json
   "katakana_common_words": {
     "general": ["イケメン", "スマホ"]
   }
   ```

2. Add to `kanji_stylistic_ruby`:
   ```json
   "kanji_stylistic_ruby": {
     "general": ["心", "魂"]
   }
   ```

3. Add to `common_terms`:
   ```json
   "common_terms": {
     "general": ["大丈夫", "馬鹿"]
   }
   ```

---

### Issue: Cache Not Updating

**Symptom:** JSON edits not taking effect.

**Solution:**
```python
from pipeline.librarian.name_filters import get_filter_manager

manager = get_filter_manager()
manager.clear_cache()
```

---

## Best Practices

### ✅ DO:
- Use base_filters.json for universal exclusions
- Create genre filters for domain-specific terms
- Document custom categories in filter metadata
- Use descriptive category names
- Keep lists alphabetically sorted for maintainability
- Test filters with real EPUB samples

### ❌ DON'T:
- Hardcode filter data in Python code
- Create duplicate entries across multiple categories
- Add character names to exclusion lists (defeats purpose)
- Use overly broad exclusion patterns
- Forget to clear cache after editing JSON

---

## Migration Guide

### From Hardcoded Constants to JSON

**Before:**
```python
# In ruby_extractor.py
COMMON_TERMS = {
    "貴方", "彼女", "自分", ...
}
NAME_SUFFIX_KANJI = ["様", "殿", ...]
```

**After:**
```json
// In base_filters.json
{
  "common_terms": {
    "pronouns": ["貴方", "彼女", "自分"]
  },
  "name_indicators": {
    "suffixes": ["様", "殿"]
  }
}
```

**Code change:**
```python
# Old
if kanji in self.COMMON_TERMS:
    return 0.0

# New
if kanji in self._common_terms:
    return 0.0
```

---

## Version History

### v1.0 (Current)
- ✅ Base filters with 170+ katakana words
- ✅ 89 kanji stylistic ruby patterns
- ✅ 216 common terms
- ✅ Genre inheritance via "extends"
- ✅ Caching for performance
- ✅ JSON schema validation

### Future Enhancements
- [ ] Auto-learning from manual corrections
- [ ] Publisher profile integration
- [ ] ML-based confidence tuning
- [ ] Filter versioning system
- [ ] Web UI for filter management

---

## Related Documentation

- [Ruby Extractor API](../ruby_extractor.py) - Main extraction logic
- [Publisher Profiles](../publisher_profiles/README.md) - Publisher-specific settings
- [JSON Schema Spec](https://json-schema.org/draft/2020-12/schema) - Schema reference

---

**Last Updated:** January 21, 2026  
**Maintainer:** MTL Studio Development Team
