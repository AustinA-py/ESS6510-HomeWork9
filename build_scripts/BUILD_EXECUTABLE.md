# Building the Executable

This guide explains how to package the Population By Region Viewer into a standalone executable.

## Quick Start

### Option 1: Automated Build (Recommended)

From the project root directory, run the PowerShell build script:

```powershell
.\build_scripts\build_executable.ps1
```

This will:
1. Activate the virtual environment
2. Install PyInstaller
3. Clean previous builds
4. Create the executable
5. Place the result in the `dist` folder

### Option 2: Manual Build

If you prefer to build manually:

```powershell
# Activate virtual environment
.venv\Scripts\activate

# Install PyInstaller
pip install pyinstaller

# Build the executable (from project root)
pyinstaller build_scripts\build_executable.spec --clean
```

## Output

After successful build, you'll find:
- `dist/PopulationViewer.exe` - The standalone executable
- The executable is approximately 50-100 MB (includes Python runtime and all dependencies)

## Distribution

The executable is completely self-contained:
- **Single file**: You can share just `PopulationViewer.exe`
- **No installation**: Users just double-click to run
- **No Python required**: All dependencies are bundled
- **Internet required**: The app fetches live data from Census TIGERweb APIs

## Troubleshooting

### Build Fails
- Ensure you have activated the virtual environment
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Try deleting `build` and `dist` folders and rebuild

### Executable Won't Run
- Windows may show a security warning - click "More info" then "Run anyway"
- Antivirus software may quarantine it - add an exception
- Try running from command prompt to see error messages

### Executable is Too Large
- This is normal - it includes Python runtime + matplotlib + numpy
- You can use UPX compression (already enabled in spec file)
- For smaller size, consider using `--onedir` mode instead of `--onefile`

## Advanced Options

### Custom Icon
To add a custom icon:
1. Get a `.ico` file
2. Update `build_scripts\build_executable.spec`: change `icon=None` to `icon='path/to/icon.ico'`
3. Rebuild

### Enable Console Window (for debugging)
In `build_scripts\build_executable.spec`, change:
```python
console=False,  # Change to True
```

### One-Directory Mode (faster startup)
In `build_scripts\build_executable.spec`, replace the `EXE` section with:
```python
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PopulationViewer',
    debug=False,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='PopulationViewer',
)
```

## System Requirements (for end users)

- Windows 7 or later (64-bit)
- Internet connection (to fetch Census data)
- ~200 MB free disk space
- 4 GB RAM recommended

## Notes

- First launch may take a few seconds as Python runtime initializes
- Data is fetched fresh from Census APIs each time
- No data is stored locally (except exported HTML files)
