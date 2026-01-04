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
                
                Debug.WriteLine("[APP] Application initialized successfully");
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[APP] ERROR during initialization: {ex.Message}");
            }
        }

        protected override void OnExit(ExitEventArgs e)
        {
            try
            {
                Debug.WriteLine("[APP] Application shutting down...");
                Debug.WriteLine("[APP] Cleanup completed");
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[APP] ERROR during cleanup: {ex.Message}");
            }
            
            base.OnExit(e);
        }
    }
}
