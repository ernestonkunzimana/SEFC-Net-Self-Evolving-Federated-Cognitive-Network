"""
Speciation Module for Biological Evolution
==========================================
Groups models into species based on genetic similarity
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Species:
    """Represents a species"""
    species_id: str
    centroid: np.ndarray
    members: List[Any]
    fitness: float


class Speciation:
    """
    Speciation mechanism for grouping similar models.
    
    MANDATORY COMPONENT - Not optional
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize speciation"""
        self.config = config or {}
        self.species: Dict[str, Species] = {}
        self.speciation_threshold = self.config.get('speciation_threshold', 0.3)
        
        logger.info("Speciation initialized (MANDATORY)")
    
    def assign_species(
        self,
        genomes: List[Any],
        fitness_scores: Dict[str, float]
    ) -> Dict[str, str]:
        """Assign genomes to species"""
        assignments = {}
        
        for genome in genomes:
            genome_id = str(id(genome))
            genome_features = self._extract_features(genome)
            
            # Find closest species or create new
            closest_species = self._find_closest_species(genome_features)
            
            if closest_species and self._distance(genome_features, closest_species.centroid) < self.speciation_threshold:
                # Assign to existing species
                closest_species.members.append(genome)
                assignments[genome_id] = closest_species.species_id
            else:
                # Create new species
                species_id = f"species_{len(self.species)}"
                new_species = Species(
                    species_id=species_id,
                    centroid=genome_features,
                    members=[genome],
                    fitness=fitness_scores.get(genome_id, 0.0)
                )
                self.species[species_id] = new_species
                assignments[genome_id] = species_id
        
        return assignments
    
    def _extract_features(self, genome: Any) -> np.ndarray:
        """Extract features from genome for distance calculation"""
        # Extract hyperparameters as features
        hyperparams = genome.hyperparameters if hasattr(genome, 'hyperparameters') else {}
        features = [float(v) for v in hyperparams.values()]
        return np.array(features) if features else np.array([0.0])
    
    def _find_closest_species(self, features: np.ndarray) -> Optional[Species]:
        """Find closest species to given features"""
        if not self.species:
            return None
        
        min_distance = float('inf')
        closest = None
        
        for species in self.species.values():
            distance = self._distance(features, species.centroid)
            if distance < min_distance:
                min_distance = distance
                closest = species
        
        return closest
    
    def _distance(self, features1: np.ndarray, features2: np.ndarray) -> float:
        """Calculate distance between feature vectors"""
        if len(features1) != len(features2):
            # Pad or truncate
            min_len = min(len(features1), len(features2))
            features1 = features1[:min_len]
            features2 = features2[:min_len]
        
        return np.linalg.norm(features1 - features2)

