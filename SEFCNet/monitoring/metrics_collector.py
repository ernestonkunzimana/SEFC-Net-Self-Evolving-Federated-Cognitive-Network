"""
Enterprise Metrics Collector for SEFCNet
======================================

Provides advanced metrics collection and monitoring capabilities:
- System performance metrics
- ML model metrics
- Network health metrics
- Resource utilization
- Custom business metrics
- High-resolution time series data
"""

import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import logging
from dataclasses import dataclass
import threading
from concurrent.futures import ThreadPoolExecutor

import prometheus_client as prom
from prometheus_client import Counter, Gauge, Histogram, Summary
import psutil
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class MetricDefinition:
    """Definition of a metric with metadata."""
    name: str
    description: str
    type: str  # 'counter', 'gauge', 'histogram', 'summary'
    labels: List[str]
    buckets: Optional[List[float]] = None  # For histograms
    quantiles: Optional[List[float]] = None  # For summaries

class MetricsRegistry:
    """Central registry for all metrics."""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._metrics: Dict[str, Any] = {}
            self._definitions: Dict[str, MetricDefinition] = {}
            self._initialized = True

    def register_metric(self, definition: MetricDefinition) -> Any:
        """Register a new metric."""
        if definition.name in self._metrics:
            return self._metrics[definition.name]

        metric_types = {
            'counter': prom.Counter,
            'gauge': prom.Gauge,
            'histogram': prom.Histogram,
            'summary': prom.Summary
        }

        kwargs = {
            'name': definition.name,
            'documentation': definition.description,
            'labelnames': definition.labels
        }

        if definition.type == 'histogram' and definition.buckets:
            kwargs['buckets'] = definition.buckets
        elif definition.type == 'summary' and definition.quantiles:
            kwargs['quantiles'] = definition.quantiles

        metric = metric_types[definition.type](**kwargs)
        self._metrics[definition.name] = metric
        self._definitions[definition.name] = definition
        return metric

    def get_metric(self, name: str) -> Optional[Any]:
        """Get a registered metric by name."""
        return self._metrics.get(name)

class MetricsCollector:
    """Enterprise-grade metrics collector."""

    def __init__(self):
        self.registry = MetricsRegistry()
        self._setup_system_metrics()
        self._setup_ml_metrics()
        self._setup_network_metrics()
        self._setup_business_metrics()
        self._executor = ThreadPoolExecutor(max_workers=4)
        self._collection_interval = 15  # seconds
        self._is_collecting = False
        self._collection_thread = None

    def _setup_system_metrics(self):
        """Setup system-level metrics."""
        metrics = [
            MetricDefinition(
                name='system_cpu_usage',
                description='CPU usage percentage',
                type='gauge',
                labels=['core']
            ),
            MetricDefinition(
                name='system_memory_usage',
                description='Memory usage in bytes',
                type='gauge',
                labels=['type']
            ),
            MetricDefinition(
                name='system_disk_usage',
                description='Disk usage in bytes',
                type='gauge',
                labels=['mount_point']
            ),
            MetricDefinition(
                name='system_network_io',
                description='Network IO statistics',
                type='gauge',
                labels=['interface', 'direction']
            )
        ]
        for metric in metrics:
            self.registry.register_metric(metric)

    def _setup_ml_metrics(self):
        """Setup machine learning metrics."""
        metrics = [
            MetricDefinition(
                name='model_training_duration',
                description='Model training duration in seconds',
                type='histogram',
                labels=['model_name', 'version'],
                buckets=[10, 30, 60, 120, 300, 600]
            ),
            MetricDefinition(
                name='model_inference_latency',
                description='Model inference latency in milliseconds',
                type='histogram',
                labels=['model_name', 'version'],
                buckets=[1, 5, 10, 25, 50, 100, 250, 500]
            ),
            MetricDefinition(
                name='model_accuracy',
                description='Model accuracy metrics',
                type='gauge',
                labels=['model_name', 'version', 'metric_type']
            ),
            MetricDefinition(
                name='feature_importance',
                description='Feature importance scores',
                type='gauge',
                labels=['model_name', 'feature_name']
            )
        ]
        for metric in metrics:
            self.registry.register_metric(metric)

    def _setup_network_metrics(self):
        """Setup network-related metrics."""
        metrics = [
            MetricDefinition(
                name='node_communication_latency',
                description='Inter-node communication latency',
                type='histogram',
                labels=['source_node', 'target_node'],
                buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5]
            ),
            MetricDefinition(
                name='message_queue_size',
                description='Size of message queues',
                type='gauge',
                labels=['queue_name', 'priority']
            ),
            MetricDefinition(
                name='network_errors',
                description='Network error counter',
                type='counter',
                labels=['error_type', 'severity']
            )
        ]
        for metric in metrics:
            self.registry.register_metric(metric)

    def _setup_business_metrics(self):
        """Setup business-specific metrics."""
        metrics = [
            MetricDefinition(
                name='energy_consumption',
                description='Energy consumption metrics',
                type='gauge',
                labels=['node_id', 'resource_type']
            ),
            MetricDefinition(
                name='optimization_impact',
                description='Impact of optimization decisions',
                type='gauge',
                labels=['optimization_type', 'metric_name']
            ),
            MetricDefinition(
                name='sla_compliance',
                description='Service Level Agreement compliance',
                type='gauge',
                labels=['service_name', 'sla_type']
            )
        ]
        for metric in metrics:
            self.registry.register_metric(metric)

    def collect_system_metrics(self):
        """Collect system metrics."""
        try:
            # CPU metrics
            for i, percentage in enumerate(psutil.cpu_percent(percpu=True)):
                self.registry.get_metric('system_cpu_usage').labels(core=f'core_{i}').set(percentage)

            # Memory metrics
            memory = psutil.virtual_memory()
            self.registry.get_metric('system_memory_usage').labels(type='total').set(memory.total)
            self.registry.get_metric('system_memory_usage').labels(type='available').set(memory.available)
            self.registry.get_metric('system_memory_usage').labels(type='used').set(memory.used)

            # Disk metrics
            for partition in psutil.disk_partitions():
                usage = psutil.disk_usage(partition.mountpoint)
                self.registry.get_metric('system_disk_usage').labels(
                    mount_point=partition.mountpoint
                ).set(usage.used)

            # Network metrics
            net_io = psutil.net_io_counters()
            self.registry.get_metric('system_network_io').labels(
                interface='all', direction='bytes_sent'
            ).set(net_io.bytes_sent)
            self.registry.get_metric('system_network_io').labels(
                interface='all', direction='bytes_recv'
            ).set(net_io.bytes_recv)

        except Exception as e:
            logger.error(f"Error collecting system metrics: {str(e)}")

    def record_ml_metric(
        self,
        metric_name: str,
        value: float,
        **labels
    ):
        """Record a machine learning metric."""
        try:
            metric = self.registry.get_metric(metric_name)
            if metric:
                if isinstance(metric, (prom.Histogram, prom.Summary)):
                    metric.labels(**labels).observe(value)
                else:
                    metric.labels(**labels).set(value)
        except Exception as e:
            logger.error(f"Error recording ML metric {metric_name}: {str(e)}")

    def record_network_metric(
        self,
        metric_name: str,
        value: float,
        **labels
    ):
        """Record a network-related metric."""
        try:
            metric = self.registry.get_metric(metric_name)
            if metric:
                if isinstance(metric, prom.Counter):
                    metric.labels(**labels).inc(value)
                elif isinstance(metric, (prom.Histogram, prom.Summary)):
                    metric.labels(**labels).observe(value)
                else:
                    metric.labels(**labels).set(value)
        except Exception as e:
            logger.error(f"Error recording network metric {metric_name}: {str(e)}")

    def record_business_metric(
        self,
        metric_name: str,
        value: float,
        **labels
    ):
        """Record a business-specific metric."""
        try:
            metric = self.registry.get_metric(metric_name)
            if metric:
                metric.labels(**labels).set(value)
        except Exception as e:
            logger.error(f"Error recording business metric {metric_name}: {str(e)}")

    def start_collection(self):
        """Start automated metrics collection."""
        if self._is_collecting:
            return

        self._is_collecting = True
        self._collection_thread = threading.Thread(
            target=self._collection_loop,
            daemon=True
        )
        self._collection_thread.start()

    def stop_collection(self):
        """Stop automated metrics collection."""
        self._is_collecting = False
        if self._collection_thread:
            self._collection_thread.join()

    def _collection_loop(self):
        """Main metrics collection loop."""
        while self._is_collecting:
            try:
                self._executor.submit(self.collect_system_metrics)
                time.sleep(self._collection_interval)
            except Exception as e:
                logger.error(f"Error in metrics collection loop: {str(e)}")
                time.sleep(1)  # Avoid tight loop on persistent errors

    def get_metrics_snapshot(self) -> Dict[str, Any]:
        """Get a snapshot of current metrics."""
        snapshot = {}
        for name, metric in self.registry._metrics.items():
            if hasattr(metric, '_value'):
                snapshot[name] = metric._value
        return snapshot

    def export_metrics(self, format: str = 'prometheus') -> str:
        """Export metrics in specified format."""
        if format == 'prometheus':
            return prom.generate_latest().decode('utf-8')
        else:
            raise ValueError(f"Unsupported export format: {format}")

class SystemMetricsCollector:
    def __init__(self):
        self.metrics_history: List[Dict] = []
        
    def collect_metrics(self) -> Dict:
        """Collect system metrics"""
        metrics = {
            'timestamp': time.time(),
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'network_bytes_sent': psutil.net_io_counters().bytes_sent,
            'network_bytes_recv': psutil.net_io_counters().bytes_recv
        }
        
        self.metrics_history.append(metrics)
        return metrics
        
    def get_average_metrics(self, window: int = 10) -> Dict:
        """Get average metrics over window"""
        if not self.metrics_history:
            return {}
            
        recent = self.metrics_history[-window:]
        return {
            'avg_cpu': np.mean([m['cpu_percent'] for m in recent]),
            'avg_memory': np.mean([m['memory_percent'] for m in recent]),
            'network_traffic': np.mean([
                m['network_bytes_sent'] + m['network_bytes_recv'] 
                for m in recent
            ])
        }

# Initialize global metrics collector
metrics_collector = MetricsCollector()