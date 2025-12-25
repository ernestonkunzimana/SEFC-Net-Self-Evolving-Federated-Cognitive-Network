from typing import List, Dict, Optional
from dataclasses import dataclass
import logging
import yaml

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]

class ConfigValidator:
    """Advanced configuration validation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate(self, config: Dict) -> ValidationResult:
        """Validate complete configuration"""
        errors = []
        warnings = []
        
        # Check required sections
        required_sections = ['federation', 'evolution', 'monitoring']
        for section in required_sections:
            if section not in config:
                errors.append(f"Missing required section: {section}")
        
        # Validate federation settings
        if 'federation' in config:
            self._validate_federation(config['federation'], errors, warnings)
        
        # Validate evolution settings
        if 'evolution' in config:
            self._validate_evolution(config['evolution'], errors, warnings)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )