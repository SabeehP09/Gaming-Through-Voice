# Game Icons Information

## Default Game Icons

To make your game cards look more professional, you can add custom icons for the default games.

### Recommended Icon Locations:

Place game icons in the `Resources` folder with these names:
- `subway_surfers_icon.png`
- `temple_run_icon.png`
- `flappy_bird_icon.png`

### Icon Specifications:
- **Format**: PNG, ICO, or JPG
- **Size**: 256x256 pixels (recommended)
- **Background**: Transparent (for PNG) or solid color
- **Style**: Square or rounded square

### Where to Find Icons:
1. **Official Game Websites**: Download from the game's official site
2. **Icon Libraries**: 
   - IconFinder (https://www.iconfinder.com/)
   - Flaticon (https://www.flaticon.com/)
   - Icons8 (https://icons8.com/)
3. **Extract from Game**: Use tools to extract icons from game executables
4. **Create Custom**: Design your own using tools like:
   - Adobe Illustrator
   - Figma
   - Canva
   - GIMP (free)

### Updating Database with Icons:

After adding icon files, update the database:

```sql
-- Update Subway Surfers icon
UPDATE games 
SET IconPath = 'C:\Path\To\Your\Project\Resources\subway_surfers_icon.png'
WHERE GameName = 'Subway Surfers' AND IsDefault = 1;

-- Update Temple Run icon
UPDATE games 
SET IconPath = 'C:\Path\To\Your\Project\Resources\temple_run_icon.png'
WHERE GameName = 'Temple Run' AND IsDefault = 1;

-- Update Flappy Bird icon
UPDATE games 
SET IconPath = 'C:\Path\To\Your\Project\Resources\flappy_bird_icon.png'
WHERE GameName = 'Flappy Bird' AND IsDefault = 1;
```

### Fallback:
If no icon is provided, the system will display a default game emoji (🎮) which still looks professional and clean.

## User-Added Game Icons

When users add their own games:
1. The system automatically tries to detect the game icon from the game's directory
2. Users can manually browse and select a custom icon
3. The icon preview is shown immediately after selection
4. Icons are stored with absolute paths in the database

## Best Practices:
- Keep icon files under 1MB for faster loading
- Use consistent styling across all game icons
- Test icons on both light and dark themes
- Ensure icons are clearly visible at small sizes (64x64)
