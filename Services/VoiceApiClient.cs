using System;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;

namespace GamingThroughVoiceRecognitionSystem.Services
{
    /// <summary>
    /// Client for communicating with Python Voice Recognition API
    /// </summary>
    public class VoiceApiClient
    {
        private readonly HttpClient httpClient;
        private readonly string baseUrl;

        public VoiceApiClient(string baseUrl = "http://localhost:5000")
        {
            this.baseUrl = baseUrl;
            httpClient = new HttpClient
            {
                Timeout = TimeSpan.FromSeconds(30)
            };
        }

        #region Authentication Methods

        /// <summary>
        /// Enroll a user for voice authentication
        /// </summary>
        public async Task<EnrollmentResponse> EnrollUserAsync(int userId, byte[] audioData)
        {
            try
            {
                var request = new
                {
                    user_id = userId,
                    audio_data = Convert.ToBase64String(audioData)
                };

                var response = await PostAsync<EnrollmentResponse>("/auth/enroll", request);
                return response;
            }
            catch (Exception ex)
            {
                return new EnrollmentResponse
                {
                    Success = false,
                    Message = $"Enrollment failed: {ex.Message}"
                };
            }
        }

        /// <summary>
        /// Verify user identity through voice
        /// </summary>
        public async Task<VerificationResponse> VerifyUserAsync(int userId, byte[] audioData, double threshold = -50)
        {
            try
            {
                var request = new
                {
                    user_id = userId,
                    audio_data = Convert.ToBase64String(audioData),
                    threshold = threshold
                };

                var response = await PostAsync<VerificationResponse>("/auth/verify", request);
                return response;
            }
            catch (Exception ex)
            {
                return new VerificationResponse
                {
                    Verified = false,
                    Confidence = 0,
                    UserId = userId,
                    Error = ex.Message
                };
            }
        }

        /// <summary>
        /// Identify which user is speaking
        /// </summary>
        public async Task<IdentificationResponse> IdentifyUserAsync(byte[] audioData, double threshold = -50)
        {
            try
            {
                var request = new
                {
                    audio_data = Convert.ToBase64String(audioData),
                    threshold = threshold
                };

                var response = await PostAsync<IdentificationResponse>("/auth/identify", request);
                return response;
            }
            catch (Exception ex)
            {
                return new IdentificationResponse
                {
                    Identified = false,
                    UserId = null,
                    Confidence = 0,
                    Error = ex.Message
                };
            }
        }

        /// <summary>
        /// Delete user's voice model
        /// </summary>
        public async Task<DeleteResponse> DeleteUserAsync(int userId)
        {
            try
            {
                var request = new { user_id = userId };
                var response = await PostAsync<DeleteResponse>("/auth/delete", request);
                return response;
            }
            catch (Exception ex)
            {
                return new DeleteResponse
                {
                    Success = false,
                    Message = $"Deletion failed: {ex.Message}"
                };
            }
        }

        #endregion

        #region Command Recognition Methods

        /// <summary>
        /// Recognize voice command from audio
        /// </summary>
        public async Task<CommandRecognitionResponse> RecognizeCommandAsync(byte[] audioData, double threshold = 0.7)
        {
            try
            {
                var request = new
                {
                    audio_data = Convert.ToBase64String(audioData),
                    threshold = threshold
                };

                var response = await PostAsync<CommandRecognitionResponse>("/commands/recognize", request);
                return response;
            }
            catch (Exception ex)
            {
                return new CommandRecognitionResponse
                {
                    Recognized = false,
                    Text = null,
                    Category = null,
                    Action = null,
                    Confidence = 0,
                    Error = ex.Message
                };
            }
        }

        /// <summary>
        /// Get list of available commands
        /// </summary>
        public async Task<CommandListResponse> GetCommandsAsync(string category = null)
        {
            try
            {
                string url = "/commands/list";
                if (!string.IsNullOrEmpty(category))
                {
                    url += $"?category={category}";
                }

                var response = await GetAsync<CommandListResponse>(url);
                return response;
            }
            catch (Exception ex)
            {
                return new CommandListResponse
                {
                    Commands = null,
                    Error = ex.Message
                };
            }
        }

        /// <summary>
        /// Add a new voice command
        /// </summary>
        public async Task<AddCommandResponse> AddCommandAsync(string category, string phrase, string action)
        {
            try
            {
                var request = new
                {
                    category = category,
                    phrase = phrase,
                    action = action
                };

                var response = await PostAsync<AddCommandResponse>("/commands/add", request);
                return response;
            }
            catch (Exception ex)
            {
                return new AddCommandResponse
                {
                    Success = false,
                    Message = $"Failed to add command: {ex.Message}"
                };
            }
        }

        /// <summary>
        /// Remove a voice command
        /// </summary>
        public async Task<RemoveCommandResponse> RemoveCommandAsync(string category, string phrase)
        {
            try
            {
                var request = new
                {
                    category = category,
                    phrase = phrase
                };

                var response = await PostAsync<RemoveCommandResponse>("/commands/remove", request);
                return response;
            }
            catch (Exception ex)
            {
                return new RemoveCommandResponse
                {
                    Success = false,
                    Message = $"Failed to remove command: {ex.Message}"
                };
            }
        }

        #endregion

        #region System Methods

        /// <summary>
        /// Check if API server is healthy
        /// </summary>
        public async Task<bool> IsHealthyAsync()
        {
            try
            {
                System.Diagnostics.Debug.WriteLine($"[VoiceAPI] Checking health at: {baseUrl}/health");
                var response = await GetAsync<HealthResponse>("/health");
                bool isHealthy = response?.Status == "healthy";
                System.Diagnostics.Debug.WriteLine($"[VoiceAPI] Health check result: {isHealthy}, Status: {response?.Status}");
                return isHealthy;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"[VoiceAPI] Health check failed: {ex.Message}");
                System.Diagnostics.Debug.WriteLine($"[VoiceAPI] Exception type: {ex.GetType().Name}");
                return false;
            }
        }

        /// <summary>
        /// Get system information
        /// </summary>
        public async Task<SystemInfoResponse> GetSystemInfoAsync()
        {
            try
            {
                var response = await GetAsync<SystemInfoResponse>("/system/info");
                return response;
            }
            catch (Exception ex)
            {
                return new SystemInfoResponse
                {
                    Error = ex.Message
                };
            }
        }

        #endregion

        #region HTTP Helper Methods

        private async Task<T> GetAsync<T>(string endpoint)
        {
            var response = await httpClient.GetAsync($"{baseUrl}{endpoint}");
            response.EnsureSuccessStatusCode();

            var content = await response.Content.ReadAsStringAsync();
            return JsonConvert.DeserializeObject<T>(content);
        }

        private async Task<T> PostAsync<T>(string endpoint, object data)
        {
            var json = JsonConvert.SerializeObject(data);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var response = await httpClient.PostAsync($"{baseUrl}{endpoint}", content);
            response.EnsureSuccessStatusCode();

            var responseContent = await response.Content.ReadAsStringAsync();
            return JsonConvert.DeserializeObject<T>(responseContent);
        }

        #endregion
    }

    #region Response Models

    public class EnrollmentResponse
    {
        [JsonProperty("success")]
        public bool Success { get; set; }

        [JsonProperty("message")]
        public string Message { get; set; }
    }

    public class VerificationResponse
    {
        [JsonProperty("verified")]
        public bool Verified { get; set; }

        [JsonProperty("confidence")]
        public double Confidence { get; set; }

        [JsonProperty("user_id")]
        public int UserId { get; set; }

        public string Error { get; set; }
    }

    public class IdentificationResponse
    {
        [JsonProperty("identified")]
        public bool Identified { get; set; }

        [JsonProperty("user_id")]
        public string UserId { get; set; }

        [JsonProperty("confidence")]
        public double Confidence { get; set; }

        public string Error { get; set; }
    }

    public class DeleteResponse
    {
        [JsonProperty("success")]
        public bool Success { get; set; }

        [JsonProperty("message")]
        public string Message { get; set; }
    }

    public class CommandRecognitionResponse
    {
        [JsonProperty("recognized")]
        public bool Recognized { get; set; }

        [JsonProperty("text")]
        public string Text { get; set; }

        [JsonProperty("category")]
        public string Category { get; set; }

        [JsonProperty("action")]
        public string Action { get; set; }

        [JsonProperty("confidence")]
        public int Confidence { get; set; }

        public string Error { get; set; }
    }

    public class CommandListResponse
    {
        [JsonProperty("commands")]
        public object Commands { get; set; }

        public string Error { get; set; }
    }

    public class AddCommandResponse
    {
        [JsonProperty("success")]
        public bool Success { get; set; }

        [JsonProperty("message")]
        public string Message { get; set; }
    }

    public class RemoveCommandResponse
    {
        [JsonProperty("success")]
        public bool Success { get; set; }

        [JsonProperty("message")]
        public string Message { get; set; }
    }

    public class HealthResponse
    {
        [JsonProperty("status")]
        public string Status { get; set; }
    }

    public class SystemInfoResponse
    {
        [JsonProperty("enrolled_users")]
        public int EnrolledUsers { get; set; }

        [JsonProperty("total_commands")]
        public int TotalCommands { get; set; }

        [JsonProperty("command_categories")]
        public string[] CommandCategories { get; set; }

        public string Error { get; set; }
    }

    #endregion
}
