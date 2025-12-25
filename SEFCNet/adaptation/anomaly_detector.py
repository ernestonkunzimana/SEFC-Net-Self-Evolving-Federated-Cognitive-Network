"""
Anomaly Detector for Federated Learning
=======================================
Detect anomalies in federated learning operations
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import deque

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """
    Anomaly Detector for federated learning.
    
    MANDATORY COMPONENT - Not optional
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize anomaly detector"""
        self.config = config or {}
        self.anomaly_threshold = self.config.get('anomaly_threshold', 3.0)  # 3 sigma
        self.history = deque(maxlen=100)
        self.anomalies_detected: List[Dict[str, Any]] = []
        
        logger.info("Anomaly Detector initialized (MANDATORY)")
    
    def detect_anomalies(
        self,
        metrics: Dict[str, float],
        node_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Detect anomalies in federated learning metrics.
        
        This is MANDATORY - all operations must be monitored for anomalies.
        """
        anomalies = []
        
        for metric_name, value in metrics.items():
            if len(self.history) > 10:
                # Calculate statistics
                historical_values = [h.get(metric_name, value) for h in self.history]
                mean = np.mean(historical_values)
                std = np.std(historical_values)
                
                if std > 0:
                    z_score = abs(value - mean) / std
                    
                    if z_score > self.anomaly_threshold:
                        anomaly = {
                            'metric': metric_name,
                            'value': value,
                            'expected_range': (mean - self.anomaly_threshold * std, mean + self.anomaly_threshold * std),
                            'z_score': z_score,
                            'severity': 'high' if z_score > 4.0 else 'medium',
                            'node_id': node_id,
                            'timestamp': datetime.now().isoformat()
                        }
                        anomalies.append(anomaly)
                        logger.warning(f"Anomaly detected in {metric_name}: z-score={z_score:.2f}")
        
        # Update history
        self.history.append(metrics)
        
        if anomalies:
            self.anomalies_detected.extend(anomalies)
        
        return {
            'anomalies_detected': len(anomalies) > 0,
            'anomalies': anomalies,
            'total_anomalies': len(self.anomalies_detected)
        }

