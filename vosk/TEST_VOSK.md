# VOSK Troubleshooting Guide

## Current Status
✅ App is running
✅ No compilation errors
✅ Speaker authentication working
❌ VOSK voice control not working

## Diagnostic Steps

### Step 1: Check Visual Studio Output Window

When you run the application, check the **Output** window in Visual Studio (View → Output):

Look for these messages:
```
[APP] Initializing VOSK voice recognition system...
[VOICE] Initializing VoiceListenerManager...
[VOICE] Starting VoiceListener.exe from: ...
[VOICE] VoiceListener.exe started successfully (PID: ...)
[VOICE] Starting file monitoring (interval: 10ms)...
```

**What to look for:**
- ✅ If you see "VoiceListener.exe started successfully" → Process started OK
- ❌ If you see "ERROR: VoiceListener.exe not found" → Executable missing
- ❌ If you see "WARNING: VOSK voice listener failed to start" → Process failed to start

### Step 2: Check if VoiceListener.exe Console Window Appears

When the app starts, you should see a **separate console window** with:
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

**If you DON'T see this console window:**
- The process isn't starting
- Check Output window for error messages

**If you see the console window but it shows errors:**
- "ERROR: VOSK model folder not found" → Model not copied to bin\Debug
- "ERROR: Could not access microphone" → Microphone permission issue

### Step 3: Test VoiceListener.exe Manually

1. **Close your application** (if running)

2. **Open Command Prompt**

3. **Navigate to the folder:**
   ```cmd
   cd "F:\Abdullah\Old version\GamingThroughVoiceRecognitionSystem\bin\Debug\vosk\VoiceListenerApp"
   ```

4. **Run VoiceListener.exe:**
   ```cmd
   VoiceListener.exe
   ```

5. **What should happen:**
   - Console shows "LISTENING FOR VOICE COMMANDS..."
   - Speak into your microphone
   - You should see: `[VOICE] Recognized: 'hello'` (or whatever you said)

6. **Check voice_listener.txt:**
   ```cmd
   type voice_listener.txt
   ```
   - Should show the last recognized text

**If this works manually but not in the app:**
- The C# code isn't starting the process correctly
- Check Output window for startup errors

### Step 4: Check File Monitoring

If VoiceListener.exe is running but commands aren't being processed:

1. **Check if voice_listener.txt is being updated:**
   - Navigate to: `bin\Debug\vosk\VoiceListenerApp\`
   - Open `voice_listener.txt` in Notepad
   - Speak a command
   - Check if the file updates

2. **If file updates but app doesn't respond:**
   - File monitoring isn't working
   - Check Output window for: `[VOICE] New command detected: '...'`

### Step 5: Common Issues and Solutions

#### Issue 1: No Console Window Appears

**Cause:** VoiceListener.exe isn't starting

**Solutions:**
1. Check Output window for error messages
2. Verify files exist:
   - `bin\Debug\vosk\VoiceListenerApp\VoiceListener.exe`
   - `bin\Debug\vosk\vosk-model-small-en-us-0.15\am\final.mdl`
3. Try running VoiceListener.exe manually (see Step 3)
4. Check antivirus isn't blocking it
5. Run Visual Studio as Administrator

#### Issue 2: Console Shows "ERROR: VOSK model folder not found"

**Cause:** Model files not copied to output directory

**Solutions:**
1. Rebuild the solution (Build → Rebuild Solution)
2. Check if model exists in source: `vosk\vosk-model-small-en-us-0.15\`
3. Verify .csproj has the correct configuration
4. Manually copy the model folder to `bin\Debug\vosk\`

#### Issue 3: Console Shows "ERROR: Could not access microphone"

**Cause:** Microphone permission or access issue

**Solutions:**
1. Check microphone is connected and working
2. Go to Windows Settings → Privacy → Microphone
3. Enable "Allow apps to access your microphone"
4. Close other apps using microphone (Skype, Discord, Teams)
5. Try a different microphone

#### Issue 4: VoiceListener.exe Runs But Commands Not Recognized

**Cause:** Speech recognition not working properly

**Solutions:**
1. Speak clearly and at normal pace
2. Reduce background noise
3. Move closer to microphone
4. Check console shows recognized text
5. Try simple commands: "hello", "test", "go home"

#### Issue 5: Commands Recognized But App Doesn't Respond

**Cause:** File monitoring or command processing issue

**Solutions:**
1. Check Output window for: `[VOICE] New command detected: '...'`
2. Check Output window for: `[VOICE] Processing command: '...'`
3. Verify command is in the switch statement (GlobalVoiceCommandHandler.cs)
4. Check voice_listener.txt is being cleared after processing

### Step 6: Enable Detailed Logging

To get more information, you can add temporary logging:

1. **In App.xaml.cs**, the startup should show:
   ```
   [APP] Initializing VOSK voice recognition system...
   [VOICE] Initializing VoiceListenerManager...
   [VOICE] VoiceListener.exe started successfully (PID: 12345)
   [VOICE] Starting file monitoring (interval: 10ms)...
   [VOICE] GlobalVoiceCommandHandler initialized successfully
   ```

2. **When you speak**, you should see:
   ```
   [VOICE] New command detected: 'go home'
   [VOICE] Processing command: 'go home'
   [VOICE] Navigating to Home
   ```

### Step 7: Quick Test Checklist

Run through this checklist:

- [ ] Application starts without errors
- [ ] VoiceListener.exe console window appears
- [ ] Console shows "LISTENING FOR VOICE COMMANDS..."
- [ ] Speaking into microphone shows recognized text in console
- [ ] voice_listener.txt file updates when you speak
- [ ] Output window shows "[VOICE] New command detected: '...'"
- [ ] Output window shows "[VOICE] Processing command: '...'"
- [ ] Application responds to the command

**If all checked:** Voice control is working! 🎉

**If some unchecked:** Find the first unchecked item and troubleshoot that step.

## Quick Fixes

### Fix 1: Rebuild Everything
```
1. Clean Solution (Build → Clean Solution)
2. Rebuild Solution (Build → Rebuild Solution)
3. Run application
```

### Fix 2: Manual File Copy
If files aren't copying automatically:
```cmd
xcopy /E /I /Y "vosk\*" "bin\Debug\vosk\"
```

### Fix 3: Test Microphone
```cmd
cd "bin\Debug\vosk\VoiceListenerApp"
VoiceListener.exe
```
Speak and verify text appears.

### Fix 4: Check Process
While app is running:
```powershell
Get-Process | Where-Object {$_.ProcessName -like "*VoiceListener*"}
```
Should show the VoiceListener process.

## What to Report

If you need help, provide:

1. **Output window messages** (all [VOICE] and [APP] lines)
2. **VoiceListener.exe console output** (if visible)
3. **Which step fails** (from checklist above)
4. **Error messages** (exact text)
5. **Manual test result** (does VoiceListener.exe work manually?)

## Expected Working Behavior

When everything works correctly:

1. **App starts:**
   - Main window opens
   - Console window appears (VoiceListener.exe)
   - Output shows successful initialization

2. **You say "go home":**
   - VoiceListener console: `[VOICE] Recognized: 'go home'`
   - Output window: `[VOICE] New command detected: 'go home'`
   - Output window: `[VOICE] Processing command: 'go home'`
   - Output window: `[VOICE] Navigating to Home`
   - App navigates to home/dashboard

3. **App closes:**
   - Output: `[APP] Application shutting down...`
   - Output: `[VOICE] VoiceListener.exe stopped successfully`
   - Console window closes

---

**Start with Step 1** and work through each step until you find where it's failing!
