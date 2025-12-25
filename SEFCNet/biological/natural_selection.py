"""
Natural Selection Module for Biological Evolution
=================================================
Survival of the fittest mechanism
"""

import logging
from typing import Dict, List, Optional, Any
import random

logger = logging.getLogger(__name__)


class NaturalSelection:
    """
    Natural Selection mechanism.
    
    MANDATORY COMPONENT - Not optional
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize natural selection"""
        self.config = config or {}
        self.selection_method = self.config.get('selection_method', 'tournament')
        self.elite_size = self.config.get('elite_size', 5)
        self.tournament_size = self.config.get('tournament_size', 3)
        
        logger.info("Natural Selection initialized (MANDATORY)")
    
    def select(
        self,
        genomes: List[Any],
        fitness_scores: Dict[str, float],
        num_selected: int
    ) -> List[Any]:
        """Select genomes based on fitness"""
        if self.selection_method == 'tournament':
            return self._tournament_selection(genomes, fitness_scores, num_selected)
        elif self.selection_method == 'elite':
            return self._elite_selection(genomes, fitness_scores, num_selected)
        else:
            return self._roulette_selection(genomes, fitness_scores, num_selected)
    
    def _tournament_selection(
        self,
        genomes: List[Any],
        fitness_scores: Dict[str, float],
        num_selected: int
    ) -> List[Any]:
        """Tournament selection"""
        selected = []
        
        # Keep elite
        elite = sorted(
            genomes,
            key=lambda g: fitness_scores.get(str(id(g)), 0.0),
            reverse=True
        )[:self.elite_size]
        selected.extend(elite)
        
        # Tournament selection for rest
        while len(selected) < num_selected:
            tournament = random.sample(
                genomes,
                min(self.tournament_size, len(genomes))
            )
            winner = max(
                tournament,
                key=lambda g: fitness_scores.get(str(id(g)), 0.0)
            )
            selected.append(winner)
        
        return selected[:num_selected]
    
    def _elite_selection(
        self,
        genomes: List[Any],
        fitness_scores: Dict[str, float],
        num_selected: int
    ) -> List[Any]:
        """Elite selection - keep only the best"""
        sorted_genomes = sorted(
            genomes,
            key=lambda g: fitness_scores.get(str(id(g)), 0.0),
            reverse=True
        )
        return sorted_genomes[:num_selected]
    
    def _roulette_selection(
        self,
        genomes: List[Any],
        fitness_scores: Dict[str, float],
        num_selected: int
    ) -> List[Any]:
        """Roulette wheel selection"""
        # Calculate probabilities
        fitnesses = [fitness_scores.get(str(id(g)), 0.0) for g in genomes]
        min_fitness = min(fitnesses)
        adjusted_fitnesses = [f - min_fitness + 0.01 for f in fitnesses]  # Avoid zero
        total = sum(adjusted_fitnesses)
        probabilities = [f / total for f in adjusted_fitnesses]
        
        # Select based on probabilities
        selected = random.choices(genomes, weights=probabilities, k=num_selected)
        return selected

