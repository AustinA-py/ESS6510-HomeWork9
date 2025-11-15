"""
API Data Loading Manager for Loading Screen

This module handles the asynchronous loading of data from the Census TIGERweb APIs
with progress updates for the loading screen.
"""

import threading
import time
from typing import Callable, Optional
from data.api_data_manager import APIDataManager

class APIDataLoadingManager:
    """Manages API data loading with progress updates"""
    
    def __init__(self, api_data_manager: APIDataManager, progress_callback: Optional[Callable] = None):
        """
        Initialize API data loading manager
        
        Args:
            api_data_manager: APIDataManager instance
            progress_callback: Function to call with progress updates
        """
        self.api_data_manager = api_data_manager
        self.progress_callback = progress_callback
        self.loading_complete = False
        self.loading_successful = False
        self.error_message = None
    
    def load_data_async(self):
        """Load data asynchronously with progress updates"""
        try:
            if self.progress_callback:
                self.progress_callback("Initializing Census API connection...")
            
            # Use the async loading method from the API data manager
            success = self.api_data_manager.load_data_async(self.progress_callback)
            
            if success:
                if self.progress_callback:
                    self.progress_callback("Data loading complete!")
                time.sleep(0.2)  # Brief pause for final message
                self.loading_successful = True
            else:
                raise Exception("Failed to load data from Census APIs")
            
        except Exception as e:
            self.error_message = str(e)
            self.loading_successful = False
            print(f"Error loading API data: {str(e)}")
        
        finally:
            self.loading_complete = True
    
    def _load_next_step(self):
        """Load data in steps (kept for compatibility but simplified for API)"""
        # For API loading, we don't need the complex step-by-step approach
        # since the APIDataManager handles the batching internally
        self.load_data_async()
    
    def _schedule_next_step(self, callback, delay_ms):
        """Schedule next loading step without blocking the main thread"""
        import threading
        
        def delayed_callback():
            time.sleep(delay_ms / 1000.0)  # Convert to seconds
            callback()
        
        thread = threading.Thread(target=delayed_callback)
        thread.daemon = True
        thread.start()
    
    def _finalize_loading(self):
        """Finalize the loading process"""
        self.loading_successful = True
        self.loading_complete = True