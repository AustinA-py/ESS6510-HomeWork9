#!/usr/bin/env python3
"""
Simple test of application loading to identify display issues
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data.api_data_manager import APIDataManager
import json

def test_application_data():
    """Test what the application sees"""
    
    print("🧪 Testing Application Data Display")
    print("=" * 50)
    
    # Create data manager
    data_manager = APIDataManager()
    
    # Load data
    print("📥 Loading API data...")
    success = data_manager.load_data_async()
    
    if not success:
        print("❌ Failed to load data")
        return
    
    print("✅ Data loaded successfully")
    
    # Test states data
    if data_manager.states_data and 'features' in data_manager.states_data:
        print(f"\n🏛️ States Analysis:")
        print(f"   Total states: {len(data_manager.states_data['features'])}")
        
        # Test first few states
        for i, feature in enumerate(data_manager.states_data['features'][:5]):
            state_name = feature['properties']['NAME']
            region = data_manager.get_state_region(state_name)
            color = data_manager.get_region_color(region) if region else 'Unknown'
            
            print(f"   {i+1}. {state_name} -> Region: {region}, Color: {color}")
            
        print(f"\n   Sample state feature structure:")
        sample_state = data_manager.states_data['features'][0]
        print(f"   Properties: {list(sample_state['properties'].keys())}")
        print(f"   Geometry type: {sample_state['geometry']['type']}")
        if sample_state['geometry']['type'] == 'Polygon':
            coord_count = len(sample_state['geometry']['coordinates'][0]) if sample_state['geometry']['coordinates'] else 0
            print(f"   Coordinate points: {coord_count}")
    
    # Test region mapping
    print(f"\n🗺️ Region Mapping Test:")
    test_states = ['California', 'Texas', 'New York', 'Florida', 'Alaska']
    for state in test_states:
        region = data_manager.get_state_region(state)
        color = data_manager.get_region_color(region) if region else '#CCCCCC'
        print(f"   {state} -> {region} ({color})")

if __name__ == "__main__":
    test_application_data()