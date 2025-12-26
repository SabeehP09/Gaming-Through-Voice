@echo off
REM ============================================================================
REM OpenCV Face Recognition Server - Installation Script
REM ============================================================================
REM This script installs all required dependencies for the OpenCV server
REM Requirements: Python 3.8+ must be installed and in PATH
REM ============================================================================

echo.
echo ============================================================================
echo OpenCV Face Recognition Server - Installation
echo ============================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [INFO] Python found:
python --version
echo.

REM Check Python version (must be 3.8+)
python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3.8 or higher is required
    echo Current version is too old. Please upgrade Python.
    pause
    exit /b 1
)

echo [INFO] Python version is compatible
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo ============================================================================
echo Step 1: Creating virtual environment (optional but recommended)
echo ============================================================================
echo.

set /p USE_VENV="Create a virtual environment? (y/n, default=y): "
if "%USE_VENV%"=="" set USE_VENV=y

if /i "%USE_VENV%"=="y" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [WARNING] Failed to create virtual environment
        echo Continuing with global Python installation...
    ) else (
        echo [INFO] Activating virtual environment...
        call venv\Scripts\activate.bat
        echo [INFO] Virtual environment activated
    )
    echo.
)

echo ============================================================================
echo Step 2: Upgrading pip
echo ============================================================================
echo.

python -m pip install --upgrade pip
if errorlevel 1 (
    echo [WARNING] Failed to upgrade pip, continuing anyway...
)
echo.

echo ============================================================================
echo Step 3: Installing Python dependencies
echo ============================================================================
echo.

if not exist requirements.txt (
    echo [ERROR] requirements.txt not found in current directory
    echo Please ensure you are running this script from the opencv_server directory
    pause
    exit /b 1
)

echo [INFO] Installing packages from requirements.txt...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    echo.
    echo Troubleshooting:
    echo - Check your internet connection
    echo - Try running: pip install --upgrade pip
    echo - Try installing packages individually
    echo - See TROUBLESHOOTING.md for more help
    pause
    exit /b 1
)

echo.
echo [INFO] All dependencies installed successfully
echo.

echo ============================================================================
echo Step 4: Downloading OpenCV models
echo ============================================================================
echo.

if not exist download_models.py (
    echo [WARNING] download_models.py not found, skipping model download
    echo You will need to download models manually
) else (
    echo [INFO] Downloading required face detection and recognition models...
    python download_models.py
    if errorlevel 1 (
        echo [WARNING] Model download failed or incomplete
        echo You may need to download models manually
        echo See models/README.md for download links
    ) else (
        echo [INFO] Models downloaded successfully
    )
)
echo.

echo ============================================================================
echo Step 5: Verifying installation
echo ============================================================================
echo.

echo [INFO] Running installation verification...
python -c "import flask; import cv2; import numpy; import pyodbc; print('[OK] All required packages imported successfully')"
if errorlevel 1 (
    echo [ERROR] Installation verification failed
    echo Some packages may not be installed correctly
    pause
    exit /b 1
)
echo.

REM Check if models exist
if exist models\deploy.prototxt (
    echo [OK] deploy.prototxt found
) else (
    echo [WARNING] deploy.prototxt not found in models directory
)

if exist models\res10_300x300_ssd_iter_140000.caffemodel (
    echo [OK] res10_300x300_ssd_iter_140000.caffemodel found
) else (
    echo [WARNING] res10_300x300_ssd_iter_140000.caffemodel not found in models directory
)

if exist models\openface_nn4.small2.v1.t7 (
    echo [OK] openface_nn4.small2.v1.t7 found
) else (
    echo [WARNING] openface_nn4.small2.v1.t7 not found in models directory
)
echo.

REM Check if config exists
if exist config.json (
    echo [OK] config.json found
) else (
    echo [WARNING] config.json not found - server may not start correctly
)
echo.

echo ============================================================================
echo Installation Complete!
echo ============================================================================
echo.
echo Next steps:
echo 1. Ensure SQL Server is running with the GamingVoiceRecognition database
echo 2. Run the database setup script: setup_database.sql
echo 3. Start the server using: start_opencv_server.bat
echo.
echo For troubleshooting, see TROUBLESHOOTING.md
echo.

if /i "%USE_VENV%"=="y" (
    echo NOTE: Virtual environment created. To activate it manually, run:
    echo       venv\Scripts\activate.bat
    echo.
)

pause
