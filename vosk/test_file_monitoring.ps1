# Test File Monitoring Script
# This script simulates voice commands by writing to the file
# Use this to test if the C# application is reading commands correctly

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "File Monitoring Test Script" -ForegroundColor Yellow
Write-Host "Tests if C# app reads commands from voice_listener.txt" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host ""

$commandFilePath = "bin\Debug\vosk\VoiceListenerApp\voice_listener.txt"

# Check if file exists
if (-not (Test-Path $commandFilePath)) {
    Write-Host "Creating voice_listener.txt..." -ForegroundColor Yellow
    New-Item -Path $commandFilePath -ItemType File -Force | Out-Null
}

Write-Host "Instructions:" -ForegroundColor Cyan
Write-Host "1. Start the Gaming Through Voice Recognition application" -ForegroundColor White
Write-Host "2. Make sure you're logged in and on the dashboard" -ForegroundColor White
Write-Host "3. Keep the application window visible" -ForegroundColor White
Write-Host "4. This script will write test commands to the file" -ForegroundColor White
Write-Host "5. Watch the application to see if it responds" -ForegroundColor White
Write-Host ""

$response = Read-Host "Is the application running and ready? (Y/N)"

if ($response -ne "Y" -and $response -ne "y") {
    Write-Host "Please start the application first, then run this script again" -ForegroundColor Yellow
    exit
}

Write-Host ""
Write-Host "Starting test sequence..." -ForegroundColor Green
Write-Host ""

# Test commands
$testCommands = @(
    @{ Command = "go home"; Description = "Navigate to dashboard"; Wait = 3 },
    @{ Command = "open settings"; Description = "Navigate to settings"; Wait = 3 },
    @{ Command = "go home"; Description = "Navigate back to dashboard"; Wait = 3 },
    @{ Command = "add game"; Description = "Open add game window"; Wait = 3 },
    @{ Command = "close window"; Description = "Close current window"; Wait = 2 },
    @{ Command = "minimize"; Description = "Minimize application"; Wait = 2 },
    @{ Command = "maximize"; Description = "Maximize application"; Wait = 2 }
)

$successCount = 0
$totalTests = $testCommands.Count

foreach ($test in $testCommands) {
    $command = $test.Command
    $description = $test.Description
    $wait = $test.Wait
    
    Write-Host "Test: $description" -ForegroundColor Cyan
    Write-Host "  Writing command: '$command'" -ForegroundColor White
    
    try {
        # Write command to file
        Set-Content -Path $commandFilePath -Value $command -NoNewline
        
        Write-Host "  ✓ Command written to file" -ForegroundColor Green
        Write-Host "  Waiting $wait seconds for application to respond..." -ForegroundColor Yellow
        
        # Wait for response
        Start-Sleep -Seconds $wait
        
        # Ask user if it worked
        Write-Host "  Did the application respond correctly? (Y/N): " -NoNewline -ForegroundColor Yellow
        $userResponse = Read-Host
        
        if ($userResponse -eq "Y" -or $userResponse -eq "y") {
            Write-Host "  ✓ Test PASSED" -ForegroundColor Green
            $successCount++
        } else {
            Write-Host "  ✗ Test FAILED" -ForegroundColor Red
        }
        
    } catch {
        Write-Host "  ✗ Error writing to file: $_" -ForegroundColor Red
    }
    
    Write-Host ""
}

# Clear the file
Write-Host "Cleaning up..." -ForegroundColor Cyan
Set-Content -Path $commandFilePath -Value "" -NoNewline
Write-Host "✓ Command file cleared" -ForegroundColor Green
Write-Host ""

# Summary
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "Test Results" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host ""
Write-Host "Tests Passed: $successCount / $totalTests" -ForegroundColor $(if ($successCount -eq $totalTests) { "Green" } elseif ($successCount -gt 0) { "Yellow" } else { "Red" })
Write-Host "Success Rate: $([math]::Round(($successCount / $totalTests) * 100, 2))%" -ForegroundColor $(if ($successCount -eq $totalTests) { "Green" } elseif ($successCount -gt 0) { "Yellow" } else { "Red" })
Write-Host ""

if ($successCount -eq $totalTests) {
    Write-Host "✓ All tests passed! File monitoring is working correctly." -ForegroundColor Green
} elseif ($successCount -gt 0) {
    Write-Host "⚠ Some tests failed. Check the following:" -ForegroundColor Yellow
    Write-Host "  - Is the application window active?" -ForegroundColor White
    Write-Host "  - Are you on the correct window for the command?" -ForegroundColor White
    Write-Host "  - Check Debug Output in Visual Studio for errors" -ForegroundColor White
} else {
    Write-Host "✗ All tests failed. Possible issues:" -ForegroundColor Red
    Write-Host "  - File monitoring may not be started" -ForegroundColor White
    Write-Host "  - GlobalVoiceCommandHandler may not be initialized" -ForegroundColor White
    Write-Host "  - Check Debug Output in Visual Studio" -ForegroundColor White
    Write-Host "  - Verify VoiceListenerManager.StartMonitoring() was called" -ForegroundColor White
}

Write-Host ""
