"""
Debug Counties API - Test different approaches to loading counties data

This script tests various approaches to identify why counties aren't loading.
"""

import requests
import sys
import os

# Add path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'geometry_query_params'))

from counties_query import counties_url, total_records_parms, counties_params

def test_counties_api_approaches():
    """Test different approaches to loading counties data"""
    
    print("🔍 Debugging Counties API")
    print("=" * 40)
    
    # Test 1: Basic connectivity
    print("\n1️⃣ Testing basic API connectivity...")
    try:
        response = requests.get(counties_url, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   URL accessible: ✅")
    except Exception as e:
        print(f"   ❌ Basic connectivity failed: {e}")
        return
    
    # Test 2: Get total count
    print("\n2️⃣ Testing total count query...")
    try:
        response = requests.get(counties_url, params=total_records_parms, timeout=30)
        print(f"   Status: {response.status_code}")
        count_data = response.json()
        print(f"   Response: {count_data}")
        
        if 'count' in count_data:
            total_count = count_data['count']
            print(f"   ✅ Total counties: {total_count}")
        else:
            print(f"   ❌ No count returned")
            return
    except Exception as e:
        print(f"   ❌ Count query failed: {e}")
        return
    
    # Test 3: Simple query with minimal parameters
    print("\n3️⃣ Testing minimal query (no geometry)...")
    try:
        simple_params = {
            "where": "OBJECTID <= 5",
            "outFields": "OBJECTID,NAME,STATE",
            "f": "json"
        }
        
        response = requests.get(counties_url, params=simple_params, timeout=30)
        print(f"   Status: {response.status_code}")
        data = response.json()
        
        if 'features' in data:
            print(f"   ✅ Features returned: {len(data['features'])}")
            if data['features']:
                sample = data['features'][0]['attributes']
                print(f"   Sample: {sample}")
        else:
            print(f"   ❌ No features: {list(data.keys())}")
            print(f"   Response: {data}")
    except Exception as e:
        print(f"   ❌ Simple query failed: {e}")
    
    # Test 4: Query with geometry
    print("\n4️⃣ Testing query with geometry...")
    try:
        geom_params = {
            "where": "OBJECTID <= 3",
            "outFields": "OBJECTID,NAME,STATE,POP100",
            "returnGeometry": "true",
            "f": "json"
        }
        
        response = requests.get(counties_url, params=geom_params, timeout=60)
        print(f"   Status: {response.status_code}")
        data = response.json()
        
        if 'features' in data:
            print(f"   ✅ Features with geometry: {len(data['features'])}")
            if data['features']:
                sample = data['features'][0]
                attrs = sample['attributes']
                has_geom = 'geometry' in sample
                print(f"   Sample: {attrs['NAME']}, Has geometry: {has_geom}")
        else:
            print(f"   ❌ No features with geometry")
            if 'error' in data:
                print(f"   Error: {data['error']}")
    except Exception as e:
        print(f"   ❌ Geometry query failed: {e}")
    
    # Test 5: Alternative where clause formats
    print("\n5️⃣ Testing alternative where clause formats...")
    
    test_where_clauses = [
        "OBJECTID = 1",
        "OBJECTID IN (1,2,3)",
        "OBJECTID BETWEEN 1 AND 3",
        "1=1"
    ]
    
    for where_clause in test_where_clauses:
        try:
            test_params = {
                "where": where_clause,
                "outFields": "OBJECTID,NAME",
                "f": "json",
                "resultRecordCount": 3  # Limit results
            }
            
            response = requests.get(counties_url, params=test_params, timeout=30)
            data = response.json()
            
            if 'features' in data and data['features']:
                print(f"   ✅ '{where_clause}': {len(data['features'])} features")
            else:
                print(f"   ❌ '{where_clause}': No features")
                
        except Exception as e:
            print(f"   ❌ '{where_clause}': Failed - {e}")
    
    # Test 6: Check service info
    print("\n6️⃣ Getting service information...")
    try:
        info_url = counties_url.replace('/query', '')
        response = requests.get(info_url, params={'f': 'json'}, timeout=30)
        info = response.json()
        
        print(f"   Service Name: {info.get('name', 'Unknown')}")
        print(f"   Max Record Count: {info.get('maxRecordCount', 'Unknown')}")
        print(f"   Supports Pagination: {info.get('supportsPagination', 'Unknown')}")
        
        if 'fields' in info:
            field_names = [f['name'] for f in info['fields']]
            print(f"   Available fields: {field_names}")
            
    except Exception as e:
        print(f"   ❌ Service info failed: {e}")
    
    print(f"\n🏁 Counties API debugging complete!")

if __name__ == "__main__":
    test_counties_api_approaches()