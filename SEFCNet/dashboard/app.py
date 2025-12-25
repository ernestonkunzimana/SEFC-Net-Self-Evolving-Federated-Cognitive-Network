"""
Advanced Dashboard for SEFCNet
=============================
Enterprise-grade dashboard with real-time monitoring, explainability,
and interactive analytics.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

import dash
import dash_bootstrap_components as dbc
import mlflow
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dash import Input, Output, dcc, html
from dash.exceptions import PreventUpdate
from prometheus_client import CollectorRegistry, Counter, Gauge, start_http_server
from queue import Queue
import threading
import time

from .components.performance_monitor import PerformanceMonitor
from .components.network_viz import NetworkVisualizer
from .components.analytics_viz import AnalyticsVisualizer

# Initialize MLflow
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))
experiment = mlflow.set_experiment("federated_learning")

# Initialize Prometheus metrics
REGISTRY = CollectorRegistry()
model_accuracy = Gauge(
    "model_accuracy", "Current model accuracy", registry=REGISTRY
)
active_clients = Gauge(
    "active_clients", "Number of active federated clients", registry=REGISTRY
)
training_rounds = Counter(
    "training_rounds", "Number of completed training rounds", registry=REGISTRY
)

# Initialize Dash app with enterprise theme
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    title="SEFCNet Enterprise Dashboard",
)

# Layout components
header = dbc.Navbar(
    dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("SEFCNet Enterprise Dashboard", className="ms-2")),
        ],
        align="center",
        className="g-0",
        ),
    ]),
    dark=True,
    color="dark",
    sticky="top",
)

metrics_cards = dbc.Row([
    dbc.Col(
        dbc.Card([
            dbc.CardHeader("Global Model Accuracy"),
            dbc.CardBody(html.H3(id="accuracy-indicator")),
        ]),
        width=4,
    ),
    dbc.Col(
        dbc.Card([
            dbc.CardHeader("Active Clients"),
            dbc.CardBody(html.H3(id="clients-indicator")),
        ]),
        width=4,
    ),
    dbc.Col(
        dbc.Card([
            dbc.CardHeader("Training Rounds"),
            dbc.CardBody(html.H3(id="rounds-indicator")),
        ]),
        width=4,
    ),
])

performance_graphs = dbc.Row([
    dbc.Col([
        dbc.Card([
            dbc.CardHeader("Model Performance Over Time"),
            dbc.CardBody(dcc.Graph(id="performance-graph")),
        ]),
    ], width=12),
])

client_status = dbc.Row([
    dbc.Col([
        dbc.Card([
            dbc.CardHeader("Client Status"),
            dbc.CardBody(
                dash_table.DataTable(
                    id="client-table",
                    columns=[
                        {"name": "Client ID", "id": "client_id"},
                        {"name": "Status", "id": "status"},
                        {"name": "Last Update", "id": "last_update"},
                        {"name": "Local Accuracy", "id": "local_accuracy"},
                    ],
                    style_table={"overflowX": "auto"},
                    style_cell={
                        "backgroundColor": "rgb(50, 50, 50)",
                        "color": "white",
                    },
                    style_header={
                        "backgroundColor": "rgb(30, 30, 30)",
                        "color": "white",
                        "fontWeight": "bold",
                    },
                )
            ),
        ]),
    ], width=12),
])

explainability_section = dbc.Row([
    dbc.Col([
        dbc.Card([
            dbc.CardHeader("Model Explainability"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H5("Feature Importance"),
                        dcc.Graph(id="feature-importance"),
                    ], width=6),
                    dbc.Col([
                        html.H5("SHAP Values"),
                        dcc.Graph(id="shap-values"),
                    ], width=6),
                ]),
            ]),
        ]),
    ], width=12),
])

app.layout = dbc.Container([
    header,
    html.Br(),
    metrics_cards,
    html.Br(),
    performance_graphs,
    html.Br(),
    client_status,
    html.Br(),
    explainability_section,
    dcc.Interval(id="interval-component", interval=5000),
], fluid=True)

# Callbacks for real-time updates
@app.callback(
    [
        Output("accuracy-indicator", "children"),
        Output("clients-indicator", "children"),
        Output("rounds-indicator", "children"),
        Output("performance-graph", "figure"),
        Output("feature-importance", "figure"),
        Output("shap-values", "figure"),
        Output("client-table", "data"),
    ],
    Input("interval-component", "n_intervals"),
)
def update_metrics(n):
    if n is None:
        raise PreventUpdate

    # Get latest metrics from MLflow
    client = mlflow.tracking.MlflowClient()
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["attributes.start_time DESC"],
    )
    
    if not runs:
        raise PreventUpdate

    latest_run = runs[0]
    accuracy = latest_run.data.metrics.get("accuracy", 0)
    n_clients = latest_run.data.metrics.get("active_clients", 0)
    n_rounds = latest_run.data.metrics.get("training_rounds", 0)

    # Update Prometheus metrics
    model_accuracy.set(accuracy)
    active_clients.set(n_clients)
    training_rounds.inc()

    # Performance graph
    metrics_history = pd.DataFrame([
        {
            "round": m.step,
            "accuracy": m.value,
            "metric": "accuracy",
        }
        for run in runs
        for m in client.get_metric_history(run.info.run_id, "accuracy")
    ])

    perf_fig = px.line(
        metrics_history,
        x="round",
        y="accuracy",
        title="Model Performance History",
    )

    # Feature importance
    feature_imp = pd.DataFrame({
        "feature": ["f1", "f2", "f3", "f4"],  # Replace with actual features
        "importance": [0.3, 0.2, 0.3, 0.2],  # Replace with actual values
    })

    imp_fig = px.bar(
        feature_imp,
        x="feature",
        y="importance",
        title="Feature Importance",
    )

    # SHAP values
    shap_fig = go.Figure()  # Replace with actual SHAP visualization

    # Client status table
    client_data = [
        {
            "client_id": f"client_{i}",
            "status": "Active",
            "last_update": "Now",
            "local_accuracy": f"{accuracy * 0.9:.2f}",
        }
        for i in range(int(n_clients))
    ]

    return (
        f"{accuracy:.2%}",
        str(int(n_clients)),
        str(int(n_rounds)),
        perf_fig,
        imp_fig,
        shap_fig,
        client_data,
    )

class Dashboard:
    def __init__(self, config: Dict):
        self.config = config
        self.metrics_queue = Queue()
        self._stop_event = threading.Event()

    def start(self):
        """Start the dashboard"""
        st.set_page_config(
            page_title="SEFCNet Dashboard",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        # Initialize session state
        if 'metrics' not in st.session_state:
            st.session_state.metrics = {}

        self._render_layout()
        self._start_metrics_update()

    def _render_layout(self):
        """Render dashboard layout"""
        st.title("🧠 SEFCNet Dashboard")
        
        # Sidebar controls
        with st.sidebar:
            self._render_controls()

        # Main content
        tab1, tab2, tab3 = st.tabs(["Overview", "Performance", "Analytics"])
        
        with tab1:
            self._render_overview()
        with tab2:
            self._render_performance()
        with tab3:
            self._render_analytics()

    def _start_metrics_update(self):
        """Start metrics update thread"""
        def update_loop():
            while not self._stop_event.is_set():
                if not self.metrics_queue.empty():
                    metrics = self.metrics_queue.get()
                    st.session_state.metrics = metrics
                time.sleep(self.config['visualization']['update_interval'])

        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start()

def run_dashboard():
    """Run the SEFCNet dashboard"""
    st.set_page_config(
        page_title="SEFCNet Dashboard",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("🧠 SEFCNet Dashboard")
    
    # Sidebar controls
    with st.sidebar:
        st.title("Controls")
        if st.button("Start Training"):
            st.session_state.training = True
        if st.button("Stop Training"):
            st.session_state.training = False

    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["Overview", "Performance", "Analytics"])
    
    with tab1:
        render_overview()
    with tab2:
        render_performance()
    with tab3:
        render_analytics()

def render_overview():
    """Render system overview"""
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Active Clients", "5", "+2")
    with col2:
        st.metric("Global Accuracy", "87.5%", "+2.3%")
    with col3:
        st.metric("Training Round", "3/10")

def render_performance():
    """Render performance metrics"""
    st.subheader("Model Performance")
    # Add performance visualization

def render_analytics():
    """Render analytics"""
    st.subheader("System Analytics")
    # Add analytics visualization

if __name__ == "__main__":
    # Start Prometheus metrics server
    start_http_server(8000)
    # Start dashboard
    app.run_server(debug=True, host="0.0.0.0", port=8050)
    run_dashboard()