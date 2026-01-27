# Publisher Profiles

Publisher-specific EPUB structure patterns for debugging and maintenance.

## Purpose

Each publisher has unique EPUB formatting conventions:
- Image naming patterns
- TOC structure
- Chapter organization
- File naming conventions

These JSON profiles document known patterns to help with:
- **Debugging** new EPUBs from known publishers
- **Pattern updates** when encountering edge cases
- **Testing** to verify all patterns still work
- **Documentation** of publisher quirks

## Profile Structure

```json
{
  "publisher": "Publisher Name",
  "publisher_ja": "日本語名",
  "country": "JP",

  "image_patterns": {
    "cover": { "patterns": [...], "examples": [...] },
    "kuchie": { "patterns": [...], "examples": [...] },
    "illustrations": { "patterns": [...], "examples": [...] }
  },

  "toc_structure": {
    "format": "EPUB3",
    "has_nav_xhtml": true,
    "nav_structure": "li > span > a"
  },

  "content_structure": {
    "filename_pattern": "...",
    "chapter_merging": true
  },

  "test_cases": [
    { "title": "...", "verified": true }
  ]
}
```

## Current Profiles

### 1. Media Factory (株式会社メディアファクトリー)
- **File:** [media_factory.json](media_factory.json)
- **Key Features:**
  - `o_` prefix on all images
  - Japanese naming (`o_hyoushi.jpg` = cover)
  - Hybrid EPUB2/3 with both `nav.xhtml` and `toc.ncx`
  - Anchors wrapped in `<span>` elements
  - Visual TOC page as content

### 2. Brave Bunko (ブレイブ文庫)
- **File:** [brave_bunko.json](brave_bunko.json)
- **Key Features:**
  - Standard EPUB3 structure
  - Clean naming conventions
  - Direct anchor children in nav
  - One file per chapter

## How to Use

### Debugging a New EPUB

1. **Identify the publisher** from the EPUB metadata
2. **Check if a profile exists** in this directory
3. **Compare actual structure** with the profile patterns
4. **If patterns don't match:**
   - Update the profile with new patterns
   - Update the main pattern regexes in `image_extractor.py`

### Adding a New Publisher

1. **Create a new JSON file:** `publisher_name.json`
2. **Document all patterns** you observe
3. **Add test cases** with verified EPUBs
4. **Update the main code** if new patterns are needed

### Testing Against Profiles

Future enhancement: Create a test script that:
- Loads all profiles
- Tests pattern regexes against examples
- Validates that all test cases still work

## Pattern Updates

When you update patterns in the code, also update the profiles:

**Example:** Adding `o_` prefix support
1. Update `image_extractor.py`:
   ```python
   COVER_PATTERN = r'^(o_)?(?:cover|hyoushi)\.jpe?g$'
   ```
2. Update `media_factory.json`:
   ```json
   "cover": {
     "patterns": ["o_hyoushi\\.jpe?g", "cover\\.jpe?g"],
     "examples": ["o_hyoushi.jpg"]
   }
   ```

## Known Publishers

| Publisher | Profile | Status | Test Cases |
|-----------|---------|--------|------------|
| Media Factory | ✅ | Active | 1 verified |
| Brave Bunko | ✅ | Active | 1 verified |
| MF Bunko J | ⏳ | Pending | - |
| Dengeki Bunko | ⏳ | Pending | - |
| Kadokawa | ⏳ | Pending | - |

## Future Enhancements

1. **Auto-detection:** Script to auto-detect publisher from EPUB metadata
2. **Pattern validation:** Test suite to verify all patterns match examples
3. **Pattern merging:** Automatically generate unified regex from all profiles
4. **Statistics:** Track which patterns are most common across publishers

---

**Maintained by:** MTL Studio Pipeline
**Last Updated:** 2026-01-19
