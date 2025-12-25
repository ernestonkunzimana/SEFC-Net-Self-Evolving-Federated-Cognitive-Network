import streamlit as st
import plotly.graph_objects as go
from typing import Dict, Any

def render_main_layout():
    """Main dashboard layout with tabs"""
    st.set_page_config(
        page_title="SEFCNet Dashboard",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Sidebar controls
    with st.sidebar:
        st.title("🧠 SEFCNet Controls")
        st.markdown("---")
        
        if st.button("Start Training", type="primary"):
            st.session_state.training = True
        
        if st.button("Stop Training", type="secondary"):
            st.session_state.training = False
            
        st.markdown("---")
        st.markdown("### Configuration")
        num_clients = st.slider("Number of Clients", 2, 10, 5)
        num_rounds = st.slider("Training Rounds", 5, 50, 10)
        
    # Main content
    tab1, tab2, tab3, tab4 = st.tabs([
        "Overview", "Network", "Performance", "Analytics"
    ])
    
    return tab1, tab2, tab3, tab4