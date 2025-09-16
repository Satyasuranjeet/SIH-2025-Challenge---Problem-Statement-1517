"""
Demo script for Geospatial NLP Query System
This script demonstrates the core functionality with minimal dependencies
"""

import os
import re
import sys
from typing import List, Dict, Optional


class SimpleFuzzyMatcher:
    """
    Simple fuzzy matcher using basic string similarity
    (Fallback when rapidfuzz is not available)
    """
    
    @staticmethod
    def similarity(s1: str, s2: str) -> float:
        """Calculate basic string similarity"""
        s1, s2 = s1.lower(), s2.lower()
        
        # Exact match
        if s1 == s2:
            return 100.0
        
        # Length difference penalty
        len_diff = abs(len(s1) - len(s2))
        max_len = max(len(s1), len(s2))
        if max_len == 0:
            return 0.0
        
        # Character overlap
        chars1 = set(s1)
        chars2 = set(s2)
        overlap = len(chars1.intersection(chars2))
        total_chars = len(chars1.union(chars2))
        
        if total_chars == 0:
            return 0.0
        
        # Basic similarity score
        char_score = (overlap / total_chars) * 100
        length_penalty = (len_diff / max_len) * 20
        
        return max(0, char_score - length_penalty)
    
    @staticmethod
    def find_best_match(query: str, candidates: List[str], threshold: float = 70) -> Optional[str]:
        """Find best matching candidate"""
        best_match = None
        best_score = 0
        
        for candidate in candidates:
            score = SimpleFuzzyMatcher.similarity(query, candidate)
            if score >= threshold and score > best_score:
                best_score = score
                best_match = candidate
        
        return best_match


class SimpleGeoDemo:
    """
    Simple demonstration of the geospatial NLP concept
    """
    
    def __init__(self):
        """Initialize with sample data"""
        self.sample_cities = [
            'mumbai', 'delhi', 'bangalore', 'chennai', 'kolkata', 'hyderabad',
            'pune', 'ahmedabad', 'jaipur', 'surat', 'lucknow', 'kanpur',
            'nagpur', 'visakhapatnam', 'bhopal', 'patna', 'vadodara',
            'new york', 'los angeles', 'chicago', 'houston', 'phoenix',
            'london', 'paris', 'tokyo', 'beijing', 'sydney', 'toronto'
        ]
        
        self.sample_countries = [
            'india', 'united states', 'united kingdom', 'canada', 'australia',
            'germany', 'france', 'japan', 'china', 'brazil', 'russia',
            'new zealand', 'south africa', 'mexico', 'italy', 'spain'
        ]
        
        self.sample_states = [
            'maharashtra', 'karnataka', 'tamil nadu', 'gujarat', 'rajasthan',
            'west bengal', 'uttar pradesh', 'madhya pradesh', 'bihar',
            'california', 'texas', 'florida', 'new york', 'illinois'
        ]
        
        # Create reverse mappings for proper case
        self.city_mappings = {city: city.title() for city in self.sample_cities}
        self.country_mappings = {country: country.title() for country in self.sample_countries}
        self.state_mappings = {state: state.title() for state in self.sample_states}
        
        # Special cases
        self.city_mappings.update({
            'new york': 'New York',
            'los angeles': 'Los Angeles',
        })
        self.country_mappings.update({
            'united states': 'United States',
            'united kingdom': 'United Kingdom',
            'new zealand': 'New Zealand',
            'south africa': 'South Africa'
        })
        self.state_mappings.update({
            'new york': 'New York',
            'west bengal': 'West Bengal',
            'uttar pradesh': 'Uttar Pradesh',
            'madhya pradesh': 'Madhya Pradesh',
            'tamil nadu': 'Tamil Nadu'
        })
    
    def extract_potential_places(self, text: str) -> List[str]:
        """Extract potential place names from text"""
        # Simple pattern matching for capitalized words
        pattern = r'\b[A-Z][a-zA-Z\-]+(?:\s+[A-Z][a-zA-Z\-]+)*\b'
        matches = re.findall(pattern, text)
        
        # Filter out common non-place words
        stop_words = {
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December',
            'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
            'Which', 'Show', 'The', 'This', 'That', 'These', 'Those', 'And', 'Or', 'But',
            'Graph', 'Chart', 'Temperature', 'Rainfall', 'Average', 'Highest', 'Following'
        }
        
        filtered_matches = [match for match in matches if match not in stop_words]
        return filtered_matches
    
    def match_entity(self, query: str) -> List[Dict[str, any]]:
        """Match extracted entity to geographical databases"""
        results = []
        
        # Preprocess query
        query_clean = re.sub(r'[^\w\s-]', '', query.lower().strip())
        query_clean = query_clean.replace('new-zealand', 'new zealand')
        
        # Try matching to cities
        city_match = SimpleFuzzyMatcher.find_best_match(query_clean, self.sample_cities)
        if city_match:
            results.append({
                'token': query,
                'canonical_name': self.city_mappings[city_match],
                'table': 'City',
                'confidence_score': SimpleFuzzyMatcher.similarity(query_clean, city_match)
            })
        
        # Try matching to countries
        country_match = SimpleFuzzyMatcher.find_best_match(query_clean, self.sample_countries)
        if country_match:
            results.append({
                'token': query,
                'canonical_name': self.country_mappings[country_match],
                'table': 'Country',
                'confidence_score': SimpleFuzzyMatcher.similarity(query_clean, country_match)
            })
        
        # Try matching to states
        state_match = SimpleFuzzyMatcher.find_best_match(query_clean, self.sample_states)
        if state_match:
            results.append({
                'token': query,
                'canonical_name': self.state_mappings[state_match],
                'table': 'State',
                'confidence_score': SimpleFuzzyMatcher.similarity(query_clean, state_match)
            })
        
        # Return best match
        if results:
            return [max(results, key=lambda x: x['confidence_score'])]
        return []
    
    def process_query(self, query: str) -> List[Dict[str, any]]:
        """Process a complete query"""
        print(f"\nProcessing: {query}")
        print("-" * 50)
        
        # Extract potential places
        potential_places = self.extract_potential_places(query)
        print(f"Potential places found: {potential_places}")
        
        # Match each potential place
        all_results = []
        for place in potential_places:
            matches = self.match_entity(place)
            all_results.extend(matches)
        
        # Display results
        if all_results:
            print("Results:")
            for result in all_results:
                print(f"Token: {result['token']}, "
                      f"Canonical name: {result['canonical_name']}, "
                      f"Table: {result['table']}")
        else:
            print("No geographical entities found.")
        
        return all_results


def main():
    """Main demo function"""
    print("🌍 GEOSPATIAL NLP QUERY SYSTEM - DEMO")
    print("=" * 50)
    print("This is a simplified demo version showing core concepts.")
    print("For full functionality, please install all dependencies.")
    print()
    
    # Initialize demo system
    demo = SimpleGeoDemo()
    
    # Demo queries
    demo_queries = [
        "Which of the following saw the highest average temperature in January, Maharashtra, Ahmedabad or entire New-Zealand?",
        "Show me a graph of rainfall for Chennai for the month of October",
        "Compare weather patterns between Mumbai, Delhi, and Bangalore",
        "What is the population of New York City and Los Angeles?",
        "Tell me about the climate in Mumbay and Deli",  # Intentional typos
    ]
    
    print("DEMO QUERIES:")
    print("=" * 30)
    
    for query in demo_queries:
        demo.process_query(query)
        print()
    
    # Interactive mode
    print("INTERACTIVE MODE:")
    print("=" * 30)
    print("Enter your queries (type 'quit' to exit):")
    
    while True:
        try:
            query = input("\nQuery: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
            
            if not query:
                continue
            
            demo.process_query(query)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    print("\nThank you for trying the demo!")
    print("Install full dependencies for complete functionality.")


if __name__ == "__main__":
    main()
