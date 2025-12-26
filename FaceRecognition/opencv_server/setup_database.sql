-- ============================================================================
-- OpenCV Face Recognition Database Setup Script
-- ============================================================================
-- This script sets up the complete database schema for face recognition
-- including tables, indexes, constraints, and optional sample data
-- 
-- Prerequisites:
-- - SQL Server 2016 or higher
-- - GamingVoiceRecognition database must exist
-- - Users table must exist (created by main application)
--
-- Usage:
--   sqlcmd -S localhost -d GamingVoiceRecognition -i setup_database.sql
--   Or run in SQL Server Management Studio (SSMS)
-- ============================================================================

USE GamingVoiceRecognition;
GO

PRINT '============================================================================';
PRINT 'OpenCV Face Recognition Database Setup';
PRINT '============================================================================';
PRINT '';
GO

-- ============================================================================
-- Step 1: Check Prerequisites
-- ============================================================================

PRINT 'Step 1: Checking prerequisites...';
PRINT '';

-- Check if Users table exists
IF OBJECT_ID('dbo.Users', 'U') IS NULL
BEGIN
    PRINT '[ERROR] Users table does not exist!';
    PRINT 'Please ensure the main application database is set up first.';
    PRINT '';
    RAISERROR('Users table not found. Setup aborted.', 16, 1);
    RETURN;
END
ELSE
BEGIN
    PRINT '[OK] Users table found';
END

-- Check SQL Server version
DECLARE @version NVARCHAR(128) = CAST(SERVERPROPERTY('ProductVersion') AS NVARCHAR(128));
PRINT '[INFO] SQL Server version: ' + @version;
PRINT '';
GO

-- ============================================================================
-- Step 2: Create FaceEmbeddings Table
-- ============================================================================

PRINT 'Step 2: Creating FaceEmbeddings table...';
PRINT '';

-- Drop existing table if it exists (for clean setup)
IF OBJECT_ID('dbo.FaceEmbeddings', 'U') IS NOT NULL
BEGIN
    PRINT '[WARNING] FaceEmbeddings table already exists';
    PRINT '[INFO] Dropping existing table...';
    DROP TABLE dbo.FaceEmbeddings;
    PRINT '[OK] Existing table dropped';
    PRINT '';
END

-- Create FaceEmbeddings table
CREATE TABLE dbo.FaceEmbeddings (
    EmbeddingId INT PRIMARY KEY IDENTITY(1,1),
    UserId INT NOT NULL,
    EmbeddingVector NVARCHAR(MAX) NOT NULL,  -- JSON array of 128 floats
    CreatedDate DATETIME NOT NULL DEFAULT GETDATE(),
    LastUsedDate DATETIME NULL,              -- Track when embedding was last used for auth
    
    -- Foreign key constraint to Users table
    CONSTRAINT FK_FaceEmbeddings_Users 
        FOREIGN KEY (UserId) 
        REFERENCES dbo.Users(UserId)
        ON DELETE CASCADE  -- Delete embeddings when user is deleted
);
GO

PRINT '[OK] FaceEmbeddings table created successfully';
PRINT '';
GO

-- ============================================================================
-- Step 3: Create Indexes
-- ============================================================================

PRINT 'Step 3: Creating indexes for optimized queries...';
PRINT '';

-- Index on UserId for fast lookups during authentication
CREATE INDEX IX_FaceEmbeddings_UserId 
    ON dbo.FaceEmbeddings(UserId);
PRINT '[OK] Index created on UserId';

-- Index on CreatedDate for temporal queries and cleanup
CREATE INDEX IX_FaceEmbeddings_CreatedDate 
    ON dbo.FaceEmbeddings(CreatedDate);
PRINT '[OK] Index created on CreatedDate';

-- Index on LastUsedDate for identifying stale embeddings
CREATE INDEX IX_FaceEmbeddings_LastUsedDate 
    ON dbo.FaceEmbeddings(LastUsedDate);
PRINT '[OK] Index created on LastUsedDate';

PRINT '';
GO

-- ============================================================================
-- Step 4: Create Helper Stored Procedures (Optional)
-- ============================================================================

PRINT 'Step 4: Creating helper stored procedures...';
PRINT '';

-- Procedure to get embedding count for a user
IF OBJECT_ID('dbo.sp_GetUserEmbeddingCount', 'P') IS NOT NULL
    DROP PROCEDURE dbo.sp_GetUserEmbeddingCount;
GO

CREATE PROCEDURE dbo.sp_GetUserEmbeddingCount
    @UserId INT
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT COUNT(*) AS EmbeddingCount
    FROM dbo.FaceEmbeddings
    WHERE UserId = @UserId;
END
GO

PRINT '[OK] Created sp_GetUserEmbeddingCount';

-- Procedure to delete old embeddings
IF OBJECT_ID('dbo.sp_DeleteOldEmbeddings', 'P') IS NOT NULL
    DROP PROCEDURE dbo.sp_DeleteOldEmbeddings;
GO

CREATE PROCEDURE dbo.sp_DeleteOldEmbeddings
    @DaysOld INT = 365
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @CutoffDate DATETIME = DATEADD(DAY, -@DaysOld, GETDATE());
    
    DELETE FROM dbo.FaceEmbeddings
    WHERE CreatedDate < @CutoffDate
      AND (LastUsedDate IS NULL OR LastUsedDate < @CutoffDate);
    
    SELECT @@ROWCOUNT AS DeletedCount;
END
GO

PRINT '[OK] Created sp_DeleteOldEmbeddings';

-- Procedure to get user statistics
IF OBJECT_ID('dbo.sp_GetFaceRecognitionStats', 'P') IS NOT NULL
    DROP PROCEDURE dbo.sp_GetFaceRecognitionStats;
GO

CREATE PROCEDURE dbo.sp_GetFaceRecognitionStats
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        COUNT(DISTINCT UserId) AS TotalUsersWithFaces,
        COUNT(*) AS TotalEmbeddings,
        AVG(CAST(EmbeddingCount AS FLOAT)) AS AvgEmbeddingsPerUser,
        MIN(EmbeddingCount) AS MinEmbeddingsPerUser,
        MAX(EmbeddingCount) AS MaxEmbeddingsPerUser
    FROM (
        SELECT UserId, COUNT(*) AS EmbeddingCount
        FROM dbo.FaceEmbeddings
        GROUP BY UserId
    ) AS UserStats;
END
GO

PRINT '[OK] Created sp_GetFaceRecognitionStats';
PRINT '';
GO

-- ============================================================================
-- Step 5: Create Views (Optional)
-- ============================================================================

PRINT 'Step 5: Creating views...';
PRINT '';

-- View to see users with face recognition enabled
IF OBJECT_ID('dbo.vw_UsersWithFaceRecognition', 'V') IS NOT NULL
    DROP VIEW dbo.vw_UsersWithFaceRecognition;
GO

CREATE VIEW dbo.vw_UsersWithFaceRecognition
AS
SELECT 
    u.UserId,
    u.Username,
    u.Email,
    COUNT(fe.EmbeddingId) AS EmbeddingCount,
    MIN(fe.CreatedDate) AS FirstRegistrationDate,
    MAX(fe.CreatedDate) AS LastRegistrationDate,
    MAX(fe.LastUsedDate) AS LastAuthenticationDate
FROM dbo.Users u
INNER JOIN dbo.FaceEmbeddings fe ON u.UserId = fe.UserId
GROUP BY u.UserId, u.Username, u.Email;
GO

PRINT '[OK] Created vw_UsersWithFaceRecognition';
PRINT '';
GO

-- ============================================================================
-- Step 6: Insert Sample Data (Optional - for testing only)
-- ============================================================================

PRINT 'Step 6: Sample data insertion...';
PRINT '';

DECLARE @InsertSampleData CHAR(1) = 'N';  -- Change to 'Y' to insert sample data

IF @InsertSampleData = 'Y'
BEGIN
    PRINT '[INFO] Inserting sample data for testing...';
    
    -- Check if test user exists
    IF NOT EXISTS (SELECT 1 FROM dbo.Users WHERE Username = 'test_user')
    BEGIN
        PRINT '[WARNING] Test user does not exist. Skipping sample data.';
        PRINT '[INFO] To insert sample data, first create a test user.';
    END
    ELSE
    BEGIN
        DECLARE @TestUserId INT;
        SELECT @TestUserId = UserId FROM dbo.Users WHERE Username = 'test_user';
        
        -- Insert sample embeddings (these are dummy vectors, not real face data)
        INSERT INTO dbo.FaceEmbeddings (UserId, EmbeddingVector, CreatedDate)
        VALUES 
            (@TestUserId, '[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 5.0, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 6.0, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 7.0, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 8.0, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 8.9, 9.0, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8, 9.9, 10.0, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.9, 11.0, 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7, 11.8, 11.9, 12.0, 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7]', DATEADD(DAY, -5, GETDATE())),
            (@TestUserId, '[0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 5.0, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 6.0, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 7.0, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 8.0, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 8.9, 9.0, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8, 9.9, 10.0, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.9, 11.0, 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7, 11.8, 11.9, 12.0, 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.8]', DATEADD(DAY, -4, GETDATE()));
        
        PRINT '[OK] Sample data inserted';
    END
END
ELSE
BEGIN
    PRINT '[INFO] Skipping sample data insertion';
    PRINT '[INFO] To insert sample data, set @InsertSampleData = ''Y'' in this script';
END

PRINT '';
GO

-- ============================================================================
-- Step 7: Verify Installation
-- ============================================================================

PRINT 'Step 7: Verifying installation...';
PRINT '';

-- Check table exists
IF OBJECT_ID('dbo.FaceEmbeddings', 'U') IS NOT NULL
    PRINT '[OK] FaceEmbeddings table exists';
ELSE
    PRINT '[ERROR] FaceEmbeddings table not found!';

-- Check indexes
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_FaceEmbeddings_UserId')
    PRINT '[OK] UserId index exists';
ELSE
    PRINT '[WARNING] UserId index not found';

IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_FaceEmbeddings_CreatedDate')
    PRINT '[OK] CreatedDate index exists';
ELSE
    PRINT '[WARNING] CreatedDate index not found';

-- Check foreign key
IF EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_FaceEmbeddings_Users')
    PRINT '[OK] Foreign key constraint exists';
ELSE
    PRINT '[WARNING] Foreign key constraint not found';

-- Display current statistics
PRINT '';
PRINT 'Current Statistics:';
SELECT 
    COUNT(*) AS TotalEmbeddings,
    COUNT(DISTINCT UserId) AS UniqueUsers
FROM dbo.FaceEmbeddings;

PRINT '';
GO

-- ============================================================================
-- Setup Complete
-- ============================================================================

PRINT '============================================================================';
PRINT 'Database Setup Complete!';
PRINT '============================================================================';
PRINT '';
PRINT 'Next steps:';
PRINT '1. Start the OpenCV server: start_opencv_server.bat';
PRINT '2. Test the API endpoints using test_api.py';
PRINT '3. Register faces through the C# application';
PRINT '';
PRINT 'Useful queries:';
PRINT '  - View users with faces: SELECT * FROM vw_UsersWithFaceRecognition';
PRINT '  - Get statistics: EXEC sp_GetFaceRecognitionStats';
PRINT '  - Count embeddings: EXEC sp_GetUserEmbeddingCount @UserId = 1';
PRINT '';
PRINT 'For rollback instructions, see database_rollback.sql';
PRINT '============================================================================';
GO
