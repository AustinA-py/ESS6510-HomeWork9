#!/usr/bin/env python3
"""
Test script to run the application with error catching
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import traceback

def test_main_application():
    """Test the main application with error catching"""
    
    print("🧪 Testing Main Application with Error Catching")
    print("=" * 60)
    
    try:
        # Import the main application
        from gui.main_application import RegionalPopulationViewer
        
        print("✅ Successfully imported RegionalPopulationViewer")
        
        # Try to create the application instance
        print("📱 Creating application instance...")
        app = RegionalPopulationViewer()
        
        print("✅ Application instance created successfully")
        
        # Check if data manager is working
        if hasattr(app, 'data_manager'):
            print("✅ Data manager exists")
        else:
            print("❌ No data manager found")
            
        # Check loading manager
        if hasattr(app, 'loading_manager'):
            print("✅ Loading manager exists")
        else:
            print("❌ No loading manager found")
        
        print("\n🎯 Application seems to initialize correctly")
        print("   The issue might be in the GUI display or event loop")
        print("   Try running the application and check for visual display")
        
        # Don't run the actual event loop to avoid hanging
        # app.run()
        
    except Exception as e:
        print(f"❌ Error during application initialization:")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        print(f"\n📍 Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    test_main_application()