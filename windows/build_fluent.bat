@echo off
chcp 65001 >nul
REM Smart Paste Fluent Build Script

echo ====================================
echo Smart Paste Fluent - Build Script
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
if exist SmartPasteFluent.spec (
    echo [CLEAN] Deleting old spec file...
    del SmartPasteFluent.spec
)

REM Run build command
echo [BUILD] Starting build...
uv run pyinstaller --onefile --windowed --name=SmartPasteFluent --add-data="resources;resources" main_fluent.py

echo.
if exist dist\SmartPasteFluent.exe (
    echo [SUCCESS] Build complete! Executable located at: dist\SmartPasteFluent.exe
) else (
    echo [ERROR] Build failed!
)

pause
