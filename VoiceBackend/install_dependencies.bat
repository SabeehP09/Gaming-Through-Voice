@echo off
echo ========================================
echo Installing Voice Backend Dependencies
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python found
python --version
echo.

REM Install core dependencies directly (no virtual environment)
echo Installing core dependencies...
echo This may take a few minutes...
echo.

REM Install Flask and CORS
echo [1/10] Installing Flask...
pip install flask flask-cors

REM Install Speech Recognition
echo [2/10] Installing SpeechRecognition...
pip install SpeechRecognition

REM Install PocketSphinx
echo [3/10] Installing PocketSphinx...
pip install pocketsphinx

REM Install Audio Processing
echo [4/10] Installing PyAudio...
echo Note: PyAudio installation may fail on some systems
pip install pipwin
pipwin install pyaudio
if errorlevel 1 (
    echo [WARNING] PyAudio installation failed
    echo You can use the no-microphone version: start_server_no_mic.bat
    echo Or manually install PyAudio from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
)

REM Install NumPy and SciPy
echo [5/10] Installing NumPy...
pip install numpy

echo [6/10] Installing SciPy...
pip install scipy

REM Install Machine Learning
echo [7/10] Installing Scikit-learn...
pip install scikit-learn

echo [8/10] Installing Librosa...
pip install librosa

REM Install Audio File Handling
echo [9/10] Installing SoundFile...
pip install soundfile

REM Install Utilities
echo [10/10] Installing Utilities...
pip install joblib python_speech_features

echo.
echo ========================================
echo Testing Installation
echo ========================================
echo.

python -c "import flask; print('[OK] Flask')"
python -c "import speech_recognition; print('[OK] SpeechRecognition')"
python -c "import sklearn; print('[OK] Scikit-learn')"
python -c "import numpy; print('[OK] NumPy')"
python -c "import librosa; print('[OK] Librosa')"

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo You can now run: start_server_simple.bat
echo.
pause
