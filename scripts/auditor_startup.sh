#!/bin/zsh

# Auditor Agent - Startup Script
# Configures environment and launches Gemini CLI

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MTL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Set up environment
export MTL_ROOT
export PYTHON_HOME="$MTL_ROOT/python_env"
export PATH="$PYTHON_HOME/bin:$PATH"
export PYTHONPATH="$MTL_ROOT/pipeline:$PYTHONPATH"

# Navigate to pipeline directory
cd "$MTL_ROOT/pipeline"

echo "============================================================"
echo " AUDITOR AGENT - GEMINI CLI"
echo "============================================================"
echo " Mode: Interactive Agent"
echo " Context: pipeline/"
echo "============================================================"
echo ""

# Launch Gemini›
gemini
