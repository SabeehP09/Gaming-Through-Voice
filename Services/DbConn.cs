using GamingThroughVoiceRecognitionSystem.Models;
using GamingThroughVoiceRecognitionSystem.Services;
using System;
using System.Collections.Generic;
using System.Configuration;
using System.Data;
using System.Data.SqlClient;
using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;

namespace GamingThroughVoiceRecognitionSystem.Database
{
    public class DbConn
    {
        private readonly string connectionString;
        private SqlConnection conn;

        public DbConn()
        {
            connectionString = ConfigurationManager.ConnectionStrings["GamingDB"].ConnectionString;
            conn = new SqlConnection(connectionString);
        }

        #region Connection Handling
        public SqlConnection Conn => conn;

        public void OpenConnection()
        {
            if (conn.State == ConnectionState.Closed)
                conn.Open();
        }

        public void CloseConnection()
        {
            if (conn.State == ConnectionState.Open)
                conn.Close();
        }
        #endregion

        #region Helper → GetData
        public DataTable GetData(string query, SqlParameter[] parameters)
        {
            DataTable dt = new DataTable();
            try
            {
                OpenConnection();
                using (SqlCommand cmd = new SqlCommand(query, conn))
                {
                    if (parameters != null)
                        cmd.Parameters.AddRange(parameters);

                    SqlDataAdapter da = new SqlDataAdapter(cmd);
                    da.Fill(dt);
                }
            }
            finally
            {
                CloseConnection();
            }
            return dt;
        }
        #endregion

        #region Password Hashing
        public string HashPassword(string password)
        {
            using (SHA256 sha = SHA256.Create())
            {
                byte[] bytes = sha.ComputeHash(Encoding.UTF8.GetBytes(password));
                StringBuilder sb = new StringBuilder();
                foreach (var b in bytes)
                    sb.Append(b.ToString("x2"));
                return sb.ToString();
            }
        }
        #endregion

        #region User Management

        // Add new user (signup)
        public bool AddUser(UserModel user)
        {
            try
            {
                OpenConnection();
                string query = @"INSERT INTO user_info (FullName, Age, Email, PasswordHash)
                                 VALUES (@FullName, @Age, @Email, @PasswordHash)";

                using (SqlCommand cmd = new SqlCommand(query, conn))
                {
                    cmd.Parameters.AddWithValue("@FullName", user.FullName);
                    cmd.Parameters.AddWithValue("@Age", user.Age);
                    cmd.Parameters.AddWithValue("@Email", user.Email);
                    cmd.Parameters.AddWithValue("@PasswordHash", HashPassword(user.PasswordHash));

                    return cmd.ExecuteNonQuery() > 0;
                }
            }
            finally
            {
                CloseConnection();
            }


        }

        // Add user with face data
        public bool AddUserWithFace(UserModel user, byte[] faceData)
        {
            try
            {
                OpenConnection();
                string query = @"INSERT INTO user_info (FullName, Age, Email, PasswordHash, FaceData)
                                 VALUES (@FullName, @Age, @Email, @PasswordHash, @FaceData)";

                using (SqlCommand cmd = new SqlCommand(query, conn))
                {
                    cmd.Parameters.AddWithValue("@FullName", user.FullName);
                    cmd.Parameters.AddWithValue("@Age", user.Age);
                    cmd.Parameters.AddWithValue("@Email", user.Email);
                    cmd.Parameters.AddWithValue("@PasswordHash", HashPassword(user.PasswordHash));
                    cmd.Parameters.AddWithValue("@FaceData", faceData ?? (object)DBNull.Value);

                    return cmd.ExecuteNonQuery() > 0;
                }
            }
            finally
            {
                CloseConnection();
            }
        }

        // Add user with voice data
        public bool AddUserWithVoice(UserModel user, byte[] voiceData)
        {
            try
            {
                OpenConnection();
                string query = @"INSERT INTO user_info (FullName, Age, Email, PasswordHash, VoiceData)
                                 VALUES (@FullName, @Age, @Email, @PasswordHash, @VoiceData)";

                using (SqlCommand cmd = new SqlCommand(query, conn))
                {
                    cmd.Parameters.AddWithValue("@FullName", user.FullName);
                    cmd.Parameters.AddWithValue("@Age", user.Age);
                    cmd.Parameters.AddWithValue("@Email", user.Email);
                    cmd.Parameters.AddWithValue("@PasswordHash", HashPassword(user.PasswordHash));
                    cmd.Parameters.AddWithValue("@VoiceData", voiceData ?? (object)DBNull.Value);

                    return cmd.ExecuteNonQuery() > 0;
                }
            }
            finally
            {
                CloseConnection();
            }
        }

        // Update user face data
        public bool UpdateUserFaceData(int userId, byte[] faceData)
        {
            try
            {
                OpenConnection();
                string query = @"UPDATE user_info SET FaceData = @FaceData WHERE UserID = @UserID";

                using (SqlCommand cmd = new SqlCommand(query, conn))
                {
                    cmd.Parameters.AddWithValue("@UserID", userId);
                    cmd.Parameters.AddWithValue("@FaceData", faceData);

                    return cmd.ExecuteNonQuery() > 0;
                }
            }
            finally
            {
                CloseConnection();
            }
        }

        // Update user voice data
        public bool UpdateUserVoiceData(int userId, byte[] voiceData)
        {
            try
            {
                OpenConnection();
                string query = @"UPDATE user_info SET VoiceData = @VoiceData WHERE UserID = @UserID";

                using (SqlCommand cmd = new SqlCommand(query, conn))
                {
                    cmd.Parameters.AddWithValue("@UserID", userId);
                    cmd.Parameters.AddWithValue("@VoiceData", voiceData);

                    return cmd.ExecuteNonQuery() > 0;
                }
            }
            finally
            {
                CloseConnection();
            }
        }

        // Get user face data
        public byte[] GetUserFaceData(int userId)
        {
            try
            {
                OpenConnection();
                string query = @"SELECT FaceData FROM user_info WHERE UserID = @UserID";

                using (SqlCommand cmd = new SqlCommand(query, conn))
                {
                    cmd.Parameters.AddWithValue("@UserID", userId);
                    object result = cmd.ExecuteScalar();
                    return result != DBNull.Value ? (byte[])result : null;
                }
            }
            finally
            {
                CloseConnection();
            }
        }

        // Store face data for existing user
        public bool StoreFaceData(int userId, byte[] faceData)
        {
            return UpdateUserFaceData(userId, faceData);
        }

        // Store voice data for existing user
        public bool StoreVoiceData(int userId, byte[] voiceData)
        {
            return UpdateUserVoiceData(userId, voiceData);
        }

        // Authenticate with face recognition using AForge.NET
        public bool AuthenticateWithFace(byte[] capturedFaceData, out int userId)
        {
            userId = -1;
            double bestConfidence = 0.0;
            int bestMatchUserId = -1;
            
            try
            {
                OpenConnection();
                // Get all users with face data
                string query = @"SELECT UserID, FaceData FROM user_info WHERE FaceData IS NOT NULL";

                using (SqlCommand cmd = new SqlCommand(query, conn))
                {
                    using (SqlDataReader dr = cmd.ExecuteReader())
                    {
                        // Use FaceRecognitionService for proper face comparison
                        var faceService = new FaceRecognitionService();
                        
                        int userCount = 0;
                        while (dr.Read())
                        {
                            userCount++;
                            int currentUserId = dr.GetInt32(0);
                            byte[] storedFaceData = (byte[])dr["FaceData"];

                            System.Diagnostics.Debug.WriteLine($"[FACE AUTH] Comparing against User {currentUserId} (Face data: {storedFaceData.Length} bytes)");

                            // Use proper face recognition comparison
                            double confidence;
                            bool isMatch = faceService.AuthenticateFace(capturedFaceData, storedFaceData, out confidence);
                            
                            System.Diagnostics.Debug.WriteLine($"[FACE AUTH] User {currentUserId}: confidence={confidence:P2}, match={isMatch}, threshold=92%");
                            
                            // Track best match
                            if (confidence > bestConfidence)
                            {
                                bestConfidence = confidence;
                                bestMatchUserId = currentUserId;
                            }
                            
                            // If we found a definite match, use it
                            if (isMatch)
                            {
                                userId = currentUserId;
                                System.Diagnostics.Debug.WriteLine($"[FACE AUTH] ✓ AUTHENTICATED as user {userId} with {confidence:P2} confidence");
                                return true;
                            }
                        }
                        
                        System.Diagnostics.Debug.WriteLine($"[FACE AUTH] Checked {userCount} users with face data");
                    }
                }
                
                // If no definite match but we have a best candidate, log it
                if (bestMatchUserId != -1)
                {
                    System.Diagnostics.Debug.WriteLine($"[FACE AUTH] Best match: User {bestMatchUserId} with {bestConfidence:P2} confidence (below threshold)");
                }
                
                return false;
            }
            finally
            {
                CloseConnection();
            }
        }

        // Authenticate with voice recognition using Python backend
        public bool AuthenticateWithVoice(byte[] capturedVoiceData, out int userId)
        {
            userId = -1;
            try
            {
                // Use Python API for voice identification
                var voiceService = new VoiceRecognitionService();
                var task = voiceService.IdentifyUserAsync(capturedVoiceData);
                task.Wait();
                
                var result = task.Result;
                bool identified = result.Item1;
                string userIdStr = result.Item2;
                double confidence = result.Item3;
                
                if (identified && confidence > 70) // 70% confidence threshold
                {
                    if (int.TryParse(userIdStr, out int parsedUserId))
                    {
                        userId = parsedUserId;
                        return true;
                    }
                }
                
                return false;
            }
            catch
            {
                // Fallback to database comparison if Python API fails
                return AuthenticateWithVoiceFallback(capturedVoiceData, out userId);
            }
        }

        // Fallback method if Python API is not available
        private bool AuthenticateWithVoiceFallback(byte[] capturedVoiceData, out int userId)
        {
            userId = -1;
            try
            {
                OpenConnection();
                string query = @"SELECT UserID, VoiceData FROM user_info WHERE VoiceData IS NOT NULL";

                using (SqlCommand cmd = new SqlCommand(query, conn))
                {
                    using (SqlDataReader dr = cmd.ExecuteReader())
                    {
                        while (dr.Read())
                        {
                            int currentUserId = dr.GetInt32(0);
                            byte[] storedVoiceData = (byte[])dr["VoiceData"];

                            if (CompareBiometricData(capturedVoiceData, storedVoiceData))
                            {
                                userId = currentUserId;
                                return true;
                            }
                        }
                    }
                }
                return false;
            }
            finally
            {
                CloseConnection();
            }
        }

        // Simple biometric data comparison (placeholder for ML-based comparison)
        private bool CompareBiometricData(byte[] data1, byte[] data2)
        {
            if (data1 == null || data2 == null || data1.Length != data2.Length)
                return false;

            // Simple byte-by-byte comparison
            // In production, this should use ML models for face/voice recognition
            // For now, we use exact match with some tolerance
            int matchingBytes = 0;
            int totalBytes = data1.Length;

            for (int i = 0; i < totalBytes; i++)
            {
                if (data1[i] == data2[i])
                    matchingBytes++;
            }

            // Allow 95% similarity threshold
            double similarity = (double)matchingBytes / totalBytes;
            return similarity >= 0.95;
        }

        // SignUp method (wrapper for AddUser)
        public bool SignUp(string fullName, int age, string email, string password)
        {
            UserModel user = new UserModel
            {
                FullName = fullName,
                Age = age,
                Email = email,
                PasswordHash = password
            };
            return AddUser(user);
        }

        // Login method
        public bool Login(string email, string password, out int userId)
        {
            return ValidateLogin(email, password, out userId);
        }

        // Validate login credentials
        public bool ValidateLogin(string email, string password, out int userId)
        {
            userId = -1;
            try
            {
                OpenConnection();
                string query = @"SELECT UserID FROM user_info 
                                 WHERE Email=@Email AND PasswordHash=@PasswordHash";

                using (SqlCommand cmd = new SqlCommand(query, conn))
                {
                    cmd.Parameters.AddWithValue("@Email", email);
                    cmd.Parameters.AddWithValue("@PasswordHash", HashPassword(password));

                    object result = cmd.ExecuteScalar();
                    if (result != null)
                    {
                        userId = Convert.ToInt32(result);
                        return true;
                    }
                    return false;
                }
            }
            finally
            {
                CloseConnection();
            }
        }

        // Get user by ID
        public UserModel GetUserById(int userId)
        {
            UserModel user = null;
            try
            {
                OpenConnection();
                string query = @"SELECT UserID, FullName, Age, Email 
                                 FROM user_info WHERE UserID=@UserID";

                using (SqlCommand cmd = new SqlCommand(query, conn))
                {
                    cmd.Parameters.AddWithValue("@UserID", userId);
                    using (SqlDataReader dr = cmd.ExecuteReader())
                    {
                        if (dr.Read())
                        {
                            user = new UserModel
                            {
                                UserId = dr.GetInt32(0),
                                FullName = dr.GetString(1),
                                Age = dr.GetInt32(2),
                                Email = dr.GetString(3)
                            };
                        }
                    }
                }
            }
            finally
            {
                CloseConnection();
            }
            return user;
        }

        // Get user by Email (for profile)
        public UserModel GetUserByEmail(string email)
        {
            UserModel user = null;
            try
            {
                OpenConnection();
                string query = @"SELECT UserID, FullName, Age, Email 
                                 FROM user_info WHERE Email=@Email";

                using (SqlCommand cmd = new SqlCommand(query, conn))
                {
                    cmd.Parameters.AddWithValue("@Email", email);
                    using (SqlDataReader dr = cmd.ExecuteReader())
                    {
                        if (dr.Read())
                        {
                            user = new UserModel
                            {
                                UserId = dr.GetInt32(0),
                                FullName = dr.GetString(1),
                                Age = dr.GetInt32(2),
                                Email = dr.GetString(3)
                            };
                        }
                    }
                }
            }
            finally
            {
                CloseConnection();
            }
            return user;
        }

        // Get user ID by email
        public int GetUserIdByEmail(string email)
        {
            try
            {
                OpenConnection();
                string query = @"SELECT UserID FROM user_info WHERE Email=@Email";

                using (SqlCommand cmd = new SqlCommand(query, conn))
                {
                    cmd.Parameters.AddWithValue("@Email", email);
                    object result = cmd.ExecuteScalar();
                    
                    if (result != null)
                    {
                        return Convert.ToInt32(result);
                    }
                    return -1;
                }
            }
            finally
            {
                CloseConnection();
            }
        }

        // Update user profile
        public bool UpdateUserProfile(UserModel user)
        {
            try
            {
                OpenConnection();
                string query = @"UPDATE user_info 
                                 SET FullName=@FullName, Age=@Age, Email=@Email
                                 WHERE UserID=@UserID";

                using (SqlCommand cmd = new SqlCommand(query, conn))
                {
                    cmd.Parameters.AddWithValue("@FullName", user.FullName);
                    cmd.Parameters.AddWithValue("@Age", user.Age);
                    cmd.Parameters.AddWithValue("@Email", user.Email);
                    cmd.Parameters.AddWithValue("@UserID", user.UserId);

                    return cmd.ExecuteNonQuery() > 0;
                }
            }
            finally
            {
                CloseConnection();
            }
        }

        #endregion

        #region Games Management
        
        // Get all games for a specific user (including default games)
        public List<GameModel> GetUserGames(int userId)
        {
            var games = new List<GameModel>();
            try
            {
                OpenConnection();
                string query = @"SELECT GameID, GameName, FilePath, IconPath, UserID, IsDefault, DateAdded 
                                FROM games 
                                WHERE UserID = @UserID OR IsDefault = 1
                                ORDER BY IsDefault DESC, DateAdded DESC";

                using (SqlCommand cmd = new SqlCommand(query, conn))
                {
                    cmd.Parameters.AddWithValue("@UserID", userId);
                    using (SqlDataReader dr = cmd.ExecuteReader())
                    {
                        while (dr.Read())
                        {
                            games.Add(new GameModel
                            {
                                GameId = dr.GetInt32(0),
                                GameName = dr.GetString(1),
                                FilePath = dr.IsDBNull(2) ? null : dr.GetString(2),
                                IconPath = dr.IsDBNull(3) ? null : dr.GetString(3),
                                UserId = dr.GetInt32(4),
                                IsDefault = dr.GetBoolean(5),
                                DateAdded = dr.GetDateTime(6)
                            });
                        }
                    }
                }
            }
            finally
            {
                CloseConnection();
            }
            return games;
        }

        // Get available games (legacy method for compatibility)
        public List<GameModel> GetAvailableGames()
        {
            var games = new List<GameModel>();
            try
            {
                OpenConnection();
                string query = "SELECT GameID, GameName, FilePath, IconPath, UserID, IsDefault, DateAdded FROM games WHERE IsDefault = 1";

                using (SqlCommand cmd = new SqlCommand(query, conn))
                {
                    using (SqlDataReader dr = cmd.ExecuteReader())
                    {
                        while (dr.Read())
                        {
                            games.Add(new GameModel
                            {
                                GameId = dr.GetInt32(0),
                                GameName = dr.GetString(1),
                                FilePath = dr.IsDBNull(2) ? null : dr.GetString(2),
                                IconPath = dr.IsDBNull(3) ? null : dr.GetString(3),
                                UserId = dr.GetInt32(4),
                                IsDefault = dr.GetBoolean(5),
                                DateAdded = dr.GetDateTime(6)
                            });
                        }
                    }
                }
            }
            finally
            {
                CloseConnection();
            }
            return games;
        }

        // Add a new game
        public bool AddGame(GameModel game)
        {
            try
            {
                OpenConnection();
                string query = @"INSERT INTO games (GameName, FilePath, IconPath, UserID, IsDefault, DateAdded)
                                VALUES (@GameName, @FilePath, @IconPath, @UserID, @IsDefault, @DateAdded);
                                SELECT CAST(SCOPE_IDENTITY() as int)";

                using (SqlCommand cmd = new SqlCommand(query, conn))
                {
                    cmd.Parameters.AddWithValue("@GameName", game.GameName);
                    cmd.Parameters.AddWithValue("@FilePath", game.FilePath ?? (object)DBNull.Value);
                    cmd.Parameters.AddWithValue("@IconPath", game.IconPath ?? (object)DBNull.Value);
                    cmd.Parameters.AddWithValue("@UserID", game.UserId);
                    cmd.Parameters.AddWithValue("@IsDefault", game.IsDefault);
                    cmd.Parameters.AddWithValue("@DateAdded", DateTime.Now);

                    object result = cmd.ExecuteScalar();
                    if (result != null)
                    {
                        game.GameId = Convert.ToInt32(result);
                        return true;
                    }
                    return false;
                }
            }
            finally
            {
                CloseConnection();
            }
        }

        // Update game
        public bool UpdateGame(GameModel game)
        {
            try
            {
                OpenConnection();
                string query = @"UPDATE games 
                                SET GameName = @GameName, FilePath = @FilePath, IconPath = @IconPath
                                WHERE GameID = @GameID AND UserID = @UserID";

                using (SqlCommand cmd = new SqlCommand(query, conn))
                {
                    cmd.Parameters.AddWithValue("@GameName", game.GameName);
                    cmd.Parameters.AddWithValue("@FilePath", game.FilePath ?? (object)DBNull.Value);
                    cmd.Parameters.AddWithValue("@IconPath", game.IconPath ?? (object)DBNull.Value);
                    cmd.Parameters.AddWithValue("@GameID", game.GameId);
                    cmd.Parameters.AddWithValue("@UserID", game.UserId);

                    return cmd.ExecuteNonQuery() > 0;
                }
            }
            finally
            {
                CloseConnection();
            }
        }

        // Delete game
        public bool DeleteGame(int gameId, int userId)
        {
            try
            {
                OpenConnection();
                // First delete all controls for this game
                string deleteControls = "DELETE FROM game_controls WHERE GameID = @GameID AND UserID = @UserID";
                using (SqlCommand cmd = new SqlCommand(deleteControls, conn))
                {
                    cmd.Parameters.AddWithValue("@GameID", gameId);
                    cmd.Parameters.AddWithValue("@UserID", userId);
                    cmd.ExecuteNonQuery();
                }

                // Then delete the game (only if not default)
                string deleteGame = "DELETE FROM games WHERE GameID = @GameID AND UserID = @UserID AND IsDefault = 0";
                using (SqlCommand cmd = new SqlCommand(deleteGame, conn))
                {
                    cmd.Parameters.AddWithValue("@GameID", gameId);
                    cmd.Parameters.AddWithValue("@UserID", userId);
                    return cmd.ExecuteNonQuery() > 0;
                }
            }
            finally
            {
                CloseConnection();
            }
        }

        // Get game controls
        public List<GameControlModel> GetGameControls(int gameId, int userId)
        {
            var controls = new List<GameControlModel>();
            try
            {
                OpenConnection();
                string query = @"SELECT ControlID, GameID, UserID, ActionName, VoiceCommand, KeyBinding 
                                FROM game_controls 
                                WHERE GameID = @GameID AND UserID = @UserID";

                using (SqlCommand cmd = new SqlCommand(query, conn))
                {
                    cmd.Parameters.AddWithValue("@GameID", gameId);
                    cmd.Parameters.AddWithValue("@UserID", userId);
                    using (SqlDataReader dr = cmd.ExecuteReader())
                    {
                        while (dr.Read())
                        {
                            controls.Add(new GameControlModel
                            {
                                ControlId = dr.GetInt32(0),
                                GameId = dr.GetInt32(1),
                                UserId = dr.GetInt32(2),
                                ActionName = dr.GetString(3),
                                VoiceCommand = dr.GetString(4),
                                KeyBinding = dr.GetString(5)
                            });
                        }
                    }
                }
            }
            finally
            {
                CloseConnection();
            }
            return controls;
        }

        // Add game control
        public bool AddGameControl(GameControlModel control)
        {
            try
            {
                OpenConnection();
                string query = @"INSERT INTO game_controls (GameID, UserID, ActionName, VoiceCommand, KeyBinding)
                                VALUES (@GameID, @UserID, @ActionName, @VoiceCommand, @KeyBinding)";

                using (SqlCommand cmd = new SqlCommand(query, conn))
                {
                    cmd.Parameters.AddWithValue("@GameID", control.GameId);
                    cmd.Parameters.AddWithValue("@UserID", control.UserId);
                    cmd.Parameters.AddWithValue("@ActionName", control.ActionName);
                    cmd.Parameters.AddWithValue("@VoiceCommand", control.VoiceCommand);
                    cmd.Parameters.AddWithValue("@KeyBinding", control.KeyBinding);

                    return cmd.ExecuteNonQuery() > 0;
                }
            }
            finally
            {
                CloseConnection();
            }
        }

        // Update game control
        public bool UpdateGameControl(GameControlModel control)
        {
            try
            {
                OpenConnection();
                string query = @"UPDATE game_controls 
                                SET ActionName = @ActionName, VoiceCommand = @VoiceCommand, KeyBinding = @KeyBinding
                                WHERE ControlID = @ControlID AND UserID = @UserID";

                using (SqlCommand cmd = new SqlCommand(query, conn))
                {
                    cmd.Parameters.AddWithValue("@ActionName", control.ActionName);
                    cmd.Parameters.AddWithValue("@VoiceCommand", control.VoiceCommand);
                    cmd.Parameters.AddWithValue("@KeyBinding", control.KeyBinding);
                    cmd.Parameters.AddWithValue("@ControlID", control.ControlId);
                    cmd.Parameters.AddWithValue("@UserID", control.UserId);

                    return cmd.ExecuteNonQuery() > 0;
                }
            }
            finally
            {
                CloseConnection();
            }
        }

        // Delete game control
        public bool DeleteGameControl(int controlId, int userId)
        {
            try
            {
                OpenConnection();
                string query = "DELETE FROM game_controls WHERE ControlID = @ControlID AND UserID = @UserID";

                using (SqlCommand cmd = new SqlCommand(query, conn))
                {
                    cmd.Parameters.AddWithValue("@ControlID", controlId);
                    cmd.Parameters.AddWithValue("@UserID", userId);

                    return cmd.ExecuteNonQuery() > 0;
                }
            }
            finally
            {
                CloseConnection();
            }
        }

        #endregion

        #region User Settings Management
        
        // Get user settings
        public UserSettings GetUserSettings(int userId)
        {
            try
            {
                OpenConnection();
                string query = @"SELECT * FROM user_settings WHERE UserID = @UserID";

                using (SqlCommand cmd = new SqlCommand(query, conn))
                {
                    cmd.Parameters.AddWithValue("@UserID", userId);
                    using (SqlDataReader dr = cmd.ExecuteReader())
                    {
                        if (dr.Read())
                        {
                            return new UserSettings
                            {
                                SettingID = dr.GetInt32(0),
                                UserID = dr.GetInt32(1),
                                Theme = dr.IsDBNull(2) ? "Dark" : dr.GetString(2),
                                VoiceRecognitionEnabled = dr.IsDBNull(3) ? true : dr.GetBoolean(3),
                                FaceRecognitionEnabled = dr.IsDBNull(4) ? false : dr.GetBoolean(4),
                                MicrophoneSensitivity = dr.IsDBNull(5) ? 50 : dr.GetInt32(5),
                                VoiceCommandTimeout = dr.IsDBNull(6) ? 5 : dr.GetInt32(6),
                                AutoLaunchGames = dr.IsDBNull(7) ? false : dr.GetBoolean(7),
                                ShowNotifications = dr.IsDBNull(8) ? true : dr.GetBoolean(8),
                                Language = dr.IsDBNull(9) ? "English" : dr.GetString(9)
                            };
                        }
                    }
                }
            }
            finally
            {
                CloseConnection();
            }
            return null;
        }

        // Create default settings for new user
        public bool CreateDefaultSettings(int userId)
        {
            try
            {
                OpenConnection();
                string query = @"INSERT INTO user_settings (UserID) VALUES (@UserID)";

                using (SqlCommand cmd = new SqlCommand(query, conn))
                {
                    cmd.Parameters.AddWithValue("@UserID", userId);
                    return cmd.ExecuteNonQuery() > 0;
                }
            }
            finally
            {
                CloseConnection();
            }
        }

        // Update user settings
        public bool UpdateUserSettings(UserSettings settings)
        {
            try
            {
                OpenConnection();
                string query = @"UPDATE user_settings 
                                SET Theme = @Theme,
                                    VoiceRecognitionEnabled = @VoiceRecognitionEnabled,
                                    FaceRecognitionEnabled = @FaceRecognitionEnabled,
                                    MicrophoneSensitivity = @MicrophoneSensitivity,
                                    VoiceCommandTimeout = @VoiceCommandTimeout,
                                    AutoLaunchGames = @AutoLaunchGames,
                                    ShowNotifications = @ShowNotifications,
                                    Language = @Language,
                                    UpdatedAt = GETDATE()
                                WHERE UserID = @UserID";

                using (SqlCommand cmd = new SqlCommand(query, conn))
                {
                    cmd.Parameters.AddWithValue("@Theme", settings.Theme);
                    cmd.Parameters.AddWithValue("@VoiceRecognitionEnabled", settings.VoiceRecognitionEnabled);
                    cmd.Parameters.AddWithValue("@FaceRecognitionEnabled", settings.FaceRecognitionEnabled);
                    cmd.Parameters.AddWithValue("@MicrophoneSensitivity", settings.MicrophoneSensitivity);
                    cmd.Parameters.AddWithValue("@VoiceCommandTimeout", settings.VoiceCommandTimeout);
                    cmd.Parameters.AddWithValue("@AutoLaunchGames", settings.AutoLaunchGames);
                    cmd.Parameters.AddWithValue("@ShowNotifications", settings.ShowNotifications);
                    cmd.Parameters.AddWithValue("@Language", settings.Language);
                    cmd.Parameters.AddWithValue("@UserID", settings.UserID);

                    return cmd.ExecuteNonQuery() > 0;
                }
            }
            finally
            {
                CloseConnection();
            }
        }

        #endregion

        #region System Voice Commands Management
        
        // Get all system voice commands
        public List<SystemVoiceCommand> GetSystemVoiceCommands()
        {
            var commands = new List<SystemVoiceCommand>();
            try
            {
                OpenConnection();
                string query = @"SELECT CommandID, CommandName, VoiceCommand, Action, Target, IsEnabled 
                                FROM system_voice_commands 
                                WHERE IsEnabled = 1
                                ORDER BY CommandName";

                using (SqlCommand cmd = new SqlCommand(query, conn))
                {
                    using (SqlDataReader dr = cmd.ExecuteReader())
                    {
                        while (dr.Read())
                        {
                            commands.Add(new SystemVoiceCommand
                            {
                                CommandID = dr.GetInt32(0),
                                CommandName = dr.GetString(1),
                                VoiceCommand = dr.GetString(2),
                                Action = dr.GetString(3),
                                Target = dr.IsDBNull(4) ? null : dr.GetString(4),
                                IsEnabled = dr.GetBoolean(5)
                            });
                        }
                    }
                }
            }
            finally
            {
                CloseConnection();
            }
            return commands;
        }

        #endregion

        #region Password Management
        
        // Update user password
        public bool UpdatePassword(int userId, string newPassword)
        {
            try
            {
                OpenConnection();
                string query = @"UPDATE user_info 
                                SET PasswordHash = @PasswordHash
                                WHERE UserID = @UserID";

                using (SqlCommand cmd = new SqlCommand(query, conn))
                {
                    cmd.Parameters.AddWithValue("@PasswordHash", HashPassword(newPassword));
                    cmd.Parameters.AddWithValue("@UserID", userId);

                    return cmd.ExecuteNonQuery() > 0;
                }
            }
            finally
            {
                CloseConnection();
            }
        }

        // Reset password by email
        public bool ResetPasswordByEmail(string email, string newPassword)
        {
            try
            {
                OpenConnection();
                string query = @"UPDATE user_info 
                                SET PasswordHash = @PasswordHash
                                WHERE Email = @Email";

                using (SqlCommand cmd = new SqlCommand(query, conn))
                {
                    cmd.Parameters.AddWithValue("@PasswordHash", HashPassword(newPassword));
                    cmd.Parameters.AddWithValue("@Email", email);

                    return cmd.ExecuteNonQuery() > 0;
                }
            }
            finally
            {
                CloseConnection();
            }
        }

        // Check if email exists
        public bool EmailExists(string email)
        {
            try
            {
                OpenConnection();
                string query = @"SELECT COUNT(*) FROM user_info WHERE Email = @Email";

                using (SqlCommand cmd = new SqlCommand(query, conn))
                {
                    cmd.Parameters.AddWithValue("@Email", email);
                    int count = (int)cmd.ExecuteScalar();
                    return count > 0;
                }
            }
            finally
            {
                CloseConnection();
            }
        }

        // Verify current password
        public bool VerifyPassword(int userId, string password)
        {
            try
            {
                OpenConnection();
                string query = @"SELECT COUNT(*) FROM user_info 
                                WHERE UserID = @UserID AND PasswordHash = @PasswordHash";

                using (SqlCommand cmd = new SqlCommand(query, conn))
                {
                    cmd.Parameters.AddWithValue("@UserID", userId);
                    cmd.Parameters.AddWithValue("@PasswordHash", HashPassword(password));

                    int count = (int)cmd.ExecuteScalar();
                    return count > 0;
                }
            }
            finally
            {
                CloseConnection();
            }
        }

        #endregion

        #region Voice Data Management (Optional)
        public bool AddVoiceSample(int userId, byte[] voiceData)
        {
            try
            {
                OpenConnection();
                string query = "INSERT INTO user_voice_data (UserID, VoiceSample) VALUES (@UserID, @VoiceSample)";
                using (SqlCommand cmd = new SqlCommand(query, conn))
                {
                    cmd.Parameters.AddWithValue("@UserID", userId);
                    cmd.Parameters.AddWithValue("@VoiceSample", voiceData);
                    return cmd.ExecuteNonQuery() > 0;
                }
            }
            finally
            {
                CloseConnection();
            }
        }

        public List<byte[]> GetVoiceSamples(int userId)
        {
            List<byte[]> samples = new List<byte[]>();
            try
            {
                OpenConnection();
                string query = "SELECT VoiceSample FROM user_voice_data WHERE UserID=@UserID";

                using (SqlCommand cmd = new SqlCommand(query, conn))
                {
                    cmd.Parameters.AddWithValue("@UserID", userId);
                    using (SqlDataReader dr = cmd.ExecuteReader())
                    {
                        while (dr.Read())
                        {
                            samples.Add((byte[])dr["VoiceSample"]);
                        }
                    }
                }
            }
            finally
            {
                CloseConnection();
            }
            return samples;
        }
        #endregion
    }
}
