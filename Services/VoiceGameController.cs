using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace GamingThroughVoiceRecognitionSystem.Services
{
    /// <summary>
    /// Service to launch and control voice-controlled games (Mr Racer, Subway Surfers, etc.)
    /// </summary>
    public class VoiceGameController
    {
        private Process voiceControllerProcess;
        private readonly string voiceGamePath;
        private readonly string pythonScript;
        private readonly string gameWindowTitle;
        private CancellationTokenSource monitorCancellation;

        public bool IsRunning => voiceControllerProcess != null && !voiceControllerProcess.HasExited;

        /// <summary>
        /// Initialize voice controller for a specific game
        /// </summary>
        /// <param name="gameName">Name of the game (e.g., "Mr Racer", "Subway Surfers")</param>
        public VoiceGameController(string gameName = "Mr Racer")
        {
            string baseDir = AppDomain.CurrentDomain.BaseDirectory;
            
            // Configure paths based on game
            if (gameName.IndexOf("Subway Surfers", StringComparison.OrdinalIgnoreCase) >= 0 ||
                gameName.IndexOf("Subway", StringComparison.OrdinalIgnoreCase) >= 0)
            {
                // For Subway Surfers, use the source directory (not output directory)
                // Go up from bin\Debug to project root, then to Games/subway game
                string projectRoot = Path.GetFullPath(Path.Combine(baseDir, "..", ".."));
                voiceGamePath = Path.Combine(projectRoot, "Games", "subway game");
                pythonScript = Path.Combine(voiceGamePath, "voice_launcher.py");
                gameWindowTitle = "Subway Surf";  // Partial match for "Subway Surfers"
                
                Debug.WriteLine($"[VoiceGame] Subway Surfers path: {voiceGamePath}");
                Debug.WriteLine($"[VoiceGame] Python script: {pythonScript}");
            }
            else // Default to Mr Racer
            {
                voiceGamePath = Path.Combine(baseDir, "Games", "VoiceGame", "VoiceGame");
                pythonScript = Path.Combine(voiceGamePath, "voice_game_controller.py");
                gameWindowTitle = "MR RACER";
            }
        }

        /// <summary>
        /// Launch Mr Racer with voice control
        /// </summary>
        /// <param name="autoLaunch">If true, automatically launches the game without waiting for voice command</param>
        public bool LaunchVoiceGame(bool autoLaunch = false)
        {
            try
            {
                if (IsRunning)
                {
                    Debug.WriteLine("[VoiceGame] Already running");
                    return true;
                }

                if (!File.Exists(pythonScript))
                {
                    Debug.WriteLine($"[VoiceGame] Script not found: {pythonScript}");
                    return false;
                }

                Debug.WriteLine("[VoiceGame] Starting voice-controlled Mr Racer...");
                
                // PAUSE app voice commands while game is running
                VoiceListenerManager.PauseMonitoring();
                Debug.WriteLine("[VoiceGame] App voice commands PAUSED");

                // Start Python voice controller (hidden window)
                voiceControllerProcess = new Process();
                voiceControllerProcess.StartInfo.FileName = "pythonw";  // Use pythonw to hide console
                
                // Use --auto-launch flag for both games when autoLaunch is true
                if (autoLaunch)
                {
                    voiceControllerProcess.StartInfo.Arguments = $"\"{pythonScript}\" --auto-launch";
                    Debug.WriteLine("[VoiceGame] Auto-launch enabled - game will start immediately");
                }
                else
                {
                    voiceControllerProcess.StartInfo.Arguments = $"\"{pythonScript}\"";
                    Debug.WriteLine("[VoiceGame] Starting voice controller");
                }
                
                voiceControllerProcess.StartInfo.WorkingDirectory = voiceGamePath;
                voiceControllerProcess.StartInfo.UseShellExecute = false;
                voiceControllerProcess.StartInfo.CreateNoWindow = true;  // Hide console window
                voiceControllerProcess.StartInfo.WindowStyle = ProcessWindowStyle.Hidden;
                voiceControllerProcess.StartInfo.RedirectStandardOutput = false;
                voiceControllerProcess.StartInfo.RedirectStandardError = false;

                bool started = voiceControllerProcess.Start();

                if (started)
                {
                    Debug.WriteLine($"[VoiceGame] Voice controller started (PID: {voiceControllerProcess.Id})");
                    Debug.WriteLine("[VoiceGame] Monitoring game window...");
                    
                    // Start monitoring the game window
                    StartGameWindowMonitoring();
                    
                    return true;
                }

                // If failed to start, resume app voice commands
                VoiceListenerManager.ResumeMonitoring(GlobalVoiceCommandHandler.ProcessGlobalCommand);
                return false;
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[VoiceGame] Error starting voice controller: {ex.Message}");
                // Resume app voice commands on error
                VoiceListenerManager.ResumeMonitoring(GlobalVoiceCommandHandler.ProcessGlobalCommand);
                return false;
            }
        }

        /// <summary>
        /// Monitor the game window and kill Python process when game closes
        /// </summary>
        private void StartGameWindowMonitoring()
        {
            monitorCancellation = new CancellationTokenSource();
            var token = monitorCancellation.Token;

            Task.Run(async () =>
            {
                try
                {
                    Debug.WriteLine("[VoiceGame] Window monitor started");
                    bool gameWasRunning = false;
                    int secondsWaiting = 0;
                    const int MAX_WAIT_SECONDS = 30; // Wait max 30 seconds for game to start

                    while (!token.IsCancellationRequested)
                    {
                        // Check if game window exists
                        bool gameRunning = IsGameWindowOpen();

                        if (gameRunning && !gameWasRunning)
                        {
                            Debug.WriteLine($"[VoiceGame] ✅ Game window detected - {gameWindowTitle} is running");
                            gameWasRunning = true;
                            secondsWaiting = 0; // Reset timeout
                        }
                        else if (!gameRunning && gameWasRunning)
                        {
                            Debug.WriteLine("[VoiceGame] ❌ Game window closed - stopping voice controller");
                            StopVoiceGame();
                            break;
                        }
                        else if (!gameRunning && !gameWasRunning)
                        {
                            // Game hasn't started yet
                            secondsWaiting++;
                            if (secondsWaiting >= MAX_WAIT_SECONDS)
                            {
                                Debug.WriteLine($"[VoiceGame] ⚠️ Timeout: Game didn't start after {MAX_WAIT_SECONDS} seconds - stopping voice controller");
                                StopVoiceGame();
                                break;
                            }
                        }

                        await Task.Delay(1000, token); // Check every second
                    }
                }
                catch (TaskCanceledException)
                {
                    Debug.WriteLine("[VoiceGame] Window monitor cancelled");
                }
                catch (Exception ex)
                {
                    Debug.WriteLine($"[VoiceGame] Monitor error: {ex.Message}");
                    StopVoiceGame();
                }
            }, token);
        }

        /// <summary>
        /// Check if the game window is currently open
        /// </summary>
        private bool IsGameWindowOpen()
        {
            try
            {
                var processes = Process.GetProcesses();
                return processes.Any(p =>
                {
                    try
                    {
                        return !string.IsNullOrEmpty(p.MainWindowTitle) &&
                               p.MainWindowTitle.IndexOf(gameWindowTitle, StringComparison.OrdinalIgnoreCase) >= 0;
                    }
                    catch
                    {
                        return false;
                    }
                });
            }
            catch
            {
                return false;
            }
        }

        /// <summary>
        /// Stop the voice controller and resume app voice control
        /// </summary>
        public void StopVoiceGame()
        {
            try
            {
                // Cancel monitoring
                if (monitorCancellation != null && !monitorCancellation.IsCancellationRequested)
                {
                    monitorCancellation.Cancel();
                    monitorCancellation.Dispose();
                    monitorCancellation = null;
                }

                // Kill Python process
                if (voiceControllerProcess != null && !voiceControllerProcess.HasExited)
                {
                    Debug.WriteLine("[VoiceGame] Killing Python voice controller process...");
                    voiceControllerProcess.Kill();
                    voiceControllerProcess.WaitForExit(2000);
                    voiceControllerProcess.Dispose();
                    voiceControllerProcess = null;
                    Debug.WriteLine("[VoiceGame] ✅ Voice controller stopped");
                }
                
                // Resume app voice control
                try
                {
                    System.Windows.Application.Current.Dispatcher.Invoke(() =>
                    {
                        VoiceListenerManager.ResumeMonitoring(GlobalVoiceCommandHandler.ProcessGlobalCommand);
                        Debug.WriteLine("[VoiceGame] ✅ App voice control RESUMED");
                    });
                }
                catch (Exception ex)
                {
                    Debug.WriteLine($"[VoiceGame] Error resuming voice control: {ex.Message}");
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[VoiceGame] Error stopping voice controller: {ex.Message}");
            }
        }

        /// <summary>
        /// Check if Python and required packages are installed
        /// </summary>
        public bool CheckDependencies()
        {
            // Just check if the script file exists - let Python handle the rest
            if (File.Exists(pythonScript))
            {
                Debug.WriteLine($"[VoiceGame] Script found: {pythonScript}");
                return true;
            }
            
            Debug.WriteLine($"[VoiceGame] Script not found: {pythonScript}");
            return false;
        }
    }
}
