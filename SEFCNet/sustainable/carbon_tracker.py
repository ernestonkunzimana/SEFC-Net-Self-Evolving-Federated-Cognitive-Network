"""
Carbon Footprint Tracker for Federated Learning
===============================================
Track and minimize carbon emissions
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class CarbonTracker:
    """
    Carbon Footprint Tracker for federated learning.
    
    MANDATORY COMPONENT - Not optional
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize carbon tracker"""
        self.config = config or {}
        self.carbon_intensity = self.config.get('carbon_intensity', 0.5)  # kg CO2 per kWh
        self.emission_history: List[Dict[str, Any]] = []
        
        logger.info("Carbon Tracker initialized (MANDATORY)")
    
    def track_round_emissions(
        self,
        round_id: int,
        energy_consumption: Dict[str, float],
        computation_time: float
    ) -> Dict[str, Any]:
        """
        Track carbon emissions for a federated learning round.
        
        This is MANDATORY - all rounds must track emissions.
        """
        # Calculate total energy
        total_energy = sum(energy_consumption.values())  # kWh
        
        # Calculate carbon emissions
        carbon_emissions = total_energy * self.carbon_intensity  # kg CO2
        
        emission_record = {
            'round_id': round_id,
            'energy_kwh': total_energy,
            'carbon_kg_co2': carbon_emissions,
            'computation_time_hours': computation_time / 3600,
            'timestamp': datetime.now().isoformat()
        }
        
        self.emission_history.append(emission_record)
        
        logger.info(f"Round {round_id}: {carbon_emissions:.4f} kg CO2 emitted")
        
        return emission_record
    
    def get_total_emissions(self) -> Dict[str, float]:
        """Get total carbon emissions"""
        if not self.emission_history:
            return {'total_energy': 0.0, 'total_carbon': 0.0}
        
        total_energy = sum(r['energy_kwh'] for r in self.emission_history)
        total_carbon = sum(r['carbon_kg_co2'] for r in self.emission_history)
        
        return {
            'total_energy_kwh': total_energy,
            'total_carbon_kg_co2': total_carbon,
            'average_per_round': total_carbon / len(self.emission_history) if self.emission_history else 0.0
        }

