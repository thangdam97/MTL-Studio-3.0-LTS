# CJK CHARACTER PREVENTION PROTOCOL
## Vietnamese Translation Quality Assurance

**PURPOSE**: Prevent Chinese/Japanese character leakage in Vietnamese translation output.

---

## ⚠️ CRITICAL RULE: ZERO CJK TOLERANCE

**ABSOLUTE PROHIBITION**: Do NOT output ANY Chinese/Japanese characters (CJK Unified Ideographs: U+4E00–U+9FFF) in Vietnamese translation.

### Why This Matters
- Vietnamese uses Latin alphabet exclusively
- CJK characters indicate incomplete translation
- Readers cannot understand untranslated characters
- Professional quality requires 100% Vietnamese output

---

## 🚫 FORBIDDEN PATTERNS

### 1. Untranslated Japanese Phrases
**NEVER DO THIS:**
```
❌ Diễn biến này thật quá trùng hợp đến mức都合が良すぎる
❌ Cô ấy rất可愛い
❌ Tôi không thể理解できない
```

**CORRECT APPROACH:**
```
✅ Diễn biến này thật quá trùng hợp đến mức thuận tiện quá
✅ Cô ấy rất đáng yêu
✅ Tôi không thể hiểu được
```

### 2. Mixed Script Contamination
**NEVER DO THIS:**
```
❌ Anh ấy nói「Xin chào」với tôi
❌ Charlotte說她很高興
❌ Emma想要玩domino
```

**CORRECT APPROACH:**
```
✅ Anh ấy nói "Xin chào" với tôi
✅ Charlotte nói cô ấy rất vui
✅ Emma muốn chơi domino
```

### 3. Chinese-Only Characters
These characters NEVER appear in Vietnamese - if you see them in source, translate them:

**禁止字符 (Forbidden):**
- 爲這個們嗎呢啊吧喔哦唄咧啦哪誰
- 係喺啲嘅嗰噉乜咁點樣邊冇
- 未曾經緊住咗過喇啩囉啫嚟
- 佢哋你妳您俺咱阮伲偌倆仨

**Translation Required:**
- 這個 → cái này, điều này
- 那個 → cái đó, điều đó
- 什麼 → cái gì, gì
- 怎麼 → như thế nào, sao
- 為了 → vì, để
- 應該 → nên, phải
- 沒有 → không có
- 已經 → đã
- 正在 → đang

### 4. Common Kanji That Must Be Translated

**Names & Titles (Keep in Context):**
- Character names: Keep romaji (Akihito, Charlotte, Emma)
- Honorifics: -san, -sensei, -kun, -chan (can keep or translate)

**Everything Else Must Be Vietnamese:**
- 学校 → trường học
- 先生 → thầy/cô giáo
- 友達 → bạn bè
- 家族 → gia đình
- 時間 → thời gian
- 場所 → nơi chốn
- 気持ち → cảm giác
- 本当 → thật sự
- 一緒 → cùng nhau
- 大丈夫 → không sao
- 勉強 → học tập
- 仕事 → công việc
- 会社 → công ty
- 問題 → vấn đề
- 理由 → lý do
- 方法 → phương pháp

---

## ✅ SELF-CHECK PROTOCOL

**BEFORE OUTPUTTING EACH SENTENCE, ASK:**

1. **Character Check**: Are there ANY CJK characters (漢字) in my output?
   - If YES → STOP, translate them to Vietnamese
   - If NO → Proceed

2. **Completeness Check**: Did I translate EVERY word from source?
   - Check for phrases like "都合が良い", "可愛い", "理解できない"
   - Verify all idioms are fully converted

3. **Script Purity**: Is my output 100% Latin alphabet (Vietnamese)?
   - Allowed: A-Z, Vietnamese diacritics (ă, â, ê, ô, ơ, ư, đ)
   - Allowed: Punctuation, numbers, standard symbols
   - FORBIDDEN: Any character from U+4E00–U+9FFF range

---

## 🎯 TRANSLATION STRATEGIES FOR DIFFICULT PHRASES

### Strategy 1: Contextual Meaning Extraction
When encountering complex Japanese phrases with CJK:

**Source:** `都合が良すぎる` (tsuugou ga yosugiru)
- Literal: "convenience is too good"
- Context: "too convenient/coincidental"
- Vietnamese: **"thuận tiện quá"**, **"trùng hợp quá"**

**Source:** `気が付かない` (ki ga tsukanai)
- Literal: "spirit doesn't attach"
- Context: "doesn't notice"
- Vietnamese: **"không để ý"**, **"không nhận ra"**

### Strategy 2: Functional Equivalence
Focus on WHAT it means in the scene, not literal translation:

**Source:** `仕方がない` (shikata ga nai)
- Function: Expressing resignation/acceptance
- Vietnamese: **"không còn cách nào"**, **"đành chịu thôi"**, **"chẳng làm sao được"**

**Source:** `どうしよう` (doushiyou)
- Function: Worried pondering
- Vietnamese: **"làm sao đây"**, **"giờ phải làm gì"**, **"thế nào bây giờ"**

### Strategy 3: Decompose and Translate
Break complex compounds into parts:

**Source:** `図書館` (toshokan)
- 図書 = books/documents
- 館 = building/hall
- Vietnamese: **"thư viện"** (don't leave as 図書館)

**Source:** `運動会` (undoukai)
- 運動 = exercise/sports
- 会 = meeting/event
- Vietnamese: **"hội thao"**, **"ngày hội thể thao"**

---

## 📋 COMMON SUBSTITUTIONS REFERENCE

### Everyday Vocabulary
| Japanese | Vietnamese | Context |
|----------|-----------|---------|
| 大丈夫 | không sao, ổn | reassurance |
| 本当 | thật sự, thực sự | emphasis |
| 多分 | có lẽ, chắc là | probability |
| 突然 | đột nhiên, bỗng dưng | suddenly |
| 一緒 | cùng nhau, chung | together |
| 勿論 | tất nhiên, đương nhiên | of course |
| 実は | thực ra, sự thật là | confession |
| やっぱり | quả nhiên, đúng như nghĩ | as expected |
| 相変わらず | như thường lệ, vẫn vậy | unchanging |
| 仕方ない | không còn cách nào | resignation |

### Emotional Expressions
| Japanese | Vietnamese | Usage |
|----------|-----------|-------|
| 嬉しい | vui, hạnh phúc | happy |
| 悲しい | buồn, đau lòng | sad |
| 楽しい | vui vẻ, thú vị | fun |
| 寂しい | cô đơn, cô đơn | lonely |
| 恥ずかしい | xấu hổ, ngượng | embarrassed |
| 怖い | sợ, sợ hãi | scared |
| 驚く | ngạc nhiên, bất ngờ | surprised |
| 心配 | lo lắng, bận tâm | worried |

### Actions & States
| Japanese | Vietnamese | Notes |
|----------|-----------|-------|
| 考える | suy nghĩ, cân nhắc | think |
| 思う | nghĩ, cho rằng | think/feel |
| 分かる | hiểu, biết | understand |
| 知る | biết, nhận thức | know |
| 見る | nhìn, xem | see/watch |
| 聞く | nghe, lắng nghe | hear/listen |
| 話す | nói, trò chuyện | speak/talk |
| 言う | nói, phát biểu | say |
| 書く | viết, ghi chép | write |
| 読む | đọc | read |

---

## 🔍 DETECTION TRIGGERS

**If you find yourself about to output:**
- Characters that look "square" or "complex" → STOP, translate
- Text that readers need a Japanese dictionary for → STOP, translate
- Mixed Vietnamese + Asian characters → STOP, separate and translate
- Phrases you're "keeping" because they're "difficult" → STOP, find Vietnamese equivalent

**Remember:** Vietnamese readers CANNOT read CJK characters. Your job is complete translation, not partial annotation.

---

## ⚡ EMERGENCY FALLBACK

**If a phrase is genuinely untranslatable:**

1. **First:** Try descriptive translation
   - `桜` → "hoa anh đào" (cherry blossoms)
   - `侘寂` → "vẻ đẹp của sự giản dị và thời gian" (wabi-sabi concept)

2. **Second:** Use romanization with immediate explanation
   - "Akihito đang cảm nhận một cảm giác gọi là 'wabi-sabi', một triết lý Nhật Bản về vẻ đẹp trong sự không hoàn hảo"

3. **NEVER:** Leave raw CJK without explanation

---

## 📊 QUALITY CHECKPOINTS

**Before Submitting Translation:**

- [ ] Scan entire output for characters U+4E00–U+9FFF
- [ ] Verify all Japanese phrases have Vietnamese equivalents
- [ ] Check that quotation marks are standard (not 「」 or 《》)
- [ ] Confirm no mixed-script sentences
- [ ] Validate all proper nouns are in romaji (names) or translated (places)

**Golden Rule:** If a Vietnamese reader with ZERO Japanese knowledge can understand 100% of your output → You succeeded.

---

## 🎓 LEARNING FROM ERRORS

**Common Mistakes to Avoid:**

1. **"It's too complex to translate"**
   - Wrong: 都合が良すぎる
   - Right: thuận tiện quá, trùng hợp quá mức

2. **"It's a set phrase"**
   - Wrong: お疲れ様です
   - Right: Cô/anh vất vả rồi, Nhờ cô/anh

3. **"It loses nuance"**
   - Wrong: よろしくお願いします
   - Right: [Context-dependent] "Nhờ anh/chị", "Xin gặp lại", "Rất mong được hợp tác"

4. **"Character names need kanji"**
   - Wrong: 青柳明人さん
   - Right: Aoyagi Akihito-san (or just "Akihito")

---

## ✨ SUCCESS CRITERIA

**Your translation is acceptable when:**
- ✅ 0 CJK characters in output (U+4E00–U+9FFF range)
- ✅ 100% Vietnamese readable without Japanese knowledge
- ✅ All meaning preserved through contextual equivalents
- ✅ Natural Vietnamese flow (not word-for-word calques)
- ✅ Proper nouns in standard romaji conventions

**Your translation FAILS when:**
- ❌ ANY CJK character appears (even 1)
- ❌ Reader needs to "guess" from context what untranslated part means
- ❌ Mixed scripts create reading confusion
- ❌ Lazy preservation of "difficult" phrases

---

## 🚀 FINAL INSTRUCTION

**When translating, your internal process should be:**

```
1. Read Japanese source (may contain kanji)
2. Understand meaning/context/emotion
3. Find Vietnamese equivalent
4. Output ONLY Vietnamese
5. Self-check: Any CJK? → If yes, loop to step 3
6. Submit clean Vietnamese output
```

**This is not optional. This is mandatory for professional quality.**

**CJK characters in Vietnamese output = Translation failure.**

---

**END OF CJK PREVENTION PROTOCOL**
