"""
Regional definitions and data loading for the Population Viewer

This module handles loading GeoJSON data and defines the US regional
groupings as specified in the requirements.
"""

import json
import os
from typing import Dict, List, Optional, Set

# Regional definitions as specified in the requirements
REGIONS = {
    'West': {
        'Washington', 'Montana', 'Idaho', 'Oregon', 'Wyoming', 
        'California', 'Nevada', 'Utah', 'Colorado', 'Alaska', 'Hawaii'
    },
    'Midwest': {
        'North Dakota', 'South Dakota', 'Nebraska', 'Kansas', 
        'Minnesota', 'Iowa', 'Missouri', 'Wisconsin', 'Illinois', 
        'Indiana', 'Michigan', 'Ohio'
    },
    'Northeast': {
        'Pennsylvania', 'Maryland', 'Delaware', 'New Jersey', 
        'Connecticut', 'Rhode Island', 'Massachusetts', 'New York', 
        'Vermont', 'New Hampshire', 'Maine'
    },
    'Southeast': {
        'District of Columbia', 'Virginia', 'West Virginia', 'Kentucky', 
        'Arkansas', 'Louisiana', 'Mississippi', 'Alabama', 'Georgia', 
        'Florida', 'South Carolina', 'North Carolina', 'Tennessee'
    },
    'Southwest': {
        'Oklahoma', 'Texas', 'New Mexico', 'Arizona'
    }
}

# Color scheme for regions
REGION_COLORS = {
    'West': '#FF6B6B',      # Red
    'Midwest': '#4ECDC4',   # Teal
    'Northeast': '#45B7D1', # Blue
    'Southeast': '#96CEB4', # Green
    'Southwest': '#FECA57'  # Yellow
}

class DataManager:
    """Manages loading and processing of GeoJSON data"""
    
    def __init__(self, data_dir: str = "source_geometries"):
        self.data_dir = data_dir
        self.states_data = None
        self.counties_data = None
        self._state_to_region = {}
        
        # Build reverse mapping from state to region
        for region, states in REGIONS.items():
            for state in states:
                self._state_to_region[state] = region
    
    def load_data(self) -> bool:
        """
        Load states and counties GeoJSON data (legacy method for compatibility)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load states data
            states_path = os.path.join(self.data_dir, "states.geojson")
            if os.path.exists(states_path):
                with open(states_path, 'r', encoding='utf-8') as f:
                    self.states_data = json.load(f)
                print(f"Loaded {len(self.states_data['features'])} states")
            else:
                print(f"Warning: {states_path} not found")
                return False
            
            # Load counties data
            counties_path = os.path.join(self.data_dir, "counties.geojson")
            if os.path.exists(counties_path):
                with open(counties_path, 'r', encoding='utf-8') as f:
                    self.counties_data = json.load(f)
                print(f"Loaded {len(self.counties_data['features'])} counties")
            else:
                print(f"Warning: {counties_path} not found")
                return False
                
            return True
            
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return False
    
    def get_state_region(self, state_name: str) -> Optional[str]:
        """
        Get the region for a given state name
        
        Args:
            state_name: Name of the state
            
        Returns:
            Region name or None if not found
        """
        return self._state_to_region.get(state_name)
    
    def get_states_in_region(self, region: str) -> Set[str]:
        """
        Get all states in a given region
        
        Args:
            region: Region name
            
        Returns:
            Set of state names in the region
        """
        return REGIONS.get(region, set())
    
    def get_counties_in_region(self, region: str) -> List[Dict]:
        """
        Get all counties in a given region
        
        Args:
            region: Region name
            
        Returns:
            List of county feature dictionaries
        """
        if not self.counties_data:
            return []
            
        region_states = self.get_states_in_region(region)
        region_counties = []
        
        for feature in self.counties_data['features']:
            # Handle both possible attribute structures
            if 'attributes' in feature:
                state_name = feature['attributes'].get('STATE_NAME')
            elif 'properties' in feature:
                state_name = feature['properties'].get('STATE_NAME')
            else:
                continue
                
            if state_name in region_states:
                region_counties.append(feature)
        
        return region_counties
    
    def get_region_color(self, region: str) -> str:
        """
        Get the color for a given region
        
        Args:
            region: Region name
            
        Returns:
            Hex color string
        """
        return REGION_COLORS.get(region, '#CCCCCC')
    
    def is_data_loaded(self) -> bool:
        """Check if data has been successfully loaded"""
        return self.states_data is not None and self.counties_data is not None