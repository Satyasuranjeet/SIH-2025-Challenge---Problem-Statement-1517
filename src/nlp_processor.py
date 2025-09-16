"""
NLP Processor Module for Geospatial NLP System
Handles natural language processing tasks for extracting place names
"""

import re
import spacy
from typing import List, Tuple, Set
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.chunk import ne_chunk
from nltk.tree import Tree


class NLPProcessor:
    """
    Handles NLP tasks for extracting geographical entities from text
    """
    
    def __init__(self):
        """
        Initialize the NLP processor with required models
        """
        self.nlp = None
        self.setup_models()
    
    def setup_models(self):
        """
        Setup and download required NLP models
        """
        try:
            # Try to load spaCy model
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("spaCy English model not found. Please install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('taggers/averaged_perceptron_tagger')
        except LookupError:
            nltk.download('averaged_perceptron_tagger')
        
        try:
            nltk.data.find('chunkers/maxent_ne_chunker')
        except LookupError:
            nltk.download('maxent_ne_chunker')
        
        try:
            nltk.data.find('corpora/words')
        except LookupError:
            nltk.download('words')
    
    def extract_potential_places_spacy(self, text: str) -> List[str]:
        """
        Extract potential place names using spaCy NER
        
        Args:
            text: Input text to process
            
        Returns:
            List of potential place names
        """
        if self.nlp is None:
            return []
        
        doc = self.nlp(text)
        places = []
        
        for ent in doc.ents:
            # Extract geographical entities
            if ent.label_ in ['GPE', 'LOC']:  # Geopolitical entities and locations
                places.append(ent.text.strip())
        
        return places
    
    def extract_potential_places_nltk(self, text: str) -> List[str]:
        """
        Extract potential place names using NLTK NER
        
        Args:
            text: Input text to process
            
        Returns:
            List of potential place names
        """
        # Tokenize and tag
        tokens = word_tokenize(text)
        pos_tags = pos_tag(tokens)
        
        # Named entity recognition
        chunks = ne_chunk(pos_tags)
        
        places = []
        for chunk in chunks:
            if isinstance(chunk, Tree):
                if chunk.label() in ['GPE', 'LOCATION']:
                    # Extract the entity text
                    entity = ' '.join([token for token, pos in chunk.leaves()])
                    places.append(entity)
        
        return places
    
    def extract_capitalized_words(self, text: str) -> List[str]:
        """
        Extract capitalized words that might be place names
        
        Args:
            text: Input text to process
            
        Returns:
            List of capitalized words
        """
        # Pattern to match capitalized words (including hyphenated ones)
        pattern = r'\b[A-Z][a-zA-Z\-]+(?:\s+[A-Z][a-zA-Z\-]+)*\b'
        matches = re.findall(pattern, text)
        
        # Filter out common non-place words
        stop_words = {
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December',
            'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
            'Which', 'Show', 'The', 'This', 'That', 'These', 'Those', 'And', 'Or', 'But',
            'A', 'An', 'As', 'At', 'By', 'For', 'From', 'In', 'Into', 'Of', 'On', 'To',
            'With', 'Without', 'Graph', 'Chart', 'Temperature', 'Rainfall', 'Average'
        }
        
        filtered_matches = [match for match in matches if match not in stop_words]
        return filtered_matches
    
    def extract_all_potential_places(self, text: str) -> List[str]:
        """
        Extract all potential place names using multiple methods
        
        Args:
            text: Input text to process
            
        Returns:
            Combined list of potential place names
        """
        all_places = []
        
        # Method 1: spaCy NER
        if self.nlp:
            spacy_places = self.extract_potential_places_spacy(text)
            all_places.extend(spacy_places)
        
        # Method 2: NLTK NER
        nltk_places = self.extract_potential_places_nltk(text)
        all_places.extend(nltk_places)
        
        # Method 3: Capitalized words
        cap_words = self.extract_capitalized_words(text)
        all_places.extend(cap_words)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_places = []
        for place in all_places:
            place_clean = place.strip()
            if place_clean and place_clean not in seen:
                seen.add(place_clean)
                unique_places.append(place_clean)
        
        return unique_places
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text for better extraction
        
        Args:
            text: Input text to preprocess
            
        Returns:
            Preprocessed text
        """
        # Basic cleaning
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single space
        text = text.strip()
        
        # Handle common variations
        text = re.sub(r'New-Zealand', 'New Zealand', text, flags=re.IGNORECASE)
        text = re.sub(r'U\.S\.A\.?', 'United States', text, flags=re.IGNORECASE)
        text = re.sub(r'U\.K\.?', 'United Kingdom', text, flags=re.IGNORECASE)
        
        return text
