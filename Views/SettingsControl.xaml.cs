using GamingThroughVoiceRecognitionSystem.Database;
using GamingThroughVoiceRecognitionSystem.Models;
using GamingThroughVoiceRecognitionSystem.Services;
using System;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Animation;

namespace GamingThroughVoiceRecognitionSystem.Views
{
    public partial class SettingsControl : UserControl
    {
        private readonly UserModel currentUser;
        private readonly DbConn db;
        private UserSettings currentSettings;

        // UI Controls (we'll reference them by name from XAML)
        private Slider voiceSensitivitySlider;
        private CheckBox enableVoiceCommandsCheckBox;
        private CheckBox noiseCancellationCheckBox;
        private CheckBox voiceFeedbackCheckBox;
        private Slider masterVolumeSlider;
        private Slider voiceVolumeSlider;
        private Slider effectsVolumeSlider;
        private CheckBox autoSaveCheckBox;
        private CheckBox showTutorialsCheckBox;
        private CheckBox enableAchievementsCheckBox;
        private CheckBox fullscreenCheckBox;
        private CheckBox saveVoiceDataCheckBox;
        private CheckBox shareStatsCheckBox;
        private CheckBox allowRecordingsCheckBox;

        public SettingsControl(UserModel user, DbConn database)
        {
            InitializeComponent();
            currentUser = user;
            db = database;

            // Find controls after InitializeComponent
            FindControls();

            // Load settings from database
            LoadSettings();

            // Set initial toggle state
            UpdateToggleUI(ThemeManager.CurrentTheme == AppTheme.Dark);
        }

        private void FindControls()
        {
            // Find all controls by traversing the visual tree
            voiceSensitivitySlider = FindName("VoiceSensitivitySlider") as Slider;
            enableVoiceCommandsCheckBox = FindName("EnableVoiceCommandsCheckBox") as CheckBox;
            noiseCancellationCheckBox = FindName("NoiseCancellationCheckBox") as CheckBox;
            voiceFeedbackCheckBox = FindName("VoiceFeedbackCheckBox") as CheckBox;
            masterVolumeSlider = FindName("MasterVolumeSlider") as Slider;
            voiceVolumeSlider = FindName("VoiceVolumeSlider") as Slider;
            effectsVolumeSlider = FindName("EffectsVolumeSlider") as Slider;
            autoSaveCheckBox = FindName("AutoSaveCheckBox") as CheckBox;
            showTutorialsCheckBox = FindName("ShowTutorialsCheckBox") as CheckBox;
            enableAchievementsCheckBox = FindName("EnableAchievementsCheckBox") as CheckBox;
            fullscreenCheckBox = FindName("FullscreenCheckBox") as CheckBox;
            saveVoiceDataCheckBox = FindName("SaveVoiceDataCheckBox") as CheckBox;
            shareStatsCheckBox = FindName("ShareStatsCheckBox") as CheckBox;
            allowRecordingsCheckBox = FindName("AllowRecordingsCheckBox") as CheckBox;
        }

        private void LoadSettings()
        {
            // Get settings from database
            currentSettings = db.GetUserSettings(currentUser.UserId);

            // If no settings exist, create default ones
            if (currentSettings == null)
            {
                db.CreateDefaultSettings(currentUser.UserId);
                currentSettings = db.GetUserSettings(currentUser.UserId);
            }

            if (currentSettings != null)
            {
                // Apply settings to UI
                if (voiceSensitivitySlider != null)
                    voiceSensitivitySlider.Value = currentSettings.MicrophoneSensitivity;

                if (enableVoiceCommandsCheckBox != null)
                    enableVoiceCommandsCheckBox.IsChecked = currentSettings.VoiceRecognitionEnabled;

                // Set theme
                bool isDark = currentSettings.Theme == "Dark";
                ThemeManager.CurrentTheme = isDark ? AppTheme.Dark : AppTheme.Light;
                UpdateToggleUI(isDark);
            }
        }

        private void ThemeToggle_Click(object sender, MouseButtonEventArgs e)
        {
            // Toggle theme
            bool isDark = ThemeManager.CurrentTheme == AppTheme.Light;
            
            // Update theme for current user only
            ThemeManager.CurrentTheme = isDark ? AppTheme.Dark : AppTheme.Light;
            
            // Update settings object (will be saved to database when user clicks Save)
            if (currentSettings != null)
            {
                currentSettings.Theme = isDark ? "Dark" : "Light";
            }
            
            // Animate toggle
            UpdateToggleUI(isDark);
        }

        private void UpdateToggleUI(bool isDark)
        {
            // Animate the toggle circle
            var animation = new ThicknessAnimation
            {
                Duration = TimeSpan.FromMilliseconds(200),
                EasingFunction = new CubicEase { EasingMode = EasingMode.EaseOut }
            };

            if (isDark)
            {
                // Move to right (Dark mode)
                animation.To = new Thickness(0, 0, 5, 0);
                ToggleCircle.HorizontalAlignment = HorizontalAlignment.Right;
                LightIcon.Opacity = 0.3;
                DarkIcon.Opacity = 1.0;
            }
            else
            {
                // Move to left (Light mode)
                animation.To = new Thickness(5, 0, 0, 0);
                ToggleCircle.HorizontalAlignment = HorizontalAlignment.Left;
                LightIcon.Opacity = 1.0;
                DarkIcon.Opacity = 0.3;
            }

            ToggleCircle.BeginAnimation(MarginProperty, animation);
        }

        private void SaveSettings_Click(object sender, RoutedEventArgs e)
        {
            if (currentSettings == null)
            {
                GlassMessageBox.Show("Error loading settings. Please try again.");
                return;
            }

            try
            {
                // Update settings from UI
                if (voiceSensitivitySlider != null)
                    currentSettings.MicrophoneSensitivity = (int)voiceSensitivitySlider.Value;

                if (enableVoiceCommandsCheckBox != null)
                    currentSettings.VoiceRecognitionEnabled = enableVoiceCommandsCheckBox.IsChecked ?? true;

                // Ensure theme is set correctly for this user
                currentSettings.Theme = ThemeManager.CurrentTheme == AppTheme.Dark ? "Dark" : "Light";

                // Save to database (user-specific)
                if (db.UpdateUserSettings(currentSettings))
                {
                    // Re-initialize theme for this user to ensure it's applied
                    ThemeManager.InitializeForUser(currentUser.UserId, currentSettings.Theme);
                    
                    GlassMessageBox.Show("Settings saved successfully!");
                }
                else
                {
                    GlassMessageBox.Show("Failed to save settings. Please try again.");
                }
            }
            catch (Exception ex)
            {
                GlassMessageBox.Show($"Error saving settings: {ex.Message}");
            }
        }
    }
}
