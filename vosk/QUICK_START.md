# VOSK Voice Recognition - Quick Start Guide

## ✅ What's Already Done

The VOSK voice recognition system has been successfully integrated into your application:

- ✅ C# services created (VoiceListenerManager, GlobalVoiceCommandHandler)
- ✅ Python voice listener script created
- ✅ Python script compiled to VoiceListener.exe
- ✅ Project configuration updated
- ✅ Application startup/shutdown integrated
- ✅ 20+ voice commands implemented

## 🔴 What You Need to Do

### Step 1: Download VOSK Model (Required!)

The voice recognition **will not work** without the VOSK model.

1. **Download the model**:
   - Visit: https://alphacephei.com/vosk/models
   - Download: **vosk-model-small-en-us-0.15** (40MB ZIP file)

2. **Extract the model**:
   - Extract the ZIP file
   - You should see a folder named `vosk-model-small-en-us-0.15`

3. **Copy to project**:
   - Copy the entire `vosk-model-small-en-us-0.15` folder
   - Paste it into: `F:\Abdullah\Old version\GamingThroughVoiceRecognitionSystem\vosk\`

4. **Verify structure**:
   ```
   vosk/
   ├── vosk-model-small-en-us-0.15/
   │   ├── am/
   │   │   └── final.mdl
   │   ├── conf/
   │   ├── graph/
   │   ├── ivector/
   │   └── README
   └── VoiceListenerApp/
       ├── VoiceListener.exe  ✅ (already created)
       └── voice_listener.txt
   ```

### Step 2: Build and Test

1. **Build the solution** in Visual Studio:
   - Press `F6` or go to Build → Build Solution
   - This will copy all VOSK files to the output directory

2. **Run the application**:
   - Press `F5` or click Start
   - A console window should appear (VoiceListener.exe)
   - Check the Output window in Visual Studio for messages

3. **Test voice commands**:
   - Say: **"go home"** → Should navigate to dashboard
   - Say: **"add game"** → Should open add game window
   - Say: **"logout"** → Should log out
   - Say: **"help"** → Should show voice commands

## 🎤 Available Voice Commands

### Global Commands (work anywhere)

| Say This | What Happens |
|----------|--------------|
| "go home" or "open dashboard" | Navigate to dashboard |
| "logout" or "sign out" | Log out current user |
| "add game" or "new game" | Activate home window (requires login) |
| "open settings" or "settings" | Navigate to settings |
| "go to profile" or "profile" | Navigate to profile |
| "voice commands" or "help" | Show voice commands help |
| "close window" or "close" | Close current window |
| "minimize" | Minimize window |
| "maximize" | Maximize/restore window |
| "exit" or "quit" | Exit application |

### Window-Specific Commands

**Login Window**:
- "manual login" → Show manual login form
- "face login" → Start face recognition
- "voice login" → Start voice login

**Sign Up Window**:
- "signup" → Complete registration
- "capture face" → Capture face data
- "record voice" → Record voice data

## 🔧 Troubleshooting

### "ERROR: VOSK model folder not found"

**Problem**: VoiceListener.exe can't find the model

**Solution**:
1. Make sure you downloaded and extracted the model
2. Verify the folder is named exactly: `vosk-model-small-en-us-0.15`
3. Check it's in the correct location: `vosk/vosk-model-small-en-us-0.15/`
4. Rebuild the solution to copy files to output directory

### "ERROR: Could not access microphone"

**Problem**: VoiceListener.exe can't access your microphone

**Solution**:
1. Check microphone is connected and working
2. Go to Windows Settings → Privacy → Microphone
3. Enable "Allow apps to access your microphone"
4. Close other apps using the microphone (Skype, Discord, Teams)

### VoiceListener.exe doesn't start

**Problem**: No console window appears

**Solution**:
1. Check that `VoiceListener.exe` exists in `bin\Debug\vosk\VoiceListenerApp\`
2. Try running `VoiceListener.exe` manually to see error messages
3. Check antivirus isn't blocking it
4. Run Visual Studio as Administrator

### Commands not recognized

**Problem**: Speaking but nothing happens

**Solution**:
1. Check VoiceListener.exe console shows recognized text
2. Speak clearly and at normal pace
3. Reduce background noise
4. Move closer to microphone
5. Check `voice_listener.txt` is being updated

### High CPU usage

**Problem**: Application uses too much CPU

**Solution**:
1. This is normal - voice recognition uses 5-10% CPU
2. To reduce: Edit `Services/VoiceListenerManager.cs`
3. Change polling interval from 10ms to 50ms:
   ```csharp
   VoiceListenerManager.StartMonitoring(ProcessGlobalCommand, intervalMs: 50);
   ```

## 📊 Expected Behavior

When everything is working correctly:

1. **Application starts**:
   - Output window shows: `[APP] Initializing VOSK voice recognition system...`
   - Output window shows: `[VOICE] VoiceListener.exe started successfully`
   - A console window appears showing "LISTENING FOR VOICE COMMANDS..."

2. **You speak a command**:
   - VoiceListener.exe console shows: `[VOICE] Recognized: 'go home'`
   - Output window shows: `[VOICE] New command detected: 'go home'`
   - Output window shows: `[VOICE] Processing command: 'go home'`
   - Application navigates to home/dashboard

3. **Application closes**:
   - Output window shows: `[APP] Application shutting down...`
   - Output window shows: `[VOICE] VoiceListener.exe stopped successfully`
   - Console window closes

## 🎯 Next Steps

After you get voice recognition working:

1. **Customize commands**: Edit `Services/GlobalVoiceCommandHandler.cs` to add new commands
2. **Adjust settings**: Modify polling interval, confidence threshold, etc.
3. **Add visual feedback**: Show recognized commands in the UI
4. **Try different models**: Download larger models for better accuracy

## 📚 Documentation

- **Complete Setup Guide**: `vosk/SETUP_GUIDE.md`
- **Python App Details**: `vosk/VoiceListenerApp/README.md`
- **VOSK Documentation**: https://alphacephei.com/vosk/

## ⚡ Quick Test

To quickly test if everything is set up correctly:

1. Open Command Prompt
2. Navigate to: `vosk\VoiceListenerApp\`
3. Run: `VoiceListener.exe`
4. If you see "LISTENING FOR VOICE COMMANDS..." - it's working!
5. Say something and check if text appears in the console
6. Press Ctrl+C to stop

If this works, then the C# application will work too!

## 🆘 Still Having Issues?

Check these files for detailed troubleshooting:
- `vosk/SETUP_GUIDE.md` - Complete setup instructions
- `vosk/VoiceListenerApp/README.md` - Python app documentation
- Visual Studio Output window - Look for `[VOICE]` and `[APP]` messages

---

**Remember**: The VOSK model is **required** - the system will not work without it!

Download it from: https://alphacephei.com/vosk/models (vosk-model-small-en-us-0.15)
