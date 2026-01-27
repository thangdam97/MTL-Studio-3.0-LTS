# MEGA CORE TRANSLATION ENGINE (Vietnamese)

**Version:** 1.0
**Date:** 2026-01-22
**Purpose:** Unified core translation mechanics for JP-VN Light Novel translation
**Consolidation:** Core translation logic for Vietnamese localization

---

## Table of Contents

1. [Pronoun Priority System](#1-pronoun-priority-system)
2. [RTAS Scoring Logic](#2-rtas-scoring-logic)
3. [Rhythm & Pacing Engine](#3-rhythm-pacing-engine)
4. [Register Formality System](#4-register-formality-system)
5. [Safety Compliance Matrix](#5-safety-compliance-matrix)
6. [Han-Viet Vocabulary System](#6-han-viet-vocabulary-system)

---

<a name="1-pronoun-priority-system"></a>
# 1. Pronoun Priority System

**Purpose:** Vietnamese pronoun selection is THE most critical aspect of JP-VN translation.
**Framework:** FAMILY > ARCHETYPE > UNKNOWN_HIERARCHY > RTAS

---

## Priority Hierarchy (Absolute)

```
Level 1: FAMILY_OVERRIDE (Cannot be overridden)
  └── Sibling, Parent, Child relationships
  └── Always use: Anh/Chi/Em/Ba/Me/Con
  └── NEVER use: Tao/May, To/Cau for family

Level 2: ARCHETYPE_VOICE_LOCK (If pair != empty)
  └── Character-specific pronoun pairs
  └── Overrides RTAS-based selection
  └── Example: OJOU = "Ta-Nguoi|Em-Anh"

Level 3: UNKNOWN_HIERARCHY (If hierarchy unclear)
  └── Formal neutral pairs based on setting
  └── HIGH_SCHOOL: To-Cau (peer assumption)
  └── ADULT: Toi-Anh/Co (formal default)

Level 4: RTAS_PAIR_MAP (Default selection)
  └── Relationship-based pronoun pairs
  └── Score 1.0-5.0, baseline 3.0
```

---

## Family Pronoun Lock (ABSOLUTE)

| Relationship | Self | Other | Notes |
|--------------|------|-------|-------|
| Younger → Elder Sibling | Em | Anh/Chi | Always VN pronouns |
| Elder → Younger Sibling | Anh/Chi | Em | Always VN pronouns |
| Child → Parent | Con | Ba/Me | Always VN pronouns |
| Parent → Child | Ba/Me | Con | Always VN pronouns |

**BANNED in Family Context:**
- ❌ Tao/May (too hostile)
- ❌ To/Cau (too casual/peer)
- ❌ Toi/Anh (too formal)

**Family -chan Exception:**
When family members use "-chan" for younger sibling, KEEP as-is:
- ✅ "Mei-chan, an com di" (natural)
- ❌ "Be Mei, an com di" (unnatural)

---

## First Person Selection

| Context | Pronoun | Lock Rule |
|---------|---------|-----------|
| Default Male | Toi | Lock entire chapter |
| Default Female | Toi/Minh | Lock entire chapter |
| Female POV (soft) | Minh | Introspective moments |
| Male Casual | Minh/To | With friends |
| Tsundere Defensive | Toi | Maintains distance |

**Narrative Override (Internal Monologue):**
- "Toi cam thay" → Keep "toi" (observation)
- "Chinh toi" → "Chinh minh" (inner thought)
- Max 2 overrides per paragraph
- Exception: TSUNDERE breakdown keeps "toi"

---

<a name="2-rtas-scoring-logic"></a>
# 2. RTAS Scoring Logic

**Definition:** Relationship Tension & Affection Score (RTAS) measures intimacy on 1.0-5.0 scale.
**Baseline:** 3.0
**Purpose:** Determines pronoun pair selection when FAMILY and ARCHETYPE don't override.

---

## RTAS Pair Map (Mixed Gender / Romance)

| Score Range | Self | Other | Tone |
|-------------|------|-------|------|
| 1.0-1.5 | Toi | Anh/Co | Formal, distant |
| 1.5-2.5 | Toi | Anh/Chi | Polite, defensive |
| 2.0-3.5 | To | Cau | Casual peers |
| 3.5-4.2 | To | Anh | Friendly, warm |
| 4.2-5.0 | Em | Anh | Romantic, intimate |

**Threshold Rule (4.0):**
- Below 4.0: Keep JP honorifics (-san, -kun, Senpai)
- At/Above 4.0: Switch to VN pronouns (Anh/Em)
- Exception: FAMILY always uses VN regardless of RTAS

---

## Male Friendship Pronoun Tiers (CRITICAL)

**Purpose:** Vietnamese male friendship has distinct tiers that MUST be reflected in pronouns.

| Tier | Self | Other | Context | Example Signals |
|------|------|-------|---------|-----------------|
| **Tier 1: Distant/Formal** | Tớ | Cậu | New classmate, acquaintance, first meeting | Polite conversation, surface-level chat |
| **Tier 2: Close Friends** | Tôi | Ông | Good friends who banter, trust each other | Teasing, inside jokes, casual insults |
| **Tier 3: Bros/Intimate** | Tao | Mày | Best friends, very informal settings | Crude jokes, no filter, private settings |

**Detection Signals for Tier 2 (Tôi-Ông):**
- Teasing/banter language in JP (からかう, いじる)
- Casual insults that show familiarity (馬鹿, アホ)
- Physical contact (shoulder pat, headlock)
- "俺/お前" usage in casual JP
- Long friendship history mentioned
- Sharing embarrassing/personal topics

**Detection Signals for Tier 3 (Tao-Mày):**
- Very crude language in JP
- Private/drunk settings
- Sexual jokes or vulgar banter
- Explicit "best friend" statement
- Characters living together / childhood friends

**Examples:**

```
Tier 1 (Tớ-Cậu) - Distant classmate:
"Này cậu, hôm nay có bài tập không?"
"Tớ không biết, cậu hỏi thầy đi."

Tier 2 (Tôi-Ông) - Close friends (like Tomoya & Koushirou):
"Ông có thù hằn gì với tôi không đấy?"
"Có chứ! Thù sâu nặng luôn là đằng khác!"
"Tôi đi guốc trong bụng ông rồi."

Tier 3 (Tao-Mày) - Bros, no filter:
"Mày điên à? Sao lại làm thế?"
"Kệ tao! Việc của mày à?"
```

**IMPORTANT:** In the 0d29 translation, Tomoya & Koushirou should use **Tier 2 (Tôi-Ông)**, NOT Tier 1 (Tớ-Cậu). They are established close friends who banter and tease each other.

---

## Female Friendship Pronoun Tiers

| Tier | Self | Other | Context |
|------|------|-------|---------|
| **Tier 1: Formal/Distant** | Tớ/Mình | Cậu/Bạn | New acquaintance, polite |
| **Tier 2: Close Friends** | Tớ/Mình | Cậu | Good friends, comfortable |
| **Tier 3: Best Friends** | Tao | Mày | Very close, playful teasing |

**Notes:**
- Female friendships in VN use "Tớ-Cậu" more broadly
- "Mình" can be both self-reference AND address (context-dependent)
- "Tao-Mày" between girls is playful, not hostile (unlike male usage which can be)

---

## Mixed-Gender Friendship (Non-Romantic)

| Relationship | Self (M) | Other (F) | Self (F) | Other (M) |
|--------------|----------|-----------|----------|-----------|
| Classmates | Tớ/Tôi | Cậu | Tớ/Mình | Cậu |
| Close Friends | Tôi | Cậu/Bà | Tớ | Ông/Cậu |
| Banter/Teasing | Tôi | Bà này | Tớ | Ông này |

**Note:** "Bà" for a female friend (teasing) mirrors "Ông" for a male friend. Example:
```
"Bà này điên thật đấy!" (Affectionate teasing to female friend)
"Ông này lại giở trò gì đây?" (Affectionate teasing to male friend)
```

---

## RTAS Modifiers

| Category | Modifier | Range |
|----------|----------|-------|
| Pronouns | Intimate pronouns | +0.3 to +0.7 |
| Honorifics | No honorific / -chan | +0.5 |
| Honorifics | -sama / formal | -0.8 |
| Particles | Warm particles (nha, ne) | +0.2 to +0.4 |
| Context | Conflict/anger | -2.0 |
| Context | Confession/intimate | +1.5 |
| Proxemics | Physical closeness | +0.5 to +1.2 |

**Formula:** `RTAS_FINAL = 3.0 + Sum(MODIFIERS)`

---

## Unknown Hierarchy Protocol

**Trigger:** First encounter, no explicit age/grade/rank stated.

**Principle:** Do NOT assume hierarchy from:
- Narrative descriptions
- Physical appearance/beauty
- Social status
- Emotional tone

**ONLY establish hierarchy from EXPLICIT Japanese markers:**
- Stated age/grade: "一年生", "二年生", "18歳"
- Honorifics: "先輩", "後輩", "年上"
- Direct narrative: "彼女は俺より年上だ"

**Neutral Pairs by Setting:**

| Setting | Self | Other | Notes |
|---------|------|-------|-------|
| High School | To | Cau | Peer assumption safe |
| General Adult | Toi | Anh/Co | Formal default |
| Workplace | Toi | Anh/Chi | Professional |

---

<a name="3-rhythm-pacing-engine"></a>
# 3. Rhythm & Pacing Engine

**Purpose:** Controls sentence cadence per character archetype.

---

## Rhythm Types

### Legato (L) - Flowing, Elegant
**Archetypes:** OJOU, ONEE
**Word Count:** 15-30+ words per sentence
**Structure:** Complex clauses, commas/semicolons
**Tone:** Elegant, contemplative

```
Example (OJOU):
"Neu duoc, em muon nghe y kien cua anh ve van de nay, boi le qua that...
day la mot tinh huong dac biet ma em chua tung gap phai."
```

### Staccato (S) - Short, Clipped
**Archetypes:** GYARU, DELINQ, KANSAI, BOKUKKO
**Word Count:** 5-12 words per sentence
**Structure:** Simple sentences, periods/exclamations
**Tone:** Energetic, urgent, casual

```
Example (GYARU):
"Troi oi! Cau noi gi vay? Khong the tin duoc!"

Example (DELINQ):
"Bien di. Khong muon nhin mat may."
```

### Staccato Breathless (Extreme)
**Trigger:** RTAS >= 4.8 OR peak emotional moment
**Word Count:** 2-5 word fragments
**Usage:** Sparingly, 2-8 fragments max

```
Example:
"Tim dap. Manh qua. Khong the. Tho duoc."
```

### Tenuto (T) - Weighted Pauses
**Archetypes:** SAMURAI, LOLIBABA, KUUDERE, CHUUNI
**Word Count:** 10-18 words per sentence
**Structure:** Balanced clauses, em dashes
**Tone:** Serious, measured, deliberate

```
Example (KUUDERE):
"Toi khong hieu. Tai sao lai phai quan tam den viec do."

Example (SAMURAI):
"Tai ha xin thinh giao — lieu nguoi co dam don nhan loi thach dau nay."
```

---

## Rhythm Shifting Rules

- Base rhythm from archetype CAN shift based on psychological state
- Return to base rhythm once emotional state normalizes
- Breathless mode is OPTIONAL enhancement for peak intensity only

| Emotional State | Rhythm Shift |
|-----------------|--------------|
| Panic/Fear | Any → Staccato |
| Confession | Any → Legato |
| Anger/Frustration | Legato → Staccato |
| Calm Reflection | Staccato → Tenuto |

---

<a name="4-register-formality-system"></a>
# 4. Register Formality System

**Purpose:** Context-based formality adjustment.

---

## Register Levels (1-5)

| Level | Context | Pronouns | Particles |
|-------|---------|----------|-----------|
| 1 | Formal ceremonies | Toi-Quy vi | A, thua |
| 2 | Business/School formal | Toi-Anh/Chi | A, da |
| 3 | Casual acquaintance | Toi/To-Cau | (none) |
| 4 | Friends | To-Cau | Nha, ne |
| 5 | Intimate | Em-Anh | Nha~, ne~ |

---

## BAN_CONTEXT Rules

Certain contexts suppress casual elements:

| Context | Suppressed | Allowed |
|---------|------------|---------|
| Funeral | Slang, humor, casual | Regional warmth |
| Formal ceremony | All casual particles | Respectful tone |
| First meeting | Familiar pronouns | Polite neutral |
| Public speech | Personal particles | Professional tone |

---

<a name="5-safety-compliance-matrix"></a>
# 5. Safety Compliance Matrix

**Purpose:** Handle sensitive content without sanitization.

---

## Fiction Context Exemptions

Light novel tropes acceptable within fictional context:
- Master/servant dynamics (fantasy)
- Age-gap relationships (fantasy/historical)
- Power imbalances (narrative conflict)
- Fantasy violence (combat, magic)
- Fan service (comedic, non-explicit)
- Romantic tension (age-appropriate)

**Translation Mandate:** Translate as written. Preserve author intent. Do NOT sanitize.

---

## Harm Reduction Strategies

| Trigger | Strategy |
|---------|----------|
| Self-harm | "Suy nghi xam nhap" / "Xung dong toi tam" |
| Assault | Clinical testimony framing |
| Minors in danger | Emphasize platonic safety |
| Trauma | "Su co do" / "Nhung gi co ay da trai qua" |

**Emergency Protocol:**
If content blocks despite reframing:
- Summarize: `[Canh bao noi dung: de cap toi bao luc]`
- Flag: `[FLAGGED: Safety block on paragraph X]`

---

<a name="6-han-viet-vocabulary-system"></a>
# 6. Han-Viet Vocabulary System

**Purpose:** Balance Sino-Vietnamese vocabulary by genre.

---

## Genre-Based Ratios

| Genre | Han-Viet % | Rationale |
|-------|------------|-----------|
| School Life / Romance | 40-50% max | Natural daily speech |
| Fantasy / Isekai | 60-70% OK | World-building terms |
| Historical / Wuxia | 70-80% OK | Period authenticity |
| Slice of Life | 35-45% max | Casual conversations |

---

## Common Han-Viet Choices

| Japanese | Han-Viet | Pure Vietnamese | Use Case |
|----------|----------|-----------------|----------|
| 感謝 | Cam ta | Cam on | Formal vs casual |
| 愛情 | Ai tinh | Tinh yeu | Literary vs spoken |
| 友人 | Huu nhan | Ban be | Formal vs casual |
| 学校 | Hoc duong | Truong hoc | Literary vs spoken |
| 心臓 | Tam tang | Trai tim | Medical vs emotional |

**Rule:** Match register and character voice. GYARU uses Pure Vietnamese; OJOU uses Han-Viet.

---

## Vocabulary Lock

Once a term is established in a project, LOCK it:
- First occurrence: "Ma phap" (magic)
- All subsequent: "Ma phap" (NOT "Phep thuat")

Consult `glossary.json` for project-specific locks.

---

*End of MEGA_CORE_TRANSLATION_ENGINE_VN.md*
