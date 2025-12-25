import pytest
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from SEFCNet.core.evolution_manager import EvolutionManager

@pytest.fixture
def evolution_manager():
    config = {
        'evolution': {
            'mutation_rate': 0.1,
            'population_size': 10,
            'generations': 50
        }
    }
    return EvolutionManager(config)

def test_evolution_step(evolution_manager):
    model_params = {
        'weights': [1.0, 2.0, 3.0],
        'biases': [0.1, 0.2, 0.3]
    }
    fitness = 0.85
    
    evolved_params = evolution_manager.evolve_model(model_params, fitness)
    assert evolved_params is not None
    assert 'weights' in evolved_params
    assert 'biases' in evolved_params