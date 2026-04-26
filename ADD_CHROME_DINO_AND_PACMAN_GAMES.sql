-- =============================================
-- Add Chrome Dino Runner and Pacman (Voice Controlled)
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
-- ADD CHROME DINO RUNNER
-- =============================================
IF NOT EXISTS (SELECT * FROM games WHERE GameName = 'Chrome Dino Runner' AND UserID = 0)
BEGIN
    INSERT INTO games (GameName, FilePath, IconPath, UserID, IsDefault, DateAdded)
    VALUES ('Chrome Dino Runner', NULL, NULL, 0, 1, GETDATE());
    PRINT 'Chrome Dino Runner added.';
END
ELSE
BEGIN
    PRINT 'Chrome Dino Runner already exists.';
END
GO

DECLARE @DinoID INT = (SELECT GameID FROM games WHERE GameName = 'Chrome Dino Runner' AND UserID = 0);

IF @DinoID IS NOT NULL AND NOT EXISTS (SELECT * FROM game_controls WHERE GameID = @DinoID)
BEGIN
    INSERT INTO game_controls (GameID, UserID, ActionName, VoiceCommand, KeyBinding, IsEnabled)
    VALUES
        (@DinoID, 0, 'Jump',   'jump',   'Up Arrow / Space', 1),
        (@DinoID, 0, 'Duck',   'duck',   'Down Arrow',       1),
        (@DinoID, 0, 'Start',  'start',  'Any Key',          1),
        (@DinoID, 0, 'Pause',  'pause',  'P',                1),
        (@DinoID, 0, 'Resume', 'resume', 'U',                1);
    PRINT 'Chrome Dino Runner controls inserted.';
END
GO

-- =============================================
-- ADD PACMAN (VOICE CONTROLLED)
-- =============================================
IF NOT EXISTS (SELECT * FROM games WHERE GameName = 'Pacman' AND UserID = 0)
BEGIN
    INSERT INTO games (GameName, FilePath, IconPath, UserID, IsDefault, DateAdded)
    VALUES ('Pacman', NULL, NULL, 0, 1, GETDATE());
    PRINT 'Pacman added.';
END
ELSE
BEGIN
    PRINT 'Pacman already exists.';
END
GO

DECLARE @PacmanID INT = (SELECT GameID FROM games WHERE GameName = 'Pacman' AND UserID = 0);

IF @PacmanID IS NOT NULL AND NOT EXISTS (SELECT * FROM game_controls WHERE GameID = @PacmanID)
BEGIN
    INSERT INTO game_controls (GameID, UserID, ActionName, VoiceCommand, KeyBinding, IsEnabled)
    VALUES
        (@PacmanID, 0, 'Move Left',  'left',         'Left Arrow',  1),
        (@PacmanID, 0, 'Move Right', 'right',         'Right Arrow', 1),
        (@PacmanID, 0, 'Move Up',    'up',            'Up Arrow',    1),
        (@PacmanID, 0, 'Move Down',  'down',          'Down Arrow',  1),
        (@PacmanID, 0, 'Pause',      'pause',         'Space',       1),
        (@PacmanID, 0, 'Resume',     'resume',        'Space',       1),
        (@PacmanID, 0, 'Restart',    'restart game',  'Enter',       1),
        (@PacmanID, 0, 'Quit',       'quit game',     'Escape',      1);
    PRINT 'Pacman controls inserted.';
END
GO

-- =============================================
-- VERIFY
-- =============================================
SELECT g.GameID, g.GameName, g.IsDefault, COUNT(gc.ControlID) AS Controls
FROM games g
LEFT JOIN game_controls gc ON g.GameID = gc.GameID
WHERE g.GameName IN ('Chrome Dino Runner', 'Pacman')
GROUP BY g.GameID, g.GameName, g.IsDefault;
GO
