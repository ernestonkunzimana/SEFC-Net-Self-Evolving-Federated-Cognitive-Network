"""
Biological Evolution Engine for SEFCNet
========================================
Mandatory component for biological evolution mechanisms in federated learning
"""

from .evolution_engine import BiologicalEvolutionEngine
from .speciation import Speciation
from .symbiosis import Symbiosis
from .natural_selection import NaturalSelection

__all__ = [
    'BiologicalEvolutionEngine',
    'Speciation',
    'Symbiosis',
    'NaturalSelection'
]

