import yaml
from pathlib import Path
from typing import Dict, Optional, Any
import logging
from dataclasses import dataclass

@dataclass
class ConfigDefaults:
    """Default configuration values"""
    FEDERATION = {
        'num_rounds': 10,
        'num_clients': 5,
        'min_fit_clients': 2,
        'min_evaluate_clients': 2
    }
    EVOLUTION = {
        'enable': True,
        'mutation_rate': 0.1,
        'population_size': 10
    }
    MONITORING = {
        'metrics_interval': 5,
        'enable_dashboard': True,
        'port': 8501
    }

class ValidationError:
    def __init__(self, path: str, message: str, severity: str = "error"):
        self.path = path
        self.message = message
        self.severity = severity

class ConfigManager:
    """Manages system configuration"""
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.config: Dict = {}
        self.logger = logging.getLogger(__name__)
        self.defaults = ConfigDefaults()

    def load_config(self) -> Dict:
        """Load and validate configuration"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            
            validation_errors = self._validate_config(raise_on_error=False)
            if validation_errors:
                for error in validation_errors:
                    self.logger.error(f"{error.path}: {error.message}")
                raise ValueError("Configuration validation failed")
                
            return self.config
            
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            raise

    def _validate_config(self, raise_on_error: bool = True):
        """Validate configuration values"""
        required_sections = ['federation', 'evolution', 'monitoring']
        errors = []
        for section in required_sections:
            if section not in self.config:
                errors.append(ValidationError(section, f"Missing required config section: {section}"))
        
        if errors:
            return errors
        
        errors.extend(self._validate_federation_config())
        errors.extend(self._validate_evolution_config())
        errors.extend(self._validate_monitoring_config())
        
        if errors and raise_on_error:
            raise ValueError("Configuration validation failed")
        return errors

    def _validate_federation_config(self):
        """Validate federation configuration"""
        errors = []
        fed_config = self.config.get('federation', {})
        if fed_config.get('num_clients', 0) < fed_config.get('min_fit_clients', 0):
            errors.append(ValidationError('federation.num_clients', "num_clients must be >= min_fit_clients"))
        return errors

    def _validate_evolution_config(self):
        """Validate evolution configuration"""
        errors = []
        evo_config = self.config.get('evolution', {})
        if not 0 <= evo_config.get('mutation_rate', 0) <= 1:
            errors.append(ValidationError('evolution.mutation_rate', "mutation_rate must be between 0 and 1"))
        return errors

    def _validate_monitoring_config(self):
        """Validate monitoring configuration"""
        errors = []
        mon_config = self.config.get('monitoring', {})
        if mon_config.get('metrics_interval', 0) < 1:
            errors.append(ValidationError('monitoring.metrics_interval', "metrics_interval must be >= 1"))
        return errors

    def _apply_defaults(self):
        """Apply default values for missing configuration"""
        for section, defaults in vars(self.defaults).items():
            if not section.startswith('_'):
                self.config.setdefault(section.lower(), {})
                for key, value in defaults.items():
                    self.config[section.lower()].setdefault(key, value)

    def get_value(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value with fallback to default"""
        return self.config.get(section, {}).get(key, default)

    def update_value(self, section: str, key: str, value: Any):
        """Update configuration value"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self._validate_config()

    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
            raise