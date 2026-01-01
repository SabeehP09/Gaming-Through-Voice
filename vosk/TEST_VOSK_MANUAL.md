# Manual VOSK Testing Guide

## Test Objective
Verify that the VOSK voice recognition system is properly integrated and functioning correctly.

## Prerequisites
- Application has been started at least once
- VoiceListener.exe exists in `bin\Debug\vosk\VoiceListenerApp\`
- VOSK model exists in `bin\Debug\vosk\vosk-model-small-en-us-0.15\`
- Microphone is connected and working

## Test 1: Verify VoiceListener.exe Runs Standalone

### Steps:
1. Open Command Prompt
2. Navigate to: `bin\Debug\vosk\VoiceListenerApp\`
3. Run: `VoiceListener.exe`

### Expected Output:
```
============================================================
VOSK Voice Listener for Gaming Through Voice Recognition
============================================================

[VOICE] Loading VOSK model from: vosk-model-small-en-us-0.15
[VOICE] Model loaded successfully

[VOICE] Initializing audio system...
[VOICE] Opening microphone stream (16000Hz, mono, 16-bit)
[VOICE] Microphone stream opened successfully

[VOICE] Output file created: voice_listener.txt

============================================================
LISTENING FOR VOICE COMMANDS...
Speak clearly into your microphone
Press Ctrl+C to stop
============================================================
```

### Test Actions:
1. Say "hello world" clearly into microphone
2. Check if console shows: `[VOICE] Recognized: 'hello world'`
3. Open `voice_listener.txt` and verify it contains: `hello world`
4. Say "go home"
5. Check if console shows: `[VOICE] Recognized: 'go home'`
6. Verify `voice_listener.txt` now contains: `go home`
7. Press Ctrl+C to stop

### Pass Criteria:
- ✅ VoiceListener.exe starts without errors
- ✅ Console shows "LISTENING FOR VOICE COMMANDS..."
- ✅ Spoken words appear in console as "[VOICE] Recognized: '...'"
- ✅ voice_listener.txt file is updated with recognized text
- ✅ Process exits cleanly on Ctrl+C

### Troubleshooting:
- **ERROR: VOSK model folder not found**: Download model from https://alphacephei.com/vosk/models
- **ERROR: Could not access microphone**: Check microphone permissions, close other apps using mic
- **No recognition**: Speak louder, check microphone volume in Windows settings
- **Wrong words recognized**: Use clearer pronunciation, reduce background noise

---

## Test 2: Verify C# Application Integration

### Steps:
1. Start the Gaming Through Voice Recognition application
2. Watch the Debug Output window in Visual Studio

### Expected Debug Output:
```
[APP] Initializing VOSK voice recognition system...
[VOICE] Initializing VoiceListenerManager...
[VOICE] VoiceListenerManager initialized successfully
[VOICE] Starting VoiceListener.exe from: F:\...\VoiceListener.exe
[VOICE] VoiceListener.exe started successfully (PID: XXXXX)
[APP] VOSK voice listener started successfully
[VOICE] Initializing GlobalVoiceCommandHandler...
[VOICE] Starting file monitoring (interval: 10ms)...
[VOICE] File monitoring started successfully
[VOICE] GlobalVoiceCommandHandler initialized successfully
[APP] VOSK voice recognition system initialized
```

### Pass Criteria:
- ✅ All initialization messages appear
- ✅ VoiceListener.exe PID is shown
- ✅ No error messages
- ✅ File monitoring starts successfully

---

## Test 3: Test Global Voice Commands

### Test Commands:

| Command | Expected Action | Window Context |
|---------|----------------|----------------|
| "go home" | Navigate to dashboard | Any window |
| "open dashboard" | Navigate to dashboard | Any window |
| "logout" | Log out user | Any window |
| "sign out" | Log out user | Any window |
| "add game" | Open add game window | Any window |
| "open settings" | Navigate to settings | Any window |
| "go to settings" | Navigate to settings | Any window |
| "go to profile" | Navigate to profile | Any window |
| "open profile" | Navigate to profile | Any window |
| "voice commands" | Show voice commands help | Any window |
| "help" | Show voice commands help | Any window |
| "close window" | Close current window | Any window |
| "close" | Close current window | Any window |
| "minimize" | Minimize application | Any window |
| "maximize" | Maximize application | Any window |
| "exit" | Close application | Any window |
| "quit" | Close application | Any window |

### Testing Procedure:
For each command:
1. Say the command clearly
2. Wait 1-2 seconds
3. Verify the expected action occurs
4. Check Debug Output for: `[VOICE] Command received: '<command>'`

### Pass Criteria:
- ✅ At least 80% of commands work correctly
- ✅ Commands execute within 2 seconds of speaking
- ✅ No duplicate command executions
- ✅ Debug output shows command was received

---

## Test 4: Test Window-Specific Commands

### Login Window Commands:

| Command | Expected Action |
|---------|----------------|
| "manual login" | Show manual login form |
| "face login" | Start face recognition |
| "voice record" | Start voice recording |

### Signup Window Commands:

| Command | Expected Action |
|---------|----------------|
| "signup" | Submit signup form |
| "capture face" | Open face capture window |
| "record voice" | Start voice recording |

### Voice Recording Window Commands:

| Command | Expected Action |
|---------|----------------|
| "start recording" | Begin voice recording |
| "stop recording" | Stop voice recording |
| "ok" | Confirm and close |
| "done" | Confirm and close |

### Testing Procedure:
1. Navigate to specific window
2. Say window-specific command
3. Verify action only works in correct window context
4. Try same command in different window - should not work

### Pass Criteria:
- ✅ Window-specific commands work in correct context
- ✅ Window-specific commands don't work in wrong context
- ✅ Global commands still work in all windows

---

## Test 5: Test File Monitoring

### Steps:
1. Start application
2. Manually write text to `bin\Debug\vosk\VoiceListenerApp\voice_listener.txt`
3. Save the file
4. Wait 1 second
5. Check if command was processed

### Test Cases:

| File Content | Expected Result |
|--------------|----------------|
| `go home` | Navigate to dashboard |
| `GO HOME` | Navigate to dashboard (case insensitive) |
| `  go home  ` | Navigate to dashboard (trimmed) |
| `` (empty) | No action |
| `unknown command xyz` | No action, debug shows unknown |

### Pass Criteria:
- ✅ File changes detected within 100ms
- ✅ Commands processed correctly
- ✅ Case insensitive matching works
- ✅ Whitespace is trimmed
- ✅ File is cleared after processing

---

## Test 6: Test Process Lifecycle

### Test 6.1: Normal Startup
1. Start application
2. Check Task Manager for VoiceListener.exe process
3. Verify process is running

**Pass**: ✅ VoiceListener.exe appears in Task Manager

### Test 6.2: Normal Shutdown
1. Close application normally
2. Check Task Manager
3. Verify VoiceListener.exe is terminated

**Pass**: ✅ VoiceListener.exe is not in Task Manager

### Test 6.3: Abnormal Shutdown
1. Start application
2. Kill application from Task Manager
3. Check if VoiceListener.exe is still running

**Expected**: VoiceListener.exe may remain as orphan process (this is a known limitation)

### Test 6.4: Multiple Starts
1. Start application
2. Note VoiceListener.exe PID
3. Close application
4. Start application again
5. Note new VoiceListener.exe PID

**Pass**: ✅ New process created each time, old process terminated

---

## Test 7: Test Error Handling

### Test 7.1: Missing Model
1. Rename `vosk-model-small-en-us-0.15` folder
2. Start application
3. Check Debug Output

**Expected**: Error message about missing model, app continues without voice

### Test 7.2: No Microphone
1. Disable microphone in Windows
2. Start application
3. Check Debug Output

**Expected**: Error message about microphone, app continues without voice

### Test 7.3: File Lock
1. Start application
2. Open `voice_listener.txt` in Notepad (keeps file locked)
3. Say a command
4. Check if error is handled gracefully

**Expected**: File I/O error logged, no crash

---

## Test 8: Performance Testing

### Test 8.1: CPU Usage
1. Start application
2. Open Task Manager
3. Monitor CPU usage of VoiceListener.exe
4. Speak continuously for 1 minute

**Pass**: ✅ CPU usage < 10% average

### Test 8.2: Memory Usage
1. Start application
2. Monitor memory usage
3. Speak 100 commands
4. Check for memory leaks

**Pass**: ✅ Memory usage stable around 100-150MB

### Test 8.3: Response Time
1. Say command
2. Measure time until action executes
3. Repeat 10 times

**Pass**: ✅ Average response time < 1 second

---

## Test 9: Stress Testing

### Test 9.1: Rapid Commands
1. Say 10 commands rapidly (1 per second)
2. Verify all are processed
3. Check for duplicates

**Pass**: ✅ All commands processed, no duplicates

### Test 9.2: Long Session
1. Run application for 1 hour
2. Speak commands periodically
3. Check for degradation

**Pass**: ✅ No performance degradation, no crashes

### Test 9.3: Background Noise
1. Play music or TV in background
2. Speak commands
3. Check recognition accuracy

**Pass**: ✅ Accuracy > 70% with moderate noise

---

## Test Results Summary

### Test Session Information
- **Date**: _______________
- **Tester**: _______________
- **Application Version**: _______________
- **VOSK Model**: vosk-model-small-en-us-0.15

### Results Checklist

| Test | Status | Notes |
|------|--------|-------|
| Test 1: Standalone VoiceListener | ⬜ Pass ⬜ Fail | |
| Test 2: C# Integration | ⬜ Pass ⬜ Fail | |
| Test 3: Global Commands | ⬜ Pass ⬜ Fail | |
| Test 4: Window-Specific Commands | ⬜ Pass ⬜ Fail | |
| Test 5: File Monitoring | ⬜ Pass ⬜ Fail | |
| Test 6: Process Lifecycle | ⬜ Pass ⬜ Fail | |
| Test 7: Error Handling | ⬜ Pass ⬜ Fail | |
| Test 8: Performance | ⬜ Pass ⬜ Fail | |
| Test 9: Stress Testing | ⬜ Pass ⬜ Fail | |

### Overall Assessment
⬜ **PASS** - All critical tests passed
⬜ **PASS WITH ISSUES** - Minor issues found
⬜ **FAIL** - Critical issues found

### Issues Found
1. _______________________________________________
2. _______________________________________________
3. _______________________________________________

### Recommendations
1. _______________________________________________
2. _______________________________________________
3. _______________________________________________
