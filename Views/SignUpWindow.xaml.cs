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
    public partial class SignUpWindow : Window
    {
        private readonly DbConn db = new DbConn();
        private byte[] capturedFaceData = null;
        private byte[] recordedVoiceData = null;

        public SignUpWindow()
        {
            InitializeComponent();
        }

        // ---------------------------------------------------------
        // WINDOW EVENTS
        // ---------------------------------------------------------
        private void Window_Loaded(object sender, RoutedEventArgs e)
        {
            // Start animated gradient background
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
        private void NameTextBox_GotFocus(object sender, RoutedEventArgs e)
        {
            if (NameTextBox.Text == "Full Name")
            {
                NameTextBox.Text = "";
                NameTextBox.Foreground = Brushes.White;
            }
        }

        private void NameTextBox_LostFocus(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrWhiteSpace(NameTextBox.Text))
            {
                NameTextBox.Text = "Full Name";
                NameTextBox.Foreground = Brushes.Gray;
            }
        }

        private void AgeTextBox_GotFocus(object sender, RoutedEventArgs e)
        {
            if (AgeTextBox.Text == "Age")
            {
                AgeTextBox.Text = "";
                AgeTextBox.Foreground = Brushes.White;
            }
        }

        private void AgeTextBox_LostFocus(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrWhiteSpace(AgeTextBox.Text))
            {
                AgeTextBox.Text = "Age";
                AgeTextBox.Foreground = Brushes.Gray;
            }
        }

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
        private async void FaceRegisterButton_Click(object sender, MouseButtonEventArgs e)
        {
            FaceRecognitionService_OpenCV faceService = null;
            Window checkingMsg = null;
            
            try
            {
                // Show checking message
                checkingMsg = GlassMessageBox.ShowProcessing("🔍 Checking face recognition availability...");
                
                // Initialize face recognition service
                faceService = new FaceRecognitionService_OpenCV();
                
                // Check server health and webcam in parallel for faster response
                var serverHealthTask = faceService.CheckServerHealthAsync(forceCheck: true);
                var webcamStatusTask = Task.Run(() => faceService.GetWebcamStatus());
                
                await Task.WhenAll(serverHealthTask, webcamStatusTask);
                
                bool serverHealthy = await serverHealthTask;
                var webcamStatus = await webcamStatusTask;
                
                checkingMsg?.Close();
                
                if (!serverHealthy)
                {
                    GlassMessageBox.ShowError(
                        "🔴 Face recognition server is offline.\n\n" +
                        "✅ You can still sign up with password.\n" +
                        "📸 Add face later from your profile.\n\n" +
                        "To start server:\nFaceRecognition\\opencv_server\\start_opencv_server.bat"
                    );
                    return;
                }
                
                if (!webcamStatus.available)
                {
                    GlassMessageBox.ShowError(
                        "📷 " + webcamStatus.message + "\n\n" +
                        "✅ You can still sign up with password.\n" +
                        "📸 Add face later from your profile."
                    );
                    return;
                }
                
                // Mark that user wants to register face
                capturedFaceData = new byte[] { 1 }; // Placeholder
                
                FaceStatusIcon.Text = "✅";
                FaceStatusText.Text = "Ready!";
                FaceStatusText.Foreground = new SolidColorBrush(Color.FromRgb(34, 197, 94));
                
                GlassMessageBox.ShowSuccess("✅ Face registration ready!\n\n📝 Complete the form and click 'Sign Up'.\n📸 We'll capture your face during signup.", autoDismiss: true);
            }
            catch (Exception ex)
            {
                checkingMsg?.Close();
                FaceStatusIcon.Text = "📷";
                FaceStatusText.Text = "Not captured";
                FaceStatusText.Foreground = new SolidColorBrush(Color.FromRgb(156, 163, 175));
                System.Diagnostics.Debug.WriteLine($"Face check error: {ex.Message}");
                GlassMessageBox.ShowError(
                    $"❌ Face check failed: {ex.Message}\n\n" +
                    "✅ You can still sign up with password."
                );
            }
            finally
            {
                faceService?.Dispose();
            }
        }

        private void VoiceRegisterButton_Click(object sender, MouseButtonEventArgs e)
        {
            try
            {
                var voiceRecordingWindow = new VoiceRecordingWindow();
                bool? result = voiceRecordingWindow.ShowDialog();

                if (result == true && voiceRecordingWindow.IsRecorded && voiceRecordingWindow.RecordedVoiceData != null)
                {
                    recordedVoiceData = voiceRecordingWindow.RecordedVoiceData;
                    System.Diagnostics.Debug.WriteLine($"Audio size: {recordedVoiceData.Length} bytes");
                    VoiceStatusIcon.Text = "✅";
                    VoiceStatusText.Text = "Recorded!";
                    VoiceStatusText.Foreground = new SolidColorBrush(Color.FromRgb(34, 197, 94)); // Green
                    GlassMessageBox.Show("Voice recorded successfully!");
                }
            }
            catch (Exception ex)
            {
                GlassMessageBox.Show($"Voice recording error: {ex.Message}");
            }
        }

        private async void SignupButton_Click(object sender, RoutedEventArgs e)
        {
            FaceRecognitionService_OpenCV faceService = null;
            
            string name = (NameTextBox.Text == "Full Name") ? "" : NameTextBox.Text.Trim();
            string ageText = (AgeTextBox.Text == "Age") ? "" : AgeTextBox.Text.Trim();
            string email = (EmailTextBox.Text == "Email") ? "" : EmailTextBox.Text.Trim();
            string password = PasswordBox.Password.Trim();

            if (string.IsNullOrEmpty(name) || string.IsNullOrEmpty(ageText) ||
                string.IsNullOrEmpty(email) || string.IsNullOrEmpty(password))
            {
                GlassMessageBox.Show("Please fill all fields.");
                return;
            }

            if (!int.TryParse(ageText, out int age))
            {
                GlassMessageBox.Show("Please enter a valid age.");
                return;
            }

            bool success = db.SignUp(name, age, email, password);
            if (success)
            {
                // Get the newly created user ID
                if (db.Login(email, password, out int userId))
                {
                    // Register face with OpenCV if user clicked face registration
                    // Requirements: 8.1, 8.2, 8.5
                    if (capturedFaceData != null)
                    {
                        try
                        {
                            // Open face registration window with webcam preview
                            var faceRegWindow = new FaceRegistrationWindow(userId);
                            bool? result = faceRegWindow.ShowDialog();
                            
                            if (result == true && faceRegWindow.IsRegistered)
                            {
                                FaceStatusIcon.Text = "✅";
                                FaceStatusText.Text = "Registered!";
                                FaceStatusText.Foreground = new SolidColorBrush(Color.FromRgb(34, 197, 94)); // Green
                                System.Diagnostics.Debug.WriteLine($"✓ Face registered successfully");
                            }
                            else
                            {
                                System.Diagnostics.Debug.WriteLine($"[Signup] Face registration failed: {faceRegWindow.ResultMessage}");
                                FaceStatusIcon.Text = "⚠️";
                                FaceStatusText.Text = "Failed";
                                FaceStatusText.Foreground = new SolidColorBrush(Color.FromRgb(239, 68, 68)); // Red
                                
                                // Don't show error popup - account was created successfully
                                // User can add face later from profile
                                System.Diagnostics.Debug.WriteLine("[Signup] Account created, face registration can be done later");
                            }
                        }
                        catch (Exception ex)
                        {
                            System.Diagnostics.Debug.WriteLine($"Face registration error: {ex.Message}");
                            FaceStatusIcon.Text = "⚠️";
                            FaceStatusText.Text = "Error";
                            FaceStatusText.Foreground = new SolidColorBrush(Color.FromRgb(239, 68, 68)); // Red
                            GlassMessageBox.ShowError(
                                $"⚠️ Face registration error: {ex.Message}\n\n" +
                                "Your account has been created successfully.\n" +
                                "You can login with email/password.\n" +
                                "Face registration can be done later from your profile."
                            );
                        }
                    }
                    
                    // Store voice data in database (legacy)
                    if (recordedVoiceData != null)
                    {
                        db.StoreVoiceData(userId, recordedVoiceData);
                    }

                    // Enroll voice in Python backend if voice data exists
                    if (recordedVoiceData != null)
                    {
                        try
                        {
                            var voiceService = new VoiceRecognitionService();
                            bool isHealthy = await voiceService.IsBackendHealthyAsync();
                            
                            if (isHealthy)
                            {
                                System.Diagnostics.Debug.WriteLine($"Enrolling user {userId} with voice data length: {recordedVoiceData.Length}");
                                
                                bool enrolled = await voiceService.EnrollUserAsync(userId, recordedVoiceData);
                                
                                System.Diagnostics.Debug.WriteLine($"Enrollment result: {enrolled}");
                                
                                if (!enrolled)
                                {
                                    System.Diagnostics.Debug.WriteLine("⚠️ Voice enrollment failed");
                                }
                                else
                                {
                                    System.Diagnostics.Debug.WriteLine($"✓ User {userId} enrolled successfully in Python backend");
                                    VoiceStatusIcon.Text = "✅";
                                    VoiceStatusText.Text = "Enrolled!";
                                    VoiceStatusText.Foreground = new SolidColorBrush(Color.FromRgb(34, 197, 94));
                                }
                            }
                            else
                            {
                                System.Diagnostics.Debug.WriteLine("⚠️ Voice backend not running");
                            }
                        }
                        catch (Exception ex)
                        {
                            System.Diagnostics.Debug.WriteLine($"Voice enrollment error: {ex.Message}");
                        }
                    }
                }

                // Build success message with registered features
                string successMsg = "✅ Account created successfully!\n\n";
                
                if (capturedFaceData != null && recordedVoiceData != null)
                {
                    successMsg += "📸 Face registered\n🎤 Voice registered\n\n";
                }
                else if (capturedFaceData != null)
                {
                    successMsg += "📸 Face registered\n\n";
                }
                else if (recordedVoiceData != null)
                {
                    successMsg += "🎤 Voice registered\n\n";
                }
                
                successMsg += "🔐 You can now login!";

                GlassMessageBox.ShowSuccess(successMsg, autoDismiss: true);
                
                // Wait for auto-dismiss
                await Task.Delay(2000);
                
                LoginWindow login = new LoginWindow();
                login.Show();
                this.Close();
            }
            else
            {
                GlassMessageBox.Show("Signup failed. Email might already exist or database error.");
            }
        }

        private void LoginTextBlock_Click(object sender, MouseButtonEventArgs e)
        {
            LoginWindow login = new LoginWindow();
            login.Show();
            this.Close();
        }

        private void BackButton_Click(object sender, RoutedEventArgs e)
        {
            MainWindow main = new MainWindow();
            main.Show();
            this.Close();
        }

        private void Window_MouseLeftButtonDown(object sender, MouseButtonEventArgs e)
        {
            if (e.ButtonState == MouseButtonState.Pressed)
                this.DragMove();
        }
    }
}
