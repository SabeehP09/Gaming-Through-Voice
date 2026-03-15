using GamingThroughVoiceRecognitionSystem.Database;
using GamingThroughVoiceRecognitionSystem.Models;
using Microsoft.Win32;
using System;
using System.Collections.ObjectModel;
using System.IO;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media.Imaging;

namespace GamingThroughVoiceRecognitionSystem.Views
{
    public partial class AddGameWindow : Window
    {
        private readonly DbConn db;
        private readonly UserModel currentUser;
        private ObservableCollection<GameControlModel> gameControls;
        private GameModel editingGame;

        public AddGameWindow(UserModel user, DbConn database, GameModel gameToEdit = null)
        {
            InitializeComponent();
            db = database;
            currentUser = user;
            editingGame = gameToEdit;

            gameControls = new ObservableCollection<GameControlModel>();
            ControlsItemsControl.ItemsSource = gameControls;

            if (editingGame != null)
            {
                LoadGameData();
            }
        }

        private void LoadGameData()
        {
            GameNameTextBox.Text = editingGame.GameName;
            GamePathTextBox.Text = editingGame.FilePath;
            IconPathTextBox.Text = editingGame.IconPath;

            if (!string.IsNullOrEmpty(editingGame.IconPath) && File.Exists(editingGame.IconPath))
            {
                LoadIconPreview(editingGame.IconPath);
            }

            // Load existing controls
            var controls = db.GetGameControls(editingGame.GameId, currentUser.UserId);
            foreach (var control in controls)
            {
                gameControls.Add(control);
            }
        }

        private void BrowseGamePath_Click(object sender, RoutedEventArgs e)
        {
            OpenFileDialog openFileDialog = new OpenFileDialog
            {
                Filter = "Executable Files (*.exe)|*.exe|All Files (*.*)|*.*",
                Title = "Select Game Executable"
            };

            if (openFileDialog.ShowDialog() == true)
            {
                GamePathTextBox.Text = openFileDialog.FileName;
                
                // Auto-fill game name if empty
                if (string.IsNullOrWhiteSpace(GameNameTextBox.Text))
                {
                    GameNameTextBox.Text = Path.GetFileNameWithoutExtension(openFileDialog.FileName);
                }

                // Try to find icon automatically
                TryAutoDetectIcon(openFileDialog.FileName);
            }
        }

        private void BrowseIconPath_Click(object sender, RoutedEventArgs e)
        {
            OpenFileDialog openFileDialog = new OpenFileDialog
            {
                Filter = "Image Files (*.png;*.jpg;*.jpeg;*.ico)|*.png;*.jpg;*.jpeg;*.ico|All Files (*.*)|*.*",
                Title = "Select Game Icon"
            };

            if (openFileDialog.ShowDialog() == true)
            {
                IconPathTextBox.Text = openFileDialog.FileName;
                LoadIconPreview(openFileDialog.FileName);
            }
        }

        private void TryAutoDetectIcon(string exePath)
        {
            try
            {
                string directory = Path.GetDirectoryName(exePath);
                string gameName = Path.GetFileNameWithoutExtension(exePath);

                // Common icon locations
                string[] possibleIcons = {
                    Path.Combine(directory, $"{gameName}.ico"),
                    Path.Combine(directory, $"{gameName}.png"),
                    Path.Combine(directory, "icon.ico"),
                    Path.Combine(directory, "icon.png"),
                    Path.Combine(directory, "game.ico"),
                    Path.Combine(directory, "game.png")
                };

                foreach (string iconPath in possibleIcons)
                {
                    if (File.Exists(iconPath))
                    {
                        IconPathTextBox.Text = iconPath;
                        LoadIconPreview(iconPath);
                        break;
                    }
                }
            }
            catch { }
        }

        private void LoadIconPreview(string iconPath)
        {
            try
            {
                if (File.Exists(iconPath))
                {
                    BitmapImage bitmap = new BitmapImage();
                    bitmap.BeginInit();
                    bitmap.UriSource = new Uri(iconPath, UriKind.Absolute);
                    bitmap.CacheOption = BitmapCacheOption.OnLoad;
                    bitmap.EndInit();

                    IconPreviewImage.Source = bitmap;
                    IconPreviewBorder.Visibility = Visibility.Visible;
                }
            }
            catch
            {
                IconPreviewBorder.Visibility = Visibility.Collapsed;
            }
        }

        private void AddControl_Click(object sender, RoutedEventArgs e)
        {
            gameControls.Add(new GameControlModel
            {
                GameId = editingGame?.GameId ?? 0,
                UserId = currentUser.UserId,
                ActionName = "",
                VoiceCommand = "",
                KeyBinding = ""
            });
        }

        private void RemoveControl_Click(object sender, RoutedEventArgs e)
        {
            if (sender is Button button && button.Tag is GameControlModel control)
            {
                gameControls.Remove(control);
            }
        }

        private void SaveGame_Click(object sender, RoutedEventArgs e)
        {
            // Validation
            if (string.IsNullOrWhiteSpace(GameNameTextBox.Text))
            {
                GlassMessageBox.Show("Please enter a game name.");
                return;
            }

            if (string.IsNullOrWhiteSpace(GamePathTextBox.Text))
            {
                GlassMessageBox.Show("Please select a game executable.");
                return;
            }

            if (!File.Exists(GamePathTextBox.Text))
            {
                GlassMessageBox.Show("The selected game executable does not exist.");
                return;
            }

            try
            {
                GameModel game = editingGame ?? new GameModel();
                game.GameName = GameNameTextBox.Text.Trim();
                game.FilePath = GamePathTextBox.Text.Trim();
                game.IconPath = string.IsNullOrWhiteSpace(IconPathTextBox.Text) ? null : IconPathTextBox.Text.Trim();
                game.UserId = currentUser.UserId;
                game.IsDefault = false;

                bool success;
                if (editingGame == null)
                {
                    // Add new game
                    success = db.AddGame(game);
                }
                else
                {
                    // Update existing game
                    success = db.UpdateGame(game);
                }

                if (success)
                {
                    // Save controls
                    if (editingGame != null)
                    {
                        // Delete old controls
                        var existingControls = db.GetGameControls(game.GameId, currentUser.UserId);
                        foreach (var control in existingControls)
                        {
                            db.DeleteGameControl(control.ControlId, currentUser.UserId);
                        }
                    }

                    // Add new controls
                    foreach (var control in gameControls)
                    {
                        if (!string.IsNullOrWhiteSpace(control.ActionName))
                        {
                            control.GameId = game.GameId;
                            control.UserId = currentUser.UserId;
                            db.AddGameControl(control);
                        }
                    }

                    GlassMessageBox.Show($"Game '{game.GameName}' saved successfully!");
                    DialogResult = true;
                    Close();
                }
                else
                {
                    GlassMessageBox.Show("Failed to save game. Please try again.");
                }
            }
            catch (Exception ex)
            {
                GlassMessageBox.Show($"An error occurred: {ex.Message}");
            }
        }

        private void CloseButton_Click(object sender, RoutedEventArgs e)
        {
            Close();
        }

        private void Window_MouseLeftButtonDown(object sender, MouseButtonEventArgs e)
        {
            if (e.ButtonState == MouseButtonState.Pressed)
                this.DragMove();
        }
    }
}
