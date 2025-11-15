"""
Austin Averill's Population By Region Viewer
ESS6510 - Homework 9

Main application entry point for the interactive regional population viewer.
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main application entry point"""
    try:
        from gui.main_application import RegionalPopulationViewer
        
        # Create and run the application
        # The RegionalPopulationViewer handles its own loading screen
        app = RegionalPopulationViewer()
        app.run()
        
    except Exception as e:
        messagebox.showerror("Application Error", f"Failed to start application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()