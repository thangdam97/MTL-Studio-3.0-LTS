#!/usr/bin/env python3
"""
CJK Character Validator for Vietnamese Translation Quality Control

Validates translated Vietnamese text for unwanted CJK character leaks using
the rules defined in cjk_validation_rules.json.

Usage:
    python cjk_validator.py <file_or_directory>
    python cjk_validator.py --scan-volume <volume_id>
"""

import re
import json
import sys
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    file_path: Path
    line_number: int
    line_content: str
    issue_type: str
    severity: Severity
    matched_pattern: str
    suggestion: str = ""


class CJKValidator:
    """Validates Vietnamese text for CJK character leaks."""
    
    def __init__(self, config_path: Path = None):
        if config_path is None:
            # Config is in pipeline/config/, script is in pipeline/scripts/
            config_path = Path(__file__).parent.parent / "config" / "cjk_validation_rules.json"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns from config."""
        # Main CJK detection pattern (excluding allowed contexts)
        cjk_ranges = [
            self.config['character_ranges'][key]['range'] 
            for key in self.config['character_ranges']
            if self.config['character_ranges'][key]['severity'] == 'error'
        ]
        self.cjk_pattern = re.compile(f"[{''.join(cjk_ranges)}]")
        
        # Allowed context patterns
        self.allowed_patterns = [
            re.compile(ctx['pattern'])
            for ctx in self.config['allowed_contexts'].values()
        ]
        
        # Leak detection patterns
        self.leak_patterns = []
        for leak_type in self.config['common_leak_patterns'].values():
            if isinstance(leak_type, list):
                for pattern_def in leak_type:
                    if 'pattern' in pattern_def:
                        self.leak_patterns.append({
                            'regex': re.compile(pattern_def['pattern']),
                            'type': pattern_def['description'],
                            'severity': Severity(pattern_def['severity'])
                        })
    
    def _is_in_allowed_context(self, text: str, match_start: int, match_end: int) -> bool:
        """Check if CJK character is in an allowed context."""
        for allowed_pattern in self.allowed_patterns:
            for allowed_match in allowed_pattern.finditer(text):
                if allowed_match.start() <= match_start and match_end <= allowed_match.end():
                    return True
        return False
    
    def validate_text(self, text: str, file_path: Path = None) -> List[ValidationIssue]:
        """Validate a text string for CJK leaks."""
        issues = []
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines, start=1):
            # Skip empty lines and markdown headers
            if not line.strip() or line.strip().startswith('#'):
                continue
            
            # Check for CJK characters
            for match in self.cjk_pattern.finditer(line):
                # Check if in allowed context
                if self._is_in_allowed_context(line, match.start(), match.end()):
                    continue
                
                # Get character info
                char = match.group()
                char_code = f"U+{ord(char):04X}"
                
                # Try to find suggested replacement
                suggestion = self._get_suggestion(char, line)
                
                issue = ValidationIssue(
                    file_path=file_path or Path("unknown"),
                    line_number=line_num,
                    line_content=line.strip(),
                    issue_type=f"CJK Character Leak: {char} ({char_code})",
                    severity=Severity.ERROR,
                    matched_pattern=char,
                    suggestion=suggestion
                )
                issues.append(issue)
            
            # Check for specific leak patterns
            for pattern_def in self.leak_patterns:
                for match in pattern_def['regex'].finditer(line):
                    if not self._is_in_allowed_context(line, match.start(), match.end()):
                        issue = ValidationIssue(
                            file_path=file_path or Path("unknown"),
                            line_number=line_num,
                            line_content=line.strip(),
                            issue_type=pattern_def['type'],
                            severity=pattern_def['severity'],
                            matched_pattern=match.group(),
                            suggestion=self._get_suggestion_for_pattern(match.group())
                        )
                        issues.append(issue)
        
        return issues
    
    def _get_suggestion(self, char: str, context: str) -> str:
        """Get replacement suggestion for a CJK character."""
        # Check replacement mappings
        for category in ['common_chinese_leaks', 'common_japanese_leaks', 'common_korean_leaks']:
            if category in self.config['replacement_mappings']:
                if char in self.config['replacement_mappings'][category]:
                    return f"Replace with: {self.config['replacement_mappings'][category][char]}"
        
        # Check punctuation
        if char in self.config['replacement_mappings'].get('punctuation_replacements', {}):
            return f"Replace with: {self.config['replacement_mappings']['punctuation_replacements'][char]}"
        
        return "Translate this character to Vietnamese"
    
    def _get_suggestion_for_pattern(self, matched_text: str) -> str:
        """Get suggestion for a pattern match."""
        # Extract CJK portion and try to find replacement
        cjk_chars = ''.join(self.cjk_pattern.findall(matched_text))
        if cjk_chars:
            for category in ['common_chinese_leaks', 'common_japanese_leaks']:
                if category in self.config['replacement_mappings']:
                    if cjk_chars in self.config['replacement_mappings'][category]:
                        vietnamese = self.config['replacement_mappings'][category][cjk_chars]
                        suggested = matched_text.replace(cjk_chars, vietnamese)
                        return f"Suggested fix: {suggested}"
        
        return "Translate CJK portion to Vietnamese"
    
    def validate_file(self, file_path: Path) -> List[ValidationIssue]:
        """Validate a single markdown file."""
        if not file_path.exists():
            return []
        
        text = file_path.read_text(encoding='utf-8')
        return self.validate_text(text, file_path)
    
    def validate_directory(self, dir_path: Path, pattern: str = "*.md") -> Dict[Path, List[ValidationIssue]]:
        """Validate all markdown files in a directory."""
        results = {}
        for file_path in dir_path.glob(pattern):
            issues = self.validate_file(file_path)
            if issues:
                results[file_path] = issues
        return results
    
    def validate_volume(self, volume_id: str, work_dir: Path = None) -> Dict[Path, List[ValidationIssue]]:
        """Validate all translated chapters in a volume."""
        if work_dir is None:
            work_dir = Path(__file__).parent.parent / "WORK"
        
        volume_base = work_dir / volume_id
        if not volume_base.exists():
            print(f"Error: Volume directory not found: {volume_base}")
            return {}
        
        # Auto-detect target language from manifest
        manifest_path = volume_base / "manifest.json"
        target_lang = "EN"  # Default to EN
        
        if manifest_path.exists():
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                    # Check translator state for target language
                    translator_state = manifest.get("pipeline_state", {}).get("translator", {})
                    if "target_language" in translator_state:
                        target_lang = translator_state["target_language"].upper()
                    else:
                        # Fallback to metadata
                        target_lang = manifest.get("metadata", {}).get("target_language", "en").upper()
            except Exception as e:
                print(f"Warning: Could not read manifest, defaulting to EN folder: {e}")
        
        volume_path = volume_base / target_lang
        if not volume_path.exists():
            print(f"Error: Translation folder not found: {volume_path}")
            print(f"Expected folder: {target_lang}/ (based on manifest target_language)")
            return {}
        
        print(f"Validating {target_lang} translations in: {volume_path}")
        return self.validate_directory(volume_path, "CHAPTER_*.md")
    
    def print_report(self, results: Dict[Path, List[ValidationIssue]]):
        """Print validation report."""
        total_errors = 0
        total_warnings = 0
        
        print("\n" + "="*80)
        print("CJK VALIDATION REPORT")
        print("="*80 + "\n")
        
        if not results:
            print("✓ No CJK character leaks detected!\n")
            return
        
        for file_path, issues in sorted(results.items()):
            print(f"\n📄 {file_path.name}")
            print("-" * 80)
            
            for issue in issues:
                icon = "❌" if issue.severity == Severity.ERROR else "⚠️"
                print(f"\n{icon} Line {issue.line_number}: {issue.issue_type}")
                print(f"   Text: {issue.line_content[:100]}...")
                print(f"   Match: '{issue.matched_pattern}'")
                if issue.suggestion:
                    print(f"   💡 {issue.suggestion}")
                
                if issue.severity == Severity.ERROR:
                    total_errors += 1
                else:
                    total_warnings += 1
        
        print("\n" + "="*80)
        print(f"SUMMARY: {total_errors} errors, {total_warnings} warnings")
        print("="*80 + "\n")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate Vietnamese translations for CJK character leaks")
    parser.add_argument('path', nargs='?', help='File or directory to validate')
    parser.add_argument('--scan-volume', metavar='VOLUME_ID', help='Validate specific volume')
    parser.add_argument('--config', help='Path to validation rules JSON')
    
    args = parser.parse_args()
    
    # Load validator
    config_path = Path(args.config) if args.config else None
    validator = CJKValidator(config_path)
    
    # Determine what to validate
    if args.scan_volume:
        print(f"Scanning volume: {args.scan_volume}")
        results = validator.validate_volume(args.scan_volume)
    elif args.path:
        path = Path(args.path)
        if path.is_file():
            issues = validator.validate_file(path)
            results = {path: issues} if issues else {}
        elif path.is_dir():
            results = validator.validate_directory(path)
        else:
            print(f"Error: Path not found: {path}")
            return 1
    else:
        parser.print_help()
        return 1
    
    # Print report
    validator.print_report(results)
    
    # Return exit code
    return 1 if any(results.values()) else 0


if __name__ == '__main__':
    sys.exit(main())
