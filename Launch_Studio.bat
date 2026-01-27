@echo off
REM ============================================================
REM  MTL PUBLISHING STUDIO - Portable Edition (Windows)
REM ============================================================

echo ============================================================
echo  MTL PUBLISHING STUDIO - Portable Edition
echo ============================================================
echo.

REM Set environment variables
set "MTL_ROOT=%~dp0"
set "PYTHON_HOME=%MTL_ROOT%python_env"
set "PATH=%PYTHON_HOME%\Scripts;%PATH%"

REM Check if VSCodium exists
if not exist "%MTL_ROOT%bin\VSCodium\VSCodium.exe" (
    echo [ERROR] VSCodium.exe not found in bin\VSCodium\
    echo Please download VSCodium portable and place in bin\VSCodium\
    echo.
    echo Download from: https://github.com/VSCodium/vscodium/releases
    echo Get: VSCodium-win32-x64-^<version^>.zip
    echo.
    pause
    exit /b 1
)

REM Check if Python environment exists
if not exist "%PYTHON_HOME%\Scripts\python.exe" (
    echo [ERROR] Python environment not found
    echo.
    echo Please create Python virtual environment:
    echo   python -m venv python_env
    echo   python_env\Scripts\activate
    echo   pip install -r pipeline\requirements.txt
    echo.
    pause
    exit /b 1
)

REM Launch VSCodium with workspace
echo Launching MTL Studio...
echo.

start "" "%MTL_ROOT%bin\VSCodium\VSCodium.exe" "%MTL_ROOT%workspace\MTL_Studio.code-workspace"

echo.
echo MTL Studio is running in VSCodium.
echo.
echo You can use this terminal for CLI commands:
echo   cd pipeline
echo   python mtl.py list
echo.
echo Press any key to close this launcher...
pause >nul
