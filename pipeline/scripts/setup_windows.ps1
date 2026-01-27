#Requires -Version 5.1
<#
.SYNOPSIS
    Windows Setup Script for MT Publishing Pipeline

.DESCRIPTION
    This script sets up the MT Publishing Pipeline on Windows:
    - Checks Python installation
    - Creates virtual environment
    - Installs dependencies
    - Configures environment variables
    - Creates VSCodium/VSCode tasks

.PARAMETER ApiKey
    Your Gemini API key (optional - can be set later)

.PARAMETER SkipVenv
    Skip virtual environment creation (use existing)

.EXAMPLE
    .\setup_windows.ps1
    .\setup_windows.ps1 -ApiKey "your-gemini-api-key"
#>

param(
    [string]$ApiKey = "",
    [switch]$SkipVenv
)

# Colors for output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Success { Write-ColorOutput Green $args }
function Write-Warning { Write-ColorOutput Yellow $args }
function Write-Error { Write-ColorOutput Red $args }
function Write-Info { Write-ColorOutput Cyan $args }

# Header
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MT Publishing Pipeline - Windows Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory and project root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Write-Info "Project root: $ProjectRoot"
Set-Location $ProjectRoot

# ============================================
# 1. Check Python Installation
# ============================================
Write-Host ""
Write-Host "[1/6] Checking Python installation..." -ForegroundColor White

$PythonCmd = $null
$PythonVersion = $null

# Try different Python commands
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $version = & $cmd --version 2>&1
        if ($version -match "Python (\d+)\.(\d+)") {
            $major = [int]$Matches[1]
            $minor = [int]$Matches[2]
            if ($major -ge 3 -and $minor -ge 10) {
                $PythonCmd = $cmd
                $PythonVersion = $version
                break
            }
        }
    } catch {
        continue
    }
}

if (-not $PythonCmd) {
    Write-Error "ERROR: Python 3.10+ is required but not found."
    Write-Host ""
    Write-Host "Please install Python from one of these sources:" -ForegroundColor Yellow
    Write-Host "  - https://www.python.org/downloads/" -ForegroundColor White
    Write-Host "  - winget install Python.Python.3.11" -ForegroundColor White
    Write-Host "  - choco install python" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Success "Found $PythonVersion (using '$PythonCmd')"

# ============================================
# 2. Create Virtual Environment
# ============================================
Write-Host ""
Write-Host "[2/6] Setting up virtual environment..." -ForegroundColor White

$VenvPath = Join-Path $ProjectRoot "venv"
$VenvPython = Join-Path $VenvPath "Scripts\python.exe"
$VenvActivate = Join-Path $VenvPath "Scripts\Activate.ps1"

if ($SkipVenv -and (Test-Path $VenvPython)) {
    Write-Warning "Skipping venv creation (using existing)"
} elseif (Test-Path $VenvPath) {
    Write-Warning "Virtual environment already exists at: $VenvPath"
    $response = Read-Host "Recreate it? (y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
        Write-Info "Removing old virtual environment..."
        Remove-Item -Recurse -Force $VenvPath
        & $PythonCmd -m venv $VenvPath
        Write-Success "Virtual environment created"
    }
} else {
    Write-Info "Creating virtual environment..."
    & $PythonCmd -m venv $VenvPath
    Write-Success "Virtual environment created at: $VenvPath"
}

# Activate virtual environment
if (Test-Path $VenvActivate) {
    Write-Info "Activating virtual environment..."
    & $VenvActivate
}

# ============================================
# 3. Install Dependencies
# ============================================
Write-Host ""
Write-Host "[3/6] Installing dependencies..." -ForegroundColor White

$RequirementsPath = Join-Path $ProjectRoot "requirements.txt"

if (Test-Path $RequirementsPath) {
    Write-Info "Installing from requirements.txt..."
    & $VenvPython -m pip install --upgrade pip -q
    & $VenvPython -m pip install -r $RequirementsPath

    if ($LASTEXITCODE -eq 0) {
        Write-Success "Dependencies installed successfully"
    } else {
        Write-Error "Failed to install some dependencies"
    }
} else {
    Write-Error "requirements.txt not found at: $RequirementsPath"
    exit 1
}

# ============================================
# 4. Configure Environment Variables
# ============================================
Write-Host ""
Write-Host "[4/6] Configuring environment..." -ForegroundColor White

$EnvFile = Join-Path $ProjectRoot ".env"
$EnvExample = @"
# MT Publishing Pipeline Environment Configuration
# ================================================

# Required: Your Gemini API Key
GEMINI_API_KEY=your-api-key-here

# Optional: Override default model (default: gemini-2.5-flash)
# GEMINI_MODEL=gemini-2.5-pro

# Optional: Enable debug mode
# DEBUG=true
"@

# Handle API Key
if ($ApiKey) {
    # API key provided via parameter
    $EnvContent = $EnvExample -replace "your-api-key-here", $ApiKey
    Set-Content -Path $EnvFile -Value $EnvContent
    Write-Success "API key configured in .env file"
} elseif (Test-Path $EnvFile) {
    # Check if existing .env has a real API key
    $existingContent = Get-Content $EnvFile -Raw
    if ($existingContent -match "GEMINI_API_KEY=(.+)" -and $Matches[1] -ne "your-api-key-here") {
        Write-Success "Existing .env file found with API key configured"
    } else {
        Write-Warning ".env file exists but API key not set"
        Write-Host "  Edit .env and add your Gemini API key" -ForegroundColor Yellow
    }
} else {
    # Create new .env file
    Set-Content -Path $EnvFile -Value $EnvExample
    Write-Warning ".env file created - please add your Gemini API key"
    Write-Host "  Edit: $EnvFile" -ForegroundColor Yellow
}

# ============================================
# 5. Create VSCodium/VSCode Configuration
# ============================================
Write-Host ""
Write-Host "[5/6] Creating VSCodium/VSCode configuration..." -ForegroundColor White

$VscodePath = Join-Path $ProjectRoot ".vscode"
if (-not (Test-Path $VscodePath)) {
    New-Item -ItemType Directory -Path $VscodePath -Force | Out-Null
}

# Create tasks.json
$TasksJson = @'
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "MTL: Run Full Pipeline",
            "type": "shell",
            "command": "${workspaceFolder}/venv/Scripts/python.exe",
            "args": [
                "${workspaceFolder}/scripts/mtl.py",
                "run",
                "${input:volumeId}"
            ],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            },
            "problemMatcher": []
        },
        {
            "label": "MTL: Translate Volume",
            "type": "shell",
            "command": "${workspaceFolder}/venv/Scripts/python.exe",
            "args": [
                "-m",
                "pipeline.translator.agent",
                "--volume",
                "${input:volumeId}"
            ],
            "group": "build",
            "presentation": {
                "reveal": "always",
                "panel": "shared"
            },
            "problemMatcher": []
        },
        {
            "label": "MTL: Translate Specific Chapters",
            "type": "shell",
            "command": "${workspaceFolder}/venv/Scripts/python.exe",
            "args": [
                "-m",
                "pipeline.translator.agent",
                "--volume",
                "${input:volumeId}",
                "--chapters",
                "${input:chapterIds}"
            ],
            "group": "build",
            "problemMatcher": []
        },
        {
            "label": "MTL: Build EPUB",
            "type": "shell",
            "command": "${workspaceFolder}/venv/Scripts/python.exe",
            "args": [
                "${workspaceFolder}/scripts/mtl.py",
                "build",
                "${input:volumeId}"
            ],
            "group": "build",
            "problemMatcher": []
        },
        {
            "label": "MTL: Check Models",
            "type": "shell",
            "command": "${workspaceFolder}/venv/Scripts/python.exe",
            "args": [
                "${workspaceFolder}/check_models.py"
            ],
            "group": "test",
            "problemMatcher": []
        },
        {
            "label": "MTL: List Volumes",
            "type": "shell",
            "command": "${workspaceFolder}/venv/Scripts/python.exe",
            "args": [
                "${workspaceFolder}/scripts/mtl.py",
                "list"
            ],
            "group": "none",
            "problemMatcher": []
        }
    ],
    "inputs": [
        {
            "id": "volumeId",
            "type": "promptString",
            "description": "Volume ID (folder name in WORK/)",
            "default": ""
        },
        {
            "id": "chapterIds",
            "type": "promptString",
            "description": "Chapter IDs (space-separated, e.g., 'chapter_01 chapter_02')",
            "default": ""
        }
    ]
}
'@

$TasksPath = Join-Path $VscodePath "tasks.json"
Set-Content -Path $TasksPath -Value $TasksJson
Write-Success "Created tasks.json"

# Create settings.json
$SettingsJson = @'
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/Scripts/python.exe",
    "python.terminal.activateEnvironment": true,
    "files.associations": {
        "*.xml": "xml"
    },
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/venv": false
    },
    "editor.formatOnSave": true,
    "[python]": {
        "editor.defaultFormatter": "ms-python.python",
        "editor.tabSize": 4
    },
    "terminal.integrated.defaultProfile.windows": "PowerShell"
}
'@

$SettingsPath = Join-Path $VscodePath "settings.json"
if (-not (Test-Path $SettingsPath)) {
    Set-Content -Path $SettingsPath -Value $SettingsJson
    Write-Success "Created settings.json"
} else {
    Write-Warning "settings.json already exists (not overwritten)"
}

# Create launch.json for debugging
$LaunchJson = @'
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Translate Volume",
            "type": "debugpy",
            "request": "launch",
            "module": "pipeline.translator.agent",
            "args": ["--volume", "${input:volumeId}"],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "Python: MTL Script",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/scripts/mtl.py",
            "args": ["run", "${input:volumeId}"],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "Python: Current File",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal"
        }
    ],
    "inputs": [
        {
            "id": "volumeId",
            "type": "promptString",
            "description": "Volume ID to process"
        }
    ]
}
'@

$LaunchPath = Join-Path $VscodePath "launch.json"
if (-not (Test-Path $LaunchPath)) {
    Set-Content -Path $LaunchPath -Value $LaunchJson
    Write-Success "Created launch.json"
} else {
    Write-Warning "launch.json already exists (not overwritten)"
}

# ============================================
# 6. Create Convenience Scripts
# ============================================
Write-Host ""
Write-Host "[6/6] Creating convenience scripts..." -ForegroundColor White

# Create run.bat for easy command-line usage
$RunBat = @'
@echo off
REM MT Publishing Pipeline - Quick Run Script
REM Usage: run.bat <command> [volume_id] [options]
REM
REM Commands:
REM   translate <volume_id>  - Translate a volume
REM   build <volume_id>      - Build EPUB
REM   run <volume_id>        - Full pipeline
REM   list                   - List volumes
REM   check                  - Check API/models

setlocal

set SCRIPT_DIR=%~dp0
set VENV_PYTHON=%SCRIPT_DIR%venv\Scripts\python.exe

if not exist "%VENV_PYTHON%" (
    echo ERROR: Virtual environment not found. Run setup_windows.ps1 first.
    exit /b 1
)

if "%1"=="" (
    echo MT Publishing Pipeline
    echo.
    echo Usage: run.bat ^<command^> [volume_id]
    echo.
    echo Commands:
    echo   translate ^<volume_id^>  - Translate a volume
    echo   build ^<volume_id^>      - Build EPUB
    echo   run ^<volume_id^>        - Full pipeline
    echo   list                   - List volumes in WORK/
    echo   check                  - Check API connection and models
    echo.
    exit /b 0
)

if "%1"=="translate" (
    "%VENV_PYTHON%" -m pipeline.translator.agent --volume %2 %3 %4 %5
) else if "%1"=="build" (
    "%VENV_PYTHON%" "%SCRIPT_DIR%scripts\mtl.py" build %2
) else if "%1"=="run" (
    "%VENV_PYTHON%" "%SCRIPT_DIR%scripts\mtl.py" run %2
) else if "%1"=="list" (
    "%VENV_PYTHON%" "%SCRIPT_DIR%scripts\mtl.py" list
) else if "%1"=="check" (
    "%VENV_PYTHON%" "%SCRIPT_DIR%check_models.py"
) else (
    echo Unknown command: %1
    echo Run 'run.bat' without arguments for help.
    exit /b 1
)

endlocal
'@

$RunBatPath = Join-Path $ProjectRoot "run.bat"
Set-Content -Path $RunBatPath -Value $RunBat
Write-Success "Created run.bat"

# Create activate.bat for quick venv activation
$ActivateBat = @'
@echo off
REM Activate MT Pipeline virtual environment
call "%~dp0venv\Scripts\activate.bat"
echo Virtual environment activated. Type 'deactivate' to exit.
'@

$ActivateBatPath = Join-Path $ProjectRoot "activate.bat"
Set-Content -Path $ActivateBatPath -Value $ActivateBat
Write-Success "Created activate.bat"

# ============================================
# Summary
# ============================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Check if API key is configured
$envContent = ""
if (Test-Path $EnvFile) {
    $envContent = Get-Content $EnvFile -Raw
}

if ($envContent -match "GEMINI_API_KEY=(.+)" -and $Matches[1] -ne "your-api-key-here" -and $Matches[1].Length -gt 10) {
    Write-Success "API Key: Configured"
} else {
    Write-Warning "API Key: NOT CONFIGURED"
    Write-Host "  Please edit .env and add your Gemini API key" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Quick Start:" -ForegroundColor Cyan
Write-Host "  1. Open this folder in VSCodium/VSCode" -ForegroundColor White
Write-Host "  2. Press Ctrl+Shift+P -> 'Tasks: Run Task'" -ForegroundColor White
Write-Host "  3. Select 'MTL: Translate Volume'" -ForegroundColor White
Write-Host ""
Write-Host "Or use command line:" -ForegroundColor Cyan
Write-Host "  .\run.bat translate <volume_id>" -ForegroundColor White
Write-Host "  .\run.bat list" -ForegroundColor White
Write-Host "  .\run.bat check" -ForegroundColor White
Write-Host ""
Write-Host "Directory Structure:" -ForegroundColor Cyan
Write-Host "  INPUT/   - Place your EPUB files here" -ForegroundColor White
Write-Host "  WORK/    - Processing workspace (auto-created)" -ForegroundColor White
Write-Host "  OUTPUT/  - Final translated EPUBs" -ForegroundColor White
Write-Host ""
