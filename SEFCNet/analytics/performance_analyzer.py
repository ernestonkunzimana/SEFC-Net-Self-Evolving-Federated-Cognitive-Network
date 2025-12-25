from typing import Any, Dict, List, Optional
import numpy as np
from dataclasses import dataclass
import logging
from datetime import datetime

@dataclass
class ModelPerformance:
    accuracy: float
    loss: float
    training_time: float
    evolution_gain: float
    timestamp: datetime

class PerformanceAnalyzer:
    """Analyzes model performance metrics"""

    def __init__(self, config: Dict):
        self.config = config
        self.performance_history: List[ModelPerformance] = []
        self.logger = logging.getLogger(__name__)

    def analyze_performance(self, metrics: Dict) -> Dict[str, Any]:
        """Analyze current performance metrics and provide summary insights."""
        performance = self._build_performance(metrics)
        self.performance_history.append(performance)
        self._check_performance_thresholds(performance)
        return {
            'trend': {'accuracy': performance.accuracy, 'loss': performance.loss},
            'anomalies': self._detect_anomalies(performance),
            'recommendations': self._generate_recommendations(performance),
            'summary': performance
        }

    def analyze_round(self, metrics: Dict) -> ModelPerformance:
        """Compatibility method used by tests to analyze a single FL round."""
        performance = self._build_performance(metrics)
        self.performance_history.append(performance)
        self._check_performance_thresholds(performance)
        return performance

    def _calculate_evolution_gain(self, metrics: Dict) -> float:
        baseline = metrics.get('baseline_accuracy', metrics.get('accuracy', 0.0))
        return metrics.get('accuracy', 0.0) - baseline

    def _check_performance_thresholds(self, performance: ModelPerformance) -> None:
        threshold = self.config.get('analytics', {}).get('performance_threshold', 0.0)
        if performance.accuracy < threshold:
            self.logger.warning("Performance below threshold: %.2f", performance.accuracy)

    def _detect_anomalies(self, performance: ModelPerformance) -> List[Dict[str, float]]:
        return []

    def _generate_recommendations(self, performance: ModelPerformance) -> List[str]:
        if performance.evolution_gain > 0:
            return ["Continue current optimization strategy"]
        return ["Investigate data quality and learning rate"]

    def _build_performance(self, metrics: Dict) -> ModelPerformance:
        return ModelPerformance(
            accuracy=metrics.get('accuracy', 0.0),
            loss=metrics.get('loss', 0.0),
            training_time=metrics.get('training_time', 0.0),
            evolution_gain=self._calculate_evolution_gain(metrics),
            timestamp=datetime.now()
        )