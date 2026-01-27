"""
HTML Builder - Generate HTML structure for PDF rendering.
"""

from pathlib import Path
from typing import List, Dict, Any
import html as html_module


class HTMLBuilder:
    """Builds HTML document for PDF generation."""
    
    def __init__(self, theme: str = 'light'):
        """
        Initialize HTML builder.
        
        Args:
            theme: 'light' or 'dark'
        """
        self.theme = theme
        self.parts = []
    
    def create_cover_page(self, cover_image: str, title: str, author: str) -> str:
        """
        Create cover page HTML.
        
        Args:
            cover_image: Path to cover image
            title: Book title
            author: Author name
            
        Returns:
            HTML string for cover page
        """
        title_escaped = html_module.escape(title)
        author_escaped = html_module.escape(author)
        
        return f'''
<div class="cover-page page-break">
    <img src="{cover_image}" alt="{title_escaped}" />
</div>
'''
    
    def create_kuchie_page(self, image_path: str, is_horizontal: bool = False) -> str:
        """
        Create kuchi-e page HTML.
        
        Args:
            image_path: Path to kuchi-e image
            is_horizontal: Whether image is landscape orientation
            
        Returns:
            HTML string for kuchi-e page
        """
        orientation_class = "horizontal" if is_horizontal else ""
        
        return f'''
<div class="kuchie-page {orientation_class} page-break">
    <img src="{image_path}" alt="Kuchi-e illustration" />
</div>
'''
    
    def create_toc_page(self, chapters: List[Dict[str, str]]) -> str:
        """
        Create table of contents page HTML.
        
        Args:
            chapters: List of chapter dicts with 'title' and 'id'
            
        Returns:
            HTML string for TOC page
        """
        toc_items = []
        for ch in chapters:
            title_escaped = html_module.escape(ch['title'])
            ch_id = ch['id']
            toc_items.append(f'    <li class="toc-item"><a href="#{ch_id}">{title_escaped}</a></li>')
        
        toc_html = '\n'.join(toc_items)
        
        return f'''
<div class="toc-page page-break">
    <h1 class="toc-title">Table of Contents</h1>
    <ol class="toc-list">
{toc_html}
    </ol>
</div>
'''
    
    def create_chapter_page(self, chapter_id: str, title: str, content: str) -> str:
        """
        Create chapter page HTML.
        
        Args:
            chapter_id: Chapter ID for anchor
            title: Chapter title
            content: Chapter content (HTML)
            
        Returns:
            HTML string for chapter
        """
        title_escaped = html_module.escape(title)
        
        return f'''
<div class="chapter" id="{chapter_id}">
    <h1 class="chapter-title">{title_escaped}</h1>
    {content}
</div>
'''
    
    def assemble_document(
        self,
        title: str,
        author: str,
        css: str,
        parts: List[str]
    ) -> str:
        """
        Assemble complete HTML document.
        
        Args:
            title: Book title
            author: Author name
            css: CSS stylesheet
            parts: List of HTML parts (cover, kuchie, toc, chapters)
            
        Returns:
            Complete HTML document string
        """
        title_escaped = html_module.escape(title)
        author_escaped = html_module.escape(author)
        
        body_content = '\n'.join(parts)
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="author" content="{author_escaped}">
    <title>{title_escaped}</title>
    <style>
{css}
    </style>
</head>
<body>
{body_content}
</body>
</html>
'''
