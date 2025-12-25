"""
Orchestration Module for SEFCNet
============================

This module provides comprehensive orchestration and coordination
capabilities for the SEFCNet platform.
"""

from .orchestration_manager import (
    orchestration_manager,
    NodeConfig,
    TaskDefinition
)
from .routes import router as orchestration_router

__all__ = [
    'orchestration_manager',
    'NodeConfig',
    'TaskDefinition',
    'orchestration_router'
]