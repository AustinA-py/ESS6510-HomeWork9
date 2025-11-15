#!/usr/bin/env python3
"""
Test the corrected data structure
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data.api_data_manager import APIDataManager

def test_data_structure():
    """Test the actual data structure after conversion"""
    
    print("🔍 Testing Data Structure After Conversion")
    print("=" * 50)
    
    # Create data manager
    data_manager = APIDataManager()
    
    # Load just states data to test
    print("📥 Loading states data...")
    success = data_manager.load_states_data()
    
    if not success:
        print("❌ Failed to load states data")
        return
    
    print("✅ States data loaded successfully")
    
    if data_manager.states_data and 'features' in data_manager.states_data:
        print(f"\n📊 States data structure:")
        first_feature = data_manager.states_data['features'][0]
        
        print(f"   Feature structure: {list(first_feature.keys())}")
        print(f"   Properties: {first_feature['properties']}")
        print(f"   Geometry type: {first_feature['geometry']['type']}")
        
        # Test accessing the way the application does
        state_name = first_feature['properties']['NAME']
        state_abbr = first_feature['properties'].get('STATE_ABBR', 'N/A')
        
        print(f"   State: {state_name}, Abbr: {state_abbr}")
        
        # Test region mapping
        region = data_manager.get_state_region(state_name)
        print(f"   Region: {region}")
        
        print(f"\n✅ Data structure is correct for application use")
    else:
        print("❌ No states data available")

if __name__ == "__main__":
    test_data_structure()