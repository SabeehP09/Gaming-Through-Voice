# VOSK Voice Recognition Setup Guide

Complete guide for setting up offline voice recognition in the Gaming Through Voice Recognition System.

## Overview

This system uses VOSK for offline speech recognition, allowing users to control the application with voice commands without requiring an internet connection.

## Architecture

```
┌─────────────────────────────────────┐
│     C# WPF Application              │
│  - VoiceListenerManager.cs          │
│  - GlobalVoiceCommandHandler.cs     │
└──────────┬──────────────────────────┘
           │ Reads voice_listener.txt
           │ (every 10ms)
           ▼
┌─────────────────────────────────────┐
│  voice_listener.txt (IPC File)      │
└──────────┬──────────────────────────┘
           │ Writes recognized text
           ▼
┌─────────────────────────────────────┐
│  VoiceListener.exe (Python)         │
│  - Captures microphone audio        │
│  - Uses VOSK for recognition        │
└──────────┬──────────────────────────┘
           │ Uses
           ▼
┌─────────────────────────────────────┐
│  vosk-model-small-en-us-0.15        │
│  - Pre-trained speech model (40MB)  │
└─────────────────────────────────────┘
```

## Prerequisites

### Required Software

1. **Python 3.7+** (for development and compilation)
   - Download from: https://www.python.org/downloads/
   - Make sure to check "Add Python to PATH" during installation

2. **Visual Studio 2019+** (for C# development)
   - With .NET Framework 4.8 SDK

3. **Microphone** (any USB or built-in microphone)

### Required Python Packages

```bash
pip install vosk pyaudio pyinstaller
```

**Note for Windows PyAudio Installation**:
If `pip install pyaudio` fails, download the pre-compiled wheel:
1. Visit: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
2. Download the appropriate `.whl` for your Python version (e.g., `PyAudio‑0.2.11‑cp39‑cp39‑win_amd64.whl`)
3. Install: `pip install PyAudio‑0.2.11‑cp39‑cp39‑win_amd64.whl`

## Setup Steps

### Step 1: Download VOSK Model

1. Visit: https://alphacephei.com/vosk/models
2. Download: **vosk-model-small-en-us-0.15** (40MB)
3. Extract the ZIP file
4. Copy the extracted folder to: `vosk/vosk-model-small-en-us-0.15/`

**Verify the structure**:
```
vosk/
└── vosk-model-small-en-us-0.15/
    ├── am/
    │   └── final.mdl
    ├── conf/
    │   ├── mfcc.conf
    │   └── model.conf
    ├── graph/
    ├── ivector/
    └── README
```

### Step 2: Test Python Script

Before compiling, test that the Python script works:

```bash
cd vosk/VoiceListenerApp
python voice_listener.py
```

**Expected output**:
```
============================================================
VOSK Voice Listener for Gaming Through Voice Recognition
============================================================

[VOICE] Loading VOSK model from: vosk-model-small-en-us-0.15
[VOICE] Model loaded successfully

[VOICE] Initializing audio system...
[VOICE] Microphone stream opened successfully

============================================================
LISTENING FOR VOICE COMMANDS...
Speak clearly into your microphone
Press Ctrl+C to stop
============================================================
```

**Test by speaking**: Say "hello" or "test" and verify it appears in the console.

### Step 3: Compile Python Script to Executable

Compile the Python script to a standalone executable:

```bash
cd vosk/VoiceListenerApp

# Option 1: Single directory (recommended)
pyinstaller --name VoiceListener --onedir --console --add-data "vosk-model-small-en-us-0.15;vosk-model-small-en-us-0.15" voice_listener.py

# Option 2: Single file (if model is already in place)
pyinstaller --name VoiceListener --onefile --console voice_listener.py
```

**Copy the executable**:
```bash
# For Option 1 (onedir):
copy dist\VoiceListener\VoiceListener.exe .
copy dist\VoiceListener\_internal .\_internal

# For Option 2 (onefile):
copy dist\VoiceListener.exe .
```

**Verify**: You should now have `VoiceListener.exe` in `vosk/VoiceListenerApp/`

### Step 4: Build C# Application

1. Open `GamingThroughVoiceRecognitionSystem.sln` in Visual Studio
2. Build the solution (F6 or Build → Build Solution)
3. The VOSK files will be automatically copied to `bin/Debug/vosk/` or `bin/Release/vosk/`

**Verify the output directory**:
```
bin/Debug/
└── vosk/
    ├── vosk-model-small-en-us-0.15/
    │   └── (model files)
    └── VoiceListenerApp/
        ├── VoiceListener.exe
        └── voice_listener.txt
```

### Step 5: Test the Integration

1. Run the application from Visual Studio (F5)
2. Check the Output window (View → Output) for VOSK messages:
   ```
   [APP] Initializing VOSK voice recognition system...
   [VOICE] Initializing VoiceListenerManager...
   [VOICE] Starting VoiceListener.exe from: ...
   [VOICE] VoiceListener.exe started successfully (PID: ...)
   [VOICE] Starting file monitoring (interval: 10ms)...
   ```

3. A console window should appear showing the VoiceListener.exe output

4. **Test voice commands**:
   - Say "go home" → Should navigate to dashboard
   - Say "add game" → Should open add game window
   - Say "logout" → Should log out
   - Say "help" → Should show voice commands

## Available Voice Commands

### Global Commands (work anywhere)

| Command | Action |
|---------|--------|
| "go home", "open dashboard" | Navigate to dashboard |
| "logout", "sign out" | Log out current user |
| "add game", "new game" | Open add game window |
| "open settings", "settings" | Navigate to settings |
| "go to profile", "profile" | Navigate to profile |
| "voice commands", "help" | Show voice commands help |
| "close window", "close" | Close current window |
| "minimize" | Minimize window |
| "maximize" | Maximize/restore window |
| "exit", "quit" | Exit application |

### Window-Specific Commands

**Login Window**:
- "manual login" → Show manual login form
- "face login" → Start face recognition
- "voice login" → Start voice login

**Sign Up Window**:
- "signup" → Complete registration
- "capture face" → Capture face data
- "record voice" → Record voice data

**Voice Recording Window**:
- "start recording" → Start recording
- "stop recording" → Stop recording
- "done" → Finish and close

## Configuration

### Adjust Polling Interval

In `Services/VoiceListenerManager.cs`, modify the `StartMonitoring` call:

```csharp
// Default: 10ms (very responsive)
VoiceListenerManager.StartMonitoring(ProcessGlobalCommand, intervalMs: 10);

// For lower CPU usage: 50ms
VoiceListenerManager.StartMonitoring(ProcessGlobalCommand, intervalMs: 50);
```

### Change VOSK Model

To use a different model:

1. Download the model from https://alphacephei.com/vosk/models
2. Extract to `vosk/` directory
3. Update `MODEL_PATH` in `voice_listener.py`:
   ```python
   MODEL_PATH = "vosk-model-en-us-0.22"  # Larger, more accurate model
   ```
4. Recompile the Python script

### Add New Commands

In `Services/GlobalVoiceCommandHandler.cs`, add to the switch statement:

```csharp
case "your command":
case "alternative phrase":
    YourActionMethod();
    break;
```

## Troubleshooting

### VoiceListener.exe doesn't start

**Symptoms**: No console window appears, no voice recognition

**Solutions**:
1. Check that `VoiceListener.exe` exists in `bin/Debug/vosk/VoiceListenerApp/`
2. Check that the VOSK model is in `bin/Debug/vosk/vosk-model-small-en-us-0.15/`
3. Run `VoiceListener.exe` manually to see error messages
4. Check antivirus isn't blocking the executable
5. Run Visual Studio as Administrator

### "ERROR: VOSK model folder not found"

**Symptoms**: VoiceListener.exe shows error about missing model

**Solutions**:
1. Verify model is downloaded and extracted correctly
2. Check folder name is exactly `vosk-model-small-en-us-0.15`
3. Verify model files are present (am/, conf/, graph/, ivector/)
4. Rebuild the solution to copy files to output directory

### "ERROR: Could not access microphone"

**Symptoms**: VoiceListener.exe can't open microphone

**Solutions**:
1. Check microphone is connected and working
2. Go to Windows Settings → Privacy → Microphone → Allow apps to access microphone
3. Close other applications using the microphone (Skype, Discord, Teams, etc.)
4. Try a different microphone
5. Check Windows Sound settings → Recording devices

### Commands not recognized

**Symptoms**: Speaking but nothing happens

**Solutions**:
1. Check VoiceListener.exe console shows recognized text
2. Check `voice_listener.txt` is being updated
3. Speak clearly and at normal pace
4. Reduce background noise
5. Move closer to microphone
6. Check command is in the switch statement in `GlobalVoiceCommandHandler.cs`

### Commands execute multiple times

**Symptoms**: Same command runs repeatedly

**Solutions**:
1. Verify `ClearVoiceCommand()` is being called
2. Check `lastCommand` caching is working
3. Increase polling interval to reduce sensitivity

### High CPU usage

**Symptoms**: Application uses too much CPU

**Solutions**:
1. Increase polling interval from 10ms to 50ms or 100ms
2. Use a smaller VOSK model
3. Close unnecessary applications
4. Check for infinite loops in command processing

### VoiceListener.exe doesn't stop on exit

**Symptoms**: Process remains after closing application

**Solutions**:
1. Verify `OnExit` is being called in `App.xaml.cs`
2. Check `VoiceListenerManager.Cleanup()` is executing
3. Manually kill process in Task Manager
4. Add better error handling in cleanup code

## Performance Optimization

### CPU Usage
- **Polling interval**: 10ms = ~5% CPU, 50ms = ~2% CPU, 100ms = ~1% CPU
- **VOSK model**: Small model = ~3% CPU, Large model = ~8% CPU
- **Total**: Expect 5-10% CPU usage with default settings

### Memory Usage
- **VOSK model**: ~100MB RAM
- **Python process**: ~50MB RAM
- **C# application**: ~100MB RAM
- **Total**: ~250MB RAM

### Disk I/O
- **File polling**: ~100 reads/second (10ms interval)
- **File size**: <100 bytes per command
- **Impact**: Minimal on SSD, negligible on HDD

## Advanced Configuration

### Custom Wake Word

To add a wake word (e.g., "computer"):

```python
# In voice_listener.py, modify the recognition loop:
if text:
    if text.startswith("computer "):
        text = text.replace("computer ", "", 1)
        with open(OUTPUT_FILE, "w") as f:
            f.write(text)
```

### Confidence Threshold

To filter low-confidence results:

```python
# In voice_listener.py:
result = json.loads(recognizer.Result())
confidence = result.get("confidence", 0)
if confidence > 0.7:  # Only accept >70% confidence
    text = result.get("text", "").lower().strip()
```

### Multiple Languages

To support multiple languages:

1. Download language-specific model
2. Update `MODEL_PATH` in `voice_listener.py`
3. Recompile executable
4. Update commands in `GlobalVoiceCommandHandler.cs`

## Deployment

### For End Users

1. **Include in installer**:
   - `vosk/` folder with all contents
   - `VoiceListener.exe` (compiled)
   - VOSK model files

2. **First-run setup**:
   - Check microphone permissions
   - Test voice recognition
   - Show available commands

3. **User documentation**:
   - List of voice commands
   - Troubleshooting guide
   - How to adjust settings

### Distribution Size

- **Application**: ~50MB
- **VOSK model (small)**: ~40MB
- **VoiceListener.exe**: ~10MB
- **Total**: ~100MB

## Security Considerations

- **Offline**: No data sent to internet
- **Local processing**: All recognition happens on device
- **Privacy**: Voice data not stored (only recognized text)
- **Permissions**: Only requires microphone access

## Support and Resources

- **VOSK Documentation**: https://alphacephei.com/vosk/
- **VOSK Models**: https://alphacephei.com/vosk/models
- **PyAudio Documentation**: https://people.csail.mit.edu/hubert/pyaudio/
- **Project Documentation**: See main README.md

## License

- **VOSK**: Apache 2.0 License
- **PyAudio**: MIT License
- **This Project**: (Your license here)
