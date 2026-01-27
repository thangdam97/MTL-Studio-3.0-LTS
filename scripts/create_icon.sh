#!/bin/bash

# Create a simple icon for MTL Studio
# This creates a basic icon using sips (built-in macOS tool)

MTL_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ICON_DIR="$MTL_ROOT/MTL Studio.app/Contents/Resources"

# Create a simple colored square as placeholder icon
# You can replace this with a custom icon later

# Create iconset directory
mkdir -p "$ICON_DIR/AppIcon.iconset"

# Generate different sizes using sips
# For now, we'll create a simple colored image

# Create base 1024x1024 image (blue gradient)
cat > "$ICON_DIR/temp_icon.svg" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<svg width="1024" height="1024" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#4A90E2;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#357ABD;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="1024" height="1024" rx="180" fill="url(#grad)"/>
  <text x="512" y="600" font-family="Arial, sans-serif" font-size="400" font-weight="bold" fill="white" text-anchor="middle">MTL</text>
  <text x="512" y="750" font-family="Arial, sans-serif" font-size="120" fill="white" text-anchor="middle" opacity="0.9">STUDIO</text>
</svg>
EOF

# Convert SVG to PNG if possible (requires rsvg-convert or similar)
# If not available, we'll skip icon creation
if command -v rsvg-convert &> /dev/null; then
    rsvg-convert -w 1024 -h 1024 "$ICON_DIR/temp_icon.svg" > "$ICON_DIR/icon_1024.png"
    
    # Generate all required sizes
    sips -z 16 16     "$ICON_DIR/icon_1024.png" --out "$ICON_DIR/AppIcon.iconset/icon_16x16.png" > /dev/null 2>&1
    sips -z 32 32     "$ICON_DIR/icon_1024.png" --out "$ICON_DIR/AppIcon.iconset/icon_16x16@2x.png" > /dev/null 2>&1
    sips -z 32 32     "$ICON_DIR/icon_1024.png" --out "$ICON_DIR/AppIcon.iconset/icon_32x32.png" > /dev/null 2>&1
    sips -z 64 64     "$ICON_DIR/icon_1024.png" --out "$ICON_DIR/AppIcon.iconset/icon_32x32@2x.png" > /dev/null 2>&1
    sips -z 128 128   "$ICON_DIR/icon_1024.png" --out "$ICON_DIR/AppIcon.iconset/icon_128x128.png" > /dev/null 2>&1
    sips -z 256 256   "$ICON_DIR/icon_1024.png" --out "$ICON_DIR/AppIcon.iconset/icon_128x128@2x.png" > /dev/null 2>&1
    sips -z 256 256   "$ICON_DIR/icon_1024.png" --out "$ICON_DIR/AppIcon.iconset/icon_256x256.png" > /dev/null 2>&1
    sips -z 512 512   "$ICON_DIR/icon_1024.png" --out "$ICON_DIR/AppIcon.iconset/icon_256x256@2x.png" > /dev/null 2>&1
    sips -z 512 512   "$ICON_DIR/icon_1024.png" --out "$ICON_DIR/AppIcon.iconset/icon_512x512.png" > /dev/null 2>&1
    sips -z 1024 1024 "$ICON_DIR/icon_1024.png" --out "$ICON_DIR/AppIcon.iconset/icon_512x512@2x.png" > /dev/null 2>&1
    
    # Convert iconset to icns
    iconutil -c icns "$ICON_DIR/AppIcon.iconset" -o "$ICON_DIR/AppIcon.icns"
    
    # Cleanup
    rm -rf "$ICON_DIR/AppIcon.iconset"
    rm "$ICON_DIR/temp_icon.svg"
    rm "$ICON_DIR/icon_1024.png"
    
    echo "✓ Icon created successfully"
else
    echo "⚠ rsvg-convert not found. Skipping icon creation."
    echo "  The app will use the default icon."
    echo "  Install librsvg to generate custom icons: brew install librsvg"
    
    # Cleanup
    rm "$ICON_DIR/temp_icon.svg"
fi
