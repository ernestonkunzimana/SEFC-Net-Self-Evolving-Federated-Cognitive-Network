from typing import Dict, List
import psutil
import logging
from dataclasses import dataclass
from prometheus_client import start_http_server, Gauge
import threading
import time

@dataclass
class SystemState:
    cpu_usage: float
    memory_usage: float
    network_io: Dict[str, int]
    disk_usage: float
    process_count: int

class SystemMonitor:
    """Monitors system resources and performance"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._initialize_metrics()
        self._start_monitoring()

    def _initialize_metrics(self):
        """Initialize Prometheus metrics"""
        self.metrics = {
            'cpu': Gauge('system_cpu_usage', 'CPU usage percentage'),
            'memory': Gauge('system_memory_usage', 'Memory usage percentage'),
            'network_in': Gauge('system_network_in', 'Network bytes received'),
            'network_out': Gauge('system_network_out', 'Network bytes sent')
        }