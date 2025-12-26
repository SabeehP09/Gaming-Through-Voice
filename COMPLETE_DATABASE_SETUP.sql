-- =============================================
-- Gaming Through Voice Recognition System
-- COMPLETE DATABASE SETUP SCRIPT
-- =============================================
-- This script creates all tables needed for:
-- - User authentication (manual, face, voice)
-- - Game management
-- - Voice commands and controls
-- - Activity tracking and history
-- - Settings and preferences
-- =============================================

USE master;
GO

-- =============================================
-- CREATE DATABASE (if not exists)
-- =============================================
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'GamingVoiceRecognitionDB')
BEGIN
    CREATE DATABASE GamingVoiceRecognitionDB;
    PRINT 'Database "GamingVoiceRecognitionDB" created successfully.';
END
ELSE
BEGIN
    PRINT 'Database "GamingVoiceRecognitionDB" already exists.';
END
GO

USE GamingVoiceRecognitionDB;
GO

-- =============================================
-- TABLE 1: user_info
-- Stores user account information and biometric data
-- =============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'user_info')
BEGIN
    CREATE TABLE user_info (
        UserID INT PRIMARY KEY IDENTITY(1,1),
        FullName NVARCHAR(255) NOT NULL,
        Age INT NOT NULL,
        Email NVARCHAR(255) NOT NULL UNIQUE,
        PasswordHash NVARCHAR(255) NOT NULL,
        FaceData VARBINARY(MAX) NULL,              -- Face recognition data
        VoiceData VARBINARY(MAX) NULL,             -- Voice recognition data
        ProfilePicture VARBINARY(MAX) NULL,        -- User profile picture
        CreatedAt DATETIME DEFAULT GETDATE(),
        LastLogin DATETIME NULL,
        IsActive BIT DEFAULT 1,
        CONSTRAINT CHK_Age CHECK (Age >= 5 AND Age <= 120)
    );
    PRINT 'Table "user_info" created successfully.';
END
ELSE
BEGIN
    PRINT 'Table "user_info" already exists.';
    
    -- Add missing columns if they don't exist
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('user_info') AND name = 'FaceData')
        ALTER TABLE user_info ADD FaceData VARBINARY(MAX) NULL;
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('user_info') AND name = 'VoiceData')
        ALTER TABLE user_info ADD VoiceData VARBINARY(MAX) NULL;
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('user_info') AND name = 'ProfilePicture')
        ALTER TABLE user_info ADD ProfilePicture VARBINARY(MAX) NULL;
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('user_info') AND name = 'CreatedAt')
        ALTER TABLE user_info ADD CreatedAt DATETIME DEFAULT GETDATE();
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('user_info') AND name = 'LastLogin')
        ALTER TABLE user_info ADD LastLogin DATETIME NULL;
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('user_info') AND name = 'IsActive')
        ALTER TABLE user_info ADD IsActive BIT DEFAULT 1;
    
    PRINT 'Table "user_info" updated with missing columns.';
END
GO

-- =============================================
-- TABLE 2: games
-- Stores game information
-- =============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'games')
BEGIN
    CREATE TABLE games (
        GameID INT PRIMARY KEY IDENTITY(1,1),
        GameName NVARCHAR(255) NOT NULL,
        FilePath NVARCHAR(500) NULL,
        IconPath NVARCHAR(500) NULL,
        UserID INT NOT NULL,
        IsDefault BIT DEFAULT 0,
        DateAdded DATETIME DEFAULT GETDATE(),
        LastPlayed DATETIME NULL,
        PlayCount INT DEFAULT 0,
        TotalPlayTime INT DEFAULT 0,                -- In minutes
        FOREIGN KEY (UserID) REFERENCES user_info(UserID) ON DELETE CASCADE
    );
    PRINT 'Table "games" created successfully.';
END
ELSE
BEGIN
    PRINT 'Table "games" already exists.';
    
    -- Add missing columns
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('games') AND name = 'IconPath')
        ALTER TABLE games ADD IconPath NVARCHAR(500) NULL;
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('games') AND name = 'IsDefault')
        ALTER TABLE games ADD IsDefault BIT DEFAULT 0;
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('games') AND name = 'DateAdded')
        ALTER TABLE games ADD DateAdded DATETIME DEFAULT GETDATE();
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('games') AND name = 'LastPlayed')
        ALTER TABLE games ADD LastPlayed DATETIME NULL;
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('games') AND name = 'PlayCount')
        ALTER TABLE games ADD PlayCount INT DEFAULT 0;
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('games') AND name = 'TotalPlayTime')
        ALTER TABLE games ADD TotalPlayTime INT DEFAULT 0;
    
    PRINT 'Table "games" updated with missing columns.';
END
GO

-- =============================================
-- TABLE 3: game_controls
-- Stores voice commands and key bindings for games
-- =============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'game_controls')
BEGIN
    CREATE TABLE game_controls (
        ControlID INT PRIMARY KEY IDENTITY(1,1),
        GameID INT NOT NULL,
        UserID INT NOT NULL,
        ActionName NVARCHAR(100) NOT NULL,
        VoiceCommand NVARCHAR(100) NOT NULL,
        KeyBinding NVARCHAR(50) NOT NULL,
        IsEnabled BIT DEFAULT 1,
        CreatedAt DATETIME DEFAULT GETDATE(),
        FOREIGN KEY (GameID) REFERENCES games(GameID) ON DELETE CASCADE,
        FOREIGN KEY (UserID) REFERENCES user_info(UserID)
    );
    PRINT 'Table "game_controls" created successfully.';
END
ELSE
BEGIN
    PRINT 'Table "game_controls" already exists.';
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('game_controls') AND name = 'IsEnabled')
        ALTER TABLE game_controls ADD IsEnabled BIT DEFAULT 1;
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('game_controls') AND name = 'CreatedAt')
        ALTER TABLE game_controls ADD CreatedAt DATETIME DEFAULT GETDATE();
    
    PRINT 'Table "game_controls" updated.';
END
GO

-- =============================================
-- TABLE 4: user_game_history
-- Tracks game play sessions
-- =============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'user_game_history')
BEGIN
    CREATE TABLE user_game_history (
        HistoryID INT PRIMARY KEY IDENTITY(1,1),
        UserID INT NOT NULL,
        GameID INT NOT NULL,
        StartTime DATETIME DEFAULT GETDATE(),
        EndTime DATETIME NULL,
        Duration INT NULL,                          -- In minutes
        VoiceCommandsUsed INT DEFAULT 0,
        FOREIGN KEY (UserID) REFERENCES user_info(UserID) ON DELETE CASCADE,
        FOREIGN KEY (GameID) REFERENCES games(GameID) ON DELETE CASCADE
    );
    PRINT 'Table "user_game_history" created successfully.';
END
ELSE
BEGIN
    PRINT 'Table "user_game_history" already exists.';
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('user_game_history') AND name = 'VoiceCommandsUsed')
        ALTER TABLE user_game_history ADD VoiceCommandsUsed INT DEFAULT 0;
    
    PRINT 'Table "user_game_history" updated.';
END
GO

-- =============================================
-- TABLE 5: user_voice_history
-- Tracks voice command usage
-- =============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'user_voice_history')
BEGIN
    CREATE TABLE user_voice_history (
        VoiceHistoryID INT PRIMARY KEY IDENTITY(1,1),
        UserID INT NOT NULL,
        GameID INT NULL,
        VoiceCommand NVARCHAR(100) NOT NULL,
        ActionPerformed NVARCHAR(100) NULL,
        Timestamp DATETIME DEFAULT GETDATE(),
        IsSuccessful BIT DEFAULT 1,
        ConfidenceScore DECIMAL(5,2) NULL,          -- 0.00 to 100.00
        FOREIGN KEY (UserID) REFERENCES user_info(UserID) ON DELETE CASCADE,
        FOREIGN KEY (GameID) REFERENCES games(GameID) ON DELETE SET NULL
    );
    PRINT 'Table "user_voice_history" created successfully.';
END
ELSE
BEGIN
    PRINT 'Table "user_voice_history" already exists.';
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('user_voice_history') AND name = 'IsSuccessful')
        ALTER TABLE user_voice_history ADD IsSuccessful BIT DEFAULT 1;
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('user_voice_history') AND name = 'ConfidenceScore')
        ALTER TABLE user_voice_history ADD ConfidenceScore DECIMAL(5,2) NULL;
    
    PRINT 'Table "user_voice_history" updated.';
END
GO

-- =============================================
-- TABLE 6: user_settings
-- Stores user preferences and settings
-- =============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'user_settings')
BEGIN
    CREATE TABLE user_settings (
        SettingID INT PRIMARY KEY IDENTITY(1,1),
        UserID INT NOT NULL UNIQUE,
        Theme NVARCHAR(50) DEFAULT 'Dark',          -- Dark, Light, Auto
        VoiceRecognitionEnabled BIT DEFAULT 1,
        FaceRecognitionEnabled BIT DEFAULT 0,
        MicrophoneSensitivity INT DEFAULT 50,       -- 0-100
        VoiceCommandTimeout INT DEFAULT 5,          -- In seconds
        AutoLaunchGames BIT DEFAULT 0,
        ShowNotifications BIT DEFAULT 1,
        Language NVARCHAR(50) DEFAULT 'English',
        UpdatedAt DATETIME DEFAULT GETDATE(),
        FOREIGN KEY (UserID) REFERENCES user_info(UserID) ON DELETE CASCADE
    );
    PRINT 'Table "user_settings" created successfully.';
END
ELSE
BEGIN
    PRINT 'Table "user_settings" already exists.';
END
GO

-- =============================================
-- TABLE 7: voice_samples
-- Stores multiple voice samples for training
-- =============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'voice_samples')
BEGIN
    CREATE TABLE voice_samples (
        SampleID INT PRIMARY KEY IDENTITY(1,1),
        UserID INT NOT NULL,
        VoiceSample VARBINARY(MAX) NOT NULL,
        SampleType NVARCHAR(50) DEFAULT 'Training', -- Training, Verification
        RecordedAt DATETIME DEFAULT GETDATE(),
        Quality DECIMAL(5,2) NULL,                  -- Quality score 0-100
        FOREIGN KEY (UserID) REFERENCES user_info(UserID) ON DELETE CASCADE
    );
    PRINT 'Table "voice_samples" created successfully.';
END
ELSE
BEGIN
    PRINT 'Table "voice_samples" already exists.';
END
GO

-- =============================================
-- TABLE 8: face_samples
-- Stores multiple face samples for training
-- =============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'face_samples')
BEGIN
    CREATE TABLE face_samples (
        SampleID INT PRIMARY KEY IDENTITY(1,1),
        UserID INT NOT NULL,
        FaceSample VARBINARY(MAX) NOT NULL,
        SampleType NVARCHAR(50) DEFAULT 'Training', -- Training, Verification
        CapturedAt DATETIME DEFAULT GETDATE(),
        Quality DECIMAL(5,2) NULL,                  -- Quality score 0-100
        FOREIGN KEY (UserID) REFERENCES user_info(UserID) ON DELETE CASCADE
    );
    PRINT 'Table "face_samples" created successfully.';
END
ELSE
BEGIN
    PRINT 'Table "face_samples" already exists.';
END
GO

-- =============================================
-- TABLE 9: login_history
-- Tracks user login attempts and methods
-- =============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'login_history')
BEGIN
    CREATE TABLE login_history (
        LoginID INT PRIMARY KEY IDENTITY(1,1),
        UserID INT NULL,
        LoginMethod NVARCHAR(50) NOT NULL,          -- Manual, Face, Voice
        LoginTime DATETIME DEFAULT GETDATE(),
        IsSuccessful BIT DEFAULT 1,
        IPAddress NVARCHAR(50) NULL,
        DeviceInfo NVARCHAR(255) NULL,
        FOREIGN KEY (UserID) REFERENCES user_info(UserID) ON DELETE CASCADE
    );
    PRINT 'Table "login_history" created successfully.';
END
ELSE
BEGIN
    PRINT 'Table "login_history" already exists.';
END
GO

-- =============================================
-- TABLE 10: system_voice_commands
-- Stores system-wide voice commands for app navigation
-- =============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'system_voice_commands')
BEGIN
    CREATE TABLE system_voice_commands (
        CommandID INT PRIMARY KEY IDENTITY(1,1),
        CommandName NVARCHAR(100) NOT NULL,
        VoiceCommand NVARCHAR(100) NOT NULL UNIQUE,
        Action NVARCHAR(100) NOT NULL,              -- Navigate, Click, Open, Close, etc.
        Target NVARCHAR(100) NULL,                  -- Dashboard, Settings, Profile, etc.
        IsEnabled BIT DEFAULT 1,
        CreatedAt DATETIME DEFAULT GETDATE()
    );
    PRINT 'Table "system_voice_commands" created successfully.';
END
ELSE
BEGIN
    PRINT 'Table "system_voice_commands" already exists.';
END
GO

-- =============================================
-- TABLE 11: user_achievements
-- Tracks user achievements and milestones
-- =============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'user_achievements')
BEGIN
    CREATE TABLE user_achievements (
        AchievementID INT PRIMARY KEY IDENTITY(1,1),
        UserID INT NOT NULL,
        AchievementName NVARCHAR(100) NOT NULL,
        Description NVARCHAR(255) NULL,
        UnlockedAt DATETIME DEFAULT GETDATE(),
        IconPath NVARCHAR(500) NULL,
        FOREIGN KEY (UserID) REFERENCES user_info(UserID) ON DELETE CASCADE
    );
    PRINT 'Table "user_achievements" created successfully.';
END
ELSE
BEGIN
    PRINT 'Table "user_achievements" already exists.';
END
GO

-- =============================================
-- TABLE 12: notifications
-- Stores user notifications
-- =============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'notifications')
BEGIN
    CREATE TABLE notifications (
        NotificationID INT PRIMARY KEY IDENTITY(1,1),
        UserID INT NOT NULL,
        Title NVARCHAR(255) NOT NULL,
        Message NVARCHAR(MAX) NOT NULL,
        Type NVARCHAR(50) DEFAULT 'Info',           -- Info, Warning, Success, Error
        IsRead BIT DEFAULT 0,
        CreatedAt DATETIME DEFAULT GETDATE(),
        FOREIGN KEY (UserID) REFERENCES user_info(UserID) ON DELETE CASCADE
    );
    PRINT 'Table "notifications" created successfully.';
END
ELSE
BEGIN
    PRINT 'Table "notifications" already exists.';
END
GO

-- =============================================
-- INSERT DEFAULT DATA
-- =============================================

-- Insert default system user (UserID = 0 for default games)
IF NOT EXISTS (SELECT * FROM user_info WHERE UserID = 0)
BEGIN
    SET IDENTITY_INSERT user_info ON;
    INSERT INTO user_info (UserID, FullName, Age, Email, PasswordHash, IsActive)
    VALUES (0, 'System', 25, 'system@voicegaming.com', 'SYSTEM_ACCOUNT', 1);
    SET IDENTITY_INSERT user_info OFF;
    PRINT 'System user created.';
END
GO

-- Insert default games
IF NOT EXISTS (SELECT * FROM games WHERE IsDefault = 1)
BEGIN
    INSERT INTO games (GameName, FilePath, IconPath, UserID, IsDefault, DateAdded)
    VALUES 
        ('Subway Surfers', NULL, NULL, 0, 1, GETDATE()),
        ('Temple Run', NULL, NULL, 0, 1, GETDATE()),
        ('Flappy Bird', NULL, NULL, 0, 1, GETDATE()),
        ('Chrome Dino', NULL, NULL, 0, 1, GETDATE());
    
    PRINT 'Default games inserted.';
END
GO

-- Insert default game controls
DECLARE @SubwaySurfersID INT = (SELECT GameID FROM games WHERE GameName = 'Subway Surfers' AND IsDefault = 1);
DECLARE @TempleRunID INT = (SELECT GameID FROM games WHERE GameName = 'Temple Run' AND IsDefault = 1);
DECLARE @FlappyBirdID INT = (SELECT GameID FROM games WHERE GameName = 'Flappy Bird' AND IsDefault = 1);
DECLARE @ChromeDinoID INT = (SELECT GameID FROM games WHERE GameName = 'Chrome Dino' AND IsDefault = 1);

-- Subway Surfers controls
IF @SubwaySurfersID IS NOT NULL AND NOT EXISTS (SELECT * FROM game_controls WHERE GameID = @SubwaySurfersID)
BEGIN
    INSERT INTO game_controls (GameID, UserID, ActionName, VoiceCommand, KeyBinding, IsEnabled)
    VALUES 
        (@SubwaySurfersID, 0, 'Jump', 'jump', 'Space', 1),
        (@SubwaySurfersID, 0, 'Move Left', 'left', 'Left Arrow', 1),
        (@SubwaySurfersID, 0, 'Move Right', 'right', 'Right Arrow', 1),
        (@SubwaySurfersID, 0, 'Roll', 'roll', 'Down Arrow', 1),
        (@SubwaySurfersID, 0, 'Pause', 'pause', 'Escape', 1);
    PRINT 'Subway Surfers controls inserted.';
END

-- Temple Run controls
IF @TempleRunID IS NOT NULL AND NOT EXISTS (SELECT * FROM game_controls WHERE GameID = @TempleRunID)
BEGIN
    INSERT INTO game_controls (GameID, UserID, ActionName, VoiceCommand, KeyBinding, IsEnabled)
    VALUES 
        (@TempleRunID, 0, 'Jump', 'jump', 'Space', 1),
        (@TempleRunID, 0, 'Slide', 'slide', 'Down Arrow', 1),
        (@TempleRunID, 0, 'Turn Left', 'left', 'Left Arrow', 1),
        (@TempleRunID, 0, 'Turn Right', 'right', 'Right Arrow', 1),
        (@TempleRunID, 0, 'Pause', 'pause', 'Escape', 1);
    PRINT 'Temple Run controls inserted.';
END

-- Flappy Bird controls
IF @FlappyBirdID IS NOT NULL AND NOT EXISTS (SELECT * FROM game_controls WHERE GameID = @FlappyBirdID)
BEGIN
    INSERT INTO game_controls (GameID, UserID, ActionName, VoiceCommand, KeyBinding, IsEnabled)
    VALUES 
        (@FlappyBirdID, 0, 'Flap', 'flap', 'Space', 1),
        (@FlappyBirdID, 0, 'Restart', 'restart', 'R', 1),
        (@FlappyBirdID, 0, 'Pause', 'pause', 'Escape', 1);
    PRINT 'Flappy Bird controls inserted.';
END

-- Chrome Dino controls
IF @ChromeDinoID IS NOT NULL AND NOT EXISTS (SELECT * FROM game_controls WHERE GameID = @ChromeDinoID)
BEGIN
    INSERT INTO game_controls (GameID, UserID, ActionName, VoiceCommand, KeyBinding, IsEnabled)
    VALUES 
        (@ChromeDinoID, 0, 'Jump', 'jump', 'Space', 1),
        (@ChromeDinoID, 0, 'Duck', 'duck', 'Down Arrow', 1),
        (@ChromeDinoID, 0, 'Restart', 'restart', 'R', 1);
    PRINT 'Chrome Dino controls inserted.';
END
GO

-- Insert default system voice commands
IF NOT EXISTS (SELECT * FROM system_voice_commands)
BEGIN
    INSERT INTO system_voice_commands (CommandName, VoiceCommand, Action, Target, IsEnabled)
    VALUES 
        -- Navigation
        ('Go Home', 'go home', 'Navigate', 'Dashboard', 1),
        ('Open Dashboard', 'open dashboard', 'Navigate', 'Dashboard', 1),
        ('Go to Profile', 'go to profile', 'Navigate', 'Profile', 1),
        ('Open Profile', 'open profile', 'Navigate', 'Profile', 1),
        ('Go to Settings', 'go to settings', 'Navigate', 'Settings', 1),
        ('Open Settings', 'open settings', 'Navigate', 'Settings', 1),
        ('Voice Commands', 'voice commands', 'Navigate', 'VoiceCommands', 1),
        
        -- Actions
        ('Add Game', 'add game', 'Click', 'AddGameButton', 1),
        ('Logout', 'logout', 'Action', 'Logout', 1),
        ('Sign Out', 'sign out', 'Action', 'Logout', 1),
        ('Close Window', 'close window', 'Action', 'Close', 1),
        ('Minimize', 'minimize', 'Action', 'Minimize', 1),
        ('Maximize', 'maximize', 'Action', 'Maximize', 1),
        
        -- Game Actions
        ('Play Game', 'play game', 'Action', 'PlaySelectedGame', 1),
        ('Stop Game', 'stop game', 'Action', 'StopGame', 1),
        
        -- General
        ('Help', 'help', 'Action', 'ShowHelp', 1),
        ('Refresh', 'refresh', 'Action', 'Refresh', 1);
    
    PRINT 'System voice commands inserted.';
END
GO

-- =============================================
-- CREATE INDEXES FOR PERFORMANCE
-- =============================================

-- user_info indexes
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_user_info_Email')
    CREATE INDEX IX_user_info_Email ON user_info(Email);

-- games indexes
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_games_UserID')
    CREATE INDEX IX_games_UserID ON games(UserID);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_games_IsDefault')
    CREATE INDEX IX_games_IsDefault ON games(IsDefault);

-- game_controls indexes
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_game_controls_GameID_UserID')
    CREATE INDEX IX_game_controls_GameID_UserID ON game_controls(GameID, UserID);

-- user_game_history indexes
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_user_game_history_UserID')
    CREATE INDEX IX_user_game_history_UserID ON user_game_history(UserID);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_user_game_history_GameID')
    CREATE INDEX IX_user_game_history_GameID ON user_game_history(GameID);

-- user_voice_history indexes
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_user_voice_history_UserID')
    CREATE INDEX IX_user_voice_history_UserID ON user_voice_history(UserID);

-- login_history indexes
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_login_history_UserID')
    CREATE INDEX IX_login_history_UserID ON login_history(UserID);

PRINT 'Indexes created successfully.';
GO

-- =============================================
-- CREATE VIEWS FOR COMMON QUERIES
-- =============================================

-- View: User game statistics
IF OBJECT_ID('vw_user_game_stats', 'V') IS NOT NULL
    DROP VIEW vw_user_game_stats;
GO

CREATE VIEW vw_user_game_stats AS
SELECT 
    u.UserID,
    u.FullName,
    COUNT(DISTINCT ugh.GameID) AS GamesPlayed,
    SUM(ugh.Duration) AS TotalPlayTime,
    SUM(ugh.VoiceCommandsUsed) AS TotalVoiceCommands,
    COUNT(ugh.HistoryID) AS TotalSessions
FROM user_info u
LEFT JOIN user_game_history ugh ON u.UserID = ugh.UserID
GROUP BY u.UserID, u.FullName;
GO

PRINT 'View "vw_user_game_stats" created.';
GO

-- View: Popular games
IF OBJECT_ID('vw_popular_games', 'V') IS NOT NULL
    DROP VIEW vw_popular_games;
GO

CREATE VIEW vw_popular_games AS
SELECT 
    g.GameID,
    g.GameName,
    g.PlayCount,
    g.TotalPlayTime,
    COUNT(DISTINCT ugh.UserID) AS UniqueUsers,
    AVG(ugh.Duration) AS AvgSessionTime
FROM games g
LEFT JOIN user_game_history ugh ON g.GameID = ugh.GameID
GROUP BY g.GameID, g.GameName, g.PlayCount, g.TotalPlayTime;
GO

PRINT 'View "vw_popular_games" created.';
GO

-- =============================================
-- CREATE STORED PROCEDURES
-- =============================================

-- Procedure: Record game session
IF OBJECT_ID('sp_RecordGameSession', 'P') IS NOT NULL
    DROP PROCEDURE sp_RecordGameSession;
GO

CREATE PROCEDURE sp_RecordGameSession
    @UserID INT,
    @GameID INT,
    @Duration INT,
    @VoiceCommandsUsed INT
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Insert session record
    INSERT INTO user_game_history (UserID, GameID, StartTime, EndTime, Duration, VoiceCommandsUsed)
    VALUES (@UserID, @GameID, DATEADD(MINUTE, -@Duration, GETDATE()), GETDATE(), @Duration, @VoiceCommandsUsed);
    
    -- Update game statistics
    UPDATE games
    SET PlayCount = PlayCount + 1,
        TotalPlayTime = TotalPlayTime + @Duration,
        LastPlayed = GETDATE()
    WHERE GameID = @GameID;
    
    -- Update user last login
    UPDATE user_info
    SET LastLogin = GETDATE()
    WHERE UserID = @UserID;
END
GO

PRINT 'Stored procedure "sp_RecordGameSession" created.';
GO

-- Procedure: Record voice command
IF OBJECT_ID('sp_RecordVoiceCommand', 'P') IS NOT NULL
    DROP PROCEDURE sp_RecordVoiceCommand;
GO

CREATE PROCEDURE sp_RecordVoiceCommand
    @UserID INT,
    @GameID INT = NULL,
    @VoiceCommand NVARCHAR(100),
    @ActionPerformed NVARCHAR(100) = NULL,
    @IsSuccessful BIT = 1,
    @ConfidenceScore DECIMAL(5,2) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    
    INSERT INTO user_voice_history (UserID, GameID, VoiceCommand, ActionPerformed, IsSuccessful, ConfidenceScore)
    VALUES (@UserID, @GameID, @VoiceCommand, @ActionPerformed, @IsSuccessful, @ConfidenceScore);
END
GO

PRINT 'Stored procedure "sp_RecordVoiceCommand" created.';
GO

-- Procedure: Record login attempt
IF OBJECT_ID('sp_RecordLogin', 'P') IS NOT NULL
    DROP PROCEDURE sp_RecordLogin;
GO

CREATE PROCEDURE sp_RecordLogin
    @UserID INT = NULL,
    @LoginMethod NVARCHAR(50),
    @IsSuccessful BIT,
    @IPAddress NVARCHAR(50) = NULL,
    @DeviceInfo NVARCHAR(255) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    
    INSERT INTO login_history (UserID, LoginMethod, IsSuccessful, IPAddress, DeviceInfo)
    VALUES (@UserID, @LoginMethod, @IsSuccessful, @IPAddress, @DeviceInfo);
    
    -- Update last login if successful
    IF @IsSuccessful = 1 AND @UserID IS NOT NULL
    BEGIN
        UPDATE user_info
        SET LastLogin = GETDATE()
        WHERE UserID = @UserID;
    END
END
GO

PRINT 'Stored procedure "sp_RecordLogin" created.';
GO

-- =============================================
-- VERIFICATION QUERIES
-- =============================================
PRINT '';
PRINT '==============================================';
PRINT 'DATABASE SETUP COMPLETED SUCCESSFULLY!';
PRINT '==============================================';
PRINT '';
PRINT 'Tables Created:';
PRINT '  1. user_info';
PRINT '  2. games';
PRINT '  3. game_controls';
PRINT '  4. user_game_history';
PRINT '  5. user_voice_history';
PRINT '  6. user_settings';
PRINT '  7. voice_samples';
PRINT '  8. face_samples';
PRINT '  9. login_history';
PRINT ' 10. system_voice_commands';
PRINT ' 11. user_achievements';
PRINT ' 12. notifications';
PRINT '';
PRINT 'Views Created:';
PRINT '  - vw_user_game_stats';
PRINT '  - vw_popular_games';
PRINT '';
PRINT 'Stored Procedures Created:';
PRINT '  - sp_RecordGameSession';
PRINT '  - sp_RecordVoiceCommand';
PRINT '  - sp_RecordLogin';
PRINT '';
PRINT 'Default Data Inserted:';
PRINT '  - System user (UserID = 0)';
PRINT '  - 4 default games';
PRINT '  - 13 game controls';
PRINT '  - 17 system voice commands';
PRINT '';
PRINT '==============================================';
PRINT 'Run the following queries to verify:';
PRINT '==============================================';
PRINT 'SELECT * FROM user_info;';
PRINT 'SELECT * FROM games;';
PRINT 'SELECT * FROM game_controls;';
PRINT 'SELECT * FROM system_voice_commands;';
PRINT '==============================================';
GO
