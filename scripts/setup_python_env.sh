#!/bin/bash

# MTL Studio - Python Environment Setup Script
# This script sets up the embedded Python environment with all dependencies

set -e  # Exit on error

echo "============================================================"
echo " MTL STUDIO - Python Environment Setup"
echo "============================================================"
echo

# Get script directory
MTL_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$MTL_ROOT"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    echo "Please install Python 3.11 or higher"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✓ Found Python $PYTHON_VERSION"
echo

# Check if requirements.txt exists
if [ ! -f "pipeline_source/requirements.txt" ]; then
    echo "[ERROR] requirements.txt not found in pipeline_source/"
    exit 1
fi

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv python_env

if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to create virtual environment"
    exit 1
fi

echo "✓ Virtual environment created"
echo

# Activate virtual environment
echo "Activating virtual environment..."
source python_env/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

echo "✓ pip upgraded"
echo

# Install requirements
echo "Installing dependencies from requirements.txt..."
echo "This may take a few minutes..."
echo

pip install -r pipeline_source/requirements.txt

if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies"
    exit 1
fi

echo
echo "✓ All dependencies installed"
echo

# Verify key packages
echo "Verifying key packages..."

PACKAGES=("google.genai" "bs4" "lxml" "ebooklib" "reportlab" "PIL")
ALL_OK=true

for pkg in "${PACKAGES[@]}"; do
    if python -c "import $pkg" 2>/dev/null; then
        echo "  ✓ $pkg"
    else
        echo "  ✗ $pkg (missing)"
        ALL_OK=false
    fi
done

echo

if [ "$ALL_OK" = true ]; then
    echo "============================================================"
    echo " Python Environment Setup Complete!"
    echo "============================================================"
    echo
    echo "Next steps:"
    echo "  1. Configure API keys in pipeline_source/.env"
    echo "  2. Launch MTL Studio: ./Launch_Studio.sh"
    echo
    echo "To activate this environment manually:"
    echo "  source python_env/bin/activate"
    echo
else
    echo "[WARNING] Some packages failed to install"
    echo "Please check the errors above"
    exit 1
fi
