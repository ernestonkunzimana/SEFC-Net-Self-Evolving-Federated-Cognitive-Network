"""
Configuration loader for YAML configs.
"""
from pathlib import Path
from typing import Dict, Any
import yaml


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load YAML configuration file."""
    with config_path.open("r") as f:
        return yaml.safe_load(f)


def merge_configs(base: Dict, override: Dict) -> Dict:
    """Merge two config dictionaries."""
    result = base.copy()
    for key, value in override.items():
        if isinstance(value, dict) and key in result and isinstance(result[key], dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    return result