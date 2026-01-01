# 🔧 Voice Backend Troubleshooting Guide

## Quick Fix for "ModuleNotFoundError: No module named 'flask'"

### Option 1: Simple Installation (Recommended)

Run these commands in order:

```bash
cd VoiceBackend
install_dependencies.bat
start_server_simple.bat
```

This installs packages globally (no virtual environment) and starts the server.

### Option 2: Manual Installation

Open Command Prompt in VoiceBackend folder and run:

```bash
pip install flask flask-cors
pip install SpeechRecognition
pip install pocketsphinx
pip install numpy scipy
pip install scikit-learn
pip install librosa
pip install soundfile
pip install joblib
pip install python_speech_features
```

Then start server:
```bash
python voice_api_server.py
```

### Option 3: Fix Virtual Environment

If you want to use virtual environment:

```bash
cd VoiceBackend

# Delete old venv if exists
rmdir /s /q venv

# Create new virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start server
python voice_api_server.py
```

---

## Common Issues & Solutions

### Issue 1: "Python is not recognized"

**Problem**: Python not in PATH

**Solution**:
1. Reinstall Python from https://www.python.org/downloads/
2. During installation, CHECK "Add Python to PATH"
3. Restart Command Prompt
4. Test: `python --version`

### Issue 2: "pip is not recognized"

**Problem**: pip not in PATH

**Solution**:
```bash
python -m pip --version
```

If that works, use `python -m pip install` instead of `pip install`

### Issue 3: PyAudio Installation Fails

**Problem**: PyAudio requires C++ compiler on Windows

**Solution A** (Easiest):
```bash
pip install pipwin
pipwin install pyaudio
```

**Solution B** (Alternative):
Download wheel file from:
https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

Choose file matching your Python version:
- Python 3.8: `PyAudio‑0.2.11‑cp38‑cp38‑win_amd64.whl`
- Python 3.9: `PyAudio‑0.2.11‑cp39‑cp39‑win_amd64.whl`
- Python 3.10: `PyAudio‑0.2.11‑cp310‑cp310‑win_amd64.whl`

Then install:
```bash
pip install PyAudio‑0.2.11‑cp38‑cp38‑win_amd64.whl
```

### Issue 4: "Access Denied" during installation

**Problem**: Insufficient permissions

**Solution**:
Run Command Prompt as Administrator:
1. Search "cmd" in Start Menu
2. Right-click → "Run as administrator"
3. Navigate to VoiceBackend folder
4. Run installation commands

### Issue 5: Port 5000 Already in Use

**Problem**: Another application using port 5000

**Solution A** - Find and kill process:
```bash
netstat -ano | findstr :5000
taskkill /PID <process_id> /F
```

**Solution B** - Use different port:

Edit `voice_api_server.py`, change last line:
```python
app.run(host='0.0.0.0', port=5001, debug=True)  # Changed to 5001
```

Then update C# code:
```csharp
var voiceApi = new VoiceApiClient("http://localhost:5001");
```

### Issue 6: Virtual Environment Not Activating

**Problem**: Execution policy restriction

**Solution**:
```bash
# Run PowerShell as Administrator
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or use Command Prompt instead of PowerShell
```

### Issue 7: Slow Installation

**Problem**: Downloading large packages

**Solution**:
- Be patient (can take 10-15 minutes)
- Use faster internet connection
- Install packages one by one to see progress

### Issue 8: "No module named 'sklearn'"

**Problem**: Package name mismatch

**Solution**:
```bash
pip install scikit-learn
```

Note: Import as `sklearn` but install as `scikit-learn`

### Issue 9: TensorFlow Installation Issues

**Problem**: TensorFlow is large and complex

**Solution**:
TensorFlow is optional. If it fails, comment it out in `requirements.txt`:
```
# tensorflow==2.13.0
# keras==2.13.1
```

The system will work without it (just without deep learning features).

### Issue 10: "Microsoft Visual C++ 14.0 is required"

**Problem**: Some packages need C++ compiler

**Solution**:
Install Microsoft C++ Build Tools:
https://visualstudio.microsoft.com/visual-cpp-build-tools/

Or use pre-built wheels from:
https://www.lfd.uci.edu/~gohlke/pythonlibs/

---

## Verification Steps

After installation, verify everything works:

### 1. Check Python
```bash
python --version
```
Should show: Python 3.8 or higher

### 2. Check pip
```bash
pip --version
```
Should show pip version

### 3. Check Flask
```bash
python -c "import flask; print('Flask OK')"
```
Should print: Flask OK

### 4. Check All Dependencies
```bash
python -c "import flask, speech_recognition, sklearn, numpy, librosa; print('All OK')"
```
Should print: All OK

### 5. Start Server
```bash
python voice_api_server.py
```
Should show:
```
🚀 Starting Voice Recognition API Server...
📡 Server will be available at: http://localhost:5000
 * Running on http://0.0.0.0:5000
```

### 6. Test Server
Open browser: http://localhost:5000/health

Should show:
```json
{
  "status": "healthy",
  "services": {
    "authentication": "running",
    "command_recognition": "running"
  }
}
```

---

## Alternative: Minimal Installation

If full installation fails, use minimal version:

### Create `voice_api_server_minimal.py`:

```python
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

@app.route('/auth/enroll', methods=['POST'])
def enroll_user():
    return jsonify({'success': True, 'message': 'Minimal mode'})

@app.route('/auth/verify', methods=['POST'])
def verify_user():
    return jsonify({'verified': True, 'confidence': 85.0})

@app.route('/commands/recognize', methods=['POST'])
def recognize_command():
    return jsonify({
        'recognized': True,
        'action': 'JUMP',
        'confidence': 90
    })

if __name__ == '__main__':
    print("🚀 Starting Minimal Voice API Server...")
    app.run(host='0.0.0.0', port=5000, debug=True)
```

Install only Flask:
```bash
pip install flask flask-cors
python voice_api_server_minimal.py
```

This gives you a working API for testing C# integration.

---

## Step-by-Step Installation Guide

### For Complete Beginners:

1. **Install Python**
   - Go to https://www.python.org/downloads/
   - Download Python 3.10 (recommended)
   - Run installer
   - ✅ CHECK "Add Python to PATH"
   - Click "Install Now"
   - Wait for installation
   - Click "Close"

2. **Open Command Prompt**
   - Press Windows Key
   - Type "cmd"
   - Press Enter

3. **Navigate to VoiceBackend**
   ```bash
   cd "E:\FYP\Final Defence\New folder\Testing Version\GamingThroughVoiceRecognitionSystem\VoiceBackend"
   ```

4. **Install Dependencies**
   ```bash
   install_dependencies.bat
   ```
   - Wait 10-15 minutes
   - Watch for errors
   - If errors, see solutions above

5. **Start Server**
   ```bash
   start_server_simple.bat
   ```

6. **Test in Browser**
   - Open browser
   - Go to: http://localhost:5000/health
   - Should see: `{"status": "healthy"}`

---

## Getting Help

If you're still stuck:

1. **Check Python Version**
   ```bash
   python --version
   ```
   Must be 3.8 or higher

2. **Check pip Version**
   ```bash
   pip --version
   ```

3. **Try Upgrading pip**
   ```bash
   python -m pip install --upgrade pip
   ```

4. **Install Packages One by One**
   ```bash
   pip install flask
   pip install flask-cors
   pip install SpeechRecognition
   # etc...
   ```

5. **Check for Error Messages**
   - Copy exact error message
   - Search online for solution
   - Check package documentation

---

## Success Checklist

✅ Python 3.8+ installed
✅ pip working
✅ Flask installed
✅ All dependencies installed
✅ Server starts without errors
✅ Health endpoint returns "healthy"
✅ No firewall blocking port 5000

If all checked, you're ready to use the voice system!

---

## Quick Commands Reference

```bash
# Check Python
python --version

# Check pip
pip --version

# Upgrade pip
python -m pip install --upgrade pip

# Install Flask
pip install flask flask-cors

# Install all dependencies
pip install -r requirements.txt

# Start server (simple)
python voice_api_server.py

# Start server (with venv)
venv\Scripts\activate
python voice_api_server.py

# Check if port is in use
netstat -ano | findstr :5000

# Kill process on port
taskkill /PID <process_id> /F
```

---

Your voice backend should now be working! 🎉
