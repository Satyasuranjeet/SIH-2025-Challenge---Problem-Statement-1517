"""
Main Geospatial Query System
Orchestrates the entire pipeline for geospatial entity extraction and matching
"""

from typing import List, Dict, Optional
import os
import sys

# Add src directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_processor import DataProcessor
from nlp_processor import NLPProcessor
from fuzzy_matcher import FuzzyMatcher


class GeospatialQuerySystem:
    """
    Main system for processing natural language queries and extracting geospatial entities
    """
    
    def __init__(self, data_path: str = None, fuzzy_threshold: float = 80):
        """
        Initialize the geospatial query system
        
        Args:
            data_path: Path to the data directory
            fuzzy_threshold: Minimum similarity threshold for fuzzy matching
        """
        self.data_processor = DataProcessor(data_path)
        self.nlp_processor = NLPProcessor()
        self.fuzzy_matcher = None
        self.fuzzy_threshold = fuzzy_threshold
        
        # Initialize the system
        self.setup()
    
    def setup(self):
        """
        Setup the system by loading data and initializing components
        """
        print("Loading geographical data...")
        try:
            # Load and process data
            self.data_processor.load_worldcities_data()
            canonical_mappings = self.data_processor.get_canonical_mappings()
            
            # Initialize fuzzy matcher
            self.fuzzy_matcher = FuzzyMatcher(canonical_mappings, self.fuzzy_threshold)
            
            # Get data statistics
            stats = self.data_processor.get_data_stats()
            print(f"Loaded {stats['total_cities']} cities from {stats['unique_countries']} countries")
            print("System initialized successfully!")
            
        except Exception as e:
            print(f"Error during setup: {e}")
            raise
    
    def process_query(self, query: str, detailed: bool = False) -> List[Dict[str, any]]:
        """
        Process a natural language query and extract geospatial entities
        
        Args:
            query: Natural language query containing place names
            detailed: Whether to return detailed matching information
            
        Returns:
            List of extracted and matched geospatial entities
        """
        if not self.fuzzy_matcher:
            raise RuntimeError("System not properly initialized. Please check setup.")
        
        # Step 1: Preprocess the query
        processed_query = self.nlp_processor.preprocess_text(query)
        
        # Step 2: Extract potential place names using NLP
        potential_places = self.nlp_processor.extract_all_potential_places(processed_query)
        
        if not potential_places:
            return []
        
        # Step 3: Match each potential place to canonical names
        results = []
        for place in potential_places:
            matches = self.fuzzy_matcher.match_query(place)
            
            if matches:
                # Take the best match for each place
                best_match = matches[0]
                
                if detailed:
                    best_match['all_matches'] = matches
                    best_match['original_query'] = query
                    best_match['processed_query'] = processed_query
                
                results.append(best_match)
        
        return results
    
    def format_results(self, results: List[Dict[str, any]], format_type: str = 'standard') -> str:
        """
        Format the results for display
        
        Args:
            results: List of result dictionaries
            format_type: Type of formatting ('standard', 'detailed', 'json')
            
        Returns:
            Formatted results string
        """
        if not results:
            return "No geographical entities found in the query."
        
        if format_type == 'json':
            import json
            return json.dumps(results, indent=2)
        
        formatted_lines = []
        
        for i, result in enumerate(results, 1):
            if format_type == 'standard':
                line = f"Token: {result['token']}, Canonical name: {result['canonical_name']}, Table: {result['table']}"
            elif format_type == 'detailed':
                line = (f"{i}. Token: {result['token']}\n"
                       f"   Canonical name: {result['canonical_name']}\n"
                       f"   Table: {result['table']}\n"
                       f"   Confidence: {result['confidence_score']:.1f}%")
            else:
                line = f"Token: {result['token']}, Canonical name: {result['canonical_name']}, Table: {result['table']}"
            
            formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def demo_queries(self) -> List[Dict[str, any]]:
        """
        Run demo queries to showcase the system
        
        Returns:
            List of demo results
        """
        demo_queries = [
            "Which of the following saw the highest average temperature in January, Maharashtra, Ahmedabad or entire New-Zealand?",
            "Show me a graph of rainfall for Chennai for the month of October",
            "Compare weather patterns between Mumbai, Delhi, and Bangalore",
            "What is the population of New York City and Los Angeles?",
            "Tell me about the climate in Mumbay and Deli",  # Intentional typos
        ]
        
        demo_results = []
        for query in demo_queries:
            print(f"\nQuery: {query}")
            results = self.process_query(query)
            formatted = self.format_results(results, 'detailed')
            print(f"Results:\n{formatted}")
            
            demo_results.append({
                'query': query,
                'results': results,
                'formatted': formatted
            })
        
        return demo_results


def main():
    """
    Main function to run the geospatial query system
    """
    try:
        # Initialize the system
        system = GeospatialQuerySystem()
        
        print("\n" + "="*60)
        print("GEOSPATIAL NLP QUERY SYSTEM")
        print("="*60)
        
        # Run demo queries
        print("\nRunning demo queries...")
        system.demo_queries()
        
        # Interactive mode
        print("\n" + "="*60)
        print("INTERACTIVE MODE")
        print("="*60)
        print("Enter your queries (type 'quit' to exit):")
        
        while True:
            query = input("\nQuery: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
            
            if not query:
                continue
            
            try:
                results = system.process_query(query)
                formatted = system.format_results(results, 'detailed')
                print(f"\nResults:\n{formatted}")
                
            except Exception as e:
                print(f"Error processing query: {e}")
        
        print("Thank you for using the Geospatial NLP Query System!")
        
    except Exception as e:
        print(f"Error initializing system: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
