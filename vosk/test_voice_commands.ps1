# VOSK Voice Command Testing Script
# This script tests if VoiceListener.exe is writing commands to the file

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "VOSK Voice Command Testing Script" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host ""

# Configuration
$voiceListenerPath = "bin\Debug\vosk\VoiceListenerApp\VoiceListener.exe"
$commandFilePath = "bin\Debug\vosk\VoiceListenerApp\voice_listener.txt"
$modelPath = "bin\Debug\vosk\vosk-model-small-en-us-0.15"

# Test 1: Check if files exist
Write-Host "[TEST 1] Checking if required files exist..." -ForegroundColor Cyan
Write-Host ""

if (Test-Path $voiceListenerPath) {
    Write-Host "  ✓ VoiceListener.exe found" -ForegroundColor Green
} else {
    Write-Host "  ✗ VoiceListener.exe NOT found at: $voiceListenerPath" -ForegroundColor Red
    Write-Host "    Please build the project first" -ForegroundColor Yellow
    exit 1
}

if (Test-Path $commandFilePath) {
    Write-Host "  ✓ voice_listener.txt found" -ForegroundColor Green
} else {
    Write-Host "  ✗ voice_listener.txt NOT found" -ForegroundColor Red
    Write-Host "    File will be created when VoiceListener.exe starts" -ForegroundColor Yellow
}

if (Test-Path $modelPath) {
    Write-Host "  ✓ VOSK model found" -ForegroundColor Green
} else {
    Write-Host "  ✗ VOSK model NOT found at: $modelPath" -ForegroundColor Red
    Write-Host "    Please download vosk-model-small-en-us-0.15" -ForegroundColor Yellow
    Write-Host "    From: https://alphacephei.com/vosk/models" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Test 2: Check if VoiceListener.exe is currently running
Write-Host "[TEST 2] Checking if VoiceListener.exe is running..." -ForegroundColor Cyan
Write-Host ""

$process = Get-Process -Name "VoiceListener" -ErrorAction SilentlyContinue

if ($process) {
    Write-Host "  ✓ VoiceListener.exe is running (PID: $($process.Id))" -ForegroundColor Green
    $isRunning = $true
} else {
    Write-Host "  ✗ VoiceListener.exe is NOT running" -ForegroundColor Yellow
    Write-Host "    Starting VoiceListener.exe for testing..." -ForegroundColor Yellow
    $isRunning = $false
}

Write-Host ""

# Test 3: Start VoiceListener.exe if not running
if (-not $isRunning) {
    Write-Host "[TEST 3] Starting VoiceListener.exe..." -ForegroundColor Cyan
    Write-Host ""
    
    try {
        $workingDir = Split-Path -Parent $voiceListenerPath
        $process = Start-Process -FilePath $voiceListenerPath -WorkingDirectory $workingDir -PassThru -WindowStyle Normal
        
        Write-Host "  ✓ VoiceListener.exe started (PID: $($process.Id))" -ForegroundColor Green
        Write-Host "    Waiting 5 seconds for initialization..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
        
        # Check if process is still running
        if (Get-Process -Id $process.Id -ErrorAction SilentlyContinue) {
            Write-Host "  ✓ Process is running successfully" -ForegroundColor Green
        } else {
            Write-Host "  ✗ Process terminated unexpectedly" -ForegroundColor Red
            Write-Host "    Check console window for errors" -ForegroundColor Yellow
            exit 1
        }
    } catch {
        Write-Host "  ✗ Failed to start VoiceListener.exe: $_" -ForegroundColor Red
        exit 1
    }
    
    Write-Host ""
}

# Test 4: Monitor command file for changes
Write-Host "[TEST 4] Monitoring voice_listener.txt for commands..." -ForegroundColor Cyan
Write-Host ""
Write-Host "  Instructions:" -ForegroundColor Yellow
Write-Host "  1. Speak clearly into your microphone" -ForegroundColor White
Write-Host "  2. Try saying: 'go home', 'logout', 'add game'" -ForegroundColor White
Write-Host "  3. This script will monitor for 30 seconds" -ForegroundColor White
Write-Host "  4. Press Ctrl+C to stop early" -ForegroundColor White
Write-Host ""
Write-Host "  Monitoring started..." -ForegroundColor Green
Write-Host ""

$startTime = Get-Date
$duration = 30
$commandsDetected = 0
$lastContent = ""

try {
    while (((Get-Date) - $startTime).TotalSeconds -lt $duration) {
        if (Test-Path $commandFilePath) {
            $content = Get-Content $commandFilePath -Raw -ErrorAction SilentlyContinue
            
            if ($content -and $content.Trim() -ne "" -and $content -ne $lastContent) {
                $commandsDetected++
                $timestamp = Get-Date -Format "HH:mm:ss"
                Write-Host "  [$timestamp] Command detected: '$($content.Trim())'" -ForegroundColor Green
                $lastContent = $content
            }
        }
        
        Start-Sleep -Milliseconds 100
    }
} catch {
    Write-Host ""
    Write-Host "  Monitoring stopped by user" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "  Monitoring complete!" -ForegroundColor Cyan
Write-Host "  Commands detected: $commandsDetected" -ForegroundColor $(if ($commandsDetected -gt 0) { "Green" } else { "Yellow" })
Write-Host ""

# Test 5: Check final file content
Write-Host "[TEST 5] Checking final file content..." -ForegroundColor Cyan
Write-Host ""

if (Test-Path $commandFilePath) {
    $finalContent = Get-Content $commandFilePath -Raw -ErrorAction SilentlyContinue
    
    if ($finalContent -and $finalContent.Trim() -ne "") {
        Write-Host "  Current content: '$($finalContent.Trim())'" -ForegroundColor Green
    } else {
        Write-Host "  File is empty" -ForegroundColor Yellow
    }
} else {
    Write-Host "  File does not exist" -ForegroundColor Red
}

Write-Host ""

# Test 6: Cleanup prompt
Write-Host "[TEST 6] Cleanup" -ForegroundColor Cyan
Write-Host ""

if (-not $isRunning) {
    Write-Host "  VoiceListener.exe was started by this script" -ForegroundColor Yellow
    $response = Read-Host "  Do you want to stop it? (Y/N)"
    
    if ($response -eq "Y" -or $response -eq "y") {
        try {
            Stop-Process -Id $process.Id -Force
            Write-Host "  ✓ VoiceListener.exe stopped" -ForegroundColor Green
        } catch {
            Write-Host "  ✗ Failed to stop process: $_" -ForegroundColor Red
        }
    } else {
        Write-Host "  VoiceListener.exe left running (PID: $($process.Id))" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "Testing Complete!" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host ""

# Summary
Write-Host "SUMMARY:" -ForegroundColor Cyan
Write-Host "--------" -ForegroundColor Cyan
if ($commandsDetected -gt 0) {
    Write-Host "✓ VOSK system is working correctly!" -ForegroundColor Green
    Write-Host "  Commands were detected and written to file" -ForegroundColor Green
} else {
    Write-Host "⚠ No commands detected" -ForegroundColor Yellow
    Write-Host "  Possible issues:" -ForegroundColor Yellow
    Write-Host "  - Microphone not working or not selected" -ForegroundColor White
    Write-Host "  - Background noise too high" -ForegroundColor White
    Write-Host "  - Speaking too quietly" -ForegroundColor White
    Write-Host "  - VOSK model not recognizing speech" -ForegroundColor White
    Write-Host ""
    Write-Host "  Try:" -ForegroundColor Yellow
    Write-Host "  - Check microphone in Windows Sound settings" -ForegroundColor White
    Write-Host "  - Speak louder and more clearly" -ForegroundColor White
    Write-Host "  - Reduce background noise" -ForegroundColor White
    Write-Host "  - Check VoiceListener.exe console for errors" -ForegroundColor White
}
Write-Host ""
