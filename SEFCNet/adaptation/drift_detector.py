"""
Concept Drift Detector for Federated Learning
=============================================
Detect distribution shifts in real-time
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import deque

logger = logging.getLogger(__name__)


class ConceptDriftDetector:
    """
    Concept Drift Detector for federated learning.
    
    MANDATORY COMPONENT - Not optional
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize drift detector"""
        self.config = config or {}
        self.drift_threshold = self.config.get('drift_threshold', 0.3)
        self.window_size = self.config.get('window_size', 100)
        self.reference_window = deque(maxlen=self.window_size)
        self.drift_history: List[Dict[str, Any]] = []
        
        logger.info("Concept Drift Detector initialized (MANDATORY)")
    
    def detect_drift(
        self,
        current_data: np.ndarray,
        current_performance: float
    ) -> Dict[str, Any]:
        """
        Detect concept drift in data distribution.
        
        This is MANDATORY - all data must be monitored for drift.
        """
        drift_detected = False
        drift_magnitude = 0.0
        
        if len(self.reference_window) >= self.window_size:
            # Compare current data with reference window
            reference_data = np.array(list(self.reference_window))
            
            # Statistical test for drift (simplified)
            current_mean = np.mean(current_data)
            reference_mean = np.mean(reference_data)
            
            current_std = np.std(current_data)
            reference_std = np.std(reference_data)
            
            # Calculate drift magnitude
            mean_drift = abs(current_mean - reference_mean) / (reference_std + 1e-6)
            std_drift = abs(current_std - reference_std) / (reference_std + 1e-6)
            
            drift_magnitude = (mean_drift + std_drift) / 2.0
            
            if drift_magnitude > self.drift_threshold:
                drift_detected = True
        
        # Update reference window
        self.reference_window.append(current_data)
        
        if drift_detected:
            drift_record = {
                'drift_detected': True,
                'drift_magnitude': drift_magnitude,
                'performance_impact': self._estimate_performance_impact(current_performance),
                'timestamp': datetime.now().isoformat()
            }
            self.drift_history.append(drift_record)
            logger.warning(f"Concept drift detected! Magnitude: {drift_magnitude:.3f}")
        
        return {
            'drift_detected': drift_detected,
            'drift_magnitude': drift_magnitude,
            'current_performance': current_performance,
            'requires_adaptation': drift_detected
        }
    
    def _estimate_performance_impact(self, current_performance: float) -> float:
        """Estimate performance impact of drift"""
        # Simplified estimation
        return max(0.0, 0.1 - current_performance)

