"""
Name Prompt Generator - Creates prompt injections for irregular name handling.

This module reads the irregular_names_module.xml template and generates
appropriate prompt sections based on detected name patterns from the ruby extractor.

Usage:
    from pipeline.prompts.name_prompt_generator import NamePromptGenerator

    generator = NamePromptGenerator()
    prompt_text = generator.generate_from_extraction_result(extraction_result)
"""

from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import re


@dataclass
class NamePattern:
    """Represents a detected name pattern for prompt generation."""
    kanji: str
    reading: str
    pattern_type: str  # 'kirakira', 'unusual_reading', 'fragmented', 'standard'
    romanized: str = ""
    notes: str = ""
    context: str = ""


class NamePromptGenerator:
    """Generates prompt text for irregular name handling."""

    def __init__(self, template_path: Optional[Path] = None):
        """
        Initialize the generator.

        Args:
            template_path: Path to irregular_names_module.xml (auto-detected if None)
        """
        if template_path is None:
            template_path = Path(__file__).parent / "irregular_names_module.xml"

        self.template_path = template_path
        self._template_cache: Optional[str] = None

    def _load_template(self) -> str:
        """Load and cache the XML template."""
        if self._template_cache is None:
            if self.template_path.exists():
                self._template_cache = self.template_path.read_text(encoding='utf-8')
            else:
                self._template_cache = ""
        return self._template_cache

    def _romanize_hiragana(self, hiragana: str) -> str:
        """Convert hiragana to romanized form."""
        # Basic hiragana to romaji mapping
        romaji_map = {
            'あ': 'a', 'い': 'i', 'う': 'u', 'え': 'e', 'お': 'o',
            'か': 'ka', 'き': 'ki', 'く': 'ku', 'け': 'ke', 'こ': 'ko',
            'さ': 'sa', 'し': 'shi', 'す': 'su', 'せ': 'se', 'そ': 'so',
            'た': 'ta', 'ち': 'chi', 'つ': 'tsu', 'て': 'te', 'と': 'to',
            'な': 'na', 'に': 'ni', 'ぬ': 'nu', 'ね': 'ne', 'の': 'no',
            'は': 'ha', 'ひ': 'hi', 'ふ': 'fu', 'へ': 'he', 'ほ': 'ho',
            'ま': 'ma', 'み': 'mi', 'む': 'mu', 'め': 'me', 'も': 'mo',
            'や': 'ya', 'ゆ': 'yu', 'よ': 'yo',
            'ら': 'ra', 'り': 'ri', 'る': 'ru', 'れ': 're', 'ろ': 'ro',
            'わ': 'wa', 'を': 'wo', 'ん': 'n',
            'が': 'ga', 'ぎ': 'gi', 'ぐ': 'gu', 'げ': 'ge', 'ご': 'go',
            'ざ': 'za', 'じ': 'ji', 'ず': 'zu', 'ぜ': 'ze', 'ぞ': 'zo',
            'だ': 'da', 'ぢ': 'di', 'づ': 'du', 'で': 'de', 'ど': 'do',
            'ば': 'ba', 'び': 'bi', 'ぶ': 'bu', 'べ': 'be', 'ぼ': 'bo',
            'ぱ': 'pa', 'ぴ': 'pi', 'ぷ': 'pu', 'ぺ': 'pe', 'ぽ': 'po',
            'きゃ': 'kya', 'きゅ': 'kyu', 'きょ': 'kyo',
            'しゃ': 'sha', 'しゅ': 'shu', 'しょ': 'sho',
            'ちゃ': 'cha', 'ちゅ': 'chu', 'ちょ': 'cho',
            'にゃ': 'nya', 'にゅ': 'nyu', 'にょ': 'nyo',
            'ひゃ': 'hya', 'ひゅ': 'hyu', 'ひょ': 'hyo',
            'みゃ': 'mya', 'みゅ': 'myu', 'みょ': 'myo',
            'りゃ': 'rya', 'りゅ': 'ryu', 'りょ': 'ryo',
            'ぎゃ': 'gya', 'ぎゅ': 'gyu', 'ぎょ': 'gyo',
            'じゃ': 'ja', 'じゅ': 'ju', 'じょ': 'jo',
            'びゃ': 'bya', 'びゅ': 'byu', 'びょ': 'byo',
            'ぴゃ': 'pya', 'ぴゅ': 'pyu', 'ぴょ': 'pyo',
            'っ': '',  # Small tsu - double next consonant
            'ー': '',  # Long vowel mark
        }

        result = []
        i = 0
        while i < len(hiragana):
            # Check for two-character combinations first
            if i + 1 < len(hiragana):
                combo = hiragana[i:i+2]
                if combo in romaji_map:
                    result.append(romaji_map[combo])
                    i += 2
                    continue

            # Single character
            char = hiragana[i]
            if char in romaji_map:
                # Handle small tsu (っ) - double next consonant
                if char == 'っ' and i + 1 < len(hiragana):
                    next_char = hiragana[i + 1]
                    if next_char in romaji_map and romaji_map[next_char]:
                        result.append(romaji_map[next_char][0])  # Double the consonant
                else:
                    result.append(romaji_map[char])
            else:
                result.append(char)  # Keep unknown characters as-is
            i += 1

        # Capitalize first letter of each word
        romanized = ''.join(result)
        return romanized.capitalize()

    def _romanize_katakana(self, katakana: str) -> str:
        """Convert katakana to romanized form."""
        # Katakana to romaji mapping
        romaji_map = {
            'ア': 'a', 'イ': 'i', 'ウ': 'u', 'エ': 'e', 'オ': 'o',
            'カ': 'ka', 'キ': 'ki', 'ク': 'ku', 'ケ': 'ke', 'コ': 'ko',
            'サ': 'sa', 'シ': 'shi', 'ス': 'su', 'セ': 'se', 'ソ': 'so',
            'タ': 'ta', 'チ': 'chi', 'ツ': 'tsu', 'テ': 'te', 'ト': 'to',
            'ナ': 'na', 'ニ': 'ni', 'ヌ': 'nu', 'ネ': 'ne', 'ノ': 'no',
            'ハ': 'ha', 'ヒ': 'hi', 'フ': 'fu', 'ヘ': 'he', 'ホ': 'ho',
            'マ': 'ma', 'ミ': 'mi', 'ム': 'mu', 'メ': 'me', 'モ': 'mo',
            'ヤ': 'ya', 'ユ': 'yu', 'ヨ': 'yo',
            'ラ': 'ra', 'リ': 'ri', 'ル': 'ru', 'レ': 're', 'ロ': 'ro',
            'ワ': 'wa', 'ヲ': 'wo', 'ン': 'n',
            'ガ': 'ga', 'ギ': 'gi', 'グ': 'gu', 'ゲ': 'ge', 'ゴ': 'go',
            'ザ': 'za', 'ジ': 'ji', 'ズ': 'zu', 'ゼ': 'ze', 'ゾ': 'zo',
            'ダ': 'da', 'ヂ': 'di', 'ヅ': 'du', 'デ': 'de', 'ド': 'do',
            'バ': 'ba', 'ビ': 'bi', 'ブ': 'bu', 'ベ': 'be', 'ボ': 'bo',
            'パ': 'pa', 'ピ': 'pi', 'プ': 'pu', 'ペ': 'pe', 'ポ': 'po',
            'キャ': 'kya', 'キュ': 'kyu', 'キョ': 'kyo',
            'シャ': 'sha', 'シュ': 'shu', 'ショ': 'sho',
            'チャ': 'cha', 'チュ': 'chu', 'チョ': 'cho',
            'ニャ': 'nya', 'ニュ': 'nyu', 'ニョ': 'nyo',
            'ヒャ': 'hya', 'ヒュ': 'hyu', 'ヒョ': 'hyo',
            'ミャ': 'mya', 'ミュ': 'myu', 'ミョ': 'myo',
            'リャ': 'rya', 'リュ': 'ryu', 'リョ': 'ryo',
            'ギャ': 'gya', 'ギュ': 'gyu', 'ギョ': 'gyo',
            'ジャ': 'ja', 'ジュ': 'ju', 'ジョ': 'jo',
            'ビャ': 'bya', 'ビュ': 'byu', 'ビョ': 'byo',
            'ピャ': 'pya', 'ピュ': 'pyu', 'ピョ': 'pyo',
            'ッ': '',  # Small tsu
            'ー': '',  # Long vowel mark
            'ァ': 'a', 'ィ': 'i', 'ゥ': 'u', 'ェ': 'e', 'ォ': 'o',  # Small vowels
            'ヴ': 'vu',  # V sound
        }

        result = []
        i = 0
        while i < len(katakana):
            # Check for two-character combinations first
            if i + 1 < len(katakana):
                combo = katakana[i:i+2]
                if combo in romaji_map:
                    result.append(romaji_map[combo])
                    i += 2
                    continue

            # Single character
            char = katakana[i]
            if char in romaji_map:
                # Handle small tsu (ッ) - double next consonant
                if char == 'ッ' and i + 1 < len(katakana):
                    next_char = katakana[i + 1]
                    if next_char in romaji_map and romaji_map[next_char]:
                        result.append(romaji_map[next_char][0])
                elif char == 'ー' and result:
                    # Long vowel - repeat last vowel
                    last = result[-1]
                    if last and last[-1] in 'aeiou':
                        result.append(last[-1])
                else:
                    result.append(romaji_map[char])
            else:
                result.append(char)
            i += 1

        return ''.join(result).capitalize()

    def romanize(self, text: str) -> str:
        """
        Convert Japanese text (hiragana/katakana) to romanized form.

        Args:
            text: Japanese text (hiragana or katakana)

        Returns:
            Romanized string
        """
        # Detect if primarily katakana or hiragana
        katakana_pattern = re.compile(r'[\u30A0-\u30FF]')
        hiragana_pattern = re.compile(r'[\u3040-\u309F]')

        katakana_count = len(katakana_pattern.findall(text))
        hiragana_count = len(hiragana_pattern.findall(text))

        if katakana_count > hiragana_count:
            return self._romanize_katakana(text)
        else:
            return self._romanize_hiragana(text)

    def generate_kirakira_section(self, names: List[NamePattern]) -> str:
        """
        Generate prompt section for kira-kira names.

        Args:
            names: List of NamePattern objects with pattern_type='kirakira'

        Returns:
            Formatted prompt text
        """
        if not names:
            return ""

        lines = [
            "### Kira-Kira Name Pattern Detected",
            "",
            "The following characters have \"kira-kira\" names where the kanji reading",
            "differs dramatically from standard readings:",
            ""
        ]

        for name in names:
            romanized = name.romanized or self._romanize_katakana(name.reading)
            lines.append(f"- **{name.kanji}** ({name.reading}) → Romanize as: **{romanized}**")
            if name.notes:
                lines.append(f"  - Note: {name.notes}")

        lines.extend([
            "",
            "**Translation Guidelines:**",
            "1. Use the KATAKANA reading as the romanized name (not the kanji reading)",
            "2. If the text explicitly comments on the unusual name (e.g., calling it a",
            "   \"kira-kira name\" or キラキラネーム), preserve that commentary",
            "3. Maintain consistency - use the same romanization throughout",
            ""
        ])

        return "\n".join(lines)

    def generate_unusual_reading_section(self, names: List[NamePattern]) -> str:
        """
        Generate prompt section for unusual readings.

        Args:
            names: List of NamePattern objects with pattern_type='unusual_reading'

        Returns:
            Formatted prompt text
        """
        if not names:
            return ""

        lines = [
            "### Unusual Name Reading Detected",
            "",
            "The following character names have non-standard readings:",
            ""
        ]

        for name in names:
            romanized = name.romanized or self.romanize(name.reading)
            lines.append(f"- **{name.kanji}** ({name.reading}) → Romanize as: **{romanized}**")
            if name.notes:
                lines.append(f"  - Note: {name.notes}")

        lines.extend([
            "",
            "**Translation Guidelines:**",
            "1. The furigana reading is the ACTUAL pronunciation - use it for romanization",
            "2. Do NOT \"correct\" the reading to a more common one",
            "3. If other characters comment on the unusual name, translate that commentary",
            ""
        ])

        return "\n".join(lines)

    def generate_fragmented_section(self, names: List[NamePattern]) -> str:
        """
        Generate prompt section for fragmented names.

        Args:
            names: List of NamePattern objects with pattern_type='fragmented'

        Returns:
            Formatted prompt text
        """
        if not names:
            return ""

        lines = [
            "### Fragmented Name Pattern",
            "",
            "The following character names appear in fragments across different POVs:",
            ""
        ]

        for name in names:
            romanized = name.romanized or self.romanize(name.reading)
            lines.append(f"- **{name.kanji}** ({name.reading}) → Full name: **{romanized}**")
            if name.notes:
                lines.append(f"  - {name.notes}")

        lines.extend([
            "",
            "**Translation Guidelines:**",
            "1. Track which name portion is used in each POV",
            "2. Preserve the intimacy/distance implied by name choice",
            "3. When assembling full names, use provided readings",
            ""
        ])

        return "\n".join(lines)

    def generate_character_list_section(self, names: List[NamePattern]) -> str:
        """
        Generate a character list section for standard names.

        Args:
            names: List of NamePattern objects with pattern_type='standard'

        Returns:
            Formatted prompt text
        """
        if not names:
            return ""

        lines = [
            "### Character Name Reference",
            "",
            "The following character names appear in this text:",
            ""
        ]

        for name in names:
            romanized = name.romanized or self.romanize(name.reading)
            lines.append(f"- **{name.kanji}** ({name.reading}) → **{romanized}**")

        lines.append("")

        return "\n".join(lines)

    def generate_from_ruby_entries(self, entries: List[Any]) -> str:
        """
        Generate complete prompt injection from RubyEntry objects.

        Args:
            entries: List of RubyEntry objects from ruby_extractor

        Returns:
            Complete prompt text for injection
        """
        # Convert RubyEntry objects to NamePattern objects
        patterns: Dict[str, List[NamePattern]] = {
            'kirakira': [],
            'unusual_reading': [],
            'fragmented': [],
            'standard': [],
        }

        for entry in entries:
            # Handle both dict and dataclass formats
            if hasattr(entry, 'kanji'):
                kanji = entry.kanji
                reading = entry.ruby
                name_type = getattr(entry, 'name_type', 'standard')
                notes = getattr(entry, 'notes', '')
                context = getattr(entry, 'context', '')
            elif isinstance(entry, dict):
                kanji = entry.get('kanji', '')
                reading = entry.get('ruby', entry.get('reading', ''))
                name_type = entry.get('name_type', 'standard')
                notes = entry.get('notes', '')
                context = entry.get('context', '')
            else:
                continue

            pattern = NamePattern(
                kanji=kanji,
                reading=reading,
                pattern_type=name_type,
                notes=notes,
                context=context,
            )

            # Map name_type to pattern category
            if name_type == 'kirakira':
                patterns['kirakira'].append(pattern)
            elif name_type in ('unusual_reading', 'archaic'):
                patterns['unusual_reading'].append(pattern)
            elif name_type == 'fragmented':
                patterns['fragmented'].append(pattern)
            else:
                patterns['standard'].append(pattern)

        return self.generate_prompt(patterns)

    def generate_prompt(self, patterns: Dict[str, List[NamePattern]]) -> str:
        """
        Generate complete prompt injection from categorized patterns.

        Args:
            patterns: Dict mapping pattern types to lists of NamePattern objects

        Returns:
            Complete prompt text for injection
        """
        sections = []

        # Header
        sections.append("## IRREGULAR NAME HANDLING")
        sections.append("")
        sections.append("This text contains character names with non-standard readings or patterns.")
        sections.append("Pay special attention to preserve the author's naming intentions.")
        sections.append("")

        # Generate each section
        if patterns.get('kirakira'):
            sections.append(self.generate_kirakira_section(patterns['kirakira']))

        if patterns.get('unusual_reading'):
            sections.append(self.generate_unusual_reading_section(patterns['unusual_reading']))

        if patterns.get('fragmented'):
            sections.append(self.generate_fragmented_section(patterns['fragmented']))

        if patterns.get('standard'):
            sections.append(self.generate_character_list_section(patterns['standard']))

        return "\n".join(sections)

    def generate_minimal_reference(self, entries: List[Any]) -> str:
        """
        Generate a minimal character reference for context-limited situations.

        Args:
            entries: List of RubyEntry objects from ruby_extractor

        Returns:
            Compact character reference string
        """
        lines = ["## Character Names"]

        for entry in entries:
            if hasattr(entry, 'kanji'):
                kanji = entry.kanji
                reading = entry.ruby
                name_type = getattr(entry, 'name_type', 'standard')
            elif isinstance(entry, dict):
                kanji = entry.get('kanji', '')
                reading = entry.get('ruby', entry.get('reading', ''))
                name_type = entry.get('name_type', 'standard')
            else:
                continue

            romanized = self.romanize(reading)

            if name_type == 'kirakira':
                lines.append(f"- {kanji}→{reading} = {romanized} (kira-kira)")
            else:
                lines.append(f"- {kanji} ({reading}) = {romanized}")

        return "\n".join(lines)


def generate_name_prompt(entries: List[Any]) -> str:
    """
    Convenience function to generate prompt from ruby entries.

    Args:
        entries: List of RubyEntry objects or dicts

    Returns:
        Formatted prompt text
    """
    generator = NamePromptGenerator()
    return generator.generate_from_ruby_entries(entries)
