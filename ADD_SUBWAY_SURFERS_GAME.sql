-- =============================================
-- Add Subway Surfers (Voice Controlled)
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
-- ADD SUBWAY SURFERS
-- =============================================
IF NOT EXISTS (SELECT * FROM games WHERE GameName = 'Subway Surfers' AND UserID = 0)
BEGIN
    INSERT INTO games (GameName, FilePath, IconPath, UserID, IsDefault, DateAdded)
    VALUES ('Subway Surfers', NULL, NULL, 0, 1, GETDATE());
    PRINT 'Subway Surfers added.';
END
ELSE
BEGIN
    PRINT 'Subway Surfers already exists.';
END
GO

DECLARE @SubwayID INT = (SELECT GameID FROM games WHERE GameName = 'Subway Surfers' AND UserID = 0);

IF @SubwayID IS NOT NULL AND NOT EXISTS (SELECT * FROM game_controls WHERE GameID = @SubwayID)
BEGIN
    INSERT INTO game_controls (GameID, UserID, ActionName, VoiceCommand, KeyBinding, IsEnabled)
    VALUES
        -- Launcher
        (@SubwayID, 0, 'Open Game',     'open subway surfer',  'Voice Only', 1),
        (@SubwayID, 0, 'Play Game',     'play subway surfer',  'Voice Only', 1),
        (@SubwayID, 0, 'Close Game',    'close game',          'Voice Only', 1),
        -- Game Start
        (@SubwayID, 0, 'Start Run',     'play',                'Swipe Gesture', 1),
        (@SubwayID, 0, 'Start',         'start',               'Swipe Gesture', 1),
        (@SubwayID, 0, 'Go',            'go',                  'Swipe Gesture', 1),
        (@SubwayID, 0, 'Run',           'run',                 'Swipe Gesture', 1),
        -- Movement (Swipe Gestures)
        (@SubwayID, 0, 'Jump',          'jump',                'Swipe Up',    1),
        (@SubwayID, 0, 'Slide',         'roll',                'Swipe Down',  1),
        (@SubwayID, 0, 'Roll',          'slide',               'Swipe Down',  1),
        (@SubwayID, 0, 'Move Left',     'left',                'Swipe Left',  1),
        (@SubwayID, 0, 'Move Right',    'right',               'Swipe Right', 1),
        -- Pause Menu
        (@SubwayID, 0, 'Pause',         'pause',               'Voice Only',  1),
        (@SubwayID, 0, 'Stop',          'stop',                'Voice Only',  1),
        (@SubwayID, 0, 'Resume',        'resume',              'Voice Only',  1),
        (@SubwayID, 0, 'Home',          'home',                'Voice Only',  1),
        (@SubwayID, 0, 'Settings',      'settings',            'Voice Only',  1);
    PRINT 'Subway Surfers controls inserted.';
END
GO

-- =============================================
-- VERIFY
-- =============================================
SELECT g.GameID, g.GameName, g.IsDefault, COUNT(gc.ControlID) AS Controls
FROM games g
LEFT JOIN game_controls gc ON g.GameID = gc.GameID
WHERE g.GameName = 'Subway Surfers'
GROUP BY g.GameID, g.GameName, g.IsDefault;
GO