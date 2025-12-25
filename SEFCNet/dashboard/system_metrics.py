"""
System metrics visualization and monitoring component
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

class SystemMetricsView:
    """User-friendly visualization of system metrics"""
    
    def __init__(self):
        """Initialize system metrics view"""
        self.gc_colors = {
            "0": "#2ECC71",  # Green for young generation
            "1": "#F1C40F",  # Yellow for middle generation
            "2": "#E74C3C"   # Red for old generation
        }
    
    def render(self):
        """Render system metrics view"""
        st.title("🔍 System Metrics Dashboard")
        
        # Create tabs for different metric categories
        tab1, tab2, tab3 = st.tabs([
            "🗑️ Garbage Collection",
            "🤝 Federation Status",
            "🐍 Python Runtime"
        ])
        
        with tab1:
            self._render_gc_metrics()
            
        with tab2:
            self._render_federation_metrics()
            
        with tab3:
            self._render_python_info()
    
    def _render_gc_metrics(self):
        """Render garbage collection metrics"""
        st.header("Garbage Collection Statistics")
        
        # Create three columns for different GC metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Objects Collected by Generation")
            # Create a bar chart for objects collected
            collected_data = {
                "Generation": ["Young (Gen 0)", "Middle (Gen 1)", "Old (Gen 2)"],
                "Objects Collected": [8824.0, 908.0, 114.0]
            }
            fig = px.bar(
                collected_data,
                x="Generation",
                y="Objects Collected",
                color="Generation",
                color_discrete_map={
                    "Young (Gen 0)": self.gc_colors["0"],
                    "Middle (Gen 1)": self.gc_colors["1"],
                    "Old (Gen 2)": self.gc_colors["2"]
                }
            )
            fig.update_layout(
                title="Objects Collected During GC",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Add explanation
            st.info("""
            **Understanding GC Generations:**
            - **Gen 0 (Young)**: Frequent collections, new objects
            - **Gen 1 (Middle)**: Objects that survived Gen 0
            - **Gen 2 (Old)**: Long-lived objects
            """)
        
        with col2:
            st.subheader("Collection Frequency")
            # Create a pie chart for collection counts
            collections_data = {
                "Generation": ["Young (Gen 0)", "Middle (Gen 1)", "Old (Gen 2)"],
                "Collections": [808.0, 73.0, 6.0]
            }
            fig = px.pie(
                collections_data,
                values="Collections",
                names="Generation",
                color="Generation",
                color_discrete_map={
                    "Young (Gen 0)": self.gc_colors["0"],
                    "Middle (Gen 1)": self.gc_colors["1"],
                    "Old (Gen 2)": self.gc_colors["2"]
                }
            )
            fig.update_layout(title="GC Collections by Generation")
            st.plotly_chart(fig, use_container_width=True)
            
            # Add metrics
            st.metric(
                "Total Collections",
                f"{sum(collections_data['Collections']):,.0f}",
                help="Total number of garbage collections across all generations"
            )
        
        # Show GC efficiency
        st.subheader("Garbage Collection Efficiency")
        efficiency_data = pd.DataFrame({
            "Generation": ["Young (Gen 0)", "Middle (Gen 1)", "Old (Gen 2)"],
            "Objects per Collection": [
                8824.0 / 808.0,
                908.0 / 73.0,
                114.0 / 6.0
            ]
        })
        
        fig = px.bar(
            efficiency_data,
            x="Generation",
            y="Objects per Collection",
            color="Generation",
            color_discrete_map={
                "Young (Gen 0)": self.gc_colors["0"],
                "Middle (Gen 1)": self.gc_colors["1"],
                "Old (Gen 2)": self.gc_colors["2"]
            }
        )
        fig.update_layout(
            title="Average Objects Collected per GC Run",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Memory management health
        st.subheader("Memory Management Health")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            health_score = self._calculate_gc_health_score(
                8824.0, 908.0, 114.0,
                808.0, 73.0, 6.0
            )
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=health_score * 100,
                title={"text": "GC Health Score"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": self._get_health_color(health_score)},
                    "steps": [
                        {"range": [0, 50], "color": "#FADBD8"},
                        {"range": [50, 80], "color": "#FCF3CF"},
                        {"range": [80, 100], "color": "#D5F5E3"}
                    ]
                }
            ))
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.metric(
                "Collection Frequency",
                "Normal" if health_score > 0.7 else "High",
                help="Assessment of garbage collection frequency"
            )
        
        with col3:
            st.metric(
                "Memory Pressure",
                "Low" if health_score > 0.8 else "Moderate",
                help="Current memory pressure on the system"
            )
    
    def _render_federation_metrics(self):
        """Render federation metrics"""
        st.header("Federation Status")
        
        # Key federation metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=0.0,  # federated_global_accuracy
                title={"text": "Global Accuracy"},
                delta={"reference": 0.8},
                gauge={
                    "axis": {"range": [0, 1]},
                    "bar": {"color": "#3498DB"},
                    "steps": [
                        {"range": [0, 0.6], "color": "#FADBD8"},
                        {"range": [0.6, 0.8], "color": "#FCF3CF"},
                        {"range": [0.8, 1.0], "color": "#D5F5E3"}
                    ]
                }
            ))
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.metric(
                "Training Rounds",
                "0",  # federated_training_rounds_total
                help="Number of completed training rounds"
            )
            
            # Add progress bar
            st.progress(
                0.0,  # federated_training_rounds_total / total_rounds
                text="Training Progress"
            )
        
        with col3:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=0.0,  # federated_active_clients
                title={"text": "Active Clients"},
                gauge={
                    "axis": {"range": [0, 5]},
                    "bar": {"color": "#2ECC71"},
                    "steps": [
                        {"range": [0, 2], "color": "#FADBD8"},
                        {"range": [2, 4], "color": "#FCF3CF"},
                        {"range": [4, 5], "color": "#D5F5E3"}
                    ]
                }
            ))
            st.plotly_chart(fig, use_container_width=True)
        
        # Federation health indicators
        st.subheader("Federation Health Indicators")
        
        health_metrics = pd.DataFrame({
            "Metric": [
                "Client Participation",
                "Training Progress",
                "Model Convergence",
                "System Stability"
            ],
            "Status": [
                "⚠️ Low",
                "🔴 Not Started",
                "⚪ Unknown",
                "✅ Stable"
            ],
            "Value": [0.0, 0.0, 0.0, 1.0]
        })
        
        st.dataframe(
            health_metrics,
            column_config={
                "Metric": "Indicator",
                "Status": "Current Status",
                "Value": st.column_config.ProgressColumn(
                    "Health Score",
                    min_value=0,
                    max_value=1,
                    format="%.2f"
                )
            },
            hide_index=True
        )
    
    def _render_python_info(self):
        """Render Python runtime information"""
        st.header("Python Runtime Information")
        
        # Python version info
        st.subheader("🐍 Python Version")
        version_col1, version_col2 = st.columns([2, 1])
        
        with version_col1:
            st.info(
                f"""
                **Python Implementation:** CPython
                **Version:** 3.11.9
                **Major:** 3
                **Minor:** 11
                **Patch Level:** 9
                """
            )
        
        with version_col2:
            st.image(
                "https://www.python.org/static/community_logos/python-logo-generic.svg",
                caption="Python"
            )
        
        # Runtime metrics
        st.subheader("🔄 Runtime Metrics")
        
        runtime_cols = st.columns(3)
        
        with runtime_cols[0]:
            st.metric(
                "GC Collections",
                f"{887:,}",  # Total GC collections
                help="Total garbage collections across all generations"
            )
        
        with runtime_cols[1]:
            st.metric(
                "Objects Collected",
                f"{9846:,}",  # Total objects collected
                help="Total objects collected by garbage collector"
            )
        
        with runtime_cols[2]:
            st.metric(
                "Collection Efficiency",
                "99.9%",  # No uncollectable objects
                help="Percentage of objects successfully collected"
            )
    
    def _calculate_gc_health_score(
        self,
        gen0_objects,
        gen1_objects,
        gen2_objects,
        gen0_collections,
        gen1_collections,
        gen2_collections
    ):
        """Calculate GC health score"""
        # Calculate objects per collection for each generation
        gen0_efficiency = gen0_objects / gen0_collections if gen0_collections > 0 else 0
        gen1_efficiency = gen1_objects / gen1_collections if gen1_collections > 0 else 0
        gen2_efficiency = gen2_objects / gen2_collections if gen2_collections > 0 else 0
        
        # Weight the scores (higher weight for older generations)
        weights = [0.5, 0.3, 0.2]
        max_objects_per_collection = 20  # Threshold for optimal efficiency
        
        scores = [
            min(gen0_efficiency / max_objects_per_collection, 1.0),
            min(gen1_efficiency / max_objects_per_collection, 1.0),
            min(gen2_efficiency / max_objects_per_collection, 1.0)
        ]
        
        # Calculate weighted score
        return sum(score * weight for score, weight in zip(scores, weights))
    
    def _get_health_color(self, score):
        """Get color based on health score"""
        if score >= 0.8:
            return "#2ECC71"  # Green
        elif score >= 0.6:
            return "#F1C40F"  # Yellow
        else:
            return "#E74C3C"  # Red