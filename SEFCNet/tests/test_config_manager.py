import os
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.config_manager import ConfigManager

@pytest.fixture
def valid_config():
    return {
        'federation': {
            'num_rounds': 10,
            'num_clients': 5,
            'min_fit_clients': 2
        },
        'evolution': {
            'enable': True,
            'mutation_rate': 0.1
        },
        'monitoring': {
            'metrics_interval': 5,
            'enable_dashboard': True
        }
    }

@pytest.fixture
def config_file(valid_config):
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
        yaml.dump(valid_config, f)
        return Path(f.name)

def test_load_valid_config(config_file):
    manager = ConfigManager(str(config_file))
    config = manager.load_config()
    assert 'federation' in config
    assert 'evolution' in config
    assert 'monitoring' in config

def test_invalid_federation_config(config_file):
    manager = ConfigManager(str(config_file))
    manager.config = {
        'federation': {'num_clients': 2, 'min_fit_clients': 5},
        'evolution': {},
        'monitoring': {}
    }
    with pytest.raises(ValueError):
        manager._validate_config()

def test_get_value(config_file, valid_config):
    manager = ConfigManager(str(config_file))
    manager.config = valid_config
    assert manager.get_value('federation', 'num_rounds') == 10
    assert manager.get_value('missing', 'key', 'default') == 'default'