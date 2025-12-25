from typing import Dict, List, Optional
import numpy as np
from dataclasses import dataclass
import logging
from datetime import datetime

@dataclass
class PerformanceMetrics:
    timestamp: datetime
    accuracy: float
    loss: float
    training_time: float
    evolution_score: float
    resource_efficiency: float

class PerformanceAnalyzer:
    """Analyzes system performance with advanced metrics"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.metrics_history: List[PerformanceMetrics] = []
        self.logger = logging.getLogger(__name__)

    async def analyze_round_performance(self, metrics: Dict) -> PerformanceMetrics:
        """Analyze performance for current round"""
        try:
            performance = PerformanceMetrics(
                timestamp=datetime.now(),
                accuracy=metrics.get('accuracy', 0.0),
                loss=metrics.get('loss', float('inf')),
                training_time=metrics.get('training_time', 0.0),
                evolution_score=await self._calculate_evolution_score(metrics),
                resource_efficiency=await self._calculate_resource_efficiency(metrics)
            )
            
            self.metrics_history.append(performance)
            await self._check_performance_thresholds(performance)
            
            return performance
            
        except Exception as e:
            self.logger.error(f"Performance analysis error: {e}")
            raise