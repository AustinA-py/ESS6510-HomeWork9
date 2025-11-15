"""
API Data Manager for Census TIGERweb Services

This module handles API interactions with the Census TIGERweb services to fetch
states and counties data, replacing the static GeoJSON files with dynamic API calls.
"""

import json
import requests
import time
from typing import Dict, List, Optional, Any
from threading import Lock
import sys
import os

# Import the query parameters
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from geometry_query_params.states_query import states_url, states_params
from geometry_query_params.counties_query import counties_url, total_records_parms, counties_params
from data.data_manager import REGIONS, REGION_COLORS

class APIDataManager:
    """Manages loading and processing of geographic data from Census TIGERweb APIs"""
    
    def __init__(self):
        """Initialize the API data manager"""
        self.states_data = None
        self.counties_data = None
        self._counties_by_region = {}  # Cache counties by region
        self._current_region = None  # Track which region's counties are currently loaded
        self._state_to_region = {}
        self._load_lock = Lock()
        
        # Build reverse mapping from state to region
        for region, states in REGIONS.items():
            for state in states:
                self._state_to_region[state] = region
    
    def load_states_data(self, progress_callback=None) -> bool:
        """
        Load states data from the TIGERweb API
        
        Args:
            progress_callback: Optional callback function for progress updates
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if progress_callback:
                progress_callback("Fetching states data from Census API...")
            
            # Add geometry to the request parameters
            params = states_params.copy()
            params['returnGeometry'] = 'true'
            params['geometryPrecision'] = '6'  # Reasonable precision for display
            
            response = requests.get(states_url, params=params, timeout=30)
            response.raise_for_status()
            
            api_data = response.json()
            
            if 'error' in api_data:
                raise Exception(f"API Error: {api_data['error']}")
            
            # Convert ArcGIS format to GeoJSON format
            self.states_data = self._convert_to_geojson(api_data, 'states')
            
            print(f"Successfully loaded {len(self.states_data['features'])} states from API")
            return True
            
        except Exception as e:
            print(f"Error loading states data: {str(e)}")
            return False
    
    def load_counties_data(self, progress_callback=None) -> bool:
        """
        Load counties data from the TIGERweb API in batches
        
        Args:
            progress_callback: Optional callback function for progress updates
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Step 1: Get total record count
            if progress_callback:
                progress_callback("Getting total county count from Census API...")
            
            count_response = requests.get(counties_url, params=total_records_parms, timeout=30)
            count_response.raise_for_status()
            count_data = count_response.json()
            
            if 'error' in count_data:
                raise Exception(f"API Error getting count: {count_data['error']}")
            
            total_records = count_data.get('count', 0)
            print(f"Total counties to fetch: {total_records}")
            
            if total_records == 0:
                raise Exception("No county records found")
            
            # Step 2: Fetch data in optimized batches (150 records for faster loading)
            batch_size = 150  # Larger batch size for better performance
            all_features = []
            successful_batches = 0
            failed_batches = 0
            
            # If total_records is very large, load all counties (remove artificial limit)
            max_records = total_records
            print(f"Loading all {max_records} counties...")
            
            for batch_start in range(1, max_records + 1, batch_size):
                batch_end = min(batch_start + batch_size - 1, max_records)
                
                if progress_callback:
                    progress = (batch_start - 1) / max_records * 100
                    progress_callback(f"Fetching counties batch {batch_start}-{batch_end} ({progress:.1f}% complete)...")
                
                # Create where clause for this batch
                where_clause = f"OBJECTID >= {batch_start} AND OBJECTID <= {batch_end}"
                
                print(f"Attempting batch {batch_start}-{batch_end}: {where_clause}")
                
                # Prepare parameters for this batch
                batch_params = counties_params.copy()
                batch_params['where'] = where_clause
                batch_params['returnGeometry'] = 'true'
                batch_params['geometryPrecision'] = '2'  # Lower precision for faster loading and smaller data
                batch_params['resultRecordCount'] = batch_size  # Explicit record limit
                
                max_retries = 3
                retry_count = 0
                batch_success = False
                
                while retry_count < max_retries and not batch_success:
                    try:
                        # Fetch this batch with longer timeout
                        batch_response = requests.get(counties_url, params=batch_params, timeout=90)
                        batch_response.raise_for_status()
                        batch_data = batch_response.json()
                        
                        if 'error' in batch_data:
                            print(f"⚠️ API Error in batch {batch_start}-{batch_end}: {batch_data['error']}")
                            if retry_count < max_retries - 1:
                                retry_count += 1
                                print(f"   Retrying... (attempt {retry_count + 1}/{max_retries})")
                                time.sleep(1)
                                continue
                            else:
                                failed_batches += 1
                                break
                        
                        # Add features from this batch
                        if 'features' in batch_data and batch_data['features']:
                            batch_features = batch_data['features']
                            all_features.extend(batch_features)
                            successful_batches += 1
                            print(f"✅ Batch {batch_start}-{batch_end}: {len(batch_features)} counties loaded")
                            batch_success = True
                        else:
                            print(f"⚠️ Batch {batch_start}-{batch_end}: No features returned")
                            if 'features' not in batch_data:
                                print(f"   Response keys: {list(batch_data.keys())}")
                            failed_batches += 1
                            break
                            
                    except requests.exceptions.Timeout:
                        print(f"⏰ Timeout for batch {batch_start}-{batch_end} (attempt {retry_count + 1})")
                        retry_count += 1
                        if retry_count < max_retries:
                            time.sleep(2)
                        else:
                            failed_batches += 1
                    except requests.exceptions.RequestException as e:
                        print(f"🔗 Request error for batch {batch_start}-{batch_end}: {str(e)}")
                        retry_count += 1
                        if retry_count < max_retries:
                            time.sleep(2)
                        else:
                            failed_batches += 1
                    except Exception as e:
                        print(f"❌ Unexpected error for batch {batch_start}-{batch_end}: {str(e)}")
                        retry_count += 1
                        if retry_count < max_retries:
                            time.sleep(2)
                        else:
                            failed_batches += 1
                
                # No delay between batches for faster loading
                # The API can handle rapid requests
            
            print(f"\nBatch Summary: {successful_batches} successful, {failed_batches} failed")
            
            if not all_features:
                raise Exception("No county features were successfully loaded from any batch")
            
            # Step 3: Convert to GeoJSON format
            if progress_callback:
                progress_callback("Converting counties data to GeoJSON format...")
            
            # Create a mock API response with all features
            combined_data = {
                'features': all_features,
                'geometryType': 'esriGeometryPolygon',
                'spatialReference': {'wkid': 102100, 'latestWkid': 3857}
            }
            
            self.counties_data = self._convert_to_geojson(combined_data, 'counties')
            
            print(f"Successfully loaded {len(self.counties_data['features'])} counties from API")
            return True
            
        except Exception as e:
            print(f"Error loading counties data: {str(e)}")
            return False
    
    def load_counties_for_region(self, region: str, progress_callback=None) -> bool:
        """
        Load counties data for a specific region from the TIGERweb API
        Uses STATE FIPS codes to query counties state-by-state (more efficient than OBJECTID batching)
        Uses caching to avoid reloading the same region multiple times
        
        Args:
            region: Region name to load counties for
            progress_callback: Optional callback function for progress updates
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if this region's counties are already cached
            if region in self._counties_by_region:
                print(f"✅ Using cached counties for {region} region ({len(self._counties_by_region[region]['features'])} counties)")
                self.counties_data = self._counties_by_region[region]
                self._current_region = region
                if progress_callback:
                    progress_callback(f"Loaded {len(self.counties_data['features'])} cached counties for {region} region")
                return True
            
            if progress_callback:
                progress_callback(f"Loading counties for {region} region...")
            
            # Get states in this region
            states_in_region = self.get_states_in_region(region)
            
            if not states_in_region:
                raise Exception(f"No states found in region: {region}")
            
            # Get STATE FIPS codes for states in this region
            state_fips_codes = []
            for feature in self.states_data['features']:
                state_name = feature['properties']['NAME']
                if state_name in states_in_region:
                    fips_code = feature['properties'].get('STATE', '')
                    # Exclude Puerto Rico (72) and U.S. Virgin Islands (78)
                    if fips_code and fips_code not in ['72', '78']:
                        state_fips_codes.append(fips_code)
            
            if not state_fips_codes:
                raise Exception(f"No FIPS codes found for states in region: {region}")
            
            print(f"Loading counties for {len(state_fips_codes)} states in {region} region...")
            
            # Fetch counties for each state
            all_features = []
            successful_states = 0
            failed_states = 0
            
            for i, fips_code in enumerate(state_fips_codes):
                if progress_callback:
                    progress = (i / len(state_fips_codes)) * 100
                    progress_callback(f"Fetching counties for state {i+1}/{len(state_fips_codes)} ({progress:.1f}% complete)...")
                
                # Create where clause for this state
                where_clause = f"STATE = '{fips_code}'"
                
                print(f"Fetching counties for state FIPS {fips_code}...")
                
                # Prepare parameters for this state
                state_params = counties_params.copy()
                state_params['where'] = where_clause
                state_params['returnGeometry'] = 'true'
                state_params['geometryPrecision'] = '2'  # Lower precision for faster loading
                
                try:
                    # Fetch counties for this state
                    response = requests.get(counties_url, params=state_params, timeout=60)
                    response.raise_for_status()
                    state_data = response.json()
                    
                    if 'error' in state_data:
                        print(f"⚠️ API Error for state {fips_code}: {state_data['error']}")
                        failed_states += 1
                        continue
                    
                    # Add features from this state
                    if 'features' in state_data and state_data['features']:
                        state_features = state_data['features']
                        all_features.extend(state_features)
                        successful_states += 1
                        print(f"✅ State {fips_code}: {len(state_features)} counties loaded")
                    else:
                        print(f"⚠️ State {fips_code}: No counties returned")
                        failed_states += 1
                        
                except requests.exceptions.Timeout:
                    print(f"⏰ Timeout for state {fips_code}, skipping...")
                    failed_states += 1
                except requests.exceptions.RequestException as e:
                    print(f"🔗 Request error for state {fips_code}: {str(e)}")
                    failed_states += 1
                except Exception as e:
                    print(f"❌ Unexpected error for state {fips_code}: {str(e)}")
                    failed_states += 1
            
            print(f"\nState Summary: {successful_states} successful, {failed_states} failed")
            
            if not all_features:
                raise Exception(f"No county features were successfully loaded for region {region}")
            
            # Convert to GeoJSON format
            if progress_callback:
                progress_callback(f"Converting {region} counties data to GeoJSON format...")
            
            # Create a mock API response with all features
            combined_data = {
                'features': all_features,
                'geometryType': 'esriGeometryPolygon',
                'spatialReference': {'wkid': 102100, 'latestWkid': 3857}
            }
            
            self.counties_data = self._convert_to_geojson(combined_data, 'counties')
            
            # Cache the counties data for this region
            self._counties_by_region[region] = self.counties_data
            self._current_region = region
            
            print(f"Successfully loaded {len(self.counties_data['features'])} counties for {region} region from API")
            return True
            
        except Exception as e:
            print(f"Error loading counties data for region {region}: {str(e)}")
            return False
    
    def _convert_to_geojson(self, api_data: Dict, data_type: str) -> Dict:
        """
        Convert ArcGIS API response to GeoJSON format
        
        Args:
            api_data: Raw API response data
            data_type: 'states' or 'counties'
            
        Returns:
            Data in GeoJSON format
        """
        features = []
        
        for feature in api_data.get('features', []):
            # Extract geometry
            geometry = self._convert_arcgis_geometry_to_geojson(feature.get('geometry', {}))
            
            # Extract properties
            attributes = feature.get('attributes', {})
            properties = {}
            
            if data_type == 'states':
                # Get state name and generate abbreviation if needed
                state_name = attributes.get('NAME', '')
                state_abbr = attributes.get('STATE_ABBR', attributes.get('STUSPS', ''))
                
                # If no abbreviation available, generate from name
                if not state_abbr:
                    state_abbr = self._get_state_abbreviation(state_name)
                
                properties = {
                    'NAME': state_name,
                    'STATE_ABBR': state_abbr,
                    'STUSPS': state_abbr,
                    'STATE': attributes.get('STATE', '')  # FIPS code for querying counties
                }
            elif data_type == 'counties':
                properties = {
                    'NAME': attributes.get('NAME', ''),
                    'STATE': attributes.get('STATE', ''),
                    'POP100': attributes.get('POP100', 0)
                }
            
            # Create GeoJSON feature
            geojson_feature = {
                'type': 'Feature',
                'properties': properties,
                'geometry': geometry
            }
            features.append(geojson_feature)
        
        return {
            'type': 'FeatureCollection',
            'features': features
        }
    
    def _convert_arcgis_geometry_to_geojson(self, arcgis_geometry: Dict) -> Dict:
        """
        Convert ArcGIS geometry to GeoJSON geometry
        Converts from Web Mercator (EPSG:3857) to WGS84 (lat/lon)
        
        Args:
            arcgis_geometry: ArcGIS geometry object
            
        Returns:
            GeoJSON geometry object with lat/lon coordinates
        """
        if not arcgis_geometry or 'rings' not in arcgis_geometry:
            return {'type': 'Polygon', 'coordinates': []}
        
        rings = arcgis_geometry['rings']
        
        # Convert all rings from Web Mercator to lat/lon
        converted_rings = []
        for ring in rings:
            converted_ring = [self._web_mercator_to_latlon(x, y) for x, y in ring]
            converted_rings.append(converted_ring)
        
        if len(converted_rings) == 1:
            # Simple polygon
            return {
                'type': 'Polygon',
                'coordinates': converted_rings
            }
        else:
            # Complex polygon - need to group rings into polygons
            # For simplicity, treat as MultiPolygon with each ring as a separate polygon
            polygons = []
            for ring in converted_rings:
                if len(ring) >= 4:  # Valid polygon needs at least 4 points
                    polygons.append([ring])
            
            if len(polygons) == 1:
                return {
                    'type': 'Polygon',
                    'coordinates': polygons[0]
                }
            else:
                return {
                    'type': 'MultiPolygon',
                    'coordinates': polygons
                }
    
    def _web_mercator_to_latlon(self, x: float, y: float) -> List[float]:
        """
        Convert Web Mercator (EPSG:3857) coordinates to lat/lon (WGS84)
        
        Args:
            x: X coordinate in Web Mercator (meters)
            y: Y coordinate in Web Mercator (meters)
            
        Returns:
            [longitude, latitude] in degrees
        """
        import math
        
        # Web Mercator to WGS84 conversion
        # Earth radius in meters
        earth_radius = 6378137.0
        
        # Convert X to longitude
        lon = (x / earth_radius) * (180.0 / math.pi)
        
        # Convert Y to latitude
        lat = (2 * math.atan(math.exp(y / earth_radius)) - math.pi / 2) * (180.0 / math.pi)
        
        return [lon, lat]
    
    def _get_state_abbreviation(self, state_name: str) -> str:
        """Get state abbreviation from full name"""
        # Import the abbreviations dictionary
        try:
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
            from geometry_query_params.us_states_abbreviations import get_state_abbreviation
            return get_state_abbreviation(state_name)
        except:
            # Fallback to first two characters
            return state_name[:2].upper() if state_name else ''
    
    def load_data_async(self, progress_callback=None, load_counties=False) -> bool:
        """
        Load states data and optionally counties data asynchronously
        
        Args:
            progress_callback: Optional callback function for progress updates
            load_counties: Whether to load counties data (default False for faster startup)
            
        Returns:
            True if successful, False otherwise
        """
        with self._load_lock:
            try:
                # Load states data first
                if not self.load_states_data(progress_callback):
                    return False
                
                # Optionally load counties data (can be loaded later when needed)
                if load_counties:
                    if not self.load_counties_data(progress_callback):
                        return False
                
                return True
                
            except Exception as e:
                print(f"Error in async data loading: {str(e)}")
                return False
    
    def is_data_loaded(self) -> bool:
        """Check if states data is loaded (counties are optional)"""
        return self.states_data is not None
    
    def are_counties_loaded(self) -> bool:
        """Check if counties data is loaded"""
        return self.counties_data is not None
    
    def get_state_region(self, state_name: str) -> Optional[str]:
        """
        Get the region for a given state name
        
        Args:
            state_name: Name of the state
            
        Returns:
            Region name or None if not found
        """
        return self._state_to_region.get(state_name)
    
    def get_states_in_region(self, region: str) -> set:
        """
        Get all states in a given region
        
        Args:
            region: Region name
            
        Returns:
            Set of state names in the region
        """
        return REGIONS.get(region, set())
    
    def get_region_color(self, region: str) -> str:
        """
        Get the color for a given region
        
        Args:
            region: Region name
            
        Returns:
            Hex color code
        """
        return REGION_COLORS.get(region, '#CCCCCC')
    
    def get_counties_in_region(self, region: str) -> List[Dict]:
        """
        Get all counties in a given region
        
        Args:
            region: Region name
            
        Returns:
            List of county features in the region
        """
        if not self.counties_data:
            return []
        
        states_in_region = self.get_states_in_region(region)
        regional_counties = []
        
        for feature in self.counties_data['features']:
            # Match by state code/name
            state_code = feature['properties'].get('STATE', '')
            # Note: You may need to add logic to convert state codes to names
            # for proper matching with the regional definitions
            
            # For now, this is a placeholder - you'll need to implement
            # the state code to state name mapping
            regional_counties.append(feature)
        
        return regional_counties

if __name__ == "__main__":
    # Test the API data manager
    def test_progress(message):
        print(f"Progress: {message}")
    
    print("Testing API Data Manager...")
    
    api_manager = APIDataManager()
    
    # Test loading data
    if api_manager.load_data_async(test_progress):
        print("✅ Data loaded successfully!")
        print(f"States loaded: {len(api_manager.states_data['features'])}")
        print(f"Counties loaded: {len(api_manager.counties_data['features'])}")
    else:
        print("❌ Failed to load data")