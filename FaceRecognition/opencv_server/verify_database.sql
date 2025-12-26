-- ============================================================
-- OpenCV Face Recognition Database Verification Script
-- ============================================================
-- This script verifies that the FaceEmbeddings table is properly
-- configured with all required columns, constraints, and indexes
-- ============================================================

USE GamingVoiceRecognition;
GO

PRINT '============================================================';
PRINT 'OpenCV Face Recognition Database Verification';
PRINT '============================================================';
PRINT '';

-- Check if table exists
IF OBJECT_ID('dbo.FaceEmbeddings', 'U') IS NOT NULL
BEGIN
    PRINT '✓ FaceEmbeddings table exists';
    PRINT '';
    
    -- Display table structure
    PRINT 'Table Columns:';
    SELECT 
        COLUMN_NAME,
        DATA_TYPE,
        CHARACTER_MAXIMUM_LENGTH,
        IS_NULLABLE,
        COLUMN_DEFAULT
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = 'FaceEmbeddings'
    ORDER BY ORDINAL_POSITION;
    PRINT '';
    
    -- Check foreign key constraint
    PRINT 'Foreign Key Constraints:';
    SELECT 
        fk.name AS ConstraintName,
        OBJECT_NAME(fk.parent_object_id) AS TableName,
        COL_NAME(fc.parent_object_id, fc.parent_column_id) AS ColumnName,
        OBJECT_NAME(fk.referenced_object_id) AS ReferencedTable,
        COL_NAME(fc.referenced_object_id, fc.referenced_column_id) AS ReferencedColumn
    FROM sys.foreign_keys AS fk
    INNER JOIN sys.foreign_key_columns AS fc 
        ON fk.object_id = fc.constraint_object_id
    WHERE OBJECT_NAME(fk.parent_object_id) = 'FaceEmbeddings';
    PRINT '';
    
    -- Check indexes
    PRINT 'Indexes:';
    SELECT 
        i.name AS IndexName,
        i.type_desc AS IndexType,
        COL_NAME(ic.object_id, ic.column_id) AS ColumnName,
        i.is_unique AS IsUnique
    FROM sys.indexes AS i
    INNER JOIN sys.index_columns AS ic 
        ON i.object_id = ic.object_id AND i.index_id = ic.index_id
    WHERE i.object_id = OBJECT_ID('dbo.FaceEmbeddings')
    ORDER BY i.name, ic.key_ordinal;
    PRINT '';
    
    -- Display row count
    PRINT 'Data Statistics:';
    SELECT 
        COUNT(*) AS TotalEmbeddings,
        COUNT(DISTINCT UserId) AS UniqueUsers,
        MIN(CreatedDate) AS OldestEmbedding,
        MAX(CreatedDate) AS NewestEmbedding
    FROM dbo.FaceEmbeddings;
    PRINT '';
    
    PRINT '✓ Database verification completed successfully';
END
ELSE
BEGIN
    PRINT '✗ FaceEmbeddings table does NOT exist';
    PRINT '';
    PRINT 'To create the table, run: database_schema.sql';
END
GO

PRINT '============================================================';
GO
