"""
Dashboard Module for SEFCNet
=========================

This module provides comprehensive dashboard and visualization
capabilities for the SEFCNet platform.
"""

from .dashboard_manager import (
    dashboard_manager,
    DashboardConfig
)
from .routes import router as dashboard_router
from .visualization import (
    ModelVisualization,
    NetworkVisualization,
    PerformanceVisualization,
    DataVisualization
)

__all__ = [
    'dashboard_manager',
    'DashboardConfig',
    'dashboard_router',
    'ModelVisualization',
    'NetworkVisualization',
    'PerformanceVisualization',
    'DataVisualization'
]
