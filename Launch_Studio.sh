#!/bin/bash

echo "============================================================"
echo " MTL PUBLISHING STUDIO - Portable Edition"
echo "============================================================"
echo

# Set environment variables
export MTL_ROOT="$(cd "$(dirname "$0")" && pwd)"
export PYTHON_HOME="$MTL_ROOT/python_env"
export PATH="$PYTHON_HOME/bin:$PATH"

# Check if VSCodium exists
if [ ! -d "$MTL_ROOT/bin/VSCodium.app" ]; then
    echo "[ERROR] VSCodium.app not found in bin/"
    echo "Please download VSCodium portable and place in bin/"
    exit 1
fi

# Launch VSCodium with workspace
echo "Launching MTL Studio..."
echo

open -a "$MTL_ROOT/bin/VSCodium.app" "$MTL_ROOT/workspace/MTL_Studio.code-workspace"

echo
echo "MTL Studio is running."
echo "You can use this terminal for CLI commands:"
echo "  - cd pipeline_source"
echo "  - python mtl.py list"
echo "  - python mtl.py status [volume_id]"
echo
