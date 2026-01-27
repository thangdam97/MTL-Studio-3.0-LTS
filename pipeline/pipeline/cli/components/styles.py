"""
Custom styles for questionary prompts.
"""

from questionary import Style

# Color scheme
COLORS = {
    'primary': '#00aaff',      # Cyan-blue
    'secondary': '#888888',    # Gray
    'success': '#00ff00',      # Green
    'warning': '#ffaa00',      # Orange
    'error': '#ff0000',        # Red
    'highlight': '#ffffff',    # White
    'muted': '#666666',        # Dark gray
}

# Custom style for questionary prompts
custom_style = Style([
    # Question styling
    ('qmark', 'fg:#00aaff bold'),           # Question mark
    ('question', 'fg:#ffffff bold'),         # Question text
    ('answer', 'fg:#00ff00 bold'),           # Selected answer
    ('pointer', 'fg:#00aaff bold'),          # Selection pointer (>)
    ('highlighted', 'fg:#00aaff bold'),      # Highlighted option
    ('selected', 'fg:#00ff00'),              # Selected checkbox
    ('separator', 'fg:#888888'),             # Separator line
    ('instruction', 'fg:#888888'),           # Instructions
    ('text', 'fg:#ffffff'),                  # Normal text
    ('disabled', 'fg:#666666 italic'),       # Disabled option
])

# Style for minimal/quick mode (less colorful)
minimal_style = Style([
    ('qmark', 'fg:#888888'),
    ('question', 'fg:#ffffff'),
    ('answer', 'fg:#00aaff'),
    ('pointer', 'fg:#00aaff'),
    ('highlighted', 'fg:#ffffff bold'),
    ('selected', 'fg:#00aaff'),
    ('separator', 'fg:#444444'),
    ('instruction', 'fg:#666666'),
    ('text', 'fg:#cccccc'),
    ('disabled', 'fg:#444444 italic'),
])
