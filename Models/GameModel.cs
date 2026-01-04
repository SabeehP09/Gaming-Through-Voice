using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace GamingThroughVoiceRecognitionSystem.Models
{
    public class GameModel
    {
        public int GameId { get; set; }
        public string GameName { get; set; }
        public string FilePath { get; set; }
        public string IconPath { get; set; }
        public int UserId { get; set; }
        public bool IsDefault { get; set; }
        public DateTime DateAdded { get; set; }
    }

    public class GameControlModel
    {
        public int ControlId { get; set; }
        public int GameId { get; set; }
        public int UserId { get; set; }
        public string ActionName { get; set; }
        public string KeyBinding { get; set; }
    }


}
