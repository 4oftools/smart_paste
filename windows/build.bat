@echo off
chcp 65001 >nul
REM Smart Paste Build Script

echo ====================================
echo Smart Paste - Build Script
echo ====================================
echo.

REM Check if pyinstaller is installed
uv run python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [ERROR] PyInstaller not found, installing...
    uv pip install pyinstaller
)

REM Clean old build files
if exist build (
    echo [CLEAN] Deleting old build directory...
    rmdir /s /q build
)
if exist dist (
    echo [CLEAN] Deleting old dist directory...
    rmdir /s /q dist
)
if exist SmartPaste.spec (
    echo [CLEAN] Deleting old spec file...
    del SmartPaste.spec
)

REM Run build command
echo [BUILD] Starting build...
uv run pyinstaller --onefile --windowed --name=SmartPaste --add-data="resources;resources" main.py

echo.
if exist dist\SmartPaste.exe (
    echo [SUCCESS] Build complete! Executable located at: dist\SmartPaste.exe
) else (
    echo [ERROR] Build failed!
)

pause
