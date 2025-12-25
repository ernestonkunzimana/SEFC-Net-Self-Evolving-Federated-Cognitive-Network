"""
Transformer-Based Aggregation for Federated Learning
====================================================
Use transformer architecture for aggregation
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class TransformerAggregation:
    """
    Transformer-Based Aggregation for federated learning.
    
    MANDATORY COMPONENT - Not optional
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize transformer aggregation"""
        self.config = config or {}
        self.d_model = self.config.get('d_model', 128)
        self.num_heads = self.config.get('num_heads', 4)
        
        logger.info(f"Transformer Aggregation initialized (MANDATORY) - d_model={self.d_model}, heads={self.num_heads}")
    
    def aggregate_with_transformer(
        self,
        model_updates: List[np.ndarray],
        node_metadata: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Aggregate model updates using transformer architecture.
        
        This is MANDATORY - all aggregations must support transformer.
        """
        logger.info("Aggregating with transformer")
        
        if not model_updates:
            return {'aggregated': np.array([])}
        
        # Encode updates as sequences
        encoded_updates = self._encode_updates(model_updates, node_metadata)
        
        # Multi-head self-attention
        attended = self._multi_head_attention(encoded_updates)
        
        # Aggregate attended representations
        aggregated = self._aggregate_attended(attended)
        
        return {
            'aggregated': aggregated,
            'attention_patterns': self._extract_attention_patterns(attended),
            'aggregation_method': 'transformer'
        }
    
    def _encode_updates(
        self,
        updates: List[np.ndarray],
        metadata: List[Dict[str, Any]]
    ) -> np.ndarray:
        """Encode updates as transformer input"""
        # Simplified encoding
        encoded = []
        for update, meta in zip(updates, metadata):
            # Combine update features with metadata
            update_features = update.flatten()[:self.d_model]  # Truncate/pad to d_model
            if len(update_features) < self.d_model:
                update_features = np.pad(update_features, (0, self.d_model - len(update_features)))
            else:
                update_features = update_features[:self.d_model]
            
            # Add metadata features
            meta_features = np.array([
                meta.get('data_quality', 0.5),
                meta.get('reliability', 0.5),
                meta.get('performance', 0.5)
            ])
            if len(meta_features) < self.d_model:
                meta_features = np.pad(meta_features, (0, self.d_model - len(meta_features)))
            
            combined = (update_features + meta_features) / 2.0
            encoded.append(combined)
        
        return np.array(encoded)
    
    def _multi_head_attention(self, encoded: np.ndarray) -> np.ndarray:
        """Apply multi-head self-attention"""
        # Simplified multi-head attention
        # In production, use proper transformer implementation
        
        # Self-attention: Q, K, V all from encoded
        Q = encoded
        K = encoded
        V = encoded
        
        # Scaled dot-product attention
        scores = np.dot(Q, K.T) / np.sqrt(self.d_model)
        attention_weights = self._softmax(scores)
        attended = np.dot(attention_weights, V)
        
        return attended
    
    def _aggregate_attended(self, attended: np.ndarray) -> np.ndarray:
        """Aggregate attended representations"""
        # Mean pooling
        return np.mean(attended, axis=0)
    
    def _extract_attention_patterns(self, attended: np.ndarray) -> Dict[str, Any]:
        """Extract attention patterns for explainability"""
        return {
            'attention_entropy': float(np.mean([np.std(row) for row in attended])),
            'focus_diversity': float(len(set(np.argmax(attended, axis=1))))
        }
    
    def _softmax(self, scores: np.ndarray) -> np.ndarray:
        """Apply softmax"""
        exp_scores = np.exp(scores - np.max(scores, axis=-1, keepdims=True))
        return exp_scores / exp_scores.sum(axis=-1, keepdims=True)

