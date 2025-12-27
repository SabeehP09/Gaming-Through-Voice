using System;
using System.Windows;
using System.Windows.Media;

namespace GamingThroughVoiceRecognitionSystem.Services
{
    public enum AppTheme
    {
        Light,
        Dark
    }

    public static class ThemeManager
    {
        private static AppTheme currentTheme = AppTheme.Light;

        public static event EventHandler ThemeChanged;

        public static AppTheme CurrentTheme
        {
            get => currentTheme;
            set
            {
                if (currentTheme != value)
                {
                    currentTheme = value;
                    ApplyTheme(value);
                    ThemeChanged?.Invoke(null, EventArgs.Empty);
                }
            }
        }

        public static void ApplyTheme(AppTheme theme)
        {
            var resources = Application.Current.Resources;

            if (theme == AppTheme.Dark)
            {
                // ===== DARK GAMING THEME - Cyberpunk/Neon Style =====
                
                // Vibrant Gaming Colors
                resources["PrimaryColor"] = (Color)ColorConverter.ConvertFromString("#FF00FF"); // Neon Magenta
                resources["SecondaryColor"] = (Color)ColorConverter.ConvertFromString("#00FFFF"); // Cyan
                resources["AccentColor"] = (Color)ColorConverter.ConvertFromString("#FFD700"); // Gold
                resources["AccentColor2"] = (Color)ColorConverter.ConvertFromString("#FF1493"); // Deep Pink

                // Dark Gaming Backgrounds
                resources["BackgroundDarkBrush"] = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#0A0E27")); // Deep Space Blue
                resources["BackgroundMediumBrush"] = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#1A1F3A")); // Dark Navy
                resources["BackgroundLightBrush"] = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#252B48")); // Lighter Navy

                // Neon Text
                resources["TextPrimaryBrush"] = new SolidColorBrush(Colors.White);
                resources["TextSecondaryBrush"] = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#00FFFF")); // Cyan
                resources["TextTertiaryBrush"] = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#B8B8FF")); // Light Purple
                resources["TextAccentBrush"] = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#FF00FF")); // Magenta

                // Gaming Glass Effects with Neon Glow
                resources["GlassBackgroundBrush"] = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#25FFFFFF"));
                resources["GlassBorderBrush"] = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#60FF00FF")); // Neon Magenta Border
                resources["SurfaceGlassBrush"] = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#35FFFFFF"));

                // Gaming Card Backgrounds
                resources["CardBackgroundBrush"] = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#1E2442"));
                resources["CardHoverBackgroundBrush"] = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#2A3052"));
                
                // Sidebar Background
                resources["SidebarBackgroundBrush"] = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#15192E"));
            }
            else
            {
                // ===== LIGHT GAMING THEME - Bright/Professional Style =====
                
                // Bright Gaming Colors
                resources["PrimaryColor"] = (Color)ColorConverter.ConvertFromString("#6366F1"); // Indigo
                resources["SecondaryColor"] = (Color)ColorConverter.ConvertFromString("#8B5CF6"); // Purple
                resources["AccentColor"] = (Color)ColorConverter.ConvertFromString("#EC4899"); // Pink
                resources["AccentColor2"] = (Color)ColorConverter.ConvertFromString("#F59E0B"); // Amber

                // Light Backgrounds - Soft Gradient
                resources["BackgroundDarkBrush"] = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#F5F7FA")); // Very Light Blue-Gray
                resources["BackgroundMediumBrush"] = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#FFFFFF")); // Pure White
                resources["BackgroundLightBrush"] = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#FAFBFC")); // Off White

                // Dark Text for Light Background
                resources["TextPrimaryBrush"] = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#1A202C")); // Dark Navy
                resources["TextSecondaryBrush"] = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#4A5568")); // Gray
                resources["TextTertiaryBrush"] = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#718096")); // Light Gray
                resources["TextAccentBrush"] = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#6366F1")); // Indigo

                // Light Glass Effects - Clean White Cards
                resources["GlassBackgroundBrush"] = new SolidColorBrush(Colors.White);
                resources["GlassBorderBrush"] = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#E2E8F0")); // Light Blue-Gray Border
                resources["SurfaceGlassBrush"] = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#F7FAFC"));

                // Light Card Backgrounds - White with Subtle Shadow
                resources["CardBackgroundBrush"] = new SolidColorBrush(Colors.White);
                resources["CardHoverBackgroundBrush"] = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#F7FAFC"));
                
                // Sidebar Background - Soft Gray
                resources["SidebarBackgroundBrush"] = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#F7FAFC"));
            }

            // Update gradient brushes - Gaming Style
            var backgroundGradient = new LinearGradientBrush
            {
                StartPoint = new Point(0, 0),
                EndPoint = new Point(1, 1)
            };
            
            if (theme == AppTheme.Dark)
            {
                // Dark: Deep Purple to Cyan gradient (Cyberpunk)
                backgroundGradient.GradientStops.Add(new GradientStop((Color)ColorConverter.ConvertFromString("#1A0B2E"), 0));
                backgroundGradient.GradientStops.Add(new GradientStop((Color)ColorConverter.ConvertFromString("#16213E"), 0.5));
                backgroundGradient.GradientStops.Add(new GradientStop((Color)ColorConverter.ConvertFromString("#0F3460"), 1));
            }
            else
            {
                // Light: Soft Professional Gradient (Subtle Blue-Gray to White)
                backgroundGradient.GradientStops.Add(new GradientStop((Color)ColorConverter.ConvertFromString("#EDF2F7"), 0)); // Light Blue-Gray
                backgroundGradient.GradientStops.Add(new GradientStop((Color)ColorConverter.ConvertFromString("#F7FAFC"), 0.5)); // Very Light Gray
                backgroundGradient.GradientStops.Add(new GradientStop((Color)ColorConverter.ConvertFromString("#FFFFFF"), 1)); // Pure White
            }
            resources["BackgroundGradientBrush"] = backgroundGradient;

            // Primary Gaming Gradient
            var primaryGradient = new LinearGradientBrush
            {
                StartPoint = new Point(0, 0),
                EndPoint = new Point(1, 1)
            };
            primaryGradient.GradientStops.Add(new GradientStop((Color)resources["PrimaryColor"], 0));
            primaryGradient.GradientStops.Add(new GradientStop((Color)resources["SecondaryColor"], 1));
            resources["PrimaryGradientBrush"] = primaryGradient;

            // Accent Gradient
            var accentGradient = new LinearGradientBrush
            {
                StartPoint = new Point(0, 0),
                EndPoint = new Point(1, 1)
            };
            accentGradient.GradientStops.Add(new GradientStop((Color)resources["AccentColor"], 0));
            accentGradient.GradientStops.Add(new GradientStop((Color)resources["AccentColor2"], 1));
            resources["AccentGradientBrush"] = accentGradient;

            // Purple Cyan Gradient (for special elements)
            var purpleCyanGradient = new LinearGradientBrush
            {
                StartPoint = new Point(0, 0),
                EndPoint = new Point(1, 1)
            };
            if (theme == AppTheme.Dark)
            {
                purpleCyanGradient.GradientStops.Add(new GradientStop((Color)ColorConverter.ConvertFromString("#A855F7"), 0));
                purpleCyanGradient.GradientStops.Add(new GradientStop((Color)ColorConverter.ConvertFromString("#06B6D4"), 1));
            }
            else
            {
                purpleCyanGradient.GradientStops.Add(new GradientStop((Color)ColorConverter.ConvertFromString("#C084FC"), 0));
                purpleCyanGradient.GradientStops.Add(new GradientStop((Color)ColorConverter.ConvertFromString("#22D3EE"), 1));
            }
            resources["PurpleCyanGradient"] = purpleCyanGradient;
        }

        // Store current user ID for user-specific settings
        private static int currentUserId = -1;

        public static void Initialize()
        {
            // Default to Dark theme on startup
            // User-specific theme will be loaded after login
            currentTheme = AppTheme.Dark;
            ApplyTheme(AppTheme.Dark);
        }

        public static void InitializeForUser(int userId, string userTheme)
        {
            // Set current user
            currentUserId = userId;
            
            // Load user-specific theme from database
            var theme = userTheme == "Dark" ? AppTheme.Dark : AppTheme.Light;
            
            // Apply theme
            currentTheme = theme;
            ApplyTheme(theme);
        }

        public static void SaveThemePreference()
        {
            // Theme is now saved per user in the database via SettingsControl
            // This method is kept for compatibility but doesn't save globally anymore
        }
    }
}
