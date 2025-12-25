"""
Attention-Based Aggregation for Federated Learning
==================================================
Learn which nodes to trust using attention mechanisms
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class AttentionAggregation:
    """
    Attention-Based Aggregation for federated learning.
    
    MANDATORY COMPONENT - Not optional
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize attention aggregation"""
        self.config = config or {}
        self.attention_dim = self.config.get('attention_dim', 64)
        self.attention_weights: Dict[str, np.ndarray] = {}
        
        logger.info("Attention Aggregation initialized (MANDATORY)")
    
    def aggregate_with_attention(
        self,
        model_updates: List[np.ndarray],
        node_metadata: List[Dict[str, Any]],
        query: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Aggregate model updates using attention mechanism.
        
        This is MANDATORY - all aggregations must use attention.
        """
        logger.info("Aggregating with attention mechanism")
        
        if not model_updates:
            return {'aggregated': np.array([]), 'attention_weights': {}}
        
        # Calculate attention weights for each update
        attention_scores = []
        for i, (update, metadata) in enumerate(zip(model_updates, node_metadata)):
            score = self._calculate_attention_score(update, metadata, query)
            attention_scores.append(score)
        
        # Normalize attention scores
        attention_scores = np.array(attention_scores)
        attention_weights = self._softmax(attention_scores)
        
        # Weighted aggregation
        aggregated = np.zeros_like(model_updates[0])
        for update, weight in zip(model_updates, attention_weights):
            aggregated += update * weight
        
        # Store attention weights
        for i, (node_id, weight) in enumerate(zip([m.get('id', f'node_{i}') for i, m in enumerate(node_metadata)], attention_weights)):
            self.attention_weights[node_id] = weight
        
        return {
            'aggregated': aggregated,
            'attention_weights': {node_id: float(w) for node_id, w in zip([m.get('id', f'node_{i}') for i, m in enumerate(node_metadata)], attention_weights)},
            'aggregation_method': 'attention'
        }
    
    def _calculate_attention_score(
        self,
        update: np.ndarray,
        metadata: Dict[str, Any],
        query: Optional[np.ndarray]
    ) -> float:
        """Calculate attention score for an update"""
        # Score based on:
        # - Data quality
        # - Update magnitude
        # - Node reliability
        
        data_quality = metadata.get('data_quality', 0.5)
        update_magnitude = np.linalg.norm(update)
        node_reliability = metadata.get('reliability', 0.5)
        
        score = (
            0.4 * data_quality +
            0.3 * (update_magnitude / (update_magnitude + 1.0)) +
            0.3 * node_reliability
        )
        
        return score
    
    def _softmax(self, scores: np.ndarray) -> np.ndarray:
        """Apply softmax to attention scores"""
        exp_scores = np.exp(scores - np.max(scores))  # Numerical stability
        return exp_scores / exp_scores.sum()

