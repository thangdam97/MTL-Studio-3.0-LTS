#!/usr/bin/env python3
"""
MTL Studio - Structure Verification & Setup Script
Verifies all required modules and reorganizes the directory structure.
"""

import os
import sys
from pathlib import Path
import shutil

class Colors:
    """Terminal colors for output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print section header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def print_success(text):
    """Print success message."""
    print(f"{Colors.GREEN}✓{Colors.RESET} {text}")

def print_error(text):
    """Print error message."""
    print(f"{Colors.RED}✗{Colors.RESET} {text}")

def print_warning(text):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {text}")

def print_info(text):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ{Colors.RESET} {text}")

def check_directory_structure():
    """Verify the MTL Studio directory structure."""
    print_header("Checking Directory Structure")
    
    required_dirs = [
        "bin",
        "data",
        "data/extensions",
        "data/user-data",
        "data/user-data/User",
        "python_env",
        "pipeline_source",
        "workspace",
        "docs",
        "scripts"
    ]
    
    all_present = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print_success(f"{dir_path}/")
        else:
            print_error(f"{dir_path}/ (missing)")
            all_present = False
    
    return all_present

def check_vscodium():
    """Check if VSCodium is present."""
    print_header("Checking VSCodium")
    
    vscodium_paths = [
        Path("bin/VSCodium.app"),  # macOS
        Path("bin/VSCodium.exe"),  # Windows
        Path("bin/vscodium")       # Linux
    ]
    
    for path in vscodium_paths:
        if path.exists():
            print_success(f"Found: {path}")
            return True
    
    print_error("VSCodium not found in bin/")
    print_info("Please download VSCodium portable and place in bin/")
    return False

def check_pipeline_modules():
    """Check if all pipeline modules are present."""
    print_header("Checking Pipeline Modules")
    
    pipeline_dir = Path("pipeline_source/pipeline")
    
    required_modules = [
        "librarian",
        "metadata_processor",
        "translator",
        "builder",
        "pdf_builder",
        "common"
    ]
    
    all_present = True
    for module in required_modules:
        module_path = pipeline_dir / module
        if module_path.exists():
            print_success(f"pipeline/{module}/")
        else:
            print_error(f"pipeline/{module}/ (missing)")
            all_present = False
    
    return all_present

def check_rag_modules():
    """Check if all RAG knowledge modules are present."""
    print_header("Checking RAG Knowledge Modules")
    
    modules_dir = Path("pipeline_source/modules")
    
    required_modules = [
        "MEGA_CORE_TRANSLATION_ENGINE.md",
        "MEGA_CHARACTER_VOICE_SYSTEM.md",
        "MEGA_ELLIPSES_ONOMATOPOEIA_MODULE.md",
        "Library_LOCALIZATION_PRIMER_EN.md",
        "Library_REFERENCE_ICL_SAMPLES.md",
        "FANTASY_TRANSLATION_MODULE_EN.md"
    ]
    
    all_present = True
    for module in required_modules:
        module_path = modules_dir / module
        if module_path.exists():
            size_kb = module_path.stat().st_size / 1024
            print_success(f"{module} ({size_kb:.1f} KB)")
        else:
            print_error(f"{module} (missing)")
            all_present = False
    
    return all_present

def check_core_files():
    """Check if core pipeline files are present."""
    print_header("Checking Core Files")
    
    core_files = [
        "pipeline_source/mtl.py",
        "pipeline_source/config.yaml",
        "pipeline_source/format_scene_breaks.py"
    ]
    
    all_present = True
    for file_path in core_files:
        path = Path(file_path)
        if path.exists():
            print_success(path.name)
        else:
            print_error(f"{path.name} (missing)")
            all_present = False
    
    return all_present

def check_prompts():
    """Check if master prompts are present."""
    print_header("Checking Master Prompts")
    
    prompts_dir = Path("pipeline_source/prompts")
    
    if not prompts_dir.exists():
        print_error("prompts/ directory missing")
        return False
    
    prompt_files = list(prompts_dir.glob("*.xml"))
    
    if not prompt_files:
        print_error("No master prompt files found")
        return False
    
    for prompt_file in prompt_files:
        print_success(prompt_file.name)
    
    return True

def check_documentation():
    """Check if documentation is present."""
    print_header("Checking Documentation")
    
    docs_dir = Path("pipeline_source/documents")
    
    if not docs_dir.exists():
        print_warning("documents/ directory missing")
        return False
    
    doc_files = list(docs_dir.glob("*.md"))
    
    print_info(f"Found {len(doc_files)} documentation files")
    
    important_docs = [
        "SCENE_BREAK_FORMATTER.md",
        "ELLIPSES_MODULE_SUMMARY.md",
        "SAFETY_CONFLICT_RESOLUTION.md",
        "CONTINUITY_PACK_SYSTEM.md",
        "MTL_STUDIO_IMPLEMENTATION_PLAN.md"
    ]
    
    for doc in important_docs:
        doc_path = docs_dir / doc
        if doc_path.exists():
            print_success(doc)
        else:
            print_warning(f"{doc} (missing)")
    
    return True

def create_workspace_config():
    """Create VSCodium workspace configuration."""
    print_header("Creating Workspace Configuration")
    
    workspace_dir = Path("workspace")
    workspace_dir.mkdir(exist_ok=True)
    
    workspace_config = {
        "folders": [
            {
                "name": "📚 Pipeline",
                "path": "../pipeline_source"
            },
            {
                "name": "📖 Documentation",
                "path": "../docs"
            },
            {
                "name": "🔧 Scripts",
                "path": "../scripts"
            }
        ],
        "settings": {
            "files.watcherExclude": {
                "**/WORK/**": True,
                "**/OUTPUT/**": True,
                "**/__pycache__/**": True
            }
        },
        "extensions": {
            "recommendations": [
                "anthropic.claude-code",
                "ms-python.python",
                "yzhang.markdown-all-in-one"
            ]
        }
    }
    
    import json
    workspace_file = workspace_dir / "MTL_Studio.code-workspace"
    with open(workspace_file, 'w') as f:
        json.dump(workspace_config, f, indent=2)
    
    print_success(f"Created {workspace_file}")
    return True

def create_launcher_script():
    """Create launcher script for macOS."""
    print_header("Creating Launcher Script")
    
    launcher_content = '''#!/bin/bash

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
'''
    
    launcher_file = Path("Launch_Studio.sh")
    with open(launcher_file, 'w') as f:
        f.write(launcher_content)
    
    # Make executable
    os.chmod(launcher_file, 0o755)
    
    print_success(f"Created {launcher_file}")
    return True

def create_readme():
    """Create README file."""
    print_header("Creating README")
    
    readme_content = '''# MTL Publishing Studio - Portable Edition

## 🚀 Quick Start

### macOS/Linux
```bash
./Launch_Studio.sh
```

### Windows
```batch
Launch_Studio.bat
```

## 📁 Directory Structure

```
MTL_Studio/
├── bin/                    # VSCodium executable
├── data/                   # VSCodium portable data
├── python_env/             # Python environment (to be set up)
├── pipeline_source/        # MT Publishing Pipeline
├── workspace/              # VSCodium workspace
├── docs/                   # Documentation
└── scripts/                # Automation scripts
```

## 🔧 Setup

### 1. Python Environment

You need to set up the Python environment:

```bash
# macOS/Linux
python3 -m venv python_env
source python_env/bin/activate
pip install -r pipeline_source/requirements.txt
```

### 2. API Keys

Create `.env` file in `pipeline_source/`:

```bash
GEMINI_API_KEY=your-gemini-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here  # Optional
```

### 3. Launch

Run the launcher script to start MTL Studio.

## 📚 Documentation

See `pipeline_source/documents/` for detailed documentation:
- QUICKSTART.md
- MTL_STUDIO_IMPLEMENTATION_PLAN.md
- User guides and references

## 🆘 Support

For issues and questions, see `pipeline_source/documents/TROUBLESHOOTING.md`

## 📄 License

See LICENSE.txt
'''
    
    readme_file = Path("README.md")
    with open(readme_file, 'w') as f:
        f.write(readme_content)
    
    print_success(f"Created {readme_file}")
    return True

def generate_summary():
    """Generate verification summary."""
    print_header("Verification Summary")
    
    checks = [
        ("Directory Structure", check_directory_structure()),
        ("VSCodium", check_vscodium()),
        ("Pipeline Modules", check_pipeline_modules()),
        ("RAG Modules", check_rag_modules()),
        ("Core Files", check_core_files()),
        ("Master Prompts", check_prompts()),
        ("Documentation", check_documentation())
    ]
    
    print("\nResults:")
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    
    for name, result in checks:
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if result else f"{Colors.RED}FAIL{Colors.RESET}"
        print(f"  {name}: {status}")
    
    print(f"\n{Colors.BOLD}Score: {passed}/{total}{Colors.RESET}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ All checks passed! MTL Studio is ready.{Colors.RESET}")
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ Some checks failed. Please review above.{Colors.RESET}")
    
    return passed == total

def main():
    """Main verification and setup routine."""
    print(f"\n{Colors.BOLD}MTL STUDIO - Structure Verification & Setup{Colors.RESET}")
    
    # Run all checks
    all_passed = generate_summary()
    
    # Create workspace and launcher
    create_workspace_config()
    create_launcher_script()
    create_readme()
    
    print_header("Next Steps")
    
    if all_passed:
        print_info("1. Set up Python environment:")
        print("   python3 -m venv python_env")
        print("   source python_env/bin/activate")
        print("   pip install -r pipeline_source/requirements.txt")
        print()
        print_info("2. Configure API keys in pipeline_source/.env")
        print()
        print_info("3. Launch MTL Studio:")
        print("   ./Launch_Studio.sh")
    else:
        print_warning("Please resolve the failed checks above before proceeding.")
    
    print()

if __name__ == "__main__":
    main()
