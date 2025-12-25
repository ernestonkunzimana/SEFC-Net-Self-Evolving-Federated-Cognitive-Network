from typing import Dict, List, Optional
import psutil
import logging
from dataclasses import dataclass
from datetime import datetime
from prometheus_client import Gauge, Counter

@dataclass
class SystemHealth:
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, int]
    process_count: int

class HealthMonitor:
    """Monitors system health with alerts"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.health_history: List[SystemHealth] = []
        self.logger = logging.getLogger(__name__)
        self._setup_prometheus_metrics()

    def _setup_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        self.metrics = {
            'cpu_usage': Gauge('system_cpu_usage', 'System CPU usage percentage'),
            'memory_usage': Gauge('system_memory_usage', 'System memory usage percentage'),
            'disk_usage': Gauge('system_disk_usage', 'System disk usage percentage'),
            'process_count': Gauge('system_process_count', 'Number of running processes'),
            'alerts': Counter('system_health_alerts', 'Number of health alerts raised')
        }