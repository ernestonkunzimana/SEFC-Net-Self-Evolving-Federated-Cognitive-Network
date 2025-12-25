import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, List

class PerformanceMonitor:
    def __init__(self):
        self.metrics_history = pd.DataFrame()
        
    def update_metrics(self, metrics: Dict[str, float]):
        """Update metrics history"""
        self.metrics_history = pd.concat([
            self.metrics_history,
            pd.DataFrame([metrics])
        ]).reset_index(drop=True)
        
    def render_metrics(self, tab):
        """Render performance metrics"""
        with tab:
            # Key metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                self._render_metric_card(
                    "Global Accuracy",
                    f"{self.metrics_history['accuracy'].iloc[-1]:.2f}%",
                    "↑" if len(self.metrics_history) > 1 and 
                    self.metrics_history['accuracy'].iloc[-1] > 
                    self.metrics_history['accuracy'].iloc[-2] else "↓"
                )
            with col2:
                self._render_metric_card(
                    "Active Clients",
                    f"{self.metrics_history['active_clients'].iloc[-1]}",
                    ""
                )
            with col3:
                self._render_metric_card(
                    "Training Round",
                    f"{len(self.metrics_history)}",
                    ""
                )
                
            # Performance charts
            self._render_performance_charts()
            
    def _render_metric_card(self, title: str, value: str, delta: str):
        """Render a metric card"""
        st.metric(title, value, delta)
        
    def _render_performance_charts(self):
        """Render performance visualization charts"""
        if len(self.metrics_history) > 1:
            # Accuracy over time
            fig = px.line(
                self.metrics_history,
                x=self.metrics_history.index,
                y=['accuracy', 'train_accuracy'],
                title='Model Performance Over Time'
            )
            st.plotly_chart(fig, use_container_width=True)