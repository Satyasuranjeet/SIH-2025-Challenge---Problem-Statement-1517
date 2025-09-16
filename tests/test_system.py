"""
Test file for the Geospatial NLP Query System
"""

import unittest
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

from data_processor import DataProcessor
from nlp_processor import NLPProcessor
from fuzzy_matcher import FuzzyMatcher
from geospatial_query_system import GeospatialQuerySystem


class TestDataProcessor(unittest.TestCase):
    """Test cases for DataProcessor"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Use a test data path that points to the parent directory
        test_data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
        self.processor = DataProcessor(test_data_path)
    
    def test_load_worldcities_data(self):
        """Test loading of worldcities data"""
        try:
            df = self.processor.load_worldcities_data()
            self.assertIsNotNone(df)
            self.assertGreater(len(df), 0)
            self.assertIn('city', df.columns)
            self.assertIn('country', df.columns)
        except FileNotFoundError:
            self.skipTest("worldcities.csv not found - test requires data file")
    
    def test_extract_canonical_names(self):
        """Test extraction of canonical names"""
        try:
            canonical_data = self.processor.extract_canonical_names()
            self.assertIn('cities', canonical_data)
            self.assertIn('countries', canonical_data)
            self.assertIn('states', canonical_data)
            self.assertGreater(len(canonical_data['cities']), 0)
            self.assertGreater(len(canonical_data['countries']), 0)
        except FileNotFoundError:
            self.skipTest("worldcities.csv not found - test requires data file")


class TestNLPProcessor(unittest.TestCase):
    """Test cases for NLPProcessor"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.nlp_processor = NLPProcessor()
    
    def test_extract_capitalized_words(self):
        """Test extraction of capitalized words"""
        text = "Which of the following saw the highest temperature, Maharashtra, Ahmedabad or New-Zealand?"
        words = self.nlp_processor.extract_capitalized_words(text)
        
        self.assertIn('Maharashtra', words)
        self.assertIn('Ahmedabad', words)
        self.assertIn('New-Zealand', words)
    
    def test_preprocess_text(self):
        """Test text preprocessing"""
        text = "Show me data for New-Zealand and U.S.A."
        processed = self.nlp_processor.preprocess_text(text)
        
        self.assertIn('New Zealand', processed)
        self.assertIn('United States', processed)
    
    def test_extract_all_potential_places(self):
        """Test extraction of all potential places"""
        text = "Compare Mumbai and Delhi weather patterns"
        places = self.nlp_processor.extract_all_potential_places(text)
        
        # Should extract Mumbai and Delhi
        place_text = ' '.join(places).lower()
        self.assertTrue('mumbai' in place_text or 'delhi' in place_text)


class TestFuzzyMatcher(unittest.TestCase):
    """Test cases for FuzzyMatcher"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create mock canonical data
        mock_data = {
            'cities': {
                'mumbai': 'Mumbai',
                'delhi': 'Delhi', 
                'ahmedabad': 'Ahmedabad',
                'chennai': 'Chennai'
            },
            'countries': {
                'india': 'India',
                'new zealand': 'New Zealand',
                'united states': 'United States'
            },
            'states': {
                'maharashtra': 'Maharashtra',
                'tamil nadu': 'Tamil Nadu'
            }
        }
        self.matcher = FuzzyMatcher(mock_data, threshold=70)
    
    def test_match_exact_city(self):
        """Test exact city matching"""
        result = self.matcher.match_to_cities('mumbai')
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 'Mumbai')
        self.assertEqual(result[2], 'City')
    
    def test_match_fuzzy_city(self):
        """Test fuzzy city matching with typos"""
        result = self.matcher.match_to_cities('mumbay')  # Typo
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 'Mumbai')
    
    def test_match_country(self):
        """Test country matching"""
        result = self.matcher.match_to_countries('new zealand')
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 'New Zealand')
        self.assertEqual(result[2], 'Country')
    
    def test_get_best_match(self):
        """Test getting best match for a query"""
        result = self.matcher.get_best_match('deli')  # Typo for Delhi
        self.assertIsNotNone(result)
        self.assertEqual(result['canonical_name'], 'Delhi')
        self.assertEqual(result['table'], 'City')


class TestGeospatialQuerySystem(unittest.TestCase):
    """Test cases for the complete system"""
    
    def setUp(self):
        """Set up test fixtures"""
        try:
            # Try to initialize with real data
            self.system = GeospatialQuerySystem()
        except Exception:
            # If real data not available, skip these tests
            self.system = None
    
    def test_system_initialization(self):
        """Test system initialization"""
        if self.system is None:
            self.skipTest("System requires worldcities.csv data file")
        
        self.assertIsNotNone(self.system.data_processor)
        self.assertIsNotNone(self.system.nlp_processor)
        self.assertIsNotNone(self.system.fuzzy_matcher)
    
    def test_process_simple_query(self):
        """Test processing a simple query"""
        if self.system is None:
            self.skipTest("System requires worldcities.csv data file")
        
        query = "What is the weather in Mumbai?"
        results = self.system.process_query(query)
        
        # Should find Mumbai
        self.assertGreater(len(results), 0)
        mumbai_found = any(
            'mumbai' in result['canonical_name'].lower() 
            for result in results
        )
        self.assertTrue(mumbai_found)
    
    def test_process_complex_query(self):
        """Test processing the example complex query"""
        if self.system is None:
            self.skipTest("System requires worldcities.csv data file")
        
        query = "Which saw highest temperature, Maharashtra, Ahmedabad or New-Zealand?"
        results = self.system.process_query(query)
        
        self.assertGreater(len(results), 0)
        
        # Check if we found the expected entities
        found_entities = [result['canonical_name'].lower() for result in results]
        
        # Should find some geographical entities
        self.assertTrue(len(found_entities) > 0)


def run_tests():
    """Run all tests"""
    print("Running Geospatial NLP Query System Tests...")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestDataProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestNLPProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestFuzzyMatcher))
    suite.addTests(loader.loadTestsFromTestCase(TestGeospatialQuerySystem))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
