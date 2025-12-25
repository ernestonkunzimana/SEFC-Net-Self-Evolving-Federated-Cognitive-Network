from typing import Dict, Any
from dataclasses import dataclass
import logging

@dataclass
class ValidationError:
    """Configuration validation error"""
    path: str
    message: str
    severity: str

class ConfigValidator:
    """Validates configuration settings"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def validate_config(self, config: Dict) -> List[ValidationError]:
        """Validate complete configuration"""
        errors = []
        errors.extend(self._validate_federation(config.get('federation', {})))
        errors.extend(self._validate_evolution(config.get('evolution', {})))
        errors.extend(self._validate_monitoring(config.get('monitoring', {})))
        return errors
        
    def _validate_federation(self, config: Dict) -> List[ValidationError]:
        """Validate federation settings"""
        errors = []
        if config.get('num_clients', 0) < config.get('min_fit_clients', 0):
            errors.append(ValidationError(
                path='federation.num_clients',
                message='num_clients must be >= min_fit_clients',
                severity='error'
            ))
        return errors