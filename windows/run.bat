@echo off
chcp 65001 >nul
REM Smart Paste Run Script

echo Starting Smart Paste...

uv run python main.py

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to run! Please check if all dependencies are installed:
    echo   uv sync
    pause
)
