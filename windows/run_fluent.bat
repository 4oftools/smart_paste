@echo off
chcp 65001 >nul
REM Smart Paste Fluent Run Script

echo Starting Smart Paste Fluent...

uv run python main_fluent.py

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to run! Please check if all dependencies are installed:
    echo   uv sync
    pause
)
