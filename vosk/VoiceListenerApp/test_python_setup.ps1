# Test Python and VOSK Setup
# This script checks if Python and required packages are installed

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "Python and VOSK Setup Test" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host ""

# Test 1: Check Python
Write-Host "[TEST 1] Checking Python installation..." -ForegroundColor Cyan
Write-Host ""

try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Python found: $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Python not found in PATH" -ForegroundColor Red
        Write-Host "    Please install Python 3.7+ from python.org" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "  ✗ Python not found: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Test 2: Check VOSK
Write-Host "[TEST 2] Checking VOSK library..." -ForegroundColor Cyan
Write-Host ""

$voskTest = python -c "import vosk; print(vosk.__version__)" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ VOSK library found: version $voskTest" -ForegroundColor Green
} else {
    Write-Host "  ✗ VOSK library not installed" -ForegroundColor Red
    Write-Host "    Installing VOSK..." -ForegroundColor Yellow
    pip install vosk
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ VOSK installed successfully" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Failed to install VOSK" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# Test 3: Check PyAudio
Write-Host "[TEST 3] Checking PyAudio library..." -ForegroundColor Cyan
Write-Host ""

$pyaudioTest = python -c "import pyaudio; print('OK')" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ PyAudio library found" -ForegroundColor Green
} else {
    Write-Host "  ✗ PyAudio library not installed" -ForegroundColor Red
    Write-Host "    Installing PyAudio..." -ForegroundColor Yellow
    pip install pyaudio
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ PyAudio installed successfully" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Failed to install PyAudio" -ForegroundColor Red
        Write-Host "    You may need to install it manually" -ForegroundColor Yellow
        Write-Host "    See: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio" -ForegroundColor Yellow
    }
}

Write-Host ""

# Test 4: Check VOSK model
Write-Host "[TEST 4] Checking VOSK model..." -ForegroundColor Cyan
Write-Host ""

if (Test-Path "vosk-model-small-en-us-0.15") {
    Write-Host "  ✓ VOSK model found" -ForegroundColor Green
} else {
    Write-Host "  ✗ VOSK model not found" -ForegroundColor Red
    Write-Host "    Please download the model:" -ForegroundColor Yellow
    Write-Host "    1. Visit: https://alphacephei.com/vosk/models" -ForegroundColor White
    Write-Host "    2. Download: vosk-model-small-en-us-0.15 (40MB)" -ForegroundColor White
    Write-Host "    3. Extract to: $(Get-Location)\vosk-model-small-en-us-0.15" -ForegroundColor White
}

Write-Host ""

# Test 5: Test voice_listener.py
Write-Host "[TEST 5] Testing voice_listener.py..." -ForegroundColor Cyan
Write-Host ""

if (Test-Path "voice_listener.py") {
    Write-Host "  ✓ voice_listener.py found" -ForegroundColor Green
    
    Write-Host "    Testing imports..." -ForegroundColor Yellow
    $importTest = python -c "import sys; sys.path.insert(0, '.'); from voice_listener import *" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Script imports successfully" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Script has import issues (may be normal)" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ✗ voice_listener.py not found" -ForegroundColor Red
}

Write-Host ""

# Summary
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "Setup Test Complete" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host ""

Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. If all tests passed, run: python voice_listener.py" -ForegroundColor White
Write-Host "2. Or rebuild the application and it will use Python automatically" -ForegroundColor White
Write-Host ""
