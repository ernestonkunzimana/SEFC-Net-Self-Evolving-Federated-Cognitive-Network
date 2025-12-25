import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock

# ensure project root on sys.path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Mock optional heavy packages only if real package not importable
_optional = ["etcd3", "consul", "passlib", "prometheus_client", "jwt"]
for name in _optional:
    try:
        __import__(name)
    except Exception:
        sys.modules[name] = MagicMock()

@pytest.fixture
def test_config():
    return {
        'federation': {
            'num_rounds': 5,
            'num_clients': 3,
            'min_fit_clients': 2
        },
        'evolution': {
            'enable': True,
            'mutation_rate': 0.1
        },
        'monitoring': {
            'metrics_interval': 5
        }
    }