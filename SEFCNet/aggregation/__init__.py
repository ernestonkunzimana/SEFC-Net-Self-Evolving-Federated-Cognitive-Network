"""
Novel Aggregation Methods for SEFCNet
=====================================
Mandatory component for attention-based and transformer-based aggregation
"""

from .attention_aggregation import AttentionAggregation
from .transformer_aggregation import TransformerAggregation
from .dynamic_aggregation import DynamicAggregation

__all__ = [
    'AttentionAggregation',
    'TransformerAggregation',
    'DynamicAggregation'
]

