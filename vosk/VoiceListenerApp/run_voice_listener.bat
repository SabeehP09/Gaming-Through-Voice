@echo off
REM Run voice_listener.py directly with Python
REM This bypasses PyInstaller packaging issues

echo ============================================================
echo Starting VOSK Voice Listener (Python Script)
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    echo Please install Python 3.7 or higher
    pause
    exit /b 1
)

REM Check if vosk is installed
python -c "import vosk" >nul 2>&1
if errorlevel 1 (
    echo ERROR: VOSK library not installed
    echo Installing required packages...
    pip install vosk pyaudio
    if errorlevel 1 (
        echo Failed to install packages
        pause
        exit /b 1
    )
)

REM Run the voice listener
python voice_listener.py

pause
