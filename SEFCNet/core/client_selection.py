from typing import List, Dict, Optional
import numpy as np
from dataclasses import dataclass
import logging

@dataclass
class ClientScore:
    client_id: str
    performance_score: float
    reliability_score: float
    resource_score: float
    final_score: float

class ClientSelector:
    """Advanced client selection strategy"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.history: Dict[str, List[ClientScore]] = {}
        self.logger = logging.getLogger(__name__)
    
    def select_clients(
        self, 
        available_clients: List[str], 
        client_metrics: Dict[str, Dict]
    ) -> List[str]:
        """Select optimal clients for federation round"""
        scores = []
        
        for client_id in available_clients:
            metrics = client_metrics.get(client_id, {})
            score = self._calculate_client_score(client_id, metrics)
            scores.append(score)
            self._update_history(score)
        
        # Sort by final score and select top N
        selected = sorted(
            scores, 
            key=lambda x: x.final_score, 
            reverse=True
        )[:self.config['federation']['clients_per_round']]
        
        return [s.client_id for s in selected]