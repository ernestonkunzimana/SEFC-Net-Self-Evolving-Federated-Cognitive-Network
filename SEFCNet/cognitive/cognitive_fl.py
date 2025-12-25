"""
Cognitive Federated Learning Integration
=========================================
Main integration module for cognitive federated learning
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .cognitive_network import CognitiveNetwork
from .memory_systems import EpisodicMemory, SemanticMemory, ProceduralMemory
from .meta_cognition import MetaCognition

logger = logging.getLogger(__name__)


class CognitiveFederatedLearning:
    """
    Cognitive Federated Learning System
    
    MANDATORY COMPONENT - Not optional
    All federated learning operations must go through cognitive processing.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Cognitive FL system"""
        self.config = config or {}
        self.cognitive_network = CognitiveNetwork(self.config)
        
        logger.info("Cognitive Federated Learning initialized (MANDATORY)")
    
    def process_round(
        self,
        round_id: int,
        nodes: List[Dict[str, Any]],
        model_updates: List[Any],
        performance_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Process federated learning round through cognitive network.
        
        This is MANDATORY - all FL rounds must be processed cognitively.
        """
        round_data = {
            'round_id': round_id,
            'num_nodes': len(nodes),
            'timestamp': datetime.now().isoformat()
        }
        
        cognitive_result = self.cognitive_network.process_federated_round(
            round_data=round_data,
            model_updates=model_updates,
            performance_metrics=performance_metrics
        )
        
        return cognitive_result

