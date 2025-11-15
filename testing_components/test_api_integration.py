"""
Test script for API data integration

Run this script to test the API data loading functionality
before integrating with the main application.
"""

import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data.api_data_manager import APIDataManager

def test_api_integration():
    """Test the API data loading functionality"""
    
    print("🚀 Testing Census TIGERweb API Integration")
    print("=" * 50)
    
    def progress_callback(message):
        print(f"📡 {message}")
    
    # Initialize API data manager
    print("\n1️⃣ Initializing API Data Manager...")
    api_manager = APIDataManager()
    
    # Test states data loading
    print("\n2️⃣ Testing States Data Loading...")
    if api_manager.load_states_data(progress_callback):
        print(f"✅ States loaded successfully: {len(api_manager.states_data['features'])} states")
        
        # Show sample state
        if api_manager.states_data['features']:
            sample_state = api_manager.states_data['features'][0]
            print(f"   Sample: {sample_state['properties']['NAME']}")
    else:
        print("❌ Failed to load states data")
        return False
    
    # Test counties data loading (first 200 records for speed)
    print("\n3️⃣ Testing Counties Data Loading (limited batch)...")
    
    # Test the API endpoint directly first
    try:
        import requests
        from geometry_query_params.counties_query import counties_url, total_records_parms, counties_params
        
        print(f"   🔍 Counties API URL: {counties_url}")
        
        # First test: Get total count
        print("   📊 Getting total county count...")
        count_response = requests.get(counties_url, params=total_records_parms, timeout=30)
        print(f"   📊 Count response status: {count_response.status_code}")
        count_data = count_response.json()
        print(f"   📊 Count response: {count_data}")
        
        if 'count' in count_data:
            total_count = count_data['count']
            print(f"   📊 Total counties available: {total_count}")
            
            # Second test: Try to fetch first 10 counties with detailed debugging
            test_params = counties_params.copy()
            test_params['where'] = "OBJECTID <= 10"
            test_params['returnGeometry'] = 'true'
            test_params['geometryPrecision'] = '6'
            
            print(f"   🔍 Test parameters: {test_params}")
            
            response = requests.get(counties_url, params=test_params, timeout=60)
            print(f"   📡 Response status: {response.status_code}")
            print(f"   📡 Response headers: {dict(response.headers)}")
            
            counties_data = response.json()
            print(f"   📡 Response keys: {list(counties_data.keys())}")
            
            if 'features' in counties_data:
                features = counties_data['features']
                print(f"   ✅ Counties test successful: {len(features)} counties loaded")
                
                if features:
                    # Show first county in detail
                    sample_county = features[0]
                    print(f"   📋 Sample county structure:")
                    print(f"       Attributes keys: {list(sample_county.get('attributes', {}).keys())}")
                    attrs = sample_county.get('attributes', {})
                    print(f"       Name: {attrs.get('NAME', 'N/A')}")
                    print(f"       State: {attrs.get('STATE', 'N/A')}")
                    print(f"       Pop100: {attrs.get('POP100', 'N/A')}")
                    print(f"       Has geometry: {'geometry' in sample_county}")
                else:
                    print("   ⚠️ No features in response")
            else:
                print(f"   ❌ No 'features' key in response: {counties_data}")
        else:
            print(f"   ❌ No 'count' in response: {count_data}")
            
    except Exception as e:
        print(f"❌ Counties test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test region mapping
    print("\n4️⃣ Testing Region Mapping...")
    test_states = ['California', 'Texas', 'New York', 'Florida']
    for state in test_states:
        region = api_manager.get_state_region(state)
        color = api_manager.get_region_color(region) if region else 'None'
        print(f"   {state} → {region} ({color})")
    
    print("\n🎉 API Integration Test Complete!")
    print("\n📋 Next Steps:")
    print("   - Run the main application to test full integration")
    print("   - The app will now load data from Census APIs instead of static files")
    print("   - Loading may take longer due to API calls, but data will be current")
    
    return True

if __name__ == "__main__":
    try:
        test_api_integration()
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()