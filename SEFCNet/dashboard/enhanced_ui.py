"""
Enhanced dashboard for SEFCNet with user-friendly visualizations
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
from pathlib import Path
import numpy as np

from ..utils.logger import get_logger
from ..utils.metrics import MetricsCollector

logger = get_logger(__name__)

class DashboardUI:
    """User-friendly dashboard for SEFCNet"""
    
    def __init__(self):
        """Initialize dashboard"""
        self.metrics = MetricsCollector()
        
        # Set page config
        st.set_page_config(
            page_title="SEFCNet Dashboard",
            page_icon="📊",
            layout="wide"
        )
        
    def render(self):
        """Render the dashboard"""
        # Header
        st.title("📊 SEFCNet Federated Learning Dashboard")
        
        # Sidebar
        with st.sidebar:
            st.header("Navigation")
            page = st.radio(
                "Select Page",
                ["Overview", "Training Metrics", "System Health", "Resources", "System Metrics"]
            )
        
        if page == "Overview":
            self._render_overview()
        elif page == "Training Metrics":
            self._render_training_metrics()
        elif page == "System Health":
            self._render_system_health()
        elif page == "System Metrics":
            from .system_metrics import SystemMetricsView
            metrics_view = SystemMetricsView()
            metrics_view.render()
        else:
            self._render_resources()
    
    def _render_overview(self):
        """Render overview page"""
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            self._metric_card(
                "Active Clients",
                self._get_active_clients(),
                "Total connected clients"
            )
        
        with col2:
            self._metric_card(
                "Global Accuracy",
                f"{self._get_global_accuracy():.2%}",
                "Current model accuracy"
            )
        
        with col3:
            self._metric_card(
                "Training Round",
                self._get_current_round(),
                "Current training round"
            )
        
        with col4:
            self._metric_card(
                "System Health",
                self._get_system_health(),
                "Overall system status"
            )
        
        # Training Progress
        st.subheader("📈 Training Progress")
        progress_data = self._get_training_progress()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=progress_data["round"],
            y=progress_data["accuracy"],
            mode="lines+markers",
            name="Global Accuracy",
            line=dict(color="#2E86C1")
        ))
        
        fig.add_trace(go.Scatter(
            x=progress_data["round"],
            y=progress_data["train_accuracy"],
            mode="lines+markers",
            name="Training Accuracy",
            line=dict(color="#28B463")
        ))
        
        fig.update_layout(
            title="Model Performance Over Time",
            xaxis_title="Training Round",
            yaxis_title="Accuracy",
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Client Performance
        st.subheader("🔄 Client Performance")
        client_data = self._get_client_performance()
        
        fig = px.bar(
            client_data,
            x="client",
            y="accuracy",
            color="accuracy",
            title="Individual Client Accuracy",
            color_continuous_scale="Viridis"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_training_metrics(self):
        """Render training metrics page"""
        st.header("📊 Training Metrics")
        
        # Training Configuration
        st.subheader("⚙️ Configuration")
        config = self._get_training_config()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Rounds", config["num_rounds"])
            st.metric("Batch Size", config["batch_size"])
            st.metric("Learning Rate", f"{config['learning_rate']:.4f}")
        
        with col2:
            st.metric("Min Fit Clients", config["min_fit_clients"])
            st.metric("Min Evaluate Clients", config["min_evaluate_clients"])
            st.metric("Min Available Clients", config["min_available_clients"])
        
        # Loss Curves
        st.subheader("📉 Loss Curves")
        loss_data = self._get_loss_data()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=loss_data["round"],
            y=loss_data["train_loss"],
            mode="lines+markers",
            name="Training Loss",
            line=dict(color="#E74C3C")
        ))
        
        fig.add_trace(go.Scatter(
            x=loss_data["round"],
            y=loss_data["val_loss"],
            mode="lines+markers",
            name="Validation Loss",
            line=dict(color="#8E44AD")
        ))
        
        fig.update_layout(
            title="Loss Evolution",
            xaxis_title="Training Round",
            yaxis_title="Loss",
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Model Updates
        st.subheader("🔄 Model Updates")
        updates_data = self._get_model_updates()
        
        fig = px.scatter(
            updates_data,
            x="round",
            y="magnitude",
            size="magnitude",
            color="client",
            title="Model Update Magnitudes",
            labels={
                "round": "Training Round",
                "magnitude": "Update Magnitude",
                "client": "Client ID"
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_system_health(self):
        """Render system health page"""
        st.header("🏥 System Health")
        
        # Resource Usage
        st.subheader("💻 Resource Usage")
        resource_data = self._get_resource_usage()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=resource_data["cpu_percent"],
                title={"text": "CPU Usage"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "#2ECC71"},
                    "steps": [
                        {"range": [0, 50], "color": "#EAFAF1"},
                        {"range": [50, 80], "color": "#FCF3CF"},
                        {"range": [80, 100], "color": "#FADBD8"}
                    ]
                }
            ))
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=resource_data["memory_percent"],
                title={"text": "Memory Usage"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "#3498DB"},
                    "steps": [
                        {"range": [0, 50], "color": "#EBF5FB"},
                        {"range": [50, 80], "color": "#FCF3CF"},
                        {"range": [80, 100], "color": "#FADBD8"}
                    ]
                }
            ))
            st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=resource_data["network_usage"],
                title={"text": "Network Usage"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "#9B59B6"},
                    "steps": [
                        {"range": [0, 50], "color": "#F5EEF8"},
                        {"range": [50, 80], "color": "#FCF3CF"},
                        {"range": [80, 100], "color": "#FADBD8"}
                    ]
                }
            ))
            st.plotly_chart(fig, use_container_width=True)
        
        # Client Health
        st.subheader("🔋 Client Health")
        health_data = self._get_client_health()
        
        fig = px.scatter(
            health_data,
            x="response_time",
            y="success_rate",
            size="data_quality",
            color="status",
            hover_data=["client_id"],
            title="Client Health Matrix",
            labels={
                "response_time": "Response Time (ms)",
                "success_rate": "Success Rate",
                "data_quality": "Data Quality Score",
                "status": "Status"
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # System Logs
        st.subheader("📝 System Logs")
        logs = self._get_system_logs()
        
        for log in logs:
            severity = log["severity"]
            if severity == "ERROR":
                st.error(log["message"])
            elif severity == "WARNING":
                st.warning(log["message"])
            else:
                st.info(log["message"])
    
    def _render_resources(self):
        """Render resources page"""
        st.header("💾 Resource Management")
        
        # Resource Allocation
        st.subheader("📊 Resource Allocation")
        allocation_data = self._get_resource_allocation()
        
        fig = px.treemap(
            allocation_data,
            path=["category", "component", "resource"],
            values="allocation",
            color="usage",
            title="Resource Allocation Overview",
            color_continuous_scale="RdYlBu_r"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Network Traffic
        st.subheader("🌐 Network Traffic")
        traffic_data = self._get_network_traffic()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=traffic_data["timestamp"],
            y=traffic_data["incoming"],
            mode="lines",
            name="Incoming Traffic",
            line=dict(color="#2ECC71")
        ))
        
        fig.add_trace(go.Scatter(
            x=traffic_data["timestamp"],
            y=traffic_data["outgoing"],
            mode="lines",
            name="Outgoing Traffic",
            line=dict(color="#E74C3C")
        ))
        
        fig.update_layout(
            title="Network Traffic Over Time",
            xaxis_title="Time",
            yaxis_title="Traffic (MB/s)",
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Resource Timeline
        st.subheader("⏱️ Resource Timeline")
        timeline_data = self._get_resource_timeline()
        
        fig = px.timeline(
            timeline_data,
            x_start="start_time",
            x_end="end_time",
            y="resource",
            color="status",
            title="Resource Usage Timeline",
            labels={
                "resource": "Resource",
                "start_time": "Start Time",
                "end_time": "End Time",
                "status": "Status"
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _metric_card(self, title, value, description):
        """Create a metric card"""
        st.metric(
            label=title,
            value=value,
            help=description
        )
    
    def _get_active_clients(self):
        """Get number of active clients"""
        try:
            return self.metrics.get_metric("federated_active_clients")
        except:
            return 0
    
    def _get_global_accuracy(self):
        """Get global model accuracy"""
        try:
            return self.metrics.get_metric("federated_global_accuracy")
        except:
            return 0.0
    
    def _get_current_round(self):
        """Get current training round"""
        try:
            return self.metrics.get_metric("federated_training_rounds_total")
        except:
            return 0
    
    def _get_system_health(self):
        """Get system health status"""
        try:
            metrics = self.metrics.get_all_metrics()
            errors = sum(1 for m in metrics if "error" in m["name"].lower())
            if errors == 0:
                return "✅ Healthy"
            elif errors < 3:
                return "⚠️ Warning"
            else:
                return "❌ Critical"
        except:
            return "❓ Unknown"
    
    def _get_training_progress(self):
        """Get training progress data"""
        try:
            history_path = Path("artifacts/federated_history.json")
            if history_path.exists():
                with open(history_path) as f:
                    history = json.load(f)
                    return pd.DataFrame(history["metrics"])
            return pd.DataFrame({
                "round": [],
                "accuracy": [],
                "train_accuracy": []
            })
        except:
            return pd.DataFrame({
                "round": [],
                "accuracy": [],
                "train_accuracy": []
            })
    
    def _get_client_performance(self):
        """Get client performance data"""
        try:
            # Implement client performance data collection
            return pd.DataFrame({
                "client": [f"Client {i}" for i in range(1, 6)],
                "accuracy": np.random.uniform(0.8, 1.0, 5)
            })
        except:
            return pd.DataFrame({"client": [], "accuracy": []})
    
    def _get_training_config(self):
        """Get training configuration"""
        return {
            "num_rounds": 10,
            "batch_size": 32,
            "learning_rate": 0.01,
            "min_fit_clients": 3,
            "min_evaluate_clients": 3,
            "min_available_clients": 5
        }
    
    def _get_loss_data(self):
        """Get loss curve data"""
        try:
            history_path = Path("artifacts/federated_history.json")
            if history_path.exists():
                with open(history_path) as f:
                    history = json.load(f)
                    return pd.DataFrame(history["losses"])
            return pd.DataFrame({
                "round": [],
                "train_loss": [],
                "val_loss": []
            })
        except:
            return pd.DataFrame({
                "round": [],
                "train_loss": [],
                "val_loss": []
            })
    
    def _get_model_updates(self):
        """Get model update data"""
        try:
            # Implement model update data collection
            rounds = list(range(1, 11))
            clients = [f"Client {i}" for i in range(1, 6)]
            data = []
            for r in rounds:
                for c in clients:
                    data.append({
                        "round": r,
                        "client": c,
                        "magnitude": np.random.uniform(0.1, 1.0)
                    })
            return pd.DataFrame(data)
        except:
            return pd.DataFrame({
                "round": [],
                "client": [],
                "magnitude": []
            })
    
    def _get_resource_usage(self):
        """Get resource usage data"""
        try:
            import psutil
            return {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "network_usage": np.random.uniform(0, 100)
            }
        except:
            return {
                "cpu_percent": 0,
                "memory_percent": 0,
                "network_usage": 0
            }
    
    def _get_client_health(self):
        """Get client health data"""
        try:
            # Implement client health data collection
            clients = [f"Client {i}" for i in range(1, 6)]
            data = []
            for c in clients:
                data.append({
                    "client_id": c,
                    "response_time": np.random.uniform(10, 100),
                    "success_rate": np.random.uniform(0.8, 1.0),
                    "data_quality": np.random.uniform(0.7, 1.0),
                    "status": np.random.choice(
                        ["Healthy", "Warning", "Critical"],
                        p=[0.7, 0.2, 0.1]
                    )
                })
            return pd.DataFrame(data)
        except:
            return pd.DataFrame({
                "client_id": [],
                "response_time": [],
                "success_rate": [],
                "data_quality": [],
                "status": []
            })
    
    def _get_system_logs(self):
        """Get system logs"""
        try:
            # Implement system log collection
            return [
                {
                    "severity": "INFO",
                    "message": "System running normally",
                    "timestamp": datetime.now()
                }
            ]
        except:
            return []
    
    def _get_resource_allocation(self):
        """Get resource allocation data"""
        try:
            # Implement resource allocation data collection
            data = []
            categories = ["Compute", "Memory", "Network"]
            components = ["Client", "Server", "Analytics"]
            resources = ["CPU", "RAM", "Bandwidth"]
            
            for cat in categories:
                for comp in components:
                    for res in resources:
                        data.append({
                            "category": cat,
                            "component": comp,
                            "resource": res,
                            "allocation": np.random.uniform(100, 1000),
                            "usage": np.random.uniform(0, 100)
                        })
            return pd.DataFrame(data)
        except:
            return pd.DataFrame({
                "category": [],
                "component": [],
                "resource": [],
                "allocation": [],
                "usage": []
            })
    
    def _get_network_traffic(self):
        """Get network traffic data"""
        try:
            # Implement network traffic data collection
            timestamps = pd.date_range(
                start="now",
                periods=100,
                freq="1min"
            )
            return pd.DataFrame({
                "timestamp": timestamps,
                "incoming": np.random.uniform(1, 10, 100),
                "outgoing": np.random.uniform(1, 10, 100)
            })
        except:
            return pd.DataFrame({
                "timestamp": [],
                "incoming": [],
                "outgoing": []
            })
    
    def _get_resource_timeline(self):
        """Get resource timeline data"""
        try:
            # Implement resource timeline data collection
            now = pd.Timestamp.now()
            resources = ["CPU", "Memory", "Network", "Storage"]
            data = []
            
            for res in resources:
                start_time = now - pd.Timedelta(hours=1)
                while start_time < now:
                    duration = pd.Timedelta(minutes=np.random.randint(5, 15))
                    data.append({
                        "resource": res,
                        "start_time": start_time,
                        "end_time": start_time + duration,
                        "status": np.random.choice(
                            ["Active", "Idle", "Busy"],
                            p=[0.6, 0.2, 0.2]
                        )
                    })
                    start_time += duration
                    
            return pd.DataFrame(data)
        except:
            return pd.DataFrame({
                "resource": [],
                "start_time": [],
                "end_time": [],
                "status": []
            })
    
    def render_header(self):
        """Render dashboard header"""
        st.title("🧠 SEFCNet Self-Evolving System")
        st.markdown("""
        Monitor and control your federated learning system in real-time.
        """)
        
    def render_metrics(self, metrics: Dict[str, float]):
        cols = st.columns(4)
        with cols[0]:
            st.metric("Global Accuracy", f"{metrics['accuracy']:.2f}%", f"{metrics['accuracy_change']}%")
        with cols[1]:
            st.metric("Active Nodes", metrics['active_nodes'], f"{metrics['node_change']}")
        with cols[2]:
            st.metric("Evolution Step", metrics['evolution_step'])
        with cols[3]:
            st.metric("Training Time", f"{metrics['training_time']:.1f}s")
            
    def plot_network_topology(self, nodes: List[Dict]):
        """Create interactive network visualization"""
        fig = go.Figure(data=[
            go.Scatter(
                x=[node['x'] for node in nodes],
                y=[node['y'] for node in nodes],
                mode='markers+text',
                text=[node['id'] for node in nodes],
                hovertext=[f"Status: {node['status']}<br>Load: {node['load']}" for node in nodes],
                marker=dict(size=20, color=[node['performance'] for node in nodes])
            )
        ])
        st.plotly_chart(fig, use_container_width=True)