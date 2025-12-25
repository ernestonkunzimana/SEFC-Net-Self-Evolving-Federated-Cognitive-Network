from typing import Dict, List, Optional
import asyncio
import pandas as pd
import numpy as np
from dataclasses import dataclass
import logging
from datetime import datetime

@dataclass
class AnalyticsResult:
    pipeline_id: str
    metrics: Dict[str, float]
    confidence: float
    timestamp: datetime
    metadata: Optional[Dict] = None

class PipelineManager:
    """Manages analytics pipelines with error handling"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.pipelines: Dict[str, callable] = {}
        self.results: List[AnalyticsResult] = []
        self.logger = logging.getLogger(__name__)

    async def register_pipeline(self, pipeline_id: str, pipeline_func: callable):
        """Register new analytics pipeline"""
        if pipeline_id in self.pipelines:
            raise ValueError(f"Pipeline {pipeline_id} already exists")
        
        self.pipelines[pipeline_id] = pipeline_func
        self.logger.info(f"Registered pipeline: {pipeline_id}")

    async def execute_pipeline(self, pipeline_id: str, data: Dict) -> AnalyticsResult:
        """Execute specific analytics pipeline"""
        if pipeline_id not in self.pipelines:
            raise ValueError(f"Unknown pipeline: {pipeline_id}")
            
        try:
            result = await self.pipelines[pipeline_id](data)
            self.results.append(result)
            return result
        except Exception as e:
            self.logger.error(f"Pipeline {pipeline_id} error: {e}")
            raise