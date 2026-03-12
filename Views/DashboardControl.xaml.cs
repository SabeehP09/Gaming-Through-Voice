using GamingThroughVoiceRecognitionSystem.Database;
using GamingThroughVoiceRecognitionSystem.Models;
using GamingThroughVoiceRecognitionSystem.Services;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Windows;
using System.Windows.Controls;

namespace GamingThroughVoiceRecognitionSystem.Views
{
    public class GameViewModel
    {
        public int GameId { get; set; }
        public string GameName { get; set; }
        public string FilePath { get; set; }
        public string IconPath { get; set; }
        public bool IsDefault { get; set; }
        public List<GameControlModel> Controls { get; set; }
    }

    public partial class DashboardControl : UserControl
    {
        private readonly UserModel currentUser;
        private readonly DbConn db;

        public DashboardControl(UserModel user, DbConn database)
        {
            InitializeComponent();
            currentUser = user;
            db = database;

            LoadData();
        }

        private void LoadData()
        {
            WelcomeText.Text = $"WELCOME BACK, {currentUser.FullName.Split(' ')[0].ToUpper()}! 🎮";
            LoadStats();
            LoadGames();
        }

        private void LoadStats()
        {
            try
            {
                var gamesPlayedData = db.GetData($"SELECT COUNT(*) FROM user_game_history WHERE UserID={currentUser.UserId}", null);
                GamesPlayedCard.Text = gamesPlayedData.Rows.Count > 0 ? gamesPlayedData.Rows[0][0].ToString() : "0";
            }
            catch
            {
                GamesPlayedCard.Text = "0";
            }

            try
            {
                var voiceCommandsData = db.GetData($"SELECT COUNT(*) FROM user_voice_history WHERE UserID={currentUser.UserId}", null);
                VoiceCommandsCard.Text = voiceCommandsData.Rows.Count > 0 ? voiceCommandsData.Rows[0][0].ToString() : "0";
            }
            catch
            {
                VoiceCommandsCard.Text = "0";
            }

            try
            {
                var hoursPlayedData = db.GetData($"SELECT ISNULL(SUM(Duration), 0) FROM user_game_history WHERE UserID={currentUser.UserId}", null);
                HoursPlayedCard.Text = hoursPlayedData.Rows.Count > 0 ? hoursPlayedData.Rows[0][0].ToString() : "0";
            }
            catch
            {
                HoursPlayedCard.Text = "0";
            }
        }

        private void LoadGames()
        {
            List<GameModel> games = db.GetUserGames(currentUser.UserId);
            
            // Create view models with controls
            var gameViewModels = games.Select(g => new GameViewModel
            {
                GameId = g.GameId,
                GameName = g.GameName,
                FilePath = g.FilePath,
                IconPath = g.IconPath,
                IsDefault = g.IsDefault,
                Controls = db.GetGameControls(g.GameId, currentUser.UserId)
            }).ToList();

            GamesGrid.ItemsSource = gameViewModels;
        }

        private void AddGame_Click(object sender, RoutedEventArgs e)
        {
            AddGameWindow addGameWindow = new AddGameWindow(currentUser, db);
            if (addGameWindow.ShowDialog() == true)
            {
                LoadGames();
            }
        }

        private void PlayGame_Click(object sender, RoutedEventArgs e)
        {
            if (sender is Button button && button.Tag is GameViewModel game)
            {
                LaunchGame(game);
            }
        }

        /// <summary>
        /// Launch a game by name (for voice commands)
        /// </summary>
        /// <param name="gameName">The name of the game to launch</param>
        public void LaunchGameByName(string gameName)
        {
            try
            {
                Debug.WriteLine($"[DASHBOARD] Attempting to launch game by name: {gameName}");
                
                // Find the game in the current games list
                var games = GamesGrid.ItemsSource as List<GameViewModel>;
                if (games == null)
                {
                    Debug.WriteLine("[DASHBOARD] No games loaded");
                    GlassMessageBox.Show("No games available. Please add games first.");
                    return;
                }

                // Try exact match first, then partial match
                var game = games.FirstOrDefault(g => 
                    g.GameName.Equals(gameName, StringComparison.OrdinalIgnoreCase));
                
                // If not found, try partial match (e.g., "Mr Racer" matches "Mr Racer (Voice Controlled)")
                if (game == null)
                {
                    game = games.FirstOrDefault(g => 
                        g.GameName.IndexOf(gameName, StringComparison.OrdinalIgnoreCase) >= 0);
                }

                if (game != null)
                {
                    Debug.WriteLine($"[DASHBOARD] Found game: {game.GameName}");
                    LaunchGame(game);
                }
                else
                {
                    Debug.WriteLine($"[DASHBOARD] Game not found: {gameName}");
                    GlassMessageBox.Show($"Game '{gameName}' not found. Please add it first.");
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[DASHBOARD] ERROR launching game by name: {ex.Message}");
                GlassMessageBox.Show($"Failed to launch game: {ex.Message}");
            }
        }

        /// <summary>
        /// Launch a game by its position number (for voice commands like "open game 1")
        /// </summary>
        /// <param name="gameNumber">The game number (1-based index)</param>
        public void LaunchGameByNumber(int gameNumber)
        {
            try
            {
                Debug.WriteLine($"[DASHBOARD] Attempting to launch game #{gameNumber}");
                
                // Find the game in the current games list
                var games = GamesGrid.ItemsSource as List<GameViewModel>;
                if (games == null || games.Count == 0)
                {
                    Debug.WriteLine("[DASHBOARD] No games loaded");
                    GlassMessageBox.Show("No games available. Please add games first.");
                    return;
                }

                // Convert to 0-based index
                int index = gameNumber - 1;
                
                if (index < 0 || index >= games.Count)
                {
                    Debug.WriteLine($"[DASHBOARD] Game #{gameNumber} not found (only {games.Count} games available)");
                    GlassMessageBox.Show($"Game #{gameNumber} not found. You have {games.Count} game(s).");
                    return;
                }

                var game = games[index];
                Debug.WriteLine($"[DASHBOARD] Found game #{gameNumber}: {game.GameName}");
                LaunchGame(game);
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[DASHBOARD] ERROR launching game by number: {ex.Message}");
                GlassMessageBox.Show($"Failed to launch game: {ex.Message}");
            }
        }

        /// <summary>
        /// Launch a game
        /// </summary>
        /// <param name="game">The game to launch</param>
        private void LaunchGame(GameViewModel game)
        {
            try
            {
                Debug.WriteLine($"[DASHBOARD] Launching game: {game.GameName} (ID: {game.GameId})");

                // Check if this is a voice-controlled game
                if (game.GameName.IndexOf("Voice Controlled", StringComparison.OrdinalIgnoreCase) >= 0 || 
                    game.GameName.IndexOf("Mr Racer", StringComparison.OrdinalIgnoreCase) >= 0 ||
                    game.GameName.IndexOf("Subway Surfers", StringComparison.OrdinalIgnoreCase) >= 0)
                {
                    Debug.WriteLine($"[DASHBOARD] Launching voice-controlled game: {game.GameName}");
                    var voiceGameController = new VoiceGameController(game.GameName);
                    
                    if (!voiceGameController.CheckDependencies())
                    {
                        GlassMessageBox.ShowError("❌ Python not found\n\nPlease install Python 3.8+ to play voice-controlled games.");
                        return;
                    }
                    
                    bool launched = voiceGameController.LaunchVoiceGame(autoLaunch: true);
                    if (launched)
                    {
                        GlassMessageBox.ShowSuccess(
                            $"🎮 {game.GameName} Launching...\n\n" +
                            "🎤 Voice control ready for gameplay\n" +
                            "📢 App voice control is paused\n" +
                            "✅ Will auto-resume when you exit the game", 
                            autoDismiss: true);
                    }
                    else
                    {
                        GlassMessageBox.ShowError("❌ Failed to start voice controller\n\nCheck that Python and dependencies are installed.");
                    }
                    return;
                }

                // Regular game launch
                if (string.IsNullOrEmpty(game.FilePath) || !File.Exists(game.FilePath))
                {
                    Debug.WriteLine($"[DASHBOARD] Game executable not found: {game.FilePath}");
                    GlassMessageBox.ShowError("Game executable not found.\n\nPlease check the game path.");
                    return;
                }

                // Launch the game process
                Process gameProcess = Process.Start(game.FilePath);
                
                if (gameProcess != null)
                {
                    Debug.WriteLine($"[DASHBOARD] Game process started (PID: {gameProcess.Id})");
                    GlassMessageBox.ShowSuccess($"✅ Launching {game.GameName}...", autoDismiss: true);
                }
                else
                {
                    Debug.WriteLine($"[DASHBOARD] Failed to start game process");
                    GlassMessageBox.ShowError($"Failed to launch {game.GameName}");
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[DASHBOARD] ERROR launching game: {ex.Message}");
                Debug.WriteLine($"[DASHBOARD] Stack trace: {ex.StackTrace}");
                GlassMessageBox.ShowError($"Failed to launch game:\n\n{ex.Message}");
            }
        }

        private void EditGame_Click(object sender, RoutedEventArgs e)
        {
            if (sender is Button button && button.Tag is GameViewModel gameVM)
            {
                GameModel game = new GameModel
                {
                    GameId = gameVM.GameId,
                    GameName = gameVM.GameName,
                    FilePath = gameVM.FilePath,
                    IconPath = gameVM.IconPath,
                    UserId = currentUser.UserId,
                    IsDefault = gameVM.IsDefault
                };

                AddGameWindow editGameWindow = new AddGameWindow(currentUser, db, game);
                if (editGameWindow.ShowDialog() == true)
                {
                    LoadGames();
                }
            }
        }

        private void DeleteGame_Click(object sender, RoutedEventArgs e)
        {
            if (sender is Button button && button.Tag is GameViewModel game)
            {
                if (game.IsDefault)
                {
                    GlassMessageBox.Show("Cannot delete default games.");
                    return;
                }

                // Simple confirmation - just delete
                if (db.DeleteGame(game.GameId, currentUser.UserId))
                {
                    GlassMessageBox.Show("Game deleted successfully!");
                    LoadGames();
                }
                else
                {
                    GlassMessageBox.Show("Failed to delete game.");
                }
            }
        }
    }
}
