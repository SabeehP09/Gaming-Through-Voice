# Voice Game Controller - State-Based System

## Features
- **State-based commands**: Only allows commands valid for current state
- **Multiple game support**: Mr Racer, Subway Surfers, Temple Run
- **Prevents repeated launches**: Won't open same game twice
- **Context-aware**: Commands change based on game state

## Installation
```bash
pip install vosk sounddevice pynput pygetwindow
```

## Run
```bash
python voice_game_controller.py
```

## States & Commands

### LAUNCHER State (no game running)
- "mr racer" → Opens Mr Racer
- "subway surfer" → Opens Subway Surfers  
- "temple run" → Opens Temple Run
- "stop" → Exit voice controller

### MAIN MENU State
- play, start, career, endless
- garage, settings, shop
- quit, close

### PLAYING State
- left, right, straight
- nitro, boost, brake
- pause

### PAUSED State
- resume, restart
- settings, quit

### SETTINGS State
- up, down, select, back
- sound, music, on, off

### GARAGE State
- next, previous, buy, upgrade
- select, back, confirm, cancel

## How It Works
1. Start in LAUNCHER state
2. Say game name to launch
3. State changes to MAIN_MENU
4. Commands filtered by current state
5. Invalid commands are blocked
6. Say "close" to close game and return to LAUNCHER
