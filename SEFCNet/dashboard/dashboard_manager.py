"""
Enterprise Dashboard Manager for SEFCNet
====================================

This module provides advanced dashboard management capabilities:
- Real-time data visualization
- Interactive analytics
- Explainable AI components
- Custom visualization plugins
- Dashboard state management
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import json
import os
from dataclasses import dataclass

import aiohttp
from fastapi import WebSocket
from prometheus_client.parser import text_string_to_metric_families
import pandas as pd
import numpy as np
from sklearn.manifold import TSNE
import plotly.graph_objs as go
import plotly.express as px

try:
    import shap
    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False
    logging.warning("SHAP not installed. Some explainability features will be disabled.")

try:
    from monitoring.metrics_collector import metrics_collector
except ImportError:
    metrics_collector = None
try:
    from monitoring.monitoring_service import monitoring_service
except ImportError:
    monitoring_service = None

logger = logging.getLogger(__name__)

@dataclass
class DashboardConfig:
    """Dashboard configuration."""
    name: str
    description: str
    refresh_interval: int  # seconds
    default_timerange: timedelta
    panels: List[Dict[str, Any]]
    data_sources: List[str]
    theme: str = "dark"

class DashboardManager:
    """Enterprise-grade dashboard manager."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._dashboard_configs: Dict[str, DashboardConfig] = {}
        self._update_interval = 1  # second
        self._is_broadcasting = False
        self._broadcast_task = None
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = 60  # seconds
        self._load_dashboard_configs()

    def _load_dashboard_configs(self):
        """Load dashboard configurations from files."""
        config_dir = os.path.join(
            os.path.dirname(__file__),
            'config',
            'grafana_dashboards'
        )
        for filename in os.listdir(config_dir):
            if filename.endswith('.json'):
                with open(os.path.join(config_dir, filename)) as f:
                    config = json.load(f)
                    self._dashboard_configs[config['uid']] = DashboardConfig(
                        name=config['title'],
                        description=config.get('description', ''),
                        refresh_interval=self._parse_refresh_interval(
                            config['refresh']
                        ),
                        default_timerange=self._parse_timerange(
                            config['time']['from'],
                            config['time']['to']
                        ),
                        panels=config['panels'],
                        data_sources=self._extract_data_sources(config),
                        theme=config.get('style', 'dark')
                    )

    def _parse_refresh_interval(self, refresh: str) -> int:
        """Parse refresh interval string to seconds."""
        if refresh.endswith('s'):
            return int(refresh[:-1])
        elif refresh.endswith('m'):
            return int(refresh[:-1]) * 60
        elif refresh.endswith('h'):
            return int(refresh[:-1]) * 3600
        return 10  # default

    def _parse_timerange(
        self,
        from_time: str,
        to_time: str
    ) -> timedelta:
        """Parse dashboard time range."""
        if from_time.startswith('now-'):
            value = int(from_time[4:-1])
            unit = from_time[-1]
            if unit == 'h':
                return timedelta(hours=value)
            elif unit == 'd':
                return timedelta(days=value)
            elif unit == 'm':
                return timedelta(minutes=value)
        return timedelta(hours=1)  # default

    def _extract_data_sources(self, config: Dict) -> List[str]:
        """Extract unique data sources from dashboard config."""
        sources = set()
        for panel in config.get('panels', []):
            if 'targets' in panel:
                for target in panel['targets']:
                    if 'datasource' in target:
                        sources.add(target['datasource'])
        return list(sources)

    async def start_broadcasting(self):
        """Start broadcasting dashboard updates."""
        if self._is_broadcasting:
            return

        self._is_broadcasting = True
        self._broadcast_task = asyncio.create_task(self._broadcast_loop())

    async def stop_broadcasting(self):
        """Stop broadcasting dashboard updates."""
        self._is_broadcasting = False
        if self._broadcast_task:
            await self._broadcast_task

    async def _broadcast_loop(self):
        """Main broadcasting loop."""
        while self._is_broadcasting:
            try:
                update = await self._gather_dashboard_data()
                await self._broadcast_update(update)
                await asyncio.sleep(self._update_interval)
            except Exception as e:
                logger.error(f"Error in broadcast loop: {str(e)}")
                await asyncio.sleep(1)

    async def _gather_dashboard_data(self) -> Dict[str, Any]:
        """Gather all required dashboard data."""
        now = datetime.utcnow()
        data = {
            'timestamp': now.isoformat(),
            'metrics': {},
            'alerts': [],
            'system_health': {},
            'ml_insights': {}
        }

        # Get metrics
        metrics_data = metrics_collector.get_metrics_snapshot()
        data['metrics'] = self._process_metrics(metrics_data)

        # Get active alerts
        data['alerts'] = monitoring_service.get_active_alerts()

        # Get system health
        data['system_health'] = monitoring_service.get_system_health()

        # Generate ML insights
        data['ml_insights'] = await self._generate_ml_insights()

        return data

    def _process_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Process and transform metrics for visualization."""
        processed = {}
        
        # Process system metrics
        if 'system_cpu_usage' in metrics:
            processed['cpu'] = self._calculate_cpu_stats(metrics['system_cpu_usage'])
        
        if 'system_memory_usage' in metrics:
            processed['memory'] = self._calculate_memory_stats(
                metrics['system_memory_usage']
            )

        # Process ML metrics
        if 'model_accuracy' in metrics:
            processed['model_performance'] = self._calculate_model_stats(
                metrics['model_accuracy']
            )

        return processed

    def _calculate_cpu_stats(self, cpu_data: Dict[str, float]) -> Dict[str, Any]:
        """Calculate CPU statistics."""
        df = pd.DataFrame(cpu_data.items(), columns=['core', 'usage'])
        return {
            'average': df['usage'].mean(),
            'max': df['usage'].max(),
            'min': df['usage'].min(),
            'by_core': df.to_dict(orient='records')
        }

    def _calculate_memory_stats(
        self,
        memory_data: Dict[str, float]
    ) -> Dict[str, Any]:
        """Calculate memory statistics."""
        total = memory_data.get('total', 1)
        used = memory_data.get('used', 0)
        return {
            'usage_percent': (used / total) * 100,
            'available_percent': 100 - ((used / total) * 100),
            'total_gb': total / (1024 ** 3),
            'used_gb': used / (1024 ** 3)
        }

    def _calculate_model_stats(
        self,
        accuracy_data: Dict[str, float]
    ) -> Dict[str, Any]:
        """Calculate model performance statistics."""
        df = pd.DataFrame(accuracy_data.items(), columns=['model', 'accuracy'])
        return {
            'global_accuracy': df[df['model'].str.contains('global')]['accuracy'].mean(),
            'local_accuracies': df[df['model'].str.contains('local')].to_dict(
                orient='records'
            ),
            'improvement': self._calculate_accuracy_improvement(df)
        }

    def _calculate_accuracy_improvement(self, df: pd.DataFrame) -> float:
        """Calculate accuracy improvement over time."""
        if len(df) < 2:
            return 0.0
        return ((df['accuracy'].iloc[-1] - df['accuracy'].iloc[0]) 
                / df['accuracy'].iloc[0] * 100)

    async def _generate_ml_insights(self) -> Dict[str, Any]:
        """Generate machine learning insights."""
        insights = {}
        
        # Feature importance analysis
        feature_importance = metrics_collector.get_metric('feature_importance')
        if feature_importance:
            insights['feature_importance'] = self._analyze_feature_importance(
                feature_importance
            )

        # Model behavior analysis (without SHAP dependency)
        model_behavior = await self._analyze_model_behavior()
        if model_behavior:
            insights['model_behavior'] = model_behavior

        # Add SHAP analysis if available
        if HAS_SHAP and feature_importance:
            try:
                shap_values = self._analyze_shap_values(feature_importance)
                if shap_values:
                    insights['shap_analysis'] = shap_values
            except Exception as e:
                logger.warning(f"SHAP analysis failed: {str(e)}")

        return insights

    def _analyze_feature_importance(
        self,
        importance_data: Dict[str, float]
    ) -> Dict[str, Any]:
        """Analyze and visualize feature importance."""
        df = pd.DataFrame(importance_data.items(), columns=['feature', 'importance'])
        df = df.sort_values('importance', ascending=False)

        return {
            'top_features': df.head(10).to_dict(orient='records'),
            'importance_distribution': {
                'mean': df['importance'].mean(),
                'std': df['importance'].std(),
                'percentiles': df['importance'].quantile([0.25, 0.5, 0.75]).to_dict()
            }
        }

    def _analyze_shap_values(
        self,
        feature_importance: Dict[str, float]
    ) -> Optional[Dict[str, Any]]:
        """Analyze SHAP values if SHAP is available."""
        if not HAS_SHAP:
            return None
            
        try:
            # Convert feature importance to numpy array
            features = list(feature_importance.keys())
            values = np.array(list(feature_importance.values()))
            
            # Create a simple explainer
            explainer = shap.Explainer(lambda x: x, np.array([values]))
            shap_values = explainer(np.array([values]))
            
            return {
                'base_values': shap_values.base_values.tolist(),
                'values': shap_values.values.tolist(),
                'features': features
            }
        except Exception as e:
            logger.warning(f"SHAP analysis error: {str(e)}")
            return None

    async def _analyze_model_behavior(self) -> Dict[str, Any]:
        """Analyze model behavior patterns."""
        # This would be implemented based on specific model metrics
        # and requirements. For now, return a placeholder.
        return {
            'stability': {
                'score': 0.85,
                'trend': 'improving'
            },
            'convergence': {
                'status': 'stable',
                'iterations_to_converge': 150
            }
        }

    async def _broadcast_update(self, update: Dict[str, Any]):
        """Broadcast updates to all connected clients."""
        for connection in self.active_connections:
            try:
                await connection.send_json(update)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {str(e)}")
                self.active_connections.remove(connection)

    async def add_connection(self, websocket: WebSocket):
        """Register new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def remove_connection(self, websocket: WebSocket):
        """Remove WebSocket connection."""
        self.active_connections.remove(websocket)

    async def get_dashboard_config(
        self,
        dashboard_id: str
    ) -> Optional[DashboardConfig]:
        """Get dashboard configuration by ID."""
        return self._dashboard_configs.get(dashboard_id)

    def get_available_dashboards(self) -> List[Dict[str, str]]:
        """Get list of available dashboards."""
        return [
            {
                'id': dashboard_id,
                'name': config.name,
                'description': config.description
            }
            for dashboard_id, config in self._dashboard_configs.items()
        ]

# Initialize global dashboard manager
dashboard_manager = DashboardManager()