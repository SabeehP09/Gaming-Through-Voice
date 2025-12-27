using GamingThroughVoiceRecognitionSystem.Models;
using GamingThroughVoiceRecognitionSystem.Database;
using System.Windows;
using System.Windows.Controls;

namespace GamingThroughVoiceRecognitionSystem.Views
{
    public partial class UserProfile : UserControl
    {
        private readonly DbConn db;
        private readonly int _userId;
        private readonly HomeWindow _parent;

        public UserProfile(int userId, HomeWindow parentWindow)
        {
            InitializeComponent();

            db = new DbConn();
            _userId = userId;
            _parent = parentWindow;

            LoadUserProfile();
        }

        public void LoadUserProfile()
        {
            UserModel user = db.GetUserById(_userId);

            if (user != null)
            {
                ProfileUserName.Text = user.FullName;
                ProfileEmail.Text = user.Email;

                // Avatar initials
                string initials = "";
                string[] nameParts = user.FullName.Split(' ');
                if (nameParts.Length > 0 && !string.IsNullOrEmpty(nameParts[0])) 
                    initials += nameParts[0][0];
                if (nameParts.Length > 1 && !string.IsNullOrEmpty(nameParts[nameParts.Length - 1])) 
                    initials += nameParts[nameParts.Length - 1][0];
                AvatarInitials.Text = initials.ToUpper();
            }

            // Load real statistics from database
            LoadStatistics();
        }

        private void LoadStatistics()
        {
            try
            {
                // Games Played - Count distinct games from history
                var gamesPlayedData = db.GetData(
                    "SELECT COUNT(DISTINCT GameID) FROM user_game_history WHERE UserID = @UserID",
                    new System.Data.SqlClient.SqlParameter[] {
                        new System.Data.SqlClient.SqlParameter("@UserID", _userId)
                    });

                if (gamesPlayedData.Rows.Count > 0)
                {
                    GamesPlayedText.Text = gamesPlayedData.Rows[0][0].ToString();
                }

                // Voice Commands - Count from voice history
                var voiceCommandsData = db.GetData(
                    "SELECT COUNT(*) FROM user_voice_history WHERE UserID = @UserID",
                    new System.Data.SqlClient.SqlParameter[] {
                        new System.Data.SqlClient.SqlParameter("@UserID", _userId)
                    });

                if (voiceCommandsData.Rows.Count > 0)
                {
                    VoiceCommandsText.Text = voiceCommandsData.Rows[0][0].ToString();
                }

                // Total Playtime - Sum duration from game history
                var playtimeData = db.GetData(
                    "SELECT ISNULL(SUM(Duration), 0) FROM user_game_history WHERE UserID = @UserID",
                    new System.Data.SqlClient.SqlParameter[] {
                        new System.Data.SqlClient.SqlParameter("@UserID", _userId)
                    });

                if (playtimeData.Rows.Count > 0)
                {
                    int totalMinutes = System.Convert.ToInt32(playtimeData.Rows[0][0]);
                    int hours = totalMinutes / 60;
                    int minutes = totalMinutes % 60;

                    if (hours > 0)
                    {
                        TotalPlaytimeText.Text = minutes > 0 ? $"{hours}h {minutes}m" : $"{hours}h";
                    }
                    else
                    {
                        TotalPlaytimeText.Text = $"{minutes}m";
                    }
                }
            }
            catch
            {
                // If tables don't exist yet, show 0
                GamesPlayedText.Text = "0";
                VoiceCommandsText.Text = "0";
                TotalPlaytimeText.Text = "0h";
            }
        }

        private void EditButton_Click(object sender, RoutedEventArgs e)
        {
            UserModel currentUser = db.GetUserById(_userId);
            if (currentUser != null)
            {
                EditProfileWindow editWindow = new EditProfileWindow(currentUser);
                bool? result = editWindow.ShowDialog();

                if (result == true)
                {
                    // Refresh profile data if changes were made
                    LoadUserProfile();
                }
            }
        }

        private void BackButton_Click(object sender, RoutedEventArgs e)
        {
            // Navigate back to dashboard
            if (_parent != null)
            {
                _parent.ContentArea.Content = new DashboardControl(db.GetUserById(_userId), db);
            }
        }
    }
}
