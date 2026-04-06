using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using System.Diagnostics;
using AForge.Video;
using AForge.Video.DirectShow;
using Newtonsoft.Json;

namespace GamingThroughVoiceRecognitionSystem.Services
{
    /// <summary>
    /// Face Recognition Service using OpenCV Python server backend.
    /// Communicates with Flask REST API for face detection and recognition.
    /// 
    /// Requirements: 6.5
    /// </summary>
    public class FaceRecognitionService_OpenCV : IDisposable
    {
        private readonly HttpClient _httpClient;
        private readonly string _serverUrl;
        private FilterInfoCollection _videoDevices;
        private VideoCaptureDevice _videoSource;
        private Bitmap _currentFrame;
        private bool _disposed = false;
        private bool _serverAvailable = false;
        private DateTime _lastHealthCheck = DateTime.MinValue;

        // Server configuration
        private const string DEFAULT_SERVER_URL = "http://localhost:5000";
        private const int REQUEST_TIMEOUT_SECONDS = 5;
        private const int HEALTH_CHECK_INTERVAL_SECONDS = 30;

        /// <summary>
        /// Initialize the Face Recognition Service with OpenCV backend.
        /// </summary>
        /// <param name="serverUrl">URL of the OpenCV Flask server (default: http://localhost:5000)</param>
        public FaceRecognitionService_OpenCV(string serverUrl = DEFAULT_SERVER_URL)
        {
            _serverUrl = serverUrl;
            
            // Initialize HTTP client with timeout
            _httpClient = new HttpClient
            {
                Timeout = TimeSpan.FromSeconds(REQUEST_TIMEOUT_SECONDS)
            };
            
            // Initialize video devices
            try
            {
                _videoDevices = new FilterInfoCollection(FilterCategory.VideoInputDevice);
                Debug.WriteLine($"[OpenCV Service] Found {_videoDevices.Count} video devices");
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[OpenCV Service] Error initializing video devices: {ex.Message}");
                _videoDevices = null;
            }
        }

        /// <summary>
        /// Check if a webcam is available.
        /// Requirements: 8.2
        /// </summary>
        public bool IsCameraAvailable()
        {
            return _videoDevices != null && _videoDevices.Count > 0;
        }

        /// <summary>
        /// Check if the OpenCV server is available and healthy.
        /// Caches the result for HEALTH_CHECK_INTERVAL_SECONDS to avoid excessive requests.
        /// Requirements: 8.1
        /// </summary>
        /// <param name="forceCheck">Force a health check even if cached result is available</param>
        /// <returns>True if server is available and healthy, false otherwise</returns>
        public async Task<bool> CheckServerHealthAsync(bool forceCheck = false)
        {
            try
            {
                // Check if we have a recent cached result
                TimeSpan timeSinceLastCheck = DateTime.Now - _lastHealthCheck;
                if (!forceCheck && timeSinceLastCheck.TotalSeconds < HEALTH_CHECK_INTERVAL_SECONDS)
                {
                    Debug.WriteLine($"[OpenCV Service] Using cached health check result: {_serverAvailable}");
                    return _serverAvailable;
                }

                Debug.WriteLine("[OpenCV Service] Performing health check...");

                // Call /health endpoint
                string url = $"{_serverUrl}/health";
                HttpResponseMessage response = await _httpClient.GetAsync(url);

                if (response.IsSuccessStatusCode)
                {
                    string responseContent = await response.Content.ReadAsStringAsync();
                    var result = JsonConvert.DeserializeObject<dynamic>(responseContent);

                    bool modelsLoaded = result.models_loaded;
                    bool databaseConnected = result.database_connected;

                    _serverAvailable = modelsLoaded && databaseConnected;
                    _lastHealthCheck = DateTime.Now;

                    Debug.WriteLine($"[OpenCV Service] Health check result: Server available={_serverAvailable}, Models loaded={modelsLoaded}, Database connected={databaseConnected}");

                    return _serverAvailable;
                }
                else
                {
                    Debug.WriteLine($"[OpenCV Service] Health check failed: HTTP {response.StatusCode}");
                    _serverAvailable = false;
                    _lastHealthCheck = DateTime.Now;
                    return false;
                }
            }
            catch (TaskCanceledException ex)
            {
                Debug.WriteLine($"[OpenCV Service] Health check timeout: {ex.Message}");
                _serverAvailable = false;
                _lastHealthCheck = DateTime.Now;
                return false;
            }
            catch (HttpRequestException ex)
            {
                Debug.WriteLine($"[OpenCV Service] Health check failed - server not reachable: {ex.Message}");
                _serverAvailable = false;
                _lastHealthCheck = DateTime.Now;
                return false;
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[OpenCV Service] Health check error: {ex.Message}");
                _serverAvailable = false;
                _lastHealthCheck = DateTime.Now;
                return false;
            }
        }

        /// <summary>
        /// Get the current server availability status (cached).
        /// Requirements: 8.1
        /// </summary>
        public bool IsServerAvailable()
        {
            return _serverAvailable;
        }

        /// <summary>
        /// Get detailed webcam availability information with troubleshooting guidance.
        /// Requirements: 8.2
        /// </summary>
        /// <returns>Tuple containing availability status and detailed message</returns>
        public (bool available, string message) GetWebcamStatus()
        {
            try
            {
                if (_videoDevices == null)
                {
                    return (false, 
                        "Unable to access video devices.\n\n" +
                        "Troubleshooting:\n" +
                        "• Check Windows privacy settings for camera access\n" +
                        "• Ensure no other application is using the webcam\n" +
                        "• Restart the application\n\n" +
                        "Alternative: Use password or voice authentication");
                }

                if (_videoDevices.Count == 0)
                {
                    return (false, 
                        "No webcam detected.\n\n" +
                        "Troubleshooting:\n" +
                        "• Connect a webcam to your computer\n" +
                        "• Check if webcam drivers are installed\n" +
                        "• Try a different USB port\n" +
                        "• Restart your computer\n\n" +
                        "Alternative: Use password or voice authentication");
                }

                return (true, $"Webcam available: {_videoDevices[0].Name}");
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[OpenCV Service] Error checking webcam status: {ex.Message}");
                return (false, 
                    $"Error checking webcam: {ex.Message}\n\n" +
                    "Alternative: Use password or voice authentication");
            }
        }

        /// <summary>
        /// Dispose of resources.
        /// </summary>
        public void Dispose()
        {
            Dispose(true);
            GC.SuppressFinalize(this);
        }

        /// <summary>
        /// Protected dispose method.
        /// </summary>
        protected virtual void Dispose(bool disposing)
        {
            if (!_disposed)
            {
                if (disposing)
                {
                    // Dispose managed resources
                    StopCamera();
                    _httpClient?.Dispose();
                    
                    if (_currentFrame != null)
                    {
                        _currentFrame.Dispose();
                        _currentFrame = null;
                    }
                }
                
                _disposed = true;
            }
        }

        /// <summary>
        /// Stop the camera if it's running.
        /// </summary>
        private void StopCamera()
        {
            if (_videoSource != null && _videoSource.IsRunning)
            {
                _videoSource.SignalToStop();
                _videoSource.WaitForStop();
                _videoSource.NewFrame -= VideoSource_NewFrame;
                _videoSource = null;
            }
        }

        /// <summary>
        /// Event handler for new video frames.
        /// </summary>
        private void VideoSource_NewFrame(object sender, NewFrameEventArgs eventArgs)
        {
            // Dispose previous frame
            if (_currentFrame != null)
            {
                _currentFrame.Dispose();
            }
            
            // Clone the new frame
            _currentFrame = (Bitmap)eventArgs.Frame.Clone();
        }

        /// <summary>
        /// Convert a Bitmap to base64 encoded string.
        /// Requirements: 6.3, 6.4, 6.5
        /// </summary>
        /// <param name="image">Bitmap image to encode</param>
        /// <returns>Base64 encoded string</returns>
        private string ConvertToBase64(Bitmap image)
        {
            try
            {
                using (MemoryStream ms = new MemoryStream())
                {
                    // Save as PNG for lossless compression
                    image.Save(ms, ImageFormat.Png);
                    byte[] imageBytes = ms.ToArray();
                    string base64String = Convert.ToBase64String(imageBytes);
                    
                    Debug.WriteLine($"[OpenCV Service] Converted image to base64: {base64String.Length} characters");
                    return base64String;
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[OpenCV Service] Error converting image to base64: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Send HTTP POST request to OpenCV server.
        /// Requirements: 6.3, 6.4, 6.5
        /// </summary>
        /// <param name="endpoint">API endpoint (e.g., "/register", "/authenticate")</param>
        /// <param name="payload">JSON payload object</param>
        /// <returns>HTTP response message</returns>
        /// <exception cref="HttpRequestException">Thrown when server is unavailable or request fails</exception>
        private async Task<HttpResponseMessage> SendToServerAsync(string endpoint, object payload)
        {
            try
            {
                string url = $"{_serverUrl}{endpoint}";
                Debug.WriteLine($"[OpenCV Service] Sending POST request to: {url}");

                // Serialize payload to JSON
                string jsonPayload = JsonConvert.SerializeObject(payload);
                var content = new StringContent(jsonPayload, Encoding.UTF8, "application/json");

                // Send POST request
                HttpResponseMessage response = await _httpClient.PostAsync(url, content);
                
                Debug.WriteLine($"[OpenCV Service] Response status: {response.StatusCode}");
                
                return response;
            }
            catch (TaskCanceledException ex)
            {
                Debug.WriteLine($"[OpenCV Service] Request timeout: {ex.Message}");
                throw new HttpRequestException($"Request to OpenCV server timed out after {REQUEST_TIMEOUT_SECONDS} seconds. Please ensure the server is running.", ex);
            }
            catch (HttpRequestException ex)
            {
                Debug.WriteLine($"[OpenCV Service] HTTP request failed: {ex.Message}");
                throw new HttpRequestException($"Failed to connect to OpenCV server at {_serverUrl}. Please ensure the server is running.", ex);
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[OpenCV Service] Unexpected error sending request: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Capture a single image from the webcam.
        /// Requirements: 1.1, 2.1, 7.5, 8.2
        /// </summary>
        /// <returns>Bitmap image from webcam, or null if capture fails</returns>
        /// <exception cref="InvalidOperationException">Thrown when webcam is not available</exception>
        public Bitmap CaptureWebcamImage()
        {
            try
            {
                // Check if camera is available
                // Requirements: 8.2
                if (!IsCameraAvailable())
                {
                    string troubleshootingMsg = 
                        "No webcam device found.\n\n" +
                        "Troubleshooting steps:\n" +
                        "1. Ensure webcam is connected\n" +
                        "2. Check if webcam is being used by another application\n" +
                        "3. Restart the application\n" +
                        "4. Check Windows privacy settings for camera access\n\n" +
                        "Alternative: Use password authentication";
                    throw new InvalidOperationException(troubleshootingMsg);
                }

                // Start camera if not already running
                bool wasRunning = _videoSource != null && _videoSource.IsRunning;
                
                if (!wasRunning)
                {
                    Debug.WriteLine("[OpenCV Service] Starting webcam for capture...");
                    _videoSource = new VideoCaptureDevice(_videoDevices[0].MonikerString);
                    _videoSource.NewFrame += VideoSource_NewFrame;
                    _videoSource.Start();
                    
                    // Wait for camera to initialize and capture first frame
                    System.Threading.Thread.Sleep(1000);
                }

                // Wait a bit more to ensure we have a current frame
                if (_currentFrame == null)
                {
                    System.Threading.Thread.Sleep(500);
                }

                // Check if we have a frame
                if (_currentFrame == null)
                {
                    throw new InvalidOperationException("Failed to capture frame from webcam. Please ensure the webcam is working properly.");
                }

                // Clone the current frame to return
                Bitmap capturedFrame = (Bitmap)_currentFrame.Clone();
                
                Debug.WriteLine($"[OpenCV Service] Captured frame: {capturedFrame.Width}x{capturedFrame.Height}");

                // Stop camera if we started it (release resources)
                if (!wasRunning)
                {
                    StopCamera();
                    Debug.WriteLine("[OpenCV Service] Webcam stopped after capture");
                }

                return capturedFrame;
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[OpenCV Service] Error capturing webcam image: {ex.Message}");
                
                // Clean up on error
                StopCamera();
                
                throw;
            }
        }

        /// <summary>
        /// Register face for a user by capturing multiple images and sending to OpenCV server.
        /// Enforces minimum embeddings requirement: exactly 5 images must be successfully captured.
        /// Requirements: 1.1, 1.2, 1.3, 1.4, 7.1
        /// </summary>
        /// <param name="userId">User ID to register face for</param>
        /// <param name="progressCallback">Optional callback for progress updates (current, total)</param>
        /// <returns>Tuple containing success status, message, and embeddings count</returns>
        public async Task<(bool success, string message, int embeddingsCount)> RegisterFaceAsync(
            int userId, 
            Action<int, int> progressCallback = null)
        {
            const int REQUIRED_IMAGES = 5;  // Requirements: 1.4 - Minimum embeddings per user
            const int DELAY_BETWEEN_CAPTURES_MS = 500;
            
            int successfulCaptures = 0;
            var failureReasons = new System.Collections.Generic.List<string>();
            
            try
            {
                Debug.WriteLine($"[OpenCV Service] Starting face registration for user {userId}");
                Debug.WriteLine($"[OpenCV Service] REQUIREMENT: Must capture exactly {REQUIRED_IMAGES} images with detected faces");

                // Check server health first
                bool serverHealthy = await CheckServerHealthAsync(forceCheck: true);
                if (!serverHealthy)
                {
                    return (false, "Face recognition server is not available. Please ensure the server is running at " + _serverUrl, 0);
                }

                // Check if camera is available
                if (!IsCameraAvailable())
                {
                    return (false, "No webcam device found. Please connect a webcam and try again.", 0);
                }

                // Start camera
                Debug.WriteLine("[OpenCV Service] Starting webcam...");
                _videoSource = new VideoCaptureDevice(_videoDevices[0].MonikerString);
                _videoSource.NewFrame += VideoSource_NewFrame;
                _videoSource.Start();
                
                // Wait for camera to initialize
                await Task.Delay(1000);

                // Capture and register multiple images
                // Requirements: 1.4 - Store at least 5 face embeddings per user
                for (int i = 0; i < REQUIRED_IMAGES; i++)
                {
                    try
                    {
                        Debug.WriteLine($"[OpenCV Service] Capturing image {i + 1}/{REQUIRED_IMAGES}...");
                        
                        // Report progress
                        progressCallback?.Invoke(i + 1, REQUIRED_IMAGES);

                        // Ensure we have a current frame
                        if (_currentFrame == null)
                        {
                            await Task.Delay(500);
                        }

                        if (_currentFrame == null)
                        {
                            string error = $"No frame available for capture {i + 1}";
                            Debug.WriteLine($"[OpenCV Service] {error}");
                            failureReasons.Add(error);
                            continue;
                        }

                        // Clone the current frame
                        Bitmap capturedImage = (Bitmap)_currentFrame.Clone();

                        // Convert to base64
                        string base64Image = ConvertToBase64(capturedImage);

                        // SECURITY: Dispose the captured image immediately after encoding
                        // Requirements: 10.1, 10.3 - No raw images stored
                        capturedImage.Dispose();
                        capturedImage = null;

                        // Prepare request payload
                        var payload = new
                        {
                            user_id = userId,
                            image = base64Image
                        };

                        // Send to server
                        HttpResponseMessage response = await SendToServerAsync("/register", payload);

                        // Parse response
                        string responseContent = await response.Content.ReadAsStringAsync();
                        
                        if (response.IsSuccessStatusCode)
                        {
                            var result = JsonConvert.DeserializeObject<dynamic>(responseContent);
                            bool success = result.success;
                            
                            if (success)
                            {
                                successfulCaptures++;
                                int embeddingsCount = result.embeddings_count != null ? (int)result.embeddings_count : successfulCaptures;
                                int minimumRequired = result.minimum_required != null ? (int)result.minimum_required : REQUIRED_IMAGES;
                                bool registrationComplete = result.registration_complete != null ? (bool)result.registration_complete : false;
                                
                                Debug.WriteLine($"[OpenCV Service] Successfully registered image {i + 1}/{REQUIRED_IMAGES}");
                                Debug.WriteLine($"[OpenCV Service] Progress: {embeddingsCount}/{minimumRequired} embeddings stored. Complete: {registrationComplete}");
                            }
                            else
                            {
                                string errorMessage = result.message;
                                Debug.WriteLine($"[OpenCV Service] Failed to register image {i + 1}: {errorMessage}");
                                failureReasons.Add($"Image {i + 1}: {errorMessage}");
                            }
                        }
                        else
                        {
                            string errorMsg = $"Server error for image {i + 1}: {response.StatusCode}";
                            Debug.WriteLine($"[OpenCV Service] {errorMsg}");
                            Debug.WriteLine($"[OpenCV Service] Response: {responseContent}");
                            failureReasons.Add(errorMsg);
                        }

                        // SECURITY: Clear base64 string from memory after transmission
                        // Requirements: 10.1, 10.3 - No image data persisted
                        base64Image = null;
                        GC.Collect(); // Force garbage collection to clear sensitive data

                        // Delay between captures
                        if (i < REQUIRED_IMAGES - 1)
                        {
                            await Task.Delay(DELAY_BETWEEN_CAPTURES_MS);
                        }
                    }
                    catch (Exception ex)
                    {
                        string error = $"Error capturing/registering image {i + 1}: {ex.Message}";
                        Debug.WriteLine($"[OpenCV Service] {error}");
                        failureReasons.Add(error);
                    }
                }

                // Stop camera
                StopCamera();

                // ENFORCEMENT: Requirements 1.4 - Must have exactly 5 successful embeddings
                if (successfulCaptures == REQUIRED_IMAGES)
                {
                    Debug.WriteLine($"[OpenCV Service] Registration SUCCESSFUL: All {REQUIRED_IMAGES}/{REQUIRED_IMAGES} images registered");
                    return (true, $"Face registration successful! All {REQUIRED_IMAGES} images captured and registered.", successfulCaptures);
                }
                else if (successfulCaptures > 0)
                {
                    Debug.WriteLine($"[OpenCV Service] Registration FAILED: Only {successfulCaptures}/{REQUIRED_IMAGES} images registered");
                    string detailedMessage = $"Registration incomplete: Only {successfulCaptures} out of {REQUIRED_IMAGES} required images were successfully registered.\n\n" +
                                           $"Please try again and ensure:\n" +
                                           $"• Your face is clearly visible and well-lit\n" +
                                           $"• You remain in frame for all {REQUIRED_IMAGES} captures\n" +
                                           $"• Only one face is visible in the frame\n\n" +
                                           $"Click 'Register Face' to retry.";
                    
                    if (failureReasons.Count > 0)
                    {
                        Debug.WriteLine($"[OpenCV Service] Failure reasons: {string.Join("; ", failureReasons)}");
                    }
                    
                    return (false, detailedMessage, successfulCaptures);
                }
                else
                {
                    Debug.WriteLine($"[OpenCV Service] Registration FAILED: No images were successfully registered");
                    string detailedMessage = "Registration failed: No face detected in any of the captured images.\n\n" +
                                           "Please ensure:\n" +
                                           "• Your face is clearly visible and centered\n" +
                                           "• The lighting is adequate\n" +
                                           "• The webcam is working properly\n" +
                                           "• Only one face is visible in the frame\n\n" +
                                           "Click 'Register Face' to retry.";
                    return (false, detailedMessage, 0);
                }
            }
            catch (HttpRequestException ex)
            {
                Debug.WriteLine($"[OpenCV Service] Server communication error: {ex.Message}");
                StopCamera();
                return (false, $"Failed to connect to face recognition server: {ex.Message}\n\nPlease ensure the OpenCV server is running.", successfulCaptures);
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[OpenCV Service] Registration error: {ex.Message}");
                StopCamera();
                return (false, $"Face registration failed: {ex.Message}\n\nPlease try again.", successfulCaptures);
            }
        }

        /// <summary>
        /// Validate that a user has completed registration with minimum required embeddings.
        /// Requirements: 1.4
        /// </summary>
        /// <param name="userId">User ID to validate</param>
        /// <returns>Tuple containing validation status, embeddings count, and message</returns>
        public async Task<(bool valid, int embeddingsCount, string message)> ValidateRegistrationAsync(int userId)
        {
            try
            {
                Debug.WriteLine($"[OpenCV Service] Validating registration for user {userId}");

                // Check server health first
                bool serverHealthy = await CheckServerHealthAsync(forceCheck: false);
                if (!serverHealthy)
                {
                    return (false, 0, "Face recognition server is not available.");
                }

                // Prepare request payload
                var payload = new
                {
                    user_id = userId
                };

                // Send to server
                HttpResponseMessage response = await SendToServerAsync("/validate_registration", payload);

                // Parse response
                string responseContent = await response.Content.ReadAsStringAsync();
                Debug.WriteLine($"[OpenCV Service] Validation response: {responseContent}");

                var result = JsonConvert.DeserializeObject<dynamic>(responseContent);
                
                bool valid = result.valid;
                int embeddingsCount = result.embeddings_count != null ? (int)result.embeddings_count : 0;
                int minimumRequired = result.minimum_required != null ? (int)result.minimum_required : 5;
                string message = result.message;

                Debug.WriteLine($"[OpenCV Service] Validation result: Valid={valid}, Count={embeddingsCount}/{minimumRequired}");

                return (valid, embeddingsCount, message);
            }
            catch (HttpRequestException ex)
            {
                Debug.WriteLine($"[OpenCV Service] Server communication error: {ex.Message}");
                return (false, 0, "Failed to connect to face recognition server.");
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[OpenCV Service] Validation error: {ex.Message}");
                return (false, 0, $"Validation failed: {ex.Message}");
            }
        }

        /// <summary>
        /// Authenticate a user by capturing a single image and comparing with stored embeddings.
        /// Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 7.2
        /// </summary>
        /// <param name="userId">User ID to authenticate</param>
        /// <returns>Tuple containing success status, confidence score, and message</returns>
        public async Task<(bool success, double confidence, string message)> AuthenticateFaceAsync(int userId)
        {
            Bitmap capturedImage = null;
            
            try
            {
                Debug.WriteLine($"[OpenCV Service] Starting face authentication for user {userId}");

                // Check server health first
                bool serverHealthy = await CheckServerHealthAsync(forceCheck: true);
                if (!serverHealthy)
                {
                    return (false, 0.0, "Face recognition server is not available. Please ensure the server is running or use password authentication.");
                }

                // Capture image from webcam
                try
                {
                    capturedImage = CaptureWebcamImage();
                }
                catch (InvalidOperationException ex)
                {
                    Debug.WriteLine($"[OpenCV Service] Webcam error: {ex.Message}");
                    return (false, 0.0, ex.Message);
                }

                if (capturedImage == null)
                {
                    return (false, 0.0, "Failed to capture image from webcam.");
                }

                Debug.WriteLine($"[OpenCV Service] Image captured: {capturedImage.Width}x{capturedImage.Height}");

                // Convert to base64
                string base64Image = ConvertToBase64(capturedImage);

                // SECURITY: Dispose the captured image immediately after encoding
                // Requirements: 10.1, 10.3 - No raw images stored
                capturedImage.Dispose();
                capturedImage = null;

                // Prepare request payload
                var payload = new
                {
                    user_id = userId,
                    image = base64Image
                };

                // Send to server
                HttpResponseMessage response = await SendToServerAsync("/authenticate", payload);

                // Parse response
                string responseContent = await response.Content.ReadAsStringAsync();
                Debug.WriteLine($"[OpenCV Service] Server response: {responseContent}");

                // SECURITY: Clear base64 string from memory after transmission
                // Requirements: 10.1, 10.3 - No image data persisted
                base64Image = null;
                GC.Collect(); // Force garbage collection to clear sensitive data

                // Parse JSON response
                var result = JsonConvert.DeserializeObject<dynamic>(responseContent);
                
                bool success = result.success;
                double confidence = result.confidence != null ? (double)result.confidence : 0.0;
                string message = result.message;

                if (response.IsSuccessStatusCode)
                {
                    if (success)
                    {
                        Debug.WriteLine($"[OpenCV Service] Authentication SUCCESS: confidence={confidence:P2}");
                        return (true, confidence, message);
                    }
                    else
                    {
                        // Authentication failed but request was successful
                        Debug.WriteLine($"[OpenCV Service] Authentication FAILED: confidence={confidence:P2}");
                        return (false, confidence, message);
                    }
                }
                else
                {
                    // Handle error responses
                    string errorCode = result.error_code;
                    
                    Debug.WriteLine($"[OpenCV Service] Server error: {errorCode} - {message}");
                    
                    // Provide user-friendly error messages
                    switch (errorCode)
                    {
                        case "NO_FACE_DETECTED":
                            return (false, 0.0, "No face detected. Please ensure your face is clearly visible and well-lit.");
                        
                        case "MULTIPLE_FACES_DETECTED":
                            return (false, 0.0, "Multiple faces detected. Please ensure only your face is visible in the frame.");
                        
                        case "NO_EMBEDDINGS_FOUND":
                            return (false, 0.0, "❌ No face data found.\n\nPlease register your face first from:\n• Sign up (for new users)\n• Profile settings (for existing users)");
                        
                        case "INSUFFICIENT_EMBEDDINGS":
                            return (false, 0.0, message ?? "⚠️ Registration incomplete.\n\nPlease complete face registration with all 5 required images from your profile settings.");
                        
                        case "SERVER_NOT_READY":
                            return (false, 0.0, "Face recognition server is not ready. Please try again in a moment.");
                        
                        default:
                            return (false, confidence, message ?? "Authentication failed due to server error.");
                    }
                }
            }
            catch (HttpRequestException ex)
            {
                Debug.WriteLine($"[OpenCV Service] Server communication error: {ex.Message}");
                return (false, 0.0, $"Failed to connect to face recognition server. Please ensure the server is running.");
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[OpenCV Service] Authentication error: {ex.Message}");
                return (false, 0.0, $"Authentication failed: {ex.Message}");
            }
            finally
            {
                // Ensure image is disposed
                if (capturedImage != null)
                {
                    capturedImage.Dispose();
                }
            }
        }
    }
}
