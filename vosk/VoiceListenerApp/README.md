# VOSK Voice Listener Application

This directory contains the Python-based voice listener application that provides offline speech recognition for the Gaming Through Voice Recognition System.

## Files

- `voice_listener.py` - Python script for voice recognition
- `voice_listener.txt` - Output file for recognized commands (created automatically)
- `VoiceListener.exe` - Compiled executable (needs to be created)

## Setup Instructions

### Step 1: Install Python Dependencies

Install the required Python packages:

```bash
pip install vosk pyaudio
```

**Note**: PyAudio may require additional setup on Windows:
- Download the appropriate `.whl` file from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
- Install with: `pip install PyAudio‑0.2.11‑cp39‑cp39‑win_amd64.whl` (adjust for your Python version)

### Step 2: Download VOSK Model

1. Visit: https://alphacephei.com/vosk/models
2. Download: **vosk-model-small-en-us-0.15** (40MB)
3. Extract the contents to: `vosk/vosk-model-small-en-us-0.15/`

The model directory should contain:
```
vosk-model-small-en-us-0.15/
├── am/
├── conf/
├── graph/
├── ivector/
└── README
```

### Step 3: Test the Python Script

Run the script directly to test:

```bash
cd vosk/VoiceListenerApp
python voice_listener.py
```

You should see:
```
VOSK Voice Listener for Gaming Through Voice Recognition
============================================================

[VOICE] Loading VOSK model from: vosk-model-small-en-us-0.15
[VOICE] Model loaded successfully

[VOICE] Initializing audio system...
[VOICE] Opening microphone stream (16000Hz, mono, 16-bit)
[VOICE] Microphone stream opened successfully

============================================================
LISTENING FOR VOICE COMMANDS...
Speak clearly into your microphone
Press Ctrl+C to stop
============================================================
```

Speak into your microphone and you should see recognized text appear.

### Step 4: Compile to Executable (Optional but Recommended)

To create a standalone executable that doesn't require Python to be installed:

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Compile the script:
```bash
cd vosk/VoiceListenerApp
pyinstaller --name VoiceListener --onedir --console --add-data "vosk-model-small-en-us-0.15;vosk-model-small-en-us-0.15" voice_listener.py
```

3. The executable will be created in `dist/VoiceListener/VoiceListener.exe`

4. Copy the entire `dist/VoiceListener/` contents to `vosk/VoiceListenerApp/`:
```bash
# Copy VoiceListener.exe and _internal folder
copy dist\VoiceListener\* vosk\VoiceListenerApp\
```

**Alternative Simple Compilation** (if model is already in place):
```bash
pyinstaller --name VoiceListener --onefile --console voice_listener.py
```
Then copy `dist/VoiceListener.exe` to `vosk/VoiceListenerApp/`

## How It Works

1. **Model Loading**: Loads the VOSK speech recognition model
2. **Audio Capture**: Opens microphone stream at 16kHz, mono, 16-bit
3. **Recognition**: Continuously processes audio chunks through VOSK
4. **Output**: Writes recognized text to `voice_listener.txt`
5. **C# Integration**: The C# application polls this file every 10ms

## Configuration

Edit the constants at the top of `voice_listener.py` to adjust settings:

```python
MODEL_PATH = "vosk-model-small-en-us-0.15"  # Model directory
OUTPUT_FILE = "voice_listener.txt"           # Output file name
SAMPLE_RATE = 16000                          # Audio sample rate (must match model)
BUFFER_SIZE = 8192                           # Audio buffer size
CHUNK_SIZE = 4096                            # Chunk size for processing
```

## Troubleshooting

### "ERROR: VOSK model folder not found"
- Ensure you've downloaded and extracted the model to the correct location
- Check that the `MODEL_PATH` matches your model directory name

### "ERROR: Could not access microphone"
- Check that a microphone is connected
- Allow microphone access in Windows Settings → Privacy → Microphone
- Close other applications using the microphone (Skype, Discord, etc.)

### "ERROR: Required module not found"
- Install missing packages: `pip install vosk pyaudio`
- For PyAudio issues on Windows, use the pre-compiled wheel

### Poor Recognition Accuracy
- Speak clearly and at a normal pace
- Reduce background noise
- Move closer to the microphone
- Consider using a better quality microphone
- Try a larger VOSK model for better accuracy

### High CPU Usage
- Reduce `BUFFER_SIZE` and `CHUNK_SIZE`
- Use a smaller VOSK model
- Close unnecessary applications

## Model Information

**vosk-model-small-en-us-0.15**
- Language: English (US)
- Size: ~40MB
- Vocabulary: ~100,000 words
- Accuracy: 85-90% for clear speech
- Latency: <500ms
- Memory: ~100MB RAM

## Alternative Models

You can use other VOSK models by downloading them and updating `MODEL_PATH`:

- **vosk-model-en-us-0.22** (1.8GB) - More accurate, slower
- **vosk-model-en-us-0.22-lgraph** (128MB) - Balanced
- **vosk-model-small-en-in-0.4** (40MB) - Indian English
- **vosk-model-small-cn-0.22** (42MB) - Chinese

Download from: https://alphacephei.com/vosk/models

## Technical Details

### Audio Specifications
- **Sample Rate**: 16000 Hz (16kHz) - Required by VOSK model
- **Bit Depth**: 16-bit (paInt16)
- **Channels**: Mono (1 channel)
- **Buffer**: 8192 bytes
- **Chunk Size**: 4096 bytes per read

### Recognition Process
1. Read 4096-byte audio chunk from microphone
2. Feed chunk to VOSK recognizer
3. Recognizer accumulates audio until complete phrase detected
4. When phrase complete (`AcceptWaveform` returns True):
   - Parse JSON result
   - Extract text
   - Convert to lowercase
   - Write to `voice_listener.txt`

### Output Format
The `voice_listener.txt` file contains only the recognized text:
- Example: `go home`
- Example: `add game`
- Example: `logout`

The C# application reads this file every 10ms and processes the commands.

## License

This application uses:
- **VOSK** - Apache 2.0 License
- **PyAudio** - MIT License

## Support

For issues with:
- **VOSK**: https://alphacephei.com/vosk/
- **PyAudio**: https://people.csail.mit.edu/hubert/pyaudio/
- **This Project**: See main project documentation
