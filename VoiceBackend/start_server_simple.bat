@echo off
echo ========================================
echo Starting Voice Recognition API Server
echo (Simple Mode - No Virtual Environment)
echo ========================================
echo.

REM Check if Flask is installed
python -c "import flask" 2>nul
if errorlevel 1 (
    echo [ERROR] Flask is not installed
    echo.
    echo Please run: install_dependencies.bat
    echo.
    pause
    exit /b 1
)

echo [OK] Dependencies found
echo.
echo Starting server on http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python voice_api_server.py

pause
