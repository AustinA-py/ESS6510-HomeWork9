# Build script for creating executable
# Run this script from the project root to package the application into an executable

Write-Host "Building Austin Averill's Population By Region Viewer Executable..." -ForegroundColor Cyan
Write-Host ""

# Change to project root directory (parent of build_scripts)
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath
Set-Location $projectRoot

Write-Host "Project root: $projectRoot" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.venv\Scripts\activate

# Install PyInstaller if not already installed
Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
pip install pyinstaller

# Clean previous builds
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }

# Build the executable
Write-Host "Building executable with PyInstaller..." -ForegroundColor Yellow
pyinstaller build_scripts\build_executable.spec --clean

# Check if build was successful
if (Test-Path "dist\PopulationViewer.exe") {
    Write-Host ""
    Write-Host "SUCCESS! Executable created successfully!" -ForegroundColor Green
    Write-Host "Location: dist\PopulationViewer.exe" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now share the entire 'dist' folder or just the PopulationViewer.exe file." -ForegroundColor Cyan
    Write-Host "The executable is completely self-contained and includes all dependencies." -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "ERROR: Build failed. Check the output above for errors." -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
