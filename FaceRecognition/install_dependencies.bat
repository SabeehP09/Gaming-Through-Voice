@echo off
echo ========================================
echo Installing Face Recognition Dependencies
echo ========================================
echo.

echo Installing Python packages...
pip install face_recognition dlib numpy Pillow flask flask-cors

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Run: python face_recognition_server.py
echo 2. Server will start on http://localhost:5001
echo.
pause
