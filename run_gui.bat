@echo off
REM SecureGuard Antivirus Launcher
REM This script activates the virtual environment and launches the GUI

cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
    echo Error: Virtual environment not found!
    echo Please run: python -m venv .venv
    echo Then run: .venv\Scripts\activate.bat
    echo And: pip install -r requirements.txt
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
python launcher.py
pause
