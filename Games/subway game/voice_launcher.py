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

# Audio queue
q = queue.Queue()

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
    "resume",
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
CONFIDENCE_THRESHOLD = 0.60

def audio_callback(indata, frames, time_info, status):
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
    dist = 150
    dur = 0.15
    
    if direction == "up":
        pyautogui.moveTo(cx, cy + dist)
        pyautogui.mouseDown()
        pyautogui.moveTo(cx, cy - dist, duration=dur)
        pyautogui.mouseUp()
    elif direction == "down":
        pyautogui.moveTo(cx, cy - dist)
        pyautogui.mouseDown()
        pyautogui.moveTo(cx, cy + dist, duration=dur)
        pyautogui.mouseUp()
    elif direction == "left":
        pyautogui.moveTo(cx + dist, cy)
        pyautogui.mouseDown()
        pyautogui.moveTo(cx - dist, cy, duration=dur)
        pyautogui.mouseUp()
    elif direction == "right":
        pyautogui.moveTo(cx - dist, cy)
        pyautogui.mouseDown()
        pyautogui.moveTo(cx + dist, cy, duration=dur)
        pyautogui.mouseUp()

def execute_command(cmd):
    global game_running, last_command, last_command_time
    cmd = cmd.lower().strip()
    
    # Prevent duplicate commands within 0.5 seconds
    current_time = time.time()
    if cmd == last_command and (current_time - last_command_time) < 0.5:
        return  # Skip duplicate
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
    
    # Start/Play - click the PLAY button (bottom right area)
    if cmd in START_COMMANDS:
        window = get_game_window()
        if window:
            # PLAY button is at bottom right of the window
            play_x = window.left + window.width - 120
            play_y = window.top + window.height - 60
            pyautogui.click(play_x, play_y)
        print("START_RUN")
        return
    
    # Game controls using swipe gestures
    if cmd == "jump":
        swipe("up")
        print("JUMP")
    
    elif cmd == "roll" or cmd == "slide":
        swipe("down")
        print("SLIDE")
    
    elif cmd == "left":
        swipe("left")
        print("LEFT")
    
    elif cmd == "right":
        swipe("right")
        print("RIGHT")
    
    elif cmd == "pause":
        keyboard.press(Key.esc)
        time.sleep(0.05)
        keyboard.release(Key.esc)
        print("PAUSE")
    
    elif cmd == "resume":
        keyboard.press(Key.enter)
        time.sleep(0.05)
        keyboard.release(Key.enter)
        print("RESUME")
    
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
    print("Menu: 'pause', 'resume'")
    print("=" * 55)
    print("NOTE: This game uses SWIPE gestures (not keyboard)")
    print("=" * 55)
    print("Listening...")
    
    with sd.RawInputStream(samplerate=16000, blocksize=1600, dtype="int16", channels=1, callback=audio_callback):
        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result_json = recognizer.Result()
                passed, text = check_confidence(result_json)
                if passed and text:
                    execute_command(text)
            else:
                partial = json.loads(recognizer.PartialResult())
                partial_text = partial.get("partial", "").strip()
                if partial_text in COMMANDS:
                    execute_command(partial_text)
                    recognizer.Reset()

if __name__ == "__main__":
    import sys
    
    # Check for --auto-launch flag (for app integration)
    if "--auto-launch" in sys.argv:
        print("AUTO-LAUNCH MODE: Starting game automatically...")
        start_game()
    
    listen_for_commands()
