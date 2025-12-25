from typing import Dict, List, Optional
import time
import numpy as np
import logging
from dataclasses import dataclass
from prometheus_client import Counter, Gauge, Histogram

@dataclass
class PerformanceMetrics:
    timestamp: float
    accuracy: float
    loss: float
    latency: float
    memory_usage: float
    cpu_usage: float

class PerformanceMonitor:
    """Advanced performance monitoring system"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.metrics_history: List[PerformanceMetrics] = []
        self.logger = logging.getLogger(__name__)
        
        # Initialize Prometheus metrics
        self.accuracy_gauge = Gauge('model_accuracy', 'Current model accuracy')
        self.training_time_histogram = Histogram(
            'training_time_seconds', 
            'Time spent training',
            buckets=(1, 2, 5, 10, 20, 50)
        )
        self.client_errors_counter = Counter(
            'client_errors_total', 
            'Total number of client errors'
        )
        
    def record_metrics(self, metrics: Dict):
        """Record and export performance metrics"""
        current_metrics = PerformanceMetrics(
            timestamp=time.time(),
            accuracy=metrics.get('accuracy', 0),
            loss=metrics.get('loss', 0),
            latency=metrics.get('latency', 0),
            memory_usage=metrics.get('memory_usage', 0),
            cpu_usage=metrics.get('cpu_usage', 0)
        )
        
        self.metrics_history.append(current_metrics)
        self._export_metrics(current_metrics)
        self._check_alerts(current_metrics)