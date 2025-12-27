using GamingThroughVoiceRecognitionSystem.Database;
using System;
using System.Windows;
using System.Windows.Input;

namespace GamingThroughVoiceRecognitionSystem.Views
{
    public partial class ForgotPasswordWindow : Window
    {
        private readonly DbConn db;

        public ForgotPasswordWindow()
        {
            InitializeComponent();
            db = new DbConn();
        }

        private void Window_MouseLeftButtonDown(object sender, MouseButtonEventArgs e)
        {
            if (e.ButtonState == MouseButtonState.Pressed)
                this.DragMove();
        }

        private void ResetButton_Click(object sender, RoutedEventArgs e)
        {
            string email = EmailTextBox.Text.Trim();
            string newPassword = NewPasswordBox.Password;
            string confirmPassword = ConfirmPasswordBox.Password;

            // Validation
            if (string.IsNullOrWhiteSpace(email))
            {
                GlassMessageBox.Show("Please enter your email address.");
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
                GlassMessageBox.Show("Passwords do not match.");
                return;
            }

            // Check if email exists
            if (!db.EmailExists(email))
            {
                GlassMessageBox.Show("Email address not found.");
                return;
            }

            // Reset password
            try
            {
                if (db.ResetPasswordByEmail(email, newPassword))
                {
                    GlassMessageBox.Show("Password reset successfully! You can now login with your new password.");
                    DialogResult = true;
                    Close();
                }
                else
                {
                    GlassMessageBox.Show("Failed to reset password. Please try again.");
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
    }
}
