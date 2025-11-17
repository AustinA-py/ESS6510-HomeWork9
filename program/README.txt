# Austin Averill's Population By Region Viewer

A desktop application for exploring US census population data by region with interactive chloropleth maps.

## Quick Start

1. **Double-click `PopulationViewer.exe`** to launch the application
2. The application will load US states data from the Census TIGERweb API
3. Select a region by clicking on the map
4. Click "Create Chloro" to view county-level population data
5. Customize and export your chloropleth maps

## Features

### Regional Overview
- Interactive map showing all 50 US states grouped into 5 regions:
  - **West**: WA, OR, CA, NV, ID, MT, WY, UT, CO, AK, HI
  - **Midwest**: ND, SD, NE, KS, MN, IA, MO, WI, IL, IN, MI, OH
  - **Northeast**: PA, MD, DE, NJ, CT, RI, MA, NY, VT, NH, ME
  - **Southeast**: DC, VA, WV, KY, AR, LA, MS, AL, GA, FL, SC, NC, TN
  - **Southwest**: OK, TX, NM, AZ
- Click any region to explore county-level data

### Chloropleth Map Generator
- **Classification Methods**:
  - Quantile: Equal number of counties per class
  - Natural Breaks (Jenks): Minimizes variance within classes
  - Equal Interval: Equal range per class
  
- **Color Schemes**: Choose from 7 professionally designed color palettes
  - Reds, Blues, Greens, Oranges, Purples, YlOrRd, RdYlBu
  
- **Interactive Features**:
  - Hover over counties to see name and population (1-second delay)
  - North arrow and scale bar for context
  - Legend with population ranges
  - Special insets for Alaska and Hawaii (West region)
  
- **Export**: Save your map as a self-contained HTML file

## System Requirements

- **Operating System**: Windows 7 or later (64-bit)
- **Internet**: Required for fetching live Census data
- **Disk Space**: ~200 MB free space
- **Memory**: 4 GB RAM recommended
- **Display**: 1280x800 or higher resolution recommended

## Usage Tips

### First Launch
- The first launch may take a few seconds as the application initializes
- You'll see a loading screen while state data is fetched from the Census API
- Once loaded, the main map will display all US regions

### Selecting a Region
1. Hover over any region to highlight it in blue
2. Click the highlighted region
3. Click "Create Chloro" button
4. County data will load (this may take 10-30 seconds depending on region size)

### Creating a Chloropleth
1. **Select Classification Method**: Choose how population data is grouped
2. **Select Color Scheme**: Click on a color ramp to preview (hover to see name)
3. **Click "Apply Chloropleth"**: Map will update with colored counties
4. **Hover over counties**: After 1 second, a tooltip shows county name and population
5. **Export**: Save as HTML to share or print

### Region-Specific Notes
- **West Region**: Alaska and Hawaii display in separate insets at the bottom
- **Southwest**: Includes TX (254 counties) - may take longer to load
- **All Regions**: Data excludes Puerto Rico and US territories

## Data Source

All data is fetched live from:
- **Census TIGERweb REST API** (MapServer 54 for states, 55 for counties)
- **Vintage**: 2020 Census boundaries
- **Population**: 2010 Census (POP100 field)

## Troubleshooting

### Application Won't Start
- **Windows Security Warning**: Click "More info" → "Run anyway"
- **Antivirus**: Add `PopulationViewer.exe` to your antivirus exceptions
- **No Internet**: Application requires internet to fetch Census data

### Counties Won't Load
- **Slow Connection**: Larger regions (Southwest, Southeast) may take 30+ seconds
- **API Timeout**: Try again - Census servers may be busy
- **Firewall**: Ensure outbound HTTPS connections are allowed

### Map Display Issues
- **Text Too Small**: Application works best at 1280x800 or higher resolution
- **Colors Not Showing**: Ensure you clicked "Apply Chloropleth" button
- **Legend Overlapping**: Try a different region or classification method

### Export Issues
- **HTML Won't Save**: Ensure you have write permissions to the selected folder
- **Browser Won't Open**: Manually navigate to the saved HTML file

## Known Limitations

- Puerto Rico and US territories are excluded from Southeast region
- Population data is from 2010 Census (latest available in TIGERweb)
- Large regions (e.g., Texas with 254 counties) may take longer to load
- Export creates HTML files only (PNG export not supported)

## Credits

**Developed by**: Austin Averill  
**Course**: ESS6510 - Homework 9  
**Data Source**: US Census Bureau TIGERweb REST API  
**Built with**: Python, tkinter, matplotlib, numpy, requests

## Version

**Version**: 1.0  
**Build Date**: November 2025  
**Python**: 3.13.5  

## License

This application is provided for educational purposes.
Census data is in the public domain (US Government).

## Support

For issues or questions, refer to the course materials or contact the developer.

---

**Note**: This is a standalone application - no installation required!
All dependencies are bundled. Just run and explore!
