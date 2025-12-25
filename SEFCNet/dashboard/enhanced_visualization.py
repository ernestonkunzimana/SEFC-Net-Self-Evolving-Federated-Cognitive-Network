from typing import Dict, Any
import streamlit as st
import plotly.express as px

class EnhancedDashboard:
    """Real-time visualization enhancements"""
    
    def __init__(self):
        self.metrics_cache = {}

    def plot_model_evolution(self, history: Dict[str, Any]):
        """Plot model architecture evolution over time"""
        st.line_chart(history["architecture_complexity"])
        
    def plot_federation_topology(self, topology: Dict[str, Any]):
        """Interactive federation topology visualization"""
        # Create network graph
        fig = px.scatter(topology, hover_data=["node_type", "status"])
        st.plotly_chart(fig)

    def render_performance_metrics(self, metrics: Dict[str, Any]):
        """Real-time performance metrics display"""
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Global Model Accuracy", f"{metrics['accuracy']:.2f}%")
        with col2:
            st.metric("Training Time", f"{metrics['time']:.1f}s")