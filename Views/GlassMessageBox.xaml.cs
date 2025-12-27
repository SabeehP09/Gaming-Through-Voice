using System;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;
using System.Windows.Media.Animation;
using System.Windows.Threading;

namespace GamingThroughVoiceRecognitionSystem.Views
{
    public enum MessageType
    {
        Info,
        Success,
        Error,
        Processing
    }

    public partial class GlassMessageBox : Window
    {
        private DispatcherTimer _autoDismissTimer;
        private bool _autoDismiss;

        public GlassMessageBox(string message, MessageType type = MessageType.Info, bool autoDismiss = false, int autoDismissSeconds = 2)
        {
            InitializeComponent();
            MessageText.Text = message;
            _autoDismiss = autoDismiss;

            // Apply fade-in animation
            var fadeIn = new DoubleAnimation(0, 1, TimeSpan.FromMilliseconds(300));
            this.BeginAnimation(OpacityProperty, fadeIn);

            // Setup auto-dismiss if requested
            if (_autoDismiss)
            {
                _autoDismissTimer = new DispatcherTimer
                {
                    Interval = TimeSpan.FromSeconds(autoDismissSeconds)
                };
                _autoDismissTimer.Tick += AutoDismissTimer_Tick;
                _autoDismissTimer.Start();
            }
        }

        private void AutoDismissTimer_Tick(object sender, EventArgs e)
        {
            _autoDismissTimer?.Stop();
            
            // Fade out animation before closing
            var fadeOut = new DoubleAnimation(1, 0, TimeSpan.FromMilliseconds(300));
            fadeOut.Completed += (s, args) => this.Close();
            this.BeginAnimation(OpacityProperty, fadeOut);
        }

        private void OkBtn_Click(object sender, RoutedEventArgs e)
        {
            _autoDismissTimer?.Stop();
            this.Close();
        }

        private void Window_MouseLeftButtonDown(object sender, MouseButtonEventArgs e)
        {
            if (e.ButtonState == MouseButtonState.Pressed)
                this.DragMove();
        }

        // Static helper to show messages easily
        public static void Show(string message)
        {
            GlassMessageBox box = new GlassMessageBox(message);
            box.ShowDialog();
        }

        // Static helper to show success messages with auto-dismiss
        public static void ShowSuccess(string message, bool autoDismiss = true)
        {
            GlassMessageBox box = new GlassMessageBox(message, MessageType.Success, autoDismiss);
            box.ShowDialog();
        }

        // Static helper to show error messages (no auto-dismiss)
        public static void ShowError(string message)
        {
            GlassMessageBox box = new GlassMessageBox(message, MessageType.Error, false);
            box.ShowDialog();
        }

        // Static helper to show processing messages
        public static GlassMessageBox ShowProcessing(string message)
        {
            GlassMessageBox box = new GlassMessageBox(message, MessageType.Processing, false);
            box.Show(); // Non-modal for processing messages
            return box;
        }
    }
}
