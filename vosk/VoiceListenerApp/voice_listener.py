#!/usr/bin/env python3
"""
VOSK Voice Listener for Gaming Through Voice Recognition System
Continuously listens to microphone and writes recognized text to file
"""

import sys
import os
import json
import signal

# Check for required modules
try:
    from vosk import Model, KaldiRecognizer
    import pyaudio
except ImportError as e:
    print(f"ERROR: Required module not found: {e}")
    print("Please install required packages:")
    print("  pip install vosk pyaudio")
    sys.exit(1)

# Configuration - OPTIMIZED FOR LOW LATENCY
MODEL_PATH = "vosk-model-small-en-in-0.4"  # Changed to English India
OUTPUT_FILE = "voice_listener.txt"
SAMPLE_RATE = 16000
BUFFER_SIZE = 4096  # Reduced from 8192 for faster response
CHUNK_SIZE = 2048   # Reduced from 4096 for lower latency

# Global variables for cleanup
audio = None
stream = None
running = True


def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    global running
    print("\n[VOICE] Shutdown signal received, cleaning up...")
    running = False


def main():
    """Main voice listener loop"""
    global audio, stream
    
    print("=" * 60)
    print("VOSK Voice Listener for Gaming Through Voice Recognition")
    print("=" * 60)
    print()
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Check if model exists
    if not os.path.exists(MODEL_PATH):
        print(f"ERROR: VOSK model folder not found: {MODEL_PATH}")
        print()
        print("Please download the model:")
        print("  1. Visit: https://alphacephei.com/vosk/models")
        print("  2. Download: vosk-model-small-en-in-0.4 (31MB)")
        print("  3. Extract to this directory")
        print()
        sys.exit(1)
    
    try:
        # Load VOSK model
        print(f"[VOICE] Loading VOSK model from: {MODEL_PATH}")
        model = Model(MODEL_PATH)
        recognizer = KaldiRecognizer(model, SAMPLE_RATE)
        
        # Set grammar for better recognition of game commands
        # This helps distinguish "two" from "to" or "too"
        grammar = json.dumps([
            "login", "sign in", "signup", "register", "sign up",
            "dashboard", "go home", "open dashboard",
            "settings", "open settings", "go to settings",
            "profile", "go to profile", "open profile",
            "voice commands", "help", "show commands",
            "add game", "new game",
            "logout", "sign out", "log out",
            "close", "close window", "minimize", "maximize",
            "exit", "quit", "close app", "close application",
            "open mr racer", "play mr racer", "launch mr racer", "start mr racer",
            "open subway surfers", "play subway surfers", "launch subway surfers", "start subway surfers",
            "open subway", "play subway",
            "open game one", "play game one", "start game one", "launch game one",
            "open game 1", "play game 1", "start game 1", "launch game 1",
            "open game two", "play game two", "start game two", "launch game two",
            "open game 2", "play game 2", "start game 2", "launch game 2",
            "open game three", "play game three", "start game three", "launch game three",
            "open game 3", "play game 3", "start game 3", "launch game 3",
            "open game four", "play game four", "start game four", "launch game four",
            "open game 4", "play game 4", "start game 4", "launch game 4",
            "open game five", "play game five", "start game five", "launch game five",
            "open game 5", "play game 5", "start game 5", "launch game 5",
            "manual login", "manual",
            "face login", "face",
            "voice login", "record voice", "record",
            "forgot password", "reset password",
            "capture face", "take photo",
            "create account",
            "[unk]"
        ])
        recognizer.SetGrammar(grammar)
        
        print("[VOICE] Model loaded successfully with game command grammar")
        print()
        
    except Exception as e:
        print(f"ERROR: Failed to load VOSK model: {e}")
        sys.exit(1)
    
    try:
        # Initialize PyAudio
        print("[VOICE] Initializing audio system...")
        audio = pyaudio.PyAudio()
        
        # Open microphone stream
        print(f"[VOICE] Opening microphone stream ({SAMPLE_RATE}Hz, mono, 16-bit)")
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=BUFFER_SIZE
        )
        print("[VOICE] Microphone stream opened successfully")
        print()
        
    except Exception as e:
        print(f"ERROR: Could not access microphone: {e}")
        print()
        print("Troubleshooting:")
        print("  - Check that a microphone is connected")
        print("  - Check microphone permissions in Windows Settings")
        print("  - Close other applications using the microphone")
        print()
        sys.exit(1)
    
    # Create empty output file
    try:
        with open(OUTPUT_FILE, "w") as f:
            f.write("")
        print(f"[VOICE] Output file created: {OUTPUT_FILE}")
    except Exception as e:
        print(f"ERROR: Could not create output file: {e}")
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("LISTENING FOR VOICE COMMANDS...")
    print("Speak clearly into your microphone")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    # Main recognition loop - OPTIMIZED FOR LOW LATENCY
    last_written = ""  # Track last written command to avoid duplicate writes
    
    try:
        while running:
            # Read audio chunk from microphone (smaller chunks = faster response)
            data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
            
            # Feed audio to recognizer
            if recognizer.AcceptWaveform(data):
                # Complete phrase detected
                result = json.loads(recognizer.Result())
                text = result.get("text", "").lower().strip()
                
                if text and text != last_written:
                    # Write recognized text to file immediately
                    try:
                        # Use unbuffered write for instant file update
                        with open(OUTPUT_FILE, "w", buffering=1) as f:
                            f.write(text)
                            f.flush()  # Force immediate write to disk
                        print(f"[VOICE] Recognized: '{text}'")
                        last_written = text
                    except Exception as e:
                        print(f"[VOICE] ERROR writing to file: {e}")
            
            # Process partial results for faster command detection
            else:
                partial = json.loads(recognizer.PartialResult())
                partial_text = partial.get("partial", "").lower().strip()
                
                # If partial result looks like a complete command, write it immediately
                # This provides faster response for short commands
                if partial_text and len(partial_text.split()) >= 1:
                    # Check if it's a known command pattern (optional optimization)
                    if partial_text != last_written:
                        # Show partial for debugging
                        print(f"[VOICE] Partial: {partial_text}", end="\r")
    
    except KeyboardInterrupt:
        print("\n[VOICE] Keyboard interrupt received")
    except Exception as e:
        print(f"\n[VOICE] ERROR in recognition loop: {e}")
    finally:
        # Cleanup
        print("\n[VOICE] Cleaning up...")
        
        if stream is not None:
            try:
                stream.stop_stream()
                stream.close()
                print("[VOICE] Audio stream closed")
            except:
                pass
        
        if audio is not None:
            try:
                audio.terminate()
                print("[VOICE] PyAudio terminated")
            except:
                pass
        
        print("[VOICE] Voice listener stopped")
        print()


if __name__ == "__main__":
    main()
