#!/bin/bash

# Setup script for Geospatial NLP Query System
# This script installs all required dependencies and sets up the environment

echo "Setting up Geospatial NLP Query System..."
echo "========================================"

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "Error: Python is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
python_version=$(python -c "import sys; print(sys.version_info[:2])")
echo "Python version: $python_version"

# Create virtual environment (optional but recommended)
echo "Creating virtual environment..."
python -m venv venv

# Activate virtual environment
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows (Git Bash)
    source venv/Scripts/activate
else
    # Linux/Mac
    source venv/bin/activate
fi

echo "Virtual environment activated."

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install requirements
echo "Installing Python packages..."
pip install -r requirements.txt

# Download spaCy model
echo "Downloading spaCy English model..."
python -m spacy download en_core_web_sm

# Download NLTK data
echo "Downloading NLTK data..."
python -c "
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
print('NLTK data downloaded successfully!')
"

# Check if worldcities.csv exists
if [ ! -f "data/worldcities.csv" ]; then
    echo "Warning: worldcities.csv not found in data/ directory."
    echo "Please ensure the file is present before running the system."
else
    echo "worldcities.csv found in data/ directory."
fi

echo ""
echo "Setup complete!"
echo "=============="
echo ""
echo "To run the system:"
echo "1. Command line interface: python src/geospatial_query_system.py"
echo "2. Web interface: streamlit run app.py"
echo "3. Run tests: python tests/test_system.py"
echo ""
echo "Note: Make sure to activate the virtual environment before running:"
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    echo "  source venv/Scripts/activate"
else
    echo "  source venv/bin/activate"
fi
