using GamingThroughVoiceRecognitionSystem.Database;
using GamingThroughVoiceRecognitionSystem.Services;
using System;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Animation;

namespace GamingThroughVoiceRecognitionSystem.Views
{
    public partial class LoginWindow : Window
    {
        private readonly DbConn db = new DbConn();

        public LoginWindow()
        {
            InitializeComponent();
        }

        // ---------------------------------------------------------
        // WINDOW EVENTS
        // ---------------------------------------------------------
        private void Window_Loaded(object sender, RoutedEventArgs e)
        {
            if (this.Resources["BackgroundAnimationStoryboard"] is Storyboard sb)
                sb.Begin();
        }

        private void WindowChrome_MouseLeftButtonDown(object sender, MouseButtonEventArgs e)
        {
            if (e.ButtonState == MouseButtonState.Pressed)
                DragMove();
        }

        private void MinimizeButton_Click(object sender, RoutedEventArgs e)
        {
            WindowState = WindowState.Minimized;
        }

        private void MaximizeButton_Click(object sender, RoutedEventArgs e)
        {
            WindowState = (WindowState == WindowState.Normal) ? WindowState.Maximized : WindowState.Normal;
        }

        private void CloseButton_Click(object sender, RoutedEventArgs e)
        {
            Close();
        }

        // ---------------------------------------------------------
        // PLACEHOLDER HANDLING
        // ---------------------------------------------------------
        private void EmailTextBox_GotFocus(object sender, RoutedEventArgs e)
        {
            if (EmailTextBox.Text == "Email")
            {
                EmailTextBox.Text = "";
                EmailTextBox.Foreground = Brushes.White;
            }
        }

        private void EmailTextBox_LostFocus(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrWhiteSpace(EmailTextBox.Text))
            {
                EmailTextBox.Text = "Email";
                EmailTextBox.Foreground = Brushes.Gray;
            }
        }

        private void PasswordBox_PasswordChanged(object sender, RoutedEventArgs e)
        {
            PasswordPlaceholder.Visibility = string.IsNullOrEmpty(PasswordBox.Password) ? Visibility.Visible : Visibility.Hidden;
        }

        // ---------------------------------------------------------
        // BUTTON EVENTS
        // ---------------------------------------------------------
        private async void FaceLoginButton_Click(object sender, MouseButtonEventArgs e)
        {
            FaceRecognitionService_OpenCV faceService = null;
            Window processingMsg = null;
            
            try
            {
                // Get user ID from email (if provided)
                string email = (EmailTextBox.Text == "Email" || string.IsNullOrWhiteSpace(EmailTextBox.Text)) 
                    ? null : EmailTextBox.Text.Trim();
                
                int userId = -1;
                
                // If email is provided, get the user ID
                if (!string.IsNullOrEmpty(email))
                {
                    // Get user ID from database
                    userId = db.GetUserIdByEmail(email);
                    
                    if (userId == -1)
                    {
                        GlassMessageBox.ShowError("❌ Email not found.\n\nPlease enter a valid email or register first.");
                        return;
                    }
                }
                else
                {
                    GlassMessageBox.ShowError("📧 Please enter your email address first.\n\nThis helps identify which face to authenticate.");
                    return;
                }
                
                // Show initial checking message
                processingMsg = GlassMessageBox.ShowProcessing("🔍 Initializing face recognition...");
                
                // Initialize face recognition service
                faceService = new FaceRecognitionService_OpenCV();
                
                // Check server health and webcam in parallel for faster response
                var serverHealthTask = faceService.CheckServerHealthAsync(forceCheck: true);
                var webcamStatusTask = Task.Run(() => faceService.GetWebcamStatus());
                
                await Task.WhenAll(serverHealthTask, webcamStatusTask);
                
                bool serverHealthy = await serverHealthTask;
                var webcamStatus = await webcamStatusTask;
                
                processingMsg?.Close();
                
                if (!serverHealthy)
                {
                    GlassMessageBox.ShowError(
                        "🔴 Face recognition server is offline.\n\n" +
                        "Alternative options:\n" +
                        "• Use password authentication below\n" +
                        "• Use voice authentication\n\n" +
                        "To start server:\nFaceRecognition\\opencv_server\\start_opencv_server.bat"
                    );
                    return;
                }
                
                if (!webcamStatus.available)
                {
                    GlassMessageBox.ShowError("📷 " + webcamStatus.message);
                    return;
                }
                
                // Show authentication in progress
                processingMsg = GlassMessageBox.ShowProcessing("📸 Authenticating...\n\nPlease look at the camera and stay still.");
                
                // Authenticate with face
                var result = await faceService.AuthenticateFaceAsync(userId);
                
                processingMsg?.Close();
                
                if (result.success)
                {
                    // Show success with confidence
                    GlassMessageBox.ShowSuccess($"✅ Face authenticated!\n\nConfidence: {result.confidence:P0}\n\nLogging you in...", autoDismiss: true);
                    
                    // Small delay for user to see success message
                    await Task.Delay(1500);
                    
                    HomeWindow homeWindow = new HomeWindow(userId);
                    homeWindow.Show();
                    this.Close();
                    GlobalVoiceCommandHandler.IsUserLoggedIn = true;
                }
                else
                {
                    GlassMessageBox.ShowError(
                        $"❌ Face authentication failed.\n\n{result.message}\n\n" +
                        "Try again or use:\n" +
                        "• Password authentication\n" +
                        "• Voice authentication"
                    );
                }
            }
            catch (Exception ex)
            {
                processingMsg?.Close();
                System.Diagnostics.Debug.WriteLine($"Face login error: {ex.Message}");
                GlassMessageBox.ShowError(
                    $"❌ Face login error: {ex.Message}\n\n" +
                    "Please use an alternative method:\n" +
                    "• Password authentication\n" +
                    "• Voice authentication"
                );
            }
            finally
            {
                faceService?.Dispose();
            }
        }

        private async void VoiceLoginButton_Click(object sender, MouseButtonEventArgs e)
        {
            try
            {
                // Open voice recording window directly (no pre-check needed for recording)
                var voiceRecordingWindow = new VoiceRecordingWindow();
                bool? result = voiceRecordingWindow.ShowDialog();

                if (result == true && voiceRecordingWindow.IsRecorded && voiceRecordingWindow.RecordedVoiceData != null)
                {
                    System.Diagnostics.Debug.WriteLine($"Voice login: Audio data length = {voiceRecordingWindow.RecordedVoiceData.Length}");
                    
                    // Show processing message
                    var processingMsg = GlassMessageBox.ShowProcessing("Authenticating voice...\n\nPlease wait.");
                    
                    try
                    {
                        // Check backend health and identify user
                        var voiceService = new VoiceRecognitionService();
                        bool isHealthy = await voiceService.IsBackendHealthyAsync();
                        
                        if (!isHealthy)
                        {
                            processingMsg?.Close();
                            GlassMessageBox.ShowError(
                                "Voice authentication server is not responding.\n\n" +
                                "Please ensure the server is running:\n" +
                                "VoiceBackend\\start_server_no_mic.bat\n\n" +
                                "Alternative: Use password authentication below."
                            );
                            return;
                        }
                        
                        // Identify user by voice using Python API
                        var identifyResult = await voiceService.IdentifyUserAsync(
                            voiceRecordingWindow.RecordedVoiceData
                        );
                        
                        bool identified = identifyResult.Item1;
                        string userIdStr = identifyResult.Item2;
                        double confidence = identifyResult.Item3;
                        
                        processingMsg?.Close();
                        
                        System.Diagnostics.Debug.WriteLine($"Identification result: identified={identified}, userId={userIdStr}, confidence={confidence}");
                        
                        if (identified && confidence > 70)
                        {
                            int userId = int.Parse(userIdStr);
                            
                            GlassMessageBox.ShowSuccess($"✓ Voice authenticated!\nConfidence: {confidence:F1}%", autoDismiss: true);
                            
                            // Wait for auto-dismiss
                            await Task.Delay(2000);
                            
                            // Login successful
                            HomeWindow homeWindow = new HomeWindow(userId);
                            homeWindow.Show();
                            this.Close();
                            GlobalVoiceCommandHandler.IsUserLoggedIn = true;
                        }
                        else if (identified)
                        {
                            GlassMessageBox.ShowError($"Voice recognized but confidence too low: {confidence:F1}%\n\nPlease try again or use password authentication.");
                        }
                        else
                        {
                            GlassMessageBox.ShowError("Voice not recognized.\n\nPlease register first or use password authentication.");
                        }
                    }
                    catch (Exception ex)
                    {
                        processingMsg?.Close();
                        System.Diagnostics.Debug.WriteLine($"Voice authentication error: {ex.Message}");
                        GlassMessageBox.ShowError(
                            $"Voice authentication failed: {ex.Message}\n\n" +
                            "Please ensure the voice server is running or use password authentication."
                        );
                    }
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Voice login error: {ex.Message}");
                GlassMessageBox.ShowError($"Voice recording error: {ex.Message}");
            }
        }

        private void ManualLoginButton_Click(object sender, RoutedEventArgs e)
        {
            string email = (EmailTextBox.Text == "Email") ? "" : EmailTextBox.Text.Trim();
            string password = PasswordBox.Password.Trim();

            if (string.IsNullOrEmpty(email) || string.IsNullOrEmpty(password))
            {
                GlassMessageBox.Show("Please enter both email and password.");
                return;
            }

            if (db.Login(email, password, out int userId))
            {
                HomeWindow homeWindow = new HomeWindow(userId);
                homeWindow.Show();
                this.Close();
                GlobalVoiceCommandHandler.IsUserLoggedIn = true;
            }
            else
            {
                GlassMessageBox.Show("Invalid email or password.");
            }
        }


        private void SignUpTextBlock_Click(object sender, MouseButtonEventArgs e)
        {
            SignUpWindow signup = new SignUpWindow();
            signup.Show();
            this.Close();
        }

        private void BackButton_Click(object sender, RoutedEventArgs e)
        {
            MainWindow main = new MainWindow();
            main.Show();
            this.Close();
        }

        private void ForgotPasswordTextBlock_Click(object sender, MouseButtonEventArgs e)
        {
            ForgotPasswordWindow forgotPasswordWindow = new ForgotPasswordWindow();
            forgotPasswordWindow.ShowDialog();
        }

        private void Window_MouseLeftButtonDown(object sender, MouseButtonEventArgs e)
        {
            if (e.ButtonState == MouseButtonState.Pressed)
                this.DragMove();
        }
    }
}
