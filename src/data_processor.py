"""
Data Processor Module for Geospatial NLP System
Handles loading and preprocessing of geographical data
"""

import pandas as pd
import os
from typing import Dict, List, Set


class DataProcessor:
    """
    Handles loading and preprocessing of geographical data from CSV files
    """
    
    def __init__(self, data_path: str = None):
        """
        Initialize the DataProcessor
        
        Args:
            data_path: Path to the data directory
        """
        if data_path is None:
            data_path = os.path.join(os.path.dirname(__file__), '..', 'data')
        self.data_path = data_path
        self.cities_df = None
        self.countries_set = None
        self.states_set = None
        self.cities_set = None
        
    def load_worldcities_data(self) -> pd.DataFrame:
        """
        Load the worldcities.csv file and return as DataFrame
        
        Returns:
            DataFrame containing the world cities data
        """
        csv_path = os.path.join(self.data_path, 'worldcities.csv')
        
        # Try different paths if the file is not found
        if not os.path.exists(csv_path):
            # Try parent directory
            csv_path = os.path.join(os.path.dirname(self.data_path), 'worldcities.csv')
            
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"worldcities.csv not found in {self.data_path} or parent directory")
            
        self.cities_df = pd.read_csv(csv_path)
        return self.cities_df
    
    def extract_canonical_names(self) -> Dict[str, Set[str]]:
        """
        Extract canonical names for cities, countries, and states
        
        Returns:
            Dictionary containing sets of canonical names for each type
        """
        if self.cities_df is None:
            self.load_worldcities_data()
        
        # Extract unique cities (using city_ascii for consistent naming)
        self.cities_set = set(self.cities_df['city_ascii'].dropna().str.lower().unique())
        
        # Extract unique countries
        self.countries_set = set(self.cities_df['country'].dropna().str.lower().unique())
        
        # Extract unique states/admin areas
        self.states_set = set(self.cities_df['admin_name'].dropna().str.lower().unique())
        
        return {
            'cities': self.cities_set,
            'countries': self.countries_set,
            'states': self.states_set
        }
    
    def get_canonical_mappings(self) -> Dict[str, Dict[str, str]]:
        """
        Create mappings from lowercase names to original case canonical names
        
        Returns:
            Dictionary containing mappings for each geographical type
        """
        if self.cities_df is None:
            self.load_worldcities_data()
        
        # Create city mappings
        city_mappings = {}
        for _, row in self.cities_df.iterrows():
            if pd.notna(row['city_ascii']):
                city_key = row['city_ascii'].lower()
                city_mappings[city_key] = row['city_ascii']
        
        # Create country mappings
        country_mappings = {}
        for country in self.cities_df['country'].dropna().unique():
            country_mappings[country.lower()] = country
        
        # Create state mappings
        state_mappings = {}
        for state in self.cities_df['admin_name'].dropna().unique():
            state_mappings[state.lower()] = state
        
        return {
            'cities': city_mappings,
            'countries': country_mappings,
            'states': state_mappings
        }
    
    def get_data_stats(self) -> Dict[str, int]:
        """
        Get statistics about the loaded data
        
        Returns:
            Dictionary containing data statistics
        """
        if self.cities_df is None:
            self.load_worldcities_data()
        
        return {
            'total_cities': len(self.cities_df),
            'unique_countries': self.cities_df['country'].nunique(),
            'unique_states': self.cities_df['admin_name'].nunique()
        }
