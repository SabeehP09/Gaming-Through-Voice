using GamingThroughVoiceRecognitionSystem.Services;
using System;
using System.Drawing;
using System.IO;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;
using System.Windows.Media.Imaging;
using System.Windows.Threading;
using AForge.Video;
using AForge.Video.DirectShow;

namespace GamingThroughVoiceRecognitionSystem.Views
{
    /// <summary>
    /// Face Registration Window with real-time webcam preview and countdown timer.
    /// Requirements: 7.5
    /// </summary>
    public partial class FaceRegistrationWindow : Window
    {
        private FilterInfoCollection _videoDevices;
        private VideoCaptureDevice _videoSource;
        private Bitmap _currentFrame;
        private DispatcherTimer _updateTimer;
        
        public int UserId { get; set; }
        public bool IsRegistered { get; private set; }
        public string ResultMessage { get; private set; }

        public FaceRegistrationWindow(int userId)
        {
            InitializeComponent();
            UserId = userId;
            IsRegistered = false;
        }

        private void Window_Loaded(object sender, RoutedEventArgs e)
        {
            try
            {
                // Initialize video devices
                _videoDevices = new FilterInfoCollection(FilterCategory.VideoInputDevice);
                
                if (_videoDevices.Count == 0)
                {
                    GlassMessageBox.Show("No camera device found! Please connect a camera and try again.");
                    this.DialogResult = false;
                    this.Close();
                    return;
                }

                // Start camera
                _videoSource = new VideoCaptureDevice(_videoDevices[0].MonikerString);
                _videoSource.NewFrame += VideoSource_NewFrame;
                _videoSource.Start();

                // Update UI timer
                _updateTimer = new DispatcherTimer
                {
                    Interval = TimeSpan.FromMilliseconds(30)
                };
                _updateTimer.Tick += UpdateTimer_Tick;
                _updateTimer.Start();
            }
            catch (Exception ex)
            {
                GlassMessageBox.Show($"Error starting camera: {ex.Message}");
                this.DialogResult = false;
                this.Close();
            }
        }

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

        private void UpdateTimer_Tick(object sender, EventArgs e)
        {
            if (_currentFrame != null)
            {
                Dispatcher.Invoke(() =>
                {
                    try
                    {
                        CameraFeed.Source = BitmapToBitmapImage(_currentFrame);
                        
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
        }

        private BitmapImage BitmapToBitmapImage(Bitmap bitmap)
        {
            using (MemoryStream memory = new MemoryStream())
            {
                bitmap.Save(memory, System.Drawing.Imaging.ImageFormat.Png);
                memory.Position = 0;
                
                BitmapImage bitmapImage = new BitmapImage();
                bitmapImage.BeginInit();
                bitmapImage.StreamSource = memory;
                bitmapImage.CacheOption = BitmapCacheOption.OnLoad;
                bitmapImage.EndInit();
                bitmapImage.Freeze();
                
                return bitmapImage;
            }
        }

        private async void CaptureButton_Click(object sender, RoutedEventArgs e)
        {
            FaceRecognitionService_OpenCV faceService = null;
            
            try
            {
                // Hide capture button and show progress
                CaptureButtonPanel.Visibility = Visibility.Collapsed;
                ProgressPanel.Visibility = Visibility.Visible;
                InstructionText.Text = "Hold still... Capturing multiple images";

                // Initialize face service
                faceService = new FaceRecognitionService_OpenCV();

                // Register face with progress callback
                int currentCapture = 0;
                var result = await faceService.RegisterFaceAsync(UserId, (current, total) =>
                {
                    Dispatcher.Invoke(() =>
                    {
                        currentCapture = current;
                        ProgressText.Text = $"Capturing image {current} of {total}...";
                        CountdownText.Text = $"{current}/{total}";
                        ProgressBar.Value = current;
                        ProgressBar.Maximum = total;
                    });
                });

                System.Diagnostics.Debug.WriteLine($"[FaceReg] Registration result: success={result.success}, embeddings={result.embeddingsCount}, message={result.message}");
                
                if (result.success)
                {
                    IsRegistered = true;
                    ResultMessage = result.message;
                    
                    // Show success overlay
                    ProgressPanel.Visibility = Visibility.Collapsed;
                    SuccessOverlay.Visibility = Visibility.Visible;
                    SuccessText.Text = $"✅ Face Registered!\n\n📸 {result.embeddingsCount} images captured";
                    
                    // Wait a moment then close
                    await Task.Delay(2000);
                    this.DialogResult = true;
                    this.Close();
                }
                else
                {
                    // Show error with details
                    System.Diagnostics.Debug.WriteLine($"[FaceReg] Registration FAILED: {result.message}");
                    System.Diagnostics.Debug.WriteLine($"[FaceReg] Embeddings captured: {result.embeddingsCount}/5");
                    
                    ProgressPanel.Visibility = Visibility.Collapsed;
                    CaptureButtonPanel.Visibility = Visibility.Visible;
                    InstructionText.Text = "❌ Registration failed - Please try again";
                    
                    ResultMessage = result.message;
                    GlassMessageBox.ShowError($"❌ Face registration failed:\n\n{result.message}\n\nImages captured: {result.embeddingsCount}/5\n\nTips:\n• Ensure good lighting\n• Face the camera directly\n• Remove glasses if possible\n• Stay still during capture");
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"[FaceReg] Exception: {ex.Message}");
                System.Diagnostics.Debug.WriteLine($"[FaceReg] Stack trace: {ex.StackTrace}");
                
                ProgressPanel.Visibility = Visibility.Collapsed;
                CaptureButtonPanel.Visibility = Visibility.Visible;
                InstructionText.Text = "❌ Error occurred - Please try again";
                
                ResultMessage = ex.Message;
                GlassMessageBox.ShowError($"❌ Error during registration:\n\n{ex.Message}\n\nPlease check:\n• OpenCV server is running\n• Webcam is working\n• Good lighting conditions");
            }
            finally
            {
                faceService?.Dispose();
            }
        }

        private void CloseButton_Click(object sender, RoutedEventArgs e)
        {
            this.DialogResult = false;
            this.Close();
        }

        private void Window_Closing(object sender, System.ComponentModel.CancelEventArgs e)
        {
            _updateTimer?.Stop();
            
            if (_videoSource != null && _videoSource.IsRunning)
            {
                _videoSource.SignalToStop();
                _videoSource.WaitForStop();
                _videoSource.NewFrame -= VideoSource_NewFrame;
            }
            
            if (_currentFrame != null)
            {
                _currentFrame.Dispose();
                _currentFrame = null;
            }
        }

        private void Window_MouseLeftButtonDown(object sender, MouseButtonEventArgs e)
        {
            if (e.ButtonState == MouseButtonState.Pressed)
                this.DragMove();
        }
    }
}
