#!/usr/bin/env python3
"""
Test geometry conversion to see what's actually in the data
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data.api_data_manager import APIDataManager
import json

def test_geometry():
    """Test the geometry data structure"""
    
    print("🔍 Testing Geometry Data")
    print("=" * 60)
    
    # Create data manager
    data_manager = APIDataManager()
    
    # Load states data
    print("📥 Loading states data...")
    success = data_manager.load_states_data()
    
    if not success:
        print("❌ Failed to load states data")
        return
    
    print("✅ States data loaded successfully")
    
    if data_manager.states_data and 'features' in data_manager.states_data:
        # Look at first state
        first_state = data_manager.states_data['features'][0]
        
        print(f"\n📊 First State: {first_state['properties']['NAME']}")
        print(f"   Geometry type: {first_state['geometry']['type']}")
        
        # Check coordinates
        geom = first_state['geometry']
        if geom['type'] == 'Polygon':
            print(f"   Number of rings: {len(geom['coordinates'])}")
            if geom['coordinates']:
                first_ring = geom['coordinates'][0]
                print(f"   Points in first ring: {len(first_ring)}")
                if first_ring:
                    print(f"   First coordinate: {first_ring[0]}")
                    print(f"   Coordinate format: lon={first_ring[0][0]}, lat={first_ring[0][1]}")
        elif geom['type'] == 'MultiPolygon':
            print(f"   Number of polygons: {len(geom['coordinates'])}")
            if geom['coordinates']:
                first_poly = geom['coordinates'][0]
                print(f"   Rings in first polygon: {len(first_poly)}")
                if first_poly:
                    first_ring = first_poly[0]
                    print(f"   Points in first ring: {len(first_ring)}")
                    if first_ring:
                        print(f"   First coordinate: {first_ring[0]}")
                        print(f"   Coordinate format: lon={first_ring[0][0]}, lat={first_ring[0][1]}")
        
        # Check a few states
        print(f"\n📋 Sample of states and their geometry types:")
        for i, feature in enumerate(data_manager.states_data['features'][:10]):
            state_name = feature['properties']['NAME']
            geom_type = feature['geometry']['type']
            has_coords = len(feature['geometry']['coordinates']) > 0 if 'coordinates' in feature['geometry'] else False
            
            if has_coords and geom_type == 'Polygon':
                coord_count = len(feature['geometry']['coordinates'][0]) if feature['geometry']['coordinates'] else 0
            elif has_coords and geom_type == 'MultiPolygon':
                coord_count = sum(len(poly[0]) for poly in feature['geometry']['coordinates'] if poly)
            else:
                coord_count = 0
            
            print(f"   {i+1}. {state_name:20s} - {geom_type:12s} - {coord_count:6d} points")

if __name__ == "__main__":
    test_geometry()
