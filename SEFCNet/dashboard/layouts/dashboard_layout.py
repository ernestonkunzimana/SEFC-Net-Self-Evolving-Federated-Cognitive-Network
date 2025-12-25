"""Dashboard layout management."""
import streamlit as st
from typing import Dict, Any

def create_layout():
    """Create the main dashboard layout."""
    st.set_page_config(
        page_title="SEFCNet Analytics Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    # Apply custom CSS for dark theme and modern look
    st.markdown("""
        <style>
        .stApp {
            background-color: #0E1117;
            color: #FAFAFA;
        }
        .stMetric {
            background-color: #262730;
            padding: 10px;
            border-radius: 5px;
        }
        .stAlert {
            background-color: #1E1E1E;
            color: #FAFAFA;
            border: 1px solid #333;
            border-radius: 5px;
        }
        .stProgress .st-bo {
            background-color: #00CC96;
        }
        .stButton>button {
            background-color: #00CC96;
            color: #FAFAFA;
        }
        .stSelectbox {
            background-color: #262730;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Create sidebar
    with st.sidebar:
        st.header("⚙️ Dashboard Controls")
        
        # Visualization controls
        st.subheader("🎯 Display Options")
        show_confidence = st.checkbox("Show Confidence Intervals", value=True)
        aggregation = st.selectbox(
            "Metric Aggregation",
            ["Mean", "Median", "Max", "Min"]
        )
        
        # Update interval
        st.subheader("🔄 Updates")
        update_interval = st.slider(
            "Refresh Interval (seconds)",
            min_value=1,
            max_value=60,
            value=5
        )
        
        # Advanced options
        with st.expander("🛠️ Advanced Settings"):
            st.checkbox("Enable Real-time Monitoring", value=True)
            st.checkbox("Show Network Graph", value=True)
            st.checkbox("Enable Model Explainability", value=True)
            
        # Export options
        st.subheader("📤 Export Options")
        export_format = st.selectbox(
            "Export Format",
            ["JSON", "CSV", "Excel"]
        )
        if st.button("Export Data"):
            st.info("Exporting data...")
            
    return {
        "show_confidence": show_confidence,
        "aggregation": aggregation,
        "update_interval": update_interval,
        "export_format": export_format
    }