#!/usr/bin/env python3
"""
Quick test script to demonstrate the Geospatial NLP Query System
"""

import sys
import os

# Add src directory to path
sys.path.append('src')

try:
    from geospatial_query_system import GeospatialQuerySystem
    
    print("🌍 GEOSPATIAL NLP QUERY SYSTEM - QUICK TEST")
    print("=" * 50)
    
    # Initialize system
    print("Initializing system...")
    system = GeospatialQuerySystem()
    print("✅ System initialized successfully!")
    
    # Test queries
    test_queries = [
        "Which city has better weather, Mumbai or Chennai?",
        "Show rainfall data for Delhi and Bangalore",
        "Compare temperature in Maharashtra and Gujarat states",
        "What about weather in New-Zealand?"
    ]
    
    print("\n🧪 RUNNING TEST QUERIES")
    print("=" * 30)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        print("   Results:")
        
        try:
            results = system.process_query(query)
            if results:
                for result in results:
                    print(f"   • {result['token']} → {result['canonical_name']} ({result['table']})")
            else:
                print("   • No geographical entities found")
        except Exception as e:
            print(f"   • Error: {e}")
    
    print(f"\n✅ All tests completed successfully!")
    print("🌐 Web interface is running at: http://localhost:8501")
    print("📝 Try more queries in the web interface!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("Please check that all dependencies are installed.")
    sys.exit(1)
