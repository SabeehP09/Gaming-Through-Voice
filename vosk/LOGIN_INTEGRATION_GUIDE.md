# Quick Integration Guide - Voice Command Security

## What You Need to Do

Add **ONE LINE** of code after successful login to enable voice command security.

## Step 1: Find Your Login Success Code

Look for where you handle successful login in your application. This is typically in:
- `LoginWindow.xaml.cs`
- `HomeWindow.xaml.cs`
- Or wherever you process login

## Step 2: Add the Import

At the top of your file, add:

```csharp
using GamingThroughVoiceRecognitionSystem.Services;
```

## Step 3: Set Login Status

After successful login, add this ONE line:

```csharp
GlobalVoiceCommandHandler.IsUserLoggedIn = true;
```

## Complete Example

### Example 1: In LoginWindow

```csharp
using System;
using System.Windows;
using GamingThroughVoiceRecognitionSystem.Services;  // ADD THIS

namespace GamingThroughVoiceRecognitionSystem.Views
{
    public partial class LoginWindow : Window
    {
        private void OnLoginButtonClick(object sender, RoutedEventArgs e)
        {
            // Your existing login logic
            bool loginSuccess = PerformLogin(username, password);
            
            if (loginSuccess)
            {
                // ADD THIS LINE - Enable voice commands
                GlobalVoiceCommandHandler.IsUserLoggedIn = true;
                
                // Your existing code to open HomeWindow
                var homeWindow = new HomeWindow(user, dbConn);
                homeWindow.Show();
                this.Close();
            }
        }
    }
}
```

### Example 2: In Voice Login Method

```csharp
private void OnVoiceLoginSuccess(UserModel user)
{
    try
    {
        // ADD THIS LINE - Enable voice commands
        GlobalVoiceCommandHandler.IsUserLoggedIn = true;
        
        // Your existing navigation code
        var homeWindow = new HomeWindow(user, dbConn);
        homeWindow.Show();
        this.Close();
    }
    catch (Exception ex)
    {
        MessageBox.Show($"Error: {ex.Message}");
    }
}
```

### Example 3: In Face Login Method

```csharp
private void OnFaceLoginSuccess(UserModel user)
{
    // ADD THIS LINE - Enable voice commands
    GlobalVoiceCommandHandler.IsUserLoggedIn = true;
    
    // Your existing code
    NavigateToHome(user);
}
```

## That's It!

Just add that one line after successful login, and voice command security will work automatically.

## What Happens

### Before Adding the Line
- User can say "go home" before logging in → Nothing happens (blocked)
- User can say "settings" before logging in → Nothing happens (blocked)

### After Adding the Line
- User logs in successfully
- `IsUserLoggedIn` is set to `true`
- User can now say "go home" → Navigates to home ✅
- User can now say "settings" → Opens settings ✅

## Testing

### Test 1: Before Login
1. Start app (don't login)
2. Say "go home"
3. Check Debug Output: `[VOICE] SECURITY: Command 'go home' blocked - user not logged in`

### Test 2: After Login
1. Login successfully
2. Check Debug Output: `[VOICE] User login status changed: LOGGED IN`
3. Say "go home"
4. Should navigate to home ✅

### Test 3: After Logout
1. Say "logout"
2. Check Debug Output: `[VOICE] User login status changed: LOGGED OUT`
3. Say "go home"
4. Should be blocked again ✅

## Where to Add It

Find any of these methods in your code and add the line:

```csharp
// Manual login success
private void OnManualLoginSuccess(UserModel user)
{
    GlobalVoiceCommandHandler.IsUserLoggedIn = true;  // ADD THIS
    // ... rest of your code
}

// Voice login success
private void OnVoiceLoginSuccess(UserModel user)
{
    GlobalVoiceCommandHandler.IsUserLoggedIn = true;  // ADD THIS
    // ... rest of your code
}

// Face login success
private void OnFaceLoginSuccess(UserModel user)
{
    GlobalVoiceCommandHandler.IsUserLoggedIn = true;  // ADD THIS
    // ... rest of your code
}

// Any other login success handler
private void HandleLoginSuccess(UserModel user)
{
    GlobalVoiceCommandHandler.IsUserLoggedIn = true;  // ADD THIS
    // ... rest of your code
}
```

## Common Locations

### LoginWindow.xaml.cs
```csharp
// Look for button click handlers
private void LoginButton_Click(object sender, RoutedEventArgs e)
{
    // After successful login
    GlobalVoiceCommandHandler.IsUserLoggedIn = true;
}

// Or async methods
private async void PerformLogin()
{
    // After successful login
    GlobalVoiceCommandHandler.IsUserLoggedIn = true;
}
```

### VoiceRecognitionService.cs
```csharp
public void OnVoiceIdentified(UserModel user)
{
    // After successful voice identification
    GlobalVoiceCommandHandler.IsUserLoggedIn = true;
}
```

### FaceRecognitionService.cs
```csharp
public void OnFaceIdentified(UserModel user)
{
    // After successful face identification
    GlobalVoiceCommandHandler.IsUserLoggedIn = true;
}
```

## Logout (Already Handled)

You don't need to do anything for logout! It's already handled automatically in the voice command system.

When user says "logout", the system automatically:
1. Sets `IsUserLoggedIn = false`
2. Closes all windows
3. Opens LoginWindow

## Troubleshooting

### Commands Still Blocked After Login
**Problem**: Said "go home" after login, but still blocked

**Solution**: Make sure you added the line in the right place:
```csharp
// WRONG - Before login check
GlobalVoiceCommandHandler.IsUserLoggedIn = true;
if (loginSuccess) { ... }

// RIGHT - After successful login
if (loginSuccess) {
    GlobalVoiceCommandHandler.IsUserLoggedIn = true;
    // ... navigate to home
}
```

### Commands Work Before Login
**Problem**: Can access post-login screens before logging in

**Solution**: Make sure you're NOT setting `IsUserLoggedIn = true` on app startup

### Logout Doesn't Block Commands
**Problem**: After logout, can still access post-login screens

**Solution**: The logout method already handles this. Check if you're manually setting `IsUserLoggedIn = true` somewhere else.

## Quick Checklist

- [ ] Added `using GamingThroughVoiceRecognitionSystem.Services;`
- [ ] Added `GlobalVoiceCommandHandler.IsUserLoggedIn = true;` after successful login
- [ ] Tested: Commands blocked before login
- [ ] Tested: Commands work after login
- [ ] Tested: Commands blocked after logout

## That's All!

Just one line of code, and your voice command security is complete!

```csharp
GlobalVoiceCommandHandler.IsUserLoggedIn = true;
```

Add it after successful login, and you're done! 🎉
