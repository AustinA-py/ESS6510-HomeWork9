"""
Main Application Window for Austin Averill's Population By Region Viewer

This module contains the main application window that handles the initial state
showing the US map with regional coloring and manages transitions to the 
chloropleth generator.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.patches as mpatches
from matplotlib.patches import Polygon
import numpy as np
import threading
from typing import Optional, Dict, List, Tuple

from data.api_data_manager import APIDataManager
from data.data_manager import REGIONS, REGION_COLORS
from gui.chloropleth_generator import ChloroplethGenerator
from gui.api_loading_screen import APIDataLoadingManager

class RegionalPopulationViewer:
    """Main application for the Regional Population Viewer"""
    
    def __init__(self):
        """Initialize the application"""
        # Initialize main window
        self.root = tk.Tk()
        self.root.title("Austin Averill's Population By Region Viewer")
        self.root.geometry("1200x800")
        self.root.configure(bg='white')
        
        # Create loading screen as a frame within the main window
        self.loading_frame = self._create_loading_frame()
        
        # Data manager
        self.data_manager = APIDataManager()
        
        # Current state
        self.selected_region = None
        self.chloropleth_generator = None
        self.last_hovered_region = None  # Cache for hover state
        self.last_motion_time = 0  # Throttle mouse motion events
        
        # GUI components (will be created after loading)
        self.main_frame = None
        self.map_frame = None
        self.control_frame = None
        self.figure = None
        self.canvas = None
        self.ax_main = None
        self.ax_alaska = None
        self.ax_hawaii = None
        self.create_chloro_btn = None
        
        # Loading state
        self.loading_manager = None
        
        # Start loading process
        self._start_loading_process()
    
    def _create_loading_frame(self):
        """Create the loading screen frame"""
        loading_frame = tk.Frame(self.root, bg='white')
        loading_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            loading_frame,
            text="Austin Averill's Population By Region Viewer",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        title_label.pack(pady=(100, 30))
        
        # Subtitle
        subtitle_label = tk.Label(
            loading_frame,
            text="ESS6510 - Homework 9",
            font=('Arial', 10),
            bg='white',
            fg='#7f8c8d'
        )
        subtitle_label.pack(pady=(0, 40))
        
        # Spinner canvas
        self.spinner_canvas = tk.Canvas(loading_frame, width=80, height=80, bg='white', highlightthickness=0)
        self.spinner_canvas.pack(pady=20)
        
        # Status label
        self.status_label = tk.Label(
            loading_frame,
            text="Initializing...",
            font=('Arial', 11),
            bg='white',
            fg='#34495e'
        )
        self.status_label.pack(pady=10)
        
        # Progress description
        self.progress_label = tk.Label(
            loading_frame,
            text="Please wait while data files are loaded into memory",
            font=('Arial', 9),
            bg='white',
            fg='#7f8c8d'
        )
        self.progress_label.pack(pady=(5, 30))
        
        # Start spinner animation
        self.spinner_angle = 0
        self.is_loading = True
        self._animate_spinner()
        
        return loading_frame
    
    def _animate_spinner(self):
        """Animate the loading spinner - runs independently of data loading"""
        if self.is_loading:
            try:
                self.spinner_canvas.delete("spinner")
                
                # Draw spinner arc
                self.spinner_canvas.create_arc(
                    10, 10, 70, 70,
                    start=self.spinner_angle,
                    extent=60,
                    outline='#3498db',
                    width=4,
                    style='arc',
                    tags="spinner"
                )
                
                # Update angle for animation
                self.spinner_angle = (self.spinner_angle + 12) % 360
                
            except tk.TclError:
                # Handle case where canvas is destroyed
                self.is_loading = False
                return
            
            # Schedule next frame at higher frequency for smoother animation
            self.root.after(30, self._animate_spinner)
    
    def _start_loading_process(self):
        """Start the data loading process with progress updates"""
        # Create data loading manager
        self.loading_manager = APIDataLoadingManager(
            self.data_manager, 
            progress_callback=self._update_loading_progress
        )
        
        # Start loading in separate thread
        loading_thread = threading.Thread(target=self._load_data_with_progress)
        loading_thread.daemon = True
        loading_thread.start()
        
        # Check loading status periodically
        self._check_loading_status()
    
    def _load_data_with_progress(self):
        """Load data in background thread"""
        self.loading_manager.load_data_async()
    
    def _update_loading_progress(self, status: str):
        """Update loading screen with current status"""
        # Schedule GUI update on main thread to avoid threading issues
        self.root.after(0, lambda: self._update_status_safe(status))
    
    def _update_status_safe(self, status: str):
        """Safely update status text from main thread"""
        if hasattr(self, 'status_label') and self.status_label.winfo_exists():
            self.status_label.config(text=status)
    
    def _check_loading_status(self):
        """Check if loading is complete and handle accordingly"""
        if self.loading_manager.loading_complete:
            if self.loading_manager.loading_successful:
                self._on_loading_complete()
            else:
                self._on_loading_error()
        else:
            # Check again more frequently for better responsiveness
            self.root.after(50, self._check_loading_status)
    
    def _on_loading_complete(self):
        """Handle successful data loading completion"""
        print("🎉 Loading complete - starting GUI setup...")
        
        # Stop spinner animation
        self.is_loading = False
        
        # Destroy loading frame
        self.loading_frame.destroy()
        
        # Force UI update to clear loading frame
        self.root.update()
        
        # Set up main GUI (creates the main_frame)
        print("🖼️ Setting up main GUI...")
        self._setup_gui()
        
        # Size window to screen dimensions (windowed, not fullscreen)
        print("📐 Setting screen size...")
        self._set_screen_size()
        
        # Create a temporary rendering overlay on the main frame
        self._show_rendering_overlay()
        
        # Force UI update to show the overlay
        self.root.update()
        
        # Draw initial map (this will take time)
        print("🗺️ Drawing initial map...")
        self._draw_initial_map()
        
        # Hide the rendering overlay
        self._hide_rendering_overlay()
        
        print("✅ Application setup complete!")
    
    def _show_rendering_overlay(self):
        """Show a rendering overlay on the main frame while drawing the map"""
        # Create overlay frame that covers the entire main frame
        self.rendering_overlay = tk.Frame(self.main_frame, bg='#2c3e50')
        self.rendering_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Add status message
        status_label = tk.Label(
            self.rendering_overlay,
            text="Drawing map features...",
            font=('Arial', 16, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        status_label.pack(expand=True, pady=(0, 20))
        
        # Add progress message
        progress_label = tk.Label(
            self.rendering_overlay,
            text="Rendering geographic features, please wait...",
            font=('Arial', 12),
            bg='#2c3e50',
            fg='#95a5a6'
        )
        progress_label.pack(expand=True)
        
        # Store reference for later updates
        self.rendering_status_label = status_label
    
    def _hide_rendering_overlay(self):
        """Hide the rendering overlay"""
        if hasattr(self, 'rendering_overlay') and self.rendering_overlay:
            self.rendering_overlay.destroy()
            self.rendering_overlay = None
            self.rendering_status_label = None
    
    def _set_screen_size(self):
        """Set window to screen size (windowed mode)"""
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Use 90% of screen size to leave room for taskbar/dock
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.9)
        
        # Center the window on screen
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Set the geometry
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Ensure window is in normal state (not maximized/minimized)
        self.root.state('normal')
    
    def _on_loading_error(self):
        """Handle data loading error"""
        # Stop spinner animation
        self.is_loading = False
        
        # Show error message
        messagebox.showerror(
            "Data Loading Error", 
            f"Failed to load geographic data:\n\n{self.loading_manager.error_message}\n\n"
            "Please ensure that states.geojson and counties.geojson files are "
            "present in the source_geometries/ directory."
        )
        
        # Exit application
        self.root.destroy()
    
    def _setup_gui(self):
        """Set up the main GUI layout"""
        # Main container
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(2, weight=1)  # Map frame gets the weight
        
        # Title
        title_label = ttk.Label(
            self.main_frame, 
            text="Austin Averill's Population By Region Viewer",
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Control panel at the top (more prominent)
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.grid(row=1, column=0, pady=(0, 10), sticky=(tk.W, tk.E))
        self.control_frame.columnconfigure(1, weight=1)  # Make instructions expand
        
        # Create Chloro button (initially disabled) - larger and more prominent
        self.create_chloro_btn = ttk.Button(
            self.control_frame,
            text="🗺️ Create Chloropleth Map",
            state='disabled',
            command=self._open_chloropleth_generator
        )
        self.create_chloro_btn.grid(row=0, column=0, padx=(0, 20), sticky=tk.W)
        
        # Style the button to make it more prominent
        style = ttk.Style()
        style.configure('Prominent.TButton', font=('Arial', 11, 'bold'))
        self.create_chloro_btn.configure(style='Prominent.TButton')
        
        # Instructions label (dynamic text based on selection)
        self.instructions = ttk.Label(
            self.control_frame,
            text="Click on a region in the map below to select it, then click the button to create a chloropleth map",
            font=('Arial', 10),
            foreground='#666666'
        )
        self.instructions.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Map container
        self.map_frame = ttk.LabelFrame(self.main_frame, text="Regional Map", padding="5")
        self.map_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self._setup_map()
    
    def _setup_map(self):
        """Set up the matplotlib map display"""
        # Create figure with subplots for main map, Alaska, and Hawaii
        self.figure = Figure(figsize=(12, 8), facecolor='white')
        
        # Main map (continental US)
        self.ax_main = self.figure.add_subplot(1, 1, 1)
        
        # Alaska and Hawaii insets (will be positioned later)
        # We'll create these as separate axes positioned within the main plot
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, self.map_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Bind click and motion events
        self.canvas.mpl_connect('button_press_event', self._on_map_click)
        self.canvas.mpl_connect('motion_notify_event', self._on_mouse_motion)
    
    def _load_data(self):
        """Load GeoJSON data (called after loading screen completes)"""
        # Data is already loaded by the loading manager
        # Just verify it's available
        if not self.data_manager.is_data_loaded():
            messagebox.showerror("Data Error", "Geographic data is not available")
            return
    
    def _draw_initial_map(self):
        """Draw the initial regional map"""
        print("🗺️ Starting to draw initial map...")
        
        if not self.data_manager.is_data_loaded():
            print("❌ Data manager reports data not loaded")
            return
        
        print(f"✅ Data is loaded: {len(self.data_manager.states_data['features'])} states available")
        
        # Clear the axes
        self.ax_main.clear()
        
        # Track regions for legend
        region_patches = {}
        states_drawn = 0
        states_skipped = 0
        total_states = len(self.data_manager.states_data['features'])
        
        # Plot states with regional coloring
        for i, feature in enumerate(self.data_manager.states_data['features']):
            # Update progress every 10 states
            if i % 10 == 0 and hasattr(self, 'rendering_status_label') and self.rendering_status_label:
                progress_pct = (i / total_states) * 100
                self.rendering_status_label.config(text=f"Drawing map features... {progress_pct:.0f}%")
                self.root.update()
            
            state_name = feature['properties']['NAME']
            region = self.data_manager.get_state_region(state_name)
            
            if not region:
                print(f"⚠️ No region found for state: {state_name}")
                states_skipped += 1
                continue
            
            # Skip non-contiguous states for main map
            if state_name in ['Alaska', 'Hawaii']:
                print(f"🏔️ Skipping non-contiguous state: {state_name}")
                states_skipped += 1
                continue
            
            # Handle different geometry types
            geometry = feature['geometry']
            geom_type = geometry['type']
            
            if geom_type == 'Polygon':
                # Single polygon - draw it
                coords = geometry['coordinates'][0]  # Exterior ring
                coords_array = np.array(coords)
                
                polygon = Polygon(
                    coords_array, 
                    facecolor=self.data_manager.get_region_color(region),
                    edgecolor='white',
                    linewidth=1.5,
                    alpha=0.8
                )
                self.ax_main.add_patch(polygon)
                states_drawn += 1
                print(f"✅ Drew polygon for {state_name} in {region}")
                
            elif geom_type == 'MultiPolygon':
                # Multiple polygons - draw all of them
                polygons_added = 0
                for polygon_coords in geometry['coordinates']:
                    coords = polygon_coords[0]  # Exterior ring of each polygon
                    coords_array = np.array(coords)
                    
                    # Skip very small islands (less than 5 points) for visual clarity
                    if len(coords_array) < 5:
                        continue
                    
                    polygon = Polygon(
                        coords_array, 
                        facecolor=self.data_manager.get_region_color(region),
                        edgecolor='white',
                        linewidth=1.5,
                        alpha=0.8
                    )
                    self.ax_main.add_patch(polygon)
                    polygons_added += 1
                    
                states_drawn += 1
                print(f"✅ Drew {polygons_added} polygons for {state_name} in {region}")
            else:
                print(f"⚠️ Unknown geometry type '{geom_type}' for {state_name}")
            
            # Add to legend tracking
            if region not in region_patches:
                region_patches[region] = mpatches.Patch(
                    color=self.data_manager.get_region_color(region),
                    label=region
                )
            
            # Add state abbreviation label at centroid of the largest polygon
            # Skip territories (not states in our dataset)
            if state_name in ['Puerto Rico', 'U.S. Virgin Islands']:
                continue
                
            centroid = self._get_state_centroid(feature)
            if centroid:
                state_abbr = feature['properties'].get('STATE_ABBR', feature['properties'].get('STUSPS', state_name[:2].upper()))
                
                # Check if this is a crowded Northeast state that needs a callout
                if self._needs_callout_label(state_name):
                    self._add_callout_label(state_name, state_abbr, centroid, region)
                else:
                    # Regular centered label
                    self.ax_main.text(
                        centroid[0], centroid[1], state_abbr,
                        ha='center', va='center',
                        fontsize=8, fontweight='bold',
                        color='black',
                        bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7, edgecolor='none')
                    )
        
        # Set map extent for continental US
        self.ax_main.set_xlim(-130, -65)
        self.ax_main.set_ylim(20, 50)
        self.ax_main.set_aspect('equal')
        self.ax_main.axis('off')
        
        # Add legend (moved to right side to avoid Alaska/Hawaii insets)
        if region_patches:
            self.ax_main.legend(
                handles=list(region_patches.values()),
                loc='center left',
                bbox_to_anchor=(1.02, 0.5)
            )
        
        # Add title
        self.ax_main.set_title("United States by Region", fontsize=14, fontweight='bold', pad=20)
        
        # Add Alaska and Hawaii insets
        self._add_alaska_hawaii_insets()
        
        # Add north arrow and scale bar
        self._add_map_elements()
        
        # Debug summary
        print(f"🎯 Map drawing summary: {states_drawn} states drawn, {states_skipped} states skipped")
        print(f"📊 Regions found: {list(region_patches.keys())}")
        
        self.canvas.draw()
        print("🖼️ Canvas draw complete!")
    
    def _add_alaska_hawaii_insets(self):
        """Add Alaska and Hawaii as inset maps"""
        # Create inset axes for Alaska (zoomed out a bit more to fit completely)
        self.ax_alaska = self.figure.add_axes([0.02, 0.02, 0.25, 0.25])
        
        # Create inset axes for Hawaii  
        self.ax_hawaii = self.figure.add_axes([0.3, 0.02, 0.15, 0.15])
        
        # Draw Alaska with wider bounds to fit completely
        self._draw_state_inset(self.ax_alaska, 'Alaska', [-190, -125], [50, 73])
        
        # Draw Hawaii
        self._draw_state_inset(self.ax_hawaii, 'Hawaii', [-162, -154], [18, 23])
    
    def _draw_state_inset(self, ax, state_name: str, xlim: List[float], ylim: List[float]):
        """Draw a state in an inset axis"""
        ax.clear()
        
        for feature in self.data_manager.states_data['features']:
            if feature['properties']['NAME'] == state_name:
                region = self.data_manager.get_state_region(state_name)
                
                # Handle different geometry types
                geometry = feature['geometry']
                geom_type = geometry['type']
                
                if geom_type == 'Polygon':
                    coords = geometry['coordinates'][0]  # Exterior ring
                    coords_array = np.array(coords)
                    
                    polygon = Polygon(
                        coords_array,
                        facecolor=self.data_manager.get_region_color(region),
                        edgecolor='white',
                        linewidth=1,
                        alpha=0.8
                    )
                    ax.add_patch(polygon)
                    
                elif geom_type == 'MultiPolygon':
                    # Handle multiple islands/polygons (important for Hawaii and Alaska)
                    for polygon_coords in geometry['coordinates']:
                        coords = polygon_coords[0]  # Exterior ring
                        coords_array = np.array(coords)
                        
                        # Skip very small islands for visual clarity
                        if len(coords_array) < 5:
                            continue
                        
                        polygon = Polygon(
                            coords_array,
                            facecolor=self.data_manager.get_region_color(region),
                            edgecolor='white',
                            linewidth=1,
                            alpha=0.8
                        )
                        ax.add_patch(polygon)
                
                # Add state abbreviation at centroid of largest polygon
                centroid = self._get_state_centroid(feature)
                if centroid:
                    state_abbr = feature['properties'].get('STATE_ABBR', feature['properties'].get('STUSPS', state_name[:2].upper()))
                    ax.text(
                        centroid[0], centroid[1], state_abbr,
                        ha='center', va='center',
                        fontsize=8, fontweight='bold',
                        color='black',
                        bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor='none')
                    )
                break
        
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.set_aspect('equal')
        ax.set_title(state_name, fontsize=10)
        
        # Remove tick marks and labels for cleaner appearance
        ax.set_xticks([])
        ax.set_yticks([])
        
        # Add border
        for spine in ax.spines.values():
            spine.set_edgecolor('black')
            spine.set_linewidth(1)
    
    def _add_map_elements(self):
        """Add north arrow and scale bar to the map"""
        # North arrow (moved higher to avoid overlapping features)
        self.ax_main.annotate(
            'N', xy=(0.95, 0.98), xycoords='axes fraction',
            ha='center', va='center', fontsize=16, fontweight='bold'
        )
        
        # Add arrow
        self.ax_main.annotate(
            '', xy=(0.95, 0.96), xytext=(0.95, 0.92),
            xycoords='axes fraction', textcoords='axes fraction',
            arrowprops=dict(arrowstyle='->', lw=2, color='black')
        )
        
        # Simple scale bar (approximate)
        self.ax_main.text(
            0.95, 0.05, '500 miles',
            transform=self.ax_main.transAxes,
            ha='right', va='bottom',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8)
        )
    
    def _calculate_polygon_centroid(self, coords: np.ndarray) -> Optional[Tuple[float, float]]:
        """Calculate a better centroid of a polygon using area-weighted method"""
        try:
            if len(coords) < 3:
                return None
            
            # Calculate area-weighted centroid (more accurate for irregular shapes)
            x = coords[:, 0]
            y = coords[:, 1]
            
            # Close the polygon if not already closed
            if not (x[0] == x[-1] and y[0] == y[-1]):
                x = np.append(x, x[0])
                y = np.append(y, y[0])
            
            # Calculate area and centroid using the shoelace formula
            area = 0.0
            cx = 0.0
            cy = 0.0
            
            for i in range(len(x) - 1):
                cross = x[i] * y[i + 1] - x[i + 1] * y[i]
                area += cross
                cx += (x[i] + x[i + 1]) * cross
                cy += (y[i] + y[i + 1]) * cross
            
            area = area / 2.0
            if abs(area) < 1e-10:  # Avoid division by zero
                # Fallback to simple mean if area calculation fails
                return (np.mean(coords[:, 0]), np.mean(coords[:, 1]))
            
            cx = cx / (6.0 * area)
            cy = cy / (6.0 * area)
            
            return (cx, cy)
        except:
            # Fallback to simple mean if calculation fails
            try:
                return (np.mean(coords[:, 0]), np.mean(coords[:, 1]))
            except:
                return None
    
    def _get_state_centroid(self, feature) -> Optional[Tuple[float, float]]:
        """Get the centroid of the largest polygon for a state (for label placement)"""
        geometry = feature['geometry']
        geom_type = geometry['type']
        
        if geom_type == 'Polygon':
            coords = np.array(geometry['coordinates'][0])
            return self._calculate_polygon_centroid(coords)
            
        elif geom_type == 'MultiPolygon':
            # Find the largest polygon by area (more accurate than just point count)
            largest_polygon = None
            max_area = 0
            
            for polygon_coords in geometry['coordinates']:
                coords = np.array(polygon_coords[0])  # Exterior ring
                if len(coords) < 3:
                    continue
                    
                # Calculate approximate area using shoelace formula
                x = coords[:, 0]
                y = coords[:, 1]
                area = 0.5 * abs(sum(x[i] * y[i + 1] - x[i + 1] * y[i] for i in range(-1, len(x) - 1)))
                
                if area > max_area:
                    max_area = area
                    largest_polygon = coords
            
            if largest_polygon is not None:
                return self._calculate_polygon_centroid(largest_polygon)
        
        return None
    
    def _needs_callout_label(self, state_name: str) -> bool:
        """Check if a state needs a callout label due to crowded positioning"""
        # Northeast states that are small and crowded
        crowded_states = {
            'Connecticut', 'Rhode Island', 'Massachusetts', 
            'Vermont', 'New Hampshire', 'Delaware', 'Maryland', 'New Jersey'
        }
        return state_name in crowded_states
    
    def _add_callout_label(self, state_name: str, state_abbr: str, centroid: Tuple[float, float], region: str):
        """Add a callout label for crowded Northeast states"""
        # Define callout positions for crowded states (slightly longer lines for better readability)
        callout_positions = {
            'Connecticut': (-67, 42),
            'Rhode Island': (-66, 43),
            'Massachusetts': (-65, 44), 
            'Vermont': (-68, 45),
            'New Hampshire': (-67, 46),
            'Delaware': (-71, 40),
            'Maryland': (-72, 39),
            'New Jersey': (-70, 41)
        }
        
        if state_name in callout_positions:
            # Get the callout position
            callout_x, callout_y = callout_positions[state_name]
            
            # Draw the callout label
            self.ax_main.text(
                callout_x, callout_y, state_abbr,
                ha='center', va='center',
                fontsize=8, fontweight='bold',
                color='black',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9, edgecolor='gray')
            )
            
            # Draw the callout line
            self.ax_main.annotate(
                '', xy=centroid, xytext=(callout_x, callout_y),
                arrowprops=dict(arrowstyle='-', color='gray', alpha=0.7, linewidth=1)
            )
        else:
            # Fallback to regular label if not in callout list
            self.ax_main.text(
                centroid[0], centroid[1], state_abbr,
                ha='center', va='center',
                fontsize=8, fontweight='bold',
                color='black',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7, edgecolor='none')
            )
    
    def _on_map_click(self, event):
        """Handle clicks on the map to select regions"""
        if event.inaxes != self.ax_main:
            return
        
        if event.xdata is None or event.ydata is None:
            return
        
        # Find which region was clicked
        clicked_region = self._find_clicked_region(event.xdata, event.ydata)
        
        if clicked_region:
            self.selected_region = clicked_region
            self.create_chloro_btn.config(state='normal')
            
            # Update the instruction text dynamically
            self._update_instruction_text(clicked_region)
            
            # Add visual highlight to the selected region
            self._highlight_selected_region(clicked_region)
    
    def _on_mouse_motion(self, event):
        """Handle mouse motion to provide visual feedback (throttled for performance)"""
        import time
        
        # Throttle mouse motion events - only process every 100ms
        current_time = time.time()
        if current_time - self.last_motion_time < 0.1:
            return
        self.last_motion_time = current_time
        
        if event.inaxes != self.ax_main:
            # Reset cursor when outside main axis
            if self.last_hovered_region is not None:
                self.canvas.get_tk_widget().config(cursor="")
                self.last_hovered_region = None
                if not self.selected_region:
                    self.instructions.config(
                        text="Click on a region in the map below to select it, then click the button to create a chloropleth map",
                        foreground='#666666'
                    )
            return
        
        if event.xdata is None or event.ydata is None:
            if self.last_hovered_region is not None:
                self.canvas.get_tk_widget().config(cursor="")
                self.last_hovered_region = None
                if not self.selected_region:
                    self.instructions.config(
                        text="Click on a region in the map below to select it, then click the button to create a chloropleth map",
                        foreground='#666666'
                    )
            return
        
        # Check if mouse is over a clickable region
        hovered_region = self._find_clicked_region(event.xdata, event.ydata)
        
        # Only update if the hovered region has changed
        if hovered_region != self.last_hovered_region:
            self.last_hovered_region = hovered_region
            
            if hovered_region:
                # Change cursor to indicate clickable area
                self.canvas.get_tk_widget().config(cursor="hand2")
                
                # Update instruction text to show what would be selected
                if not self.selected_region:  # Only update if no region is selected
                    self.instructions.config(
                        text=f"Click to select: {hovered_region}",
                        foreground='#1976D2'  # Blue color for hover state
                    )
            else:
                # Reset cursor and text when not over a clickable area
                self.canvas.get_tk_widget().config(cursor="")
                if not self.selected_region:  # Only reset if no region is selected
                    self.instructions.config(
                        text="Click on a region in the map below to select it, then click the button to create a chloropleth map",
                        foreground='#666666'
                    )
    
    def _update_instruction_text(self, region_name: str):
        """Update the instruction text to reflect the selected region"""
        self.instructions.config(
            text=f"✓ Selected region: {region_name} - Click 'Create Chloropleth Map' to visualize county-level data",
            foreground='#2E7D32'  # Green color to indicate success
        )
    
    def _highlight_selected_region(self, region_name: str):
        """Add a visual highlight around the selected region"""
        # Clear any existing highlights
        self._clear_region_highlights()
        
        # Draw highlight border around all states in the selected region
        states_in_region = self.data_manager.get_states_in_region(region_name)
        
        # Highlight color - blue
        highlight_color = '#2E86DE'  # Blue color for highlights
        
        for feature in self.data_manager.states_data['features']:
            state_name = feature['properties']['NAME']
            
            # Skip Alaska and Hawaii for main map (they'll be highlighted in insets)
            if state_name in ['Alaska', 'Hawaii']:
                continue
                
            if state_name in states_in_region:
                # Draw highlight border
                geometry = feature['geometry']
                geom_type = geometry['type']
                
                if geom_type == 'Polygon':
                    coords = geometry['coordinates'][0]
                    coords_array = np.array(coords)
                    
                    # Draw thick border for highlight
                    self.ax_main.plot(
                        coords_array[:, 0], coords_array[:, 1], 
                        color=highlight_color, linewidth=4, alpha=0.8, 
                        zorder=10, label='_highlight_'
                    )
                    
                elif geom_type == 'MultiPolygon':
                    for polygon_coords in geometry['coordinates']:
                        coords = polygon_coords[0]
                        coords_array = np.array(coords)
                        
                        if len(coords_array) >= 5:  # Skip very small islands
                            self.ax_main.plot(
                                coords_array[:, 0], coords_array[:, 1], 
                                color=highlight_color, linewidth=4, alpha=0.8, 
                                zorder=10, label='_highlight_'
                            )
        
        # Highlight Alaska and Hawaii insets if they're in the selected region
        if 'Alaska' in states_in_region or 'Hawaii' in states_in_region:
            self._highlight_insets(states_in_region, highlight_color)
        
        # Refresh the canvas
        self.canvas.draw()
    
    def _highlight_insets(self, states_in_region: set, highlight_color: str):
        """Highlight Alaska and/or Hawaii insets if they're in the selected region"""
        for feature in self.data_manager.states_data['features']:
            state_name = feature['properties']['NAME']
            
            if state_name not in states_in_region:
                continue
            
            # Determine which inset to highlight
            if state_name == 'Alaska' and hasattr(self, 'ax_alaska'):
                target_ax = self.ax_alaska
            elif state_name == 'Hawaii' and hasattr(self, 'ax_hawaii'):
                target_ax = self.ax_hawaii
            else:
                continue
            
            # Draw highlight border on the inset
            geometry = feature['geometry']
            geom_type = geometry['type']
            
            if geom_type == 'Polygon':
                coords = geometry['coordinates'][0]
                coords_array = np.array(coords)
                
                target_ax.plot(
                    coords_array[:, 0], coords_array[:, 1], 
                    color=highlight_color, linewidth=3, alpha=0.8, 
                    zorder=10, label='_highlight_'
                )
                
            elif geom_type == 'MultiPolygon':
                for polygon_coords in geometry['coordinates']:
                    coords = polygon_coords[0]
                    coords_array = np.array(coords)
                    
                    if len(coords_array) >= 5:
                        target_ax.plot(
                            coords_array[:, 0], coords_array[:, 1], 
                            color=highlight_color, linewidth=3, alpha=0.8, 
                            zorder=10, label='_highlight_'
                        )
    
    def _clear_region_highlights(self):
        """Clear any existing region highlights from main map and insets"""
        # Clear highlights from main map
        lines_to_remove = []
        for line in self.ax_main.lines:
            if hasattr(line, '_label') and line._label == '_highlight_':
                lines_to_remove.append(line)
        
        for line in lines_to_remove:
            line.remove()
        
        # Clear highlights from Alaska inset
        if hasattr(self, 'ax_alaska'):
            lines_to_remove = []
            for line in self.ax_alaska.lines:
                if hasattr(line, '_label') and line._label == '_highlight_':
                    lines_to_remove.append(line)
            
            for line in lines_to_remove:
                line.remove()
        
        # Clear highlights from Hawaii inset
        if hasattr(self, 'ax_hawaii'):
            lines_to_remove = []
            for line in self.ax_hawaii.lines:
                if hasattr(line, '_label') and line._label == '_highlight_':
                    lines_to_remove.append(line)
            
            for line in lines_to_remove:
                line.remove()
    
    def _find_clicked_region(self, x: float, y: float) -> Optional[str]:
        """Find which region contains the clicked point using proper point-in-polygon testing"""
        
        # Check each state to see if the click point is inside it
        for feature in self.data_manager.states_data['features']:
            state_name = feature['properties']['NAME']
            
            # Skip non-contiguous states for main map
            if state_name in ['Alaska', 'Hawaii']:
                continue
                
            region = self.data_manager.get_state_region(state_name)
            if not region:
                continue
            
            # Check if point is inside this state's geometry
            if self._point_in_state(x, y, feature):
                return region
        
        return None
    
    def _point_in_state(self, x: float, y: float, feature) -> bool:
        """Check if a point is inside a state's geometry using ray casting algorithm (optimized)"""
        geometry = feature['geometry']
        geom_type = geometry['type']
        
        if geom_type == 'Polygon':
            return self._point_in_polygon(x, y, np.array(geometry['coordinates'][0]))
            
        elif geom_type == 'MultiPolygon':
            # Check if point is in any of the polygons (limit to major polygons for performance)
            for i, polygon_coords in enumerate(geometry['coordinates']):
                coords = np.array(polygon_coords[0])  # Exterior ring
                # Skip very small islands for hover detection (performance optimization)
                if len(coords) >= 100:  # Only check substantial polygons
                    if self._point_in_polygon(x, y, coords):
                        return True
        
        return False
    
    def _point_in_polygon(self, x: float, y: float, polygon_coords: np.ndarray) -> bool:
        """Ray casting algorithm to determine if point is inside polygon (with bounding box optimization)"""
        if len(polygon_coords) < 3:
            return False
        
        # Quick bounding box check first (much faster than full polygon test)
        min_x, min_y = polygon_coords[:, 0].min(), polygon_coords[:, 1].min()
        max_x, max_y = polygon_coords[:, 0].max(), polygon_coords[:, 1].max()
        
        if x < min_x or x > max_x or y < min_y or y > max_y:
            return False
        
        # Now do the full ray casting algorithm
        n = len(polygon_coords)
        inside = False
        
        p1x, p1y = polygon_coords[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon_coords[i % n]
            
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside
    
    def _open_chloropleth_generator(self):
        """Open the chloropleth generator for the selected region"""
        if not self.selected_region:
            return
        
        # Show loading indicator
        self.create_chloro_btn.config(state='disabled', text='Loading counties...')
        self.instructions.config(
            text=f"Loading county data for {self.selected_region} region, please wait...",
            foreground='#FF6B35'  # Orange for loading
        )
        self.root.update()  # Force UI update
        
        # Load counties for the selected region in a thread
        # The data manager will cache counties by region automatically
        import threading
        def load_and_open():
            success = self.data_manager.load_counties_for_region(
                self.selected_region,
                progress_callback=self._update_county_loading_progress
            )
            
            # Schedule GUI update on main thread
            self.root.after(0, lambda: self._on_counties_loaded(success))
        
        loading_thread = threading.Thread(target=load_and_open)
        loading_thread.daemon = True
        loading_thread.start()
    
    def _update_county_loading_progress(self, status: str):
        """Update UI with county loading progress"""
        self.root.after(0, lambda: self.instructions.config(text=status))
    
    def _on_counties_loaded(self, success: bool):
        """Handle completion of county data loading"""
        if success:
            self._launch_chloropleth_generator()
        else:
            # Show error message
            self.create_chloro_btn.config(state='normal', text='🗺️ Create Chloropleth Map')
            self.instructions.config(
                text=f"❌ Failed to load county data for {self.selected_region}. Please try again.",
                foreground='#D32F2F'  # Red for error
            )
    
    def _launch_chloropleth_generator(self):
        """Launch the chloropleth generator window"""
        # Reset button text
        self.create_chloro_btn.config(text='🗺️ Create Chloropleth Map')
        
        # Hide main window
        self.root.withdraw()
        
        # Create chloropleth generator window
        self.chloropleth_generator = ChloroplethGenerator(
            parent=self.root,
            region=self.selected_region,
            data_manager=self.data_manager,
            return_callback=self._return_to_main
        )
    
    def _return_to_main(self):
        """Return to the main window from chloropleth generator"""
        self.root.deiconify()
        self.selected_region = None
        self.create_chloro_btn.config(state='disabled')
        
        # Reset instruction text
        self.instructions.config(
            text="Click on a region in the map below to select it, then click the button to create a chloropleth map",
            foreground='#666666'
        )
        
        # Clear any highlights
        self._clear_region_highlights()
        self.canvas.draw()
        
        if self.chloropleth_generator:
            self.chloropleth_generator.destroy()
            self.chloropleth_generator = None
    
    def run(self):
        """Start the application"""
        self.root.mainloop()
    
    def destroy(self):
        """Clean up and destroy the application"""
        if self.chloropleth_generator:
            self.chloropleth_generator.destroy()
        self.root.destroy()