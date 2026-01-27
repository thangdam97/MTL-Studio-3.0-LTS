"""
CJK Artifact Cleaner - Detects and removes stray Chinese characters in Japanese text.

This module identifies Chinese characters that have leaked into Japanese source text
during EPUB extraction. It uses context-aware detection to distinguish between:
- Valid Japanese Kanji (surrounded by hiragana/katakana)
- Stray Chinese characters (isolated, no Japanese neighbors)
"""

import re
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass


@dataclass
class CJKArtifact:
    """Detected CJK artifact with context."""
    line_number: int
    char: str
    position: int
    left_context: str
    right_context: str
    confidence: float
    reason: str


class CJKArtifactCleaner:
    """Detects and optionally removes stray CJK characters from text."""
    
    # Common Japanese Kanji (JLPT N5-N1, newspaper frequency)
    # Top 2000+ most common kanji used in Japanese
    COMMON_JAPANESE_KANJI = set("""
        一二三四五六七八九十百千万円年月日時分人大小中学生先
        校本書店国会社名語文字目手足口耳心体話言読書見聞食飲
        行来帰入出上下左右前後東西南北内外間近遠高安多少長新
        古明早今毎週次方何私達彼女男子母父兄弟姉妹友達気持思
        考知分使作勉強仕事休買売開始終教室家族親切元冷暖涼熱
        好悪楽面白便利不自由物品質問答試験合格失敗事故理由必
        要英語漢歌音楽映画写真旅行病院薬医者看護婦交通電車汽
        自動車飛機船地図駅道路橋建林公園海山川空天気雨雪風花
        春夏秋冬朝昼夜晩色青赤黒白茶等安全危険注意番号値段代
        金払借貸貧困難易忘覚変化同世界都府県市区町村島部屋着
        服帽眼鏡靴袋箱机椅板壁窓戸棚鍵紙本誌新聞雑類種様計画
        約束意味感情愛恋心配不安嬉幸福運命信頼相談決定判断選
        比較参加案内連絡伝達報告説明表現理解確認認検査調査研究
        発見存在続増減加減乗除割引当係関連結婚離別再会出会別
        若老幼児童孫祖父母経験記憶想像夢希望願望欲求満足失望
        残念後悔反省責任義務権利法律規則禁止許可許婚約恋愛結婚
        離婚再婚独身既婚未婚家庭生活暮毎週末平日休祝祭典式礼
        祝賀慶弔喜怒哀楽笑泣叫黙静騒音響声調歌曲演奏練習芸術
        美術絵画彫刻建築設計技術科化物理数算式図形線点面積体積
        容器液固態様状況況条件場合際他互相互換代替補充追加削除
        修正訂正改善進歩向発展成長変退後遅延期限定時刻秒瞬速遅
        急速緩慢順序列並例示範模倣真偽正誤適当然異常例外特別
        殊普通常識非識別認証明証券票帳簿録登載掲示告知通報導誘
        致招待迎送別辞退断容承諾許認批評価値格等級階段位置所在
        存保管蔵蓄積貯余残欠損壊破砕片断絶途径過経由巡回転移動
        運搬輸送配達受取引渡授与贈寄付提供支援助協力団結束縛拘
        制限禁抑圧迫害奪略盗窃賊罪犯法違反則規範準標基底根源因
        果効影響響応答反質疑謎解析評論証議論争競闘戦敗勝負担任
        命令指示導援救護衛守防攻撃破壊滅亡死亡存続永遠久遠暫瞬
        現在過未将既然偶奇怪妙異変突発急激徐々段階層深浅厚薄広
        狭密粗細太太陽光星夜闇暗照輝眩盲視観察覧監督導師範教授
        講演述語談論辯弁解釈訳翻通訳訳註釈義定確固堅硬軟柔弱強
        力勢威圧迫勧誘惑魅魔鬼怖恐懼畏敬尊崇拝祈祷願念仏神聖俗
    """.replace('\n', '').replace(' ', ''))
    
    # Known Chinese-only or rare characters that shouldn't appear in Japanese
    CHINESE_ONLY_CHARS = set("""
        爲這個們嗎呢啊吧喔哦唄咧啦哪誰係喺啲嘅嗰噉乜咁點樣邊
        冇未曾經緊住咗過喇啩囉啫嚟佢哋你妳您俺咱阮伲偌倆仨
    """.replace('\n', '').replace(' ', ''))
    
    # Common Chinese character pairs rarely used in Japanese
    CHINESE_COMPOUNDS = {
        '有好', '爲了', '這個', '那個', '什麼', '怎麼', '為什', '還是',
        '可以', '不能', '應該', '會不', '沒有', '已經', '正在', '將要',
    }
    
    def __init__(self, strict_mode: bool = False, min_confidence: float = 0.7, 
                 context_window: int = 5):
        """
        Initialize CJK artifact cleaner.
        
        Args:
            strict_mode: If True, auto-removes artifacts. If False, only detects.
            min_confidence: Minimum confidence threshold (0.0-1.0) for flagging.
            context_window: Number of characters to check on each side.
        """
        self.strict_mode = strict_mode
        self.min_confidence = min_confidence
        self.context_window = context_window
        
    def detect_artifacts(self, text: str) -> List[CJKArtifact]:
        """
        Detect CJK artifacts in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of detected artifacts
        """
        artifacts = []
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Find all CJK Unified Ideographs (U+4E00 to U+9FFF)
            for match in re.finditer(r'[\u4E00-\u9FFF]', line):
                char = match.group()
                pos = match.start()
                
                # Extract context
                left_start = max(0, pos - self.context_window)
                right_end = min(len(line), pos + self.context_window + 1)
                
                left_context = line[left_start:pos]
                right_context = line[pos+1:right_end]
                
                # Calculate suspicion score
                confidence, reason = self._calculate_suspicion(
                    char, left_context, right_context
                )
                
                if confidence >= self.min_confidence:
                    artifacts.append(CJKArtifact(
                        line_number=line_num,
                        char=char,
                        position=pos,
                        left_context=left_context,
                        right_context=right_context,
                        confidence=confidence,
                        reason=reason
                    ))
        
        return artifacts
    
    def _calculate_suspicion(self, char: str, left_ctx: str, 
                            right_ctx: str) -> Tuple[float, str]:
        """
        Calculate suspicion score for a CJK character.
        
        Args:
            char: The character to evaluate
            left_ctx: Left context string
            right_ctx: Right context string
            
        Returns:
            Tuple of (confidence_score, reason_string)
        """
        score = 0.0
        reasons = []
        
        # Factor 1: Known Chinese-only character (HIGH PRIORITY)
        if char in self.CHINESE_ONLY_CHARS:
            score += 0.4
            reasons.append("Chinese-only char")
        
        # Factor 2: Not in common Japanese Kanji list (MEDIUM)
        elif char not in self.COMMON_JAPANESE_KANJI:
            score += 0.25
            reasons.append("Rare in Japanese")
        
        # Factor 3: Check for Chinese compound patterns
        if left_ctx and left_ctx[-1] + char in self.CHINESE_COMPOUNDS:
            score += 0.15
            reasons.append(f"Chinese compound: {left_ctx[-1]}{char}")
        if right_ctx and char + right_ctx[0] in self.CHINESE_COMPOUNDS:
            score += 0.15
            reasons.append(f"Chinese compound: {char}{right_ctx[0]}")
        
        # Factor 4: No Japanese kana neighbors (CRITICAL)
        has_left_kana = any(self._is_japanese_kana(c) for c in left_ctx)
        has_right_kana = any(self._is_japanese_kana(c) for c in right_ctx)
        
        if not has_left_kana and not has_right_kana:
            score += 0.3
            reasons.append("No kana neighbors")
        elif not has_left_kana:
            score += 0.15
            reasons.append("No left kana")
        elif not has_right_kana:
            score += 0.15
            reasons.append("No right kana")
        
        # Factor 5: Surrounded by Latin/Vietnamese characters (SUSPICIOUS)
        if left_ctx and self._is_latin_or_vietnamese(left_ctx[-1]):
            score += 0.1
            reasons.append("Left: Latin/Vietnamese")
        if right_ctx and self._is_latin_or_vietnamese(right_ctx[0]):
            score += 0.1
            reasons.append("Right: Latin/Vietnamese")
        
        reason = "; ".join(reasons) if reasons else "OK"
        return min(score, 1.0), reason
    
    def _is_japanese_kana(self, char: str) -> bool:
        """Check if character is hiragana or katakana."""
        if not char:
            return False
        code = ord(char)
        # Hiragana: U+3040–U+309F, Katakana: U+30A0–U+30FF
        return (0x3040 <= code <= 0x309F) or (0x30A0 <= code <= 0x30FF)
    
    def _is_latin_or_vietnamese(self, char: str) -> bool:
        """Check if character is Latin alphabet or Vietnamese."""
        if not char:
            return False
        code = ord(char)
        # Basic Latin + Latin-1 Supplement + Latin Extended-A/B (for Vietnamese)
        return (0x0041 <= code <= 0x007A) or \
               (0x00C0 <= code <= 0x024F) or \
               char in 'ăâêôơưđĂÂÊÔƠƯĐ'
    
    def clean_file(self, filepath: Path) -> Dict[str, any]:
        """
        Clean a single file, detecting and optionally removing artifacts.
        
        Args:
            filepath: Path to file to clean
            
        Returns:
            Dictionary with statistics and results
        """
        if not filepath.exists():
            return {
                'file': str(filepath),
                'error': 'File not found',
                'artifacts': [],
                'modified': False
            }
        
        # Read file
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Detect artifacts
        artifacts = self.detect_artifacts(content)
        
        result = {
            'file': filepath.name,
            'artifacts': len(artifacts),
            'modified': False,
            'details': []
        }
        
        if not artifacts:
            return result
        
        # Log artifacts
        for artifact in artifacts:
            detail = {
                'line': artifact.line_number,
                'char': artifact.char,
                'code': f"U+{ord(artifact.char):04X}",
                'confidence': f"{artifact.confidence:.2f}",
                'context': f"...{artifact.left_context}[{artifact.char}]{artifact.right_context}...",
                'reason': artifact.reason
            }
            result['details'].append(detail)
        
        # Auto-remove if strict mode
        if self.strict_mode and artifacts:
            cleaned_content = content
            # Remove artifacts (sort by position descending to maintain indices)
            lines = cleaned_content.split('\n')
            
            for artifact in sorted(artifacts, key=lambda a: (a.line_number, a.position), 
                                  reverse=True):
                line_idx = artifact.line_number - 1
                if line_idx < len(lines):
                    line = lines[line_idx]
                    # Remove the character
                    lines[line_idx] = line[:artifact.position] + line[artifact.position+1:]
            
            cleaned_content = '\n'.join(lines)
            
            # Write back
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            
            result['modified'] = True
        
        return result
    
    def clean_directory(self, directory: Path, pattern: str = "CHAPTER_*.md") -> Dict[str, any]:
        """
        Clean all matching files in a directory.
        
        Args:
            directory: Directory to process
            pattern: Glob pattern for files to process
            
        Returns:
            Summary statistics
        """
        files = sorted(directory.glob(pattern))
        
        results = {
            'directory': str(directory),
            'files_processed': 0,
            'files_with_artifacts': 0,
            'total_artifacts': 0,
            'files_modified': 0,
            'file_results': []
        }
        
        for filepath in files:
            result = self.clean_file(filepath)
            results['files_processed'] += 1
            
            if result.get('artifacts', 0) > 0:
                results['files_with_artifacts'] += 1
                results['total_artifacts'] += result['artifacts']
                results['file_results'].append(result)
            
            if result.get('modified', False):
                results['files_modified'] += 1
        
        return results
    
    def clean_volume(self, work_dir: Path) -> Dict[str, any]:
        """
        Clean all language directories in a volume work directory.
        
        Args:
            work_dir: Volume work directory
            
        Returns:
            Global summary statistics
        """
        language_dirs = ['JP', 'EN', 'VN']  # Process all language directories
        
        global_results = {
            'volume': work_dir.name,
            'languages_processed': 0,
            'total_files': 0,
            'total_artifacts': 0,
            'files_modified': 0,
            'language_results': {}
        }
        
        for lang_dir in language_dirs:
            lang_path = work_dir / lang_dir
            if not lang_path.exists():
                continue
            
            lang_results = self.clean_directory(lang_path)
            
            if lang_results['files_processed'] > 0:
                global_results['languages_processed'] += 1
                global_results['total_files'] += lang_results['files_processed']
                global_results['total_artifacts'] += lang_results['total_artifacts']
                global_results['files_modified'] += lang_results['files_modified']
                global_results['language_results'][lang_dir] = lang_results
        
        return global_results


def format_results_report(results: Dict[str, any]) -> str:
    """
    Format results dictionary into a readable report.
    
    Args:
        results: Results from clean_volume()
        
    Returns:
        Formatted string report
    """
    lines = []
    lines.append("\n" + "="*60)
    lines.append("CJK ARTIFACT CLEANUP REPORT")
    lines.append("="*60)
    
    lines.append(f"\nVolume: {results.get('volume', 'Unknown')}")
    lines.append(f"Languages processed: {results['languages_processed']}")
    lines.append(f"Total files: {results['total_files']}")
    lines.append(f"Total artifacts found: {results['total_artifacts']}")
    lines.append(f"Files modified: {results['files_modified']}")
    
    for lang, lang_results in results.get('language_results', {}).items():
        if lang_results['files_with_artifacts'] > 0:
            lines.append(f"\n{lang} Directory:")
            lines.append(f"  Files with artifacts: {lang_results['files_with_artifacts']}")
            lines.append(f"  Total artifacts: {lang_results['total_artifacts']}")
            
            for file_result in lang_results.get('file_results', []):
                lines.append(f"\n  File: {file_result['file']}")
                lines.append(f"    Artifacts: {file_result['artifacts']}")
                
                for detail in file_result.get('details', [])[:5]:  # Show first 5
                    lines.append(f"    - Line {detail['line']}: '{detail['char']}' "
                               f"({detail['code']}) confidence={detail['confidence']}")
                    lines.append(f"      Context: {detail['context']}")
                    lines.append(f"      Reason: {detail['reason']}")
                
                if len(file_result.get('details', [])) > 5:
                    remaining = len(file_result['details']) - 5
                    lines.append(f"    ... and {remaining} more artifacts")
    
    lines.append("\n" + "="*60 + "\n")
    
    return '\n'.join(lines)
