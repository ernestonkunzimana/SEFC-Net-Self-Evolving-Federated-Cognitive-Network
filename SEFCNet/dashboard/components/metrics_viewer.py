"""Metrics visualization component for the dashboard."""
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List

class MetricsViewer:
    def __init__(self):
        self.figure_template = "plotly_dark"
        
    def create_metrics_dashboard(self, history: Dict) -> None:
        """Create a comprehensive metrics dashboard."""
        if not history:
            st.warning("No metrics history available")
            return
            
        # Create main metrics figure
        fig = self.create_main_metrics_figure(history)
        st.plotly_chart(fig, use_container_width=True)
        
        # Create detailed metrics
        self.show_detailed_metrics(history)
        
    def create_main_metrics_figure(self, history: Dict) -> go.Figure:
        """Create the main metrics visualization figure."""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                "Training Accuracy",
                "Validation Accuracy",
                "Loss Progression",
                "Client Performance"
            )
        )
        
        # Add training accuracy
        if "metrics_distributed_fit" in history:
            train_acc = history["metrics_distributed_fit"].get("train_accuracy", [])
            if train_acc:
                rounds = [m[0] for m in train_acc]
                accuracies = [m[1] for m in train_acc]
                
                fig.add_trace(
                    go.Scatter(
                        x=rounds,
                        y=accuracies,
                        mode='lines+markers',
                        name='Training Accuracy',
                        line=dict(color='#00CC96')
                    ),
                    row=1, col=1
                )
                
        # Add validation accuracy
        if "metrics_distributed" in history:
            val_acc = history["metrics_distributed"].get("accuracy", [])
            if val_acc:
                rounds = [m[0] for m in val_acc]
                accuracies = [m[1] for m in val_acc]
                
                fig.add_trace(
                    go.Scatter(
                        x=rounds,
                        y=accuracies,
                        mode='lines+markers',
                        name='Validation Accuracy',
                        line=dict(color='#EF553B')
                    ),
                    row=1, col=2
                )
                
        # Add loss progression
        if "losses_distributed" in history:
            losses = history["losses_distributed"]
            if losses:
                rounds = [m[0] for m in losses]
                loss_values = [m[1] for m in losses]
                
                fig.add_trace(
                    go.Scatter(
                        x=rounds,
                        y=loss_values,
                        mode='lines+markers',
                        name='Loss',
                        line=dict(color='#636EFA')
                    ),
                    row=2, col=1
                )
                
        # Add client performance distribution
        if "metrics_distributed_fit" in history:
            client_metrics = history["metrics_distributed_fit"].get("train_accuracy", [])
            if client_metrics:
                client_accuracies = [m[1] for m in client_metrics]
                
                fig.add_trace(
                    go.Box(
                        y=client_accuracies,
                        name='Client Accuracies',
                        boxpoints='all',
                        jitter=0.3,
                        pointpos=-1.8
                    ),
                    row=2, col=2
                )
                
        # Update layout
        fig.update_layout(
            height=800,
            showlegend=True,
            template=self.figure_template,
            title_text="Federated Learning Metrics Dashboard",
            title_x=0.5
        )
        
        return fig
        
    def show_detailed_metrics(self, history: Dict) -> None:
        """Display detailed metrics and statistics."""
        # Calculate and display aggregate statistics
        if "metrics_distributed" in history:
            final_accuracy = history["metrics_distributed"]["accuracy"][-1][1]
            accuracy_progression = [m[1] for m in history["metrics_distributed"]["accuracy"]]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Final Accuracy",
                    f"{final_accuracy:.4f}",
                    f"{final_accuracy - accuracy_progression[-2]:.4f}"
                )
                
            with col2:
                st.metric(
                    "Best Accuracy",
                    f"{max(accuracy_progression):.4f}"
                )
                
            with col3:
                st.metric(
                    "Accuracy Stability",
                    f"{np.std(accuracy_progression):.4f}"
                )
                
        # Display convergence analysis
        with st.expander("📈 Convergence Analysis", expanded=False):
            if "losses_distributed" in history:
                losses = [l[1] for l in history["losses_distributed"]]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    y=losses,
                    mode='lines',
                    name='Loss'
                ))
                
                fig.update_layout(
                    title="Loss Convergence",
                    xaxis_title="Round",
                    yaxis_title="Loss",
                    template=self.figure_template
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
        # Display client performance analysis
        with st.expander("👥 Client Performance Analysis", expanded=False):
            if "metrics_distributed_fit" in history:
                client_metrics = history["metrics_distributed_fit"].get("train_accuracy", [])
                if client_metrics:
                    df = pd.DataFrame(client_metrics, columns=['round', 'accuracy'])
                    
                    fig = px.box(
                        df,
                        y='accuracy',
                        title="Client Performance Distribution"
                    )
                    
                    fig.update_layout(template=self.figure_template)
                    st.plotly_chart(fig, use_container_width=True)