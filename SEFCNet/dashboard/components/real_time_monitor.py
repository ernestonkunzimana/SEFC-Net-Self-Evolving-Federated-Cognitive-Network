"""Real-time monitoring component for the dashboard."""
import streamlit as st
import time
from typing import Optional
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

class RealTimeMonitor:
    def __init__(self, update_interval: int):
        self.update_interval = update_interval
        self.last_update = datetime.now()
        self.metrics_history = []
        
    def update_metrics(self, metrics: dict):
        """Update metrics history with new data."""
        current_time = datetime.now()
        metrics['timestamp'] = current_time
        self.metrics_history.append(metrics)
        
        # Keep only last hour of data
        cutoff = current_time - timedelta(hours=1)
        self.metrics_history = [m for m in self.metrics_history if m['timestamp'] > cutoff]
        
    def create_realtime_chart(self) -> Optional[go.Figure]:
        """Create a real-time chart of metrics."""
        if not self.metrics_history:
            return None
            
        df = pd.DataFrame(self.metrics_history)
        
        fig = go.Figure()
        
        # Add traces for each metric
        for column in df.columns:
            if column != 'timestamp':
                fig.add_trace(go.Scatter(
                    x=df['timestamp'],
                    y=df[column],
                    name=column,
                    mode='lines+markers'
                ))
                
        fig.update_layout(
            title='Real-time Metrics',
            xaxis_title='Time',
            yaxis_title='Value',
            hovermode='x unified',
            template='plotly_dark'
        )
        
        return fig
        
    def display_metrics(self):
        """Display real-time metrics in the dashboard."""
        if time.time() - self.last_update.timestamp() >= self.update_interval:
            st.empty().text(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Create metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if self.metrics_history:
                    latest = self.metrics_history[-1]
                    st.metric(
                        "Accuracy",
                        f"{latest.get('accuracy', 0):.4f}",
                        f"{latest.get('accuracy_delta', 0):.4f}"
                    )
                    
            with col2:
                if self.metrics_history:
                    st.metric(
                        "Loss",
                        f"{latest.get('loss', 0):.4f}",
                        f"{latest.get('loss_delta', 0):.4f}"
                    )
                    
            with col3:
                if self.metrics_history:
                    st.metric(
                        "Active Clients",
                        latest.get('active_clients', 0)
                    )
            
            # Display real-time chart
            chart = self.create_realtime_chart()
            if chart:
                st.plotly_chart(chart, use_container_width=True)
                
            self.last_update = datetime.now()