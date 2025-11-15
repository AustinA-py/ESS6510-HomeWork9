"""
Chloropleth Generator Window

This module contains the chloropleth generator interface that appears
after a user selects a region and clicks "Create Chloro".
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.patches import Polygon
import numpy as np
from typing import Optional, Dict, List, Callable
import webbrowser
import tempfile
import os

class ChloroplethGenerator:
    """Chloropleth map generator window"""
    
    def __init__(self, parent, region: str, data_manager, return_callback: Callable):
        """
        Initialize the chloropleth generator
        
        Args:
            parent: Parent window
            region: Selected region name
            data_manager: Data manager instance
            return_callback: Function to call when returning to main window
        """
        self.parent = parent
        self.region = region
        self.data_manager = data_manager
        self.return_callback = return_callback
        
        # Create new window
        self.window = tk.Toplevel(parent)
        self.window.title(f"Chloropleth Generator - {region} Region")
        self.window.geometry("1400x900")
        self.window.configure(bg='white')
        
        # Variables
        self.classification_method = tk.StringVar(value="Quantile")
        self.color_scheme = tk.StringVar(value="Reds")
        self.current_map = None
        self.counties_data = []  # Store county data for classification
        self.county_patches = []  # Store polygon patches for re-coloring
        
        # Tooltip variables
        self.hover_tooltip = None  # The tooltip annotation
        self.hover_timer = None  # Timer for 1-second delay
        self.last_hover_time = 0
        self.current_hover_county = None
        
        # GUI components
        self.main_frame = None
        self.control_frame = None
        self.map_frame = None
        self.figure = None
        self.canvas = None
        self.ax = None
        
        self._setup_gui()
        
        # Create loading overlay
        self._create_loading_overlay()
        
        # Load data with progress
        self.window.after(100, self._load_region_data_with_progress)
        
        # Handle window closing
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _create_loading_overlay(self):
        """Create a loading overlay that shows while drawing counties"""
        # This will be created when needed - no need to create it now
        self.loading_overlay = None
        self.loading_label = None
        self.loading_progress = None
    
    def _show_loading(self, message="Loading...", progress=""):
        """Show the full-screen loading overlay"""
        # Create overlay if it doesn't exist
        if self.loading_overlay is None:
            self.loading_overlay = tk.Frame(self.window, bg='#2c3e50')
            self.loading_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
            
            # Loading label
            self.loading_label = tk.Label(
                self.loading_overlay,
                text=message,
                font=('Arial', 16, 'bold'),
                bg='#2c3e50',
                fg='white'
            )
            self.loading_label.pack(expand=True, pady=(0, 20))
            
            # Progress label
            self.loading_progress = tk.Label(
                self.loading_overlay,
                text=progress,
                font=('Arial', 12),
                bg='#2c3e50',
                fg='#95a5a6'
            )
            self.loading_progress.pack(expand=True)
        else:
            # Update existing overlay
            self.loading_label.config(text=message)
            self.loading_progress.config(text=progress)
            self.loading_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        self.window.update()
    
    def _hide_loading(self):
        """Hide the loading overlay"""
        if self.loading_overlay:
            self.loading_overlay.place_forget()
            self.window.update()
    
    def _load_region_data_with_progress(self):
        """Load and display county data with progress indication"""
        self._show_loading("Loading counties...", "Retrieving county data...")
        self._load_region_data()
    
    def _setup_gui(self):
        """Set up the chloropleth generator GUI"""
        # Main container
        self.main_frame = ttk.Frame(self.window, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(
            self.main_frame, 
            text=f"Population Chloropleth - {self.region} Region",
            font=('Arial', 14, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Control panel
        self._setup_controls()
        
        # Map panel
        self._setup_map_panel()
    
    def _setup_controls(self):
        """Set up the control panel"""
        self.control_frame = ttk.LabelFrame(self.main_frame, text="Controls", padding="10")
        self.control_frame.grid(row=1, column=0, sticky=(tk.W, tk.N, tk.S), padx=(0, 10))
        
        # Classification method dropdown
        ttk.Label(self.control_frame, text="Classification Method:").pack(anchor=tk.W, pady=(0, 5))
        
        classification_combo = ttk.Combobox(
            self.control_frame, 
            textvariable=self.classification_method,
            values=["Quantile", "Natural Breaks (Jenks)", "Equal Interval"],
            state="readonly",
            width=25
        )
        classification_combo.pack(anchor=tk.W, pady=(0, 15))
        
        # Color scheme visual selector
        color_scheme_label = ttk.Label(self.control_frame, text="Color Scheme:")
        color_scheme_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Create tooltip label that always reserves space (to prevent layout shifting)
        # Use white background to blend with ttk.LabelFrame
        self.tooltip_label = tk.Label(
            self.control_frame,
            text="",  # Empty initially
            bg='white',  # White background to blend with ttk frame
            fg='#2c3e50',  # Dark text color for visibility
            relief=tk.FLAT,
            borderwidth=0,
            font=('Arial', 9, 'italic'),  # Italic to distinguish from labels
            padx=5,
            pady=2,
            height=1  # Reserve space for one line of text
        )
        # Pack it now so it always reserves space
        self.tooltip_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Create a frame for color ramp buttons
        self.color_ramp_frame = tk.Frame(self.control_frame, bg='white')
        self.color_ramp_frame.pack(anchor=tk.W, pady=(0, 15), fill=tk.X)
        
        # Define color schemes with their matplotlib names
        self.color_schemes = {
            "Reds": ["#fee5d9", "#fcae91", "#fb6a4a", "#de2d26", "#a50f15"],
            "Blues": ["#eff3ff", "#bdd7e7", "#6baed6", "#3182bd", "#08519c"],
            "Greens": ["#edf8e9", "#bae4b3", "#74c476", "#31a354", "#006d2c"],
            "Oranges": ["#feedde", "#fdbe85", "#fd8d3c", "#e6550d", "#a63603"],
            "Purples": ["#f2f0f7", "#cbc9e2", "#9e9ac8", "#756bb1", "#54278f"],
            "YlOrRd": ["#ffffb2", "#fecc5c", "#fd8d3c", "#f03b20", "#bd0026"],
            "RdYlBu": ["#d7191c", "#fdae61", "#ffffbf", "#abd9e9", "#2c7bb6"]
        }
        
        # Create color ramp buttons
        self.color_buttons = {}
        for scheme_name, colors in self.color_schemes.items():
            btn_frame = tk.Frame(self.color_ramp_frame, bg='white')
            btn_frame.pack(fill=tk.X, pady=2)
            
            # Create a canvas to draw the color ramp
            canvas = tk.Canvas(btn_frame, width=200, height=20, highlightthickness=0)
            canvas.pack(side=tk.LEFT, padx=(0, 5))
            
            # Draw the 5 color blocks
            block_width = 40
            for i, color in enumerate(colors):
                canvas.create_rectangle(
                    i * block_width, 0,
                    (i + 1) * block_width, 20,
                    fill=color,
                    outline='black',
                    width=1
                )
            
            # Store reference
            self.color_buttons[scheme_name] = canvas
            
            # Make canvas clickable
            canvas.bind("<Button-1>", lambda e, s=scheme_name: self._select_color_scheme(s))
            canvas.bind("<Enter>", lambda e, s=scheme_name: self._show_tooltip(s))
            canvas.bind("<Leave>", lambda e: self._hide_tooltip())
            
            # Highlight if this is the current selection
            if scheme_name == self.color_scheme.get():
                canvas.config(highlightthickness=2, highlightbackground='#2E86DE')
        
        # Apply button
        apply_btn = ttk.Button(
            self.control_frame,
            text="Apply Chloropleth",
            command=self._apply_chloropleth
        )
        apply_btn.pack(pady=(10, 0), fill=tk.X)
        
        # Export button
        export_btn = ttk.Button(
            self.control_frame,
            text="Export to HTML",
            command=self._export_to_html
        )
        export_btn.pack(pady=(10, 0), fill=tk.X)
        
        # Return button
        return_btn = ttk.Button(
            self.control_frame,
            text="Return to Main",
            command=self._on_closing
        )
        return_btn.pack(pady=(20, 0), fill=tk.X)
        
        # Instructions
        instructions = tk.Text(
            self.control_frame,
            height=8,
            width=30,
            wrap=tk.WORD,
            font=('Arial', 9),
            state=tk.DISABLED
        )
        instructions.pack(pady=(20, 0), fill=tk.BOTH, expand=True)
        
        instructions.config(state=tk.NORMAL)
        instructions.insert(tk.END, 
            "Instructions:\n\n"
            "1. Select a classification method\n"
            "2. Click a color scheme\n"
            "3. Click 'Apply Chloropleth'\n"
            "4. Hover over counties for population info\n"
            "5. Use mouse wheel to zoom\n"
            "6. Export to HTML when ready"
        )
        instructions.config(state=tk.DISABLED)
    
    def _select_color_scheme(self, scheme_name: str):
        """Handle color scheme selection"""
        # Update the selected color scheme
        self.color_scheme.set(scheme_name)
        
        # Update visual highlighting
        for name, canvas in self.color_buttons.items():
            if name == scheme_name:
                canvas.config(highlightthickness=2, highlightbackground='#2E86DE')
            else:
                canvas.config(highlightthickness=0)
    
    def _show_tooltip(self, scheme_name: str):
        """Show tooltip with color scheme name (text only, no background box)"""
        self.tooltip_label.config(text=scheme_name)
    
    def _hide_tooltip(self):
        """Hide the tooltip by clearing text"""
        self.tooltip_label.config(text="")
    
    def _setup_map_panel(self):
        """Set up the map display panel"""
        self.map_frame = ttk.LabelFrame(self.main_frame, text=f"{self.region} Region Counties", padding="5")
        self.map_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create matplotlib figure with insets for West region
        self.figure = Figure(figsize=(10, 8), facecolor='white')
        
        # Check if this is the West region and create insets
        if self.region == "West":
            # Main plot for contiguous states - shifted up to make room for insets
            self.ax = self.figure.add_subplot(1, 1, 1, position=[0.05, 0.35, 0.9, 0.6])
            
            # Alaska inset (bottom right-left position) - right justified along bottom
            # Position: 35% width, 25% height, positioned at bottom right
            self.ax_alaska = self.figure.add_axes([0.30, 0.05, 0.35, 0.25])
            self.ax_alaska.set_title('Alaska', fontsize=10, fontweight='bold')
            # Set coordinate limits to match main application
            self.ax_alaska.set_xlim([-190, -125])
            self.ax_alaska.set_ylim([50, 73])
            self.ax_alaska.set_aspect('equal')
            # Remove tick marks and labels for cleaner appearance
            self.ax_alaska.set_xticks([])
            self.ax_alaska.set_yticks([])
            
            # Hawaii inset (bottom far right) - right justified along bottom
            # Position: 25% width, 25% height, positioned at far bottom right
            self.ax_hawaii = self.figure.add_axes([0.70, 0.05, 0.25, 0.25])
            self.ax_hawaii.set_title('Hawaii', fontsize=10, fontweight='bold')
            # Set coordinate limits to match main application
            self.ax_hawaii.set_xlim([-162, -154])
            self.ax_hawaii.set_ylim([18, 23])
            self.ax_hawaii.set_aspect('equal')
            # Remove tick marks and labels for cleaner appearance
            self.ax_hawaii.set_xticks([])
            self.ax_hawaii.set_yticks([])
            
            # Add bounding boxes to insets
            for ax in [self.ax_alaska, self.ax_hawaii]:
                ax.spines['top'].set_visible(True)
                ax.spines['right'].set_visible(True)
                ax.spines['bottom'].set_visible(True)
                ax.spines['left'].set_visible(True)
                ax.spines['top'].set_linewidth(2)
                ax.spines['right'].set_linewidth(2)
                ax.spines['bottom'].set_linewidth(2)
                ax.spines['left'].set_linewidth(2)
        else:
            # Single plot for other regions
            self.ax = self.figure.add_subplot(1, 1, 1)
            self.ax_alaska = None
            self.ax_hawaii = None
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, self.map_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Bind hover events for tooltips
        self.canvas.mpl_connect('motion_notify_event', self._on_hover)
    
    def _load_region_data(self):
        """Load and display county data for the selected region"""
        counties = self.data_manager.get_counties_in_region(self.region)
        
        if not counties:
            messagebox.showwarning("No Data", f"No county data found for {self.region} region")
            return
        
        self._draw_initial_counties(counties)
    
    def _draw_initial_counties(self, counties: List[Dict]):
        """Draw counties with black outline and no fill"""
        self._show_loading("Drawing counties...", f"Rendering {len(counties)} counties...")
        
        self.ax.clear()
        if self.ax_alaska:
            self.ax_alaska.clear()
            self.ax_alaska.set_title('Alaska', fontsize=10, fontweight='bold')
            # Set coordinate limits to match main application
            self.ax_alaska.set_xlim([-190, -125])
            self.ax_alaska.set_ylim([50, 73])
            self.ax_alaska.set_aspect('equal')
            # Remove tick marks and labels for cleaner appearance
            self.ax_alaska.set_xticks([])
            self.ax_alaska.set_yticks([])
            # Add bounding box
            for spine in self.ax_alaska.spines.values():
                spine.set_visible(True)
                spine.set_linewidth(2)
        if self.ax_hawaii:
            self.ax_hawaii.clear()
            self.ax_hawaii.set_title('Hawaii', fontsize=10, fontweight='bold')
            # Set coordinate limits to match main application
            self.ax_hawaii.set_xlim([-162, -154])
            self.ax_hawaii.set_ylim([18, 23])
            self.ax_hawaii.set_aspect('equal')
            # Remove tick marks and labels for cleaner appearance
            self.ax_hawaii.set_xticks([])
            self.ax_hawaii.set_yticks([])
            # Add bounding box
            for spine in self.ax_hawaii.spines.values():
                spine.set_visible(True)
                spine.set_linewidth(2)
        
        self.counties_data = []  # Reset county data
        self.county_patches = []  # Reset patches
        
        # Get STATE FIPS codes for Alaska (02) and Hawaii (15)
        alaska_fips = '02'
        hawaii_fips = '15'
        
        total_counties = len(counties)
        for i, county in enumerate(counties):
            # Update progress every 50 counties
            if i % 50 == 0:
                progress_pct = (i / total_counties) * 100
                self._show_loading(
                    "Drawing counties...", 
                    f"Rendering county {i+1}/{total_counties} ({progress_pct:.0f}%)"
                )
            
            # Get county properties
            if 'properties' in county:
                name = county['properties'].get('NAME', 'Unknown')
                population = county['properties'].get('POP100', 0)
                state_fips = county['properties'].get('STATE', '')
                
                # Store county data for classification
                self.counties_data.append({
                    'name': name,
                    'population': population,
                    'geometry': county.get('geometry', {}),
                    'state_fips': state_fips
                })
                
                # Determine which axes to use
                if self.region == "West":
                    if state_fips == alaska_fips and self.ax_alaska:
                        target_ax = self.ax_alaska
                    elif state_fips == hawaii_fips and self.ax_hawaii:
                        target_ax = self.ax_hawaii
                    else:
                        target_ax = self.ax
                else:
                    target_ax = self.ax
                
                # Handle geometry
                geometry = county.get('geometry', {})
                geom_type = geometry.get('type', '')
                
                if geom_type == 'Polygon':
                    # Single polygon
                    if geometry.get('coordinates'):
                        coords = geometry['coordinates'][0]  # Exterior ring
                        coords_array = np.array(coords)
                        
                        polygon = Polygon(
                            coords_array,
                            facecolor='none',
                            edgecolor='black',
                            linewidth=0.5,
                            picker=True
                        )
                        polygon.county_data = {
                            'name': name,
                            'population': population
                        }
                        polygon.target_ax = target_ax  # Store which axis this patch belongs to
                        target_ax.add_patch(polygon)
                        self.county_patches.append(polygon)
                        
                elif geom_type == 'MultiPolygon':
                    # Multiple polygons
                    for polygon_coords in geometry.get('coordinates', []):
                        if polygon_coords:
                            coords = polygon_coords[0]  # Exterior ring
                            coords_array = np.array(coords)
                            
                            polygon = Polygon(
                                coords_array,
                                facecolor='none',
                                edgecolor='black',
                                linewidth=0.5,
                                picker=True
                            )
                            polygon.county_data = {
                                'name': name,
                                'population': population
                            }
                            polygon.target_ax = target_ax  # Store which axis this patch belongs to
                            target_ax.add_patch(polygon)
                            self.county_patches.append(polygon)
        
        self._show_loading("Finalizing map...", "Adjusting view and rendering...")
        
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        self.ax.set_title(f"{self.region} Region Counties", fontsize=14, fontweight='bold')
        
        # Auto-adjust view for main plot
        self.ax.autoscale()
        
        # Set fixed coordinate limits for insets to match main application
        if self.ax_alaska:
            self.ax_alaska.set_aspect('equal')
            # Use same coordinate limits as main application
            self.ax_alaska.set_xlim([-190, -125])
            self.ax_alaska.set_ylim([50, 73])
            # Remove tick marks and labels for cleaner appearance
            self.ax_alaska.set_xticks([])
            self.ax_alaska.set_yticks([])
            
        if self.ax_hawaii:
            self.ax_hawaii.set_aspect('equal')
            # Use same coordinate limits as main application
            self.ax_hawaii.set_xlim([-162, -154])
            self.ax_hawaii.set_ylim([18, 23])
            # Remove tick marks and labels for cleaner appearance
            self.ax_hawaii.set_xticks([])
            self.ax_hawaii.set_yticks([])
        
        # Add north arrow and scale bar
        self._add_map_elements()
        
        self.canvas.draw()
        
        # Hide loading overlay after drawing is complete
        self._hide_loading()
    
    def _add_map_elements(self):
        """Add north arrow and scale bar with region-specific positioning"""
        
        if self.region == "Southwest":
            # Southwest: North arrow in top-right
            n_y = 0.96
            arrow_y_start = 0.94
            arrow_y_end = 0.88
            n_x = 0.95
            arrow_x = 0.95
            
            # Scale bar in bottom-right
            scale_x = 0.95
            scale_y = 0.04
            scale_ha = 'right'
            
        elif self.region == "Southeast":
            # Southeast: North arrow and scale in bottom-right (stacked)
            # Scale at bottom
            scale_x = 0.95
            scale_y = 0.04
            scale_ha = 'right'
            
            # North arrow just above scale
            arrow_y_end = 0.08
            arrow_y_start = 0.14
            n_y = 0.16
            n_x = 0.95
            arrow_x = 0.95
            
        elif self.region == "Midwest":
            # Midwest: North arrow in top-right, scale in bottom-right
            n_y = 0.96
            arrow_y_start = 0.94
            arrow_y_end = 0.88
            n_x = 0.95
            arrow_x = 0.95
            
            scale_x = 0.95
            scale_y = 0.04
            scale_ha = 'right'
            
        elif self.region == "Northeast":
            # Northeast: North arrow and scale in bottom-right (stacked)
            # Scale at bottom
            scale_x = 0.95
            scale_y = 0.04
            scale_ha = 'right'
            
            # North arrow just above scale
            arrow_y_end = 0.08
            arrow_y_start = 0.14
            n_y = 0.16
            n_x = 0.95
            arrow_x = 0.95
            
        elif self.region == "West":
            # West: North arrow in top-right (outside contiguous frame)
            n_y = 0.96
            arrow_y_start = 0.94
            arrow_y_end = 0.88
            n_x = 1.05  # Outside the main plot
            arrow_x = 1.05
            
            # Scale above Hawaii inset (at bottom, outside main plot)
            scale_x = 1.05
            scale_y = 0.32  # Just above the insets at 30% bottom
            scale_ha = 'left'
        else:
            # Default positioning
            n_y = 0.96
            arrow_y_start = 0.94
            arrow_y_end = 0.88
            n_x = 0.95
            arrow_x = 0.95
            scale_x = 0.95
            scale_y = 0.04
            scale_ha = 'right'
        
        # N label
        self.ax.annotate(
            'N', xy=(n_x, n_y), xycoords='axes fraction',
            ha='center', va='center', fontsize=16, fontweight='bold',
            color='black'
        )
        
        # North arrow shaft
        self.ax.annotate(
            '', xy=(arrow_x, arrow_y_start), xytext=(arrow_x, arrow_y_end),
            xycoords='axes fraction', textcoords='axes fraction',
            arrowprops=dict(arrowstyle='->', lw=2, color='black')
        )
        
        # Scale bar
        self.ax.text(
            scale_x, scale_y, '500 miles',
            transform=self.ax.transAxes,
            ha=scale_ha, va='bottom',
            fontsize=10,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9, edgecolor='black')
        )
    
    def _apply_chloropleth(self):
        """Apply chloropleth symbology based on selected parameters"""
        if not self.counties_data or not self.county_patches:
            messagebox.showwarning("No Data", "Please load county data first")
            return
        
        # Show loading overlay
        self._show_loading("Applying chloropleth...", "Classifying population data...")
        
        # Get populations
        populations = [county['population'] for county in self.counties_data]
        
        # Filter out zero or invalid populations
        valid_populations = [p for p in populations if p > 0]
        
        if not valid_populations:
            self._hide_loading()
            messagebox.showwarning("No Data", "No valid population data found")
            return
        
        # Get classification method and color scheme
        method = self.classification_method.get()
        scheme = self.color_scheme.get()
        
        # Classify data into 5 classes
        num_classes = 5
        breaks = self._classify_data(valid_populations, method, num_classes)
        
        # Get colormap
        import matplotlib.cm as cm
        colormap = cm.get_cmap(scheme, num_classes)
        
        # Update progress
        self._show_loading("Applying chloropleth...", "Applying colors to counties...")
        
        # Apply colors to patches
        # Note: Don't zip counties_data and county_patches - they have different lengths
        # because MultiPolygon counties create multiple patches
        for i, patch in enumerate(self.county_patches):
            # Get population from the patch's stored county data
            population = patch.county_data.get('population', 0)
            
            # Determine which class this county belongs to
            if population <= 0:
                # No data - use light gray
                color = '#e0e0e0'
            else:
                class_idx = self._get_class_index(population, breaks)
                color = colormap(class_idx)
            
            # Update patch color
            patch.set_facecolor(color)
            patch.set_alpha(0.8)
        
        # Add legend
        self._add_legend(breaks, colormap, num_classes)
        
        # Redraw canvas
        self.canvas.draw()
        
        # Hide loading overlay
        self._hide_loading()
        
        # Update title to show applied classification
        self.ax.set_title(
            f"{self.region} Region Counties - {method} Classification ({scheme} Colors)",
            fontsize=12,
            fontweight='bold'
        )
    
    def _classify_data(self, data: List[float], method: str, num_classes: int) -> List[float]:
        """
        Classify data into breaks using specified method
        
        Args:
            data: List of values to classify
            method: Classification method name
            num_classes: Number of classes
            
        Returns:
            List of break values
        """
        sorted_data = sorted(data)
        
        if method == "Quantile":
            # Equal count in each class
            breaks = []
            for i in range(1, num_classes):
                percentile = (i / num_classes) * 100
                breaks.append(np.percentile(sorted_data, percentile))
            breaks.append(max(sorted_data))
            return breaks
            
        elif method == "Equal Interval":
            # Equal range in each class
            min_val = min(sorted_data)
            max_val = max(sorted_data)
            interval = (max_val - min_val) / num_classes
            breaks = [min_val + interval * (i + 1) for i in range(num_classes)]
            return breaks
            
        elif method == "Natural Breaks (Jenks)":
            # Simplified Jenks natural breaks
            # For a full implementation, you'd use a library like jenkspy
            # This is a simple approximation
            return self._jenks_breaks(sorted_data, num_classes)
        
        else:
            # Default to quantile
            return self._classify_data(data, "Quantile", num_classes)
    
    def _jenks_breaks(self, data: List[float], num_classes: int) -> List[float]:
        """
        Simplified Jenks natural breaks algorithm
        This is an approximation - for production use a library like jenkspy
        """
        # For simplicity, use a combination of quantile and variance
        # A real Jenks algorithm minimizes within-class variance
        sorted_data = sorted(data)
        n = len(sorted_data)
        
        # Start with quantile breaks
        breaks = []
        for i in range(1, num_classes):
            idx = int((i / num_classes) * n)
            if idx < n:
                breaks.append(sorted_data[idx])
        breaks.append(max(sorted_data))
        
        return breaks
    
    def _get_class_index(self, value: float, breaks: List[float]) -> int:
        """Get the class index for a given value"""
        for i, break_val in enumerate(breaks):
            if value <= break_val:
                return i
        return len(breaks) - 1
    
    def _add_legend(self, breaks: List[float], colormap, num_classes: int):
        """Add a legend showing the classification breaks"""
        # Remove existing legend if present
        if self.ax.get_legend():
            self.ax.get_legend().remove()
        
        # Create legend entries
        legend_elements = []
        from matplotlib.patches import Patch
        
        # Add class for "No Data"
        legend_elements.append(Patch(facecolor='#e0e0e0', edgecolor='black', label='No Data'))
        
        # Add classes
        prev_break = 0
        for i in range(num_classes):
            color = colormap(i)
            lower = prev_break if i == 0 else breaks[i-1]
            upper = breaks[i]
            
            # Format numbers with commas
            label = f"{int(lower):,} - {int(upper):,}"
            legend_elements.append(Patch(facecolor=color, edgecolor='black', label=label))
            prev_break = breaks[i]
        
        # Add legend with region-specific positioning
        if self.region == "Southwest":
            # Southwest: Legend in bottom-left
            legend_loc = 'lower left'
            legend_bbox = (0.02, 0.02)
            
        elif self.region == "Southeast":
            # Southeast: Legend in bottom-left
            legend_loc = 'lower left'
            legend_bbox = (0.02, 0.02)
            
        elif self.region == "Midwest":
            # Midwest: Legend to the left of scale bar in bottom-right
            legend_loc = 'lower right'
            legend_bbox = (0.70, 0.02)
            
        elif self.region == "Northeast":
            # Northeast: Legend above north arrow in bottom-right
            legend_loc = 'lower right'
            legend_bbox = (0.98, 0.20)
            
        elif self.region == "West":
            # West: Legend below north arrow, outside contiguous frame on right
            legend_loc = 'upper left'
            legend_bbox = (1.02, 0.88)
        else:
            # Default positioning
            legend_loc = 'best'
            legend_bbox = None
        
        self.ax.legend(
            handles=legend_elements,
            loc=legend_loc,
            bbox_to_anchor=legend_bbox,
            frameon=True,
            fancybox=True,
            shadow=True,
            title='Population (2010)',
            fontsize=9
        )
        
        # Adjust subplot to make room for legend
        # Skip tight_layout for West region since we use manually positioned axes
        if self.region != "West":
            self.figure.tight_layout()
    
    def _export_to_html(self):
        """Export current map to HTML file with embedded base64 image"""
        try:
            import base64
            from io import BytesIO
            
            # Create a simple HTML file with the current map
            filename = filedialog.asksaveasfilename(
                title="Export Map to HTML",
                defaultextension=".html",
                filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
            )
            
            if filename:
                # Save matplotlib figure to a BytesIO buffer
                buffer = BytesIO()
                self.figure.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
                buffer.seek(0)
                
                # Encode the image to base64
                img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
                buffer.close()
                
                # Create HTML content with embedded base64 image
                html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>{self.region} Region Population Map</title>
    <meta charset="UTF-8">
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            text-align: center; 
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        .info {{
            color: #7f8c8d;
            margin: 5px 0;
        }}
        img {{ 
            max-width: 100%; 
            height: auto;
            margin: 20px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        .footer {{
            margin-top: 20px;
            color: #95a5a6;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{self.region} Region Population Chloropleth</h1>
        <p class="info">Classification Method: {self.classification_method.get()}</p>
        <p class="info">Color Scheme: {self.color_scheme.get()}</p>
        <img src="data:image/png;base64,{img_base64}" alt="{self.region} Region Population Map">
        <p class="footer">Generated by Austin Averill's Population By Region Viewer</p>
    </div>
</body>
</html>
"""
                
                # Write HTML file
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                messagebox.showinfo("Export Complete", f"Map exported to {filename}")
                
                # Ask if user wants to open in browser
                if messagebox.askyesno("Open File", "Would you like to open the HTML file in your browser?"):
                    webbrowser.open(f"file://{os.path.abspath(filename)}")
                    
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export map: {str(e)}")
    
    def _on_hover(self, event):
        """Handle mouse hover for county tooltips with 1-second delay"""
        import time
        
        # Hide tooltip immediately when mouse moves (before doing anything else)
        if self.hover_tooltip:
            self.hover_tooltip.remove()
            self.hover_tooltip = None
            self.current_hover_county = None
            self.canvas.draw_idle()
        
        # Cancel any pending timer
        if self.hover_timer:
            self.window.after_cancel(self.hover_timer)
            self.hover_timer = None
        
        # Check if mouse is over a valid axis
        if event.inaxes not in [self.ax, self.ax_alaska, self.ax_hawaii]:
            self.current_hover_county = None
            return
        
        # Check if we're over a county patch
        if event.xdata is None or event.ydata is None:
            self.current_hover_county = None
            return
        
        # Find which county we're hovering over
        hovered_county = None
        mouse_point = (event.xdata, event.ydata)
        
        for patch in self.county_patches:
            # Check if this patch belongs to the current axis
            if hasattr(patch, 'target_ax') and patch.target_ax == event.inaxes:
                # Use matplotlib's contains method which returns (bool, dict)
                contains, _ = patch.contains(event)
                if contains:
                    hovered_county = patch
                    break
        
        if hovered_county and hasattr(hovered_county, 'county_data'):
            self.current_hover_county = hovered_county
            # Schedule tooltip to appear after 1 second
            self.hover_timer = self.window.after(1000, lambda: self._show_county_tooltip(event, hovered_county))
        else:
            self.current_hover_county = None
    
    def _show_county_tooltip(self, event, county_patch):
        """Show tooltip for a county after delay"""
        # Only show if we're still hovering over the same county
        if self.current_hover_county != county_patch:
            return
        
        # Check if event still has valid data
        if not hasattr(event, 'xdata') or not hasattr(event, 'ydata'):
            return
        
        if event.xdata is None or event.ydata is None:
            return
        
        # Get county data
        data = county_patch.county_data
        name = data.get('name', 'Unknown')
        population = data.get('population', 0)
        
        # Create tooltip text
        tooltip_text = f"{name}\nPopulation: {population:,}"
        
        # Determine which axis to use
        target_ax = county_patch.target_ax if hasattr(county_patch, 'target_ax') else self.ax
        
        # Create annotation near cursor with light beige background
        self.hover_tooltip = target_ax.annotate(
            tooltip_text,
            xy=(event.xdata, event.ydata),
            xytext=(15, 15),  # Offset from cursor
            textcoords='offset points',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#F5F5DC', alpha=0.95, edgecolor='black'),
            fontsize=10,
            zorder=1000  # Ensure it's on top
        )
        
        self.canvas.draw_idle()
    
    def _on_closing(self):
        """Handle window closing"""
        self.window.destroy()
        if self.return_callback:
            self.return_callback()
    
    def destroy(self):
        """Destroy the window"""
        if hasattr(self, 'window'):
            self.window.destroy()