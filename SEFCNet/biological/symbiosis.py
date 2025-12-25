"""
Symbiosis Module for Biological Evolution
==========================================
Models help each other improve through symbiotic relationships
"""

import logging
from typing import Dict, List, Optional, Any
import random

logger = logging.getLogger(__name__)


class Symbiosis:
    """
    Symbiosis mechanism for models to help each other.
    
    MANDATORY COMPONENT - Not optional
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize symbiosis"""
        self.config = config or {}
        self.symbiotic_pairs: List[tuple] = []
        self.benefit_rate = self.config.get('benefit_rate', 0.1)
        
        logger.info("Symbiosis initialized (MANDATORY)")
    
    def form_symbiotic_relationships(
        self,
        genomes: List[Any],
        fitness_scores: Dict[str, float]
    ) -> Dict[str, float]:
        """Form symbiotic relationships and calculate benefits"""
        benefits = {}
        
        for genome in genomes:
            genome_id = str(id(genome))
            current_fitness = fitness_scores.get(genome_id, 0.0)
            
            # Find symbiotic partner (complementary, different species)
            partner = self._find_symbiotic_partner(genome, genomes, fitness_scores)
            
            if partner:
                # Calculate symbiotic benefit
                benefit = self._calculate_benefit(genome, partner, fitness_scores)
                benefits[genome_id] = benefit
                self.symbiotic_pairs.append((genome_id, str(id(partner))))
            else:
                benefits[genome_id] = 0.0
        
        return benefits
    
    def _find_symbiotic_partner(
        self,
        genome: Any,
        all_genomes: List[Any],
        fitness_scores: Dict[str, float]
    ) -> Optional[Any]:
        """Find a symbiotic partner for a genome"""
        # Find complementary genomes (different species, higher fitness)
        candidates = [
            g for g in all_genomes
            if (hasattr(g, 'species_id') and hasattr(genome, 'species_id') and
                g.species_id != genome.species_id and
                fitness_scores.get(str(id(g)), 0.0) > fitness_scores.get(str(id(genome)), 0.0))
        ]
        
        if candidates:
            return random.choice(candidates)
        return None
    
    def _calculate_benefit(
        self,
        genome1: Any,
        genome2: Any,
        fitness_scores: Dict[str, Any]
    ) -> float:
        """Calculate symbiotic benefit"""
        fitness1 = fitness_scores.get(str(id(genome1)), 0.0)
        fitness2 = fitness_scores.get(str(id(genome2)), 0.0)
        
        # Benefit is proportional to partner's advantage
        benefit = (fitness2 - fitness1) * self.benefit_rate
        return max(0.0, benefit)

