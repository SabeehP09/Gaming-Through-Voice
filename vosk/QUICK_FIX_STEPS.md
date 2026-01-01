# Quick Fix Steps - VOSK Voice Recognition

## The Problem
VoiceListener.exe is failing because PyInstaller didn't package the VOSK DLLs correctly.

## The Solution (4 Steps)

### Step 0: Rebuild Project (REQUIRED - 1 minute)
**The .csproj file was just updated to copy voice_listener.py**

In Visual Studio:
1. Click **Build** > **Rebuild Solution** (or press Ctrl+Shift+B)
2. Wait for build to complete

This copies `voice_listener.py` to `bin\Debug\vosk\VoiceListenerApp\`

---

### Step 1: Verify Python Setup (2 minutes)
```powershell
cd "F:\Abdullah\Old version\GamingThroughVoiceRecognitionSystem\vosk\VoiceListenerApp"
.\test_python_setup.ps1
```

**If any tests fail**, install missing packages:
```powershell
pip install vosk pyaudio
```

### Step 2: Test Python Script (1 minute)
```powershell
cd "..\..\bin\Debug\vosk\VoiceListenerApp"
python voice_listener.py
```

**Expected output**:
```
============================================================
VOSK Voice Listener for Gaming Through Voice Recognition
============================================================

[VOICE] Loading VOSK model from: vosk-model-small-en-us-0.15
[VOICE] Model loaded successfully
...
LISTENING FOR VOICE COMMANDS...
```

**Test it**: Say "hello world" into your microphone

**Expected**: Console shows `[VOICE] Recognized: 'hello world'`

**If it works**: Press Ctrl+C to stop, proceed to Step 3

**If it doesn't work**: See troubleshooting below

### Step 3: Rebuild and Test Application (2 minutes)
1. In Visual Studio, click **Build > Rebuild Solution**
2. Run the application (F5)
3. Check Debug Output window for:
```
[VOICE] Found Python script at: ...
[VOICE] Attempting to start with Python...
[VOICE] VoiceListener started with Python (PID: XXXXX)
```
4. Say "go home" - application should navigate to dashboard

**Done!** Voice recognition is now working.

## Quick Troubleshooting

### Python Not Found
```powershell
# Check if Python is installed
python --version

# If not found, install from: https://www.python.org/downloads/
# Make sure to check "Add Python to PATH" during installation
```

### VOSK Not Installed
```powershell
pip install vosk
```

### PyAudio Not Installed
```powershell
pip install pyaudio
```

### VOSK Model Missing
1. Download: https://alphacephei.com/vosk/models
2. Get: vosk-model-small-en-us-0.15 (40MB)
3. Extract to: `bin\Debug\vosk\vosk-model-small-en-us-0.15`

### Microphone Not Working
1. Check Windows Settings > Privacy > Microphone
2. Allow desktop apps to access microphone
3. Check microphone volume in Sound settings
4. Close other apps using the microphone

### Still Not Working?
See detailed guide: `vosk/FIX_VOSK_ISSUE.md`

## What Changed?

The C# application now runs `python voice_listener.py` instead of `VoiceListener.exe`. This is:
- ✅ More reliable (no PyInstaller issues)
- ✅ Easier to debug (see Python errors directly)
- ✅ Faster to develop (no recompiling needed)
- ✅ Better error messages

The .exe is still there as a fallback if Python isn't available.

## Testing Commands

After fixing, test with these voice commands:
- "go home" - Navigate to dashboard
- "logout" - Log out
- "add game" - Open add game window
- "open settings" - Navigate to settings
- "minimize" - Minimize window
- "maximize" - Maximize window

## Need More Help?

1. **Setup verification**: Run `vosk/VoiceListenerApp/test_python_setup.ps1`
2. **Voice monitoring**: Run `vosk/test_voice_commands.ps1`
3. **File monitoring**: Run `vosk/test_file_monitoring.ps1`
4. **Full guide**: Read `vosk/FIX_VOSK_ISSUE.md`
5. **Manual testing**: Read `vosk/TEST_VOSK_MANUAL.md`
