using GamingThroughVoiceRecognitionSystem.Services;
using System;
using System.Drawing;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;
using System.Windows.Threading;

namespace GamingThroughVoiceRecognitionSystem.Views
{
    public partial class FaceCaptureWindow : Window
    {
        private FaceRecognitionService faceService;
        private DispatcherTimer updateTimer;
        public byte[] CapturedFaceData { get; private set; }
        public bool IsCaptured { get; private set; }

        public FaceCaptureWindow()
        {
            InitializeComponent();
            faceService = new FaceRecognitionService();
        }

        private void Window_Loaded(object sender, RoutedEventArgs e)
        {
            try
            {
                if (!faceService.IsCameraAvailable())
                {
                    GlassMessageBox.Show("No camera device found! Please connect a camera and try again.");
                    this.Close();
                    return;
                }

                faceService.FrameCaptured += FaceService_FrameCaptured;
                faceService.StartCamera();

                // Update UI timer
                updateTimer = new DispatcherTimer
                {
                    Interval = TimeSpan.FromMilliseconds(30)
                };
                updateTimer.Tick += UpdateTimer_Tick;
                updateTimer.Start();
            }
            catch (Exception ex)
            {
                GlassMessageBox.Show($"Error starting camera: {ex.Message}");
                this.Close();
            }
        }

        private void UpdateTimer_Tick(object sender, EventArgs e)
        {
            // Timer for any additional UI updates if needed
        }

        private void FaceService_FrameCaptured(object sender, Bitmap frame)
        {
            Dispatcher.Invoke(() =>
            {
                try
                {
                    CameraFeed.Source = faceService.BitmapToBitmapImage(frame);
                    
                    // Hide loading overlay once first frame is received
                    if (LoadingOverlay.Visibility == Visibility.Visible)
                    {
                        LoadingOverlay.Visibility = Visibility.Collapsed;
                    }
                }
                catch
                {
                    // Ignore frame update errors
                }
            });
        }

        private async void CaptureButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                CapturedFaceData = faceService.CaptureFace();
                
                if (CapturedFaceData != null)
                {
                    IsCaptured = true;
                    
                    // Show success overlay
                    SuccessOverlay.Visibility = Visibility.Visible;
                    InstructionText.Text = "Face captured successfully!";
                    
                    // Wait a moment then close
                    await Task.Delay(1500);
                    this.DialogResult = true;
                    this.Close();
                }
                else
                {
                    GlassMessageBox.Show("Failed to capture face. Please try again.");
                }
            }
            catch (Exception ex)
            {
                GlassMessageBox.Show($"Error capturing face: {ex.Message}");
            }
        }

        private void CloseButton_Click(object sender, RoutedEventArgs e)
        {
            this.DialogResult = false;
            this.Close();
        }

        private void Window_Closing(object sender, System.ComponentModel.CancelEventArgs e)
        {
            updateTimer?.Stop();
            faceService?.StopCamera();
        }

        private void Window_MouseLeftButtonDown(object sender, MouseButtonEventArgs e)
        {
            if (e.ButtonState == MouseButtonState.Pressed)
                this.DragMove();
        }
    }
}
