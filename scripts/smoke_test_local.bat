@echo off
REM End-to-end smoke test with local Ollama (Windows)

echo === Cardinal Biggles - Local Smoke Test ===
echo.

set CONFIG=config\local_ollama.yaml
set TOPIC=Artificial Intelligence
set OUTPUT=.\reports\local\smoke_test.md

echo Step 1: Checking prerequisites...

where ollama >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Ollama not installed
    exit /b 1
)

echo Prerequisites OK
echo.

REM Create output directory
if not exist ".\reports\local" mkdir ".\reports\local"

echo Step 2: Running research workflow...
echo Topic: %TOPIC%
echo Config: %CONFIG%
echo Output: %OUTPUT%
echo.

python -m cli.main research "%TOPIC%" --config "%CONFIG%" --output "%OUTPUT%" --no-hil

if %ERRORLEVEL% EQU 0 (
    echo.
    echo === SMOKE TEST PASSED ===
    echo Report: %OUTPUT%
    echo.
    echo Preview (first 10 lines):
    powershell -Command "Get-Content '%OUTPUT%' -TotalCount 10"
) else (
    echo.
    echo === SMOKE TEST FAILED ===
    exit /b 1
)
