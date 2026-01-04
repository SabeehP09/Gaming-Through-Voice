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
        public bool AutoLaunchGames { get; set; }
        public bool ShowNotifications { get; set; }
        public string Language { get; set; }
        public DateTime UpdatedAt { get; set; }
    }
}
