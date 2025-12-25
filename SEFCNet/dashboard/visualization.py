"""
Visualization Components for SEFCNet
================================

This module provides advanced visualization components:
- Interactive charts and graphs
- Real-time data visualization
- ML model visualization
- Network topology visualization
- Performance analytics views
"""

from typing import Any, Dict, List, Optional, Tuple
import json
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from sklearn.manifold import TSNE
import networkx as nx
import shap

class ModelVisualization:
    """ML model visualization components."""

    @staticmethod
    def create_feature_importance_plot(
        importance_data: Dict[str, float],
        top_n: int = 10
    ) -> Dict[str, Any]:
        """Create feature importance visualization."""
        df = pd.DataFrame(
            importance_data.items(),
            columns=['feature', 'importance']
        ).sort_values('importance', ascending=True)
        
        if len(df) > top_n:
            df = df.tail(top_n)

        fig = go.Figure(
            go.Bar(
                x=df['importance'],
                y=df['feature'],
                orientation='h'
            )
        )

        fig.update_layout(
            title="Feature Importance",
            xaxis_title="Importance Score",
            yaxis_title="Feature",
            height=400
        )

        return json.loads(fig.to_json())

    @staticmethod
    def create_model_convergence_plot(
        history: List[Dict[str, float]]
    ) -> Dict[str, Any]:
        """Create model convergence visualization."""
        df = pd.DataFrame(history)
        
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['loss'],
                mode='lines',
                name='Training Loss'
            )
        )
        if 'val_loss' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['val_loss'],
                    mode='lines',
                    name='Validation Loss'
                )
            )

        fig.update_layout(
            title="Model Convergence",
            xaxis_title="Iteration",
            yaxis_title="Loss",
            height=400
        )

        return json.loads(fig.to_json())

    @staticmethod
    def create_shap_summary_plot(
        shap_values: np.ndarray,
        feature_names: List[str]
    ) -> Dict[str, Any]:
        """Create SHAP summary plot for model interpretability."""
        shap.initjs()
        fig = shap.summary_plot(
            shap_values,
            feature_names=feature_names,
            plot_type="bar",
            show=False
        )
        return json.loads(fig.to_json())

class NetworkVisualization:
    """Network topology and performance visualization."""

    @staticmethod
    def create_network_topology_plot(
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create network topology visualization."""
        G = nx.Graph()
        
        # Add nodes
        for node in nodes:
            G.add_node(
                node['id'],
                **{k: v for k, v in node.items() if k != 'id'}
            )

        # Add edges
        for edge in edges:
            G.add_edge(
                edge['source'],
                edge['target'],
                **{k: v for k, v in edge.items() if k not in ['source', 'target']}
            )

        # Create layout
        pos = nx.spring_layout(G)

        # Create node trace
        node_x = []
        node_y = []
        node_text = []
        node_color = []

        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(f"Node: {node}")
            node_color.append(G.nodes[node].get('status', 0))

        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            text=node_text,
            marker=dict(
                color=node_color,
                size=20,
                colorscale='Viridis'
            )
        )

        # Create edge trace
        edge_x = []
        edge_y = []

        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            mode='lines',
            line=dict(width=0.5, color='#888')
        )

        # Create figure
        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                title="Network Topology",
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                annotations=[],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )
        )

        return json.loads(fig.to_json())

    @staticmethod
    def create_latency_heatmap(
        latency_matrix: np.ndarray,
        node_labels: List[str]
    ) -> Dict[str, Any]:
        """Create network latency heatmap."""
        fig = go.Figure(
            data=go.Heatmap(
                z=latency_matrix,
                x=node_labels,
                y=node_labels,
                colorscale='Viridis'
            )
        )

        fig.update_layout(
            title="Network Latency Heatmap",
            xaxis_title="Target Node",
            yaxis_title="Source Node",
            height=400
        )

        return json.loads(fig.to_json())

class PerformanceVisualization:
    """System performance visualization components."""

    @staticmethod
    def create_resource_usage_plot(
        resource_data: Dict[str, List[float]],
        time_points: List[str]
    ) -> Dict[str, Any]:
        """Create resource usage visualization."""
        fig = go.Figure()

        for resource, values in resource_data.items():
            fig.add_trace(
                go.Scatter(
                    x=time_points,
                    y=values,
                    mode='lines',
                    name=resource
                )
            )

        fig.update_layout(
            title="Resource Usage Over Time",
            xaxis_title="Time",
            yaxis_title="Usage (%)",
            height=400
        )

        return json.loads(fig.to_json())

    @staticmethod
    def create_performance_dashboard(
        metrics: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Create comprehensive performance dashboard."""
        dashboard = []

        # CPU Usage
        if 'cpu' in metrics:
            cpu_fig = go.Figure(
                data=[
                    go.Indicator(
                        mode="gauge+number",
                        value=metrics['cpu']['average'],
                        title={'text': "CPU Usage"},
                        gauge={'axis': {'range': [0, 100]}}
                    )
                ]
            )
            dashboard.append({
                'title': 'CPU Usage',
                'plot': json.loads(cpu_fig.to_json())
            })

        # Memory Usage
        if 'memory' in metrics:
            memory_fig = go.Figure(
                data=[
                    go.Pie(
                        values=[
                            metrics['memory']['used_gb'],
                            metrics['memory']['total_gb'] - metrics['memory']['used_gb']
                        ],
                        labels=['Used', 'Available'],
                        hole=.3
                    )
                ]
            )
            dashboard.append({
                'title': 'Memory Usage',
                'plot': json.loads(memory_fig.to_json())
            })

        return dashboard

class DataVisualization:
    """Data analysis visualization components."""

    @staticmethod
    def create_distribution_plot(
        data: np.ndarray,
        title: str
    ) -> Dict[str, Any]:
        """Create distribution visualization."""
        fig = go.Figure(
            data=[
                go.Histogram(x=data, nbinsx=30)
            ]
        )

        fig.update_layout(
            title=title,
            xaxis_title="Value",
            yaxis_title="Count",
            height=400
        )

        return json.loads(fig.to_json())

    @staticmethod
    def create_correlation_matrix(
        df: pd.DataFrame
    ) -> Dict[str, Any]:
        """Create correlation matrix visualization."""
        corr_matrix = df.corr()

        fig = go.Figure(
            data=go.Heatmap(
                z=corr_matrix,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale='RdBu'
            )
        )

        fig.update_layout(
            title="Feature Correlation Matrix",
            height=600
        )

        return json.loads(fig.to_json())

    @staticmethod
    def create_tsne_plot(
        data: np.ndarray,
        labels: np.ndarray
    ) -> Dict[str, Any]:
        """Create t-SNE visualization for high-dimensional data."""
        tsne = TSNE(n_components=2, random_state=42)
        transformed_data = tsne.fit_transform(data)

        fig = go.Figure(
            data=go.Scatter(
                x=transformed_data[:, 0],
                y=transformed_data[:, 1],
                mode='markers',
                marker=dict(
                    color=labels,
                    colorscale='Viridis',
                    showscale=True
                )
            )
        )

        fig.update_layout(
            title="t-SNE Visualization",
            xaxis_title="Component 1",
            yaxis_title="Component 2",
            height=600
        )

        return json.loads(fig.to_json())