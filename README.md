# Austin Averill's Population By Region Viewer

A Python-based GUI application for visualizing US population data by region and creating chloropleth maps at the county level using live Census Bureau data.

## 🎯 Quick Start

### Option 1: Use the Executable (Recommended)
**No Python installation required!**

1. Download `dist/PopulationViewer.exe` (39.73 MB)
2. Double-click to run
3. Internet connection required for Census API data

See `dist/README.txt` for detailed user instructions.

### Option 2: Run from Source

1. Install Python 3.8+ and dependencies:
```powershell
pip install -r requirements.txt
```

2. Run the application:
```powershell
python main.py
```

## 📊 Overview

This application provides an interactive map interface with:
- **Live Census Data**: Fetches current state and county boundaries from US Census TIGERweb REST API
- **Regional Organization**: Five US regions with color-coded visualization
- **County Chloropleth Maps**: Interactive population visualization with multiple classification methods
- **Alaska/Hawaii Insets**: Proper display of non-contiguous states
- **HTML Export**: Self-contained maps with embedded base64 images
- **Optimized Performance**: Region-specific county loading and caching

## 🗂️ Project Structure

```
ESS6510-HomeWork9/
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies (matplotlib, numpy, requests, jenkspy)
├── README.md                        # This file
│
├── dist/                            # 📦 Distribution folder
│   ├── PopulationViewer.exe        # Standalone Windows executable (39.73 MB)
│   └── README.txt                  # End-user documentation
│
├── build_scripts/                   # 🔧 Build configuration and documentation
│   ├── build_executable.spec       # PyInstaller configuration
│   ├── build_executable.ps1        # Automated build script
│   ├── BUILD_EXECUTABLE.md         # Instructions for rebuilding the executable
│   └── EXECUTABLE_BUILD_SUCCESS.md # Build documentation and success notes
│
├── examples/                        # 📄 Sample exported HTML files
│   ├── southwest.html              # Example Southwest region chloropleth export
│   └── southeast.html              # Example Southeast region chloropleth export
│
├── geometry_query_params/           # Census API query configurations
│   ├── states_query.json           # State boundaries query (MapServer 54)
│   └── counties_query.json         # County boundaries query (MapServer 55)
│
└── src/                            # Source code
    ├── data/
    │   ├── __init__.py
    │   └── api_data_manager.py     # Census API integration with coordinate conversion
    └── gui/
        ├── __init__.py
        ├── main_application.py     # Main application window with region selection
        └── chloropleth_generator.py # Chloropleth generation with tooltips and export
```

## 🗺️ Regional Definitions

The application divides the United States into five regions:

- **West** (11 states): Washington, Montana, Idaho, Oregon, Wyoming, California, Nevada, Utah, Colorado, Alaska, Hawaii
- **Midwest** (12 states): North Dakota, South Dakota, Nebraska, Kansas, Minnesota, Iowa, Missouri, Wisconsin, Illinois, Indiana, Michigan, Ohio  
- **Northeast** (11 states): Pennsylvania, Maryland, Delaware, New Jersey, Connecticut, Rhode Island, Massachusetts, New York, Vermont, New Hampshire, Maine
- **Southeast** (13 states + DC): Washington D.C., Virginia, West Virginia, Kentucky, Arkansas, Louisiana, Mississippi, Alabama, Georgia, Florida, South Carolina, North Carolina, Tennessee
- **Southwest** (4 states): Oklahoma, Texas, New Mexico, Arizona

**Note**: Puerto Rico and US Virgin Islands are excluded from the Southeast region.

## 🎨 Features

### Main Application Window
- **Interactive Regional Map**: Click any state to select its region
- **Color-Coded Regions**: Visual distinction between all five regions
- **Alaska/Hawaii Insets**: Properly positioned non-contiguous states
- **Live Data Loading**: Real-time fetch from Census TIGERweb API
- **Loading Overlays**: Full-screen progress indicators during data fetch
- **Region Caching**: Instant reload on revisiting regions

### Chloropleth Generator
- **Classification Methods**: 
  - Quantile (equal count per class)
  - Equal Interval (equal range per class)
  - Jenks Natural Breaks (optimal variance-based breaks)
- **Color Schemes** (7 options with visual previews):
  - YlOrRd (Yellow-Orange-Red)
  - YlGnBu (Yellow-Green-Blue)
  - PuBuGn (Purple-Blue-Green)
  - RdPu (Red-Purple)
  - OrRd (Orange-Red)
  - Greens
  - Blues
- **Interactive Tooltips**:
  - County hover with 1-second delay
  - Displays county name, state, and population
  - Light beige background (#F5F5DC)
  - Instant hide on mouse exit
- **Map Elements** (region-specific positioning):
  - Legend with classification breaks
  - North arrow
  - Scale bar
- **HTML Export**: Base64-embedded PNG for self-contained sharing
- **Zoom/Pan**: Full matplotlib navigation toolbar

## 🔧 Technical Details

### Data Sources
- **Census TIGERweb REST API**:
  - States: MapServer 54 (STATE layer with FIPS codes)
  - Counties: MapServer 55 (COUNTY layer with population estimates)
- **Coordinate System**: Web Mercator (EPSG:3857) → WGS84 conversion
- **Data Format**: GeoJSON FeatureCollection

### Performance Optimizations
- **STATE FIPS Filtering**: Loads only counties for selected region's states
- **Region Caching**: Stores loaded counties to prevent redundant API calls
- **Mouse Throttling**: 100ms delay on hover events
- **Bounding Box Checks**: Pre-filters counties before polygon intersection tests

### Technology Stack
- **GUI Framework**: tkinter (Python standard library)
- **Mapping**: matplotlib 3.5+ with Polygon patches
- **HTTP Requests**: requests library for Census API
- **Array Processing**: numpy 1.20+ for coordinate transformations
- **Classification**: jenkspy for Natural Breaks (Jenks) algorithm
- **Threading**: Async data loading with loading overlays
- **Export**: base64 encoding for embedded HTML images

### Executable Packaging
- **Tool**: PyInstaller 6.16.0
- **Mode**: Single-file executable
- **Size**: 39.73 MB (includes Python runtime + all dependencies)
- **Platforms**: Windows 64-bit
- **Dependencies Bundled**: Python 3.13, matplotlib, numpy, tkinter, requests, jenkspy, PIL

## 📋 Usage Guide

### Running the Application

1. **Launch**: Double-click `PopulationViewer.exe` or run `python main.py`
2. **Initial Load**: Wait 5-10 seconds for state boundaries to load from Census API
3. **Main Map**: Displays all 50 states + DC colored by region

### Creating a Chloropleth Map

1. **Select Region**: Click any state on the main map
   - Selected region highlights
   - "Create Chloro" button becomes enabled
   
2. **Open Chloropleth Window**: Click "Create Chloro"
   - Loading overlay appears
   - Counties load from Census API (1-30 seconds depending on region)
   - Initial map shows counties with black outlines
   
3. **Configure Visualization**:
   - Choose **Classification Method**:
     - Quantile: Equal number of counties per class
     - Equal Interval: Equal population range per class
     - Jenks: Statistically optimal natural breaks
   - Choose **Color Scheme**: Click color ramp images to select
   
4. **Apply Colors**: Click "Apply Chloropleth"
   - Counties fill with colors based on classification
   - Legend updates with population breaks
   - Map elements reposition based on region
   
5. **Interact**:
   - **Hover**: Mouse over counties to see details (1-second delay)
   - **Zoom**: Use matplotlib toolbar to zoom/pan
   - **Export**: Click "Export to HTML" to save map

### Export Format

HTML exports contain:
- Self-contained HTML file with embedded base64 PNG image
- No external dependencies
- Can be opened in any web browser
- Suitable for email sharing or web hosting

## 🛠️ Development

### Requirements
```
matplotlib>=3.5.0
numpy>=1.20.0
requests>=2.25.0
jenkspy>=0.3.0
```

### Rebuilding the Executable

```powershell
# Clean previous builds
Remove-Item -Recurse -Force dist, build

# Build with PyInstaller
pyinstaller build_scripts\build_executable.spec --clean
```

Or use the automated script:
```powershell
.\build_scripts\build_executable.ps1
```

See `build_scripts\BUILD_EXECUTABLE.md` for detailed instructions.

### API Query Configuration

Census API queries are defined in `geometry_query_params/`:
- `states_query.json`: STATE layer query (all 51 features)
- `counties_query.json`: COUNTY layer query (filtered by STATE FIPS)

Modify `where` clauses to adjust data filtering.

## 🚨 Known Limitations

- **Internet Required**: Application requires active connection to Census TIGERweb API
- **API Availability**: Dependent on Census Bureau server uptime
- **Loading Times**: Vary by region size and network speed
  - Southwest: ~1-2 seconds (379 counties)
  - Midwest: ~15-20 seconds (1,055 counties)
  - West: ~10-15 seconds (474 counties)
- **Windows Only**: Executable is Windows 64-bit specific
- **Memory Usage**: ~150-300 MB when all regions cached

## 🔐 Security Notes

### Windows SmartScreen
First-time users may see "Windows protected your PC" warning.
- **Action**: Click "More info" → "Run anyway"
- **Reason**: Executable is not digitally signed (requires paid certificate)

### Antivirus Software
Some AV programs may flag PyInstaller executables.
- **Action**: Add exception or whitelist the file
- **Reason**: Bundled Python runtime triggers heuristic detection

## 📝 License

Created for ESS6510 coursework by Austin Averill (November 2025).

## 🙏 Acknowledgments

- **Data Source**: US Census Bureau TIGERweb REST API
- **Classification**: jenkspy library for Jenks Natural Breaks algorithm
- **Packaging**: PyInstaller for executable generation