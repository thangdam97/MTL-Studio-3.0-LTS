"""
PDF Styles - CSS for light and dark modes.
"""

from .config import *

def get_base_css() -> str:
    """Get base CSS that applies to both themes."""
    return f'''
/* Page Setup */
@page {{
    size: {PAGE_SIZE};
    margin: {MARGIN_TOP} {MARGIN_RIGHT} {MARGIN_BOTTOM} {MARGIN_LEFT};
}}

@page :first {{
    margin: 0;  /* Cover page - full bleed */
}}

@page chapter {{
    @top-center {{
        content: string(chapter-title);
        font-size: 9pt;
        font-style: italic;
    }}
    @bottom-center {{
        content: counter(page);
        font-size: 9pt;
    }}
}}

/* Reset */
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

/* Typography */
body {{
    font-family: {FONT_FAMILY};
    font-size: {FONT_SIZE};
    line-height: {LINE_HEIGHT};
    text-align: {TEXT_ALIGN};
    hyphens: auto;
}}

/* Headings */
h1 {{
    font-size: 18pt;
    font-weight: bold;
    text-align: center;
    page-break-before: always;
    margin-top: 40mm;
    margin-bottom: 10mm;
    string-set: chapter-title content();
}}

h2 {{
    font-size: 14pt;
    font-weight: bold;
    margin-top: 8mm;
    margin-bottom: 4mm;
}}

/* Paragraphs */
p {{
    text-indent: 1em;
    margin-bottom: 0;
    orphans: 2;
    widows: 2;
}}

p:first-of-type {{
    text-indent: 0;  /* No indent for first paragraph */
}}

/* Strong/Emphasis */
strong {{
    font-weight: bold;
}}

em {{
    font-style: italic;
}}

/* Page Breaks */
.page-break {{
    page-break-after: always;
}}

.page-break-before {{
    page-break-before: always;
}}

.no-break {{
    page-break-inside: avoid;
}}

/* Cover Page */
.cover-page {{
    page: cover;
    text-align: center;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100vh;
}}

.cover-page img {{
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
}}

/* Kuchi-e Pages */
.kuchie-page {{
    page-break-before: always;
    page-break-after: always;
    text-align: center;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100vh;
}}

.kuchie-page img {{
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
}}

.kuchie-page.horizontal {{
    /* Landscape kuchi-e - rotate for proper viewing */
    transform: rotate(90deg);
    transform-origin: center;
}}

/* Table of Contents */
.toc-page {{
    page-break-before: always;
    page-break-after: always;
}}

.toc-title {{
    font-size: 18pt;
    font-weight: bold;
    text-align: center;
    margin-top: 40mm;
    margin-bottom: 10mm;
}}

.toc-list {{
    list-style: none;
    padding: 0;
}}

.toc-item {{
    margin-bottom: 4mm;
    text-indent: 0;
}}

.toc-item a {{
    text-decoration: none;
}}

/* Chapters */
.chapter {{
    page: chapter;
    page-break-before: always;
}}

/* Illustrations */
.illustration {{
    text-align: center;
    page-break-inside: avoid;
    margin: 8mm 0;
    text-indent: 0;
}}

.illustration img {{
    max-width: 100%;
    max-height: 60mm;
    object-fit: contain;
}}
'''

def get_light_mode_css() -> str:
    """Get light mode specific CSS."""
    return '''
/* Light Mode Theme */
body {
    background-color: #ffffff;
    color: #000000;
}

h1, h2, h3 {
    color: #000000;
}

.toc-item a {
    color: #000000;
}

.cover-page,
.kuchie-page {
    background-color: #ffffff;
}
'''

def get_dark_mode_css() -> str:
    """Get dark mode specific CSS."""
    return '''
/* Dark Mode Theme */
body {
    background-color: #1a1a1a;
    color: #e0e0e0;
}

h1, h2, h3 {
    color: #ffffff;
}

.toc-item a {
    color: #e0e0e0;
}

.cover-page,
.kuchie-page {
    background-color: #000000;  /* Pure black for images */
}

/* Adjust image brightness slightly for dark mode */
.chapter img {
    filter: brightness(0.95);
}
'''

def get_css(theme: str = 'light') -> str:
    """
    Get complete CSS for specified theme.
    
    Args:
        theme: 'light' or 'dark'
        
    Returns:
        Complete CSS string
    """
    base = get_base_css()
    
    if theme == 'dark':
        return base + get_dark_mode_css()
    else:
        return base + get_light_mode_css()
