@echo off
echo ========================================
echo Voice Recognition API Server
echo (No Microphone Version)
echo ========================================
echo.

REM Check required packages
echo Checking dependencies...
python -c "import flask" 2>nul
if errorlevel 1 (
    echo [ERROR] Flask not installed
    echo Installing Flask...
    pip install flask flask-cors
)

python -c "import numpy" 2>nul
if errorlevel 1 (
    echo [ERROR] NumPy not installed
    echo Installing NumPy...
    pip install numpy
)

python -c "import sklearn" 2>nul
if errorlevel 1 (
    echo [ERROR] Scikit-learn not installed
    echo Installing Scikit-learn...
    pip install scikit-learn
)

python -c "import soundfile" 2>nul
if errorlevel 1 (
    echo [ERROR] SoundFile not installed
    echo Installing SoundFile...
    pip install soundfile
)

python -c "import librosa" 2>nul
if errorlevel 1 (
    echo [ERROR] Librosa not installed
    echo Installing Librosa...
    pip install librosa
)

python -c "import python_speech_features" 2>nul
if errorlevel 1 (
    echo [ERROR] python_speech_features not installed
    echo Installing python_speech_features...
    pip install python_speech_features
)

echo.
echo [OK] All required dependencies found
echo.
echo ========================================
echo Starting Server (No Microphone Mode)
echo ========================================
echo.
echo This version works with pre-recorded audio only.
echo Voice authentication will work perfectly!
echo Live speech recognition requires PyAudio.
echo.
echo Server starting on http://localhost:5000
echo Press Ctrl+C to stop
echo.

python voice_api_server_no_mic.py

pause
