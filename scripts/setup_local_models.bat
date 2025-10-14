@echo off
REM Setup script for local Ollama models (Windows)

echo === Cardinal Biggles - Local Model Setup ===
echo.

REM Check if Ollama is installed
where ollama >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Ollama is not installed
    echo Please install from: https://ollama.com
    exit /b 1
)

echo Ollama is installed
echo.

echo Option 1: Minimal Setup (Recommended for testing)
echo   - Model: llama3.1:8b
echo   - RAM: ~8GB
echo   - Speed: Fast
echo.

set /p choice="Pull llama3.1:8b? (y/n): "

if /i "%choice%"=="y" (
    echo.
    echo Pulling llama3.1:8b...
    ollama pull llama3.1:8b

    if %ERRORLEVEL% EQU 0 (
        echo.
        echo Setup complete! You can now run:
        echo   python -m cli.main research "Test Topic" --config config/local_ollama.yaml
    ) else (
        echo Failed to pull model
        exit /b 1
    )
) else (
    echo Cancelled
    exit /b 0
)
