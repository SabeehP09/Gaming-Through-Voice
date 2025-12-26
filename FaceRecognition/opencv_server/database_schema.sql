-- ============================================================
-- OpenCV Face Recognition Database Schema
-- ============================================================
-- This script creates the FaceEmbeddings table for storing
-- face recognition embeddings (128-dimensional vectors)
-- ============================================================

USE GamingVoiceRecognition;
GO

-- Check if table already exists and drop if needed (for clean setup)
IF OBJECT_ID('dbo.FaceEmbeddings', 'U') IS NOT NULL
BEGIN
    PRINT 'Dropping existing FaceEmbeddings table...';
    DROP TABLE dbo.FaceEmbeddings;
END
GO

-- Create FaceEmbeddings table
CREATE TABLE dbo.FaceEmbeddings (
    EmbeddingId INT PRIMARY KEY IDENTITY(1,1),
    UserId INT NOT NULL,
    EmbeddingVector NVARCHAR(MAX) NOT NULL,  -- JSON array of 128 floats
    CreatedDate DATETIME NOT NULL DEFAULT GETDATE(),
    
    -- Foreign key constraint to Users table
    CONSTRAINT FK_FaceEmbeddings_Users 
        FOREIGN KEY (UserId) 
        REFERENCES dbo.Users(UserId)
        ON DELETE CASCADE  -- Delete embeddings when user is deleted
);
GO

-- Create index on UserId for fast lookups
CREATE INDEX IX_FaceEmbeddings_UserId 
    ON dbo.FaceEmbeddings(UserId);
GO

-- Create index on CreatedDate for temporal queries
CREATE INDEX IX_FaceEmbeddings_CreatedDate 
    ON dbo.FaceEmbeddings(CreatedDate);
GO

PRINT '✓ FaceEmbeddings table created successfully';
PRINT '✓ Foreign key constraint added to Users table';
PRINT '✓ Indexes created for optimized queries';
GO

-- Display table structure
PRINT '';
PRINT 'Table Structure:';
EXEC sp_help 'dbo.FaceEmbeddings';
GO

-- Sample query to verify table is empty
PRINT '';
PRINT 'Current row count:';
SELECT COUNT(*) AS TotalEmbeddings FROM dbo.FaceEmbeddings;
GO
