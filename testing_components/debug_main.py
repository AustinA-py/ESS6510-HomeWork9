#!/usr/bin/env python3
"""
Debug version of main.py with enhanced error catching
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os
import traceback

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main application entry point with enhanced debugging"""
    print("🚀 Starting Austin Averill's Population By Region Viewer...")
    
    try:
        print("📦 Importing modules...")
        from gui.main_application import RegionalPopulationViewer
        
        print("🖥️ Creating application...")
        # Create and run the application
        app = RegionalPopulationViewer()
        
        print("▶️ Starting application...")
        app.run()
        
        print("✅ Application completed successfully")
        
    except ImportError as e:
        print(f"❌ Import Error: {str(e)}")
        print("   Make sure all required modules are installed")
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Application Error: {str(e)}")
        traceback.print_exc()
        try:
            messagebox.showerror("Application Error", f"Failed to start application:\n\n{str(e)}")
        except:
            pass
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()