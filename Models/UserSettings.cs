using System;

namespace GamingThroughVoiceRecognitionSystem.Models
{
    public class UserSettings
    {
        public int SettingID { get; set; }
        public int UserID { get; set; }
        public string Theme { get; set; }
        public bool VoiceRecognitionEnabled { get; set; }
        public bool FaceRecognitionEnabled { get; set; }
        public int MicrophoneSensitivity { get; set; }
        public int VoiceCommandTimeout { get; set; }
        public bool AutoLaunchGames { get; set; }
        public bool ShowNotifications { get; set; }
        public string Language { get; set; }
        public DateTime UpdatedAt { get; set; }
    }

    public class SystemVoiceCommand
    {
        public int CommandID { get; set; }
        public string CommandName { get; set; }
        public string VoiceCommand { get; set; }
        public string Action { get; set; }
        public string Target { get; set; }
        public bool IsEnabled { get; set; }
        public DateTime CreatedAt { get; set; }
    }
}
