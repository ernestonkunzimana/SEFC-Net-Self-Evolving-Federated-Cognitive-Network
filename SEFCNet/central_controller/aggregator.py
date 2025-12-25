"""
Federated aggregation strategies: FedAvg, FedProx, FedMeta.
"""
from typing import List, Dict
import numpy as np


class FedAvgAggregator:
    """Standard Federated Averaging."""
    
    @staticmethod
    def aggregate(parameters: List[List[np.ndarray]], weights: List[int]) -> List[np.ndarray]:
        """Weighted average of parameters."""
        if not parameters:
            return []
        
        num_layers = len(parameters[0])
        aggregated = []
        
        for layer_idx in range(num_layers):
            layer_params = [p[layer_idx] for p in parameters]
            total_weight = sum(weights)
            
            if total_weight == 0:
                aggregated.append(layer_params[0])
                continue
            
            weighted_sum = sum(
                w * layer_param 
                for w, layer_param in zip(weights, layer_params)
            )
            aggregated.append(weighted_sum / total_weight)
        
        return aggregated


class FedProxAggregator(FedAvgAggregator):
    """FedProx with proximal term."""
    
    def __init__(self, mu: float = 0.01):
        self.mu = mu
    
    def aggregate(self, parameters: List[List[np.ndarray]], weights: List[int], 
                  global_params: List[np.ndarray]) -> List[np.ndarray]:
        """FedProx aggregation with regularization."""
        # Simplified: use FedAvg for now, add proximal term if needed
        return super().aggregate(parameters, weights)


class FedMetaAggregator(FedAvgAggregator):
    """Meta-learning aggregation (MAML-style)."""
    
    def aggregate(self, parameters: List[List[np.ndarray]], weights: List[int],
                  meta_gradients: List[List[np.ndarray]] = None) -> List[np.ndarray]:
        """Meta-learning aware aggregation."""
        # Start with standard FedAvg
        base = super().aggregate(parameters, weights)
        
        # Apply meta-gradient updates if provided
        if meta_gradients:
            # Simplified meta-update
            for i, grad in enumerate(meta_gradients):
                if i < len(base):
                    base[i] -= 0.01 * grad  # alpha * meta_grad
        
        return base