@echo off
REM ============================================
REM MT Publishing Pipeline - Windows Setup
REM ============================================
REM This script sets up the pipeline on Windows.
REM Run from the pipeline directory.
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ========================================
echo   MT Publishing Pipeline - Windows Setup
echo ========================================
echo.

REM Get script directory
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
cd /d "%PROJECT_ROOT%"

echo Project root: %CD%
echo.

REM ============================================
REM 1. Check Python Installation
REM ============================================
echo [1/5] Checking Python installation...

set PYTHON_CMD=
set PYTHON_VERSION=

REM Try python command
python --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYTHON_VERSION=%%v
    set PYTHON_CMD=python
    goto :python_found
)

REM Try python3 command
python3 --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    for /f "tokens=2" %%v in ('python3 --version 2^>^&1') do set PYTHON_VERSION=%%v
    set PYTHON_CMD=python3
    goto :python_found
)

REM Try py launcher
py --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    for /f "tokens=2" %%v in ('py --version 2^>^&1') do set PYTHON_VERSION=%%v
    set PYTHON_CMD=py
    goto :python_found
)

echo [ERROR] Python 3.10+ is required but not found.
echo.
echo Please install Python from:
echo   - https://www.python.org/downloads/
echo   - winget install Python.Python.3.11
echo   - choco install python
echo.
pause
exit /b 1

:python_found
echo [OK] Found Python %PYTHON_VERSION% (using '%PYTHON_CMD%')

REM ============================================
REM 2. Create Virtual Environment
REM ============================================
echo.
echo [2/5] Setting up virtual environment...

set "VENV_PATH=%PROJECT_ROOT%\venv"
set "VENV_PYTHON=%VENV_PATH%\Scripts\python.exe"
set "VENV_ACTIVATE=%VENV_PATH%\Scripts\activate.bat"

if exist "%VENV_PYTHON%" (
    echo [INFO] Virtual environment already exists
    set /p RECREATE="Recreate it? (y/N): "
    if /i "!RECREATE!"=="y" (
        echo Removing old virtual environment...
        rmdir /s /q "%VENV_PATH%"
        %PYTHON_CMD% -m venv "%VENV_PATH%"
        echo [OK] Virtual environment recreated
    )
) else (
    echo Creating virtual environment...
    %PYTHON_CMD% -m venv "%VENV_PATH%"
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)

REM ============================================
REM 3. Install Dependencies
REM ============================================
echo.
echo [3/5] Installing dependencies...

if not exist "%PROJECT_ROOT%\requirements.txt" (
    echo [ERROR] requirements.txt not found
    pause
    exit /b 1
)

echo Upgrading pip...
"%VENV_PYTHON%" -m pip install --upgrade pip -q

echo Installing packages from requirements.txt...
"%VENV_PYTHON%" -m pip install -r "%PROJECT_ROOT%\requirements.txt"

if %ERRORLEVEL% equ 0 (
    echo [OK] Dependencies installed successfully
) else (
    echo [WARNING] Some dependencies may have failed to install
)

REM ============================================
REM 4. Configure Environment
REM ============================================
echo.
echo [4/5] Configuring environment...

set "ENV_FILE=%PROJECT_ROOT%\.env"

if exist "%ENV_FILE%" (
    echo [OK] .env file exists
    findstr /c:"GEMINI_API_KEY=your-api-key-here" "%ENV_FILE%" >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        echo [WARNING] API key not configured in .env file
        echo           Please edit .env and add your Gemini API key
    ) else (
        echo [OK] API key appears to be configured
    )
) else (
    echo Creating .env file...
    (
        echo # MT Publishing Pipeline Environment Configuration
        echo # ================================================
        echo.
        echo # Required: Your Gemini API Key
        echo GEMINI_API_KEY=your-api-key-here
        echo.
        echo # Optional: Override default model
        echo # GEMINI_MODEL=gemini-2.5-pro
    ) > "%ENV_FILE%"
    echo [OK] .env file created
    echo [WARNING] Please edit .env and add your Gemini API key
)

REM ============================================
REM 5. Create Convenience Scripts
REM ============================================
echo.
echo [5/5] Creating convenience scripts...

REM Create run.bat
(
    echo @echo off
    echo REM MT Publishing Pipeline - Quick Run Script
    echo setlocal
    echo set "SCRIPT_DIR=%%~dp0"
    echo set "VENV_PYTHON=%%SCRIPT_DIR%%venv\Scripts\python.exe"
    echo.
    echo if not exist "%%VENV_PYTHON%%" ^(
    echo     echo ERROR: Virtual environment not found. Run setup first.
    echo     exit /b 1
    echo ^)
    echo.
    echo if "%%1"=="" ^(
    echo     echo MT Publishing Pipeline
    echo     echo.
    echo     echo Usage: run.bat ^<command^> [volume_id]
    echo     echo.
    echo     echo Commands:
    echo     echo   translate ^<volume_id^>  - Translate a volume
    echo     echo   build ^<volume_id^>      - Build EPUB
    echo     echo   run ^<volume_id^>        - Full pipeline
    echo     echo   list                   - List volumes
    echo     echo   check                  - Check API/models
    echo     exit /b 0
    echo ^)
    echo.
    echo if "%%1"=="translate" ^(
    echo     "%%VENV_PYTHON%%" -m pipeline.translator.agent --volume %%2 %%3 %%4 %%5
    echo ^) else if "%%1"=="build" ^(
    echo     "%%VENV_PYTHON%%" "%%SCRIPT_DIR%%scripts\mtl.py" build %%2
    echo ^) else if "%%1"=="run" ^(
    echo     "%%VENV_PYTHON%%" "%%SCRIPT_DIR%%scripts\mtl.py" run %%2
    echo ^) else if "%%1"=="list" ^(
    echo     "%%VENV_PYTHON%%" "%%SCRIPT_DIR%%scripts\mtl.py" list
    echo ^) else if "%%1"=="check" ^(
    echo     "%%VENV_PYTHON%%" "%%SCRIPT_DIR%%check_models.py"
    echo ^) else ^(
    echo     echo Unknown command: %%1
    echo     exit /b 1
    echo ^)
    echo endlocal
) > "%PROJECT_ROOT%\run.bat"
echo [OK] Created run.bat

REM Create activate.bat
(
    echo @echo off
    echo call "%%~dp0venv\Scripts\activate.bat"
    echo echo Virtual environment activated. Type 'deactivate' to exit.
) > "%PROJECT_ROOT%\activate.bat"
echo [OK] Created activate.bat

REM ============================================
REM Summary
REM ============================================
echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Quick Start:
echo   1. Edit .env and add your GEMINI_API_KEY
echo   2. Place EPUB files in INPUT/
echo   3. Run: run.bat translate ^<volume_id^>
echo.
echo Commands:
echo   run.bat list              - List available volumes
echo   run.bat check             - Test API connection
echo   run.bat translate ^<id^>    - Translate a volume
echo   run.bat build ^<id^>        - Build EPUB
echo.
echo For VSCodium/VSCode:
echo   Open this folder and use Ctrl+Shift+P -^> "Tasks: Run Task"
echo.

pause
