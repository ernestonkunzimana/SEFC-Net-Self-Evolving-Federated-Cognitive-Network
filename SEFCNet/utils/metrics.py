"""
Metrics computation utilities.
"""
from typing import List, Dict
import numpy as np


def compute_accuracy(y_true: List, y_pred: List) -> float:
    """Compute accuracy."""
    return sum(a == b for a, b in zip(y_true, y_pred)) / len(y_true) if y_true else 0.0


def compute_loss_distribution(losses: List[float]) -> Dict[str, float]:
    """Compute loss statistics."""
    if not losses:
        return {}
    
    return {
        "mean": float(np.mean(losses)),
        "std": float(np.std(losses)),
        "min": float(np.min(losses)),
        "max": float(np.max(losses))
    }


def aggregate_metrics(metrics_list: List[Dict], weights: List[int] = None) -> Dict:
    """Weighted aggregation of metrics."""
    if not metrics_list:
        return {}
    
    if weights is None:
        weights = [1] * len(metrics_list)
    
    total_weight = sum(weights)
    aggregated = {}
    
    for key in metrics_list[0].keys():
        if isinstance(metrics_list[0][key], (int, float)):
            aggregated[key] = sum(
                m.get(key, 0) * w for m, w in zip(metrics_list, weights)
            ) / total_weight
    
    return aggregated