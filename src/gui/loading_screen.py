"""
Loading Screen with Spinner for Data Loading

This module provides a loading screen with animated spinner while
GeoJSON data is being loaded into memory.
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from typing import Callable, Optional

class LoadingScreen:
    """Loading screen with animated spinner"""
    
    def __init__(self, parent: Optional[tk.Tk] = None):
        """Initialize the loading screen"""
        if parent:
            self.root = tk.Toplevel(parent)
        else:
            self.root = tk.Tk()
        
        self.root.title("Loading...")
        self.root.geometry("400x300")
        self.root.configure(bg='white')
        self.root.resizable(False, False)
        
        # Center the window
        self.root.eval('tk::PlaceWindow . center')
        
        # Remove window decorations for splash effect
        self.root.overrideredirect(True)
        
        self.is_loading = True
        self.spinner_angle = 0
        
        self._setup_gui()
        self._start_spinner_animation()
    
    def _setup_gui(self):
        """Set up the loading screen GUI"""
        # Main frame with border
        main_frame = tk.Frame(self.root, bg='white', relief='raised', bd=2)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="Austin Averill's Population By Region Viewer",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        title_label.pack(pady=(30, 20))
        
        # Create canvas for spinner
        self.canvas = tk.Canvas(
            main_frame,
            width=80,
            height=80,
            bg='white',
            highlightthickness=0
        )
        self.canvas.pack(pady=20)
        
        # Loading text
        self.status_label = tk.Label(
            main_frame,
            text="Loading geographic data...",
            font=('Arial', 11),
            bg='white',
            fg='#34495e'
        )
        self.status_label.pack(pady=10)
        
        # Progress text
        self.progress_label = tk.Label(
            main_frame,
            text="Please wait while data files are loaded into memory",
            font=('Arial', 9),
            bg='white',
            fg='#7f8c8d'
        )
        self.progress_label.pack(pady=(5, 30))
    
    def _start_spinner_animation(self):
        """Start the spinner animation"""
        self._draw_spinner()
        if self.is_loading:
            self.root.after(50, self._start_spinner_animation)
    
    def _draw_spinner(self):
        """Draw the animated spinner"""
        self.canvas.delete("spinner")
        
        # Draw spinner arc
        self.canvas.create_arc(
            10, 10, 70, 70,
            start=self.spinner_angle,
            extent=60,
            outline='#3498db',
            width=4,
            style='arc',
            tags="spinner"
        )
        
        # Update angle for animation
        self.spinner_angle = (self.spinner_angle + 15) % 360
    
    def update_status(self, text: str):
        """Update the status text - thread-safe"""
        if hasattr(self, 'status_label'):
            # Schedule GUI update on main thread to avoid threading issues
            self.root.after(0, lambda: self._update_status_safe(text))
    
    def _update_status_safe(self, text: str):
        """Safely update status text from main thread"""
        if hasattr(self, 'status_label') and self.status_label.winfo_exists():
            self.status_label.config(text=text)
    
    def close(self):
        """Close the loading screen"""
        self.is_loading = False
        self.root.destroy()

class DataLoadingManager:
    """Manages data loading with progress updates"""
    
    def __init__(self, data_manager, progress_callback: Optional[Callable] = None):
        """
        Initialize data loading manager
        
        Args:
            data_manager: DataManager instance
            progress_callback: Function to call with progress updates
        """
        self.data_manager = data_manager
        self.progress_callback = progress_callback
        self.loading_complete = False
        self.loading_successful = False
        self.error_message = None
    
    def load_data_async(self):
        """Load data asynchronously with progress updates"""
        try:
            if self.progress_callback:
                self.progress_callback("Initializing data loader...")
            
            # Use a queue-based approach to break up the work
            self._load_next_step()
            
        except Exception as e:
            self.error_message = str(e)
            self.loading_successful = False
            self.loading_complete = True
            print(f"Error loading data: {str(e)}")
    
    def _load_next_step(self):
        """Load data in small steps to keep UI responsive"""
        try:
            import os
            import json
            
            # Step 1: Load states data
            if not hasattr(self, '_states_loaded'):
                if self.progress_callback:
                    self.progress_callback("Loading states.geojson...")
                
                states_path = os.path.join(self.data_manager.data_dir, "states.geojson")
                if os.path.exists(states_path):
                    with open(states_path, 'r', encoding='utf-8') as f:
                        self.data_manager.states_data = json.load(f)
                    print(f"Loaded {len(self.data_manager.states_data['features'])} states")
                else:
                    raise FileNotFoundError(f"States data file not found: {states_path}")
                
                self._states_loaded = True
                # Schedule next step with small delay to allow spinner to animate
                self._schedule_next_step(self._load_next_step, 100)
                return
            
            # Step 2: Load counties data
            if not hasattr(self, '_counties_loaded'):
                if self.progress_callback:
                    self.progress_callback("Loading counties.geojson...")
                
                counties_path = os.path.join(self.data_manager.data_dir, "counties.geojson")
                if os.path.exists(counties_path):
                    with open(counties_path, 'r', encoding='utf-8') as f:
                        self.data_manager.counties_data = json.load(f)
                    print(f"Loaded {len(self.data_manager.counties_data['features'])} counties")
                else:
                    raise FileNotFoundError(f"Counties data file not found: {counties_path}")
                
                self._counties_loaded = True
                # Schedule next step with small delay
                self._schedule_next_step(self._load_next_step, 100)
                return
            
            # Step 3: Finalize
            if self.progress_callback:
                self.progress_callback("Finalizing data processing...")
            
            # Small delay before marking complete to show final message
            self._schedule_next_step(self._finalize_loading, 200)
            
        except Exception as e:
            self.error_message = str(e)
            self.loading_successful = False
            self.loading_complete = True
            print(f"Error loading data: {str(e)}")
    
    def _schedule_next_step(self, callback, delay_ms):
        """Schedule next loading step without blocking the main thread"""
        import threading
        
        def delayed_callback():
            time.sleep(delay_ms / 1000.0)  # Convert to seconds
            callback()
        
        thread = threading.Thread(target=delayed_callback)
        thread.daemon = True
        thread.start()
    
    def _finalize_loading(self):
        """Finalize the loading process"""
        self.loading_successful = True
        self.loading_complete = True