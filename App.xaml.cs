using GamingThroughVoiceRecognitionSystem.Services;
using System;
using System.Collections.Generic;
using System.Configuration;
using System.Data;
using System.Diagnostics;
using System.Linq;
using System.Threading.Tasks;
using System.Windows;

namespace GamingThroughVoiceRecognitionSystem
{
    /// <summary>
    /// Interaction logic for App.xaml
    /// </summary>
    public partial class App : Application
    {
        protected override void OnStartup(StartupEventArgs e)
        {
            base.OnStartup(e);
            
            try
            {
                // Initialize theme on app startup
                ThemeManager.Initialize();
                
                // Initialize VOSK voice recognition system
                Debug.WriteLine("[APP] Initializing VOSK voice recognition system...");
                
                // Initialize VoiceListenerManager
                VoiceListenerManager.Initialize();
                
                // Start VoiceListener.exe process
                bool voiceStarted = VoiceListenerManager.StartVoiceListener();
                if (voiceStarted)
                {
                    Debug.WriteLine("[APP] VOSK voice listener started successfully");
                }
                else
                {
                    Debug.WriteLine("[APP] WARNING: VOSK voice listener failed to start - voice commands will not work");
                    Debug.WriteLine("[APP] Application will continue without voice recognition");
                }
                
                // Initialize GlobalVoiceCommandHandler
                GlobalVoiceCommandHandler.Initialize();
                
                // TEMPORARY: Enable voice commands for testing (remove this after adding login integration)
                // TODO: Remove this line and set IsUserLoggedIn = true in your login success code
                GlobalVoiceCommandHandler.IsUserLoggedIn = true;
                Debug.WriteLine("[APP] TEMPORARY: Voice commands enabled for testing");
                
                Debug.WriteLine("[APP] VOSK voice recognition system initialized");
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[APP] ERROR during VOSK initialization: {ex.Message}");
                Debug.WriteLine("[APP] Application will continue without voice recognition");
            }
        }

        protected override void OnExit(ExitEventArgs e)
        {
            try
            {
                Debug.WriteLine("[APP] Application shutting down...");
                
                // Cleanup VOSK voice recognition system
                GlobalVoiceCommandHandler.Cleanup();
                VoiceListenerManager.Cleanup();
                
                Debug.WriteLine("[APP] VOSK cleanup completed");
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[APP] ERROR during VOSK cleanup: {ex.Message}");
            }
            
            base.OnExit(e);
        }
    }
}
