@echo off
echo ========================================
echo Voice Recognition Backend Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python is installed
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment created
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install requirements
echo Installing required packages...
echo This may take several minutes...
echo.

pip install -r requirements.txt
if errorlevel 1 (
    echo [WARNING] Some packages failed to install
    echo Trying alternative installation methods...
    echo.
    
    REM Try installing PyAudio separately
    echo Installing PyAudio...
    pip install pipwin
    pipwin install pyaudio
)

echo.
echo ========================================
echo Testing Installation
echo ========================================
echo.

REM Test imports
python -c "import speech_recognition; print('[OK] Speech Recognition')"
python -c "import sklearn; print('[OK] Scikit-learn')"
python -c "import librosa; print('[OK] Librosa')"
python -c "import flask; print('[OK] Flask')"
python -c "import numpy; print('[OK] NumPy')"

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the voice recognition server:
echo   1. Run: venv\Scripts\activate.bat
echo   2. Run: python voice_api_server.py
echo.
echo Or simply run: start_server.bat
echo.
pause
