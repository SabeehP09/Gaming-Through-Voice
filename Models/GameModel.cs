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
        public string VoiceCommand { get; set; }
        public string KeyBinding { get; set; }
    }

    public class GameVoiceCommand
    {
        public int CommandId { get; set; }
        public int GameId { get; set; }
        public string VoiceCommand { get; set; }
        public string KeyBinding { get; set; }
        public bool IsEnabled { get; set; }
        public DateTime CreatedDate { get; set; }
    }

    public class GameVoiceConfig
    {
        public int GameId { get; set; }
        public string GameName { get; set; }
        public bool VoiceControlEnabled { get; set; }
        public string GrammarFile { get; set; }
        public string DictionaryFile { get; set; }
        public List<GameVoiceCommand> Commands { get; set; }
    }
}
