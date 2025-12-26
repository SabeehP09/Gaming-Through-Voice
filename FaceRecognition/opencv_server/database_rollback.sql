-- ============================================================================
-- OpenCV Face Recognition Database Rollback Script
-- ============================================================================
-- This script removes all face recognition database components
-- 
-- WARNING: This will permanently delete all face embeddings!
-- Make sure to backup your data before running this script.
--
-- Usage:
--   sqlcmd -S localhost -d GamingVoiceRecognition -i database_rollback.sql
--   Or run in SQL Server Management Studio (SSMS)
-- ============================================================================

USE GamingVoiceRecognition;
GO

PRINT '============================================================================';
PRINT 'OpenCV Face Recognition Database Rollback';
PRINT '============================================================================';
PRINT '';
PRINT 'WARNING: This will delete all face recognition data!';
PRINT '';
GO

-- ============================================================================
-- Step 1: Backup Data (Optional)
-- ============================================================================

PRINT 'Step 1: Data backup...';
PRINT '';

-- Check if there is data to backup
DECLARE @EmbeddingCount INT = 0;

IF OBJECT_ID('dbo.FaceEmbeddings', 'U') IS NOT NULL
BEGIN
    SELECT @EmbeddingCount = COUNT(*) FROM dbo.FaceEmbeddings;
    
    IF @EmbeddingCount > 0
    BEGIN
        PRINT '[WARNING] Found ' + CAST(@EmbeddingCount AS VARCHAR(10)) + ' embeddings in database';
        PRINT '[INFO] Consider backing up data before proceeding';
        PRINT '[INFO] To backup: SELECT * INTO FaceEmbeddings_Backup FROM FaceEmbeddings';
        PRINT '';
    END
    ELSE
    BEGIN
        PRINT '[INFO] No embeddings found, safe to proceed';
        PRINT '';
    END
END
GO

-- ============================================================================
-- Step 2: Drop Views
-- ============================================================================

PRINT 'Step 2: Dropping views...';
PRINT '';

IF OBJECT_ID('dbo.vw_UsersWithFaceRecognition', 'V') IS NOT NULL
BEGIN
    PRINT '[INFO] Dropping view vw_UsersWithFaceRecognition...';
    DROP VIEW dbo.vw_UsersWithFaceRecognition;
    PRINT '[OK] View dropped';
END
ELSE
BEGIN
    PRINT '[INFO] View vw_UsersWithFaceRecognition does not exist';
END

PRINT '';
GO

-- ============================================================================
-- Step 3: Drop Stored Procedures
-- ============================================================================

PRINT 'Step 3: Dropping stored procedures...';
PRINT '';

IF OBJECT_ID('dbo.sp_GetUserEmbeddingCount', 'P') IS NOT NULL
BEGIN
    PRINT '[INFO] Dropping procedure sp_GetUserEmbeddingCount...';
    DROP PROCEDURE dbo.sp_GetUserEmbeddingCount;
    PRINT '[OK] Procedure dropped';
END

IF OBJECT_ID('dbo.sp_DeleteOldEmbeddings', 'P') IS NOT NULL
BEGIN
    PRINT '[INFO] Dropping procedure sp_DeleteOldEmbeddings...';
    DROP PROCEDURE dbo.sp_DeleteOldEmbeddings;
    PRINT '[OK] Procedure dropped';
END

IF OBJECT_ID('dbo.sp_GetFaceRecognitionStats', 'P') IS NOT NULL
BEGIN
    PRINT '[INFO] Dropping procedure sp_GetFaceRecognitionStats...';
    DROP PROCEDURE dbo.sp_GetFaceRecognitionStats;
    PRINT '[OK] Procedure dropped';
END

PRINT '';
GO

-- ============================================================================
-- Step 4: Drop Indexes
-- ============================================================================

PRINT 'Step 4: Dropping indexes...';
PRINT '';

IF OBJECT_ID('dbo.FaceEmbeddings', 'U') IS NOT NULL
BEGIN
    IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_FaceEmbeddings_LastUsedDate' AND object_id = OBJECT_ID('dbo.FaceEmbeddings'))
    BEGIN
        PRINT '[INFO] Dropping index IX_FaceEmbeddings_LastUsedDate...';
        DROP INDEX IX_FaceEmbeddings_LastUsedDate ON dbo.FaceEmbeddings;
        PRINT '[OK] Index dropped';
    END

    IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_FaceEmbeddings_CreatedDate' AND object_id = OBJECT_ID('dbo.FaceEmbeddings'))
    BEGIN
        PRINT '[INFO] Dropping index IX_FaceEmbeddings_CreatedDate...';
        DROP INDEX IX_FaceEmbeddings_CreatedDate ON dbo.FaceEmbeddings;
        PRINT '[OK] Index dropped';
    END

    IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_FaceEmbeddings_UserId' AND object_id = OBJECT_ID('dbo.FaceEmbeddings'))
    BEGIN
        PRINT '[INFO] Dropping index IX_FaceEmbeddings_UserId...';
        DROP INDEX IX_FaceEmbeddings_UserId ON dbo.FaceEmbeddings;
        PRINT '[OK] Index dropped';
    END
END

PRINT '';
GO

-- ============================================================================
-- Step 5: Drop Foreign Key Constraint
-- ============================================================================

PRINT 'Step 5: Dropping foreign key constraint...';
PRINT '';

IF EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_FaceEmbeddings_Users')
BEGIN
    PRINT '[INFO] Dropping foreign key FK_FaceEmbeddings_Users...';
    ALTER TABLE dbo.FaceEmbeddings DROP CONSTRAINT FK_FaceEmbeddings_Users;
    PRINT '[OK] Foreign key dropped';
END
ELSE
BEGIN
    PRINT '[INFO] Foreign key does not exist or already dropped';
END

PRINT '';
GO

-- ============================================================================
-- Step 6: Drop Table
-- ============================================================================

PRINT 'Step 6: Dropping FaceEmbeddings table...';
PRINT '';

IF OBJECT_ID('dbo.FaceEmbeddings', 'U') IS NOT NULL
BEGIN
    PRINT '[INFO] Dropping FaceEmbeddings table...';
    DROP TABLE dbo.FaceEmbeddings;
    PRINT '[OK] Table dropped successfully';
END
ELSE
BEGIN
    PRINT '[INFO] FaceEmbeddings table does not exist';
END

PRINT '';
GO

-- ============================================================================
-- Step 7: Verify Rollback
-- ============================================================================

PRINT 'Step 7: Verifying rollback...';
PRINT '';

-- Check table
IF OBJECT_ID('dbo.FaceEmbeddings', 'U') IS NULL
    PRINT '[OK] FaceEmbeddings table removed';
ELSE
    PRINT '[ERROR] FaceEmbeddings table still exists!';

-- Check views
IF OBJECT_ID('dbo.vw_UsersWithFaceRecognition', 'V') IS NULL
    PRINT '[OK] Views removed';
ELSE
    PRINT '[WARNING] Some views still exist';

-- Check procedures
IF OBJECT_ID('dbo.sp_GetUserEmbeddingCount', 'P') IS NULL
   AND OBJECT_ID('dbo.sp_DeleteOldEmbeddings', 'P') IS NULL
   AND OBJECT_ID('dbo.sp_GetFaceRecognitionStats', 'P') IS NULL
    PRINT '[OK] Stored procedures removed';
ELSE
    PRINT '[WARNING] Some stored procedures still exist';

PRINT '';
GO

-- ============================================================================
-- Rollback Complete
-- ============================================================================

PRINT '============================================================================';
PRINT 'Rollback Complete!';
PRINT '============================================================================';
PRINT '';
PRINT 'All face recognition database components have been removed.';
PRINT '';
PRINT 'To reinstall:';
PRINT '  Run setup_database.sql';
PRINT '';
PRINT 'Note: This does not affect the Users table or other application data.';
PRINT '============================================================================';
GO
