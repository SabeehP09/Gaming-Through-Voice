# 🎤 Voice Recognition Backend

Complete offline voice recognition system for gaming and authentication.

## 🌟 Features

### 1. Voice Authentication (Like Siri)
- **Speaker Recognition**: Identify users by their unique voice characteristics
- **Voice Enrollment**: Register new users with voice samples
- **Voice Verification**: Verify user identity for login
- **Voice Identification**: Automatically identify which user is speaking

### 2. Voice Command Recognition
- **Offline Speech-to-Text**: Works without internet using PocketSphinx
- **Custom Commands**: Define your own voice commands
- **Gaming Commands**: Pre-configured commands for game control
- **Navigation Commands**: Control app navigation with voice
- **Continuous Listening**: Background voice command recognition

### 3. REST API Server
- **Flask-based API**: Easy integration with C# application
- **Base64 Audio Transfer**: Efficient audio data transmission
- **Real-time Processing**: Fast response times
- **Error Handling**: Robust error management

---

## 📋 Requirements

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows 10/11
- **RAM**: Minimum 4GB (8GB recommended)
- **Microphone**: Any USB or built-in microphone

### Python Packages
All required packages are listed in `requirements.txt`

---

## 🚀 Installation

### Step 1: Install Python
1. Download Python 3.8+ from [python.org](https://www.python.org/downloads/)
2. During installation, check "Add Python to PATH"
3. Verify installation:
   ```bash
   python --version
   ```

### Step 2: Install Dependencies
```bash
cd VoiceBackend
pip install -r requirements.txt
```

### Step 3: Install PyAudio (Windows)
PyAudio requires special installation on Windows:

```bash
pip install pipwin
pipwin install pyaudio
```

Or download the wheel file from:
https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

Then install:
```bash
pip install PyAudio‑0.2.11‑cp38‑cp38‑win_amd64.whl
```

### Step 4: Test Installation
```bash
python -c "import speech_recognition; print('✓ Speech Recognition OK')"
python -c "import sklearn; print('✓ Scikit-learn OK')"
python -c "import librosa; print('✓ Librosa OK')"
```

---

## 🎯 Quick Start

### 1. Start the API Server
```bash
cd VoiceBackend
python voice_api_server.py
```

You should see:
```
🚀 Starting Voice Recognition API Server...
📡 Server will be available at: http://localhost:5000
 * Running on http://0.0.0.0:5000
```

### 2. Test the Server
Open a browser and go to: `http://localhost:5000/health`

You should see:
```json
{
  "status": "healthy",
  "services": {
    "authentication": "running",
    "command_recognition": "running"
  }
}
```

### 3. Test Voice Authentication
```python
from voice_authentication import VoiceAuthenticator

# Initialize
auth = VoiceAuthenticator()

# Enroll a user (record 3-5 seconds of speech)
auth.enroll_user(user_id=1, audio_file_path="user1_voice.wav")

# Verify the user
is_verified, confidence = auth.verify_user(
    user_id=1, 
    audio_file_path="user1_test.wav"
)

print(f"Verified: {is_verified}, Confidence: {confidence}%")
```

### 4. Test Voice Commands
```python
from voice_command_recognizer import VoiceCommandRecognizer

# Initialize
recognizer = VoiceCommandRecognizer()

# List available commands
recognizer.list_commands()

# Recognize a command
print("Say a command...")
category, action, confidence = recognizer.recognize_command()

if action:
    print(f"Command: {action} ({confidence}% confidence)")
```

---

## 📚 API Documentation

### Base URL
```
http://localhost:5000
```

### Authentication Endpoints

#### 1. Enroll User
**POST** `/auth/enroll`

Enroll a new user for voice authentication.

**Request:**
```json
{
  "user_id": 123,
  "audio_data": "base64_encoded_audio_data"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User 123 enrolled successfully"
}
```

#### 2. Verify User
**POST** `/auth/verify`

Verify if voice matches enrolled user.

**Request:**
```json
{
  "user_id": 123,
  "audio_data": "base64_encoded_audio_data",
  "threshold": -50
}
```

**Response:**
```json
{
  "verified": true,
  "confidence": 85.5,
  "user_id": 123
}
```

#### 3. Identify User
**POST** `/auth/identify`

Identify which enrolled user is speaking.

**Request:**
```json
{
  "audio_data": "base64_encoded_audio_data",
  "threshold": -50
}
```

**Response:**
```json
{
  "identified": true,
  "user_id": "123",
  "confidence": 82.3
}
```

#### 4. Delete User
**POST** `/auth/delete`

Delete user's voice model.

**Request:**
```json
{
  "user_id": 123
}
```

**Response:**
```json
{
  "success": true,
  "message": "User 123 deleted"
}
```

### Command Recognition Endpoints

#### 1. Recognize Command
**POST** `/commands/recognize`

Recognize voice command from audio.

**Request:**
```json
{
  "audio_data": "base64_encoded_audio_data",
  "threshold": 0.7
}
```

**Response:**
```json
{
  "recognized": true,
  "text": "jump",
  "category": "gaming",
  "action": "JUMP",
  "confidence": 95
}
```

#### 2. List Commands
**GET** `/commands/list?category=gaming`

Get available commands.

**Response:**
```json
{
  "commands": {
    "navigation": {
      "go home": "HOME",
      "open settings": "SETTINGS"
    },
    "gaming": {
      "jump": "JUMP",
      "attack": "ATTACK"
    }
  }
}
```

#### 3. Add Command
**POST** `/commands/add`

Add a new voice command.

**Request:**
```json
{
  "category": "gaming",
  "phrase": "shoot",
  "action": "SHOOT"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Command added: shoot -> SHOOT"
}
```

#### 4. Remove Command
**POST** `/commands/remove`

Remove a voice command.

**Request:**
```json
{
  "category": "gaming",
  "phrase": "shoot"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Command removed: shoot"
}
```

### System Endpoints

#### 1. Health Check
**GET** `/health`

Check if server is running.

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "authentication": "running",
    "command_recognition": "running"
  }
}
```

#### 2. System Info
**GET** `/system/info`

Get system information.

**Response:**
```json
{
  "enrolled_users": 5,
  "total_commands": 25,
  "command_categories": ["navigation", "gaming", "system"],
  "models_directory": "voice_models",
  "commands_file": "commands.json"
}
```

---

## 🎮 Default Voice Commands

### Navigation Commands
- "go home" → HOME
- "open dashboard" → DASHBOARD
- "show profile" → PROFILE
- "open settings" → SETTINGS
- "show games" → GAMES
- "voice commands" → VOICE_COMMANDS

### Gaming Commands
- "jump" → JUMP
- "move forward" → FORWARD
- "move backward" → BACKWARD
- "move left" → LEFT
- "move right" → RIGHT
- "attack" → ATTACK
- "defend" → DEFEND
- "pause game" → PAUSE
- "resume game" → RESUME
- "quit game" → QUIT

### System Commands
- "start listening" → START_LISTEN
- "stop listening" → STOP_LISTEN
- "help" → HELP
- "repeat" → REPEAT
- "cancel" → CANCEL
- "confirm" → CONFIRM
- "yes" → YES
- "no" → NO

---

## 🔧 Configuration

### Voice Authentication Settings

Edit `voice_authentication.py`:

```python
# Number of Gaussian components (higher = more accurate but slower)
self.n_components = 16

# Number of MFCC coefficients
self.n_mfcc = 13

# Verification threshold (lower = more strict)
threshold = -50
```

### Voice Command Settings

Edit `voice_command_recognizer.py`:

```python
# Energy threshold for voice detection
self.recognizer.energy_threshold = 4000

# Pause threshold (seconds of silence)
self.recognizer.pause_threshold = 0.8

# Command matching threshold (0-1)
threshold = 0.7
```

---

## 🐛 Troubleshooting

### Issue: PyAudio Installation Fails
**Solution**: Use pipwin or download wheel file
```bash
pip install pipwin
pipwin install pyaudio
```

### Issue: Microphone Not Detected
**Solution**: Check microphone permissions in Windows Settings
1. Settings → Privacy → Microphone
2. Allow apps to access microphone

### Issue: Poor Recognition Accuracy
**Solutions**:
1. Record in quiet environment
2. Speak clearly and at normal pace
3. Adjust `energy_threshold` in recognizer
4. Use better quality microphone

### Issue: Server Won't Start
**Solution**: Check if port 5000 is available
```bash
netstat -ano | findstr :5000
```

Kill process if needed:
```bash
taskkill /PID <process_id> /F
```

### Issue: Slow Recognition
**Solutions**:
1. Reduce `n_components` in authenticator
2. Use shorter audio samples
3. Close other applications

---

## 📊 Performance Tips

### For Better Accuracy:
1. **Enrollment**: Record 5-10 seconds of clear speech
2. **Environment**: Use in quiet room
3. **Microphone**: Use good quality USB microphone
4. **Training**: Enroll with multiple samples

### For Faster Processing:
1. Reduce `n_components` to 8-12
2. Use shorter audio samples (2-3 seconds)
3. Lower `n_mfcc` to 10-12
4. Enable GPU acceleration (TensorFlow)

---

## 🔐 Security Notes

1. **Voice Models**: Stored locally in `voice_models/` directory
2. **Audio Data**: Not stored permanently (only during processing)
3. **API Access**: Runs on localhost by default
4. **Production**: Use HTTPS and authentication for production

---

## 📝 License

This voice recognition backend is part of the Gaming Through Voice Recognition System.

---

## 🆘 Support

For issues or questions:
1. Check troubleshooting section
2. Review API documentation
3. Test with example scripts
4. Check Python and package versions

---

## 🎉 Ready to Use!

Your voice recognition backend is now set up and ready to integrate with the C# application!

Start the server:
```bash
python voice_api_server.py
```

Then run your C# application to start using voice features!
