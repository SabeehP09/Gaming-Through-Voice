using System;
using System.Diagnostics;
using System.Linq;
using System.Windows;
using System.Windows.Input;
using System.Windows.Media;
using GamingThroughVoiceRecognitionSystem.Views;

namespace GamingThroughVoiceRecognitionSystem.Services
{
    /// <summary>
    /// Handles global voice commands and routes them to appropriate actions
    /// </summary>
    public static class GlobalVoiceCommandHandler
    {
        #region Private Fields

        private static Window currentWindow;
        private static bool isUserLoggedIn = true;  // TEMPORARY: Set to true for testing

        #endregion

        #region Public Properties

        /// <summary>
        /// Gets or sets whether a user is currently logged in
        /// This controls access to post-login voice commands
        /// </summary>
        public static bool IsUserLoggedIn
        {
            get => isUserLoggedIn;
            set
            {
                isUserLoggedIn = value;
                Debug.WriteLine($"[VOICE] User login status changed: {(value ? "LOGGED IN" : "LOGGED OUT")}");
            }
        }

        #endregion

        #region Initialization

        /// <summary>
        /// Initialize the global voice command handler
        /// </summary>
        public static void Initialize()
        {
            try
            {
                Debug.WriteLine("[VOICE] Initializing GlobalVoiceCommandHandler...");
                
                // Start monitoring voice commands with optimized low-latency polling
                VoiceListenerManager.StartMonitoring(ProcessGlobalCommand, intervalMs: 5);
                
                Debug.WriteLine("[VOICE] GlobalVoiceCommandHandler initialized successfully");
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[VOICE] ERROR initializing GlobalVoiceCommandHandler: {ex.Message}");
            }
        }

        #endregion

        #region Command Processing

        /// <summary>
        /// Process a voice command received from the file monitor
        /// </summary>
        /// <param name="command">The voice command text (lowercase)</param>
        public static void ProcessGlobalCommand(string command)
        {
            try
            {
                Debug.WriteLine($"[VOICE] Processing command: '{command}'");
                
                // Clear the command file to prevent re-processing
                VoiceListenerManager.ClearVoiceCommand();
                
                // Get current active window
                Application.Current.Dispatcher.Invoke(() =>
                {
                    currentWindow = Application.Current.Windows.OfType<Window>().FirstOrDefault(w => w.IsActive);
                });

                // Try window-specific commands first
                bool handled = ProcessWindowSpecificCommand(command, currentWindow);
                if (handled)
                {
                    Debug.WriteLine($"[VOICE] Command handled by window-specific handler");
                    return;
                }

                // Process global commands with security
                switch (command)
                {
                    // ============================================================
                    // POST-LOGIN COMMANDS (Require authentication)
                    // ============================================================
                    
                    case "go home":
                    case "open dashboard":
                    case "dashboard":
                        if (RequireAuthentication("go home"))
                        {
                            NavigateToHome();
                        }
                        break;

                    // ============================================================
                    // PRE-LOGIN COMMANDS (Always available)
                    // ============================================================
                    
                    case "login":
                    case "sign in":
                        NavigateToLogin();
                        break;

                    case "signup":
                    case "register":
                    case "sign up":
                        NavigateToSignUp();
                        break;

                    case "open settings":
                    case "go to settings":
                    case "settings":
                        if (RequireAuthentication("settings"))
                        {
                            NavigateToSettings();
                        }
                        break;

                    case "go to profile":
                    case "open profile":
                    case "profile":
                        if (RequireAuthentication("profile"))
                        {
                            NavigateToProfile();
                        }
                        break;

                    case "voice commands":
                    case "help":
                    case "show commands":
                        if (RequireAuthentication("voice commands"))
                        {
                            ShowVoiceCommands();
                        }
                        break;

                    case "add game":
                    case "new game":
                        if (RequireAuthentication("add game"))
                        {
                            OpenAddGameWindow();
                        }
                        break;

                    case "logout":
                    case "sign out":
                    case "log out":
                        if (RequireAuthentication("logout"))
                        {
                            Logout();
                        }
                        break;

                    // Window management commands
                    case "close":
                    case "close window":
                        CloseCurrentWindow();
                        break;

                    case "minimize":
                        MinimizeWindow();
                        break;

                    case "maximize":
                        MaximizeWindow();
                        break;

                    case "exit":
                    case "quit":
                    case "close app":
                    case "close application":
                        ExitApplication();
                        break;

                    default:
                        Debug.WriteLine($"[VOICE] Unknown command: '{command}'");
                        break;
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[VOICE] ERROR processing command '{command}': {ex.Message}");
            }
        }

        /// <summary>
        /// Process window-specific voice commands
        /// </summary>
        /// <param name="command">The voice command text</param>
        /// <param name="window">The current active window</param>
        /// <returns>True if command was handled, false otherwise</returns>
        private static bool ProcessWindowSpecificCommand(string command, Window window)
        {
            if (window == null) return false;

            try
            {
                // LoginWindow commands
                if (window is LoginWindow loginWin)
                {
                    switch (command)
                    {
                        case "manual login":
                        case "manual":
                            Debug.WriteLine("[VOICE] LoginWindow: Manual login");
                            Application.Current.Dispatcher.Invoke(() =>
                            {
                                var manualLoginBtn = FindVisualChild<System.Windows.Controls.Button>(loginWin, "ManualLoginButton");
                                manualLoginBtn?.RaiseEvent(new RoutedEventArgs(System.Windows.Controls.Primitives.ButtonBase.ClickEvent));
                            });
                            return true;

                        case "face login":
                        case "face":
                            Debug.WriteLine("[VOICE] LoginWindow: Face login");
                            Application.Current.Dispatcher.Invoke(() =>
                            {
                                var faceLoginBtn = FindVisualChild<System.Windows.Controls.Border>(loginWin, "FaceLoginButton");
                                if (faceLoginBtn != null)
                                {
                                    faceLoginBtn.RaiseEvent(new MouseButtonEventArgs(Mouse.PrimaryDevice, 0, MouseButton.Left)
                                    {
                                        RoutedEvent = UIElement.MouseLeftButtonDownEvent
                                    });
                                }
                            });
                            return true;

                        case "voice login":
                        case "record voice":
                        case "record":
                            Debug.WriteLine("[VOICE] LoginWindow: Voice login - opening voice recording");
                            Application.Current.Dispatcher.Invoke(() =>
                            {
                                var voiceLoginBtn = FindVisualChild<System.Windows.Controls.Border>(loginWin, "VoiceLoginButton");
                                if (voiceLoginBtn != null)
                                {
                                    voiceLoginBtn.RaiseEvent(new MouseButtonEventArgs(Mouse.PrimaryDevice, 0, MouseButton.Left)
                                    {
                                        RoutedEvent = UIElement.MouseLeftButtonDownEvent
                                    });
                                }
                            });
                            return true;

                        case "forgot password":
                        case "reset password":
                            Debug.WriteLine("[VOICE] LoginWindow: Forgot password");
                            Application.Current.Dispatcher.Invoke(() =>
                            {
                                var forgotPwdText = FindVisualChild<System.Windows.Controls.TextBlock>(loginWin, "ForgotPasswordTextBlock");
                                if (forgotPwdText != null)
                                {
                                    forgotPwdText.RaiseEvent(new MouseButtonEventArgs(Mouse.PrimaryDevice, 0, MouseButton.Left)
                                    {
                                        RoutedEvent = UIElement.MouseLeftButtonDownEvent
                                    });
                                }
                            });
                            return true;
                    }
                }

                // SignUpWindow commands
                if (window is SignUpWindow signupWin)
                {
                    switch (command)
                    {
                        case "signup":
                        case "register":
                        case "create account":
                            Debug.WriteLine("[VOICE] SignUpWindow: Complete signup");
                            Application.Current.Dispatcher.Invoke(() =>
                            {
                                var signupBtn = FindVisualChild<System.Windows.Controls.Button>(signupWin, "SignupButton");
                                signupBtn?.RaiseEvent(new RoutedEventArgs(System.Windows.Controls.Primitives.ButtonBase.ClickEvent));
                            });
                            return true;

                        case "face":
                        case "capture face":
                        case "take photo":
                            Debug.WriteLine("[VOICE] SignUpWindow: Capture face");
                            Application.Current.Dispatcher.Invoke(() =>
                            {
                                var faceRegisterBtn = FindVisualChild<System.Windows.Controls.Border>(signupWin, "FaceRegisterButton");
                                if (faceRegisterBtn != null)
                                {
                                    faceRegisterBtn.RaiseEvent(new MouseButtonEventArgs(Mouse.PrimaryDevice, 0, MouseButton.Left)
                                    {
                                        RoutedEvent = UIElement.MouseLeftButtonDownEvent
                                    });
                                }
                            });
                            return true;

                        case "record voice":
                        case "voice":
                            Debug.WriteLine("[VOICE] SignUpWindow: Record voice - opening voice recording");
                            Application.Current.Dispatcher.Invoke(() =>
                            {
                                var voiceRegisterBtn = FindVisualChild<System.Windows.Controls.Border>(signupWin, "VoiceRegisterButton");
                                if (voiceRegisterBtn != null)
                                {
                                    voiceRegisterBtn.RaiseEvent(new MouseButtonEventArgs(Mouse.PrimaryDevice, 0, MouseButton.Left)
                                    {
                                        RoutedEvent = UIElement.MouseLeftButtonDownEvent
                                    });
                                }
                            });
                            return true;
                    }
                }

                // HomeWindow commands
                if (window is HomeWindow homeWin)
                {
                    switch (command)
                    {
                        case "dashboard":
                        case "home":
                            Debug.WriteLine("[VOICE] HomeWindow: Navigating to dashboard");
                            homeWin.NavigateToHome();
                            return true;

                        case "profile":
                        case "my profile":
                            Debug.WriteLine("[VOICE] HomeWindow: Navigating to profile");
                            homeWin.NavigateToProfile();
                            return true;

                        case "voice commands":
                        case "commands":
                            Debug.WriteLine("[VOICE] HomeWindow: Showing voice commands");
                            homeWin.NavigateToVoiceCommands();
                            return true;

                        case "settings":
                            Debug.WriteLine("[VOICE] HomeWindow: Navigating to settings");
                            homeWin.NavigateToSettings();
                            return true;

                        case "add game":
                        case "new game":
                            Debug.WriteLine("[VOICE] HomeWindow: Add game command");
                            Application.Current.Dispatcher.Invoke(() =>
                            {
                                // Check if we're on the dashboard
                                var contentArea = homeWin.ContentArea;
                                if (contentArea?.Content is DashboardControl dashboard)
                                {
                                    Debug.WriteLine("[VOICE] Found DashboardControl, triggering add game");
                                    var addGameBtn = FindVisualChild<System.Windows.Controls.Button>(dashboard, "AddGameButton");
                                    addGameBtn?.RaiseEvent(new RoutedEventArgs(System.Windows.Controls.Primitives.ButtonBase.ClickEvent));
                                }
                                else
                                {
                                    Debug.WriteLine("[VOICE] Not on dashboard, navigating to dashboard first");
                                    homeWin.NavigateToHome();
                                }
                            });
                            return true;

                        case "open subway surfers":
                        case "play subway surfers":
                        case "launch subway surfers":
                        case "start subway surfers":
                        case "open subway":
                        case "play subway":
                            Debug.WriteLine("[VOICE] HomeWindow: Launch Subway Surfers command");
                            Application.Current.Dispatcher.Invoke(() =>
                            {
                                var contentArea = homeWin.ContentArea;
                                if (contentArea?.Content is DashboardControl dashboard)
                                {
                                    Debug.WriteLine("[VOICE] Found DashboardControl, launching Subway Surfers");
                                    dashboard.LaunchGameByName("Subway Surfers");
                                }
                                else
                                {
                                    Debug.WriteLine("[VOICE] Not on dashboard, navigating to dashboard first");
                                    homeWin.NavigateToHome();
                                }
                            });
                            return true;

                        case "open mr racer":
                        case "play mr racer":
                        case "launch mr racer":
                        case "start mr racer":
                            Debug.WriteLine("[VOICE] HomeWindow: Launch Mr Racer command");
                            Application.Current.Dispatcher.Invoke(() =>
                            {
                                var contentArea = homeWin.ContentArea;
                                if (contentArea?.Content is DashboardControl dashboard)
                                {
                                    Debug.WriteLine("[VOICE] Found DashboardControl, launching Mr Racer");
                                    dashboard.LaunchGameByName("Mr Racer");
                                }
                                else
                                {
                                    Debug.WriteLine("[VOICE] Not on dashboard, navigating to dashboard first");
                                    homeWin.NavigateToHome();
                                }
                            });
                            return true;

                        // Game number commands (open game 1, play game 2, etc.)
                        case "open game one":
                        case "play game one":
                        case "start game one":
                        case "launch game one":
                        case "open game 1":
                        case "play game 1":
                        case "start game 1":
                        case "launch game 1":
                            LaunchGameByNumber(homeWin, 1);
                            return true;

                        case "open game two":
                        case "play game two":
                        case "start game two":
                        case "launch game two":
                        case "open game 2":
                        case "play game 2":
                        case "start game 2":
                        case "launch game 2":
                            LaunchGameByNumber(homeWin, 2);
                            return true;

                        case "open game three":
                        case "play game three":
                        case "start game three":
                        case "launch game three":
                        case "open game 3":
                        case "play game 3":
                        case "start game 3":
                        case "launch game 3":
                            LaunchGameByNumber(homeWin, 3);
                            return true;

                        case "open game four":
                        case "play game four":
                        case "start game four":
                        case "launch game four":
                        case "open game 4":
                        case "play game 4":
                        case "start game 4":
                        case "launch game 4":
                            LaunchGameByNumber(homeWin, 4);
                            return true;

                        case "open game five":
                        case "play game five":
                        case "start game five":
                        case "launch game five":
                        case "open game 5":
                        case "play game 5":
                        case "start game 5":
                        case "launch game 5":
                            LaunchGameByNumber(homeWin, 5);
                            return true;

                        case "change mode":
                        case "toggle theme":
                        case "switch theme":
                            Debug.WriteLine("[VOICE] HomeWindow: Toggle theme command");
                            Application.Current.Dispatcher.Invoke(() =>
                            {
                                // Check if we're on settings
                                var contentArea = homeWin.ContentArea;
                                if (contentArea?.Content is SettingsControl settings)
                                {
                                    Debug.WriteLine("[VOICE] Found SettingsControl, toggling theme");
                                    var themeToggle = FindVisualChild<System.Windows.Controls.Border>(settings, "ThemeToggle");
                                    if (themeToggle != null)
                                    {
                                        themeToggle.RaiseEvent(new MouseButtonEventArgs(Mouse.PrimaryDevice, 0, MouseButton.Left)
                                        {
                                            RoutedEvent = UIElement.MouseLeftButtonDownEvent
                                        });
                                    }
                                }
                                else
                                {
                                    Debug.WriteLine("[VOICE] Not on settings, navigating to settings first");
                                    homeWin.NavigateToSettings();
                                }
                            });
                            return true;
                    }
                }

                // VoiceRecordingWindow commands
                if (window.GetType().Name == "VoiceRecordingWindow")
                {
                    switch (command)
                    {
                        case "start":
                        case "start recording":
                        case "record":
                            Debug.WriteLine("[VOICE] VoiceRecordingWindow: Start recording");
                            Application.Current.Dispatcher.Invoke(() =>
                            {
                                var recordBtn = FindVisualChild<System.Windows.Controls.Button>(window, "RecordButton");
                                recordBtn?.RaiseEvent(new RoutedEventArgs(System.Windows.Controls.Primitives.ButtonBase.ClickEvent));
                            });
                            return true;

                        case "stop":
                        case "stop recording":
                            Debug.WriteLine("[VOICE] VoiceRecordingWindow: Stop recording");
                            Application.Current.Dispatcher.Invoke(() =>
                            {
                                var recordBtn = FindVisualChild<System.Windows.Controls.Button>(window, "RecordButton");
                                recordBtn?.RaiseEvent(new RoutedEventArgs(System.Windows.Controls.Primitives.ButtonBase.ClickEvent));
                            });
                            return true;

                        case "ok":
                        case "done":
                        case "finish":
                            Debug.WriteLine("[VOICE] VoiceRecordingWindow: Done");
                            Application.Current.Dispatcher.Invoke(() =>
                            {
                                var closeBtn = FindVisualChild<System.Windows.Controls.Button>(window, "CloseButton");
                                closeBtn?.RaiseEvent(new RoutedEventArgs(System.Windows.Controls.Primitives.ButtonBase.ClickEvent));
                            });
                            return true;
                    }
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[VOICE] ERROR in window-specific command processing: {ex.Message}");
            }

            return false;
        }

        #endregion

        #region Security Methods

        /// <summary>
        /// Check if user is authenticated before allowing command execution
        /// </summary>
        /// <param name="commandName">Name of the command being executed</param>
        /// <returns>True if user is logged in, false otherwise</returns>
        private static bool RequireAuthentication(string commandName)
        {
            if (!isUserLoggedIn)
            {
                Debug.WriteLine($"[VOICE] SECURITY: Command '{commandName}' blocked - user not logged in");
                return false;
            }
            return true;
        }

        /// <summary>
        /// Check if navigation to target window is allowed from current window
        /// </summary>
        /// <param name="currentWindow">The current active window</param>
        /// <param name="targetWindowType">The type of window to navigate to</param>
        /// <returns>True if navigation is allowed, false otherwise</returns>
        private static bool IsNavigationAllowed(Window currentWindow, Type targetWindowType)
        {
            if (currentWindow == null)
            {
                Debug.WriteLine("[VOICE] SECURITY: No active window, allowing navigation");
                return true;
            }

            Type currentType = currentWindow.GetType();

            // Define allowed navigation paths (context-based security)
            // LoginWindow <-> SignUpWindow (bidirectional)
            if (currentType == typeof(LoginWindow) && targetWindowType == typeof(SignUpWindow))
            {
                Debug.WriteLine("[VOICE] SECURITY: Navigation from Login to Signup - ALLOWED");
                return true;
            }

            if (currentType == typeof(SignUpWindow) && targetWindowType == typeof(LoginWindow))
            {
                Debug.WriteLine("[VOICE] SECURITY: Navigation from Signup to Login - ALLOWED");
                return true;
            }

            // Same window navigation is always allowed
            if (currentType == targetWindowType)
            {
                Debug.WriteLine("[VOICE] SECURITY: Same window navigation - ALLOWED");
                return true;
            }

            // Block all other pre-login navigations
            Debug.WriteLine($"[VOICE] SECURITY: Navigation from {currentType.Name} to {targetWindowType.Name} - BLOCKED");
            return false;
        }

        #endregion

        #region Navigation Actions

        /// <summary>
        /// Navigate to home/dashboard
        /// </summary>
        private static void NavigateToHome()
        {
            Application.Current.Dispatcher.Invoke(() =>
            {
                try
                {
                    Debug.WriteLine("[VOICE] Navigating to Home");
                    
                    // Check if user is logged in
                    // If HomeWindow exists, activate it or navigate to dashboard
                    var homeWindow = Application.Current.Windows.OfType<HomeWindow>().FirstOrDefault();
                    if (homeWindow != null)
                    {
                        homeWindow.Activate();
                        // TODO: Navigate to dashboard control within HomeWindow
                    }
                    else
                    {
                        Debug.WriteLine("[VOICE] HomeWindow not found - user may not be logged in");
                    }
                }
                catch (Exception ex)
                {
                    Debug.WriteLine($"[VOICE] ERROR navigating to home: {ex.Message}");
                }
            });
        }

        /// <summary>
        /// Navigate to login window
        /// </summary>
        private static void NavigateToLogin()
        {
            Application.Current.Dispatcher.Invoke(() =>
            {
                try
                {
                    Debug.WriteLine("[VOICE] Navigating to Login");
                    
                    var loginWindow = Application.Current.Windows.OfType<LoginWindow>().FirstOrDefault();
                    if (loginWindow != null)
                    {
                        Debug.WriteLine("[VOICE] LoginWindow already exists, activating it");
                        loginWindow.Activate();
                    }
                    else
                    {
                        Debug.WriteLine("[VOICE] Creating new LoginWindow");
                        
                        // Close SignUpWindow if it's open (to avoid multiple windows)
                        var signupWindow = Application.Current.Windows.OfType<SignUpWindow>().FirstOrDefault();
                        if (signupWindow != null)
                        {
                            Debug.WriteLine("[VOICE] Closing SignUpWindow before opening LoginWindow");
                            signupWindow.Close();
                        }
                        
                        // Hide MainWindow if it's open (to avoid it staying in background)
                        var mainWindow = Application.Current.Windows.OfType<MainWindow>().FirstOrDefault();
                        if (mainWindow != null)
                        {
                            Debug.WriteLine("[VOICE] Hiding MainWindow before opening LoginWindow");
                            mainWindow.Hide();
                        }
                        
                        loginWindow = new LoginWindow();
                        loginWindow.Show();
                        Debug.WriteLine("[VOICE] LoginWindow created and shown");
                    }
                }
                catch (Exception ex)
                {
                    Debug.WriteLine($"[VOICE] ERROR navigating to login: {ex.Message}");
                    Debug.WriteLine($"[VOICE] Stack trace: {ex.StackTrace}");
                }
            });
        }

        /// <summary>
        /// Navigate to signup window
        /// </summary>
        private static void NavigateToSignUp()
        {
            Application.Current.Dispatcher.Invoke(() =>
            {
                try
                {
                    Debug.WriteLine("[VOICE] Navigating to SignUp");
                    
                    var signupWindow = Application.Current.Windows.OfType<SignUpWindow>().FirstOrDefault();
                    if (signupWindow != null)
                    {
                        Debug.WriteLine("[VOICE] SignUpWindow already exists, activating it");
                        signupWindow.Activate();
                    }
                    else
                    {
                        Debug.WriteLine("[VOICE] Creating new SignUpWindow");
                        
                        // Close LoginWindow if it's open (to avoid multiple windows)
                        var loginWindow = Application.Current.Windows.OfType<LoginWindow>().FirstOrDefault();
                        if (loginWindow != null)
                        {
                            Debug.WriteLine("[VOICE] Closing LoginWindow before opening SignUpWindow");
                            loginWindow.Close();
                        }
                        
                        // Hide MainWindow if it's open (to avoid it staying in background)
                        var mainWindow = Application.Current.Windows.OfType<MainWindow>().FirstOrDefault();
                        if (mainWindow != null)
                        {
                            Debug.WriteLine("[VOICE] Hiding MainWindow before opening SignUpWindow");
                            mainWindow.Hide();
                        }
                        
                        signupWindow = new SignUpWindow();
                        signupWindow.Show();
                        Debug.WriteLine("[VOICE] SignUpWindow created and shown");
                    }
                }
                catch (Exception ex)
                {
                    Debug.WriteLine($"[VOICE] ERROR navigating to signup: {ex.Message}");
                    Debug.WriteLine($"[VOICE] Stack trace: {ex.StackTrace}");
                }
            });
        }

        /// <summary>
        /// Navigate to settings
        /// </summary>
        private static void NavigateToSettings()
        {
            Application.Current.Dispatcher.Invoke(() =>
            {
                try
                {
                    Debug.WriteLine("[VOICE] Navigating to Settings");
                    
                    var homeWindow = Application.Current.Windows.OfType<HomeWindow>().FirstOrDefault();
                    if (homeWindow != null)
                    {
                        homeWindow.Activate();
                        // TODO: Navigate to settings control within HomeWindow
                    }
                }
                catch (Exception ex)
                {
                    Debug.WriteLine($"[VOICE] ERROR navigating to settings: {ex.Message}");
                }
            });
        }

        /// <summary>
        /// Navigate to profile
        /// </summary>
        private static void NavigateToProfile()
        {
            Application.Current.Dispatcher.Invoke(() =>
            {
                try
                {
                    Debug.WriteLine("[VOICE] Navigating to Profile");
                    
                    var homeWindow = Application.Current.Windows.OfType<HomeWindow>().FirstOrDefault();
                    if (homeWindow != null)
                    {
                        homeWindow.Activate();
                        // TODO: Navigate to profile control within HomeWindow
                    }
                }
                catch (Exception ex)
                {
                    Debug.WriteLine($"[VOICE] ERROR navigating to profile: {ex.Message}");
                }
            });
        }

        /// <summary>
        /// Show voice commands help
        /// </summary>
        private static void ShowVoiceCommands()
        {
            Application.Current.Dispatcher.Invoke(() =>
            {
                try
                {
                    Debug.WriteLine("[VOICE] Showing voice commands help");
                    
                    var homeWindow = Application.Current.Windows.OfType<HomeWindow>().FirstOrDefault();
                    if (homeWindow != null)
                    {
                        homeWindow.Activate();
                        // TODO: Navigate to voice commands control within HomeWindow
                    }
                }
                catch (Exception ex)
                {
                    Debug.WriteLine($"[VOICE] ERROR showing voice commands: {ex.Message}");
                }
            });
        }

        #endregion

        #region Window Actions

        /// <summary>
        /// Close the current active window
        /// </summary>
        private static void CloseCurrentWindow()
        {
            Application.Current.Dispatcher.Invoke(() =>
            {
                try
                {
                    Debug.WriteLine("[VOICE] Closing current window");
                    
                    var activeWindow = Application.Current.Windows.OfType<Window>().FirstOrDefault(w => w.IsActive);
                    if (activeWindow != null && !(activeWindow is MainWindow))
                    {
                        activeWindow.Close();
                    }
                }
                catch (Exception ex)
                {
                    Debug.WriteLine($"[VOICE] ERROR closing window: {ex.Message}");
                }
            });
        }

        /// <summary>
        /// Minimize the current window
        /// </summary>
        private static void MinimizeWindow()
        {
            Application.Current.Dispatcher.Invoke(() =>
            {
                try
                {
                    Debug.WriteLine("[VOICE] Minimizing window");
                    
                    var activeWindow = Application.Current.Windows.OfType<Window>().FirstOrDefault(w => w.IsActive);
                    if (activeWindow != null)
                    {
                        activeWindow.WindowState = WindowState.Minimized;
                    }
                }
                catch (Exception ex)
                {
                    Debug.WriteLine($"[VOICE] ERROR minimizing window: {ex.Message}");
                }
            });
        }

        /// <summary>
        /// Maximize the current window
        /// </summary>
        private static void MaximizeWindow()
        {
            Application.Current.Dispatcher.Invoke(() =>
            {
                try
                {
                    Debug.WriteLine("[VOICE] Maximizing window");
                    
                    var activeWindow = Application.Current.Windows.OfType<Window>().FirstOrDefault(w => w.IsActive);
                    if (activeWindow != null)
                    {
                        activeWindow.WindowState = activeWindow.WindowState == WindowState.Maximized 
                            ? WindowState.Normal 
                            : WindowState.Maximized;
                    }
                }
                catch (Exception ex)
                {
                    Debug.WriteLine($"[VOICE] ERROR maximizing window: {ex.Message}");
                }
            });
        }

        /// <summary>
        /// Exit the application
        /// </summary>
        private static void ExitApplication()
        {
            Application.Current.Dispatcher.Invoke(() =>
            {
                try
                {
                    Debug.WriteLine("[VOICE] Exiting application");
                    Application.Current.Shutdown();
                }
                catch (Exception ex)
                {
                    Debug.WriteLine($"[VOICE] ERROR exiting application: {ex.Message}");
                }
            });
        }

        /// <summary>
        /// Logout the current user
        /// </summary>
        private static void Logout()
        {
            Application.Current.Dispatcher.Invoke(() =>
            {
                try
                {
                    Debug.WriteLine("[VOICE] Logging out");
                    
                    // Set login status to false
                    IsUserLoggedIn = false;
                    
                    // Close all windows except main
                    foreach (Window window in Application.Current.Windows)
                    {
                        if (!(window is MainWindow))
                        {
                            window.Close();
                        }
                    }
                    
                    // Open login window
                    var loginWindow = new LoginWindow();
                    loginWindow.Show();
                }
                catch (Exception ex)
                {
                    Debug.WriteLine($"[VOICE] ERROR during logout: {ex.Message}");
                }
            });
        }

        /// <summary>
        /// Open add game window
        /// </summary>
        private static void OpenAddGameWindow()
        {
            Application.Current.Dispatcher.Invoke(() =>
            {
                try
                {
                    Debug.WriteLine("[VOICE] Opening add game window");
                    
                    // Note: AddGameWindow requires UserModel and DbConn parameters
                    // This should be triggered from HomeWindow which has access to these
                    // For now, we'll just log that the command was received
                    Debug.WriteLine("[VOICE] 'Add game' command received - this should be handled by HomeWindow");
                    
                    // Try to find HomeWindow and trigger its add game functionality
                    var homeWindow = Application.Current.Windows.OfType<HomeWindow>().FirstOrDefault();
                    if (homeWindow != null)
                    {
                        // HomeWindow should have a method to handle adding games
                        // For now, just activate the window
                        homeWindow.Activate();
                        Debug.WriteLine("[VOICE] HomeWindow activated - user can manually add game");
                    }
                    else
                    {
                        Debug.WriteLine("[VOICE] HomeWindow not found - user must be logged in to add games");
                    }
                }
                catch (Exception ex)
                {
                    Debug.WriteLine($"[VOICE] ERROR opening add game window: {ex.Message}");
                }
            });
        }

        /// <summary>
        /// Launch a game by its position number on the dashboard
        /// </summary>
        /// <param name="homeWindow">The HomeWindow instance</param>
        /// <param name="gameNumber">The game number (1-based index)</param>
        private static void LaunchGameByNumber(HomeWindow homeWindow, int gameNumber)
        {
            Application.Current.Dispatcher.Invoke(() =>
            {
                try
                {
                    Debug.WriteLine($"[VOICE] Launching game #{gameNumber}");
                    
                    var contentArea = homeWindow.ContentArea;
                    if (contentArea?.Content is DashboardControl dashboard)
                    {
                        Debug.WriteLine("[VOICE] Found DashboardControl, launching game by number");
                        dashboard.LaunchGameByNumber(gameNumber);
                    }
                    else
                    {
                        Debug.WriteLine("[VOICE] Not on dashboard");
                    }
                }
                catch (Exception ex)
                {
                    Debug.WriteLine($"[VOICE] ERROR launching game by number: {ex.Message}");
                }
            });
        }

        #endregion

        #region Cleanup

        /// <summary>
        /// Cleanup the global voice command handler
        /// </summary>
        public static void Cleanup()
        {
            try
            {
                Debug.WriteLine("[VOICE] Cleaning up GlobalVoiceCommandHandler...");
                VoiceListenerManager.StopMonitoring();
                currentWindow = null;
                Debug.WriteLine("[VOICE] GlobalVoiceCommandHandler cleanup completed");
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[VOICE] ERROR during GlobalVoiceCommandHandler cleanup: {ex.Message}");
            }
        }

        #endregion

        #region Helper Methods

        /// <summary>
        /// Find a child element in the visual tree by name
        /// </summary>
        private static T FindVisualChild<T>(DependencyObject parent, string name) where T : DependencyObject
        {
            if (parent == null) return null;

            int childCount = VisualTreeHelper.GetChildrenCount(parent);
            for (int i = 0; i < childCount; i++)
            {
                var child = VisualTreeHelper.GetChild(parent, i);
                
                if (child is T typedChild && (child as FrameworkElement)?.Name == name)
                {
                    return typedChild;
                }

                var result = FindVisualChild<T>(child, name);
                if (result != null)
                {
                    return result;
                }
            }

            return null;
        }

        #endregion
    }
}
