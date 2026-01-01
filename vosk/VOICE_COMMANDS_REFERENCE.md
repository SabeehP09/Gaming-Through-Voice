# Voice Commands Reference Card

## 🎮 Gaming Through Voice Recognition System

### Global Commands (Work Anywhere)

#### Navigation
| Command | Aliases | Action |
|---------|---------|--------|
| **go home** | open dashboard, dashboard | Navigate to home/dashboard |
| **login** | sign in | Navigate to login window |
| **signup** | register, sign up | Navigate to signup window |
| **settings** | open settings, go to settings | Navigate to settings |
| **profile** | go to profile, open profile | Navigate to profile |
| **help** | voice commands, show commands | Show voice commands help |

#### Actions
| Command | Aliases | Action |
|---------|---------|--------|
| **add game** | new game | Open add game dialog |
| **logout** | sign out, log out | Log out current user |

#### Window Management
| Command | Aliases | Action |
|---------|---------|--------|
| **close** | close window | Close current window |
| **minimize** | - | Minimize application |
| **maximize** | - | Maximize/restore application |
| **exit** | quit, close app, close application | Exit application |

---

### Window-Specific Commands

#### 🔐 Login Window
| Command | Aliases | Action |
|---------|---------|--------|
| **manual login** | manual | Show manual login form |
| **face login** | face | Start face recognition login |
| **voice login** | record, voice record | Start voice login |
| **forgot password** | reset password | Open password reset |

#### 📝 Signup Window
| Command | Aliases | Action |
|---------|---------|--------|
| **signup** | register, create account | Complete registration |
| **capture face** | face, take photo | Capture face data |
| **record voice** | voice | Record voice data |

#### 🏠 Home Window
| Command | Aliases | Action |
|---------|---------|--------|
| **dashboard** | home | Navigate to dashboard |
| **profile** | my profile | Navigate to profile |
| **voice commands** | commands | Show voice commands |
| **settings** | - | Navigate to settings |

#### 🎤 Voice Recording Window
| Command | Aliases | Action |
|---------|---------|--------|
| **start recording** | start, record | Start recording |
| **stop recording** | stop | Stop recording |
| **done** | ok, finish | Finish and close |

---

## Tips for Best Recognition

### 1. Speak Clearly
- Use normal speaking voice
- Don't shout or whisper
- Speak at normal pace

### 2. Reduce Background Noise
- Close windows
- Turn off TV/music
- Use in quiet environment

### 3. Use Natural Phrases
- Say "go home" not "gohome"
- Pause briefly between words
- Use complete phrases

### 4. Try Aliases
If one phrase doesn't work, try an alias:
- "go home" → "dashboard"
- "logout" → "sign out"
- "close" → "close window"

### 5. Check Microphone
- Ensure microphone is selected in Windows
- Check microphone volume
- Test in Windows Sound settings

---

## Troubleshooting

### Command Not Recognized
1. Check Debug Output for: `[VOICE] Recognized: 'your words'`
2. Verify command is in the list above
3. Try an alias
4. Speak more clearly

### Wrong Command Executed
1. Speak more slowly
2. Reduce background noise
3. Check microphone quality
4. Try different phrasing

### No Response
1. Check VoiceListener is running (console window visible)
2. Check Debug Output for errors
3. Verify microphone is working
4. Restart application

---

## Quick Test Commands

Try these to test the system:

1. **"go home"** - Should navigate to dashboard
2. **"minimize"** - Should minimize window
3. **"maximize"** - Should maximize window
4. **"help"** - Should show voice commands
5. **"close"** - Should close current window

---

## Adding Custom Commands

See **CUSTOMIZE_COMMANDS.md** for detailed instructions on:
- Adding new global commands
- Adding window-specific commands
- Modifying existing commands
- Adding command aliases

---

## Command Format

All commands are:
- **Lowercase** - "GO HOME" becomes "go home"
- **Trimmed** - "  go home  " becomes "go home"
- **Exact match** - Must match one of the defined commands

---

## Debug Output

When you say a command, you'll see in Debug Output:
```
[VOICE] Recognized: 'go home'
[VOICE] New command detected: 'go home'
[VOICE] Processing command: 'go home'
[VOICE] Navigating to Home
```

If you see "Unknown command", the command isn't defined yet.

---

## Supported Languages

Currently: **English (US)** only

The VOSK model (vosk-model-small-en-us-0.15) is trained for US English.

For other languages, download a different model from:
https://alphacephei.com/vosk/models

---

## Performance

- **Recognition Latency**: < 500ms
- **Command Processing**: < 100ms
- **Total Response Time**: < 1 second
- **Accuracy**: 85-90% for clear speech

---

## System Requirements

- **Python**: 3.7 or higher
- **VOSK**: Latest version
- **PyAudio**: Latest version
- **Microphone**: Any USB or built-in microphone
- **OS**: Windows 7 or higher

---

## Getting Help

1. **Setup Issues**: See `QUICK_FIX_STEPS.md`
2. **Customization**: See `CUSTOMIZE_COMMANDS.md`
3. **Testing**: See `TEST_VOSK_MANUAL.md`
4. **Troubleshooting**: See `FIX_VOSK_ISSUE.md`

---

## Version

**VOSK Integration**: v1.0
**Model**: vosk-model-small-en-us-0.15
**Last Updated**: December 7, 2025

---

**Enjoy hands-free control of your gaming system! 🎮🎤**
