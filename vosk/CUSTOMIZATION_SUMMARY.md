# Voice Command Customization - Quick Start

## 🎉 System is Working!

Your VOSK voice recognition system is now operational. Here's how to customize it.

## 📚 Documentation Created

### 1. **CUSTOMIZE_COMMANDS.md** (Main Guide)
Complete guide with:
- How to add global commands
- How to add window-specific commands
- How to modify existing commands
- Examples and patterns
- Best practices

### 2. **VOICE_COMMANDS_REFERENCE.md** (Reference Card)
Quick reference showing:
- All current commands
- Command aliases
- Window-specific commands
- Tips for best recognition
- Troubleshooting guide

### 3. **COMMAND_TEMPLATE.txt** (Copy-Paste Template)
Ready-to-use code templates:
- Global command template
- Window-specific command template
- Common patterns
- Complete examples

## 🚀 Quick Start: Add Your First Custom Command

### Step 1: Open the File
Open `Services/GlobalVoiceCommandHandler.cs` in Visual Studio

### Step 2: Add Command to Switch
Find the `ProcessGlobalCommand` method and add:

```csharp
case "my command":
case "alternative name":
    MyCustomAction();
    break;
```

### Step 3: Add Action Method
Add this method anywhere in the class:

```csharp
private static void MyCustomAction()
{
    Application.Current.Dispatcher.Invoke(() =>
    {
        try
        {
            Debug.WriteLine("[VOICE] Executing my custom action");
            
            // YOUR CODE HERE
            MessageBox.Show("My command works!");
            
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"[VOICE] ERROR: {ex.Message}");
        }
    });
}
```

### Step 4: Test
1. Rebuild (Ctrl+Shift+B)
2. Run (F5)
3. Say "my command"
4. See the message box!

## 📋 Current Commands

### Global Commands
- **Navigation**: go home, login, signup, settings, profile, help
- **Actions**: add game, logout
- **Window**: close, minimize, maximize, exit

### Window-Specific
- **LoginWindow**: manual login, face login, voice login
- **SignUpWindow**: signup, capture face, record voice
- **HomeWindow**: dashboard, profile, voice commands, settings
- **VoiceRecordingWindow**: start recording, stop recording, done

## 💡 Common Customizations

### Add Game Control Commands
```csharp
case "play game":
case "start game":
    PlaySelectedGame();
    break;

case "pause game":
    PauseGame();
    break;

case "save game":
    SaveGame();
    break;
```

### Add Navigation Commands
```csharp
case "next":
case "next page":
    NavigateNext();
    break;

case "previous":
case "back":
    NavigatePrevious();
    break;
```

### Add Search Command
```csharp
case "search":
case "find":
    OpenSearch();
    break;
```

### Add Volume Control
```csharp
case "volume up":
case "louder":
    IncreaseVolume();
    break;

case "volume down":
case "quieter":
    DecreaseVolume();
    break;

case "mute":
    ToggleMute();
    break;
```

## 🎯 Where to Add Code

### Global Commands
Add to `ProcessGlobalCommand` method's switch statement

### Window-Specific Commands
Add to `ProcessWindowSpecificCommand` method

### Action Methods
Add in the appropriate region:
- `#region Navigation Actions` - For navigation
- `#region Window Actions` - For window management
- Create new region if needed

## 🔍 Testing Your Commands

### 1. Check Debug Output
```
[VOICE] Recognized: 'your command'
[VOICE] Processing command: 'your command'
[VOICE] Executing: Your Action
```

### 2. Manual Test
```powershell
Set-Content "bin\Debug\vosk\VoiceListenerApp\voice_listener.txt" -Value "your command"
```

### 3. Voice Test
Just say the command and watch it work!

## 📖 Full Documentation

1. **CUSTOMIZE_COMMANDS.md** - Complete customization guide
2. **VOICE_COMMANDS_REFERENCE.md** - All commands reference
3. **COMMAND_TEMPLATE.txt** - Copy-paste templates
4. **GlobalVoiceCommandHandler.cs** - The actual code file

## 🎓 Learning Path

### Beginner
1. Read **VOICE_COMMANDS_REFERENCE.md** to see what's available
2. Try all existing commands
3. Add a simple command using **COMMAND_TEMPLATE.txt**

### Intermediate
1. Read **CUSTOMIZE_COMMANDS.md** examples
2. Add multiple commands with aliases
3. Add window-specific commands

### Advanced
1. Create complex command logic
2. Integrate with game controls
3. Add conditional command behavior
4. Create command categories

## 🛠️ Tools Available

### Testing Scripts
- `test_voice_commands.ps1` - Monitor voice recognition
- `test_file_monitoring.ps1` - Test C# integration
- `test_python_setup.ps1` - Verify setup

### Documentation
- `CUSTOMIZE_COMMANDS.md` - How-to guide
- `VOICE_COMMANDS_REFERENCE.md` - Command reference
- `COMMAND_TEMPLATE.txt` - Code templates
- `FIX_VOSK_ISSUE.md` - Troubleshooting

## 💪 Next Steps

1. **Explore Current Commands**
   - Try all commands in VOICE_COMMANDS_REFERENCE.md
   - See what works for your workflow

2. **Add Your First Command**
   - Use COMMAND_TEMPLATE.txt
   - Start with something simple
   - Test it works

3. **Customize for Your Needs**
   - Add game-specific commands
   - Add shortcuts you use often
   - Add window management commands

4. **Share Your Commands**
   - Document your custom commands
   - Share with team members
   - Build a command library

## 🎮 Game-Specific Ideas

### For Action Games
- "attack", "defend", "jump", "run"
- "use item", "switch weapon"
- "quick save", "quick load"

### For Strategy Games
- "build", "upgrade", "research"
- "select all", "group units"
- "zoom in", "zoom out"

### For RPG Games
- "inventory", "map", "quest log"
- "save game", "load game"
- "character", "skills"

## 📞 Need Help?

1. Check **CUSTOMIZE_COMMANDS.md** for detailed examples
2. Use **COMMAND_TEMPLATE.txt** for ready-to-use code
3. Check **VOICE_COMMANDS_REFERENCE.md** for current commands
4. Look at existing commands in GlobalVoiceCommandHandler.cs

## ✅ Success Checklist

- [ ] System is working (voice recognition active)
- [ ] Tried all existing commands
- [ ] Read CUSTOMIZE_COMMANDS.md
- [ ] Added first custom command
- [ ] Tested custom command works
- [ ] Added command aliases
- [ ] Documented custom commands

## 🎉 You're Ready!

You now have:
- ✅ Working voice recognition system
- ✅ Complete documentation
- ✅ Code templates
- ✅ Testing tools
- ✅ Customization guide

Start customizing and make the system your own!

---

**Happy Voice Commanding! 🎤🎮**
