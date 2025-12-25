"""
Biological Evolution Engine for SEFCNet
========================================
Genetic algorithms, speciation, symbiosis, and natural selection for FL models
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import random

logger = logging.getLogger(__name__)


@dataclass
class ModelGenome:
    """Represents a model's genetic code"""
    architecture: Dict[str, Any]
    hyperparameters: Dict[str, float]
    fitness: float = 0.0
    generation: int = 0
    species_id: Optional[str] = None
    mutations: List[str] = field(default_factory=list)


@dataclass
class Species:
    """Represents a species of models"""
    species_id: str
    members: List[ModelGenome]
    average_fitness: float
    niche: Dict[str, Any]  # Ecological niche
    created_at: datetime


class BiologicalEvolutionEngine:
    """
    Biological Evolution Engine
    Implements genetic algorithms, speciation, symbiosis, and natural selection.
    
    MANDATORY COMPONENT - Not optional
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize biological evolution engine"""
        self.config = config or {}
        self.population: List[ModelGenome] = []
        self.species: Dict[str, Species] = {}
        self.generation = 0
        self.mutation_rate = self.config.get('mutation_rate', 0.1)
        self.crossover_rate = self.config.get('crossover_rate', 0.7)
        self.population_size = self.config.get('population_size', 50)
        self.elite_size = self.config.get('elite_size', 5)
        
        logger.info("Biological Evolution Engine initialized (MANDATORY)")
    
    def evolve_population(
        self,
        fitness_scores: Dict[str, float]
    ) -> List[ModelGenome]:
        """
        Evolve population through biological mechanisms.
        
        This is MANDATORY - all model evolution must go through biological processes.
        """
        self.generation += 1
        logger.info(f"Biological evolution generation {self.generation}")
        
        # Update fitness scores
        for genome in self.population:
            genome.fitness = fitness_scores.get(str(id(genome)), 0.0)
        
        # Natural Selection: Select fittest individuals
        selected = self._natural_selection()
        
        # Speciation: Group into species
        self._speciate(selected)
        
        # Crossover: Create offspring
        offspring = self._crossover(selected)
        
        # Mutation: Introduce genetic variation
        mutated = self._mutate(offspring)
        
        # Symbiosis: Models help each other
        symbiotic = self._symbiosis(mutated)
        
        # Update population
        self.population = symbiotic[:self.population_size]
        
        logger.info(
            f"Evolution complete: {len(self.species)} species, "
            f"best fitness: {max(g.fitness for g in self.population):.4f}"
        )
        
        return self.population
    
    def _natural_selection(self) -> List[ModelGenome]:
        """Natural selection: Survival of the fittest"""
        # Sort by fitness
        sorted_pop = sorted(self.population, key=lambda g: g.fitness, reverse=True)
        
        # Elite selection (keep best)
        elite = sorted_pop[:self.elite_size]
        
        # Tournament selection for rest
        tournament_size = self.config.get('tournament_size', 3)
        selected = elite.copy()
        
        while len(selected) < self.population_size:
            tournament = random.sample(sorted_pop, min(tournament_size, len(sorted_pop)))
            winner = max(tournament, key=lambda g: g.fitness)
            selected.append(winner)
        
        return selected
    
    def _speciate(self, population: List[ModelGenome]):
        """Speciation: Group models into species based on similarity"""
        self.species = {}
        speciation_threshold = self.config.get('speciation_threshold', 0.3)
        
        for genome in population:
            # Find similar species or create new one
            assigned = False
            for species_id, species in self.species.items():
                if self._genetic_distance(genome, species.members[0]) < speciation_threshold:
                    species.members.append(genome)
                    genome.species_id = species_id
                    assigned = True
                    break
            
            if not assigned:
                # Create new species
                species_id = f"species_{len(self.species)}"
                new_species = Species(
                    species_id=species_id,
                    members=[genome],
                    average_fitness=genome.fitness,
                    niche=self._determine_niche(genome),
                    created_at=datetime.now()
                )
                self.species[species_id] = new_species
                genome.species_id = species_id
        
        # Update species average fitness
        for species in self.species.values():
            if species.members:
                species.average_fitness = np.mean([g.fitness for g in species.members])
    
    def _crossover(self, parents: List[ModelGenome]) -> List[ModelGenome]:
        """Crossover: Create offspring from parents"""
        offspring = []
        
        # Keep elite
        elite = sorted(parents, key=lambda g: g.fitness, reverse=True)[:self.elite_size]
        offspring.extend(elite)
        
        # Create offspring through crossover
        while len(offspring) < self.population_size:
            parent1, parent2 = random.sample(parents, 2)
            
            if random.random() < self.crossover_rate:
                child = self._perform_crossover(parent1, parent2)
                child.generation = self.generation
                offspring.append(child)
            else:
                # No crossover, use parent
                offspring.append(parent1)
        
        return offspring[:self.population_size]
    
    def _perform_crossover(
        self,
        parent1: ModelGenome,
        parent2: ModelGenome
    ) -> ModelGenome:
        """Perform genetic crossover between two parents"""
        # Crossover hyperparameters (uniform crossover)
        child_hyperparams = {}
        for key in set(parent1.hyperparameters.keys()) | set(parent2.hyperparameters.keys()):
            if random.random() < 0.5:
                child_hyperparams[key] = parent1.hyperparameters.get(key, 0.0)
            else:
                child_hyperparams[key] = parent2.hyperparameters.get(key, 0.0)
        
        # Crossover architecture (simplified - take from better parent)
        if parent1.fitness > parent2.fitness:
            child_architecture = parent1.architecture.copy()
        else:
            child_architecture = parent2.architecture.copy()
        
        return ModelGenome(
            architecture=child_architecture,
            hyperparameters=child_hyperparams,
            generation=self.generation
        )
    
    def _mutate(self, population: List[ModelGenome]) -> List[ModelGenome]:
        """Mutation: Introduce genetic variation"""
        mutated = []
        
        for genome in population:
            if random.random() < self.mutation_rate:
                # Mutate hyperparameters
                for key in genome.hyperparameters:
                    if random.random() < 0.3:  # 30% chance per parameter
                        mutation = np.random.normal(0, 0.1)
                        genome.hyperparameters[key] += mutation
                        genome.mutations.append(f"{key}_mutated")
                
                # Mutate architecture (simplified)
                if random.random() < 0.2:  # 20% chance
                    # Add or remove a layer (simplified)
                    if 'num_layers' in genome.architecture:
                        genome.architecture['num_layers'] += random.choice([-1, 1])
                        genome.architecture['num_layers'] = max(1, genome.architecture['num_layers'])
                        genome.mutations.append("architecture_mutated")
            
            mutated.append(genome)
        
        return mutated
    
    def _symbiosis(self, population: List[ModelGenome]) -> List[ModelGenome]:
        """Symbiosis: Models help each other improve"""
        symbiotic = []
        
        for genome in population:
            # Find symbiotic partner (different species, complementary)
            partners = [
                g for g in population
                if g.species_id != genome.species_id and g.fitness > genome.fitness
            ]
            
            if partners:
                partner = random.choice(partners)
                # Symbiotic benefit: learn from partner
                benefit = (partner.fitness - genome.fitness) * 0.1
                genome.fitness += benefit
                genome.mutations.append("symbiotic_benefit")
            
            symbiotic.append(genome)
        
        return symbiotic
    
    def _genetic_distance(
        self,
        genome1: ModelGenome,
        genome2: ModelGenome
    ) -> float:
        """Calculate genetic distance between two genomes"""
        # Distance based on hyperparameters
        common_keys = set(genome1.hyperparameters.keys()) & set(genome2.hyperparameters.keys())
        if not common_keys:
            return 1.0
        
        distances = []
        for key in common_keys:
            val1 = genome1.hyperparameters[key]
            val2 = genome2.hyperparameters[key]
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                diff = abs(val1 - val2)
                max_val = max(abs(val1), abs(val2), 1.0)
                distances.append(diff / max_val)
        
        return np.mean(distances) if distances else 1.0
    
    def _determine_niche(self, genome: ModelGenome) -> Dict[str, Any]:
        """Determine ecological niche for a genome"""
        return {
            'hyperparameter_space': list(genome.hyperparameters.keys()),
            'architecture_type': genome.architecture.get('type', 'unknown'),
            'fitness_level': 'high' if genome.fitness > 0.7 else 'medium' if genome.fitness > 0.5 else 'low'
        }
    
    def initialize_population(self, initial_genomes: List[ModelGenome]):
        """Initialize population with initial genomes"""
        self.population = initial_genomes
        self.generation = 0
        logger.info(f"Initialized population with {len(self.population)} genomes")
    
    def get_best_genome(self) -> Optional[ModelGenome]:
        """Get best genome from current population"""
        if not self.population:
            return None
        return max(self.population, key=lambda g: g.fitness)
    
    def get_species_diversity(self) -> Dict[str, Any]:
        """Get diversity metrics"""
        return {
            'num_species': len(self.species),
            'species_sizes': {sid: len(s.members) for sid, s in self.species.items()},
            'average_fitness_by_species': {
                sid: s.average_fitness for sid, s in self.species.items()
            },
            'generation': self.generation
        }

