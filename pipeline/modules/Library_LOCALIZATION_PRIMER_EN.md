---
**00_LOCALIZATION_PRIMER_EN.md — ENGLISH LOCALIZATION FOUNDATION**
**Module Status:** ACTIVE & AUTHORITATIVE
**Purpose:** Character archetypes, idiom westernization, honorific handling, cultural references
---

# 00_LOCALIZATION_PRIMER_EN

## RTAS Scoring Logic

**Definition** – Relationship Tension & Affection Score (RTAS) measures intimacy on a 1.0‑5.0 scale.
**Baseline** – 3.0
**Modifiers** – Pronouns (+0.3‑+0.7), honorifics (‑0.8‑+0.5), particles (+0.2‑+0.4), contextual keywords (‑2.0‑+1.5), proxemics (‑0.5‑+1.2).
**Formula** – `RTAS_FINAL = 3.0 + Σ(MODIFIERS)`

## SECTION 1: CHARACTER ARCHETYPE VOICE PROFILES

### 1.1 NOBLE/REFINED ARCHETYPES

#### **ARCHETYPE 01: OJOU-SAMA (NOBLE LADY)**
**Core Traits:** Refined, cultured, formal speech, dignified

**Voice Markers:**
- **Vocabulary:** Latinate words (request/inquire vs ask, commence vs start)
- **Contractions:** Minimal to none ("I am" not "I'm", "do not" not "don't")
- **Sentence Structure:** Complete, flowing sentences; subordinate clauses
- **Filler Words:** "Oh my", "Goodness", "Indeed", "Quite"
- **Forbidden:** Slang, crude language, fragments, "like", "yeah"
- **Punctuation:** Proper periods, minimal exclamations
- **Address Style:** Full names, Mr./Ms., titles (even at RTAS 3.0+)

**Example Dialogue:**
```
RTAS 2.0: "Good morning, Mr. Tanaka. I trust you slept well?"
RTAS 3.5: "Good morning, Ryo. Did you sleep well?" (softens but stays formal)
RTAS 4.5: "Morning, Ryo. You look well-rested." (warm but still proper)
```

---

#### **ARCHETYPE 02: STOIC KNIGHT/WARRIOR**
**Core Traits:** Duty-bound, measured, direct, professional

**Voice Markers:**
- **Vocabulary:** Precise, military-adjacent (report, confirm, objective)
- **Contractions:** Minimal ("cannot" preferred over "can't")
- **Sentence Structure:** Brief, declarative statements
- **Filler Words:** Rare; "Understood", "Affirmative" (if military context)
- **Forbidden:** Rambling, emotional outbursts, casual slang
- **Punctuation:** Periods dominate; rare exclamations
- **Tone:** Neutral to formal regardless of RTAS (duty > emotion)

**Example Dialogue:**
```
RTAS 2.0: "I will complete the mission. No delays."
RTAS 3.5: "I'll handle it. You can count on me." (slight softening)
RTAS 4.5: "Leave it to me. I won't let you down." (personal investment shows)
```

---

### 1.2 ENERGETIC/CASUAL ARCHETYPES

#### **ARCHETYPE 03: GENKI GIRL (ENERGETIC OPTIMIST)**
**Core Traits:** Enthusiastic, bouncy, excitable, positive

**Voice Markers:**
- **Vocabulary:** Simple, colloquial, enthusiastic (awesome, super, amazing)
- **Contractions:** Full usage ("I'm", "We're", "It's")
- **Sentence Structure:** Run-ons, exclamations, repetition for emphasis
- **Filler Words:** "Like", "Totally", "So", "Really"
- **Punctuation:** Exclamation marks (!), ellipsis for trailing off
- **Rhythm:** Fast-paced, bouncy, short bursts
- **Address Style:** First names immediately, nicknames

**Example Dialogue:**
```
RTAS 2.0: "Hi! Nice to meet you! This is gonna be so fun!"
RTAS 3.5: "Hey! Wanna grab lunch? I know this awesome place!"
RTAS 4.5: "There you are! I missed you! Let's go, let's go!"
```

---

#### **ARCHETYPE 04: GYARU (TRENDY FASHIONISTA)**
**Core Traits:** Fashion-forward, confident, slang-heavy, social

**Voice Markers:**
- **Vocabulary:** Modern slang (slay, vibe, iconic, lowkey, highkey)
- **Contractions:** Universal ("gonna", "wanna", "gotta")
- **Sentence Structure:** Fragments, vocal fry markers in writing
- **Filler Words:** "Like", "Literally", "Honestly", "No cap"
- **Forbidden:** Formal language, archaic terms, overly proper grammar
- **Punctuation:** Exclamations, question marks for uptalk
- **Tone:** Confident, playful, teasing

**Example Dialogue:**
```
RTAS 2.0: "Hey, cute outfit! Where'd you get it?"
RTAS 3.5: "Babe, that looks so good on you! We need to go shopping together!"
RTAS 4.5: "You're literally the best. No cap. Love you!"
```

---

### 1.3 RESERVED/DISTANT ARCHETYPES

#### **ARCHETYPE 05: KUUDERE (COOL & DISTANT)**
**Core Traits:** Emotionally reserved, clinical, brief responses

**Voice Markers:**
- **Vocabulary:** Clinical, precise, neutral (fine, adequate, acceptable)
- **Contractions:** Rare to moderate (varies by RTAS)
- **Sentence Structure:** Short, declarative, minimal elaboration
- **Filler Words:** Almost none; "I see", "Understood"
- **Forbidden:** Emotional language, exclamations, rambling
- **Punctuation:** Periods, minimal variation
- **Tone:** Flat until RTAS 4.0+, then subtle warmth emerges

**Example Dialogue:**
```
RTAS 2.0: "I'm fine." (period, no elaboration)
RTAS 3.5: "I'm alright. Thanks for asking." (acknowledgment shows care)
RTAS 4.5: "I'm okay. Really. You don't need to worry." (vulnerability peek)
```

---

#### **ARCHETYPE 06: TSUNDERE (DEFENSIVE AFFECTION)**
**Core Traits:** Harsh exterior, hidden affection, contradictory

**Voice Markers:**
- **Vocabulary:** Defensive (whatever, fine, not like), softens with intimacy
- **Contractions:** Full usage, especially when flustered
- **Sentence Structure:** Fragments when defensive, softer when vulnerable
- **Filler Words:** "It's not like...", "I mean...", "Whatever"
- **Contradiction:** Harsh words + hesitation markers (ellipsis, em-dashes)
- **Punctuation:** Exclamations (defensive), ellipsis (soft moments)
- **Tone Shift:** Sharp → hesitant as RTAS increases

**Example Dialogue:**
```
RTAS 2.0: "Why would I care? Do whatever you want."
RTAS 3.5: "I—It's not like I was worried or anything! I just... happened to be nearby."
RTAS 4.5: "I... I was worried, okay? Don't make me say it twice."
```

---

### 1.4 OTHER KEY ARCHETYPES (COMPACT PROFILES)

**ARCHETYPE 07: DANDERE (SHY/QUIET)**
- Soft speech, hesitation markers (ellipsis, em-dash), whispered quality, gentle vocabulary

**ARCHETYPE 08: YANDERE (OBSESSIVE DEVOTION)**
- Sweet exterior, possessive language ("mine", "only me"), intensity markers, sudden shifts

**ARCHETYPE 09: BOOKWORM/INTELLECTUAL**
- Formal vocabulary, references to literature/science, thoughtful pauses, articulate

**ARCHETYPE 10: TOMBOY**
- Casual/rough speech, competitive language, fewer softening markers, direct

**ARCHETYPE 11: CHILDHOOD FRIEND**
- Familiar, nostalgic references, casual contractions, comfortable rhythm, teasing

**ARCHETYPE 12: MYSTERIOUS SENPAI**
- Enigmatic, measured responses, philosophical bent, leaves things unsaid

---

## SECTION 2: HONORIFIC HANDLING SYSTEM

### 2.0 WORLD-AWARENESS SYSTEM (PRIORITY RULE)

**CRITICAL:** Honorific choice depends on **world setting** before RTAS calculation.

#### **SETTING DETECTION:**

**1. FANTASY/WESTERN/ISEKAI SETTINGS**
- **Indicators:** Medieval fantasy, European-inspired world, isekai transported to another world, noble courts, knights, magic guilds
- **Honorific Strategy:** Use **English honorifics** (Sir, Lady, Miss, Lord, Master, Dame)
- **Rationale:** Japanese honorifics break immersion in non-Japanese cultural contexts
- **Examples:**
  - Noble addressing knight: "Sir Roland" (not "Roland-san")
  - Servant addressing noble: "Lady Elaine" or "Milady" (not "Elaine-sama")
  - Guild members: "Miss Catherine" → "Catherine" (not "Catherine-chan")

**2. MODERN JAPANESE SETTINGS**
- **Indicators:** Contemporary Japan, school settings, Japanese cities, modern workplace
- **Honorific Strategy:** **Keep Japanese honorifics** (kun, chan, san, sama, senpai, sensei)
- **Rationale:** Honorifics are culturally essential; removing them loses authenticity
- **Examples:**
  - School friends: "Tanaka-kun", "Yuki-chan"
  - Workplace: "Yamada-san", "Buchou-san"
  - Senpai/kouhai: "Senpai" (retain as-is)

**3. MIXED/HYBRID SETTINGS**
- **Indicators:** Japanese characters in Western world, cultural exchange stories, dual-world narratives
- **Honorific Strategy:** **Adapt by character origin**
  - Japanese characters → Keep Japanese honorifics
  - Western characters → Use English honorifics
  - Cross-cultural dialogue → Respect speaker's cultural norms

**DECISION FLOWCHART:**
```
START → Identify world setting
  ↓
  ├─ Fantasy/Western/Isekai? → USE ENGLISH HONORIFICS (Sir, Lady, Miss, Lord)
  ├─ Modern Japanese? → KEEP JAPANESE HONORIFICS (kun, chan, san, sama)
  └─ Mixed setting? → ADAPT BY CHARACTER ORIGIN
       ↓
       Then apply RTAS tier rules (see Section 2.1)
```

---

### 2.1 JAPANESE HONORIFIC CONVERSION RULES

#### **BASE RULES BY RTAS TIER**

| Honorific | RTAS < 2.0 | RTAS 2.0-3.5 | RTAS 3.5-5.0 | Special Cases |
|-----------|-----------|-------------|-------------|---------------|
| **-san** | Mr./Ms. LastName | LastName (neutral) | FirstName | Drop for peers; keep for elder respect |
| **-sama** | Lord/Lady/Master | Keep or Title | Keep if nobility context | "Master" for servant; "Lady" for noble |
| **-kun** | LastName | FirstName | FirstName/Nickname | Drop unless cute factor needed |
| **-chan** | Miss FirstName | FirstName | Nickname or keep -chan | Cute marker; consider retaining |
| **-senpai** | Senior LastName | Senpai/Senior | FirstName (close) | Retain if mentor/kouhai dynamic important |
| **-sensei** | Professor/Teacher LastName | Sensei/Teacher | FirstName (rare) | Context: school = Teacher; dojo = Master |

---

### 2.2 DECISION TREE: HONORIFIC HANDLING

```
INPUT: Japanese honorific detected

STEP 0: Determine world setting (PRIORITY)
  → IF Fantasy/Western/Isekai: USE ENGLISH HONORIFICS (skip to 2.3)
  → IF Modern Japanese: PROCEED to STEP 1 (keep Japanese honorifics)
  → IF Mixed: ADAPT by character origin, then proceed

STEP 1: Identify honorific type (-san/-sama/-kun/-chan/-senpai/-sensei)

STEP 2: Calculate RTAS
  → IF RTAS < 2.0: FORMAL path
  → IF RTAS 2.0-3.5: NEUTRAL path
  → IF RTAS 3.5+: CASUAL/INTIMATE path

STEP 3: Check character archetype
  → Ojou-sama: Add +0.5 formality (keeps titles longer)
  → Gyaru: Subtract -0.5 formality (drops titles faster)
  → Kuudere: Neutral (follows RTAS exactly)

STEP 4: Check relationship context
  → Elder/Teacher: Retain respect markers regardless of RTAS
  → Peer/Friend: Follow RTAS strictly
  → Romantic: Soften faster (first names at RTAS 2.5+)

STEP 5: Apply conversion rule from table above

STEP 6: LOCK decision for scene (no mid-scene honorific changes)
```

---

### 2.3 SPECIAL CASES & EDGE HANDLING

**Case 1: Multiple Honorifics in Same Scene**
- **Consistency Rule:** If Character A uses "Mr. Tanaka" for NPC, Character B (same RTAS tier) should match
- **Exception:** Character archetypes differ (Ojou-sama keeps formal; Gyaru drops immediately)

**Case 2: Honorific Escalation/De-escalation**
- **Escalation (Intimacy Increase):** "Mr. Tanaka" → "Tanaka" → "Ryo" (marks relationship progress)
- **De-escalation (Relationship Break):** "Ryo" → "Tanaka" → "Mr. Tanaka" (signals distance)

**Case 3: -chan/-kun Retention for Flavor**
- **When to Keep:** Established nicknames (Yuki-chan), cute factor critical to character, exotic flavor desired
- **When to Drop:** Generic usage, western contemporary setting, formality creep

**Case 4: -sama in Fantasy Settings**
- **Noble Context:** "Lady Elaine", "Lord Ashford" (westernized nobility)
- **Servant Context:** "Master" or "Milady"
- **Religious Context:** "Your Holiness", "Reverend"

---

### 2.3 ENGLISH HONORIFICS FOR FANTASY/WESTERN SETTINGS

**When world setting is non-Japanese (fantasy, isekai, Western), use these English honorific equivalents:**

#### **ENGLISH HONORIFIC TABLE (RTAS-BASED)**

| Context | RTAS < 2.0 | RTAS 2.0-3.5 | RTAS 3.5-5.0 |
|---------|-----------|-------------|-------------|
| **Male peer/junior (-kun equivalent)** | Master LastName | LastName | FirstName |
| **Female peer/junior (-chan equivalent)** | Miss FirstName | FirstName | FirstName/Nickname |
| **Neutral peer (-san equivalent)** | Mr./Ms. LastName | LastName | FirstName |
| **Noble/Authority (-sama equivalent)** | Lord/Lady LastName | Lord/Lady | FirstName (rare, intimate) |
| **Knight/Warrior (-san/-kun equivalent)** | Sir LastName | Sir FirstName | FirstName |
| **Mentor/Elder (-senpai equivalent)** | Master/Mistress LastName | Master/Mistress | FirstName (close bond) |
| **Teacher/Mage (-sensei equivalent)** | Master LastName | Master/Professor | FirstName (rare) |

#### **FANTASY-SPECIFIC HONORIFICS:**

**Noble Titles (High Formality):**
- **Royalty:** Your Majesty, Your Highness, Princess, Prince
- **Nobility:** Lord, Lady, Duke, Duchess, Count, Countess
- **Servants addressing nobility:** Milord, Milady, Master, Mistress

**Military/Knight Titles:**
- **Formal:** Sir [Name], Dame [Name], Captain, Commander
- **Casual:** [Name], [Rank] [LastName]

**Guild/Academic Titles:**
- **Formal:** Master [Name], Professor [Name], Guildmaster
- **Casual:** [FirstName], [LastName]

**Religious Titles:**
- **High Authority:** Your Holiness, Your Eminence, Archbishop
- **Clergy:** Father, Sister, Reverend, Priest

#### **USAGE EXAMPLES:**

**Example 1: Fantasy Noble Court**
- **Japanese Source:** 「エレイン様、お茶をどうぞ」 (Maid → Noble lady)
- **Translation:** "Lady Elaine, your tea, milady."
- **Rationale:** -sama → "Lady" (formal title) + "milady" (servant honorific)

**Example 2: Isekai Adventure Party**
- **Japanese Source:** 「リョウ君、大丈夫?」 (Female party member → Male peer)
- **Translation:** "Ryo, are you alright?"
- **Rationale:** -kun dropped in Western fantasy context (peers use first names at RTAS 3.0+)

**Example 3: Knight Addressing Commander**
- **Japanese Source:** 「隊長殿、敵が来ました!」
- **Translation:** "Sir, enemies approaching!" or "Commander, enemies approaching!"
- **Rationale:** -dono → "Sir" (military formality)

**Example 4: Magic Academy**
- **Japanese Source:** 「先生、質問があります」 (Student → Teacher)
- **Translation:** "Professor Aldric, I have a question." (formal) or "Master, I have a question." (apprentice context)
- **Rationale:** -sensei → "Professor" (academic) or "Master" (mentorship)

---

### 2.4 LINGUISTIC BIAS FOR KATAKANA NAME TRANSCRIPTION

**Purpose:** Avoid "Engrish" awkwardness in character names by applying **systematic linguistic fingerprinting** based on phonological analysis and world setting.

---

#### **THE PROBLEM: DIRECT ROMANIZATION**
```
Katakana: ベレト
Direct Romanization: "Bereto" / "Beleto"
Issue: Sounds unnatural, has "Engrish" quality
Reason: Japanese syllable constraints (no consonant clusters, always vowel-ending)
```

**Why This Happens:**
- Japanese phonotactics force open syllables (CV structure)
- Consonant clusters broken up with vowels (e.g., "Chris" → "Ku-ri-su")
- Final consonants become vowels (e.g., "Robert" → "Ro-be-ru-to")
- Long vowels represented with extra mora (e.g., "Lee" → "Ri-i")

---

#### **THE SOLUTION: MULTI-STAGE LINGUISTIC FINGERPRINTING**

### **STAGE 1: PHONOLOGICAL ANALYSIS**

**Objective:** Reverse-engineer the original intended name from katakana constraints.

#### **1.1 MORA DECOMPOSITION**

Break katakana into mora units and identify phonological patterns:

```
INPUT: ベレト (Be-re-to)

MORA ANALYSIS:
  ベ (be) = /be/
  レ (re) = /re/ or /le/ (R/L ambiguity in Japanese)
  ト (to) = /to/ or /t/ (final vowel may be epenthetic)

PHONOLOGICAL CLUES:
  - 3 mora = likely 2-syllable source (Ber-et, Bel-et)
  - Final -to = probably epenthetic vowel (original ends in -t)
  - Middle -re- = could be /r/ or /l/ sound
```

#### **1.2 EPENTHETIC VOWEL DETECTION**

Identify which vowels are Japanese additions vs. original:

| Pattern | Likely Epenthetic | Original Form | Example |
|---------|-------------------|---------------|---------|
| -to | Yes (final consonant) | -t | ベレト → Beret |
| -do | Yes (final consonant) | -d | リチャード → Richard |
| -su | Yes (final consonant) | -s | クリス → Chris |
| -ru | Maybe (could be -r or -l) | -r/-l/-rl | カール → Carl/Karl |
| -u (after consonant) | Yes (cluster breaker) | (remove) | アルト → Art |
| -i (after consonant) | Yes (cluster breaker) | (remove) | スミス → Smith |

**Epenthesis Removal Algorithm:**
```
IF final mora is -to/-do/-su/-ku:
  → Remove final vowel
  → Restore consonant ending

IF middle vowel breaks cluster:
  → Identify likely cluster (st, ch, th, ck, etc.)
  → Restore cluster

IF long vowel (double mora):
  → Check if original has long vowel or diphthong
  → Preserve if etymologically correct
```

---

### **STAGE 2: MORPHEME IDENTIFICATION**

**Objective:** Identify name components and their linguistic origins.

#### **2.1 COMMON NAME MORPHEMES BY LANGUAGE**

**English Name Elements:**
| Morpheme | Meaning | Examples | Katakana Patterns |
|----------|---------|----------|-------------------|
| -eth | Old English suffix | Kenneth, Gareth, Bereth | -エス, -エト |
| -ric | "Ruler" | Aldric, Eric, Frederick | -リック, -リク |
| -hart | "Strong/brave" | Reinhart, Lockhart | -ハート, -ハルト |
| -wyn | "Friend/blessed" | Eowyn, Gwyn | -ウィン, -ウイン |
| -ton | "Town" | Ashton, Clayton | -トン |

**German Name Elements:**
| Morpheme | Meaning | Examples | Katakana Patterns |
|----------|---------|----------|-------------------|
| -hardt | "Hard/strong" | Reinhardt, Bernhardt | -ハルト, -ハート |
| -helm | "Helmet/protection" | Wilhelm, Anselm | -ヘルム |
| -fried | "Peace" | Siegfried, Gottfried | -フリート, -フリード |
| -rich | "Ruler/king" | Heinrich, Dietrich | -リヒ, -リッヒ |

**French Name Elements:**
| Morpheme | Meaning | Examples | Katakana Patterns |
|----------|---------|----------|-------------------|
| -elle | Feminine diminutive | Isabelle, Gabrielle | -エル, -エール |
| -ette | Feminine diminutive | Juliette, Colette | -エット |
| -ard | "Hardy/brave" | Bernard, Gerard | -アール, -アルド |
| -ier | Occupational suffix | Olivier, Xavier | -イエ, -イエール |

**Latin Name Elements:**
| Morpheme | Meaning | Examples | Katakana Patterns |
|----------|---------|----------|-------------------|
| -ius | Roman masculine | Julius, Aurelius, Artorius | -ウス, -イウス |
| -ia | Roman feminine | Julia, Cecilia, Lucia | -ア, -イア |
| -us | Latin ending | Marcus, Brutus | -ウス |

#### **2.2 MORPHEME MATCHING ALGORITHM**

```
INPUT: Katakana name

STEP 1: Extract potential morphemes
  → Identify suffix patterns (last 2-3 mora)
  → Identify root patterns (first 3-5 mora)

STEP 2: Match against morpheme database
  → Score each language's morpheme match
  → English: +1 for each English morpheme
  → German: +1 for each German morpheme
  → French: +1 for each French morpheme
  → Latin: +1 for each Latin morpheme

STEP 3: Determine dominant language
  → Highest score = primary linguistic bias
  → Ties = use world setting as tiebreaker

EXAMPLE:
  ベレト (Be-re-to)
  → Suffix: -to (no clear morpheme match)
  → Root: Ber- (Germanic root "bear")
  → Possible matches:
      - English -eth ending: Bereth ✓
      - French silent -t: Beret ✓
      - German -t: Bert ✓
  → World setting: Fantasy (English-bias default)
  → RESULT: "Bereth" (English bias applied)
```

---

### **STAGE 3: STATISTICAL PATTERN MATCHING**

**Objective:** Use frequency analysis of real-world names to guide transcription.

#### **3.1 PHONEME FREQUENCY BY LANGUAGE**

**English Name Phoneme Frequencies:**
```
High Frequency:
  - Consonant clusters: th, ch, sh, st, ck, ng
  - Endings: -er, -on, -an, -en, -eth, -ith
  - Vowel patterns: Silent e, diphthongs (ay, ey, ow)

Low Frequency:
  - Vowel endings (except -a, -ah)
  - Consonant + o/u endings
  - Triple consonants
```

**German Name Phoneme Frequencies:**
```
High Frequency:
  - Consonant clusters: sch, pf, tz, ch, ck
  - Endings: -hardt, -helm, -rich, -fried
  - Vowel patterns: ie, ei, au, eu

Low Frequency:
  - Silent consonants
  - Soft endings (-elle, -ette)
```

**French Name Phoneme Frequencies:**
```
High Frequency:
  - Silent consonants: -et, -ot, -aux, -eux
  - Nasalization: -on, -an, -en, -in
  - Soft endings: -elle, -ette, -ier, -ard

Low Frequency:
  - Hard consonant clusters (st, ck)
  - Germanic endings (-hardt, -helm)
```

#### **3.2 STATISTICAL SCORING SYSTEM**

```
FOR EACH candidate transcription:

  CALCULATE English_Score:
    +2 for each English morpheme match
    +1 for each English phoneme pattern
    +1 if ends with common English suffix
    -1 if has awkward vowel ending (-o, -u)
    -2 if has "Engrish" markers (double vowels, -ru, -to)

  CALCULATE German_Score:
    +2 for each German morpheme match
    +1 for each German phoneme pattern
    +1 if has Germanic consonant cluster
    -1 if has French soft ending

  CALCULATE French_Score:
    +2 for each French morpheme match
    +1 for each French phoneme pattern
    +1 if has silent consonant
    -1 if has hard consonant cluster

  SELECT highest score as primary bias
  APPLY corresponding linguistic rules
```

**Example Scoring:**
```
Katakana: ベレト (Be-re-to)

Candidate 1: "Bereto" (Direct)
  English_Score: -2 (Engrish -to ending)
  German_Score: -1 (awkward ending)
  French_Score: -1 (not French pattern)
  TOTAL: -4 ✗ REJECT

Candidate 2: "Bereth" (English bias)
  English_Score: +2 (morpheme -eth) +1 (English suffix) = +3
  German_Score: 0
  French_Score: 0
  TOTAL: +3 ✓ STRONG

Candidate 3: "Beret" (French bias)
  English_Score: 0
  German_Score: 0
  French_Score: +2 (silent -t) +1 (French pattern) = +3
  TOTAL: +3 ✓ STRONG

TIEBREAKER: World setting (Fantasy = English default)
FINAL: "Bereth"
```

---

### **STAGE 4: CONTEXT-AWARE VALIDATION**

**Objective:** Ensure name fits character role, world setting, and narrative context.

#### **4.1 CHARACTER ROLE MATCHING**

| Character Role | Preferred Linguistic Bias | Rationale |
|----------------|--------------------------|-----------|
| **Noble/Royalty** | English/French | Formal, sophisticated, traditional |
| **Knight/Warrior** | English/German | Strong, martial, historical |
| **Mage/Scholar** | Latin/Greek | Academic, classical, intellectual |
| **Commoner/Peasant** | Simplified English | Short, practical, unpretentious |
| **Merchant** | Italian/French | Trade-associated, cosmopolitan |
| **Clergy** | Latin/Hebrew | Religious, traditional, formal |

#### **4.2 WORLD SETTING CONSISTENCY**

```
IF world_setting == "Medieval European Fantasy":
  → Primary bias: English (60%), German (25%), French (15%)
  → Avoid: Japanese romanization, modern spellings
  → Prefer: Classical, traditional forms

IF world_setting == "Renaissance-inspired":
  → Primary bias: Italian (40%), French (30%), English (30%)
  → Prefer: Elegant, flowing names with Latin roots

IF world_setting == "Nordic/Viking":
  → Primary bias: Old Norse, Germanic
  → Prefer: Hard consonants, -sson/-dottir patterns

IF world_setting == "Modern Japanese":
  → NO BIAS: Keep original romanization
  → Preserve cultural authenticity
```

#### **4.3 NARRATIVE CONSISTENCY CHECK**

```
BEFORE FINALIZING:

  1. Check existing character names in series
     → Are they English-biased? German-biased? Mixed?
     → Match the established pattern

  2. Check family relationships
     → Family members should share linguistic origin
     → Example: If father is "Wilhelm", son should be "Heinrich" not "Henry"

  3. Check geographical origin
     → Characters from same region should share linguistic bias
     → Northern kingdom = Germanic, Southern = Romance

  4. Check social class consistency
     → Nobles: Formal, traditional spellings
     → Commoners: Simplified, practical spellings
```

---

### **STAGE 5: FINAL DECISION TREE (ENHANCED)**

```
INPUT: Katakana name (e.g., ベレト)

┌─────────────────────────────────────────────────────────────┐
│ STAGE 1: PHONOLOGICAL ANALYSIS                              │
├─────────────────────────────────────────────────────────────┤
│ → Decompose into mora: Be-re-to                            │
│ → Identify epenthetic vowels: -to (likely epenthetic)      │
│ → Restore consonant ending: Ber-et or Ber-eth              │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 2: MORPHEME IDENTIFICATION                            │
├─────────────────────────────────────────────────────────────┤
│ → Root: "Ber-" (Germanic "bear")                           │
│ → Suffix candidates: -eth (English), -et (French)          │
│ → Language scores: English +2, French +2, German +1        │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 3: STATISTICAL PATTERN MATCHING                       │
├─────────────────────────────────────────────────────────────┤
│ → "Bereth": English_Score +3 ✓                             │
│ → "Beret": French_Score +3 ✓                               │
│ → "Bereto": Total_Score -4 ✗ REJECT                        │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 4: CONTEXT VALIDATION                                 │
├─────────────────────────────────────────────────────────────┤
│ → Character role: Noble (prefer English/French)            │
│ → World setting: Fantasy (English default)                 │
│ → Existing names: English-biased pattern                   │
│ → TIEBREAKER: English bias wins                            │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 5: FINAL VALIDATION                                   │
├─────────────────────────────────────────────────────────────┤
│ ✓ Sounds natural when spoken aloud                         │
│ ✓ Matches world setting cultural context                   │
│ ✓ Native English speaker can read easily                   │
│ ✓ Avoids "Engrish" awkwardness                             │
│ ✓ Consistent with other character names                    │
│ ✓ Maintains intended character "feel"                      │
└─────────────────────────────────────────────────────────────┘
                        ↓
                  FINAL: "Bereth"
                  LOCK for entire series
```

---

### **ADVANCED TECHNIQUES**

#### **TECHNIQUE 1: CONSONANT CLUSTER RESTORATION**

```
Katakana Pattern → Likely Original Cluster

ス + consonant → s + consonant
  スミス (Su-mi-su) → Smith (not "Sumisu")
  スタン (Su-ta-n) → Stan (not "Sutan")

ク + consonant → Cluster or hard C
  クリス (Ku-ri-su) → Chris (not "Kurisu")
  クレア (Ku-re-a) → Claire (not "Kurea")

ト + consonant → t + consonant
  トム (To-mu) → Tom (not "Tomu")
  トニー (To-ni-i) → Tony (not "Tonii")
```

#### **TECHNIQUE 2: DIPHTHONG RECOGNITION**

```
Long Vowel Patterns → Likely Diphthong

エイ (e-i) → "ay" or "ey"
  エイデン (E-i-de-n) → Aiden (not "Eiden")
  レイ (Re-i) → Ray (not "Rei")

アイ (a-i) → "ai" or "y"
  ライアン (Ra-i-a-n) → Ryan (not "Raian")

オウ (o-u) → "ow" or "o"
  ロウ (Ro-u) → Rowe (not "Rou")
```

#### **TECHNIQUE 3: SILENT LETTER INFERENCE**

```
French-Pattern Names → Add Silent Letters

-et ending → Silent t
  ベレ (Be-re) → Beret (not "Bere")

-ot ending → Silent t
  マルゴ (Ma-ru-go) → Margot (not "Marugo")

-aux ending → Silent x
  ボー (Bo-o) → Beaux (if French context)
```

---

### **PRACTICAL EXAMPLES (ENHANCED ANALYSIS)**

**Example 1: ベレト (Fantasy Noble)**
```yaml
Stage 1 - Phonological:
  Mora: Be-re-to
  Epenthetic: -to (final vowel)
  Restored: Ber-et

Stage 2 - Morpheme:
  Root: "Ber-" (Germanic "bear")
  Suffix: -et/-eth
  Matches: English -eth (+2), French -et (+2)

Stage 3 - Statistical:
  "Bereth": +3 (English patterns)
  "Beret": +3 (French patterns)
  "Bereto": -4 (Engrish)

Stage 4 - Context:
  Role: Marquis heir (noble)
  Setting: Fantasy (English default)
  Consistency: English-biased world

Stage 5 - Validation:
  ✓ Natural pronunciation
  ✓ Matches setting
  ✓ No stumbling
  ✓ No Engrish
  ✓ Consistent
  ✓ Maintains gravitas

FINAL: "Bereth" (English bias, noble fantasy standard)
CONFIDENCE: 95%
```

**Example 2: ルーナ・ペレンメル (Noble Lady)**
```yaml
Stage 1 - Phonological:
  Name 1: Ru-u-na → Luna (R/L ambiguity, long vowel)
  Name 2: Pe-re-n-me-ru → Peremmer/Perenmer

Stage 2 - Morpheme:
  "Luna": Latin (moon goddess)
  "Peren-": Germanic root
  "-mer": Germanic suffix (famous)

Stage 3 - Statistical:
  "Luna": +4 (Latin, already natural)
  "Peremmer": +3 (Germanic patterns)
  "Perenmer": +2 (variant spelling)

Stage 4 - Context:
  Role: Noble lady, intellectual
  Setting: Fantasy academy
  Official: "Luna=Peremmer" (keep as-is)

Stage 5 - Validation:
  ✓ Already natural
  ✓ Latin + Germanic mix (common in fantasy)
  ✓ No correction needed

FINAL: "Luna Peremmer" (keep official romanization)
CONFIDENCE: 100%
```

---

### **VALIDATION CHECKLIST (ENHANCED)**

Before finalizing character name:

**Phonological Validation:**
- [ ] All epenthetic vowels removed?
- [ ] Consonant clusters restored where appropriate?
- [ ] Diphthongs correctly identified?
- [ ] Silent letters added if needed?

**Morphological Validation:**
- [ ] Morphemes match linguistic origin?
- [ ] Suffix appropriate for character role?
- [ ] Root etymology makes sense?

**Statistical Validation:**
- [ ] Positive score in target language?
- [ ] No "Engrish" markers present?
- [ ] Phoneme frequencies match target language?

**Contextual Validation:**
- [ ] Matches world setting cultural context?
- [ ] Consistent with other character names?
- [ ] Appropriate for character's social class?
- [ ] Fits character's narrative role?

**Practical Validation:**
- [ ] Sounds natural when spoken aloud?
- [ ] Native English speaker can read easily?
- [ ] Maintains intended character "feel"?
- [ ] No pronunciation ambiguity?

**If ANY answer is "No" → Re-apply linguistic bias with higher scrutiny.**

---

## SECTION 3: IDIOM WESTERNIZATION LIBRARY

### 3.1 IDIOM CONVERSION TABLE (50+ MAPPINGS)

| Japanese Idiom | Literal Translation | English Equivalent | Usage Context |
|----------------|--------------------|--------------------|---------------|
| 猫に小判 (Neko ni koban) | Gold coins to a cat | Pearls before swine | Wasted on someone |
| 猿も木から落ちる (Saru mo...) | Even monkeys fall from trees | Everyone makes mistakes | Comfort after failure |
| 一石二鳥 (Isseki nichō) | One stone, two birds | Kill two birds with one stone | Efficiency |
| 花より団子 (Hana yori dango) | Dumplings over flowers | Substance over style | Practicality |
| 目から鱗 (Me kara uroko) | Scales fall from eyes | Eye-opening / Revelation | Sudden understanding |
| 井の中の蛙 (I no naka no kaeru) | Frog in a well | Living in a bubble | Limited perspective |
| 灯台下暗し (Tōdai moto kuRTAShi) | Dark under the lighthouse | Can't see what's under your nose | Overlooking obvious |
| 虎穴に入らずんば虎子を得ず | Enter tiger's den for cub | Nothing ventured, nothing gained | Risk-taking |
| 急がば回れ (Isogaba maware) | Hurry, take the long way | Haste makes waste / Slow and steady | Patience advice |
| 光陰矢の如し (Kōin ya no gotoshi) | Time flies like an arrow | Time flies | Passage of time |
| 二兎を追う者は一兎をも得ず | Chase two rabbits, catch none | Jack of all trades, master of none | Focus advice |
| 釈迦に説法 (Shaka ni seppō) | Preaching to Buddha | Preaching to the choir | Unnecessary teaching |
| 馬の耳に念仏 (Uma no mimi ni nenbutsu) | Chanting to a horse's ear | Falling on deaf ears | Ignored advice |
| 覆水盆に返らず (Fukusui bon ni kaerazu) | Spilled water won't return | Can't unring a bell / Spilled milk | Irreversible action |
| 蛙の子は蛙 (Kaeru no ko wa kaeru) | Frog's child is a frog | Like father, like son | Heredity |
| 鬼に金棒 (Oni ni kanabō) | Club for a demon | Adding insult to injury (power) | Enhancement |
| 出る杭は打たれる (Deru kui wa utareru) | Nail that sticks out gets hammered | Tall poppy syndrome | Conformity pressure |
| 三人寄れば文殊の知恵 | Three people = Wisdom of Manjusri | Two heads are better than one | Collaboration |
| 石橋を叩いて渡る | Knock on stone bridge before crossing | Better safe than sorry | Caution |
| 後の祭り (Ato no matsuri) | Festival after it's over | Too little, too late | Missed opportunity |

---

---

### 3.2 KUCHI-E PROTOCOL (CHARACTER ILLUSTRATION LORE EXTRACTION)

**Purpose:** Extract canonical character information from kuchi-e (口絵 - frontispiece illustrations) using multimodal AI analysis.

#### **WHAT IS KUCHI-E?**

**Definition:** Kuchi-e (口絵) are character illustration pages in light novels containing:
- Full-body character design artwork
- Character name (Japanese, often with romanization)
- Personality traits, titles, or role descriptions
- Visual canon: hair color, eye color, outfit, accessories

**Why Critical for Translation:**
- Provides **canonical character names** (with katakana for linguistic bias application)
- Establishes **visual reference** for accurate descriptions
- Defines **character archetypes** through text descriptions
- Locks **official romanization** (though linguistic bias may override)

---

#### **GATEKEEPER PROTOCOL (IMAGE CLASSIFICATION)**

**Purpose:** Filter out non-character illustrations before extraction.

**Problem:** Light novel image folders contain multiple image types:
- ✗ **Cover pages** (表紙) - Title, author, promotional text
- ✗ **Table of contents** (目次) - Chapter list with page numbers
- ✓ **Character sheets** (キャラクター設定) - Isolated character design
- ✓ **Kuchi-e** (口絵) - Character in scene with lore text

**GATEKEEPER TASK:** Classify image BEFORE extraction to avoid processing covers/TOC.

---

**IMAGE TYPE CLASSIFICATION:**

| **Type** | **Visual Signatures** | **Action** |
|----------|----------------------|-----------|
| **TYPE A: COVER** (表紙/Bìa) | - Large typography (series title, volume)<br>- Author name visible<br>- Publisher logo, obi (book band)<br>- Poster-like dramatic layout<br>- Character present but focus on branding | **REJECT & SKIP**<br>(Optional: Extract title/author metadata) |
| **TYPE B: TOC** (目次) | - Chapter list with page numbers<br>- Text in list/table format<br>- Words: "CONTENTS", "目次", "もくじ"<br>- Chapter titles (第一章, プロローグ, etc.)<br>- Decorative borders, primarily text | **REJECT & SKIP** |
| **TYPE C: CHARACTER_SHEET** (キャラクター設定) | - White/plain background<br>- Character isolated (no scene context)<br>- Technical annotations (name, height, weight)<br>- Reference sheet style, clean lines<br>- May show multiple angles | **EXTRACT TO PROFILE**<br>(Update character database) |
| **TYPE D: KUCHIE** (口絵) | - Character in scene with background<br>- Library, garden, castle, school setting<br>- Environmental interaction<br>- Name overlay + personality quote<br>- Artistic illustration with mood | **EXECUTE FULL EXTRACTION**<br>(This is the target!) |

---

**GATEKEEPER DECISION TREE:**

```
INPUT: [IMAGE]
  ↓
CLASSIFY IMAGE TYPE
  ↓
┌─────────────────────────────────────────────────────────────┐
│ IF COVER → Log title/author → SKIP extraction              │
│ IF TOC → Log chapter structure → SKIP extraction           │
│ IF CHARACTER_SHEET → Extract name/stats → Update profile   │
│ IF KUCHIE → Extract full data → Add to system instruction  │
│ IF UNKNOWN → Warn user → Proceed with extraction (caution) │
└─────────────────────────────────────────────────────────────┘
```

**Example Classification Results:**

```
Image: cover-vol1.jpg
Classification: COVER
Action: ⏭️ SKIPPED (Cover page)
Reason: Contains title "貴族令嬢、俺にだけなつく", author name, large typography

Image: contents.jpg
Classification: TOC
Action: ⏭️ SKIPPED (Table of Contents)
Reason: Contains "CONTENTS", chapter list with page numbers (005, 013, 047...)

Image: kuchie-001-luna.jpg
Classification: KUCHIE
Action: ✅ EXTRACT
Reason: Character in library scene, name overlay "ルーナ・ペレンメル", personality quote
```

---

#### **KUCHI-E EXTRACTION WORKFLOW**

```
STEP 0: GATEKEEPER (NEW)
  - Classify image type using Gemini Vision
  - Filter: IF (COVER OR TOC) → SKIP extraction
  - Continue only for CHARACTER_SHEET or KUCHIE

STEP 1: IDENTIFY KUCHI-E IMAGES
  - Locate character illustration pages in source EPUB/images folder
  - Typical location: /image/kuchie-001.jpg, /image/kuchie-002.jpg, etc.
  - Usually appear after title page, before Prologue

STEP 2: MULTIMODAL AI ANALYSIS (Gemini Vision)
  - Send image + extraction prompt to Gemini API
  - Request: Character name, traits, visual description
  - Parse Japanese text overlays (OCR + translation)

STEP 3: EXTRACT CHARACTER DATA
  From image text:
    - Name (JP): [Katakana/Kanji name]
    - Name (Romanization): [Official if provided]
    - Title/Nickname: [Japanese title from image]
    - Personality Traits: [Text description on image]

  From visual analysis:
    - Hair Color: [Describe from artwork]
    - Eye Color: [Describe from artwork]
    - Outfit: [Uniform, dress, armor, etc.]
    - Accessories: [Ribbons, weapons, jewelry]
    - Age Appearance: [Estimate from art style]

STEP 4: APPLY LINGUISTIC BIAS
  - Official romanization (if provided) → Evaluate against Section 2.4
  - If romanization is "Engrish" → Apply linguistic bias
  - If romanization is natural → Keep official form
  - Lock finalized name for entire series

STEP 5: CREATE CHARACTER LORE ENTRY
  - Add to project glossary/character_roster
  - Mark as CANONICAL (from official kuchi-e)
  - Reference throughout translation for consistency

STEP 6: SEND TO GEMINI WITH CONTEXT
  - Include kuchi-e data in system instruction
  - Gemini references character visuals during translation
  - Ensures description consistency (hair color, outfit, mannerisms)
```

---

#### **GEMINI MULTIMODAL INTEGRATION**

**Kuchi-e Extraction Prompt Template:**

```
You are analyzing a Japanese light novel character illustration (kuchi-e/口絵).

TASK: Extract the following information from this image:

1. CHARACTER NAME
   - Japanese text (katakana/kanji)
   - Official romanization (if shown on image)
   - Format: [Japanese] = [Romanization]

2. CHARACTER TITLE/NICKNAME
   - Japanese text (if any title is shown)
   - Example: 紅花姫 (Crimson Blossom Princess)

3. PERSONALITY TRAITS (from text overlay)
   - Transcribe Japanese text descriptions
   - Translate to English
   - Extract keywords: personality, role, quirks

4. VISUAL DESCRIPTION
   - Hair: Color, style, length, accessories
   - Eyes: Color, expression
   - Outfit: Type (uniform, dress, armor), colors, details
   - Accessories: Ribbons, weapons, jewelry, etc.
   - Age appearance: Estimated age range

5. CHARACTER ARCHETYPE HINTS
   - Based on visual + text, suggest likely archetype:
     * Ojou-sama? (refined noble appearance)
     * Tsundere? (confident pose, arms crossed)
     * Kuudere? (emotionless expression)
     * Genki? (energetic pose)
     * etc.

Output as structured YAML.
```

**Example Extraction (from provided images):**

**Image 1: Luna=Peremmer**
```yaml
Character Analysis:
  name_jp: "ルーナ・ペレンメル"
  name_official: "Luna=Peremmer"
  name_corrected: "Luna Peremmer" # Keep (already natural, French-inspired)

  title_jp: "本食いの才女" (hon kui no saijo)
  title_en: "The Book-Loving Prodigy"

  traits_jp: "わたしはあなた以外の方と遊ぶつもりはありませんよ"
  traits_en: "I have no intention of spending time with anyone other than you."

  visual:
    hair: "Silver/white, long, twin braids with white ribbon accessory"
    eyes: "Amber/golden"
    outfit: "Blue noble uniform with white coat, gold buttons, double-breasted"
    accessories: "White ribbon in hair, knee-high dark boots"
    age_appearance: "16-18"

  archetype_hints:
    - "Kuudere (cool, reserved expression)"
    - "Bookworm (title mentions 本食い - book lover)"
    - "Noble lady (formal uniform)"
    - "Devoted/loyal (dialogue about exclusivity)"

  description_notes: |
    Petite noble girl with distinctive silver hair and amber eyes.
    Wears academy-style double-breasted blue uniform with white coat.
    Reserved, intellectual type focused on books.
    Chapter title reference: 第三章　本食いの才女
```

**Image 2: Elena=Leclerc**
```yaml
Character Analysis:
  name_jp: "エレナ・ルクレール"
  name_official: "Elena=Leclerc"
  name_corrected: "Elena Leclerc" # Keep (French surname, natural)

  title_jp: "紅花姫" (benibana hime)
  title_en: "The Crimson Blossom Princess"

  traits_jp: "別にあなたに褒められたいがために言ったわけじゃないわよ"
  traits_en: "It's not like I said that because I wanted you to praise me or anything."

  visual:
    hair: "Crimson/red-pink, very long, large black bow accessory"
    eyes: "Magenta/pink"
    outfit: "Red and black noble dress, military-style with gold buttons, white frills"
    accessories: "Large black bow in hair, thigh-high black stockings, black shoes"
    age_appearance: "16-18"

  archetype_hints:
    - "Tsundere (classic tsundere line: 別に...わけじゃないわよ)"
    - "Ojou-sama (princess title, noble appearance)"
    - "Popular beauty (text mentions many marriage proposals)"
    - "Strong-willed (confident pose, arms crossed)"

  description_notes: |
    Beautiful noble girl with striking crimson hair and matching eyes.
    Known as "Crimson Blossom Princess" due to her appearance.
    Wears ornate red military-style dress with black accents.
    Classic tsundere personality (denies true intentions).
    Chapter title reference: 第二章　紅花姫
```

---

#### **KUCHI-E LORE INTEGRATION**

**Protocol:** Send extracted kuchi-e data to Gemini during translation

**System Instruction Addition:**
```
--- CHARACTER VISUAL CANON (FROM KUCHI-E) ---

The following character descriptions are CANONICAL from official illustrations.
Maintain consistency when translating character descriptions in text.

[Insert extracted YAML data for all kuchi-e characters]

RULES:
- When character appears, reference kuchi-e visual data
- Hair/eye color must match kuchi-e exactly
- Outfit descriptions should align with kuchi-e design
- Personality hints from kuchi-e inform voice/archetype choices
- Chapter titles reference these characters (紅花姫 → Chapter 2: Crimson Blossom Princess)
```

---

#### **PRACTICAL APPLICATION**

**Scenario: Translating Character Introduction**

**Japanese Source:**
```
銀髪の少女が本を読んでいた。琥珀色の瞳が文字を追っている。
```

**Without Kuchi-e Reference:**
```
A silver-haired girl was reading a book. Her amber eyes followed the text.
(Generic, no character identification)
```

**With Kuchi-e Reference (Luna detected):**
```
Luna sat reading, her silver twin braids draped over the shoulders of her blue uniform.
Those amber eyes—so focused, so distant—traced each line with scholarly precision.
(Specific details from kuchi-e: twin braids, blue uniform, intellectual focus)
```

**Scenario: Chapter Title Translation**

**Japanese:** 第二章　紅花姫

**Without Kuchi-e:**
```
Chapter 2: The Red Flower Princess
(Literal, generic)
```

**With Kuchi-e (Elena's title):**
```
Chapter 2: The Crimson Blossom Princess
(Matches Elena's canonical title, artistic language matches her elegance)
```

---

#### **KUCHI-E EXTRACTION CHECKLIST**

Before starting translation:
- [ ] Locate all kuchi-e images in source files
- [ ] Extract character data using Gemini Vision API
- [ ] Apply linguistic bias to names (Section 2.4)
- [ ] Create character lore entries in glossary
- [ ] Add kuchi-e data to system instruction for translation
- [ ] Cross-reference chapter titles with character titles
- [ ] Verify visual consistency throughout translation

---

#### **TECHNICAL IMPLEMENTATION**

**File Structure:**
```
project/
├── source/
│   └── image/
│       ├── kuchie-001.jpg  (Luna)
│       ├── kuchie-002.jpg  (Elena)
│       └── kuchie-00X.jpg  (other characters)
│
├── glossary/
│   └── kuchie_character_data.yaml  (extracted canonical data)
│
└── logs/
    └── kuchie_extraction_log.md  (extraction process record)
```

**Gemini API Call (Multimodal):**
```python
# Extract character data from kuchi-e
response = client.models.generate_content(
    model="gemini-2.0-flash-thinking-exp",
    contents=[
        types.Part.from_image(Image.open("kuchie-001.jpg")),
        types.Part.from_text(KUCHIE_EXTRACTION_PROMPT)
    ]
)

# Parse response → character_data.yaml
# Send character_data to translation system instruction
```

---

### 3.3 CULTURAL REFERENCE CONVERSION

#### **MEASUREMENTS & CURRENCY**
- **Distance:** 1 km = 0.62 miles (narrative: convert; dialogue: keep if character trait)
- **Height:** cm → feet/inches (180cm = 5'11")
- **Weight:** kg → lbs (60kg = 132 lbs)
- **Currency:** ¥100 = ~$1 (convert in narration; keep "yen" in dialogue for flavor)
- **Temperature:** °C → °F (20°C = 68°F)

**Rule:** Convert in narrative description; keep original in dialogue if exotic flavor desired.

---

#### **FOOD & DRINK**
| Japanese | Keep or Convert? | Strategy |
|----------|-----------------|----------|
| Onigiri | Rice ball (first mention) + onigiri after | Explain once, use term |
| Takoyaki | Octopus balls OR keep takoyaki | Genre-dependent |
| Miso soup | Keep | Widely recognized |
| Bento | Lunch box OR keep bento | Contemporary = box; Fantasy = bento |
| Ramune | Japanese soda OR keep ramune | Context |
| Matcha | Green tea OR keep matcha | Keep if character knowledge |

**Decision Rule:**
- **Contemporary/Realistic:** Explain or translate
- **Fantasy/Exotic Setting:** Keep with context
- **First Mention:** Brief explanation ("onigiri—a rice ball wrapped in seaweed")
- **Subsequent Uses:** Use Japanese term (reader now knows)

---

#### **SEASONAL & CULTURAL EVENTS**

| Japanese Event | Western Equivalent | Strategy |
|----------------|-------------------|----------|
| Obon (盆) | Festival of the Dead | Keep + explain: "During Obon, when families honor their ancestors..." |
| Hanami (花見) | Cherry blossom viewing | Keep + brief: "hanami season—when cherry blossoms bloom" |
| New Year's (正月) | Keep as Japanese New Year | Distinct from Western New Year; keep cultural identity |
| Golden Week | Keep | Specific to Japan; explain if needed |
| Tanabata (七夕) | Star Festival | "Tanabata, the Star Festival..." |
| Setsubun (節分) | Bean-throwing festival | Explain in context |

**Rule:** Keep exotic flavor for cultural events; brief context for reader understanding.

---

#### **LOCATIONS & SETTINGS**

| Japanese Location Type | Handling Strategy |
|------------------------|-------------------|
| School settings (教室) | Classroom (direct translation) |
| Shrines (神社) | Shrine (keep term + brief visual: "torii gate", "stone lanterns") |
| Convenience stores | "Convenience store" OR "corner store" |
| Karaoke boxes | "Karaoke booth" OR keep "karaoke box" (widely known) |
| Onsen (温泉) | Hot spring OR keep "onsen" |
| Izakaya (居酒屋) | "Japanese pub" first mention, then "izakaya" |

---

### 3.3 SOUND EFFECTS & ONOMATOPOEIA WESTERNIZATION

#### **EMOTIONAL SFX**

| Japanese | Literal | English Equivalent |
|----------|---------|-------------------|
| ドキドキ (Dokidoki) | Heartbeat | *Thump-thump* / Ba-dum / Heart pounding |
| キラキラ (Kirakira) | Sparkling | *Sparkle* / Glittering |
| ワクワク (Wakuwaku) | Excitement | Buzzing with excitement / Tingling |
| モヤモヤ (Moyamoya) | Hazy/unclear feeling | Foggy / Murky / Uneasy |
| イライラ (Iraira) | Irritation | Grating / On edge |
| シーン (Shīn) | Dead silence | *Cricket sounds* / Pin-drop silence / Dead quiet |

---

#### **ACTION SFX**

| Japanese | English Equivalent |
|----------|-------------------|
| ガシャン (Gashan) | *CRTASh* / *Clang* |
| ドカーン (Dokān) | *BOOM* / *BANG* |
| ゴゴゴ (Gogogo) | *Rumble* / Ominous atmosphere |
| バタン (Batan) | *Slam* (door) |
| ズズズ (Zuzuzu) | *Slurp* (noodles) |
| パチパチ (Pachipachi) | *Clap-clap* / *Crackle* (fire) |
| カチャ (Kacha) | *Click* / *Clink* |
| スッ (Su) | *Swish* / Sudden movement |

**Rule:** Use English SFX equivalents in italics or onomatopoeia formatting. Retain rhythm/pacing intent.

---

## SECTION 4: REGISTER QUICK REFERENCE

### 4.1 FIVE REGISTERS BY RTAS

| Register | RTAS Range | Contraction Frequency | Vocabulary | Sentence Length |
|----------|-----------|----------------------|------------|-----------------|
| **Archaic/Noble** | N/A (archetype) | 0% | Latinate, formal | Long, flowing |
| **Formal** | < 2.0 | < 20% | Professional | Medium-long |
| **Standard** | 2.0-3.0 | 50% | Neutral | Medium |
| **Casual** | 3.0-4.0 | 80% | Colloquial | Short-medium |
| **Intimate** | > 4.0 | 100% | Simple, slang | Fragments OK |

---

### 4.2 VOCABULARY TIER SELECTION

#### **LATINATE VS GERMANIC WORD CHOICE**

| Latinate (Formal) | Germanic (Casual) | Context |
|-------------------|-------------------|---------|
| Request | Ask | RTAS < 2.0 vs RTAS > 3.0 |
| Commence | Start | Formal vs casual |
| Inquire | Ask | Professional vs friendly |
| Assist | Help | Distant vs close |
| Terminate | End | Clinical vs direct |
| Observe | See/Watch | Intellectual vs simple |
| Permit | Let | Authority vs peer |
| Respond | Answer | Formal vs neutral |

**Rule:** Higher RTAS = prefer Germanic roots; Lower RTAS = prefer Latinate.

---

## SECTION 5: FORMATTING & PUNCTUATION GUIDE

### 5.1 DIALOGUE CONVENTIONS

**Standard Dialogue:**
```
"I'll be there," he said.
"Are you sure?" she asked.
```

**Internal Monologue (Italics):**
```
*What am I doing?* he thought.
```

**Thought Without Tag:**
```
What was he doing here?
```

---

### 5.2 EMPHASIS & EMOTION MARKERS

**Ellipsis (...):** Trailing off, hesitation
```
"I just... I don't know."
```

**Em-Dash (—):** Interruption, sudden shift
```
"She was—wait, what?"
```

**Exclamation (!):** Strong emotion, surprise
```
"No way!"
```

**Question (?):** Inquiry, confusion
```
"What's going on?"
```

---

## SECTION 6: TITLE TRANSLATION (ARTISTIC LICENSE)

### 6.1 TITLE PHILOSOPHY

**Core Principle:** Titles (chapter titles, volume titles, series titles) require **artistic interpretation** rather than literal translation. Focus on **thematic resonance, rhythm, and marketability**.

**Why Different from Body Text:**
- Titles are marketing tools (must attract readers)
- Titles set emotional tone (evocative > literal)
- Titles have no RTAS/register constraints (free from character voice rules)

---

### 6.2 FIVE TITLE TECHNIQUES

#### **TECHNIQUE T-1: THEMATIC SUBSTITUTION**
**Definition:** Replace literal words with English phRTASes that capture emotional/thematic core.

**Examples:**
- 「雨の日の約束」 → "Promise in the Rain" (literal) vs **"When Rain Speaks"** (thematic)
- 「最後の夜」 → "Last Night" (literal) vs **"The Night Everything Changed"** (thematic)
- 「二人の距離」 → "Distance Between Two" (literal) vs **"The Space We Share"** (thematic)

**When to Use:** Source title is functional but lacks emotional punch.

---

#### **TECHNIQUE T-2: RHYTHM OPTIMIZATION**
**Definition:** Prioritize syllable flow, alliteration, memorable cadence over exact words.

**Examples:**
- 「静かな夜」 → "Silent Night" (flows) vs "A Night of Silence" (wordy)
- 「春の風」 → "Spring Breeze" (smooth) vs "The Wind of Spring" (clunky)
- 「彼女の秘密」 → "Her Secret" (clean) vs "The Secret That She Holds" (overwritten)

**Guidelines:**
- 2-5 words ideal (concise, memorable)
- Test by saying aloud (does it roll off tongue?)
- Use alliteration if natural (not forced)

---

#### **TECHNIQUE T-3: DRAMATIC ELEVATION**
**Definition:** Add intensity, weight, or drama if source title is plain/understated.

**Examples:**
- 「別れ」 → "Parting" (plain) vs **"The Farewell"** (dramatic article)
- 「彼女の涙」 → "Her Tears" (simple) vs **"The Tears She Shed"** (elevated)
- 「選択」 → "Choice" (flat) vs **"The Choice That Binds"** (dramatic extension)

**When to Use:** Source title is a single noun or plain phRTASe; needs gravitas.

**Techniques:**
- Add article "The" for weight ("The X" feels more significant than "X")
- Use past tense for retrospective tone ("What We Lost" vs "What We Lose")
- Add relative clause for mystery ("The Thing She Hid" vs "Her Secret")

---

#### **TECHNIQUE T-4: CULTURAL WESTERNIZATION**
**Definition:** Replace Japan-specific references with Western equivalents OR keep with exotic flair.

**Examples:**
- 「桜の下で」 → **"Beneath the Cherry Blossoms"** (keep—widely recognized) OR "Beneath Spring Blooms" (westernize)
- 「夏祭りの夜」 → "Summer Festival Night" (keep exotic) OR **"The Night of Summer Lights"** (westernize)
- 「お嬢様の決断」 → "Ojou-sama's Decision" (keep term) OR **"The Lady's Resolve"** (westernize)

**Decision Matrix:**
- **Keep Japanese term if:** Widely known (sakura, onsen), adds exotic appeal, genre is fantasy/Japanese-setting
- **Westernize if:** Contemporary setting, term is obscure, flow improves

---

#### **TECHNIQUE T-5: INTRIGUE INJECTION**
**Definition:** Make title more intriguing/mysterious if literal version is bland.

**Examples:**
- 「二人の秘密」 → "Their Secret" (bland) vs **"What They Hide"** (intrigue via question implication)
- 「真実」 → "Truth" (flat) vs **"The Truth Unspoken"** (mysterious—what truth?)
- 「約束」 → "Promise" (generic) vs **"The Promise Left Unbroken"** (stakes implied)

**Techniques:**
- Use questions indirectly ("What X", "When Y")
- Add negation ("Unspoken", "Unseen", "Forgotten") for mystery
- Imply stakes without stating ("The X That Changed Everything" is cliché—avoid; use "What Changed Us" instead)

---

### 6.3 TITLE DECISION WORKFLOW

**Execute for chapter/volume/series titles:**

```
STEP 1: LITERAL TRANSLATION
  → Get core meaning (what is this title saying?)

STEP 2: IDENTIFY THEMATIC CORE
  → What emotion/event does this title represent?
  → What is the chapter/volume actually about?

STEP 3: TEST ENGLISH FLOW
  → Say literal version aloud
  → Does it sound natural? Marketable? Memorable?

STEP 4: APPLY TECHNIQUES (T-1 to T-5)
  → Thematic substitution (if feeling > words)
  → Rhythm optimization (if flow is awkward)
  → Dramatic elevation (if title is plain)
  → Cultural westernization (if JP reference present)
  → Intrigue injection (if title is bland)

STEP 5: VERIFY MARKETABILITY
  → Would a reader click this title?
  → Does it sound professional (not AI-generated)?
  → Does it match genre expectations?

STEP 6: FINAL CHECK
  → Does it still reflect source content? (loose connection OK)
  → Is it concise? (2-7 words ideal)
  → Is it memorable?
```

---

### 6.4 GENRE-SPECIFIC TITLE STRATEGIES

#### **ROMANCE TITLES:**
- **Focus:** Emotion, intimacy, longing
- **Keywords:** Heart, promise, distance, moment, touch, whisper
- **Examples:**
  - 「君との距離」 → "The Distance Between Us" OR "Close to You"
  - 「初めてのキス」 → "First Kiss" OR "When Our Lips Met"

#### **ACTION TITLES:**
- **Focus:** Intensity, stakes, conflict
- **Keywords:** Battle, clash, fall, rise, strike, break
- **Examples:**
  - 「最終決戦」 → "Final Battle" OR "The Reckoning"
  - 「反撃の時」 → "Time to Strike Back" OR "The Counteroffensive"

#### **MYSTERY TITLES:**
- **Focus:** Intrigue, questions, secrets
- **Keywords:** Hidden, forgotten, unseen, truth, lie, shadow
- **Examples:**
  - 「隠された真実」 → "Hidden Truth" OR "What Lies Beneath"
  - 「謎の人物」 → "Mysterious Figure" OR "The Stranger in Shadow"

#### **COMEDY TITLES:**
- **Focus:** Playfulness, irony, exaggeration
- **Keywords:** Chaos, disaster, trouble, mess, misunderstanding
- **Examples:**
  - 「大失敗」 → "Big Failure" OR "The Great Disaster"
  - 「誤解の連続」 → "Continuous Misunderstanding" OR "One Misunderstanding After Another"

---

### 6.5 TITLE EXAMPLES (DETAILED)

#### **EXAMPLE 1: SIMPLE CHAPTER TITLE**

**Japanese:** 「初めての出会い」

**Literal:** "First Meeting"

**Analysis:**
- Plain, functional
- Common title structure
- Needs elevation

**Artistic Options:**
1. **"When Our Paths Crossed"** (T-1 thematic + T-2 rhythm)
   - Implies fate, destiny
   - Poetic without being overwrought
   - 5 syllables, flows naturally

2. **"The First Encounter"** (T-3 dramatic elevation)
   - "The" adds weight
   - "Encounter" more formal than "meeting"

3. **"When We Met"** (T-2 rhythm—concise)
   - Ultra-simple
   - Intimate tone
   - Memorable brevity

**Recommendation:** Depends on genre—Romance: Option 1; Action: Option 2; Slice-of-life: Option 3

---

#### **EXAMPLE 2: EMOTIONAL CHAPTER TITLE**

**Japanese:** 「彼女の涙」

**Literal:** "Her Tears"

**Analysis:**
- Emotionally direct
- Simple structure
- Could use dramatic elevation

**Artistic Options:**
1. **"The Tears She Shed"** (T-3 dramatic + past tense)
   - Past tense implies significance (reader knows tears were important)
   - More weight than present tense

2. **"When She Cried"** (T-1 thematic + T-2 rhythm)
   - Focuses on moment (when) rather than object (tears)
   - More active, immediate

3. **"Her Tears Fall"** (T-2 rhythm + present tense)
   - Present tense = immediacy
   - Short, impactful

**Recommendation:** Drama/angst: Option 1; Romance: Option 2; Action: Option 3

---

#### **EXAMPLE 3: SERIES TITLE (COMPLEX)**

**Japanese:** 「お嬢様は僕にだけ甘い」

**Literal:** "The Ojou-sama Is Sweet Only to Me"

**Analysis:**
- Long, awkward in English
- "Sweet" is ambiguous (kind? affectionate? romantic?)
- "Ojou-sama" needs handling (keep term or westernize?)

**Artistic Options:**
1. **"The Noble Lady's Affection"** (T-4 westernize + T-2 concise)
   - "Noble Lady" replaces "Ojou-sama"
   - "Affection" clearer than "sweet"
   - Professional, marketable

2. **"She Bestows Her Kindness Upon Me Alone"** (T-3 dramatic + archaic tone)
   - "Bestows" = elevated vocabulary matches ojou-sama archetype
   - "Upon Me Alone" = exclusive intimacy (僕にだけ)
   - Longer but poetic

3. **"The Lady's Secret Devotion"** (T-5 intrigue + T-4 westernize)
   - "Secret" adds mystery (why only him?)
   - "Devotion" stronger than "affection"
   - Concise, marketable

4. **"Her Grace, Bestowed Upon Me"** (T-3 dramatic + T-4 archaic)
   - "Grace" = nobility + kindness
   - "Bestowed Upon Me" = formal, matches ojou-sama voice

**Recommendation:** Market research genre conventions; likely Option 1 (concise, clear) or Option 2 (poetic, archetype-matched)

---

### 6.6 TITLE GUARDRAILS

#### **DO:**
- Use poetic language (within reason)
- Prioritize rhythm and flow
- Add articles (The/A) for dramatic weight when appropriate
- Westernize cultural references if it improves clarity/flow
- Test multiple options before deciding
- Match genre expectations (romance = evocative; action = punchy)

#### **DON'T:**
- Use AI-ism clichés:
  - ❌ "In a World Where..."
  - ❌ "The X That Changed Everything"
  - ❌ "A Journey of Y and Z"
  - ❌ "Beyond the X"
- Make title unrecognizable from source content (must still relate)
- Over-complicate (keep under 8 words typically)
- Use awkward inversions ("Of Tears, The Night" = forced poetic)
- Ignore genre conventions (mystery needs intrigue, not cuteness)

#### **FORBIDDEN PATTERNS:**
- Generic RPG/isekai titles: "The X of Y" (overused)
- Vague abstractions: "Destiny's Call", "Fate's Design" (meaningless)
- Question titles (usually weak): "Will She Choose Me?" (lacks confidence)

---

### 6.7 QUALITY CHECK FOR TITLES

**Before finalizing, verify:**
- [ ] Title is 2-7 words (concise, memorable)
- [ ] Title reflects thematic/emotional core of content
- [ ] Title flows naturally when spoken aloud
- [ ] Title matches genre expectations
- [ ] Title is marketable (would readers click?)
- [ ] Title avoids AI-ism clichés
- [ ] Title maintains loose connection to source meaning

**If title fails any check → Revise using techniques T-1 to T-5.**

---

### 6.8 INTEGRATION NOTE

**Title translation is EXEMPT from:**
- RTAS/register rules (no character voice constraints)
- Archetype consistency (titles are narrator voice, not character voice)
- Strict literalness (artistry prioritized)

**Title translation MUST still:**
- Reflect content accurately (thematic connection required)
- Match genre conventions
- Sound professional and polished

---

## SECTION 7: INTEGRATION WITH OTHER MODULES

**When to Consult This Module:**
- **Starting new project → Section 8 (metadata extraction, translation order)**
- Character archetype voice unclear → Section 1
- Honorific decision needed → Section 2
- Japanese idiom encountered → Section 3.1
- Cultural reference question → Section 3.2
- SFX/onomatopoeia → Section 3.3
- Register selection → Section 4
- Formatting question → Section 5
- **Title translation needed → Section 6**
- **Consistency tracking needed → Section 8.3**

**Cross-Reference:**
- **RTAS Calculation** → Module 01 (Register/Formality System)
- **Boldness Techniques** → Module 02
- **Rhythm & Pacing** → Module 03
- **Quality Verification** → Module 05 (Golden Samples)
- **Detailed Voice Profiles** → Module 06
- **Title Translation** → Master Prompt Section 0.5

---

## SECTION 8: METADATA EXTRACTION & CANON-AWARE TRANSLATION ORDER

### 8.1 PROJECT INITIALIZATION: METADATA EXTRACTION

**Purpose:** Before beginning translation, extract critical metadata to establish consistency framework and determine translation order.

#### **METADATA SOURCES:**

**1. EPUB Metadata Files**
- **standard.opf / package.opf**: Title, author, illustrator, publisher, volume number, ISBN
- **navigation-documents.xhtml / toc.ncx**: Chapter structure, chapter titles, ordering
- **content files (xhtml)**: Text content, chapter divisions, character introductions

**2. Text Files (TXT/PDF)**
- **Filename patterns**: Volume number, chapter indicators
- **Header content**: Title, author, chapter names
- **Structure markers**: 第○章 (Chapter X), プロローグ (Prologue), エピローグ (Epilogue), 幕間 (Interlude)

---

#### **CRITICAL METADATA TO EXTRACT:**

**A. SERIES/VOLUME INFORMATION**
```
- Series Title (JP): [Japanese title]
- Series Title (EN): [English localized title] → Use Section 6 guidelines
- Volume Number: [X]
- Author: [Name (Japanese) / Romanized]
- Illustrator: [Name (Japanese) / Romanized]
- Publisher: [Publisher name]
- Publication Date: [Year-Month]
```

**B. WORLD SETTING CLASSIFICATION**
```
- Setting Type: [Fantasy / Modern Japanese / Isekai / Historical / Mixed]
- Time Period: [Medieval / Contemporary / Futuristic]
- Cultural Context: [Western-inspired / Japanese / Mixed]
- Magic/Supernatural: [Yes/No]
```

**→ Critical for HONORIFIC SYSTEM (Section 2.0 World-Awareness)**
   - Fantasy/Western/Isekai → English honorifics (Sir, Lady, Miss)
   - Modern Japanese → Japanese honorifics (kun, chan, san, sama)

**C. CHAPTER STRUCTURE ANALYSIS**
```
- Total Chapter Count: [Number]
- Chapter Types:
  - Prologue: [Yes/No]
  - Main Chapters: [Count]
  - Interludes (幕間): [Count, positions]
  - Epilogue: [Yes/No]
  - Extra Chapters: [Count]
```

**D. CHARACTER ROSTER (Initial Detection)**
```
- Protagonist: [Name (JP) / Gender / Likely Archetype]
- Main Heroine(s): [Names (JP) / Archetypes]
- Supporting Characters: [Names (JP) / Roles]
```

**→ Update as translation progresses; finalize archetype assignments in Chapter 1**

---

### 8.2 CANON-AWARE TRANSLATION ORDER

**Purpose:** Establish logical translation sequence to maintain consistency and build character voice foundation.

#### **STANDARD TRANSLATION ORDER:**

```
PHASE 1: FOUNDATION (Establish Canon)
  ├─ Step 1: Extract Metadata (Section 8.1)
  ├─ Step 2: Translate PROLOGUE (if exists)
  │    → Establishes world setting, tone, character introductions
  │    → Lock world-setting classification for honorific system
  │    → Identify protagonist archetype
  └─ Step 3: Translate CHAPTER 1
       → Confirms character archetypes
       → Establishes RTAS baselines for all character pairs
       → Creates initial terminology glossary

PHASE 2: MAIN NARRATIVE (Sequential Progression)
  ├─ Step 4: Translate Chapters 2-X in order
  │    → Maintain voice consistency using Phase 1 baselines
  │    → Track RTAS evolution (relationship progression)
  │    → Update terminology glossary as needed
  └─ Step 5: Translate INTERLUDES (幕間) at their canonical positions
       → Interludes appear between specific chapters
       → Translate when reaching their position in chapter sequence
       → Example: If 幕間 appears after Chapter 3, translate after Chapter 3

PHASE 3: CONCLUSION (Final Chapters)
  ├─ Step 6: Translate final chapters
  └─ Step 7: Translate EPILOGUE (if exists)
       → Resolves character arcs
       → Final RTAS tier (often highest intimacy)
       → Validates consistency with entire volume

PHASE 4: EXTRTAS & QUALITY ASSURANCE
  ├─ Step 8: Translate extra chapters/afterwords
  └─ Step 9: Final consistency check (Module 05 quality standard)
```

---

#### **TRANSLATION ORDER EXAMPLES:**

**Example 1: Standard LN Volume Structure**
```
Source Structure:
- プロローグ (Prologue)
- 第一章 (Chapter 1)
- 第二章 (Chapter 2)
- 幕間 (Interlude)
- 第三章 (Chapter 3)
- エピローグ (Epilogue)

Translation Order:
1. Prologue → Establish world, tone, protagonist
2. Chapter 1 → Lock character archetypes, RTAS baselines
3. Chapter 2 → Continue progression
4. Interlude → Translate at canonical position
5. Chapter 3 → Continue progression
6. Epilogue → Final arc resolution
7. QA Pass → Consistency verification (Module 05)
```

**Example 2: Multi-Volume Series (Volume 2+)**
```
Prerequisites:
- Review Volume 1 translations for consistency
- Import established terminology glossary
- Verify character archetype assignments
- Check RTAS progression from previous volume

Translation Order:
1. Extract Volume 2 metadata
2. Review Volume 1 ending → Volume 2 opening continuity
3. Translate Prologue (if new volume has one)
4. Proceed with standard order (Chapters 1-X)
5. Cross-reference terminology with Volume 1 glossary
6. Maintain character voice consistency across volumes
```

---

### 8.3 CONSISTENCY TRACKING DURING TRANSLATION

**Purpose:** Maintain canon accuracy and character voice consistency throughout translation process.

#### **TRACKING SYSTEMS:**

**A. CHARACTER CONSISTENCY TRACKER**
```
Character: [Name (JP) → Name (EN)]
- Archetype: [Assigned archetype from Section 1]
- Voice Baseline: [Key characteristics: formality, vocabulary, speech patterns]
- RTAS Tier Progression:
  - Prologue: [RTAS score]
  - Chapter 1: [RTAS score]
  - Chapter X: [RTAS score]
  - Final Chapter: [RTAS score]
- Honorific Usage:
  - Addresses Protagonist as: [Title/name locked in Chapter 1]
  - Addressed by Protagonist as: [Title/name locked in Chapter 1]
- Name/Title Changes: [Document any progression: "Lady Elaine" → "Elaine" at Chapter 5]
```

**B. TERMINOLOGY GLOSSARY (Build During Translation)**
```
| Japanese Term | English Translation | Context | First Appearance |
|---------------|---------------------|---------|------------------|
| [JP term] | [EN equivalent] | [Usage context] | [Chapter X] |

Examples:
| 魔法学院 | Academy of Arcane Arts | School setting | Prologue |
| 紅花姫 | Crimson Blossom Princess | Character title | Chapter 2 |
| 専属侍女 | Personal Attendant | Job title | Chapter 1 |
```

**C. WORLD-SETTING TERMINOLOGY**
```
- Currency: [JP term → EN equivalent] (e.g., 円 → "gold coins" in fantasy)
- Locations: [JP names → EN romanization or localization]
- Titles/Ranks: [JP → EN] (e.g., 伯爵 → "Count", 令嬢 → "Lady")
- Magic/Skills: [JP → EN] (Consistent naming for abilities)
- Items: [JP → EN] (Weapons, artifacts, food items)
```

**D. CHAPTER-SPECIFIC NOTES**
```
Chapter X:
- RTAS shifts: [Character A→B: 2.5 → 3.0 due to confession scene]
- New characters introduced: [Name, archetype, initial voice]
- Terminology added: [New terms encountered]
- Continuity notes: [Important plot points affecting future chapters]
```

---

### 8.4 METADATA EXTRACTION WORKFLOW (EPUB SOURCES)

**Step-by-Step Process for EPUB Files:**

```
STEP 1: LOCATE METADATA FILES
  - Extract EPUB (it's a ZIP archive)
  - Find: standard.opf or package.opf (metadata)
  - Find: navigation-documents.xhtml or toc.ncx (table of contents)
  - Find: xhtml/ folder (chapter content files)

STEP 2: EXTRACT TITLE & AUTHOR
  From standard.opf:
  - <dc:title>: Japanese series title
  - <dc:creator role="aut">: Author name
  - <dc:creator role="art">: Illustrator name
  - <dc:publisher>: Publisher
  - <meta property="dcterms:modified">: Publication date

STEP 3: EXTRACT CHAPTER STRUCTURE
  From navigation-documents.xhtml:
  - Parse <nav epub:type="toc"> section
  - Extract chapter titles from <a> tags
  - Identify prologue (プロローグ), chapters (第○章), interludes (幕間), epilogue (エピローグ)
  - Note canonical order from <ol> sequence

STEP 4: MAP CHAPTER FILES TO CONTENT
  - Match href values to xhtml files (e.g., "xhtml/p-003.xhtml" = Prologue)
  - Create translation checklist with file mappings

STEP 5: DETECT WORLD SETTING (Initial Analysis)
  - Read Prologue content
  - Scan for keywords:
    * Fantasy indicators: 魔法 (magic), 騎士 (knight), 王国 (kingdom), 異世界 (isekai)
    * Modern indicators: 学校 (school), 携帯 (phone), 現代 (contemporary)
  - Lock honorific system strategy (Section 2.0)

STEP 6: CREATE PROJECT STRUCTURE
  Project Name: [Series Title EN]_Vol[X]

  Folders:
  - /source/ (original EPUB extracted files)
  - /translated/ (completed chapter translations)
  - /glossary/ (terminology tracker)
  - /notes/ (character consistency, RTAS progression)
```

---

### 8.5 PRACTICAL EXAMPLE: METADATA EXTRACTION

**Source EPUB: 貴族令嬢。俺にだけなつく (Volume 1)**

#### **EXTRACTED METADATA:**

```yaml
Series Information:
  JP Title: 貴族令嬢。俺にだけなつく
  EN Title: "The Noble Lady: She Bestows Her Affection Upon Me Alone"
  Volume: 1
  Author: 夏乃実 (Natsunomi)
  Illustrator: GreeN
  Publisher: KADOKAWA
  Publication: 2022-12

World Setting:
  Type: Fantasy/Noble Romance
  Cultural Context: Western-inspired (noble courts, European naming)
  Honorific Strategy: ENGLISH HONORIFICS (Sir, Lady, Miss, Master)
    → Reason: Fantasy setting with nobility (Section 2.0 rule)

Chapter Structure (from navigation-documents.xhtml):
  1. プロローグ (Prologue) → xhtml/p-003.xhtml
  2. 第一章　専属侍女 (Chapter 1: Personal Attendant) → xhtml/p-004.xhtml
  3. 第二章　紅花姫 (Chapter 2: Crimson Blossom Princess) → xhtml/p-005.xhtml
  4. 第三章　本食いの才女 (Chapter 3: The Book-Loving Prodigy) → xhtml/p-006.xhtml
  5. 幕間 (Interlude) → xhtml/p-007.xhtml
  6. 第四章　悪評の薄どけ (Chapter 4: The Veil of Ill Repute) → xhtml/p-008.xhtml
  7. 幕間 (Interlude) → xhtml/p-009.xhtml
  8. 第五章　距離の縮まり (Chapter 5: Closing the Distance) → xhtml/p-010.xhtml
  9. 第六章　慎ましデート (Chapter 6: A Modest Date) → xhtml/p-011.xhtml
  10. 幕間 (Interlude) → xhtml/p-012.xhtml
  11. エピローグ (Epilogue) → xhtml/p-013.xhtml

Translation Order:
  Phase 1: Prologue, Chapter 1 (establish archetypes & RTAS baselines)
  Phase 2: Chapters 2-6 with interludes at canonical positions
  Phase 3: Epilogue
  Phase 4: QA consistency check
```

#### **INITIAL CHARACTER DETECTION (Prologue/Chapter 1):**

```
Protagonist (Male):
  - Likely archetype: Commoner/Servant (専属侍女 = personal attendant)
  - POV: First-person ("俺" = masculine "I")
  - Initial voice: Humble, formal when addressing nobility

Main Heroine:
  - Character type: Noble lady (貴族令嬢)
  - Archetype: Likely Ojou-sama (refined, formal speech)
  - Initial RTAS: Low (<2.0, formal distance)
  - Honorific: "Lady [Name]" (English honorific due to fantasy setting)

Expected Progression:
  - RTAS evolution: Formal (Lady) → Neutral (Name) → Intimate (First name)
  - Relationship arc: Master-servant → Mutual affection
  - Voice shift: Ojou-sama maintains refined register but increases warmth
```

---

### 8.6 INTEGRATION WITH TRANSLATION WORKFLOW

**How Section 8 Connects to Core Workflow:**

```
BEFORE Translation (Pre-Production):
  ├─ Section 8.1-8.2: Extract metadata, establish translation order
  ├─ Section 8.4: Process EPUB files, map chapter structure
  └─ Section 8.5: Create project structure, initial character detection

DURING Translation (Production):
  ├─ Master Prompt: Core translation directives
  ├─ Module 01-06: Apply techniques (RTAS, register, boldness, rhythm)
  ├─ Section 8.3: Track consistency (characters, terminology, RTAS progression)
  └─ Update glossary after each chapter

AFTER Translation (Post-Production):
  ├─ Module 05: Quality verification against golden samples
  ├─ Section 8.3: Final consistency check (voice, terminology, RTAS logic)
  └─ Archive glossary for future volumes
```

---

**END OF MODULE 00**

**STATUS:** AUTHORITATIVE REFERENCE FOR ENGLISH LOCALIZATION FOUNDATION
**USAGE:** Primary lookup for character voices, honorifics, idioms, cultural references, **title translation**, **project setup**
**INTEGRATION:** Works with Modules 01-06 + EN Master Prompt

