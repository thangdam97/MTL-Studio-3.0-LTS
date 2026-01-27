#!/usr/bin/env python3
"""Copy translated metadata from backup to new file."""

import json
import sys
from pathlib import Path

def main():
    work_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    
    backup_file = work_dir / 'metadata_en.json.backup'
    output_file = work_dir / 'metadata_en.json'
    
    print(f"Loading backup from: {backup_file}")
    
    # Load backup metadata_en.json with translations
    with open(backup_file, 'r', encoding='utf-8') as f:
        old_metadata = json.load(f)
    
    # Load new metadata_en.json (if exists, or create empty)
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            new_metadata = json.load(f)
    except:
        new_metadata = {}
    
    # Copy all translated content from old to new
    new_metadata['title_en'] = old_metadata.get('title_en', '')
    new_metadata['author_en'] = old_metadata.get('author_en', '')
    new_metadata['illustrator_en'] = old_metadata.get('illustrator_en', 'N/A')
    new_metadata['publisher_en'] = old_metadata.get('publisher_en', '')
    new_metadata['chapters'] = old_metadata.get('chapters', [])
    new_metadata['character_names'] = old_metadata.get('character_names', {})
    new_metadata['glossary'] = old_metadata.get('glossary', {})
    new_metadata['target_language'] = 'en'
    new_metadata['language_code'] = 'en'
    
    # Save updated metadata_en.json
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(new_metadata, f, ensure_ascii=False, indent=2)
    
    print("✓ Copied translations from backup:")
    print(f"  Title: {new_metadata['title_en']}")
    print(f"  Author: {new_metadata['author_en']}")
    print(f"  Chapters: {len(new_metadata['chapters'])}")
    print(f"  Character names: {len(new_metadata['character_names'])}")
    print(f"  Glossary terms: {len(new_metadata['glossary'])}")

if __name__ == '__main__':
    main()
