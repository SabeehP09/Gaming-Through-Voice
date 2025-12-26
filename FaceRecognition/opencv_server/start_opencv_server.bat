@echo off
REM ============================================================================
REM OpenCV Face Recognition Server - Startup Script
REM ============================================================================
REM This script starts the Flask server for face recognition
REM Make sure to run install_opencv_server.bat first
REM ============================================================================

echo.
echo ============================================================================
echo OpenCV Face Recognition Server
echo ============================================================================
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please run install_opencv_server.bat first
    pause
    exit /b 1
)

echo [INFO] Python version:
python --version
echo.

REM Check if virtual environment exists and activate it
if exist venv\Scripts\activate.bat (
    echo [INFO] Activating virtual environment...
    call venv\Scripts\activate.bat
    echo [INFO] Virtual environment activated
    echo.
) else (
    echo [INFO] No virtual environment found, using global Python
    echo.
)

REM Check if required packages are installed
echo [INFO] Checking dependencies...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Flask is not installed
    echo Please run install_opencv_server.bat first
    pause
    exit /b 1
)

python -c "import cv2" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] OpenCV is not installed
    echo Please run install_opencv_server.bat first
    pause
    exit /b 1
)

python -c "import pyodbc" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pyodbc is not installed
    echo Please run install_opencv_server.bat first
    pause
    exit /b 1
)

echo [OK] All dependencies found
echo.

REM Check if app.py exists
if not exist app.py (
    echo [ERROR] app.py not found in current directory
    echo Please ensure you are running this script from the opencv_server directory
    pause
    exit /b 1
)

REM Check if config.json exists
if not exist config.json (
    echo [WARNING] config.json not found
    echo Server will use default configuration
    echo.
)

REM Check if models exist
echo [INFO] Checking models...
set MODELS_OK=1

if not exist models\deploy.prototxt (
    echo [WARNING] deploy.prototxt not found in models directory
    set MODELS_OK=0
)

if not exist models\res10_300x300_ssd_iter_140000.caffemodel (
    echo [WARNING] res10_300x300_ssd_iter_140000.caffemodel not found in models directory
    set MODELS_OK=0
)

if not exist models\openface_nn4.small2.v1.t7 (
    echo [WARNING] openface_nn4.small2.v1.t7 not found in models directory
    set MODELS_OK=0
)

if %MODELS_OK%==0 (
    echo.
    echo [WARNING] Some models are missing!
    echo Please run: python download_models.py
    echo.
    set /p CONTINUE="Continue anyway? (y/n): "
    if /i not "%CONTINUE%"=="y" (
        echo Server startup cancelled
        pause
        exit /b 1
    )
) else (
    echo [OK] All models found
)
echo.

REM Create logs directory if it doesn't exist
if not exist logs (
    echo [INFO] Creating logs directory...
    mkdir logs
)

REM Display server information
echo ============================================================================
echo Starting Flask Server
echo ============================================================================
echo.
echo Server will start on: http://127.0.0.1:5000
echo.
echo Available endpoints:
echo   GET  /health         - Check server health
echo   POST /register       - Register a new face
echo   POST /authenticate   - Authenticate a face
echo.
echo Press Ctrl+C to stop the server
echo.
echo ============================================================================
echo.

REM Set Flask environment variables
set FLASK_APP=app.py
set FLASK_ENV=production

REM Start the Flask server
echo [INFO] Starting server...
echo.

python app.py

REM If we get here, the server has stopped
echo.
echo ============================================================================
echo Server stopped
echo ============================================================================
echo.

REM Check if there was an error
if errorlevel 1 (
    echo [ERROR] Server exited with an error
    echo Check logs/errors.log for details
    echo.
    echo Common issues:
    echo - Port 5000 already in use
    echo - Database connection failed
    echo - Models not loaded correctly
    echo.
    echo See TROUBLESHOOTING.md for help
) else (
    echo [INFO] Server shut down normally
)

echo.
pause
