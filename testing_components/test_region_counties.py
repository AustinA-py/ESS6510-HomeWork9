#!/usr/bin/env python3
"""
Test loading counties for a specific region
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data.api_data_manager import APIDataManager

def test_region_counties():
    """Test loading counties for a specific region"""
    
    print("🔍 Testing Region-Specific County Loading")
    print("=" * 60)
    
    # Create data manager
    data_manager = APIDataManager()
    
    # Load states data first
    print("📥 Loading states data...")
    if not data_manager.load_states_data():
        print("❌ Failed to load states data")
        return
    
    print("✅ States data loaded successfully")
    
    # Test loading counties for West region
    test_region = "West"
    print(f"\n📥 Loading counties for {test_region} region...")
    
    success = data_manager.load_counties_for_region(test_region)
    
    if success:
        print(f"\n✅ Successfully loaded counties for {test_region}")
        print(f"   Total counties: {len(data_manager.counties_data['features'])}")
        
        # Show sample
        if data_manager.counties_data['features']:
            sample = data_manager.counties_data['features'][0]
            print(f"   Sample county: {sample['properties']['NAME']} (State: {sample['properties']['STATE']})")
    else:
        print(f"❌ Failed to load counties for {test_region}")

if __name__ == "__main__":
    test_region_counties()
