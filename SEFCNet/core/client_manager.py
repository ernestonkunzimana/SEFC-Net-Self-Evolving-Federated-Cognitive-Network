from dataclasses import dataclass
from typing import Dict, List, Optional
import logging
import numpy as np

@dataclass
class ClientState:
    """Client state information"""
    client_id: str
    is_active: bool
    performance: float
    last_update: float
    resources: Dict[str, float]

class ClientManager:
    """Manages federated learning clients"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.clients: Dict[str, ClientState] = {}
        self.logger = logging.getLogger(__name__)
        
    def register_client(self, client_id: str, resources: Dict[str, float]) -> bool:
        """Register a new client"""
        if client_id in self.clients:
            self.logger.warning(f"Client {client_id} already registered")
            return False
            
        self.clients[client_id] = ClientState(
            client_id=client_id,
            is_active=True,
            performance=0.0,
            last_update=0.0,
            resources=resources
        )
        return True
        
    def update_client_performance(self, client_id: str, performance: float):
        """Update client performance metrics"""
        if client_id in self.clients:
            self.clients[client_id].performance = performance
            self.clients[client_id].last_update = time.time()