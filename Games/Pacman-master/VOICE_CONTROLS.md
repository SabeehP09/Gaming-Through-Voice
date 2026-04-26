# Voice-Controlled Pac-Man Game

## Features

### Voice Commands
- **Movement**: Say "left", "right", "up", or "down" to move Pac-Man
- **Pause/Resume**: Say "stop" or "pause" to pause, "start", "go", or "resume" to continue
- **Restart**: Say "restart game" or "new game" to restart after game over
- **Quit**: Say "quit", "quit game", "close game", or "exit" to close the game

### Improvements
1. **Grammar-Based Recognition**: Only listens for specific command words for better accuracy
2. **Debouncing**: Commands have 0.8 second cooldown to prevent multiple triggers
3. **No Partial Results**: Only processes complete words to avoid false triggers
4. **Visual Feedback**: Shows recognized commands and actions in console
5. **Dual Control**: Keyboard controls still work alongside voice commands
6. **No Music**: Background music disabled for better voice recognition
7. **Reduced Enemy Speed**: Ghosts move at 50% speed for balanced gameplay
8. **Continuous Movement**: Pac-Man keeps moving until you give a new direction

### Keyboard Controls (Still Available)
- Arrow Keys: Move Pac-Man
- Space: Pause/Resume
- Enter: Restart (on game over screen)
- Escape: Quit (on game over screen)

### How to Run
```bash
python pacman_voice.py
```

### Requirements
- pygame-ce
- vosk
- sounddevice
- Working microphone

### Tips for Best Results
- Speak clearly and at normal volume
- Wait for the command to be recognized before speaking again
- Use single words when possible (e.g., "left" instead of "go left")
- Make sure your microphone is working and not muted
