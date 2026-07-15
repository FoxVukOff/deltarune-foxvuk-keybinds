@echo off
cd /d "%~dp0"

REM Check if keyboard module is installed
python -c "import keyboard" 2>nul
if %errorlevel% neq 0 (
    echo Installing keyboard module...
    pip install keyboard
)

REM Check for admin rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ============================================
    echo  This script requires Administrator privileges.
    echo  Relaunching as Administrator...
    echo ============================================
    powershell -Command "Start-Process cmd -ArgumentList '/c cd /d \"%~dp0\" && python deltarune_remap.py' -Verb RunAs"
    exit /b
)

python deltarune_remap.py
