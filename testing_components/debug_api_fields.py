#!/usr/bin/env python3
"""
Debug script to examine the actual field names in API data
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data.api_data_manager import APIDataManager
import json

def debug_api_fields():
    """Debug the actual field names in API data"""
    
    print("🔍 Debugging API Data Fields")
    print("=" * 50)
    
    # Create data manager
    data_manager = APIDataManager()
    
    # Load data
    print("📥 Loading API data...")
    data_manager.load_data_async()
    
    # Check states data
    if data_manager.states_data and 'features' in data_manager.states_data:
        print(f"\n🏛️ States Data Analysis")
        print(f"   Total states: {len(data_manager.states_data['features'])}")
        
        # Look at first state feature
        first_state = data_manager.states_data['features'][0]
        print(f"   Sample state properties:")
        for key, value in first_state['properties'].items():
            print(f"     {key}: {value}")
        
        print(f"   Sample state geometry type: {first_state['geometry']['type']}")
    
    # Check counties data
    if data_manager.counties_data and 'features' in data_manager.counties_data:
        print(f"\n🏘️ Counties Data Analysis")
        print(f"   Total counties: {len(data_manager.counties_data['features'])}")
        
        # Look at first county feature
        first_county = data_manager.counties_data['features'][0]
        print(f"   Sample county properties:")
        for key, value in first_county['properties'].items():
            print(f"     {key}: {value}")
        
        print(f"   Sample county geometry type: {first_county['geometry']['type']}")

if __name__ == "__main__":
    debug_api_fields()