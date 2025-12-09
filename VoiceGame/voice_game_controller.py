"""
Mr Racer Voice Controller - Universal Commands
Commands work based on button positions, not strict screen tracking
"""

import json
import time
import queue
import sys
import subprocess
import os
import threading

def check_deps():
    m = []
    try:
        import vosk
    except:
        m.append("vosk")
    try:
        import sounddevice
    except:
        m.append("sounddevice")
    try:
        import pygetwindow
    except:
        m.append("pygetwindow")
    try:
        import pyautogui
    except:
        m.append("pyautogui")
    try:
        import pynput
    except:
        m.append("pynput")
    if m:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + m)
        sys.exit(0)

check_deps()

import vosk
import sounddevice as sd
import pygetwindow as gw
import pyautogui
from pynput.keyboard import Key, Controller as KeyboardController

keyboard = KeyboardController()

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0  # No delay for fast gameplay

# ============================================================
# ALL BUTTON POSITIONS (x%, y%)
# These positions work across multiple screens
# ============================================================

# System commands
SYSTEM_COMMANDS = ["open mr racer", "play mr racer", "start mr racer", "quit game", "close game"]

# Universal navigation buttons (same position on multiple screens)
NAV_BUTTONS = {
    "back": (0.08, 0.92),      # Bottom left - works on garage, game mode, etc.
    "next": (0.92, 0.92),      # Bottom right - works on garage, game mode, etc.
}

# Main Menu buttons
MAIN_MENU_BUTTONS = {
    "watch": (0.15, 0.92),
    "game mode": (0.50, 0.92),
    "garage": (0.85, 0.92),
    "settings": (0.96, 0.08),
    "daily rewards": (0.93, 0.62),
}

# Game Mode selection buttons (positions from screenshot)
GAME_MODE_BUTTONS = {
    "challenge": (0.15, 0.55),      # First mode - left
    "career race": (0.35, 0.55),    # Second mode
    "career": (0.35, 0.55),         # Alias for career race
    "endless": (0.55, 0.55),        # Third mode - center (selected in screenshot)
    "free ride": (0.75, 0.55),      # Fourth mode
    "chase": (0.95, 0.55),          # Fifth mode - right edge
}

# Mode sub-options (one way / two way for endless)
MODE_OPTIONS = {
    "one way": (0.50, 0.80),        # One way option
    "two way": (0.60, 0.80),        # Two way option
}

# Start button (appears after selecting a mode)
START_BUTTON = (0.50, 0.85)         # Center bottom - START button

# Settings page buttons
SETTINGS_BUTTONS = {
    "close settings": (0.95, 0.07),
    "sound": (0.37, 0.15),
    "maria voice": (0.37, 0.27),
    "auto": (0.58, 0.42),
    "manual": (0.70, 0.42),
    "km": (0.60, 0.56),
    "miles": (0.68, 0.56),
    "help": (0.64, 0.70),
}

# Help dialog
HELP_BUTTONS = {
    "close help": (0.50, 0.85),
}

# Volume commands
VOLUME_COMMANDS = ["bg music increase", "bg music decrease", "sound fx increase", "sound fx decrease"]
BG_MUSIC_DIAL = (0.54, 0.18)
SOUND_FX_DIAL = (0.73, 0.18)

# ============================================================
# GAMEPLAY CONTROLS (during racing) - using pynput keyboard
# ============================================================
# Map voice commands to pynput keys
def get_key(name):
    """Get pynput key from name"""
    key_map = {
        "left": Key.left,
        "right": Key.right,
        "up": Key.up,
        "down": Key.down,
    }
    if name in key_map:
        return key_map[name]
    return name  # Single character like 'h', 'c'

GAMEPLAY_KEYS = {
    "left": "left",         # Left Arrow
    "right": "right",       # Right Arrow
    "horn": "h",            # H key
    "accelerate": "up",     # Up Arrow (gas)
    "gas": "up",            # Up Arrow (alias)
    "brake": "down",        # Down Arrow
    "camera": "c",          # C key
}

# Pause button during gameplay (top left corner)
GAMEPLAY_BUTTONS = {
    "pause": (0.04, 0.08),  # Pause || icon top left
}

# Pause Menu buttons (when game is paused) - adjusted from screenshot
PAUSE_MENU_BUTTONS = {
    "continue": (0.50, 0.42),      # Yellow CONTINUE button
    "settings": (0.50, 0.52),      # SETTINGS button - right below continue
    "restart": (0.50, 0.62),       # RESTART button
    "camera": (0.50, 0.72),        # CAMERA button
    "main menu": (0.50, 0.82),     # MAIN MENU button
}

# Confirmation dialog (Yes/No) - "Do you want quit this mode?"
CONFIRM_BUTTONS = {
    "yes": (0.35, 0.62),           # YES button - left side
    "no": (0.65, 0.62),            # NO button - right side
}

# Mission Failed/Result screen buttons (GARAGE, HOME, REPLAY at bottom)
RESULT_SCREEN_BUTTONS = {
    "garage": (0.20, 0.92),        # GARAGE button - left
    "home": (0.50, 0.92),          # HOME button - center
    "replay": (0.75, 0.88),        # REPLAY button - adjusted left and up
}

# Gameplay commands list
GAMEPLAY_COMMANDS = [
    "pause", "horn", "left", "right", "brake", "straight", 
    "accelerate", "gas", "release", "start race", "go", "race", "stop", 
    "pause game", "continue", "resume", "start", "play",
    "one way", "two way", "restart", "main menu", "yes", "no",
    "home", "replay"
]

# Key tap duration
KEY_TAP_DURATION = 0.1
STEER_HOLD_DURATION = 0.3  # Hold left/right for 0.3 seconds

MIN_CONFIDENCE = 0.60  # Lower threshold for faster response
STEER_COOLDOWN = 0.05  # Very fast cooldown for rapid steering


class VoiceController:
    def __init__(self):
        self.audio_queue = queue.Queue()
        self.game_active = False
        self.app_id = "Playgama.MRRACER-CarRacing_a9mympr8mvnem!App"
        self.window_title = "MR RACER"
        self.last_command = None
        self.last_command_time = 0
        self.cooldown = 0.15  # Very fast for gameplay
        self.held_button = None
        self.accelerating = False  # Track if acceleration is held
        self.in_gameplay = False   # Track if we're in gameplay mode

    def get_all_commands(self):
        """All commands for Vosk grammar"""
        cmds = SYSTEM_COMMANDS.copy()
        cmds += list(NAV_BUTTONS.keys())
        cmds += list(MAIN_MENU_BUTTONS.keys())
        cmds += list(GAME_MODE_BUTTONS.keys())
        cmds += list(MODE_OPTIONS.keys())
        cmds += list(SETTINGS_BUTTONS.keys())
        cmds += list(HELP_BUTTONS.keys())
        cmds += list(GAMEPLAY_BUTTONS.keys())
        cmds += list(PAUSE_MENU_BUTTONS.keys())
        cmds += list(CONFIRM_BUTTONS.keys())
        cmds += list(RESULT_SCREEN_BUTTONS.keys())
        cmds += list(GAMEPLAY_KEYS.keys())
        cmds += GAMEPLAY_COMMANDS
        cmds += VOLUME_COMMANDS
        return list(set(cmds))

    def get_window(self):
        try:
            windows = gw.getWindowsWithTitle(self.window_title)
            if windows:
                return windows[0]
        except:
            pass
        return None

    def activate_window(self, win):
        """Safely activate window"""
        try:
            win.activate()
        except:
            pass

    def click_at(self, pos):
        """Click at position (x%, y%)"""
        win = self.get_window()
        if not win:
            print("  [ERROR] Window not found")
            return False
        x = win.left + int(win.width * pos[0])
        y = win.top + int(win.height * pos[1])
        self.activate_window(win)
        pyautogui.click(x, y)
        print(f"  [CLICK] ({x}, {y})")
        return True

    def press_key(self, key_name, cmd_name):
        """Press a keyboard key for gameplay using pynput"""
        key = get_key(key_name)
        
        # Determine hold duration
        if key_name in ["left", "right"]:
            duration = STEER_HOLD_DURATION
        else:
            duration = KEY_TAP_DURATION
        
        # Press and release the key (non-blocking for steering)
        keyboard.press(key)
        time.sleep(duration)
        keyboard.release(key)
        print(f"  [KEY] {cmd_name} ({duration}s)")
        return True

    def steer(self, direction):
        """Steer left or right - direct key press for reliability"""
        key = Key.left if direction == "left" else Key.right
        # Direct press without threading for more reliable response
        keyboard.press(key)
        time.sleep(STEER_HOLD_DURATION)
        keyboard.release(key)
        print(f"  [STEER] {direction}")

    def start_acceleration(self):
        """Start holding acceleration key"""
        if not self.accelerating:
            keyboard.press(Key.up)
            self.accelerating = True
            self.in_gameplay = True
            print("  [ACCEL] Started - holding Up Arrow")

    def stop_acceleration(self):
        """Stop holding acceleration key"""
        if self.accelerating:
            keyboard.release(Key.up)
            self.accelerating = False
            print("  [ACCEL] Stopped - released Up Arrow")

    def resume_acceleration(self):
        """Resume acceleration after brake"""
        if self.in_gameplay and not self.accelerating:
            keyboard.press(Key.up)
            self.accelerating = True
            print("  [ACCEL] Resumed")

    def drag_dial(self, dial_pos, direction):
        """Drag a dial to increase/decrease volume"""
        win = self.get_window()
        if not win:
            return False
        cx = win.left + int(win.width * dial_pos[0])
        cy = win.top + int(win.height * dial_pos[1])
        drag_amount = 20 if direction == "increase" else -20
        win.activate()
        time.sleep(0.1)
        pyautogui.click(cx, cy)
        time.sleep(0.05)
        pyautogui.drag(drag_amount, 0, duration=0.2)
        print(f"  [DRAG] {direction}")
        return True

    def is_duplicate(self, cmd):
        now = time.time()
        if cmd == self.last_command and (now - self.last_command_time) < self.cooldown:
            return True
        self.last_command = cmd
        self.last_command_time = now
        return False

    def get_confidence(self, result):
        if "result" in result:
            words = result["result"]
            if words:
                return sum(w.get("conf", 0) for w in words) / len(words)
        return 0.0

    def launch_game(self):
        if self.game_active:
            print("  [INFO] Already running")
            return
        print("  [LAUNCH] Opening Mr Racer...")
        subprocess.Popen(f'start shell:AppsFolder\\{self.app_id}', shell=True)
        time.sleep(3)
        for _ in range(5):
            if self.get_window():
                self.game_active = True
                print("  [OK] Launched!")
                return
            time.sleep(1)

    def close_game(self):
        if not self.game_active:
            return
        print("  [CLOSE] Closing game...")
        self.stop_acceleration()  # Release acceleration key
        self.in_gameplay = False
        subprocess.run('taskkill /F /FI "WINDOWTITLE eq MR RACER*"', shell=True, capture_output=True)
        self.game_active = False
        print("  [OK] Closed!")


    def execute_command(self, cmd, conf):
        """Execute command - no strict screen tracking"""
        if conf < MIN_CONFIDENCE:
            return False
        
        if self.is_duplicate(cmd):
            return False
        
        print(f"\n{'='*50}")
        print(f"[VOICE] '{cmd}' (conf: {conf:.2f})")
        
        # System commands
        if cmd in ["open mr racer", "play mr racer", "start mr racer"]:
            self.launch_game()
            return True
        if cmd in ["quit game", "close game"]:
            self.close_game()
            return True
        
        if not self.game_active:
            print("  [INFO] Game not running")
            return False
        
        # Navigation buttons (work on multiple screens)
        if cmd in NAV_BUTTONS:
            self.click_at(NAV_BUTTONS[cmd])
            return True
        
        # Main menu buttons
        if cmd in MAIN_MENU_BUTTONS:
            self.click_at(MAIN_MENU_BUTTONS[cmd])
            return True
        
        # Game mode selection
        if cmd in GAME_MODE_BUTTONS:
            self.click_at(GAME_MODE_BUTTONS[cmd])
            return True
        
        # Mode options (one way / two way)
        if cmd in MODE_OPTIONS:
            self.click_at(MODE_OPTIONS[cmd])
            return True
        
        # Start button (to start a race from mode selection)
        if cmd in ["start", "play"]:
            self.click_at(START_BUTTON)
            return True
        
        # Settings buttons
        if cmd in SETTINGS_BUTTONS:
            self.click_at(SETTINGS_BUTTONS[cmd])
            return True
        
        # Help buttons
        if cmd in HELP_BUTTONS:
            self.click_at(HELP_BUTTONS[cmd])
            return True
        
        # Volume controls
        if cmd == "bg music increase":
            self.drag_dial(BG_MUSIC_DIAL, "increase")
            return True
        if cmd == "bg music decrease":
            self.drag_dial(BG_MUSIC_DIAL, "decrease")
            return True
        if cmd == "sound fx increase":
            self.drag_dial(SOUND_FX_DIAL, "increase")
            return True
        if cmd == "sound fx decrease":
            self.drag_dial(SOUND_FX_DIAL, "decrease")
            return True
        
        # Gameplay buttons (click) - only pause uses screen click
        if cmd in GAMEPLAY_BUTTONS:
            self.click_at(GAMEPLAY_BUTTONS[cmd])
            return True
        
        # START RACE - begin with acceleration held
        if cmd in ["start race", "go", "race"]:
            self.start_acceleration()
            return True
        
        # BRAKE - stop acceleration, press brake, then resume acceleration
        if cmd == "brake":
            self.stop_acceleration()
            keyboard.press(Key.down)
            time.sleep(KEY_TAP_DURATION)
            keyboard.release(Key.down)
            print("  [KEY] brake -> 'down'")
            # Resume acceleration after braking
            time.sleep(0.1)
            self.resume_acceleration()
            return True
        
        # PAUSE GAME - stop acceleration and click pause button
        if cmd in ["stop", "pause game", "pause"]:
            self.stop_acceleration()
            self.in_gameplay = False
            self.click_at(GAMEPLAY_BUTTONS["pause"])
            return True
        
        # PAUSE MENU BUTTONS
        if cmd == "continue" or cmd == "resume":
            self.click_at(PAUSE_MENU_BUTTONS["continue"])
            time.sleep(0.3)
            self.start_acceleration()
            return True
        
        if cmd == "restart":
            self.click_at(PAUSE_MENU_BUTTONS["restart"])
            time.sleep(0.5)
            self.start_acceleration()
            return True
        
        # Settings from pause menu
        if cmd == "settings" and not self.in_gameplay:
            self.click_at(PAUSE_MENU_BUTTONS["settings"])
            return True
        
        if cmd == "main menu":
            self.in_gameplay = False
            self.click_at(PAUSE_MENU_BUTTONS["main menu"])
            return True
        
        # Camera in pause menu (different from gameplay camera key)
        if cmd == "camera" and not self.in_gameplay:
            self.click_at(PAUSE_MENU_BUTTONS["camera"])
            return True
        
        # Confirmation dialog (Yes/No)
        if cmd == "yes":
            self.click_at(CONFIRM_BUTTONS["yes"])
            return True
        
        if cmd == "no":
            self.click_at(CONFIRM_BUTTONS["no"])
            return True
        
        # Result/Mission Failed screen buttons
        if cmd == "home":
            self.in_gameplay = False
            self.click_at(RESULT_SCREEN_BUTTONS["home"])
            return True
        
        if cmd == "replay":
            self.click_at(RESULT_SCREEN_BUTTONS["replay"])
            time.sleep(0.5)
            self.start_acceleration()
            return True
        
        # Garage from result screen (different position than main menu)
        if cmd == "garage" and not self.in_gameplay:
            self.click_at(RESULT_SCREEN_BUTTONS["garage"])
            return True
        
        # Gameplay keyboard controls - other actions (left, right, horn, camera)
        if cmd in GAMEPLAY_KEYS and cmd not in ["brake", "accelerate", "gas"]:
            self.press_key(GAMEPLAY_KEYS[cmd], cmd)
            return True
        
        # Accelerate/gas - start acceleration if not already
        if cmd in ["accelerate", "gas"]:
            self.start_acceleration()
            return True
        
        # Release steering / straight - no key needed, just stop pressing
        if cmd in ["straight", "release"]:
            print("  [RELEASE] Steering centered (release keys)")
            return True
        
        return False

    def audio_callback(self, indata, frames, time_info, status):
        self.audio_queue.put(bytes(indata))

    def download_model(self):
        p = "vosk-model-small-en-us-0.15"
        if os.path.exists(p):
            return p
        print("\nDownloading model...")
        import urllib.request, zipfile
        urllib.request.urlretrieve(
            "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip", "m.zip")
        with zipfile.ZipFile("m.zip", 'r') as z:
            z.extractall(".")
        os.remove("m.zip")
        return p

    def run(self):
        print("=" * 55)
        print("MR RACER VOICE CONTROLLER")
        print("=" * 55)
        print(f"\nConfidence: {MIN_CONFIDENCE}")
        print("\nSYSTEM:")
        print("  open/play/start mr racer, quit/close game")
        print("\nNAVIGATION (works on multiple screens):")
        print("  back, next")
        print("\nMAIN MENU:")
        print("  watch, game mode, garage, settings, daily rewards")
        print("\nGAME MODE SELECTION:")
        print("  challenge, career race, endless, free ride, chase")
        print("  one way, two way (for endless mode)")
        print("  start, play (to start the race)")
        print("\nSETTINGS:")
        print("  close settings, sound, maria voice")
        print("  auto, manual, km, miles, help")
        print("  bg music increase/decrease")
        print("  sound fx increase/decrease")
        print("\nHELP:")
        print("  close help")
        print("\nGAMEPLAY (keyboard controls):")
        print("  'go' / 'race' - START with auto-acceleration")
        print("  'pause' - PAUSE game (opens pause menu)")
        print("  left, right - steering")
        print("  brake - brake (auto-resumes acceleration)")
        print("  horn (H), camera (C)")
        print("\nPAUSE MENU:")
        print("  continue/resume - Resume game")
        print("  settings - Open settings")
        print("  restart - Restart race")
        print("  camera - Change camera view")
        print("  main menu - Return to main menu")
        print("\nCONFIRMATION DIALOG:")
        print("  yes - Confirm action")
        print("  no - Cancel action")
        print("\nRESULT/FAILED SCREEN:")
        print("  garage - Go to garage")
        print("  home - Go to main menu")
        print("  replay - Replay the race")
        print("\n" + "=" * 55)
        print("Say 'open mr racer' to start\n")
        
        vosk.SetLogLevel(-1)
        model = vosk.Model(self.download_model())
        recognizer = vosk.KaldiRecognizer(model, 16000, json.dumps(self.get_all_commands()))
        recognizer.SetWords(True)
        
        try:
            with sd.RawInputStream(samplerate=16000, blocksize=1600,
                                   dtype='int16', channels=1,
                                   callback=self.audio_callback):
                last_steer_time = 0
                last_partial = ""
                
                while True:
                    data = self.audio_queue.get()
                    now = time.time()
                    
                    # Process audio
                    if recognizer.AcceptWaveform(data):
                        result = json.loads(recognizer.Result())
                        text = result.get("text", "").strip()
                        if text:
                            conf = self.get_confidence(result)
                            # Handle steering from final results too
                            if text in ["left", "right"] and self.in_gameplay:
                                if (now - last_steer_time) > STEER_COOLDOWN:
                                    print(f"[STEER] {text}")
                                    self.steer(text)
                                    last_steer_time = now
                            elif text == "brake" and self.in_gameplay:
                                print(f"[BRAKE]")
                                self.stop_acceleration()
                                keyboard.press(Key.down)
                                time.sleep(KEY_TAP_DURATION)
                                keyboard.release(Key.down)
                                self.resume_acceleration()
                            else:
                                self.execute_command(text, conf)
                        last_partial = ""
                    else:
                        # Check partial results for faster steering
                        partial = json.loads(recognizer.PartialResult())
                        partial_text = partial.get("partial", "").strip()
                        
                        # Only act on new partial results
                        if partial_text and partial_text != last_partial:
                            if partial_text in ["left", "right"] and self.in_gameplay:
                                if (now - last_steer_time) > STEER_COOLDOWN:
                                    print(f"[FAST-STEER] {partial_text}")
                                    self.steer(partial_text)
                                    last_steer_time = now
                            elif partial_text == "brake" and self.in_gameplay:
                                print(f"[FAST-BRAKE]")
                                self.stop_acceleration()
                                keyboard.press(Key.down)
                                time.sleep(KEY_TAP_DURATION)
                                keyboard.release(Key.down)
                                self.resume_acceleration()
                            last_partial = partial_text
                            
        except KeyboardInterrupt:
            self.stop_acceleration()
            print("\n\nStopped.")


if __name__ == "__main__":
    time.sleep(2)
    VoiceController().run()
