-- iPhone-Level Face Recognition Database Schema
-- Stores 128-dimensional face embeddings for each user

-- Create face embeddings table
CREATE TABLE user_face_embeddings (
    EmbeddingID INT PRIMARY KEY IDENTITY(1,1),
    UserID INT NOT NULL,
    EmbeddingData NVARCHAR(MAX) NOT NULL,  -- JSON array of 128 floats
    CaptureAngle VARCHAR(20) NOT NULL,      -- 'front', 'left', 'right', 'up', 'down'
    QualityScore FLOAT NOT NULL,            -- 0.0 to 1.0
    CaptureDate DATETIME DEFAULT GETDATE(),
    IsActive BIT DEFAULT 1,
    FOREIGN KEY (UserID) REFERENCES user_info(UserID) ON DELETE CASCADE
);

-- Create index for faster lookups
CREATE INDEX IX_user_face_embeddings_UserID ON user_face_embeddings(UserID);
CREATE INDEX IX_user_face_embeddings_IsActive ON user_face_embeddings(IsActive);

-- Add column to track face recognition enrollment status
ALTER TABLE user_info 
ADD FaceRecognitionEnrolled BIT DEFAULT 0;

-- View to get user face recognition status
CREATE VIEW vw_user_face_status AS
SELECT 
    u.UserID,
    u.FullName,
    u.Email,
    u.FaceRecognitionEnrolled,
    COUNT(e.EmbeddingID) as EmbeddingCount,
    MAX(e.CaptureDate) as LastCaptureDate,
    AVG(e.QualityScore) as AvgQualityScore
FROM user_info u
LEFT JOIN user_face_embeddings e ON u.UserID = e.UserID AND e.IsActive = 1
GROUP BY u.UserID, u.FullName, u.Email, u.FaceRecognitionEnrolled;

GO

-- Stored procedure to enroll user face
CREATE PROCEDURE sp_EnrollUserFace
    @UserID INT,
    @EmbeddingData NVARCHAR(MAX),
    @CaptureAngle VARCHAR(20),
    @QualityScore FLOAT
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Insert embedding
    INSERT INTO user_face_embeddings (UserID, EmbeddingData, CaptureAngle, QualityScore)
    VALUES (@UserID, @EmbeddingData, @CaptureAngle, @QualityScore);
    
    -- Update enrollment status
    UPDATE user_info 
    SET FaceRecognitionEnrolled = 1 
    WHERE UserID = @UserID;
    
    SELECT SCOPE_IDENTITY() AS EmbeddingID;
END;
GO

-- Stored procedure to get user embeddings
CREATE PROCEDURE sp_GetUserEmbeddings
    @UserID INT
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        EmbeddingID,
        EmbeddingData,
        CaptureAngle,
        QualityScore,
        CaptureDate
    FROM user_face_embeddings
    WHERE UserID = @UserID AND IsActive = 1
    ORDER BY QualityScore DESC;
END;
GO

-- Stored procedure to get all enrolled users
CREATE PROCEDURE sp_GetAllEnrolledUsers
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT DISTINCT
        u.UserID,
        u.FullName,
        u.Email,
        COUNT(e.EmbeddingID) as EmbeddingCount
    FROM user_info u
    INNER JOIN user_face_embeddings e ON u.UserID = e.UserID
    WHERE e.IsActive = 1
    GROUP BY u.UserID, u.FullName, u.Email
    HAVING COUNT(e.EmbeddingID) > 0;
END;
GO

-- Stored procedure to delete user face data
CREATE PROCEDURE sp_DeleteUserFaceData
    @UserID INT
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Soft delete embeddings
    UPDATE user_face_embeddings 
    SET IsActive = 0 
    WHERE UserID = @UserID;
    
    -- Update enrollment status
    UPDATE user_info 
    SET FaceRecognitionEnrolled = 0 
    WHERE UserID = @UserID;
    
    SELECT @@ROWCOUNT AS DeletedCount;
END;
GO

-- Sample queries for testing

-- Check user face recognition status
-- SELECT * FROM vw_user_face_status;

-- Get embeddings for specific user
-- EXEC sp_GetUserEmbeddings @UserID = 1;

-- Get all enrolled users
-- EXEC sp_GetAllEnrolledUsers;

-- Delete user face data
-- EXEC sp_DeleteUserFaceData @UserID = 1;
