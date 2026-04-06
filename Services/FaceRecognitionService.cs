using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Linq;
using System.Windows.Media.Imaging;
using AForge.Video;
using AForge.Video.DirectShow;
using System.Diagnostics;

namespace GamingThroughVoiceRecognitionSystem.Services
{
    /// <summary>
    /// Face Recognition Service using System.Drawing (no AForge.Imaging dependency)
    /// </summary>
    public class FaceRecognitionService
    {
        private FilterInfoCollection videoDevices;
        private VideoCaptureDevice videoSource;
        private Bitmap currentFrame;

        public event EventHandler<Bitmap> FrameCaptured;
        public event EventHandler CameraStarted;
        public event EventHandler CameraStopped;

        // Face detection parameters
        private const int FACE_WIDTH = 100;
        private const int FACE_HEIGHT = 100;
        private const double MATCH_THRESHOLD = 0.92; // 92% similarity required (very strict for security)

        public FaceRecognitionService()
        {
            videoDevices = new FilterInfoCollection(FilterCategory.VideoInputDevice);
        }

        public bool IsCameraAvailable()
        {
            return videoDevices.Count > 0;
        }

        public void StartCamera()
        {
            if (!IsCameraAvailable())
            {
                throw new Exception("No camera device found!");
            }

            videoSource = new VideoCaptureDevice(videoDevices[0].MonikerString);
            videoSource.NewFrame += VideoSource_NewFrame;
            videoSource.Start();
            CameraStarted?.Invoke(this, EventArgs.Empty);
        }

        private void VideoSource_NewFrame(object sender, NewFrameEventArgs eventArgs)
        {
            currentFrame = (Bitmap)eventArgs.Frame.Clone();
            FrameCaptured?.Invoke(this, currentFrame);
        }

        public byte[] CaptureFace()
        {
            if (currentFrame == null)
                return null;

            try
            {
                // Extract center region and convert to grayscale
                Bitmap faceImage = ExtractAndNormalizeFace(currentFrame);
                
                if (faceImage != null)
                {
                    // Convert to byte array
                    using (MemoryStream ms = new MemoryStream())
                    {
                        faceImage.Save(ms, ImageFormat.Png);
                        byte[] faceData = ms.ToArray();
                        
                        Debug.WriteLine($"[FACE] Captured face data: {faceData.Length} bytes");
                        return faceData;
                    }
                }
                else
                {
                    Debug.WriteLine("[FACE] Failed to extract face");
                    return null;
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[FACE] Error capturing face: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Extract center region and convert to grayscale using System.Drawing
        /// </summary>
        private Bitmap ExtractAndNormalizeFace(Bitmap image)
        {
            try
            {
                // Calculate center region
                int centerX = image.Width / 2;
                int centerY = image.Height / 2;
                int faceSize = Math.Min(image.Width, image.Height) / 2;
                
                int x = Math.Max(0, centerX - faceSize / 2);
                int y = Math.Max(0, centerY - faceSize / 2);
                int width = Math.Min(faceSize, image.Width - x);
                int height = Math.Min(faceSize, image.Height - y);
                
                // Crop to center region
                Rectangle cropRect = new Rectangle(x, y, width, height);
                Bitmap croppedImage = image.Clone(cropRect, image.PixelFormat);
                
                // Convert to grayscale
                Bitmap grayImage = ConvertToGrayscale(croppedImage);
                
                // Resize to standard size
                Bitmap resizedImage = new Bitmap(grayImage, new Size(FACE_WIDTH, FACE_HEIGHT));
                
                Debug.WriteLine($"[FACE] Face extracted: {FACE_WIDTH}x{FACE_HEIGHT}");
                return resizedImage;
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[FACE] Error extracting face: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Convert image to grayscale using System.Drawing with histogram equalization
        /// </summary>
        private Bitmap ConvertToGrayscale(Bitmap original)
        {
            Bitmap grayscale = new Bitmap(original.Width, original.Height);
            
            // First pass: convert to grayscale
            for (int y = 0; y < original.Height; y++)
            {
                for (int x = 0; x < original.Width; x++)
                {
                    Color originalColor = original.GetPixel(x, y);
                    
                    // Calculate grayscale value (weighted average)
                    int grayValue = (int)(originalColor.R * 0.299 + originalColor.G * 0.587 + originalColor.B * 0.114);
                    
                    Color grayColor = Color.FromArgb(grayValue, grayValue, grayValue);
                    grayscale.SetPixel(x, y, grayColor);
                }
            }
            
            // Apply simple histogram equalization for better contrast
            grayscale = NormalizeHistogram(grayscale);
            
            return grayscale;
        }

        /// <summary>
        /// Normalize histogram for better contrast (simple version)
        /// </summary>
        private Bitmap NormalizeHistogram(Bitmap image)
        {
            try
            {
                // Calculate histogram
                int[] histogram = new int[256];
                for (int y = 0; y < image.Height; y++)
                {
                    for (int x = 0; x < image.Width; x++)
                    {
                        Color pixel = image.GetPixel(x, y);
                        histogram[pixel.R]++;
                    }
                }

                // Calculate cumulative distribution
                int[] cdf = new int[256];
                cdf[0] = histogram[0];
                for (int i = 1; i < 256; i++)
                {
                    cdf[i] = cdf[i - 1] + histogram[i];
                }

                // Find min and max
                int cdfMin = cdf.FirstOrDefault(v => v > 0);
                int totalPixels = image.Width * image.Height;

                // Apply equalization
                Bitmap result = new Bitmap(image.Width, image.Height);
                for (int y = 0; y < image.Height; y++)
                {
                    for (int x = 0; x < image.Width; x++)
                    {
                        Color pixel = image.GetPixel(x, y);
                        int oldValue = pixel.R;
                        
                        // Equalize
                        int newValue = (int)(((cdf[oldValue] - cdfMin) / (double)(totalPixels - cdfMin)) * 255);
                        newValue = Math.Max(0, Math.Min(255, newValue));
                        
                        Color newColor = Color.FromArgb(newValue, newValue, newValue);
                        result.SetPixel(x, y, newColor);
                    }
                }

                return result;
            }
            catch
            {
                return image; // Return original if equalization fails
            }
        }

        /// <summary>
        /// Compare two face images and return similarity score (0.0 to 1.0)
        /// </summary>
        public double CompareFaces(byte[] face1Data, byte[] face2Data)
        {
            try
            {
                if (face1Data == null || face2Data == null)
                    return 0.0;

                // Convert byte arrays to bitmaps
                Bitmap face1 = ByteArrayToBitmap(face1Data);
                Bitmap face2 = ByteArrayToBitmap(face2Data);
                
                if (face1 == null || face2 == null)
                    return 0.0;

                // Ensure both images are same size
                if (face1.Width != face2.Width || face1.Height != face2.Height)
                {
                    face1 = new Bitmap(face1, new Size(FACE_WIDTH, FACE_HEIGHT));
                    face2 = new Bitmap(face2, new Size(FACE_WIDTH, FACE_HEIGHT));
                }

                // Calculate similarity
                double similarity = CalculateImageSimilarity(face1, face2);
                
                Debug.WriteLine($"[FACE] Face similarity: {similarity:P2}");
                return similarity;
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[FACE] Error comparing faces: {ex.Message}");
                return 0.0;
            }
        }

        /// <summary>
        /// Calculate similarity between two images using improved algorithm (0.0 to 1.0)
        /// </summary>
        private double CalculateImageSimilarity(Bitmap img1, Bitmap img2)
        {
            try
            {
                // Use multiple metrics for better discrimination
                double pixelSimilarity = CalculatePixelSimilarity(img1, img2);
                double structuralSimilarity = CalculateStructuralSimilarity(img1, img2);
                
                // Weighted combination (pixel similarity is more important)
                double finalSimilarity = (pixelSimilarity * 0.7) + (structuralSimilarity * 0.3);
                
                Debug.WriteLine($"[FACE] Pixel similarity: {pixelSimilarity:P2}, Structural: {structuralSimilarity:P2}, Final: {finalSimilarity:P2}");
                
                return finalSimilarity;
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[FACE] Error calculating similarity: {ex.Message}");
                return 0.0;
            }
        }

        /// <summary>
        /// Calculate pixel-by-pixel similarity
        /// </summary>
        private double CalculatePixelSimilarity(Bitmap img1, Bitmap img2)
        {
            double totalDifference = 0;
            int pixelCount = img1.Width * img1.Height;

            for (int y = 0; y < img1.Height; y++)
            {
                for (int x = 0; x < img1.Width; x++)
                {
                    Color pixel1 = img1.GetPixel(x, y);
                    Color pixel2 = img2.GetPixel(x, y);
                    
                    // Use grayscale value (R, G, B should be same for grayscale)
                    int diff = Math.Abs(pixel1.R - pixel2.R);
                    
                    // Square the difference to penalize large differences more
                    totalDifference += (diff * diff);
                }
            }

            // Calculate root mean squared error
            double rmse = Math.Sqrt(totalDifference / pixelCount);
            
            // Convert to similarity score (0.0 to 1.0)
            // RMSE ranges from 0 to 255, so normalize
            double similarity = 1.0 - (rmse / 255.0);
            
            return Math.Max(0.0, similarity);
        }

        /// <summary>
        /// Calculate structural similarity (simplified SSIM)
        /// </summary>
        private double CalculateStructuralSimilarity(Bitmap img1, Bitmap img2)
        {
            try
            {
                // Calculate mean intensity
                double mean1 = 0, mean2 = 0;
                int pixelCount = img1.Width * img1.Height;

                for (int y = 0; y < img1.Height; y++)
                {
                    for (int x = 0; x < img1.Width; x++)
                    {
                        mean1 += img1.GetPixel(x, y).R;
                        mean2 += img2.GetPixel(x, y).R;
                    }
                }

                mean1 /= pixelCount;
                mean2 /= pixelCount;

                // Calculate variance and covariance
                double var1 = 0, var2 = 0, covar = 0;

                for (int y = 0; y < img1.Height; y++)
                {
                    for (int x = 0; x < img1.Width; x++)
                    {
                        double diff1 = img1.GetPixel(x, y).R - mean1;
                        double diff2 = img2.GetPixel(x, y).R - mean2;
                        
                        var1 += diff1 * diff1;
                        var2 += diff2 * diff2;
                        covar += diff1 * diff2;
                    }
                }

                var1 /= pixelCount;
                var2 /= pixelCount;
                covar /= pixelCount;

                // Calculate correlation coefficient
                double denominator = Math.Sqrt(var1 * var2);
                if (denominator < 0.0001) return 0.0;

                double correlation = covar / denominator;
                
                // Normalize to 0-1 range (correlation is -1 to 1)
                double similarity = (correlation + 1.0) / 2.0;
                
                return Math.Max(0.0, Math.Min(1.0, similarity));
            }
            catch
            {
                return 0.5; // Return neutral value on error
            }
        }

        /// <summary>
        /// Check if captured face matches stored face
        /// </summary>
        public bool AuthenticateFace(byte[] capturedFaceData, byte[] storedFaceData, out double confidence)
        {
            confidence = CompareFaces(capturedFaceData, storedFaceData);
            bool isMatch = confidence >= MATCH_THRESHOLD;
            
            Debug.WriteLine($"[FACE] Authentication: {(isMatch ? "SUCCESS" : "FAILED")} (confidence: {confidence:P2})");
            return isMatch;
        }

        /// <summary>
        /// Convert byte array to Bitmap
        /// </summary>
        private Bitmap ByteArrayToBitmap(byte[] imageData)
        {
            try
            {
                using (MemoryStream ms = new MemoryStream(imageData))
                {
                    return new Bitmap(ms);
                }
            }
            catch
            {
                return null;
            }
        }

        public void StopCamera()
        {
            if (videoSource != null && videoSource.IsRunning)
            {
                videoSource.SignalToStop();
                videoSource.WaitForStop();
                videoSource.NewFrame -= VideoSource_NewFrame;
                CameraStopped?.Invoke(this, EventArgs.Empty);
            }
        }

        public BitmapImage ByteArrayToBitmapImage(byte[] imageData)
        {
            if (imageData == null || imageData.Length == 0)
                return null;

            var image = new BitmapImage();
            using (var mem = new MemoryStream(imageData))
            {
                mem.Position = 0;
                image.BeginInit();
                image.CreateOptions = BitmapCreateOptions.PreservePixelFormat;
                image.CacheOption = BitmapCacheOption.OnLoad;
                image.UriSource = null;
                image.StreamSource = mem;
                image.EndInit();
            }
            image.Freeze();
            return image;
        }

        public BitmapImage BitmapToBitmapImage(Bitmap bitmap)
        {
            using (MemoryStream memory = new MemoryStream())
            {
                bitmap.Save(memory, ImageFormat.Bmp);
                memory.Position = 0;
                BitmapImage bitmapimage = new BitmapImage();
                bitmapimage.BeginInit();
                bitmapimage.StreamSource = memory;
                bitmapimage.CacheOption = BitmapCacheOption.OnLoad;
                bitmapimage.EndInit();
                bitmapimage.Freeze();
                return bitmapimage;
            }
        }
    }
}
