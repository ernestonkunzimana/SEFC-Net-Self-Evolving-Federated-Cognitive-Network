"""
Enterprise-grade dashboard components for advanced visualization and monitoring
"""
from typing import Dict, List, Optional, Any, Callable
import asyncio
from datetime import datetime

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np

from .config import DashboardConfig
from ..utils.metrics import MetricsCollector
from ..utils.logger import get_logger
from ..models.base_model import ModelMetrics
from ..analytics.analytics_manager import analytics_manager

logger = get_logger(__name__)

class DashboardComponents:
    """Enterprise dashboard components with real-time updates and interactivity"""
    
    def __init__(self, config: DashboardConfig):
        self.config = config
        self.metrics_collector = MetricsCollector()
        
    def create_header(self) -> html.Div:
        """Create dashboard header with navigation and controls"""
        return html.Div([
            dbc.NavbarSimple(
                children=[
                    dbc.NavItem(dbc.NavLink("Overview", href="/overview")),
                    dbc.NavItem(dbc.NavLink("Models", href="/models")),
                    dbc.NavItem(dbc.NavLink("Analytics", href="/analytics")),
                    dbc.NavItem(dbc.NavLink("Explainability", href="/xai")),
                    dbc.DropdownMenu(
                        children=[
                            dbc.DropdownMenuItem("Settings", href="/settings"),
                            dbc.DropdownMenuItem("Profile", href="/profile"),
                            dbc.DropdownMenuItem("Logout", href="/logout"),
                        ],
                        nav=True,
                        in_navbar=True,
                        label="More",
                    ),
                ],
                brand="SEFCNet Enterprise Dashboard",
                brand_href="/",
                color="primary",
                dark=True,
            )
        ])
    
    def create_metrics_panel(self) -> html.Div:
        """Create real-time metrics panel"""
        return html.Div([
            dbc.Card([
                dbc.CardHeader("System Metrics"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H4("CPU Usage"),
                            dcc.Graph(id="cpu-gauge"),
                        ], width=4),
                        dbc.Col([
                            html.H4("Memory Usage"),
                            dcc.Graph(id="memory-gauge"),
                        ], width=4),
                        dbc.Col([
                            html.H4("Network I/O"),
                            dcc.Graph(id="network-chart"),
                        ], width=4),
                    ]),
                    dcc.Interval(
                        id='metrics-update',
                        interval=self.config.UPDATE_INTERVAL,
                        n_intervals=0
                    )
                ])
            ])
        ])
    
    def create_model_performance(self) -> html.Div:
        """Create model performance visualization panel"""
        return html.Div([
            dbc.Card([
                dbc.CardHeader("Model Performance"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H4("Accuracy Trends"),
                            dcc.Graph(id="accuracy-chart"),
                        ], width=6),
                        dbc.Col([
                            html.H4("Loss Trends"),
                            dcc.Graph(id="loss-chart"),
                        ], width=6),
                    ]),
                    dbc.Row([
                        dbc.Col([
                            html.H4("Model Comparison"),
                            dcc.Graph(id="model-comparison"),
                        ], width=12),
                    ]),
                    dcc.Interval(
                        id='performance-update',
                        interval=self.config.UPDATE_INTERVAL * 2,
                        n_intervals=0
                    )
                ])
            ])
        ])
    
    def create_xai_panel(self) -> html.Div:
        """Create explainable AI visualization panel"""
        return html.Div([
            dbc.Card([
                dbc.CardHeader("Model Explainability"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H4("Feature Importance"),
                            dcc.Graph(id="feature-importance"),
                        ], width=6),
                        dbc.Col([
                            html.H4("SHAP Values"),
                            dcc.Graph(id="shap-summary"),
                        ], width=6),
                    ]),
                    dbc.Row([
                        dbc.Col([
                            html.H4("Decision Boundary"),
                            dcc.Graph(id="decision-boundary"),
                        ], width=12),
                    ])
                ])
            ])
        ])
    
    def create_alerts_panel(self) -> html.Div:
        """Create real-time alerts and notifications panel"""
        return html.Div([
            dbc.Card([
                dbc.CardHeader("System Alerts"),
                dbc.CardBody([
                    html.Div(id="alerts-container"),
                    dcc.Interval(
                        id='alerts-update',
                        interval=self.config.UPDATE_INTERVAL,
                        n_intervals=0
                    )
                ])
            ])
        ])
    
    async def update_metrics(self, n_intervals: int) -> List[go.Figure]:
        """Update system metrics visualizations"""
        try:
            metrics = await self.metrics_collector.get_current_metrics()
            
            cpu_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=metrics["cpu_usage"],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "CPU Usage %"}
            ))
            
            memory_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=metrics["memory_usage"],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Memory Usage %"}
            ))
            
            network_chart = go.Figure([
                go.Scatter(
                    x=metrics["timestamp"],
                    y=metrics["network_in"],
                    name="Network In"
                ),
                go.Scatter(
                    x=metrics["timestamp"],
                    y=metrics["network_out"],
                    name="Network Out"
                )
            ])
            
            return [cpu_gauge, memory_gauge, network_chart]
        except Exception as e:
            logger.error(f"Error updating metrics: {str(e)}")
            return []
    
    async def update_performance(self, n_intervals: int) -> List[go.Figure]:
        """Update model performance visualizations"""
        try:
            performance = await analytics_manager.get_performance_metrics()
            
            accuracy_chart = px.line(
                performance["accuracy"],
                title="Model Accuracy Over Time"
            )
            
            loss_chart = px.line(
                performance["loss"],
                title="Model Loss Over Time"
            )
            
            comparison = px.bar(
                performance["comparison"],
                title="Model Performance Comparison"
            )
            
            return [accuracy_chart, loss_chart, comparison]
        except Exception as e:
            logger.error(f"Error updating performance charts: {str(e)}")
            return []
    
    def register_callbacks(self, app: dash.Dash) -> None:
        """Register all dashboard callbacks"""
        
        @app.callback(
            [Output("cpu-gauge", "figure"),
             Output("memory-gauge", "figure"),
             Output("network-chart", "figure")],
            [Input("metrics-update", "n_intervals")]
        )
        def update_system_metrics(n_intervals):
            return asyncio.run(self.update_metrics(n_intervals))
        
        @app.callback(
            [Output("accuracy-chart", "figure"),
             Output("loss-chart", "figure"),
             Output("model-comparison", "figure")],
            [Input("performance-update", "n_intervals")]
        )
        def update_model_metrics(n_intervals):
            return asyncio.run(self.update_performance(n_intervals))
        
        @app.callback(
            Output("alerts-container", "children"),
            [Input("alerts-update", "n_intervals")]
        )
        def update_alerts(n_intervals):
            alerts = self.metrics_collector.get_alerts()
            return [
                dbc.Alert(
                    alert["message"],
                    color=alert["severity"],
                    dismissable=True
                ) for alert in alerts
            ]