"""
Green Federated Learning
========================
Sustainable and energy-efficient federated learning
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .carbon_tracker import CarbonTracker
from .energy_optimizer import EnergyOptimizer

logger = logging.getLogger(__name__)


class GreenFederatedLearning:
    """
    Green Federated Learning System.
    
    MANDATORY COMPONENT - Not optional
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize green FL"""
        self.config = config or {}
        self.carbon_tracker = CarbonTracker(self.config.get('carbon', {}))
        self.energy_optimizer = EnergyOptimizer(self.config.get('energy', {}))
        
        logger.info("Green Federated Learning initialized (MANDATORY)")
    
    def process_green_round(
        self,
        round_id: int,
        nodes: List[Dict[str, Any]],
        computation_requirements: Dict[str, float],
        computation_time: float
    ) -> Dict[str, Any]:
        """
        Process federated learning round with sustainability focus.
        
        This is MANDATORY - all rounds must be sustainable.
        """
        logger.info(f"Processing green FL round {round_id}")
        
        # Optimize energy consumption
        energy_optimization = self.energy_optimizer.optimize_energy_consumption(
            nodes, computation_requirements
        )
        
        # Track carbon emissions
        energy_consumption = energy_optimization['schedule']['energy_allocation']
        carbon_tracking = self.carbon_tracker.track_round_emissions(
            round_id, energy_consumption, computation_time
        )
        
        return {
            'round_id': round_id,
            'energy_optimization': energy_optimization,
            'carbon_tracking': carbon_tracking,
            'sustainability_score': self._calculate_sustainability_score(
                energy_optimization, carbon_tracking
            ),
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_sustainability_score(
        self,
        energy_opt: Dict[str, Any],
        carbon_track: Dict[str, Any]
    ) -> float:
        """Calculate overall sustainability score"""
        energy_score = min(1.0, 1.0 - (carbon_track['carbon_kg_co2'] / 10.0))  # Normalize
        efficiency_score = energy_opt.get('energy_savings_percent', 0.0) / 100.0
        
        return (energy_score + efficiency_score) / 2.0

