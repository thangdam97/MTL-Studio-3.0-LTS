"""
CSS Processor - Language-Agnostic CSS Processing.

Modifies CSS files to replace source language fonts with target fonts
and adds professional styling for translated EPUBs.
"""

import re
from pathlib import Path
from typing import Dict

from .config import FONT_FAMILY_REPLACEMENTS


class CSSProcessor:
    """Processes CSS files for translated EPUBs."""

    @staticmethod
    def process_css_files(working_dir: Path, css_files: list = None) -> None:
        """
        Process CSS files in the working directory.

        Args:
            working_dir: Working directory for EPUB contents
            css_files: List of relative CSS file paths to process
        """
        if css_files is None:
            css_files = ["style/book-style.css", "style/style-standard.css"]

        print("[INFO] Processing CSS files...")

        for css_rel_path in css_files:
            css_file = working_dir / css_rel_path

            if not css_file.exists():
                print(f"  [WARN] CSS file not found: {css_file}")
                continue

            CSSProcessor._modify_css_file(css_file)

        # Add fonts import and styling to main stylesheet
        book_style_file = working_dir / "style" / "book-style.css"
        if book_style_file.exists():
            CSSProcessor._add_fonts_import(book_style_file)
            CSSProcessor._add_professional_styling(book_style_file)

    @staticmethod
    def _modify_css_file(css_path: Path) -> None:
        """Modify a single CSS file with font replacements."""
        with open(css_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        for old_font, new_font in FONT_FAMILY_REPLACEMENTS.items():
            content = CSSProcessor._replace_font_family(content, old_font, new_font)

        if content != original_content:
            with open(css_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  [OK] Modified {css_path.name}")
        else:
            print(f"  - No changes needed for {css_path.name}")

    @staticmethod
    def _replace_font_family(content: str, old_font: str, new_font: str) -> str:
        """Replace font family in CSS content."""
        pattern = rf'font-family:\s*([^;]*?){re.escape(old_font)}([^;]*?);'

        def replace_func(match):
            before = match.group(1)
            after = match.group(2)
            return f'font-family: {before}{new_font}{after};'

        return re.sub(pattern, replace_func, content)

    @staticmethod
    def _add_fonts_import(book_style_path: Path) -> None:
        """Add @import 'fonts.css' to book-style.css."""
        with open(book_style_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        fonts_import = '@import "fonts.css";\n'

        for line in lines:
            if 'fonts.css' in line:
                print(f"  - fonts.css import already exists in {book_style_path.name}")
                return

        # Find position after @charset and other @imports
        insert_position = 0
        for idx, line in enumerate(lines):
            if line.strip().startswith('@import') or line.strip().startswith('@charset'):
                insert_position = idx + 1

        lines.insert(insert_position, fonts_import)

        with open(book_style_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        print(f"  [OK] Added fonts.css import to {book_style_path.name}")

    @staticmethod
    def _add_professional_styling(book_style_path: Path) -> None:
        """Add professional J-Novel Club styling to book-style.css."""
        professional_css = '''

/* ============================================
   PROFESSIONAL EPUB STYLING
   Language-Agnostic Typography Enhancements
   ============================================ */

/* CSS Variables */
:root {
  --primary-font: "Google Sans", sans-serif;
  --body-line-height: 1.55;
  --heading-line-height: 1.3;
  --paragraph-indent: 20pt;
  --text-color-light: #2c2c2c;
  --bg-color-light: #ffffff;
  --text-color-dark: #e8e8e8;
  --bg-color-dark: #1a1a1a;
}

/* Global Typography */
html {
  font-feature-settings: "liga" 1, "kern" 1;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}

/* Paragraph Styling */
p {
  display: block;
  margin-top: 0em;
  margin-bottom: 0em;
  text-indent: var(--paragraph-indent);
  line-height: var(--body-line-height);
  hyphens: auto;
  widows: 3;
  orphans: 3;
}

p.noindent {
  text-indent: 0em;
  margin-top: 0.5em;
}

p.centerp {
  text-align: center;
  text-indent: 0;
}

/* Headings */
h1, h2.chapter-title {
  font-size: 1.15em;
  margin-top: 1.5em;
  margin-bottom: 1.5em;
  line-height: var(--heading-line-height);
  text-align: center;
  text-indent: 0;
  font-weight: bold;
}

h2 {
  font-size: 1.2em;
  margin-top: 1em;
  margin-bottom: 0.5em;
  text-indent: 0;
  font-weight: bold;
}

/* Images */
img.insert {
  max-width: 100%;
  max-height: 100vh;
  height: auto;
  width: auto;
  display: block;
  margin: 0 auto;
  page-break-inside: avoid;
  object-fit: contain;
}

img.fit {
  max-width: 100%;
  height: auto;
  page-break-inside: avoid;
}

/* Section breaks */
p.section-break {
  text-align: center;
  margin-top: 1em;
  margin-bottom: 1em;
  text-indent: 0;
  page-break-before: avoid;
  page-break-after: avoid;
  page-break-inside: avoid;
}

/* Insert page styling */
body.nomargin {
  margin: 0;
  padding: 0;
}

body.center {
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
}

.insert-page, .kuchie-image {
  text-align: center;
  margin: 0;
  padding: 0;
}

/* TOC Styling */
section[epub|type~="toc"] h1 {
  font-size: 1.5em;
  text-align: center;
  margin: 2em 0;
}

section[epub|type~="toc"] ol {
  list-style-type: none;
  margin: 0;
  padding: 0;
}

section[epub|type~="toc"] li {
  margin: 1em 0;
  text-indent: 0;
  line-height: 1.8em;
}

section[epub|type~="toc"] a {
  color: inherit;
  text-decoration: none;
}

/* Dark Mode Support */
@media (prefers-color-scheme: dark) {
  body {
    color: var(--text-color-dark);
    background-color: var(--bg-color-dark);
  }
  a { color: #64b5f6; }
  a:visited { color: #ce93d8; }
}

/* Responsive Design */
@media screen and (max-width: 600px) {
  p {
    text-indent: 0;
    margin-bottom: 0.5em;
  }
  h1 { font-size: 1.3em; }
  h2 { font-size: 1.1em; }
}
'''

        with open(book_style_path, 'a', encoding='utf-8') as f:
            f.write(professional_css)

        print(f"  [OK] Added professional styling to {book_style_path.name}")

    @staticmethod
    def validate_css_syntax(css_path: Path) -> bool:
        """Basic CSS syntax validation."""
        with open(css_path, 'r', encoding='utf-8') as f:
            content = f.read()

        opening_braces = content.count('{')
        closing_braces = content.count('}')

        if opening_braces != closing_braces:
            raise SyntaxError(
                f"CSS brace mismatch in {css_path.name}: "
                f"{opening_braces} opening, {closing_braces} closing"
            )

        return True


def process_all_css_files(working_dir: Path) -> None:
    """Main function to process all CSS files."""
    CSSProcessor.process_css_files(working_dir)
