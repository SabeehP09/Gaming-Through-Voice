# 🚀 Quick Start Guide - Voice Backend

## ⚡ Fastest Way to Get Started

### Option 1: No Microphone Version (Recommended for Testing)

This version works perfectly for voice authentication but doesn't require PyAudio.

```bash
cd VoiceBackend
start_server_no_mic.bat
```

**What works:**
- ✅ Voice Authentication (Enroll, Verify, Identify)
- ✅ Command Management (Add, Remove, List)
- ✅ All API endpoints
- ✅ C# Integration

**What doesn't work:**
- ❌ Live microphone input (you send pre-recorded audio instead)

**Perfect for:**
- Testing the system
- Voice authentication features
- C# integration development
- When PyAudio won't install

---

### Option 2: Full Version (With Microphone)

Requires PyAudio installation.

#### Step 1: Install PyAudio

**For Python 3.13:**
```bash
pip install pipwin
pipwin install pyaudio
```

If that fails, download wheel from:
https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

Choose: `PyAudio-0.2.14-cp313-cp313-win_amd64.whl`

Then:
```bash
pip install PyAudio-0.2.14-cp313-cp313-win_amd64.whl
```

#### Step 2: Install Other Dependencies
```bash
pip install flask flask-cors
pip install SpeechRecognition pocketsphinx
pip install numpy scipy scikit-learn
pip install librosa soundfile
pip install python_speech_features joblib
```

#### Step 3: Start Server
```bash
python voice_api_server.py
```

---

## 🎯 Which Version Should I Use?

### Use **No Microphone Version** if:
- ✅ You just want to test the system
- ✅ PyAudio won't install
- ✅ You're developing C# integration
- ✅ You only need voice authentication
- ✅ Your C# app records audio (which it does!)

### Use **Full Version** if:
- ✅ You need live speech recognition
- ✅ You want continuous listening
- ✅ PyAudio installed successfully
- ✅ You need real-time command recognition

---

## 📝 Current Situation

Based on your error, you have Python 3.13 and PyAudio won't install easily.

**Recommended Solution:**

1. **Use No Microphone Version for now:**
   ```bash
   start_server_no_mic.bat
   ```

2. **Your C# app already records audio**, so you can:
   - Record audio in C# (using NAudio - already working)
   - Send audio to Python API
   - Get voice authentication results
   - Everything works!

3. **Later, if you want live speech recognition:**
   - Download PyAudio wheel for Python 3.13
   - Install it manually
   - Switch to full version

---

## ✅ Testing the No Microphone Version

### 1. Start Server
```bash
cd VoiceBackend
start_server_no_mic.bat
```

### 2. Test in Browser
Open: http://localhost:5000/health

Should see:
```json
{
  "status": "healthy",
  "services": {
    "authentication": "running",
    "command_recognition": "limited (no microphone)"
  }
}
```

### 3. Test from C#

```csharp
var voiceApi = new VoiceApiClient("http://localhost:5000");

// Check if server is running
bool isHealthy = await voiceApi.IsHealthyAsync();
Console.WriteLine($"Server healthy: {isHealthy}");

// Enroll user (using audio from VoiceRecordingWindow)
var enrollResponse = await voiceApi.EnrollUserAsync(userId, audioData);
Console.WriteLine($"Enrollment: {enrollResponse.Success}");

// Verify user
var verifyResponse = await voiceApi.VerifyUserAsync(userId, audioData);
Console.WriteLine($"Verified: {verifyResponse.Verified}, Confidence: {verifyResponse.Confidence}%");
```

---

## 🔧 Troubleshooting

### Server won't start
```bash
# Install Flask
pip install flask flask-cors

# Try again
start_server_no_mic.bat
```

### Import errors
```bash
# Install missing package
pip install <package_name>

# Common ones:
pip install numpy
pip install scikit-learn
pip install soundfile
pip install librosa
pip install python_speech_features
```

### Port 5000 in use
```bash
# Find process
netstat -ano | findstr :5000

# Kill it
taskkill /PID <process_id> /F

# Or edit voice_api_server_no_mic.py and change port to 5001
```

---

## 📊 Feature Comparison

| Feature | No Mic Version | Full Version |
|---------|---------------|--------------|
| Voice Authentication | ✅ Yes | ✅ Yes |
| Voice Enrollment | ✅ Yes | ✅ Yes |
| Voice Verification | ✅ Yes | ✅ Yes |
| Voice Identification | ✅ Yes | ✅ Yes |
| Command Management | ✅ Yes | ✅ Yes |
| Live Microphone | ❌ No | ✅ Yes |
| Speech Recognition | ❌ No | ✅ Yes |
| C# Integration | ✅ Yes | ✅ Yes |
| PyAudio Required | ❌ No | ✅ Yes |

---

## 🎉 You're Ready!

For your use case (voice authentication for login/signup), the **No Microphone Version is perfect** because:

1. Your C# app already records audio (VoiceRecordingWindow)
2. You send that audio to Python API
3. Python processes it and returns results
4. No need for Python to access microphone directly!

**Start the server now:**
```bash
start_server_no_mic.bat
```

Then test your C# integration! 🚀
