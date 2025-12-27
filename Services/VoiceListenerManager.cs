using System;
using System.Diagnostics;
using System.IO;
using System.Windows.Threading;

namespace GamingThroughVoiceRecognitionSystem.Services
{
    /// <summary>
    /// Manages the VoiceListener.exe process lifecycle and monitors voice commands from file
    /// </summary>
    public static class VoiceListenerManager
    {
        #region Private Fields

        private static Process listenerProcess;
        private static DispatcherTimer commandTimer;
        private static string lastCommand = string.Empty;

        #endregion

        #region Path Configuration

        // Base directory (bin\Debug or bin\Release)
        private static readonly string BaseDirectory = AppDomain.CurrentDomain.BaseDirectory;

        // VoiceListener paths (in bin folder after build)
        private static readonly string VoiceListenerFolder = Path.Combine(BaseDirectory, "vosk", "VoiceListenerApp");
        
        /// <summary>
        /// Path to VoiceListener.exe executable
        /// </summary>
        public static string VoiceListenerExePath => Path.Combine(VoiceListenerFolder, "VoiceListener.exe");
        
        /// <summary>
        /// Path to voice_listener.py Python script
        /// </summary>
        public static string VoiceListenerPyPath => Path.Combine(VoiceListenerFolder, "voice_listener.py");
        
        /// <summary>
        /// Path to voice_listener.txt command file
        /// </summary>
        public static string VoiceCommandFilePath => Path.Combine(VoiceListenerFolder, "voice_listener.txt");

        #endregion

        #region Initialization

        /// <summary>
        /// Initialize the voice listener system
        /// Creates the command file if it doesn't exist
        /// </summary>
        public static void Initialize()
        {
            try
            {
                Debug.WriteLine("[VOICE] Initializing VoiceListenerManager...");
                EnsureCommandFileExists();
                Debug.WriteLine("[VOICE] VoiceListenerManager initialized successfully");
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[VOICE] ERROR during initialization: {ex.Message}");
            }
        }

        /// <summary>
        /// Ensures the voice command file exists
        /// </summary>
        public static void EnsureCommandFileExists()
        {
            try
            {
                // Create directory if it doesn't exist
                string directory = Path.GetDirectoryName(VoiceCommandFilePath);
                if (!Directory.Exists(directory))
                {
                    Directory.CreateDirectory(directory);
                    Debug.WriteLine($"[VOICE] Created directory: {directory}");
                }

                // Create empty file if it doesn't exist
                if (!File.Exists(VoiceCommandFilePath))
                {
                    File.WriteAllText(VoiceCommandFilePath, string.Empty);
                    Debug.WriteLine($"[VOICE] Created command file: {VoiceCommandFilePath}");
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[VOICE] ERROR creating command file: {ex.Message}");
            }
        }

        #endregion

        #region Process Lifecycle Management

        /// <summary>
        /// Start the VoiceListener process (tries Python script first, then .exe)
        /// </summary>
        /// <returns>True if started successfully, false otherwise</returns>
        public static bool StartVoiceListener()
        {
            try
            {
                // Check if already running
                if (listenerProcess != null && !listenerProcess.HasExited)
                {
                    Debug.WriteLine("[VOICE] VoiceListener is already running");
                    return true;
                }

                // Try Python script first (more reliable)
                if (File.Exists(VoiceListenerPyPath))
                {
                    Debug.WriteLine($"[VOICE] Found Python script at: {VoiceListenerPyPath}");
                    Debug.WriteLine("[VOICE] Attempting to start with Python...");
                    
                    if (StartWithPython())
                    {
                        return true;
                    }
                    
                    Debug.WriteLine("[VOICE] Python method failed, trying .exe...");
                }

                // Fall back to .exe
                if (File.Exists(VoiceListenerExePath))
                {
                    Debug.WriteLine($"[VOICE] Found executable at: {VoiceListenerExePath}");
                    return StartWithExe();
                }

                Debug.WriteLine("[VOICE] ERROR: Neither voice_listener.py nor VoiceListener.exe found");
                Debug.WriteLine($"[VOICE] Looked in: {VoiceListenerFolder}");
                return false;
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[VOICE] ERROR starting VoiceListener: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Start VoiceListener using Python interpreter
        /// </summary>
        private static bool StartWithPython()
        {
            try
            {
                listenerProcess = new Process();
                listenerProcess.StartInfo.FileName = "python";
                listenerProcess.StartInfo.Arguments = $"\"{VoiceListenerPyPath}\"";
                listenerProcess.StartInfo.WorkingDirectory = VoiceListenerFolder;
                listenerProcess.StartInfo.UseShellExecute = false;
                listenerProcess.StartInfo.CreateNoWindow = false; // Show console for debugging
                listenerProcess.StartInfo.RedirectStandardOutput = false;
                listenerProcess.StartInfo.RedirectStandardError = false;
                
                bool started = listenerProcess.Start();
                
                if (started)
                {
                    Debug.WriteLine($"[VOICE] VoiceListener started with Python (PID: {listenerProcess.Id})");
                    return true;
                }
                
                return false;
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[VOICE] ERROR starting with Python: {ex.Message}");
                listenerProcess = null;
                return false;
            }
        }

        /// <summary>
        /// Start VoiceListener using compiled .exe
        /// </summary>
        private static bool StartWithExe()
        {
            try
            {
                listenerProcess = new Process();
                listenerProcess.StartInfo.FileName = VoiceListenerExePath;
                listenerProcess.StartInfo.WorkingDirectory = VoiceListenerFolder;
                listenerProcess.StartInfo.UseShellExecute = false;
                listenerProcess.StartInfo.CreateNoWindow = false; // Show console for debugging
                
                bool started = listenerProcess.Start();
                
                if (started)
                {
                    Debug.WriteLine($"[VOICE] VoiceListener.exe started successfully (PID: {listenerProcess.Id})");
                    return true;
                }
                
                return false;
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[VOICE] ERROR starting .exe: {ex.Message}");
                listenerProcess = null;
                return false;
            }
        }

        /// <summary>
        /// Stop the VoiceListener.exe process
        /// </summary>
        public static void StopVoiceListener()
        {
            try
            {
                if (listenerProcess != null && !listenerProcess.HasExited)
                {
                    Debug.WriteLine($"[VOICE] Stopping VoiceListener.exe (PID: {listenerProcess.Id})...");
                    listenerProcess.Kill();
                    listenerProcess.WaitForExit(2000); // Wait up to 2 seconds
                    listenerProcess.Dispose();
                    listenerProcess = null;
                    Debug.WriteLine("[VOICE] VoiceListener.exe stopped successfully");
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[VOICE] ERROR stopping VoiceListener.exe: {ex.Message}");
            }
        }

        #endregion

        #region File Monitoring

        /// <summary>
        /// Start monitoring the voice command file
        /// </summary>
        /// <param name="onCommandReceived">Callback invoked when a new command is detected</param>
        /// <param name="intervalMs">Polling interval in milliseconds (default: 5ms for low latency)</param>
        public static void StartMonitoring(Action<string> onCommandReceived, int intervalMs = 5)
        {
            try
            {
                // Stop existing timer if any
                StopMonitoring();

                Debug.WriteLine($"[VOICE] Starting file monitoring (interval: {intervalMs}ms)...");

                // Create and configure timer
                commandTimer = new DispatcherTimer();
                commandTimer.Interval = TimeSpan.FromMilliseconds(intervalMs);
                commandTimer.Tick += (s, e) =>
                {
                    try
                    {
                        string command = ReadVoiceCommand();
                        
                        // Only process if command is new and not empty
                        if (!string.IsNullOrEmpty(command) && command != lastCommand)
                        {
                            lastCommand = command;
                            Debug.WriteLine($"[VOICE] New command detected: '{command}'");
                            onCommandReceived?.Invoke(command);
                        }
                    }
                    catch (Exception ex)
                    {
                        Debug.WriteLine($"[VOICE] ERROR in monitoring tick: {ex.Message}");
                    }
                };

                commandTimer.Start();
                Debug.WriteLine("[VOICE] File monitoring started successfully");
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[VOICE] ERROR starting monitoring: {ex.Message}");
            }
        }

        /// <summary>
        /// Stop monitoring the voice command file
        /// </summary>
        public static void StopMonitoring()
        {
            try
            {
                if (commandTimer != null)
                {
                    commandTimer.Stop();
                    commandTimer = null;
                    Debug.WriteLine("[VOICE] File monitoring stopped");
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[VOICE] ERROR stopping monitoring: {ex.Message}");
            }
        }

        /// <summary>
        /// Read the current voice command from file (optimized for low latency)
        /// </summary>
        /// <returns>The command text (lowercase, trimmed) or empty string if no command</returns>
        public static string ReadVoiceCommand()
        {
            try
            {
                if (File.Exists(VoiceCommandFilePath))
                {
                    // Use FileStream with FileShare.ReadWrite for faster, non-blocking reads
                    using (FileStream fs = new FileStream(VoiceCommandFilePath, FileMode.Open, FileAccess.Read, FileShare.ReadWrite))
                    using (StreamReader sr = new StreamReader(fs))
                    {
                        string content = sr.ReadToEnd();
                        return content.Trim().ToLower();
                    }
                }
            }
            catch (IOException)
            {
                // File locked by another process, skip this read
                // This is normal and can happen occasionally
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[VOICE] ERROR reading command file: {ex.Message}");
            }

            return string.Empty;
        }

        /// <summary>
        /// Clear the voice command file (optimized for low latency)
        /// </summary>
        public static void ClearVoiceCommand()
        {
            try
            {
                if (File.Exists(VoiceCommandFilePath))
                {
                    // Use FileStream with immediate flush for instant clearing
                    using (FileStream fs = new FileStream(VoiceCommandFilePath, FileMode.Truncate, FileAccess.Write, FileShare.ReadWrite))
                    {
                        fs.Flush(true); // Force immediate write to disk
                    }
                }
            }
            catch (IOException)
            {
                // File locked, skip clearing
                // This is normal and can happen occasionally
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[VOICE] ERROR clearing command file: {ex.Message}");
            }
        }

        #endregion

        #region Pause/Resume

        private static bool isPaused = false;

        /// <summary>
        /// Pause voice command monitoring (for in-game voice control)
        /// </summary>
        public static void PauseMonitoring()
        {
            try
            {
                if (!isPaused)
                {
                    StopMonitoring();
                    isPaused = true;
                    Debug.WriteLine("[VOICE] Voice monitoring PAUSED (game voice control active)");
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[VOICE] ERROR pausing monitoring: {ex.Message}");
            }
        }

        /// <summary>
        /// Resume voice command monitoring (after game exits)
        /// </summary>
        public static void ResumeMonitoring(Action<string> onCommandReceived)
        {
            try
            {
                if (isPaused)
                {
                    StartMonitoring(onCommandReceived, intervalMs: 5);
                    isPaused = false;
                    Debug.WriteLine("[VOICE] Voice monitoring RESUMED (app voice control active)");
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[VOICE] ERROR resuming monitoring: {ex.Message}");
            }
        }

        #endregion

        #region Cleanup

        /// <summary>
        /// Complete cleanup of voice listener system
        /// </summary>
        public static void Cleanup()
        {
            try
            {
                Debug.WriteLine("[VOICE] Cleaning up VoiceListenerManager...");
                StopMonitoring();
                StopVoiceListener();
                lastCommand = string.Empty;
                isPaused = false;
                Debug.WriteLine("[VOICE] Cleanup completed");
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[VOICE] ERROR during cleanup: {ex.Message}");
            }
        }

        #endregion
    }
}
