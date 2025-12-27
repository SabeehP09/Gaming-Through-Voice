using GamingThroughVoiceRecognitionSystem.Database;
using GamingThroughVoiceRecognitionSystem.Models;
using GamingThroughVoiceRecognitionSystem.Services;
using System;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;

namespace GamingThroughVoiceRecognitionSystem.Views
{
    public partial class EditProfileWindow : Window
    {
        private readonly DbConn db;
        private readonly UserModel currentUser;
        private string loginMethod; // "Manual", "Face", "Voice"

        public EditProfileWindow(UserModel user)
        {
            InitializeComponent();
            db = new DbConn();
            currentUser = user;

            DetermineLoginMethod();
            ShowAppropriateSection();
        }

        private void DetermineLoginMethod()
        {
            // Check if user has face data
            byte[] faceData = db.GetUserFaceData(currentUser.UserId);
            
            // Check if user has voice data (we'll need to add a method for this)
            // For now, we'll check if they have a password
            
            if (faceData != null && faceData.Length > 0)
            {
                loginMethod = "Face";
            }
            else
            {
                // Default to manual for now
                // In a full implementation, you'd check for voice data too
                loginMethod = "Manual";
            }

            LoginMethodText.Text = $"Login Method: {loginMethod}";
        }

        private void ShowAppropriateSection()
        {
            // Hide all sections first
            ManualLoginSection.Visibility = Visibility.Collapsed;
            FaceRecognitionSection.Visibility = Visibility.Collapsed;
            VoiceRecognitionSection.Visibility = Visibility.Collapsed;

            // Show appropriate section
            switch (loginMethod)
            {
                case "Manual":
                    ManualLoginSection.Visibility = Visibility.Visible;
                    break;
                case "Face":
                    FaceRecognitionSection.Visibility = Visibility.Visible;
                    break;
                case "Voice":
                    VoiceRecognitionSection.Visibility = Visibility.Visible;
                    break;
            }
        }

        private void SaveButton_Click(object sender, RoutedEventArgs e)
        {
            switch (loginMethod)
            {
                case "Manual":
                    ChangePassword();
                    break;
                case "Face":
                    // Face capture is handled by CaptureFaceButton_Click
                    GlassMessageBox.Show("Please use the 'Capture New Face' button to update your face data.");
                    break;
                case "Voice":
                    // Voice recording is handled by RecordVoiceButton_Click
                    GlassMessageBox.Show("Please use the 'Record New Voice' button to update your voice data.");
                    break;
            }
        }

        private void ChangePassword()
        {
            string currentPassword = CurrentPasswordBox.Password;
            string newPassword = NewPasswordBox.Password;
            string confirmPassword = ConfirmPasswordBox.Password;

            // Validation
            if (string.IsNullOrWhiteSpace(currentPassword))
            {
                GlassMessageBox.Show("Please enter your current password.");
                return;
            }

            if (string.IsNullOrWhiteSpace(newPassword))
            {
                GlassMessageBox.Show("Please enter a new password.");
                return;
            }

            if (newPassword.Length < 6)
            {
                GlassMessageBox.Show("Password must be at least 6 characters long.");
                return;
            }

            if (newPassword != confirmPassword)
            {
                GlassMessageBox.Show("New passwords do not match.");
                return;
            }

            // Verify current password
            if (!db.VerifyPassword(currentUser.UserId, currentPassword))
            {
                GlassMessageBox.Show("Current password is incorrect.");
                return;
            }

            // Update password
            try
            {
                if (db.UpdatePassword(currentUser.UserId, newPassword))
                {
                    GlassMessageBox.Show("Password changed successfully!");
                    DialogResult = true;
                    Close();
                }
                else
                {
                    GlassMessageBox.Show("Failed to change password. Please try again.");
                }
            }
            catch (Exception ex)
            {
                GlassMessageBox.Show($"Error: {ex.Message}");
            }
        }

        private void CaptureFaceButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var faceCaptureWindow = new FaceCaptureWindow();
                bool? result = faceCaptureWindow.ShowDialog();

                if (result == true && faceCaptureWindow.IsCaptured && faceCaptureWindow.CapturedFaceData != null)
                {
                    // Update face data
                    if (db.UpdateUserFaceData(currentUser.UserId, faceCaptureWindow.CapturedFaceData))
                    {
                        GlassMessageBox.Show("Face data updated successfully!");
                        DialogResult = true;
                        Close();
                    }
                    else
                    {
                        GlassMessageBox.Show("Failed to update face data. Please try again.");
                    }
                }
            }
            catch (Exception ex)
            {
                GlassMessageBox.Show($"Error: {ex.Message}");
            }
        }

        private async void RecordVoiceButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var voiceService = new VoiceRecognitionService();
                
                // Check backend
                bool isHealthy = await voiceService.IsBackendHealthyAsync();
                if (!isHealthy)
                {
                    GlassMessageBox.Show("Voice backend not running.\n\nPlease start: VoiceBackend\\start_server_no_mic.bat");
                    return;
                }
                
                var voiceRecordingWindow = new VoiceRecordingWindow();
                bool? result = voiceRecordingWindow.ShowDialog();

                if (result == true && voiceRecordingWindow.IsRecorded && voiceRecordingWindow.RecordedVoiceData != null)
                {
                    GlassMessageBox.Show("🎤 Updating your voice profile...");
                    
                    // Delete old voice model from Python backend
                    await voiceService.DeleteUserVoiceAsync(currentUser.UserId);
                    
                    // Enroll new voice in Python backend
                    bool enrolled = await voiceService.EnrollUserAsync(
                        currentUser.UserId, 
                        voiceRecordingWindow.RecordedVoiceData
                    );
                    
                    // Update database
                    bool dbUpdated = db.UpdateUserVoiceData(currentUser.UserId, voiceRecordingWindow.RecordedVoiceData);
                    
                    if (enrolled && dbUpdated)
                    {
                        GlassMessageBox.Show("✓ Voice profile updated successfully!");
                        DialogResult = true;
                        Close();
                    }
                    else if (dbUpdated)
                    {
                        GlassMessageBox.Show("⚠️ Voice data saved but enrollment failed.\nYou may need to re-enroll.");
                        DialogResult = true;
                        Close();
                    }
                    else
                    {
                        GlassMessageBox.Show("✗ Failed to update voice data. Please try again.");
                    }
                }
            }
            catch (Exception ex)
            {
                GlassMessageBox.Show($"Error: {ex.Message}");
            }
        }

        private void CloseButton_Click(object sender, RoutedEventArgs e)
        {
            Close();
        }

        private void Window_MouseLeftButtonDown(object sender, MouseButtonEventArgs e)
        {
            if (e.ButtonState == MouseButtonState.Pressed)
                this.DragMove();
        }
    }
}
