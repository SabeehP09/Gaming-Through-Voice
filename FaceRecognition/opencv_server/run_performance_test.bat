@echo off
echo Running Performance Tests...
echo.
python -c "import sys; sys.dont_write_bytecode = True; exec(open('test_performance.py').read())"
pause
