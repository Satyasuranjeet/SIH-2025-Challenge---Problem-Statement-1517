"""
Fuzzy Matcher Module for Geospatial NLP System
Handles fuzzy string matching for geographical entities
"""

from rapidfuzz import fuzz, process
from typing import Dict, List, Tuple, Optional, Set
import re


class FuzzyMatcher:
    """
    Handles fuzzy string matching for mapping extracted text to canonical place names
    """
    
    def __init__(self, canonical_data: Dict[str, Dict[str, str]], threshold: float = 80):
        """
        Initialize the fuzzy matcher
        
        Args:
            canonical_data: Dictionary containing canonical mappings for cities, countries, states
            threshold: Minimum similarity threshold for matches (0-100)
        """
        self.canonical_data = canonical_data
        self.threshold = threshold
        
        # Create lookup lists for fuzzy matching
        self.cities_lookup = list(canonical_data.get('cities', {}).keys())
        self.countries_lookup = list(canonical_data.get('countries', {}).keys())
        self.states_lookup = list(canonical_data.get('states', {}).keys())
        
        # Create reverse mappings for getting original case
        self.city_mappings = canonical_data.get('cities', {})
        self.country_mappings = canonical_data.get('countries', {})
        self.state_mappings = canonical_data.get('states', {})
    
    def preprocess_query(self, query: str) -> str:
        """
        Preprocess query string for better matching
        
        Args:
            query: Input query string
            
        Returns:
            Preprocessed query string
        """
        # Convert to lowercase
        query = query.lower()
        
        # Remove extra spaces and punctuation
        query = re.sub(r'[^\w\s-]', '', query)
        query = re.sub(r'\s+', ' ', query)
        query = query.strip()
        
        # Handle common variations
        replacements = {
            'new-zealand': 'new zealand',
            'newyork': 'new york',
            'losangeles': 'los angeles',
            'sanfrancisco': 'san francisco',
            'unitedstates': 'united states',
            'unitedkingdom': 'united kingdom',
            'southafrica': 'south africa',
        }
        
        for old, new in replacements.items():
            query = query.replace(old, new)
        
        return query
    
    def find_best_match(self, query: str, lookup_list: List[str], 
                       mapping_dict: Dict[str, str]) -> Optional[Tuple[str, float, str]]:
        """
        Find the best fuzzy match for a query in a lookup list
        
        Args:
            query: Query string to match
            lookup_list: List of canonical names to search in
            mapping_dict: Dictionary mapping lowercase to original case
            
        Returns:
            Tuple of (canonical_name, score, table_type) or None if no good match
        """
        if not lookup_list:
            return None
        
        # Preprocess query
        processed_query = self.preprocess_query(query)
        
        # Find best match using different algorithms
        matches = []
        
        # Ratio matching
        ratio_match = process.extractOne(processed_query, lookup_list, scorer=fuzz.ratio)
        if ratio_match and ratio_match[1] >= self.threshold:
            matches.append(('ratio', ratio_match))
        
        # Partial ratio matching (good for substring matches)
        partial_match = process.extractOne(processed_query, lookup_list, scorer=fuzz.partial_ratio)
        if partial_match and partial_match[1] >= self.threshold:
            matches.append(('partial', partial_match))
        
        # Token sort ratio (good for word order variations)
        token_sort_match = process.extractOne(processed_query, lookup_list, scorer=fuzz.token_sort_ratio)
        if token_sort_match and token_sort_match[1] >= self.threshold:
            matches.append(('token_sort', token_sort_match))
        
        # Token set ratio (good for extra words)
        token_set_match = process.extractOne(processed_query, lookup_list, scorer=fuzz.token_set_ratio)
        if token_set_match and token_set_match[1] >= self.threshold:
            matches.append(('token_set', token_set_match))
        
        if not matches:
            return None
        
        # Select best match (highest score)
        best_match = max(matches, key=lambda x: x[1][1])
        matched_key = best_match[1][0]
        score = best_match[1][1]
        
        # Get original case canonical name
        canonical_name = mapping_dict.get(matched_key, matched_key)
        
        return canonical_name, score, best_match[0]
    
    def match_to_cities(self, query: str) -> Optional[Tuple[str, float, str]]:
        """
        Match query to cities
        
        Args:
            query: Query string to match
            
        Returns:
            Tuple of (canonical_name, score, match_type) or None
        """
        result = self.find_best_match(query, self.cities_lookup, self.city_mappings)
        if result:
            return result[0], result[1], 'City'
        return None
    
    def match_to_countries(self, query: str) -> Optional[Tuple[str, float, str]]:
        """
        Match query to countries
        
        Args:
            query: Query string to match
            
        Returns:
            Tuple of (canonical_name, score, match_type) or None
        """
        result = self.find_best_match(query, self.countries_lookup, self.country_mappings)
        if result:
            return result[0], result[1], 'Country'
        return None
    
    def match_to_states(self, query: str) -> Optional[Tuple[str, float, str]]:
        """
        Match query to states/admin areas
        
        Args:
            query: Query string to match
            
        Returns:
            Tuple of (canonical_name, score, match_type) or None
        """
        result = self.find_best_match(query, self.states_lookup, self.state_mappings)
        if result:
            return result[0], result[1], 'State'
        return None
    
    def match_query(self, query: str) -> List[Dict[str, any]]:
        """
        Match a query to all geographical types and return best matches
        
        Args:
            query: Query string to match
            
        Returns:
            List of match dictionaries with details
        """
        matches = []
        
        # Try matching to each type
        city_match = self.match_to_cities(query)
        country_match = self.match_to_countries(query)
        state_match = self.match_to_states(query)
        
        # Collect all valid matches
        for match, table_type in [(city_match, 'City'), (country_match, 'Country'), (state_match, 'State')]:
            if match:
                matches.append({
                    'token': query,
                    'canonical_name': match[0],
                    'table': match[2],
                    'confidence_score': match[1],
                    'match_algorithm': match[2] if len(match) > 2 else 'unknown'
                })
        
        # Sort by confidence score
        matches.sort(key=lambda x: x['confidence_score'], reverse=True)
        
        return matches
    
    def get_best_match(self, query: str) -> Optional[Dict[str, any]]:
        """
        Get the single best match for a query
        
        Args:
            query: Query string to match
            
        Returns:
            Best match dictionary or None
        """
        matches = self.match_query(query)
        return matches[0] if matches else None
