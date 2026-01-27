"""
PDF Generator - ReportLab-based PDF creation.

Pure Python implementation with no system dependencies.
"""

from pathlib import Path
from typing import Optional, List
from io import BytesIO

from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Image as RLImage, KeepTogether
)
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black, HexColor


class PDFGenerator:
    """Generates PDF using ReportLab."""
    
    def __init__(self, theme: str = 'light'):
        """
        Initialize PDF generator.
        
        Args:
            theme: 'light' or 'dark'
        """
        self.theme = theme
        self.setup_colors()
        self.setup_styles()
    
    def setup_colors(self):
        """Setup theme colors."""
        if self.theme == 'dark':
            self.bg_color = HexColor('#1a1a1a')
            self.text_color = HexColor('#e0e0e0')
            self.heading_color = HexColor('#ffffff')
        else:
            self.bg_color = HexColor('#ffffff')
            self.text_color = HexColor('#000000')
            self.heading_color = HexColor('#000000')
    
    def setup_styles(self):
        """Setup paragraph styles."""
        styles = getSampleStyleSheet()
        
        # Body text
        self.style_body = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontName='Times-Roman',
            fontSize=11,
            leading=17.6,  # 1.6 line height
            textColor=self.text_color,
            alignment=TA_JUSTIFY,
            firstLineIndent=11,  # 1em indent
        )
        
        # First paragraph (no indent)
        self.style_first = ParagraphStyle(
            'FirstPara',
            parent=self.style_body,
            firstLineIndent=0,
        )
        
        # Chapter title
        self.style_chapter = ParagraphStyle(
            'ChapterTitle',
            parent=styles['Heading1'],
            fontName='Times-Bold',
            fontSize=18,
            leading=22,
            textColor=self.heading_color,
            alignment=TA_CENTER,
            spaceAfter=10*mm,
        )
        
        # TOC title
        self.style_toc_title = ParagraphStyle(
            'TOCTitle',
            parent=self.style_chapter,
        )
        
        # TOC item
        self.style_toc_item = ParagraphStyle(
            'TOCItem',
            parent=styles['Normal'],
            fontName='Times-Roman',
            fontSize=11,
            leading=16,
            textColor=self.text_color,
            leftIndent=0,
            firstLineIndent=0,
        )
    
    def generate_pdf(
        self,
        output_path: Path,
        title: str,
        author: str,
        cover_image: Optional[Path],
        kuchie_images: List[tuple],
        chapters: List[dict],
        base_path: Path
    ) -> bool:
        """
        Generate PDF from content.
        
        Args:
            output_path: Where to save PDF
            title: Book title
            author: Author name
            cover_image: Path to cover image
            kuchie_images: List of (path, is_horizontal) tuples
            chapters: List of chapter dicts
            base_path: Base path for resolving image paths
            
        Returns:
            True if successful
        """
        try:
            from reportlab.platypus.doctemplate import BaseDocTemplate, PageTemplate, Frame
            
            # Create document
            doc = BaseDocTemplate(
                str(output_path),
                pagesize=A5,
                title=title,
                author=author,
            )
            
            # Define page templates
            # Cover template (no margins)
            cover_frame = Frame(0, 0, A5[0], A5[1], leftPadding=0, bottomPadding=0,
                              rightPadding=0, topPadding=0, id='cover_frame')
            cover_template = PageTemplate(id='Cover', frames=[cover_frame])
            
            # Normal template (with margins)
            normal_frame = Frame(15*mm, 20*mm, A5[0]-30*mm, A5[1]-40*mm,
                               leftPadding=0, bottomPadding=0,
                               rightPadding=0, topPadding=0, id='normal_frame')
            normal_template = PageTemplate(id='Normal', frames=[normal_frame],
                                         onPage=self._page_template)
            
            doc.addPageTemplates([cover_template, normal_template])
            
            # Build content
            story = []
            
            # Cover page
            if cover_image and cover_image.exists():
                from reportlab.platypus import NextPageTemplate
                story.append(NextPageTemplate('Cover'))
                img = RLImage(str(cover_image))
                img.drawWidth = A5[0]
                img.drawHeight = A5[1]
                story.append(img)
                story.append(PageBreak())
                # Switch to normal template for rest of document
                story.append(NextPageTemplate('Normal'))
            
            # Kuchie pages
            for img_path, is_horizontal in kuchie_images:
                full_path = base_path / img_path
                if full_path.exists():
                    available_width = A5[0] - 30*mm
                    available_height = A5[1] - 60*mm
                    
                    img = RLImage(str(full_path))
                    aspect = img.imageWidth / img.imageHeight
                    
                    if is_horizontal:
                        img.drawWidth = available_width
                        img.drawHeight = available_width / aspect
                        if img.drawHeight > available_height:
                            img.drawHeight = available_height
                            img.drawWidth = available_height * aspect
                    else:
                        img.drawHeight = available_height
                        img.drawWidth = available_height * aspect
                        if img.drawWidth > available_width:
                            img.drawWidth = available_width
                            img.drawHeight = available_width / aspect
                    
                    story.append(Spacer(1, 20*mm))
                    story.append(img)
                    story.append(PageBreak())
            
            # Table of contents
            story.append(self._create_toc(chapters))
            story.append(PageBreak())
            
            # Chapters
            for i, chapter in enumerate(chapters):
                story.extend(self._create_chapter(chapter, is_first=(i==0)))
                if i < len(chapters) - 1:
                    story.append(PageBreak())
            
            # Build PDF
            doc.build(story)
            
            return True
            
        except Exception as e:
            print(f"[ERROR] PDF generation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _page_template(self, canvas_obj, doc):
        """Page template for headers/footers."""
        canvas_obj.saveState()
        
        # Set background color for dark mode
        if self.theme == 'dark':
            canvas_obj.setFillColor(self.bg_color)
            canvas_obj.rect(0, 0, A5[0], A5[1], fill=1, stroke=0)
        
        # Page number (except first page)
        if doc.page > 1:
            canvas_obj.setFont('Times-Roman', 9)
            canvas_obj.setFillColor(self.text_color)
            page_num = canvas_obj.getPageNumber()
            text = str(page_num)
            canvas_obj.drawCentredString(A5[0]/2, 10*mm, text)
        
        canvas_obj.restoreState()
    
    def _create_cover_page(self, image_path: Path):
        """Create cover page with full-page image."""
        # Cover page should fill the entire page (no margins)
        img = RLImage(str(image_path))
        img.drawHeight = A5[1]
        img.drawWidth = A5[0]
        return img
    
    def _create_image_page(self, image_path: Path, is_horizontal: bool):
        """Create kuchi-e image page."""
        # Calculate available space (page size minus margins)
        available_width = A5[0] - 30*mm
        available_height = A5[1] - 60*mm
        
        # Create image and scale to fit
        img = RLImage(str(image_path))
        
        # Calculate aspect ratio
        aspect = img.imageWidth / img.imageHeight
        
        # Scale to fit available space
        if is_horizontal:
            # Landscape - fit to width
            img.drawWidth = available_width
            img.drawHeight = available_width / aspect
            if img.drawHeight > available_height:
                img.drawHeight = available_height
                img.drawWidth = available_height * aspect
        else:
            # Portrait - fit to height
            img.drawHeight = available_height
            img.drawWidth = available_height * aspect
            if img.drawWidth > available_width:
                img.drawWidth = available_width
                img.drawHeight = available_width / aspect
        
        return KeepTogether([Spacer(1, 20*mm), img])
    
    def _create_toc(self, chapters: List[dict]):
        """Create table of contents."""
        elements = []
        
        # Title
        elements.append(Spacer(1, 40*mm))
        elements.append(Paragraph("Table of Contents", self.style_toc_title))
        elements.append(Spacer(1, 10*mm))
        
        # Chapters
        for ch in chapters:
            title = ch['title']
            elements.append(Paragraph(title, self.style_toc_item))
            elements.append(Spacer(1, 4*mm))
        
        return KeepTogether(elements)
    
    def _create_chapter(self, chapter: dict, is_first: bool = False):
        """Create chapter content."""
        elements = []
        
        # Chapter title
        elements.append(Spacer(1, 40*mm))
        elements.append(Paragraph(chapter['title'], self.style_chapter))
        
        # Chapter content (list of paragraphs)
        paragraphs = chapter.get('paragraphs', [])
        
        for i, para_text in enumerate(paragraphs):
            # Check if this is an image marker
            if para_text.startswith('[IMAGE:'):
                # Extract image path
                img_path = para_text.replace('[IMAGE:', '').replace(']', '')

                # Normalize path (convert from EPUB format to actual file path)
                if img_path.startswith('../Images/'):
                    img_path = img_path.replace('../Images/', 'assets/illustrations/')
                elif img_path.startswith('../image/'):
                    img_path = img_path.replace('../image/', 'assets/illustrations/')

                # Try to add the image on its own page
                try:
                    from pathlib import Path
                    # Get base path from chapter dict if available
                    base_path = chapter.get('base_path', Path('.'))
                    full_img_path = base_path / img_path

                    if full_img_path.exists():
                        # Page break before illustration
                        elements.append(PageBreak())

                        # Calculate size to fit full page (with margins)
                        available_width = A5[0] - 30*mm
                        available_height = A5[1] - 50*mm  # Full page height minus margins

                        img = RLImage(str(full_img_path))
                        aspect = img.imageWidth / img.imageHeight

                        # Scale to fit available space while maintaining aspect ratio
                        if aspect > (available_width / available_height):
                            # Image is wider - fit to width
                            img.drawWidth = available_width
                            img.drawHeight = available_width / aspect
                        else:
                            # Image is taller - fit to height
                            img.drawHeight = available_height
                            img.drawWidth = available_height * aspect

                        # Center vertically on the page
                        vertical_space = (available_height - img.drawHeight) / 2
                        elements.append(Spacer(1, vertical_space))
                        elements.append(img)

                        # Page break after illustration to continue text on next page
                        elements.append(PageBreak())
                except Exception as e:
                    print(f"[WARNING] Failed to add illustration {img_path}: {e}")
                continue
            
            # Regular paragraph
            # First paragraph has no indent
            style = self.style_first if i == 0 else self.style_body
            
            # Create paragraph with HTML support for bold/italic
            try:
                para = Paragraph(para_text, style)
                elements.append(para)
            except Exception as e:
                # Fallback to plain text if HTML parsing fails
                print(f"[WARNING] Failed to parse paragraph: {e}")
                elements.append(Paragraph(para_text.replace('<', '&lt;').replace('>', '&gt;'), style))
        
        return elements
    
    def get_file_size(self, pdf_path: Path) -> str:
        """Get human-readable file size."""
        size_bytes = pdf_path.stat().st_size
        
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
