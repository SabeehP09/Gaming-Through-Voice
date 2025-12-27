using GamingThroughVoiceRecognitionSystem.Database;
using GamingThroughVoiceRecognitionSystem.Models;
using System.Collections.Generic;
using System.Linq;
using System.Windows.Controls;

namespace GamingThroughVoiceRecognitionSystem.Views
{
    public partial class VoiceCommandsControl : UserControl
    {
        private readonly UserModel currentUser;
        private readonly DbConn db;

        public VoiceCommandsControl(UserModel user, DbConn database)
        {
            InitializeComponent();
            currentUser = user;
            db = database;

            LoadVoiceCommands();
        }

        private void LoadVoiceCommands()
        {
            // Load system voice commands
            var systemCommands = db.GetSystemVoiceCommands();

            // Load user's game controls
            var userGames = db.GetUserGames(currentUser.UserId);
            var allGameControls = new List<GameControlModel>();

            foreach (var game in userGames)
            {
                var controls = db.GetGameControls(game.GameId, currentUser.UserId);
                allGameControls.AddRange(controls);
            }

            // Group commands by category
            var movementCommands = allGameControls.Where(c => 
                c.ActionName.ToLower().Contains("move") || 
                c.ActionName.ToLower().Contains("jump") ||
                c.ActionName.ToLower().Contains("turn")).ToList();

            var actionCommands = allGameControls.Where(c => 
                c.ActionName.ToLower().Contains("attack") || 
                c.ActionName.ToLower().Contains("shoot") ||
                c.ActionName.ToLower().Contains("reload") ||
                c.ActionName.ToLower().Contains("use")).ToList();

            var navigationCommands = systemCommands.Where(c => 
                c.Action == "Navigate" || 
                c.CommandName.ToLower().Contains("open")).ToList();

            // Update UI with actual command counts
            // You can bind these to ItemsControls or update TextBlocks dynamically
            UpdateCommandDisplay(movementCommands, actionCommands, navigationCommands, systemCommands);
        }

        private void UpdateCommandDisplay(
            List<GameControlModel> movementCommands,
            List<GameControlModel> actionCommands,
            List<SystemVoiceCommand> navigationCommands,
            List<SystemVoiceCommand> systemCommands)
        {
            // Calculate statistics
            int totalGameCommands = movementCommands.Count + actionCommands.Count;
            int totalSystemCommands = systemCommands.Count;
            int totalCommands = totalGameCommands + totalSystemCommands;

            // You can update a progress bar or stats display here
            // For now, the static UI will show the predefined commands
            // In a future update, you can dynamically generate the command cards
        }
    }
}
