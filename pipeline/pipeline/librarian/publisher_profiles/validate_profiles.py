#!/usr/bin/env python3
"""
Validate publisher profiles and test pattern matching.

Usage:
    python3 validate_profiles.py                    # Validate all profiles
    python3 validate_profiles.py media_factory      # Validate specific profile
    python3 validate_profiles.py --generate-regex   # Generate unified regex patterns
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def load_profile(profile_path: Path) -> Dict:
    """Load a publisher profile."""
    with open(profile_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_patterns(profile: Dict, profile_name: str) -> Tuple[bool, List[str]]:
    """
    Validate that all example filenames match their patterns.

    Returns:
        Tuple of (success, error_messages)
    """
    errors = []

    for img_type, config in profile.get("image_patterns", {}).items():
        patterns = config.get("patterns", [])
        examples = config.get("examples", [])

        if not patterns:
            errors.append(f"{profile_name}: {img_type} has no patterns defined")
            continue

        if not examples:
            errors.append(f"{profile_name}: {img_type} has no examples to test")
            continue

        # Combine all patterns for this image type
        combined_pattern = "|".join(f"(?:{p})" for p in patterns)
        regex = re.compile(f"^(?:{combined_pattern})$", re.IGNORECASE)

        # Test each example
        for example in examples:
            if not regex.match(example):
                errors.append(
                    f"{profile_name}: {img_type} pattern doesn't match example '{example}'\n"
                    f"  Patterns: {patterns}"
                )

    return (len(errors) == 0, errors)


def generate_unified_patterns(profiles: List[Dict]) -> Dict[str, str]:
    """
    Generate unified regex patterns from all profiles.

    Returns:
        Dictionary mapping image type to unified pattern
    """
    unified = {
        "cover": set(),
        "kuchie": set(),
        "illustrations": set()
    }

    for profile in profiles:
        for img_type, config in profile.get("image_patterns", {}).items():
            if img_type in unified:
                unified[img_type].update(config.get("patterns", []))

    # Combine patterns
    result = {}
    for img_type, patterns in unified.items():
        if patterns:
            combined = "|".join(f"(?:{p})" for p in sorted(patterns))
            result[img_type] = f"^(?:{combined})$"

    return result


def print_profile_summary(profile: Dict, profile_name: str):
    """Print a summary of a publisher profile."""
    print(f"\n{'='*60}")
    print(f"Profile: {profile_name}")
    print(f"{'='*60}")
    print(f"Publisher: {profile['publisher']}")
    if 'publisher_ja' in profile:
        print(f"Japanese:   {profile['publisher_ja']}")
    print(f"Country:    {profile.get('country', 'Unknown')}")

    if 'notes' in profile:
        print(f"\nNotes: {profile['notes']}")

    print(f"\nImage Patterns:")
    for img_type, config in profile.get("image_patterns", {}).items():
        patterns = config.get("patterns", [])
        examples = config.get("examples", [])
        print(f"  {img_type.capitalize()}:")
        print(f"    Patterns: {len(patterns)}")
        print(f"    Examples: {examples[:3]}{'...' if len(examples) > 3 else ''}")

    print(f"\nTOC Structure:")
    toc = profile.get("toc_structure", {})
    print(f"  Format: {toc.get('format', 'Unknown')}")
    print(f"  Nav XHTML: {toc.get('has_nav_xhtml', False)}")
    print(f"  TOC NCX: {toc.get('has_toc_ncx', False)}")
    print(f"  Visual TOC: {toc.get('has_visual_toc', False)}")

    test_cases = profile.get("test_cases", [])
    print(f"\nTest Cases: {len(test_cases)} verified" if test_cases else "\nTest Cases: None")


def main():
    """Main validation script."""
    script_dir = Path(__file__).parent
    profile_files = list(script_dir.glob("*.json"))

    if not profile_files:
        print("No profile files found!")
        return 1

    # Parse arguments
    generate_regex = "--generate-regex" in sys.argv
    specific_profile = None
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            specific_profile = arg

    # Filter profiles if specific one requested
    if specific_profile:
        profile_files = [f for f in profile_files if specific_profile in f.stem]
        if not profile_files:
            print(f"Profile '{specific_profile}' not found!")
            return 1

    # Load all profiles
    profiles = []
    for profile_file in sorted(profile_files):
        try:
            profile = load_profile(profile_file)
            profiles.append((profile_file.stem, profile))
        except Exception as e:
            print(f"Error loading {profile_file.name}: {e}")
            return 1

    # Validate each profile
    all_valid = True
    for profile_name, profile in profiles:
        print_profile_summary(profile, profile_name)

        valid, errors = validate_patterns(profile, profile_name)
        if not valid:
            all_valid = False
            print(f"\n❌ Validation FAILED:")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"\n✅ Validation PASSED")

    # Generate unified patterns if requested
    if generate_regex:
        print(f"\n{'='*60}")
        print("Unified Pattern Regexes")
        print(f"{'='*60}")

        unified = generate_unified_patterns([p for _, p in profiles])
        for img_type, pattern in unified.items():
            print(f"\n{img_type.upper()}_PATTERN = re.compile(r'{pattern}', re.IGNORECASE)")

    return 0 if all_valid else 1


if __name__ == "__main__":
    sys.exit(main())
