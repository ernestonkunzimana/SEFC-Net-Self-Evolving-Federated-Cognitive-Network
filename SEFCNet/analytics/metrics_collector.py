"""
Compatibility shim for analytics metrics.

The original design kept metrics collection under the monitoring subsystem.
Tests expect to be able to import `SEFCNet.analytics.metrics_collector.MetricsCollector`,
so this module simply re-exports the implementation from `monitoring.metrics_collector`.
"""

from ..monitoring.metrics_collector import MetricsCollector  # noqa: F401


