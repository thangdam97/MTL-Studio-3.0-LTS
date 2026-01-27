#!/bin/zsh
# ============================================
# MTL Studio - Terminal Startup Script
# Single terminal launch with clean menu
# ============================================

# Close any existing terminals (optional - keep if user prefers)
# killall zsh 2>/dev/null || true

# Get the script's directory and navigate to pipeline
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MTL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Set up environment
export MTL_ROOT
export PYTHON_HOME="$MTL_ROOT/python_env"
export PATH="$PYTHON_HOME/bin:$PATH"
export PYTHONPATH="$MTL_ROOT/pipeline:$PYTHONPATH"

# Change to pipeline directory
cd "$MTL_ROOT/pipeline"

# Launch the main menu (single terminal)
exec ./start.sh "$@"

