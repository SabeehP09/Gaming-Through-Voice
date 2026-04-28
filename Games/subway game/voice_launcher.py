import subprocess
import os
import queue
import json
import time
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from pynput.keyboard import Key, Controller as KeyboardController
import pyautogui
import pygetwindow as gw

# Disable pyautogui delays
pyautogui.PAUSE = 0

# Initialize keyboard controller
keyboard = KeyboardController()

# Game state
game_running = False
game_process = None
last_command = ""
last_command_time = 0
last_swipe_time = 0  # Cooldown to prevent ghost swipes after slide/roll

# Swipe commands that need cooldown protection
SWIPE_COMMANDS = {"jump", "left", "right", "roll", "slide"}
SWIPE_COOLDOWN = 0.8  # seconds

# Audio queue
q = queue.Queue(maxsize=2)

# Command list for grammar-based recognition
COMMANDS = [
    "open subway surfer",
    "play subway surfer",
    "play",
    "start",
    "go",
    "run",
    "jump",
    "roll",
    "slide",
    "left",
    "right",
    "pause",
    "stop",
    "resume",
    "home",
    "settings",
    "quit game",
    "exit game",
    "close game"
]

# Launcher commands
LAUNCHER_COMMANDS = {"open subway surfer", "play subway surfer"}

# Start running commands
START_COMMANDS = {"play", "start", "go", "run"}

# Close game commands
CLOSE_COMMANDS = {"quit game", "exit game", "close game"}

# Confidence threshold
CONFIDENCE_THRESHOLD = 0.65

# Single-word instant commands that should fire from partial results
INSTANT_COMMANDS = {"jump", "left", "right", "roll", "slide", "go", "run", "play", "start", "home", "resume", "pause", "stop"}

def audio_callback(indata, frames, time_info, status):
    if q.full():
        try:
            q.get_nowait()
        except:
            pass
    q.put(bytes(indata))


def is_game_process_running():
    global game_process, game_running
    if game_process is not None:
        poll = game_process.poll()
        if poll is None:
            return True
        else:
            game_running = False
            game_process = None
    return False

def get_game_window():
    for title in ["Subway Surf", "Subway Surfers"]:
        windows = gw.getWindowsWithTitle(title)
        for w in windows:
            if "configuration" in w.title.lower():
                continue
            if title.lower() in w.title.lower():
                return w
    return None

def get_config_window():
    windows = gw.getWindowsWithTitle("Configuration")
    for w in windows:
        if "subway" in w.title.lower() and "configuration" in w.title.lower():
            return w
    return None

def start_game():
    global game_running, game_process
    game_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Subway_Surfers.exe")
    game_process = subprocess.Popen(game_path)
    game_running = True
    print("START_GAME")
    
    time.sleep(1)
    for _ in range(10):
        config_win = get_config_window()
        if config_win:
            play_x = config_win.left + config_win.width - 150
            play_y = config_win.top + config_win.height - 30
            pyautogui.click(play_x, play_y)
            print("CLICKED_PLAY")
            break
        time.sleep(0.5)
    
    time.sleep(2)
    activate_game_window()
    
    # Show keyboard not supported message
    print("")
    print("=" * 55)
    print("NOTE: Keyboard controls are not supported by this")
    print("version of the game. Using SWIPE gestures instead.")
    print("=" * 55)
    print("")

def activate_game_window():
    window = get_game_window()
    if window:
        try:
            window.activate()
        except:
            pass

def swipe(direction):
    """Perform swipe gesture on game window"""
    window = get_game_window()
    if not window:
        return
    
    cx = window.left + window.width // 2
    cy = window.top + window.height // 2
    
    # Swipe distance and duration
    dist = 45
    dur = 0
    
    if direction == "up":
        pyautogui.moveTo(cx, cy + dist)
        pyautogui.mouseDown()
        pyautogui.moveTo(cx, cy - dist, duration=0.3)
        pyautogui.mouseUp()
    elif direction == "down":
        pyautogui.moveTo(cx, cy - dist)
        pyautogui.mouseDown()
        pyautogui.moveTo(cx, cy + dist, duration=0.3)
        pyautogui.mouseUp()
    elif direction == "left":
        pyautogui.moveTo(cx + dist, cy)
        pyautogui.mouseDown()
        pyautogui.moveTo(cx - dist, cy, duration=0.3)
        pyautogui.mouseUp()
    elif direction == "right":
        pyautogui.moveTo(cx - dist, cy)
        pyautogui.mouseDown()
        pyautogui.moveTo(cx + dist, cy, duration=0.3)
        pyautogui.mouseUp()

def execute_command(cmd):
    global game_running, last_command, last_command_time, last_swipe_time
    cmd = cmd.lower().strip()

    current_time = time.time()

    # Block any swipe command if we're still in swipe cooldown
    if cmd in SWIPE_COMMANDS and (current_time - last_swipe_time) < SWIPE_COOLDOWN:
        return

    # Prevent duplicate commands within 1 second
    if cmd == last_command and (current_time - last_command_time) < 1.0:
        return
    last_command = cmd
    last_command_time = current_time
    
    # Launcher commands
    if cmd in LAUNCHER_COMMANDS:
        if is_game_process_running():
            print("GAME_ALREADY_RUNNING")
        else:
            start_game()
        return
    
    # Close game commands
    if cmd in CLOSE_COMMANDS:
        if is_game_process_running() and game_process:
            game_process.terminate()
            game_running = False
            print("GAME_CLOSED")
        else:
            print("NO_GAME_RUNNING")
        return
    
    # In-game commands
    if not is_game_process_running():
        print("NO_COMMAND")
        return
    
    activate_game_window()
    
    # Start/Play - click the PLAY button (slightly right of center, bottom area)
    if cmd in START_COMMANDS:
        window = get_game_window()
        if window:
            # PLAY/Restart button is slightly right of center at the bottom
            # Offset +60 from center to avoid Shop button on the far right
            play_x = window.left + window.width // 2 + 170
            play_y = window.top + window.height - 60
            pyautogui.click(play_x, play_y)
        print("START_RUN")
        return
    
    # Game controls using swipe gestures
    if cmd == "jump":
        last_swipe_time = time.time()
        swipe("up")
        print("JUMP")

    elif cmd == "roll" or cmd == "slide":
        last_swipe_time = time.time()
        swipe("down")
        print("SLIDE")

    elif cmd == "left":
        last_swipe_time = time.time()
        swipe("left")
        print("LEFT")

    elif cmd == "right":
        last_swipe_time = time.time()
        swipe("right")
        print("RIGHT")
    
    elif cmd == "pause" or cmd == "stop":
        # Click the pause button in top-left corner
        window = get_game_window()
        if window:
            # Pause button is in top-left corner (adjusted position)
            pause_x = window.left + 30
            pause_y = window.top + 40
            pyautogui.click(pause_x, pause_y)
        print("PAUSE")
    
    elif cmd == "resume":
        # Click the resume button (green button at bottom center-right)
        window = get_game_window()
        if window:
            # Resume button is at bottom center-right of the window
            resume_x = window.left + window.width // 2 + 100
            resume_y = window.top + window.height - 60
            pyautogui.click(resume_x, resume_y)
        print("RESUME")
    
    elif cmd == "home":
        # Click the home button (house icon - leftmost of the 3 bottom buttons)
        window = get_game_window()
        if window:
            # Home is the leftmost button, well to the left of center
            home_x = window.left + window.width // 2 - 190
            home_y = window.top + window.height - 50
            pyautogui.click(home_x, home_y)
        print("HOME")
    
    elif cmd == "settings":
        # Click the settings button (gear icon at bottom center)
        window = get_game_window()
        if window:
            # Settings button is at bottom center of the window
            settings_x = window.left + window.width // 2
            settings_y = window.top + window.height - 60
            pyautogui.click(settings_x, settings_y)
        print("SETTINGS")
    
    else:
        print("NO_COMMAND")

def check_confidence(result_json):
    try:
        result = json.loads(result_json)
        if "result" in result and len(result["result"]) > 0:
            confidences = [word.get("conf", 0) for word in result["result"]]
            avg_conf = sum(confidences) / len(confidences)
            return avg_conf >= CONFIDENCE_THRESHOLD, result.get("text", "")
        elif "text" in result:
            return True, result.get("text", "")
    except:
        pass
    return False, ""

def listen_for_commands():
    global game_running
    
    model_path = "vosk-model-small-en-us-0.15"
    if not os.path.exists(model_path):
        import urllib.request
        import zipfile
        url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
        print("Downloading model...")
        urllib.request.urlretrieve(url, "model.zip")
        with zipfile.ZipFile("model.zip", 'r') as zip_ref:
            zip_ref.extractall(".")
        os.remove("model.zip")
        print("Model downloaded!")
    
    model = Model(model_path)
    recognizer = KaldiRecognizer(model, 16000, json.dumps(COMMANDS))
    recognizer.SetWords(True)
    
    print("=" * 55)
    print("SUBWAY SURFERS VOICE CONTROLLER")
    print("=" * 55)
    print("Launcher: 'open subway surfer', 'play subway surfer'")
    print("Close: 'quit game', 'exit game', 'close game'")
    print("Start: 'play', 'start', 'run', 'go'")
    print("Controls: 'jump', 'slide', 'left', 'right'")
    print("Pause Menu: 'pause', 'stop', 'resume', 'home', 'settings'")
    print("=" * 55)
    print("NOTE: This game uses SWIPE gestures (not keyboard)")
    print("=" * 55)
    print("Listening...")
    
    with sd.RawInputStream(samplerate=16000, blocksize=256, dtype="int16", channels=1, callback=audio_callback):
        partial_fired = False
        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result_json = recognizer.Result()
                # Skip final result if partial already handled this command
                if not partial_fired:
                    passed, text = check_confidence(result_json)
                    if passed and text and text.strip():
                        execute_command(text)
                partial_fired = False  # Reset flag after final result
            else:
                # Check partial result for instant single-word commands
                partial_json = recognizer.PartialResult()
                try:
                    partial = json.loads(partial_json).get("partial", "").strip().lower()
                    if partial and partial in INSTANT_COMMANDS:
                        execute_command(partial)
                        partial_fired = True  # Mark so final result is skipped
                        recognizer.Reset()
                except:
                    pass

if __name__ == "__main__":
    import sys

    # Check for --auto-launch flag (for app integration)
    if "--auto-launch" in sys.argv:
        print("AUTO-LAUNCH MODE: Starting game automatically...")
        start_game()

    try:
        listen_for_commands()
    except KeyboardInterrupt:
        print("\nStopped.")
