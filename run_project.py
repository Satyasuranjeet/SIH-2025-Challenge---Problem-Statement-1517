"""
Project Launcher for Geospatial NLP Query System
This script helps run different components of the system
"""

import os
import sys
import subprocess
import argparse


def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ['pandas', 'spacy', 'rapidfuzz', 'nltk', 'streamlit']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages


def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("Dependencies installed successfully!")
        
        # Download spaCy model
        print("Downloading spaCy model...")
        subprocess.check_call([sys.executable, '-m', 'spacy', 'download', 'en_core_web_sm'])
        print("spaCy model downloaded!")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False


def run_demo():
    """Run the simplified demo"""
    print("Running simplified demo...")
    try:
        subprocess.run([sys.executable, 'demo.py'])
    except Exception as e:
        print(f"Error running demo: {e}")


def run_cli():
    """Run the command line interface"""
    missing = check_dependencies()
    if missing:
        print(f"Missing dependencies: {missing}")
        print("Please install dependencies first with: python run_project.py --install")
        return
    
    print("Running CLI interface...")
    try:
        subprocess.run([sys.executable, 'src/geospatial_query_system.py'])
    except Exception as e:
        print(f"Error running CLI: {e}")


def run_web():
    """Run the web interface"""
    missing = check_dependencies()
    if missing:
        print(f"Missing dependencies: {missing}")
        print("Please install dependencies first with: python run_project.py --install")
        return
    
    print("Starting web interface...")
    try:
        subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'app.py'])
    except Exception as e:
        print(f"Error running web interface: {e}")


def run_tests():
    """Run the test suite"""
    missing = check_dependencies()
    if missing:
        print(f"Missing dependencies: {missing}")
        print("Running basic tests without full dependencies...")
    
    print("Running tests...")
    try:
        subprocess.run([sys.executable, 'tests/test_system.py'])
    except Exception as e:
        print(f"Error running tests: {e}")


def show_project_info():
    """Display project information"""
    print("""
🌍 GEOSPATIAL NLP QUERY SYSTEM
==============================

This project implements a sophisticated NLP system for extracting and 
matching geographical entities from natural language queries.

FEATURES:
- Multi-method entity extraction (spaCy, NLTK, pattern matching)
- Fuzzy string matching for handling typos and variations
- Support for cities, countries, and states/regions
- Web interface with interactive visualization
- Command line interface for batch processing
- Comprehensive test suite

COMPONENTS:
- src/data_processor.py      : Data loading and preprocessing
- src/nlp_processor.py       : NLP entity extraction
- src/fuzzy_matcher.py       : Fuzzy string matching
- src/geospatial_query_system.py : Main system orchestrator
- app.py                     : Streamlit web interface
- demo.py                    : Simple demo (no dependencies)
- tests/test_system.py       : Test suite

DATA:
- data/worldcities.csv       : Geographical entities database
  (Contains cities, countries, and administrative regions)

USAGE EXAMPLES:
Query: "Which saw highest temperature, Maharashtra, Ahmedabad or New-Zealand?"
Output: 
  Token: Maharashtra, Canonical name: Maharashtra, Table: State
  Token: Ahmedabad, Canonical name: Ahmedabad, Table: City  
  Token: New-Zealand, Canonical name: New Zealand, Table: Country

Built for SIH 2025 - Problem Statement 1517
Team: SIH1517
""")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Geospatial NLP Query System Launcher')
    parser.add_argument('--install', action='store_true', help='Install dependencies')
    parser.add_argument('--demo', action='store_true', help='Run simple demo (no dependencies needed)')
    parser.add_argument('--cli', action='store_true', help='Run command line interface')
    parser.add_argument('--web', action='store_true', help='Run web interface')
    parser.add_argument('--test', action='store_true', help='Run test suite')
    parser.add_argument('--info', action='store_true', help='Show project information')
    
    args = parser.parse_args()
    
    # Change to project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    if args.install:
        install_dependencies()
    elif args.demo:
        run_demo()
    elif args.cli:
        run_cli()
    elif args.web:
        run_web()
    elif args.test:
        run_tests()
    elif args.info:
        show_project_info()
    else:
        # Default: show help and options
        print("🌍 GEOSPATIAL NLP QUERY SYSTEM")
        print("=" * 40)
        print("\nAvailable options:")
        print("  --install    Install all dependencies")
        print("  --demo       Run simple demo (works without dependencies)")
        print("  --cli        Run command line interface")
        print("  --web        Run web interface")
        print("  --test       Run test suite")
        print("  --info       Show detailed project information")
        print("\nQuick start:")
        print("1. python run_project.py --install")
        print("2. python run_project.py --web")
        print("\nOr try the demo:")
        print("   python run_project.py --demo")


if __name__ == "__main__":
    main()
