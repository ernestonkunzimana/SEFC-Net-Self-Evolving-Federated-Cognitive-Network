from typing import Dict, List
import numpy as np
from dataclasses import dataclass

@dataclass
class RewardConfig:
    accuracy_weight: float = 0.6
    complexity_weight: float = 0.2
    efficiency_weight: float = 0.2
    history_window: int = 10

class RewardEngine:
    """Autonomous reward computation engine"""
    
    def __init__(self, config: RewardConfig):
        self.config = config
        self.history: List[Dict] = []
        
    def compute_reward(self, metrics: Dict) -> float:
        """Compute reward based on multiple factors"""
        accuracy_reward = self._compute_accuracy_reward(metrics['accuracy'])
        complexity_reward = self._compute_complexity_reward(metrics['model_size'])
        efficiency_reward = self._compute_efficiency_reward(metrics['training_time'])
        
        total_reward = (
            self.config.accuracy_weight * accuracy_reward +
            self.config.complexity_weight * complexity_reward +
            self.config.efficiency_weight * efficiency_reward
        )
        
        self.history.append(metrics)
        return total_reward
        
    def _compute_accuracy_reward(self, accuracy: float) -> float:
        """Compute reward based on accuracy improvement"""
        if not self.history:
            return 0.0
        return accuracy - self.history[-1]["accuracy"]
        
    def _compute_complexity_reward(self, model_size: float) -> float:
        """Compute reward based on model complexity"""
        return -model_size  # Simpler models are preferred
        
    def _compute_efficiency_reward(self, training_time: float) -> float:
        """Compute reward based on training efficiency"""
        return -training_time  # Less training time is preferred