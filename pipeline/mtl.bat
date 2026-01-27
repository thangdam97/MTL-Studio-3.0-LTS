@echo off
REM ============================================
REM MT Publishing Pipeline - Windows Launcher
REM ============================================
REM Launch the interactive TUI for translation pipeline
REM
REM Usage:
REM   mtl                    # Launch TUI (default)
REM   mtl --tui              # Explicitly launch TUI
REM   mtl run <epub>         # Legacy CLI mode
REM   mtl --help             # Show help
REM ============================================

setlocal enabledelayedexpansion

REM Get script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Check for virtual environment Python first
set "VENV_PYTHON=%SCRIPT_DIR%venv\Scripts\python.exe"
set "PYTHON_CMD="

if exist "%VENV_PYTHON%" (
    set "PYTHON_CMD=%VENV_PYTHON%"
    goto :found_python
)

REM Try python command
python --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_CMD=python"
    goto :found_python
)

REM Try python3 command
python3 --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_CMD=python3"
    goto :found_python
)

REM Try py launcher
py --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_CMD=py"
    goto :found_python
)

echo.
echo ERROR: Python 3.10+ is required but not found.
echo.
echo Please install Python from:
echo   - https://www.python.org/downloads/
echo   - winget install Python.Python.3.11
echo   - choco install python
echo.
echo Make sure to check "Add Python to PATH" during installation.
echo.
pause
exit /b 1

:found_python

REM Check dependencies
"%PYTHON_CMD%" -c "import questionary; import rich" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Installing required dependencies...
    "%PYTHON_CMD%" -m pip install questionary rich -q

    "%PYTHON_CMD%" -c "import questionary; import rich" >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo.
        echo ERROR: Failed to install dependencies.
        echo Please run: pip install questionary rich
        echo.
        pause
        exit /b 1
    )
    echo Dependencies installed.
)

REM Run the pipeline
if "%~1"=="" (
    REM No arguments - launch TUI
    "%PYTHON_CMD%" "%SCRIPT_DIR%scripts\mtl.py"
) else (
    REM Pass all arguments to mtl.py
    "%PYTHON_CMD%" "%SCRIPT_DIR%scripts\mtl.py" %*
)

endlocal
