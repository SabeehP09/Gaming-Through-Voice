@echo off
echo ========================================
echo Installing PyAudio for Windows
echo ========================================
echo.

REM Check Python version
python --version
echo.

REM Method 1: Try pipwin
echo [Method 1] Trying pipwin...
pip install pipwin
pipwin install pyaudio

REM Test if it worked
python -c "import pyaudio; print('[SUCCESS] PyAudio installed via pipwin')" 2>nul
if not errorlevel 1 (
    echo.
    echo ========================================
    echo PyAudio installed successfully!
    echo ========================================
    pause
    exit /b 0
)

echo [Method 1] Failed, trying alternative...
echo.

REM Method 2: Try pip directly
echo [Method 2] Trying pip install...
pip install pyaudio

REM Test if it worked
python -c "import pyaudio; print('[SUCCESS] PyAudio installed via pip')" 2>nul
if not errorlevel 1 (
    echo.
    echo ========================================
    echo PyAudio installed successfully!
    echo ========================================
    pause
    exit /b 0
)

echo [Method 2] Failed, trying wheel file...
echo.

REM Method 3: Download and install wheel
echo [Method 3] Downloading PyAudio wheel file...
echo.
echo Please download the appropriate wheel file for your Python version from:
echo https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
echo.
echo For Python 3.13: PyAudio-0.2.14-cp313-cp313-win_amd64.whl
echo For Python 3.12: PyAudio-0.2.14-cp312-cp312-win_amd64.whl
echo For Python 3.11: PyAudio-0.2.14-cp311-cp311-win_amd64.whl
echo For Python 3.10: PyAudio-0.2.14-cp310-cp310-win_amd64.whl
echo.
echo After downloading, place the .whl file in this folder and run:
echo pip install PyAudio-0.2.14-cpXXX-cpXXX-win_amd64.whl
echo.
echo Or use the no-microphone version: start_server_no_mic.bat
echo.
pause
