using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace GamingThroughVoiceRecognitionSystem.Models
{
    public class UserModel
    {
        public int UserId { get; set; }
        public string FullName { get; set; }
        public int Age { get; set; }
        public string Email { get; set; }
        public string PasswordHash { get; set; }
        public int GamePlayed { get; set; }
        public int TotalVoiceCommands { get; set; }
        public int HoursPlayed { get; set; }
        public int VoiceTrainingProgress { get; set; }
    }
}
