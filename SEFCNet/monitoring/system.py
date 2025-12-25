from typing import Dict, List, Optional
import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from prometheus_client import start_http_server, Gauge, Counter, Summary

@dataclass
class MonitoringMetrics:
    """System monitoring metrics"""
    cpu_usage: float
    memory_usage: float
    network_io: Dict[str, float]
    model_performance: Dict[str, float]
    timestamp: datetime

class MonitoringSystem:
    """Comprehensive system monitoring"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.metrics_history: List[MonitoringMetrics] = []
        self.logger = logging.getLogger(__name__)
        self._setup_prometheus()
        self._monitoring_task = None

    async def start_monitoring(self):
        """Start monitoring system"""
        try:
            # Start Prometheus server
            start_http_server(self.config['monitoring']['prometheus_port'])
            
            # Start monitoring loop
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())
            self.logger.info("Monitoring system started")
            
        except Exception as e:
            self.logger.error(f"Monitoring system error: {e}")
            raise