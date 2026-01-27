#!/usr/bin/env python3
"""
Chapter 2 Chunked Translation Script
Translates Chapter 2 in 3 parts to avoid safety filter issues.
"""

import sys
import json
from pathlib import Path

# Add pipeline to path
pipeline_root = Path(__file__).parent.parent
sys.path.insert(0, str(pipeline_root))

from pipeline.common.gemini_client import GeminiClient

def translate_chunk(chunk_num: int, work_dir: Path, gemini_client: GeminiClient):
    """Translate a single chunk of Chapter 2."""
    
    # Input/output paths
    input_path = work_dir / f"JP/CHAPTER_02_CHUNKS/part{chunk_num}.md"
    output_path = work_dir / f"EN/CHAPTER_02_CHUNKS/part{chunk_num}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"Translating Chapter 2 - Part {chunk_num}/3")
    print(f"{'='*60}")
    print(f"Input: {input_path}")
    print(f"Output: {output_path}")
    
    # Load source
    with open(input_path, 'r', encoding='utf-8') as f:
        source_text = f.read()
    
    # Load master prompt
    master_prompt_path = pipeline_root / "prompts/master_prompt_en_compressed.xml"
    with open(master_prompt_path, 'r', encoding='utf-8') as f:
        system_instruction = f.read()
    
    # Build user prompt
    user_prompt = f"""Translate the following Japanese light novel text to natural, fluent English.

This is Part {chunk_num} of 3 from Chapter 2. Maintain narrative continuity and character voice.

## Source Text (Japanese):

{source_text}

## Instructions:
- Translate to natural English prose
- Preserve character names and honorifics
- Keep markdown formatting
- Maintain scene breaks (☆☆ → * * *)
- Output ONLY the translated text, no explanations
"""
    
    # Call Gemini
    try:
        response = gemini_client.generate(
            prompt=user_prompt,
            system_instruction=system_instruction,
            temperature=0.6,
            max_output_tokens=65535,
            model="gemini-2.5-flash"
        )
        
        if not response.content:
            print(f"❌ Part {chunk_num}: Empty response (safety block?)")
            return False
        
        # Save output
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(response.content)
        
        # Stats
        input_tokens = response.input_tokens
        output_tokens = response.output_tokens
        output_lines = len(response.content.split('\n'))
        
        print(f"✅ Part {chunk_num} completed:")
        print(f"   Input tokens: {input_tokens:,}")
        print(f"   Output tokens: {output_tokens:,}")
        print(f"   Output lines: {output_lines}")
        
        return True
        
    except Exception as e:
        print(f"❌ Part {chunk_num} failed: {e}")
        return False

def merge_chunks(work_dir: Path):
    """Merge the 3 translated chunks back into Chapter 2."""
    
    print(f"\n{'='*60}")
    print("Merging translated chunks...")
    print(f"{'='*60}")
    
    output_path = work_dir / "EN/CHAPTER_02.md"
    
    # Read all parts
    parts = []
    for i in range(1, 4):
        part_path = work_dir / f"EN/CHAPTER_02_CHUNKS/part{i}.md"
        if not part_path.exists():
            print(f"❌ Part {i} not found: {part_path}")
            return False
        
        with open(part_path, 'r', encoding='utf-8') as f:
            content = f.read()
            parts.append(content)
            print(f"✓ Loaded part {i}: {len(content.split())} words")
    
    # Merge (strip trailing whitespace from parts 1-2, preserve part 3 ending)
    merged = parts[0].rstrip() + "\n\n" + parts[1].rstrip() + "\n\n" + parts[2]
    
    # Save
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(merged)
    
    # Stats
    total_lines = len(merged.split('\n'))
    total_words = len(merged.split())
    
    print(f"\n✅ Chapter 2 merged successfully:")
    print(f"   Output: {output_path}")
    print(f"   Total lines: {total_lines}")
    print(f"   Total words: {total_words}")
    
    return True

def main():
    """Main translation workflow."""
    
    # Paths
    work_dir = Path("/Users/damminhthang/Documents/WORK/AI_MODULES/MTL_STUDIO/pipeline/WORK/陰キャの俺が席替えでS級美少女に囲まれたら秘密の関係が始まった。３_20260122_16a0")
    
    # Initialize Gemini client
    print("Initializing Gemini client...")
    client = GeminiClient()
    
    # Translate each chunk
    success = True
    for chunk_num in range(1, 4):
        if not translate_chunk(chunk_num, work_dir, client):
            success = False
            break
    
    if not success:
        print("\n❌ Translation failed. Stopping.")
        return 1
    
    # Merge chunks
    if not merge_chunks(work_dir):
        print("\n❌ Merge failed.")
        return 1
    
    print(f"\n{'='*60}")
    print("✅ Chapter 2 translation complete!")
    print(f"{'='*60}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
