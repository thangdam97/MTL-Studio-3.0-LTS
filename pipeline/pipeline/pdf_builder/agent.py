"""
PDF Builder Agent - Main orchestrator for PDF generation using ReportLab.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional

from .config import get_output_dir, get_work_dir
from .pdf_generator import PDFGenerator


class PDFBuilderAgent:
    """Main PDF builder agent."""
    
    def __init__(self, work_base: Optional[Path] = None):
        """Initialize PDF builder agent."""
        self.work_base = Path(work_base) if work_base else get_work_dir()
    
    def build_pdf(
        self,
        volume_id: str,
        theme: str = 'light',
        skip_qc: bool = False
    ) -> bool:
        """Build PDF from manifest."""
        print(f"\\n{'='*60}")
        print(f"PDF BUILDER - Building: {volume_id}")
        print(f"Theme: {theme}")
        print(f"{'='*60}\\n")
        
        # Load manifest
        work_dir = self.work_base / volume_id
        manifest_path = work_dir / "manifest.json"
        
        if not manifest_path.exists():
            print(f"[ERROR] Manifest not found: {manifest_path}")
            return False
        
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        print(f"[STEP 1/5] Loading manifest...")
        metadata = manifest.get('metadata', {})
        title = metadata.get('title', 'Untitled')
        author = metadata.get('author', 'Unknown')
        print(f"     Title: {title}")
        print(f"     Author: {author}")
        
        # Determine which themes to build
        themes_to_build = ['light', 'dark'] if theme == 'both' else [theme]
        
        # Build PDF for each theme
        for current_theme in themes_to_build:
            success = self._build_single_pdf(
                work_dir=work_dir,
                manifest=manifest,
                theme=current_theme
            )
            if not success:
                return False
        
        print(f"\\n{'='*60}")
        print("PDF BUILD COMPLETE")
        print(f"{'='*60}\\n")
        
        return True
    
    def _build_single_pdf(
        self,
        work_dir: Path,
        manifest: dict,
        theme: str
    ) -> bool:
        """Build a single PDF for specified theme."""
        metadata = manifest.get('metadata', {})
        title = metadata.get('title', 'Untitled')
        author = metadata.get('author', 'Unknown')
        
        print(f"\\n[Building {theme.upper()} mode PDF]\\n")
        
        # Step 2: Process chapters
        print(f"[STEP 2/5] Processing chapters...")
        chapters = self._process_chapters(work_dir, manifest)
        print(f"     Processed: {len(chapters)} chapters")
        
        # Step 3: Process images
        print(f"\\n[STEP 3/5] Processing images...")
        assets = manifest.get('assets', {})
        cover_image = work_dir / "assets" / assets.get('cover', 'cover.jpg')
        
        kuchie_images = []
        for kuchie in assets.get('kuchie', []):
            kuchie_path = f"assets/kuchie/{kuchie}"
            is_horizontal = bool(re.search(r'\\d+-\\d+', kuchie))
            kuchie_images.append((kuchie_path, is_horizontal))
        
        print(f"     Found: {len(kuchie_images)} kuchi-e")
        
        # Step 4: Generate PDF
        print(f"\\n[STEP 4/5] Generating PDF...")
        output_dir = get_output_dir()
        output_dir.mkdir(parents=True, exist_ok=True)
        
        theme_suffix = f"_{theme.capitalize()}" if theme != 'light' else ""
        pdf_filename = f"{title[:50]}{theme_suffix}.pdf"
        pdf_path = output_dir / pdf_filename
        
        generator = PDFGenerator(theme=theme)
        success = generator.generate_pdf(
            output_path=pdf_path,
            title=title,
            author=author,
            cover_image=cover_image if cover_image.exists() else None,
            kuchie_images=kuchie_images,
            chapters=chapters,
            base_path=work_dir
        )
        
        if success:
            file_size = generator.get_file_size(pdf_path)
            print(f"     [OK] PDF created: {pdf_filename}")
            print(f"     Size: {file_size}")
            print(f"     Path: {pdf_path}")
        else:
            print(f"     [ERROR] PDF generation failed")
            return False
        
        return True
    
    def _process_chapters(
        self,
        work_dir: Path,
        manifest: dict
    ) -> List[dict]:
        """Process markdown chapters."""
        chapters_data = manifest.get('chapters', [])
        chapters_data = sorted(chapters_data, key=lambda ch: ch.get('toc_order', 999))
        
        en_dir = work_dir / "EN"
        chapters = []
        
        for ch_data in chapters_data:
            chapter_id = ch_data.get('id', '')
            source_file = ch_data.get('source_file', '')
            title = ch_data.get('title', 'Untitled')
            
            md_path = en_dir / source_file
            if not md_path.exists():
                print(f"     [SKIP] Not found: {source_file}")
                continue
            
            with open(md_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            paragraphs = self._markdown_to_paragraphs(markdown_content)
            
            chapters.append({
                'id': chapter_id,
                'title': title,
                'paragraphs': paragraphs,
                'base_path': work_dir  # Add base path for image resolution
            })
            
            print(f"     [OK] {source_file}")
        
        return chapters
    
    def _markdown_to_paragraphs(self, markdown: str) -> List[str]:
        """Convert markdown to list of paragraphs."""
        # Remove title
        lines = markdown.split('\n')
        if lines and lines[0].startswith('#'):
            lines = lines[1:]
        
        paragraphs = []
        current_para = []
        
        for line in lines:
            line = line.strip()
            
            if not line:
                if current_para:
                    para_text = ' '.join(current_para)
                    para_text = self._process_inline_markdown(para_text)
                    paragraphs.append(para_text)
                    current_para = []
                continue
            
            # Check if line is an image
            if line.startswith('![') or line.startswith('<img'):
                # Finish current paragraph first
                if current_para:
                    para_text = ' '.join(current_para)
                    para_text = self._process_inline_markdown(para_text)
                    paragraphs.append(para_text)
                    current_para = []
                
                # Extract image path and add as special marker
                img_path = self._extract_image_path(line)
                if img_path:
                    paragraphs.append(f'[IMAGE:{img_path}]')
                continue
            
            # Regular text line - add to current paragraph
            current_para.append(line)
        
        # Don't forget the final paragraph!
        if current_para:
            para_text = ' '.join(current_para)
            para_text = self._process_inline_markdown(para_text)
            paragraphs.append(para_text)
        
        return paragraphs
    
    def _extract_image_path(self, line: str) -> Optional[str]:
        """Extract image path from markdown or HTML image tag."""
        # Try markdown format: ![alt](path)
        match = re.search(r'!\[.*?\]\((.+?)\)', line)
        if match:
            return match.group(1)
        
        # Try HTML format: <img src="path" />
        match = re.search(r'src="(.+?)"', line)
        if match:
            return match.group(1)
        
        return None
    
    def _process_inline_markdown(self, text: str) -> str:
        """Process inline markdown (bold, italic)."""
        # Bold
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)
        
        # Italic
        text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
        text = re.sub(r'_(.+?)_', r'<i>\1</i>', text)
        
        return text


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="PDF Builder - Generate professional light novel PDFs"
    )
    parser.add_argument("volume_id", type=str, help="Volume ID (WORK directory name)")
    parser.add_argument(
        "--theme",
        type=str,
        choices=['light', 'dark', 'both'],
        default='light',
        help="PDF theme (default: light)"
    )
    parser.add_argument(
        "--skip-qc",
        action='store_true',
        help="Skip quality checks"
    )
    
    args = parser.parse_args()
    
    agent = PDFBuilderAgent()
    success = agent.build_pdf(
        volume_id=args.volume_id,
        theme=args.theme,
        skip_qc=args.skip_qc
    )
    
    exit(0 if success else 1)
