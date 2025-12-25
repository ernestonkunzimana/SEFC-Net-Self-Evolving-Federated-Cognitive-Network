"""
Enterprise Monitoring Service for SEFCNet
======================================

Provides comprehensive monitoring capabilities:
- Real-time system monitoring
- Anomaly detection
- Alert management
- Health checks
- Performance profiling
- Resource monitoring
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple
import json
from dataclasses import dataclass
import threading
from concurrent.futures import ThreadPoolExecutor

import aiohttp
from prometheus_client.parser import text_string_to_metric_families
import numpy as np
from scipy import stats
import prometheus_client as prom
from prometheus_client import CollectorRegistry, Gauge, Counter, Histogram

from .metrics_collector import metrics_collector

logger = logging.getLogger(__name__)

@dataclass
class Alert:
    """Alert definition with metadata."""
    id: str
    name: str
    description: str
    severity: str  # 'critical', 'warning', 'info'
    timestamp: datetime
    metric_name: str
    threshold: float
    current_value: float
    labels: Dict[str, str]
    status: str  # 'active', 'acknowledged', 'resolved'

@dataclass
class HealthCheck:
    """Health check definition."""
    name: str
    endpoint: str
    interval: int  # seconds
    timeout: int  # seconds
    healthy_threshold: int
    unhealthy_threshold: int

class MonitoringService:
    """Enterprise-grade monitoring service."""

    def __init__(self):
        # Use an instance-local registry to avoid duplicate timeseries in the global registry
        self.registry = CollectorRegistry()

        # initialize metrics with the local registry
        self.metrics = {
            'model_accuracy': Gauge('model_accuracy', 'Current model accuracy', registry=self.registry),
            'training_time_seconds': Histogram(
                'training_time_seconds',
                'Time spent training',
                buckets=(1, 2, 5, 10, 20, 50),
                registry=self.registry
            ),
            'client_errors_total': Counter('client_errors_total', 'Total number of client errors', registry=self.registry)
        }

        self.alert_history: List[Alert] = []
        self.active_alerts: Set[str] = set()
        self.health_checks: Dict[str, HealthCheck] = {}
        self.health_status: Dict[str, bool] = {}
        self._executor = ThreadPoolExecutor(max_workers=4)
        self._monitoring_interval = 30  # seconds
        self._is_monitoring = False
        self._monitoring_task = None
        self._alert_rules: Dict[str, Dict] = {}
        self._setup_default_alert_rules()

    def _setup_default_alert_rules(self):
        """Setup default monitoring alert rules."""
        self._alert_rules = {
            'high_cpu_usage': {
                'metric': 'system_cpu_usage',
                'threshold': 90.0,
                'window': 300,  # 5 minutes
                'severity': 'critical',
                'description': 'CPU usage exceeds 90%'
            },
            'high_memory_usage': {
                'metric': 'system_memory_usage',
                'threshold': 85.0,
                'window': 300,
                'severity': 'warning',
                'description': 'Memory usage exceeds 85%'
            },
            'high_model_latency': {
                'metric': 'model_inference_latency',
                'threshold': 100.0,  # ms
                'window': 600,  # 10 minutes
                'severity': 'warning',
                'description': 'Model inference latency exceeds 100ms'
            },
            'network_error_spike': {
                'metric': 'network_errors',
                'threshold': 10.0,
                'window': 300,
                'severity': 'critical',
                'description': 'Spike in network errors detected'
            }
        }

    async def start_monitoring(self):
        """Start the monitoring service."""
        if self._is_monitoring:
            return

        self._is_monitoring = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())

    async def stop_monitoring(self):
        """Stop the monitoring service."""
        self._is_monitoring = False
        if self._monitoring_task:
            await self._monitoring_task

    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self._is_monitoring:
            try:
                # Collect and analyze metrics
                metrics_snapshot = metrics_collector.get_metrics_snapshot()
                await self._analyze_metrics(metrics_snapshot)

                # Perform health checks
                await self._perform_health_checks()

                # Update alert statuses
                self._update_alert_statuses()

                await asyncio.sleep(self._monitoring_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                await asyncio.sleep(1)

    async def _analyze_metrics(self, metrics: Dict[str, Any]):
        """Analyze metrics for anomalies and threshold violations."""
        for rule_name, rule in self._alert_rules.items():
            metric_name = rule['metric']
            if metric_name in metrics:
                value = metrics[metric_name]
                if isinstance(value, dict):  # Handle labeled metrics
                    for label_combo, label_value in value.items():
                        await self._check_threshold(
                            rule_name, metric_name, label_value,
                            rule['threshold'], rule['severity'],
                            dict(zip(label_combo, label_combo))
                        )
                else:
                    await self._check_threshold(
                        rule_name, metric_name, value,
                        rule['threshold'], rule['severity']
                    )

    async def _check_threshold(
        self,
        rule_name: str,
        metric_name: str,
        value: float,
        threshold: float,
        severity: str,
        labels: Dict[str, str] = None
    ):
        """Check if a metric exceeds its threshold."""
        if value > threshold:
            alert_id = f"{rule_name}_{datetime.utcnow().isoformat()}"
            if alert_id not in self.active_alerts:
                alert = Alert(
                    id=alert_id,
                    name=rule_name,
                    description=self._alert_rules[rule_name]['description'],
                    severity=severity,
                    timestamp=datetime.utcnow(),
                    metric_name=metric_name,
                    threshold=threshold,
                    current_value=value,
                    labels=labels or {},
                    status='active'
                )
                self.alert_history.append(alert)
                self.active_alerts.add(alert_id)
                await self._handle_alert(alert)

    async def _handle_alert(self, alert: Alert):
        """Handle a new alert."""
        # Log the alert
        logger.warning(f"New alert: {alert.name} - {alert.description}")

        # TODO: Implement alert notification (email, Slack, etc.)
        # This would be implemented based on specific requirements

    async def _perform_health_checks(self):
        """Perform registered health checks."""
        async with aiohttp.ClientSession() as session:
            for check_name, check in self.health_checks.items():
                try:
                    async with session.get(
                        check.endpoint,
                        timeout=check.timeout
                    ) as response:
                        is_healthy = response.status == 200
                        self.health_status[check_name] = is_healthy
                        if not is_healthy:
                            logger.warning(f"Health check failed: {check_name}")
                except Exception as e:
                    logger.error(f"Health check error for {check_name}: {str(e)}")
                    self.health_status[check_name] = False

    def _update_alert_statuses(self):
        """Update status of active alerts."""
        current_time = datetime.utcnow()
        metrics_snapshot = metrics_collector.get_metrics_snapshot()

        for alert in self.alert_history:
            if alert.status == 'active':
                # Check if the condition is still valid
                if alert.metric_name in metrics_snapshot:
                    current_value = metrics_snapshot[alert.metric_name]
                    if current_value <= alert.threshold:
                        alert.status = 'resolved'
                        self.active_alerts.remove(alert.id)

    def register_health_check(self, check: HealthCheck):
        """Register a new health check."""
        self.health_checks[check.name] = check
        self.health_status[check.name] = True

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an active alert."""
        for alert in self.alert_history:
            if alert.id == alert_id and alert.status == 'active':
                alert.status = 'acknowledged'
                return True
        return False

    def get_active_alerts(
        self,
        severity: Optional[str] = None
    ) -> List[Alert]:
        """Get currently active alerts."""
        alerts = [
            alert for alert in self.alert_history
            if alert.status == 'active'
        ]
        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]
        return alerts

    def get_alert_history(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Alert]:
        """Get historical alerts within a time range."""
        if not start_time:
            start_time = datetime.min
        if not end_time:
            end_time = datetime.max

        return [
            alert for alert in self.alert_history
            if start_time <= alert.timestamp <= end_time
        ]

    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status."""
        return {
            'healthy': all(self.health_status.values()),
            'checks': self.health_status,
            'active_alerts': len(self.active_alerts),
            'last_updated': datetime.utcnow().isoformat()
        }

    def record_metrics(self, metrics: Dict[str, Any]):
        """Record system metrics"""
        try:
            for key, value in metrics.items():
                if key in self.metrics:
                    self.metrics[key].set(value)
            logger.info(f"Metrics recorded successfully: {metrics}")
        except Exception as e:
            logger.error(f"Error recording metrics: {str(e)}")

    def start_monitoring(self, port: int = 8000):
        """Start the monitoring server"""
        prom.start_http_server(port)
        logger.info(f"Monitoring server started on port {port}")

# Initialize global monitoring service
monitoring_service = MonitoringService()