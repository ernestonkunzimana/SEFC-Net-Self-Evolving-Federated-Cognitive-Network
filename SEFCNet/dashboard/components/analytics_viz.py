import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, List

class AnalyticsVisualizer:
    def __init__(self):
        self.client_metrics = {}
        
    def update_analytics(self, client_metrics: Dict[str, List[float]]):
        """Update client analytics data"""
        self.client_metrics = client_metrics
        
    def render_analytics(self, tab):
        """Render analytics visualizations"""
        with tab:
            st.markdown("### Client Performance Analytics")
            
            if self.client_metrics:
                # Convert to DataFrame
                df = pd.DataFrame(self.client_metrics)
                
                # Client comparison
                fig1 = px.bar(
                    df.mean(),
                    title='Average Client Performance',
                    labels={'value': 'Accuracy', 'index': 'Client ID'}
                )
                st.plotly_chart(fig1, use_container_width=True)
                
                # Performance distribution
                fig2 = px.box(
                    df.melt(),
                    x='variable',
                    y='value',
                    title='Performance Distribution by Client',
                    labels={'value': 'Accuracy', 'variable': 'Client ID'}
                )
                st.plotly_chart(fig2, use_container_width=True)
                
                # Correlation heatmap
                fig3 = px.imshow(
                    df.corr(),
                    title='Client Performance Correlation',
                    labels={'color': 'Correlation'}
                )
                st.plotly_chart(fig3, use_container_width=True)