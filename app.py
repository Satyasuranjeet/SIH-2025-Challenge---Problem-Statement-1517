"""
Streamlit Web Interface for Geospatial NLP Query System
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
import json

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

try:
    from src.geospatial_query_system import GeospatialQuerySystem
except ImportError:
    # Fallback if running from different directory
    from geospatial_query_system import GeospatialQuerySystem


def main():
    """
    Main Streamlit application
    """
    st.set_page_config(
        page_title="Geospatial NLP Query System",
        page_icon="🌍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Title and description
    st.title("🌍 Geospatial NLP Query System")
    st.markdown("""
    **A Smart System for Extracting Geographic Entities from Natural Language**
    
    This system uses advanced NLP techniques and fuzzy matching to identify and map place names 
    in natural language queries to canonical geographical entities.
    """)
    
    # Initialize session state
    if 'system' not in st.session_state:
        with st.spinner("Initializing system... Please wait"):
            try:
                st.session_state.system = GeospatialQuerySystem()
                st.success("System initialized successfully!")
            except Exception as e:
                st.error(f"Failed to initialize system: {e}")
                st.stop()
    
    # Sidebar with system information
    with st.sidebar:
        st.header("📊 System Information")
        
        if hasattr(st.session_state.system, 'data_processor'):
            stats = st.session_state.system.data_processor.get_data_stats()
            st.metric("Total Cities", f"{stats['total_cities']:,}")
            st.metric("Unique Countries", stats['unique_countries'])
            st.metric("Unique States/Regions", stats['unique_states'])
        
        st.header("⚙️ Settings")
        fuzzy_threshold = st.slider(
            "Fuzzy Matching Threshold", 
            min_value=50, 
            max_value=100, 
            value=80, 
            help="Minimum similarity score for matching (higher = more strict)"
        )
        
        # Update threshold if changed
        if hasattr(st.session_state.system, 'fuzzy_matcher'):
            st.session_state.system.fuzzy_matcher.threshold = fuzzy_threshold
        
        st.header("📝 Example Queries")
        examples = [
            "Which of the following saw the highest average temperature in January, Maharashtra, Ahmedabad or entire New-Zealand?",
            "Show me a graph of rainfall for Chennai for the month of October",
            "Compare weather patterns between Mumbai, Delhi, and Bangalore",
            "What is the population of New York City and Los Angeles?",
            "Tell me about the climate in Mumbay and Deli"
        ]
        
        for i, example in enumerate(examples):
            if st.button(f"Example {i+1}", key=f"example_{i}"):
                st.session_state.query_input = example
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🔍 Query Input")
        
        # Get query from session state or default
        default_query = st.session_state.get('query_input', '')
        
        query = st.text_area(
            "Enter your natural language query:",
            value=default_query,
            height=100,
            placeholder="e.g., Which city has higher rainfall, Mumbai or Chennai?"
        )
        
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            process_btn = st.button("🚀 Process Query", type="primary")
        
        with col_btn2:
            detailed_btn = st.button("📋 Detailed Analysis")
        
        with col_btn3:
            clear_btn = st.button("🗑️ Clear")
        
        if clear_btn:
            st.session_state.query_input = ''
            st.rerun()
    
    with col2:
        st.header("📈 Quick Stats")
        
        # Placeholder for quick stats
        stats_placeholder = st.empty()
    
    # Process query
    if process_btn or detailed_btn:
        if not query.strip():
            st.warning("Please enter a query first.")
        else:
            with st.spinner("Processing query..."):
                try:
                    # Process the query
                    results = st.session_state.system.process_query(
                        query, 
                        detailed=detailed_btn
                    )
                    
                    if not results:
                        st.warning("No geographical entities found in your query.")
                    else:
                        # Display results
                        st.header("🎯 Results")
                        
                        # Create tabs for different views
                        tab1, tab2, tab3, tab4 = st.tabs(["📋 Summary", "📊 Detailed View", "🗺️ Map", "📁 Raw Data"])
                        
                        with tab1:
                            st.subheader("Extracted Geographical Entities")
                            
                            for i, result in enumerate(results, 1):
                                with st.container():
                                    col_token, col_canonical, col_table, col_confidence = st.columns(4)
                                    
                                    with col_token:
                                        st.write(f"**Token:** {result['token']}")
                                    
                                    with col_canonical:
                                        st.write(f"**Canonical:** {result['canonical_name']}")
                                    
                                    with col_table:
                                        st.write(f"**Type:** {result['table']}")
                                    
                                    with col_confidence:
                                        confidence = result['confidence_score']
                                        color = "green" if confidence >= 90 else "orange" if confidence >= 70 else "red"
                                        st.write(f"**Confidence:** <span style='color:{color}'>{confidence:.1f}%</span>", unsafe_allow_html=True)
                                    
                                    st.divider()
                        
                        with tab2:
                            st.subheader("Detailed Analysis")
                            
                            # Create a dataframe for better display
                            df_results = pd.DataFrame(results)
                            
                            # Display as a styled table
                            st.dataframe(
                                df_results[['token', 'canonical_name', 'table', 'confidence_score']],
                                use_container_width=True,
                                hide_index=True
                            )
                            
                            # Confidence distribution
                            if len(results) > 1:
                                fig_conf = px.bar(
                                    df_results, 
                                    x='token', 
                                    y='confidence_score',
                                    color='table',
                                    title="Confidence Scores by Entity"
                                )
                                st.plotly_chart(fig_conf, use_container_width=True)
                        
                        with tab3:
                            st.subheader("Geographic Distribution")
                            
                            # Try to create a simple map if we have city data
                            cities_in_results = [r for r in results if r['table'] == 'City']
                            
                            if cities_in_results:
                                st.write(f"Found {len(cities_in_results)} cities in your query")
                                
                                # You could integrate with actual coordinates here
                                # For now, just show a placeholder
                                st.info("Map visualization would show the locations of identified cities on a world map.")
                            else:
                                st.info("No cities found for map visualization.")
                        
                        with tab4:
                            st.subheader("Raw JSON Data")
                            st.json(results)
                        
                        # Update quick stats
                        with stats_placeholder.container():
                            col_s1, col_s2, col_s3 = st.columns(3)
                            
                            with col_s1:
                                st.metric("Entities Found", len(results))
                            
                            with col_s2:
                                avg_confidence = sum(r['confidence_score'] for r in results) / len(results)
                                st.metric("Avg Confidence", f"{avg_confidence:.1f}%")
                            
                            with col_s3:
                                entity_types = len(set(r['table'] for r in results))
                                st.metric("Entity Types", entity_types)
                
                except Exception as e:
                    st.error(f"Error processing query: {e}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p>🏆 Built for SIH 2025 - Team SIH1517 | Geospatial NLP Query System</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
