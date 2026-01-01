"""
Voice Command Recognition System
Offline speech-to-text and command recognition for gaming
Uses PocketSphinx for offline recognition
"""

import speech_recognition as sr
import json
import os
from difflib import SequenceMatcher
import threading
import queue


class VoiceCommandRecognizer:
    """
    Recognizes voice commands for gaming and app navigation
    Works completely offline using PocketSphinx
    """
    
    def __init__(self, commands_file="commands.json"):
        """
        Initialize the voice command recognizer
        
        Args:
            commands_file: JSON file containing command definitions
        """
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Load commands
        self.commands_file = commands_file
        self.commands = self.load_commands()
        
        # Recognition settings
        self.recognizer.energy_threshold = 4000  # Adjust based on environment
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8  # Seconds of silence to consider end of phrase
        
        # Continuous listening
        self.is_listening = False
        self.listen_thread = None
        self.command_queue = queue.Queue()
        
    def load_commands(self):
        """
        Load command definitions from JSON file
        
        Returns:
            Dictionary of commands
        """
        if os.path.exists(self.commands_file):
            with open(self.commands_file, 'r') as f:
                return json.load(f)
        else:
            # Default commands
            default_commands = {
                "navigation": {
                    "go home": "HOME",
                    "open dashboard": "DASHBOARD",
                    "show profile": "PROFILE",
                    "open settings": "SETTINGS",
                    "show games": "GAMES",
                    "voice commands": "VOICE_COMMANDS"
                },
                "gaming": {
                    "jump": "JUMP",
                    "move forward": "FORWARD",
                    "move backward": "BACKWARD",
                    "move left": "LEFT",
                    "move right": "RIGHT",
                    "attack": "ATTACK",
                    "defend": "DEFEND",
                    "pause game": "PAUSE",
                    "resume game": "RESUME",
                    "quit game": "QUIT"
                },
                "system": {
                    "start listening": "START_LISTEN",
                    "stop listening": "STOP_LISTEN",
                    "help": "HELP",
                    "repeat": "REPEAT",
                    "cancel": "CANCEL",
                    "confirm": "CONFIRM",
                    "yes": "YES",
                    "no": "NO"
                }
            }
            
            # Save default commands
            with open(self.commands_file, 'w') as f:
                json.dump(default_commands, f, indent=4)
            
            return default_commands
    
    def save_commands(self):
        """Save current commands to file"""
        with open(self.commands_file, 'w') as f:
            json.dump(self.commands, f, indent=4)
    
    def add_command(self, category, phrase, action):
        """
        Add a new voice command
        
        Args:
            category: Command category (navigation, gaming, system)
            phrase: Voice phrase to recognize
            action: Action identifier
        """
        if category not in self.commands:
            self.commands[category] = {}
        
        self.commands[category][phrase.lower()] = action
        self.save_commands()
        print(f"✓ Added command: '{phrase}' -> {action}")
    
    def remove_command(self, category, phrase):
        """Remove a voice command"""
        if category in self.commands and phrase.lower() in self.commands[category]:
            del self.commands[category][phrase.lower()]
            self.save_commands()
            print(f"✓ Removed command: '{phrase}'")
            return True
        return False
    
    def recognize_speech(self, timeout=5, phrase_time_limit=10):
        """
        Recognize speech from microphone
        
        Args:
            timeout: Seconds to wait for speech to start
            phrase_time_limit: Maximum seconds for phrase
            
        Returns:
            Recognized text or None
        """
        try:
            with self.microphone as source:
                # Adjust for ambient noise
                print("🎤 Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Listen for audio
                audio = self.recognizer.listen(source, 
                                              timeout=timeout,
                                              phrase_time_limit=phrase_time_limit)
                
                # Recognize using PocketSphinx (offline)
                try:
                    text = self.recognizer.recognize_sphinx(audio)
                    print(f"📝 Recognized: {text}")
                    return text.lower()
                except sr.UnknownValueError:
                    print("❓ Could not understand audio")
                    return None
                except sr.RequestError as e:
                    print(f"❌ Recognition error: {e}")
                    return None
                    
        except sr.WaitTimeoutError:
            print("⏱️ Listening timed out")
            return None
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None
    
    def match_command(self, text, threshold=0.7):
        """
        Match recognized text to a command
        
        Args:
            text: Recognized text
            threshold: Similarity threshold (0-1)
            
        Returns:
            (category, action, confidence) or (None, None, 0)
        """
        if not text:
            return None, None, 0
        
        text = text.lower().strip()
        best_match = None
        best_score = 0
        best_category = None
        
        # Check all commands
        for category, commands in self.commands.items():
            for phrase, action in commands.items():
                # Calculate similarity
                similarity = SequenceMatcher(None, text, phrase.lower()).ratio()
                
                # Check for exact substring match
                if phrase.lower() in text or text in phrase.lower():
                    similarity = max(similarity, 0.9)
                
                if similarity > best_score:
                    best_score = similarity
                    best_match = action
                    best_category = category
        
        if best_score >= threshold:
            confidence = int(best_score * 100)
            print(f"✓ Matched: {best_match} ({confidence}% confidence)")
            return best_category, best_match, confidence
        else:
            print(f"✗ No command matched (best: {int(best_score * 100)}%)")
            return None, None, 0
    
    def recognize_command(self, timeout=5, phrase_time_limit=10, threshold=0.7):
        """
        Listen and recognize a voice command
        
        Returns:
            (category, action, confidence) or (None, None, 0)
        """
        text = self.recognize_speech(timeout, phrase_time_limit)
        return self.match_command(text, threshold)
    
    def start_continuous_listening(self, callback=None):
        """
        Start continuous voice command recognition in background
        
        Args:
            callback: Function to call with (category, action, confidence)
        """
        if self.is_listening:
            print("⚠️ Already listening")
            return
        
        self.is_listening = True
        
        def listen_loop():
            print("🎤 Started continuous listening")
            while self.is_listening:
                try:
                    category, action, confidence = self.recognize_command(
                        timeout=2, 
                        phrase_time_limit=5,
                        threshold=0.7
                    )
                    
                    if action:
                        if callback:
                            callback(category, action, confidence)
                        else:
                            self.command_queue.put((category, action, confidence))
                            
                except Exception as e:
                    print(f"❌ Listening error: {str(e)}")
            
            print("🛑 Stopped continuous listening")
        
        self.listen_thread = threading.Thread(target=listen_loop, daemon=True)
        self.listen_thread.start()
    
    def stop_continuous_listening(self):
        """Stop continuous listening"""
        self.is_listening = False
        if self.listen_thread:
            self.listen_thread.join(timeout=2)
    
    def get_next_command(self, timeout=None):
        """
        Get next command from queue (for continuous listening)
        
        Args:
            timeout: Seconds to wait for command
            
        Returns:
            (category, action, confidence) or None
        """
        try:
            return self.command_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def list_commands(self, category=None):
        """
        List all available commands
        
        Args:
            category: Specific category or None for all
        """
        if category:
            if category in self.commands:
                print(f"\n📋 {category.upper()} Commands:")
                for phrase, action in self.commands[category].items():
                    print(f"  '{phrase}' → {action}")
            else:
                print(f"❌ Category '{category}' not found")
        else:
            print("\n📋 All Available Commands:")
            for cat, commands in self.commands.items():
                print(f"\n{cat.upper()}:")
                for phrase, action in commands.items():
                    print(f"  '{phrase}' → {action}")


# Example usage
if __name__ == "__main__":
    # Initialize recognizer
    recognizer = VoiceCommandRecognizer()
    
    # List available commands
    recognizer.list_commands()
    
    # Example: Single command recognition
    print("\n🎤 Say a command...")
    category, action, confidence = recognizer.recognize_command()
    
    if action:
        print(f"✓ Command: {action} (Category: {category}, Confidence: {confidence}%)")
    
    # Example: Continuous listening
    # def on_command(category, action, confidence):
    #     print(f"Command received: {action}")
    #
    # recognizer.start_continuous_listening(callback=on_command)
    # # ... do other work ...
    # recognizer.stop_continuous_listening()
