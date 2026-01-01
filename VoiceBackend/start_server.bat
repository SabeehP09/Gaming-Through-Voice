@echo off
echo ========================================
echo Starting Voice Recognition API Server
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [WARNING] Virtual environment not found
    echo Running setup first...
    echo.
    call setup.bat
    if errorlevel 1 (
        echo [ERROR] Setup failed
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Verify Flask is installed
python -c "import flask" 2>nul
if errorlevel 1 (
    echo [WARNING] Flask not found, installing dependencies...
    pip install flask flask-cors
)

REM Start server
echo.
echo Starting server on http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python voice_api_server.py

pause
