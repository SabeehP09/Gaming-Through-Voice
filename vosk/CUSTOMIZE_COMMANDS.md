# How to Customize Voice Commands

## Overview

Voice commands are handled in `Services/GlobalVoiceCommandHandler.cs`. This guide shows you how to:
1. Add new global commands
2. Add new window-specific commands
3. Modify existing command actions
4. Add command aliases

## Command Types

### 1. Global Commands
Work from any window in the application.

**Examples**: "go home", "logout", "add game", "minimize"

### 2. Window-Specific Commands
Only work when a specific window is active.

**Examples**: "manual login" (LoginWindow), "start recording" (VoiceRecordingWindow)

## How to Add a New Global Command

### Step 1: Add the Command to the Switch Statement

Open `Services/GlobalVoiceCommandHandler.cs` and find the `ProcessGlobalCommand` method.

Add your command to the switch statement:

```csharp
private static void ProcessGlobalCommand(string command)
{
    // ... existing code ...
    
    switch (command)
    {
        // ... existing commands ...
        
        // YOUR NEW COMMAND
        case "my command":
        case "alternative name":  // Optional alias
            MyCustomAction();
            break;
            
        // ... rest of commands ...
    }
}
```

### Step 2: Create the Action Method

Add a new method to handle your command:

```csharp
/// <summary>
/// Description of what this command does
/// </summary>
private static void MyCustomAction()
{
    Application.Current.Dispatcher.Invoke(() =>
    {
        try
        {
            Debug.WriteLine("[VOICE] Executing my custom action");
            
            // YOUR CODE HERE
            // Example: Open a window, navigate, perform action, etc.
            
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"[VOICE] ERROR in my custom action: {ex.Message}");
        }
    });
}
```

### Step 3: Test Your Command

1. Rebuild the application
2. Run it
3. Say "my command" into the microphone
4. Check Debug Output for: `[VOICE] Executing my custom action`

## How to Add a Window-Specific Command

### Step 1: Find the Window Section

In `ProcessWindowSpecificCommand` method, find or add your window type:

```csharp
private static bool ProcessWindowSpecificCommand(string command, Window window)
{
    if (window == null) return false;

    try
    {
        // YOUR WINDOW TYPE
        if (window is YourWindowType)
        {
            switch (command)
            {
                case "your command":
                case "alternative":
                    // Handle the command
                    Debug.WriteLine("[VOICE] YourWindow: Your command");
                    // Call method or perform action
                    return true;  // Command was handled
            }
        }
        
        // ... other window types ...
    }
    catch (Exception ex)
    {
        Debug.WriteLine($"[VOICE] ERROR: {ex.Message}");
    }

    return false;  // Command not handled
}
```

### Step 2: Implement the Action

You can either:
- Call a method on the window directly
- Trigger an event
- Perform the action inline

```csharp
if (window is YourWindowType yourWindow)
{
    switch (command)
    {
        case "do something":
            // Option 1: Call window method
            yourWindow.DoSomething();
            return true;
            
        case "trigger event":
            // Option 2: Perform action inline
            Application.Current.Dispatcher.Invoke(() =>
            {
                // Your code here
            });
            return true;
    }
}
```

## Examples

### Example 1: Add "Refresh" Command

```csharp
// In ProcessGlobalCommand switch statement
case "refresh":
case "reload":
    RefreshCurrentView();
    break;

// New method
private static void RefreshCurrentView()
{
    Application.Current.Dispatcher.Invoke(() =>
    {
        try
        {
            Debug.WriteLine("[VOICE] Refreshing current view");
            
            var homeWindow = Application.Current.Windows.OfType<HomeWindow>().FirstOrDefault();
            if (homeWindow != null)
            {
                // Trigger refresh logic
                // homeWindow.RefreshData();
            }
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"[VOICE] ERROR refreshing: {ex.Message}");
        }
    });
}
```

### Example 2: Add "Play Game" Command

```csharp
// In ProcessGlobalCommand switch statement
case "play game":
case "start game":
case "launch game":
    PlaySelectedGame();
    break;

// New method
private static void PlaySelectedGame()
{
    Application.Current.Dispatcher.Invoke(() =>
    {
        try
        {
            Debug.WriteLine("[VOICE] Playing selected game");
            
            var homeWindow = Application.Current.Windows.OfType<HomeWindow>().FirstOrDefault();
            if (homeWindow != null)
            {
                // Trigger play game logic
                // homeWindow.PlaySelectedGame();
            }
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"[VOICE] ERROR playing game: {ex.Message}");
        }
    });
}
```

### Example 3: Add "Next" and "Previous" Commands

```csharp
// In ProcessGlobalCommand switch statement
case "next":
case "next page":
    NavigateNext();
    break;

case "previous":
case "prev":
case "back":
    NavigatePrevious();
    break;

// New methods
private static void NavigateNext()
{
    Application.Current.Dispatcher.Invoke(() =>
    {
        try
        {
            Debug.WriteLine("[VOICE] Navigating to next");
            // Your navigation logic
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"[VOICE] ERROR: {ex.Message}");
        }
    });
}

private static void NavigatePrevious()
{
    Application.Current.Dispatcher.Invoke(() =>
    {
        try
        {
            Debug.WriteLine("[VOICE] Navigating to previous");
            // Your navigation logic
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"[VOICE] ERROR: {ex.Message}");
        }
    });
}
```

### Example 4: Add Game-Specific Commands

```csharp
// In ProcessWindowSpecificCommand
if (window.GetType().Name == "GameWindow")
{
    switch (command)
    {
        case "pause":
        case "pause game":
            Debug.WriteLine("[VOICE] GameWindow: Pause");
            // Pause game logic
            return true;

        case "resume":
        case "continue":
            Debug.WriteLine("[VOICE] GameWindow: Resume");
            // Resume game logic
            return true;

        case "save":
        case "save game":
            Debug.WriteLine("[VOICE] GameWindow: Save");
            // Save game logic
            return true;

        case "menu":
        case "main menu":
            Debug.WriteLine("[VOICE] GameWindow: Main menu");
            // Show menu logic
            return true;
    }
}
```

## Modifying Existing Commands

### Change Command Action

Find the command in the switch statement and modify its action:

```csharp
// Before
case "go home":
    NavigateToHome();
    break;

// After - with custom logic
case "go home":
    Application.Current.Dispatcher.Invoke(() =>
    {
        Debug.WriteLine("[VOICE] Going home with custom logic");
        // Your custom logic here
        NavigateToHome();
        // Additional actions
    });
    break;
```

### Add Command Aliases

Just add more case statements:

```csharp
// Before
case "logout":
    Logout();
    break;

// After - with more aliases
case "logout":
case "log out":
case "sign out":
case "exit account":
case "bye":
    Logout();
    break;
```

### Remove Commands

Simply delete or comment out the case:

```csharp
// Remove this command
// case "unwanted command":
//     UnwantedAction();
//     break;
```

## Best Practices

### 1. Use Clear Command Names
```csharp
// Good
case "add game":
case "new game":

// Bad
case "ag":
case "ng":
```

### 2. Provide Multiple Aliases
```csharp
// Good - multiple ways to say the same thing
case "go home":
case "open dashboard":
case "dashboard":
case "home":
```

### 3. Always Use try-catch
```csharp
private static void MyAction()
{
    Application.Current.Dispatcher.Invoke(() =>
    {
        try
        {
            // Your code
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"[VOICE] ERROR: {ex.Message}");
        }
    });
}
```

### 4. Log Command Execution
```csharp
Debug.WriteLine("[VOICE] Executing: My Action");
```

### 5. Check Window State
```csharp
var homeWindow = Application.Current.Windows.OfType<HomeWindow>().FirstOrDefault();
if (homeWindow != null)
{
    // Safe to use homeWindow
}
else
{
    Debug.WriteLine("[VOICE] HomeWindow not found");
}
```

## Testing Your Commands

### 1. Check Debug Output
After saying a command, check Visual Studio Debug Output for:
```
[VOICE] New command detected: 'your command'
[VOICE] Processing command: 'your command'
[VOICE] Executing: Your Action
```

### 2. Test with File
Manually write to `voice_listener.txt`:
```powershell
Set-Content "bin\Debug\vosk\VoiceListenerApp\voice_listener.txt" -Value "your command"
```

### 3. Test All Aliases
Make sure all aliases work:
- "go home"
- "open dashboard"
- "dashboard"
- "home"

## Common Patterns

### Pattern 1: Navigate to Window
```csharp
private static void NavigateToMyWindow()
{
    Application.Current.Dispatcher.Invoke(() =>
    {
        try
        {
            var myWindow = Application.Current.Windows.OfType<MyWindow>().FirstOrDefault();
            if (myWindow != null)
            {
                myWindow.Activate();
            }
            else
            {
                myWindow = new MyWindow();
                myWindow.Show();
            }
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"[VOICE] ERROR: {ex.Message}");
        }
    });
}
```

### Pattern 2: Toggle State
```csharp
private static void ToggleSomething()
{
    Application.Current.Dispatcher.Invoke(() =>
    {
        try
        {
            var window = Application.Current.Windows.OfType<MyWindow>().FirstOrDefault();
            if (window != null)
            {
                window.IsEnabled = !window.IsEnabled;
            }
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"[VOICE] ERROR: {ex.Message}");
        }
    });
}
```

### Pattern 3: Perform Action on Active Window
```csharp
private static void DoSomethingOnActiveWindow()
{
    Application.Current.Dispatcher.Invoke(() =>
    {
        try
        {
            var activeWindow = Application.Current.Windows
                .OfType<Window>()
                .FirstOrDefault(w => w.IsActive);
                
            if (activeWindow != null)
            {
                // Perform action
            }
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"[VOICE] ERROR: {ex.Message}");
        }
    });
}
```

## Quick Reference

### Current Global Commands
- Navigation: "go home", "login", "signup", "settings", "profile", "help"
- Actions: "add game", "logout"
- Window: "close", "minimize", "maximize", "exit"

### Current Window-Specific Commands
- **LoginWindow**: "manual login", "face login", "voice login", "forgot password"
- **SignUpWindow**: "signup", "capture face", "record voice"
- **HomeWindow**: "dashboard", "profile", "voice commands", "settings"
- **VoiceRecordingWindow**: "start recording", "stop recording", "done"

## Need Help?

1. Check Debug Output for errors
2. Verify command is lowercase in switch statement
3. Make sure method is called correctly
4. Test with manual file write first
5. Check window type is correct

## Example: Complete Custom Command

Here's a complete example of adding a "search" command:

```csharp
// 1. Add to switch statement in ProcessGlobalCommand
case "search":
case "find":
case "look for":
    OpenSearch();
    break;

// 2. Add the action method
/// <summary>
/// Open search functionality
/// </summary>
private static void OpenSearch()
{
    Application.Current.Dispatcher.Invoke(() =>
    {
        try
        {
            Debug.WriteLine("[VOICE] Opening search");
            
            var homeWindow = Application.Current.Windows.OfType<HomeWindow>().FirstOrDefault();
            if (homeWindow != null)
            {
                homeWindow.Activate();
                // Trigger search UI
                // homeWindow.ShowSearchDialog();
            }
            else
            {
                Debug.WriteLine("[VOICE] HomeWindow not found - user must be logged in");
            }
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"[VOICE] ERROR opening search: {ex.Message}");
        }
    });
}

// 3. Rebuild and test
// Say "search" or "find" or "look for"
```

That's it! You can now customize voice commands to fit your application's needs.
