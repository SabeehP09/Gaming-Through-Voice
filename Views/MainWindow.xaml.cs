using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Animation;
using System.Windows.Media.Imaging;
using System.Windows.Shapes;

namespace GamingThroughVoiceRecognitionSystem.Views
{
    public partial class MainWindow : Window
    {
        private bool isMaximized = false; // Track window state

        public MainWindow()
        {
            InitializeComponent();

            // Initialize button hover/pulse animations
            SetupButtonAnimations(LoginButton);
            SetupButtonAnimations(SignUpButton);
            SetupButtonAnimations(CloseButton);
            SetupButtonAnimations(MinimizeButton);
            SetupButtonAnimations(MaximizeButton);
        }

        // -----------------------
        // Window Loaded Event
        // -----------------------
        private void Window_Loaded(object sender, RoutedEventArgs e)
        {
            // Placeholder for background animation or voice recognition startup
            // Example: StartStoryboard(BackgroundAnimationStoryboard);
        }

        // -----------------------
        // Drag Window Only on Top Area
        // -----------------------
        private void WindowChrome_MouseLeftButtonDown(object sender, MouseButtonEventArgs e)
        {
            if (e.ButtonState == MouseButtonState.Pressed)
                this.DragMove();
        }

        // -----------------------
        // Close Button
        // -----------------------
        private void CloseButton_Click(object sender, RoutedEventArgs e)
        {
            this.Close();
        }

        // -----------------------
        // Minimize Button
        // -----------------------
        private void MinimizeButton_Click(object sender, RoutedEventArgs e)
        {
            this.WindowState = WindowState.Minimized;
        }

        // -----------------------
        // Maximize/Restore Button
        // -----------------------
        private void MaximizeButton_Click(object sender, RoutedEventArgs e)
        {
            if (isMaximized)
            {
                this.WindowState = WindowState.Normal;
                this.Width = 900;
                this.Height = 600;
                isMaximized = false;
            }
            else
            {
                this.WindowState = WindowState.Maximized;
                isMaximized = true;
            }
        }

        // -----------------------
        // Login Button Click
        // -----------------------
        private void LoginButton_Click(object sender, RoutedEventArgs e)
        {
            // TODO: Add face recognition login logic here
            LoginWindow loginWindow = new LoginWindow();
            loginWindow.Show();
            this.Close();
          //  MessageBox.Show("Login button clicked - integrate face/voice recognition");
        }

        // -----------------------
        // SignUp Button Click
        // -----------------------
        private void SignUpButton_Click(object sender, RoutedEventArgs e)
        {
            // TODO: Add face recognition signup logic here
            SignUpWindow signUpWindow = new SignUpWindow();
            signUpWindow.Show();
            this.Close();
            //MessageBox.Show("SignUp button clicked - integrate face/voice registration");
        }

        // -----------------------
        // Button Hover & Pulse Animation
        // -----------------------
        private void SetupButtonAnimations(Button button)
        {
            // Scale transform
            var scale = new ScaleTransform(1, 1);
            button.RenderTransformOrigin = new Point(0.5, 0.5);
            button.RenderTransform = scale;

            // Mouse Enter
            button.MouseEnter += (s, e) =>
            {
                var enlarge = new DoubleAnimation(1.0, 1.1, TimeSpan.FromMilliseconds(200))
                {
                    EasingFunction = new CubicEase { EasingMode = EasingMode.EaseOut }
                };
                scale.BeginAnimation(ScaleTransform.ScaleXProperty, enlarge);
                scale.BeginAnimation(ScaleTransform.ScaleYProperty, enlarge);
            };

            // Mouse Leave
            button.MouseLeave += (s, e) =>
            {
                var shrink = new DoubleAnimation(1.1, 1.0, TimeSpan.FromMilliseconds(200))
                {
                    EasingFunction = new CubicEase { EasingMode = EasingMode.EaseOut }
                };
                scale.BeginAnimation(ScaleTransform.ScaleXProperty, shrink);
                scale.BeginAnimation(ScaleTransform.ScaleYProperty, shrink);
            };

            // Optional Pulse Animation (continuous subtle pulse)
            var pulse = new DoubleAnimation(1.0, 1.03, TimeSpan.FromSeconds(1))
            {
                AutoReverse = true,
                RepeatBehavior = RepeatBehavior.Forever,
                EasingFunction = new SineEase { EasingMode = EasingMode.EaseInOut }
            };
            scale.BeginAnimation(ScaleTransform.ScaleXProperty, pulse);
            scale.BeginAnimation(ScaleTransform.ScaleYProperty, pulse);
        }

        private void Window_MouseLeftButtonDown(object sender, MouseButtonEventArgs e)
        {
            if (e.ButtonState == MouseButtonState.Pressed)
                this.DragMove();
        }
    }
}