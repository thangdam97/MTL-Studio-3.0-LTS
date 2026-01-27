#!/usr/bin/env python3
"""
Verification script to confirm anti-AI-ism modules are properly integrated.

This script tests:
1. Module files exist and are loadable
2. Master prompt references the modules
3. PromptLoader correctly injects module content
4. Final system instruction contains anti-AI-ism directives
"""

import sys
from pathlib import Path

# Add pipeline to path
pipeline_root = Path(__file__).parent
sys.path.insert(0, str(pipeline_root))

from pipeline.translator.prompt_loader import PromptLoader
from pipeline.translator.config import get_master_prompt_path, get_modules_directory

def verify_module_files():
    """Check that anti-AI-ism module files exist."""
    print("=" * 70)
    print("STEP 1: Verifying Module Files")
    print("=" * 70)

    modules_dir = get_modules_directory()
    print(f"Modules directory: {modules_dir}")

    required_modules = [
        "ANTI_EXPOSITION_DUMP_MODULE.md",
        "ANTI_FORMAL_LANGUAGE_MODULE.md"
    ]

    all_found = True
    for module_name in required_modules:
        module_path = modules_dir / module_name
        exists = module_path.exists()
        status = "✓" if exists else "✗"
        print(f"  {status} {module_name}: {module_path}")

        if exists:
            size_kb = module_path.stat().st_size / 1024
            print(f"      Size: {size_kb:.1f}KB")
        else:
            all_found = False

    print()
    return all_found

def verify_master_prompt_references():
    """Check that master prompt references anti-AI-ism modules."""
    print("=" * 70)
    print("STEP 2: Verifying Master Prompt References")
    print("=" * 70)

    master_prompt_path = get_master_prompt_path()
    print(f"Master prompt: {master_prompt_path}")

    with open(master_prompt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    required_refs = [
        "ANTI_EXPOSITION_DUMP_MODULE.md",
        "ANTI_FORMAL_LANGUAGE_MODULE.md",
        "ANTI_AI_ISM_ENFORCEMENT"
    ]

    all_found = True
    for ref in required_refs:
        found = ref in content
        status = "✓" if found else "✗"
        print(f"  {status} Contains reference to: {ref}")

        if not found:
            all_found = False

    # Check for quality gate
    if "<QUALITY_GATE>" in content:
        print("  ✓ Quality gate checklist present")
    else:
        print("  ✗ Quality gate checklist MISSING")
        all_found = False

    print()
    return all_found

def verify_prompt_loader_injection():
    """Test that PromptLoader correctly loads and injects modules."""
    print("=" * 70)
    print("STEP 3: Testing PromptLoader Injection")
    print("=" * 70)

    loader = PromptLoader()

    # Load modules
    print("Loading RAG modules...")
    modules = loader.load_rag_modules()

    anti_exposition = "ANTI_EXPOSITION_DUMP_MODULE.md" in modules
    anti_formality = "ANTI_FORMAL_LANGUAGE_MODULE.md" in modules

    print(f"  {'✓' if anti_exposition else '✗'} ANTI_EXPOSITION_DUMP_MODULE.md loaded")
    print(f"  {'✓' if anti_formality else '✗'} ANTI_FORMAL_LANGUAGE_MODULE.md loaded")

    if not (anti_exposition and anti_formality):
        print("\n✗ FAILED: Not all anti-AI-ism modules loaded")
        return False

    # Build system instruction
    print("\nBuilding system instruction with module injection...")
    system_instruction = loader.build_system_instruction()

    # Verify injection
    print("\nVerifying injected content:")

    checks = [
        ("ANTI_EXPOSITION_DUMP_MODULE.md", "<!-- START MODULE: ANTI_EXPOSITION_DUMP_MODULE.md -->"),
        ("ANTI_FORMAL_LANGUAGE_MODULE.md", "<!-- START MODULE: ANTI_FORMAL_LANGUAGE_MODULE.md -->"),
        ("Show don't tell", "SHOW, DON'T TELL"),
        ("Casual register directive", "CASUAL REGISTER FOR TEEN DIALOGUE"),
        ("Quality gate", "<QUALITY_GATE>"),
        ("Contraction enforcement", "80%+ usage"),
        ("Emotion showing", 'Replace "felt [emotion]"'),
    ]

    all_present = True
    for description, search_term in checks:
        found = search_term in system_instruction
        status = "✓" if found else "✗"
        print(f"  {status} {description}")
        if not found:
            all_present = False

    # Size check
    size_kb = len(system_instruction.encode('utf-8')) / 1024
    print(f"\nFinal system instruction size: {size_kb:.1f}KB")

    if size_kb > 1000:
        print(f"  ⚠ Warning: System instruction is large ({size_kb:.1f}KB). May impact TPM.")

    print()
    return all_present

def verify_user_prompt_hints():
    """Check that user prompt includes anti-AI-ism hints."""
    print("=" * 70)
    print("STEP 4: Verifying User Prompt Hints")
    print("=" * 70)

    loader = PromptLoader()

    # Build sample user prompt
    user_prompt = loader.build_translation_prompt(
        source_text="サンプルテキスト",
        chapter_title="Test Chapter",
        previous_context=None,
        name_registry=None
    )

    hints = [
        ("Contraction reminder", "80%+ contraction rate"),
        ("AI-ism warning", "Avoid AI-isms"),
    ]

    all_present = True
    for description, search_term in hints:
        found = search_term in user_prompt
        status = "✓" if found else "✗"
        print(f"  {status} {description}")
        if not found:
            all_present = False

    print()
    return all_present

def main():
    print("\n" + "=" * 70)
    print("ANTI-AI-ISM INTEGRATION VERIFICATION")
    print("=" * 70)
    print()

    results = []

    # Run verification steps
    results.append(("Module Files", verify_module_files()))
    results.append(("Master Prompt References", verify_master_prompt_references()))
    results.append(("PromptLoader Injection", verify_prompt_loader_injection()))
    results.append(("User Prompt Hints", verify_user_prompt_hints()))

    # Summary
    print("=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)

    all_passed = True
    for step_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {step_name}")
        if not passed:
            all_passed = False

    print()

    if all_passed:
        print("🎉 ALL CHECKS PASSED!")
        print()
        print("The anti-AI-ism modules are properly integrated and will be sent to")
        print("the API with every translation request. The translator will now:")
        print("  - Enforce casual register for teen dialogue")
        print("  - Use contractions 80%+ in friendly conversations")
        print("  - Show emotions through action, not labels")
        print("  - Avoid formal vocabulary (shall/procure/establishment)")
        print("  - Remove exposition dumps and over-explanations")
        print()
        print("Next steps:")
        print("  1. Test on a sample chapter to verify output quality")
        print("  2. Monitor translation logs for anti-AI-ism confirmations")
        print("  3. Compare before/after using quality metrics")
        return 0
    else:
        print("❌ VERIFICATION FAILED")
        print()
        print("Some checks did not pass. Please review the errors above.")
        print("Common fixes:")
        print("  - Ensure module files are in pipeline/modules/")
        print("  - Verify master_prompt_en_compressed.xml includes module references")
        print("  - Check that module filenames match exactly")
        return 1

if __name__ == "__main__":
    sys.exit(main())
