@echo off
echo ========================================
echo Installing with Conda (Alternative Method)
echo ========================================
echo.

echo Creating conda environment...
conda create -n facerecog python=3.9 -y

echo.
echo Activating environment...
call conda activate facerecog

echo.
echo Installing dlib from conda-forge...
conda install -c conda-forge dlib -y

echo.
echo Installing other packages...
pip install face_recognition flask flask-cors Pillow numpy

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo To use:
echo 1. conda activate facerecog
echo 2. python face_recognition_server.py
echo.
pause
