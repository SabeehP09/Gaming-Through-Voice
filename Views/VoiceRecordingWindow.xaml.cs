using GamingThroughVoiceRecognitionSystem.Services;
using System;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Animation;

namespace GamingThroughVoiceRecognitionSystem.Views
{
    public partial class VoiceRecordingWindow : Window
    {
        private VoiceRecognitionService voiceService;
        public byte[] RecordedVoiceData { get; private set; }
        public bool IsRecorded { get; private set; }
        private bool isRecording = false;

        public VoiceRecordingWindow()
        {
            InitializeComponent();
            voiceService = new VoiceRecognitionService();
        }

        private void Window_Loaded(object sender, RoutedEventArgs e)
        {
            voiceService.AudioLevelChanged += VoiceService_AudioLevelChanged;
            voiceService.RecordingStarted += VoiceService_RecordingStarted;
            voiceService.RecordingStopped += VoiceService_RecordingStopped;
        }

        private void VoiceService_AudioLevelChanged(object sender, float level)
        {
            Dispatcher.Invoke(() =>
            {
                // Update audio visualizer
                double scale = 1.0 + (level * 2);
                var transform = AudioWave.RenderTransform as ScaleTransform;
                if (transform != null)
                {
                    transform.ScaleX = scale;
                    transform.ScaleY = scale;
                }
            });
        }

        private void VoiceService_RecordingStarted(object sender, EventArgs e)
        {
            Dispatcher.Invoke(() =>
            {
                RecordButton.Content = "⏹ STOP RECORDING";
                InstructionText.Text = "Recording... Speak clearly!";
                StartPulseAnimation();
            });
        }

        private void VoiceService_RecordingStopped(object sender, EventArgs e)
        {
            Dispatcher.Invoke(() =>
            {
                RecordButton.Content = "🎤 START RECORDING";
                InstructionText.Text = "Click to start recording";
                StopPulseAnimation();
            });
        }

        private void RecordButton_Click(object sender, RoutedEventArgs e)
        {
            if (!isRecording)
            {
                // Start recording
                voiceService.StartRecording();
                isRecording = true;
            }
            else
            {
                // Stop recording
                RecordedVoiceData = voiceService.StopRecording();
                isRecording = false;

                if (RecordedVoiceData != null && RecordedVoiceData.Length > 0)
                {
                    ShowSuccessAndClose();
                }
                else
                {
                    GlassMessageBox.Show("No audio recorded. Please try again.");
                }
            }
        }

        private async void ShowSuccessAndClose()
        {
            IsRecorded = true;
            SuccessOverlay.Visibility = Visibility.Visible;
            InstructionText.Text = "Voice recorded successfully!";

            await Task.Delay(1500);
            this.DialogResult = true;
            this.Close();
        }

        private void StartPulseAnimation()
        {
            var pulseAnimation = new DoubleAnimation
            {
                From = 1.0,
                To = 1.2,
                Duration = TimeSpan.FromSeconds(0.8),
                AutoReverse = true,
                RepeatBehavior = RepeatBehavior.Forever
            };

            RecordingIndicator.RenderTransform = new System.Windows.Media.ScaleTransform(1, 1);
            RecordingIndicator.RenderTransformOrigin = new Point(0.5, 0.5);
            RecordingIndicator.RenderTransform.BeginAnimation(System.Windows.Media.ScaleTransform.ScaleXProperty, pulseAnimation);
            RecordingIndicator.RenderTransform.BeginAnimation(System.Windows.Media.ScaleTransform.ScaleYProperty, pulseAnimation);
        }

        private void StopPulseAnimation()
        {
            RecordingIndicator.RenderTransform.BeginAnimation(System.Windows.Media.ScaleTransform.ScaleXProperty, null);
            RecordingIndicator.RenderTransform.BeginAnimation(System.Windows.Media.ScaleTransform.ScaleYProperty, null);
        }

        private void CloseButton_Click(object sender, RoutedEventArgs e)
        {
            if (isRecording)
            {
                voiceService.StopRecording();
            }
            this.DialogResult = false;
            this.Close();
        }

        private void Window_Closing(object sender, System.ComponentModel.CancelEventArgs e)
        {
            voiceService?.Dispose();
        }

        private void Window_MouseLeftButtonDown(object sender, MouseButtonEventArgs e)
        {
            if (e.ButtonState == MouseButtonState.Pressed)
                this.DragMove();
        }
    }
}
