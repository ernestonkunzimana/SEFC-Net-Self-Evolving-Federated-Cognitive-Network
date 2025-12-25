from typing import Dict, List, Optional
import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ClientStatus:
    client_id: str
    is_active: bool
    last_heartbeat: datetime
    performance_metrics: Dict
    resource_usage: Dict

class ClientManager:
    """Manages federated learning clients with advanced monitoring"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.clients: Dict[str, ClientStatus] = {}
        self.logger = logging.getLogger(__name__)
        self._monitoring_task = None

    async def start_monitoring(self):
        """Start client monitoring"""
        self._monitoring_task = asyncio.create_task(self._monitor_clients())
        self.logger.info("Client monitoring started")

    async def _monitor_clients(self):
        while True:
            try:
                await self._check_client_health()
                await asyncio.sleep(self.config['monitoring']['client_check_interval'])
            except Exception as e:
                self.logger.error(f"Client monitoring error: {e}")