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
                var authData = db.GetData($"SELECT COUNT(*) FROM user_authentication_log WHERE UserID={currentUser.UserId}", null);
                VoiceCommandsCard.Text = authData.Rows.Count > 0 ? authData.Rows[0][0].ToString() : "0";
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
        /// Launch a game
        /// </summary>
        /// <param name="game">The game to launch</param>
        private void LaunchGame(GameViewModel game)
        {
            try
            {
                Debug.WriteLine($"[DASHBOARD] Launching game: {game.GameName} (ID: {game.GameId})");

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
