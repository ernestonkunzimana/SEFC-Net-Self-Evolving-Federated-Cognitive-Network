"""
Dynamic Aggregation for Federated Learning
==========================================
Dynamic weighting based on real-time conditions
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class DynamicAggregation:
    """
    Dynamic Aggregation for federated learning.
    
    MANDATORY COMPONENT - Not optional
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize dynamic aggregation"""
        self.config = config or {}
        self.adaptation_rate = self.config.get('adaptation_rate', 0.1)
        self.weight_history: List[Dict[str, float]] = []
        
        logger.info("Dynamic Aggregation initialized (MANDATORY)")
    
    def aggregate_dynamically(
        self,
        model_updates: List[np.ndarray],
        node_metadata: List[Dict[str, Any]],
        current_performance: Dict[str, float],
        historical_performance: Optional[Dict[str, List[float]]] = None
    ) -> Dict[str, Any]:
        """
        Aggregate with dynamic weights based on real-time conditions.
        
        This is MANDATORY - all aggregations must be dynamic.
        """
        logger.info("Dynamic aggregation")
        
        if not model_updates:
            return {'aggregated': np.array([]), 'weights': {}}
        
        # Calculate dynamic weights
        weights = self._calculate_dynamic_weights(
            node_metadata, current_performance, historical_performance
        )
        
        # Normalize weights
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v / total_weight for k, v in weights.items()}
        
        # Weighted aggregation
        aggregated = np.zeros_like(model_updates[0])
        for update, metadata in zip(model_updates, node_metadata):
            node_id = metadata.get('id', 'unknown')
            weight = weights.get(node_id, 1.0 / len(model_updates))
            aggregated += update * weight
        
        self.weight_history.append(weights)
        
        return {
            'aggregated': aggregated,
            'weights': weights,
            'aggregation_method': 'dynamic',
            'weight_entropy': self._calculate_weight_entropy(weights)
        }
    
    def _calculate_dynamic_weights(
        self,
        metadata: List[Dict[str, Any]],
        current_perf: Dict[str, float],
        historical_perf: Optional[Dict[str, List[float]]]
    ) -> Dict[str, float]:
        """Calculate dynamic weights"""
        weights = {}
        
        for meta in metadata:
            node_id = meta.get('id', 'unknown')
            
            # Base weight from metadata
            base_weight = (
                0.3 * meta.get('data_quality', 0.5) +
                0.3 * meta.get('reliability', 0.5) +
                0.4 * current_perf.get(node_id, 0.5)
            )
            
            # Adjust based on historical performance trend
            if historical_perf and node_id in historical_perf:
                history = historical_perf[node_id]
                if len(history) > 1:
                    trend = (history[-1] - history[0]) / len(history)
                    base_weight += trend * 0.2  # Reward improving nodes
            
            weights[node_id] = max(0.0, base_weight)
        
        return weights
    
    def _calculate_weight_entropy(self, weights: Dict[str, float]) -> float:
        """Calculate entropy of weight distribution"""
        if not weights:
            return 0.0
        
        weight_values = np.array(list(weights.values()))
        weight_values = weight_values[weight_values > 0]  # Remove zeros
        
        if len(weight_values) == 0:
            return 0.0
        
        # Normalize
        weight_values = weight_values / weight_values.sum()
        
        # Calculate entropy
        entropy = -np.sum(weight_values * np.log(weight_values + 1e-10))
        return float(entropy)

