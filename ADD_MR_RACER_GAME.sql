-- =============================================
-- Add Mr Racer (Microsoft Store - Voice Controlled)
-- Run this script in GamingVoiceRecognitionDB
-- =============================================

USE GamingVoiceRecognitionDB;
GO

-- =============================================
-- CREATE SYSTEM USER (UserID = 0) IF NOT EXISTS
-- =============================================
IF NOT EXISTS (SELECT * FROM user_info WHERE UserID = 0)
BEGIN
    SET IDENTITY_INSERT user_info ON;
    INSERT INTO user_info (UserID, FullName, Age, Email, PasswordHash, IsActive)
    VALUES (0, 'System', 25, 'system@voicegaming.com', 'SYSTEM_ACCOUNT', 1);
    SET IDENTITY_INSERT user_info OFF;
    PRINT 'System user (UserID = 0) created.';
END
ELSE
BEGIN
    PRINT 'System user already exists.';
END
GO

-- =============================================
-- ADD MR RACER
-- =============================================
IF NOT EXISTS (SELECT * FROM games WHERE GameName = 'Mr Racer' AND UserID = 0)
BEGIN
    INSERT INTO games (GameName, FilePath, IconPath, UserID, IsDefault, DateAdded)
    VALUES ('Mr Racer', NULL, NULL, 0, 1, GETDATE());
    PRINT 'Mr Racer added.';
END
ELSE
BEGIN
    PRINT 'Mr Racer already exists.';
END
GO

DECLARE @MrRacerID INT = (SELECT GameID FROM games WHERE GameName = 'Mr Racer' AND UserID = 0);

IF @MrRacerID IS NOT NULL AND NOT EXISTS (SELECT * FROM game_controls WHERE GameID = @MrRacerID)
BEGIN
    INSERT INTO game_controls (GameID, UserID, ActionName, VoiceCommand, KeyBinding, IsEnabled)
    VALUES
        -- System
        (@MrRacerID, 0, 'Open Game',    'open mr racer',  'Voice Only', 1),
        (@MrRacerID, 0, 'Close Game',   'close game',     'Voice Only', 1),
        -- Navigation
        (@MrRacerID, 0, 'Back',         'back',           'Voice Only', 1),
        (@MrRacerID, 0, 'Next',         'next',           'Voice Only', 1),
        (@MrRacerID, 0, 'Game Mode',    'game mode',      'Voice Only', 1),
        (@MrRacerID, 0, 'Garage',       'garage',         'Voice Only', 1),
        -- Race Start
        (@MrRacerID, 0, 'Start Race',   'go',             'Up Arrow',   1),
        (@MrRacerID, 0, 'Start',        'start',          'Voice Only', 1),
        -- Driving
        (@MrRacerID, 0, 'Steer Left',   'left',           'Left Arrow', 1),
        (@MrRacerID, 0, 'Steer Right',  'right',          'Right Arrow',1),
        (@MrRacerID, 0, 'Brake',        'brake',          'Down Arrow', 1),
        (@MrRacerID, 0, 'Horn',         'horn',           'H',          1),
        (@MrRacerID, 0, 'Camera',       'camera',         'C',          1),
        -- Pause Menu
        (@MrRacerID, 0, 'Pause',        'pause',          'Voice Only', 1),
        (@MrRacerID, 0, 'Continue',     'continue',       'Voice Only', 1),
        (@MrRacerID, 0, 'Restart',      'restart',        'Voice Only', 1),
        (@MrRacerID, 0, 'Main Menu',    'main menu',      'Voice Only', 1),
        -- Result Screen
        (@MrRacerID, 0, 'Replay',       'replay',         'Voice Only', 1),
        (@MrRacerID, 0, 'Home',         'home',           'Voice Only', 1);
    PRINT 'Mr Racer controls inserted.';
END
GO

-- =============================================
-- VERIFY
-- =============================================
SELECT g.GameID, g.GameName, g.IsDefault, COUNT(gc.ControlID) AS Controls
FROM games g
LEFT JOIN game_controls gc ON g.GameID = gc.GameID
WHERE g.GameName = 'Mr Racer'
GROUP BY g.GameID, g.GameName, g.IsDefault;
GO
