using System;
using System.IO;
using System.Threading.Tasks;
using NAudio.Wave;

namespace GamingThroughVoiceRecognitionSystem.Services
{
    public class VoiceRecognitionService
    {
        private bool isRecording;
        private WaveInEvent waveIn;
        private MemoryStream audioStream;
        private WaveFileWriter waveWriter;
        private readonly VoiceApiClient voiceApiClient;

        public event EventHandler<float> AudioLevelChanged;
        public event EventHandler RecordingStarted;
        public event EventHandler RecordingStopped;

        public bool IsRecording => isRecording;

        public VoiceRecognitionService()
        {
            voiceApiClient = new VoiceApiClient("http://localhost:5001");
        }

        public void StartRecording()
        {
            if (isRecording)
                return;

            try
            {
                // Create memory stream for audio
                audioStream = new MemoryStream();
                
                // Initialize NAudio WaveIn for microphone recording
                waveIn = new WaveInEvent
                {
                    WaveFormat = new WaveFormat(16000, 1), // 16kHz, mono
                    BufferMilliseconds = 100
                };
                
                // Create WAV file writer
                waveWriter = new WaveFileWriter(audioStream, waveIn.WaveFormat);
                
                // Handle incoming audio data from microphone
                waveIn.DataAvailable += (s, e) =>
                {
                    if (waveWriter != null && e.BytesRecorded > 0)
                    {
                        // Write real microphone data to WAV file
                        waveWriter.Write(e.Buffer, 0, e.BytesRecorded);
                        
                        // Calculate audio level for visualization
                        float max = 0;
                        for (int i = 0; i < e.BytesRecorded; i += 2)
                        {
                            if (i + 1 < e.BytesRecorded)
                            {
                                short sample = (short)((e.Buffer[i + 1] << 8) | e.Buffer[i]);
                                float sampleValue = Math.Abs(sample / 32768f);
                                if (sampleValue > max)
                                    max = sampleValue;
                            }
                        }
                        AudioLevelChanged?.Invoke(this, max);
                    }
                };
                
                waveIn.RecordingStopped += (s, e) =>
                {
                    RecordingStopped?.Invoke(this, EventArgs.Empty);
                };

                // Start recording from microphone
                waveIn.StartRecording();
                isRecording = true;
                RecordingStarted?.Invoke(this, EventArgs.Empty);
                
                System.Diagnostics.Debug.WriteLine("✓ Real microphone recording started");
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"✗ Recording failed: {ex.Message}");
                throw new Exception($"Failed to start recording: {ex.Message}\n\nMake sure you have a microphone connected and enabled.", ex);
            }
        }

        public byte[] StopRecording()
        {
            if (!isRecording)
                return null;

            try
            {
                // Stop recording from microphone
                waveIn?.StopRecording();
                
                // Wait for final data
                System.Threading.Thread.Sleep(200);
                
                // Flush and close WAV writer
                waveWriter?.Flush();
                waveWriter?.Dispose();
                waveWriter = null;
                
                // Get complete WAV file with REAL voice data
                byte[] audioData = audioStream.ToArray();
                
                // Cleanup
                audioStream?.Dispose();
                audioStream = null;
                waveIn?.Dispose();
                waveIn = null;
                
                isRecording = false;
                
                System.Diagnostics.Debug.WriteLine($"✓ Real recording stopped. Audio size: {audioData.Length} bytes");
                
                // Verify it's a valid WAV file
                if (audioData.Length > 44)
                {
                    string header = System.Text.Encoding.ASCII.GetString(audioData, 0, 4);
                    if (header == "RIFF")
                    {
                        System.Diagnostics.Debug.WriteLine("✓ Valid WAV file with REAL voice data");
                    }
                }
                
                return audioData;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"✗ Stop recording failed: {ex.Message}");
                isRecording = false;
                return null;
            }
        }

        public void Dispose()
        {
            if (isRecording)
            {
                StopRecording();
            }
            
            waveWriter?.Dispose();
            audioStream?.Dispose();
            waveIn?.Dispose();
        }

        // ==================== Python API Integration ====================

        /// <summary>
        /// Check if Python voice backend is running
        /// </summary>
        public async Task<bool> IsBackendHealthyAsync()
        {
            try
            {
                return await voiceApiClient.IsHealthyAsync();
            }
            catch
            {
                return false;
            }
        }

        /// <summary>
        /// Enroll user for voice authentication
        /// </summary>
        public async Task<bool> EnrollUserAsync(int userId, byte[] audioData)
        {
            try
            {
                var response = await voiceApiClient.EnrollUserAsync(userId, audioData);
                return response.Success;
            }
            catch (Exception ex)
            {
                throw new Exception($"Voice enrollment failed: {ex.Message}", ex);
            }
        }

        /// <summary>
        /// Verify user by voice
        /// </summary>
        public async Task<(bool verified, double confidence)> VerifyUserAsync(int userId, byte[] audioData)
        {
            try
            {
                var response = await voiceApiClient.VerifyUserAsync(userId, audioData);
                return (response.Verified, response.Confidence);
            }
            catch (Exception ex)
            {
                throw new Exception($"Voice verification failed: {ex.Message}", ex);
            }
        }

        /// <summary>
        /// Identify which user is speaking
        /// </summary>
        public async Task<(bool identified, string userId, double confidence)> IdentifyUserAsync(byte[] audioData)
        {
            try
            {
                var response = await voiceApiClient.IdentifyUserAsync(audioData);
                return (response.Identified, response.UserId, response.Confidence);
            }
            catch (Exception ex)
            {
                throw new Exception($"Voice identification failed: {ex.Message}", ex);
            }
        }

        /// <summary>
        /// Delete user's voice model
        /// </summary>
        public async Task<bool> DeleteUserVoiceAsync(int userId)
        {
            try
            {
                var response = await voiceApiClient.DeleteUserAsync(userId);
                return response.Success;
            }
            catch (Exception ex)
            {
                throw new Exception($"Voice deletion failed: {ex.Message}", ex);
            }
        }
    }
}
