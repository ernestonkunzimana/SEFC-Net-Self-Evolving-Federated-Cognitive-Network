from typing import Dict, Optional, Type
import tensorflow as tf
import logging
from pathlib import Path

class ModelRegistry:
    """Manages model versioning and storage"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.models: Dict[str, Type[tf.keras.Model]] = {}
        self.logger = logging.getLogger(__name__)
        self.storage_path = Path(config.get('model_storage', 'models'))
        
    def register_model(self, name: str, model_class: Type[tf.keras.Model]):
        """Register a new model type"""
        if name in self.models:
            self.logger.warning(f"Model {name} already registered")
            return
            
        self.models[name] = model_class
        self.logger.info(f"Registered model: {name}")
        
    def save_model_version(self, name: str, model: tf.keras.Model, version: str):
        """Save a model version"""
        if name not in self.models:
            raise ValueError(f"Unknown model type: {name}")
            
        save_path = self.storage_path / name / version
        save_path.mkdir(parents=True, exist_ok=True)
        model.save(save_path)
        self.logger.info(f"Saved {name} version {version}")