"""
Client registry and artifact tracking for federated learning.
"""
from typing import Dict, List, Optional
from pathlib import Path
import json
import pickle
from datetime import datetime


class ClientRegistry:
    """Track connected clients and their metadata."""
    
    def __init__(self):
        self.clients: Dict[str, Dict] = {}
        self.artifacts: Dict[str, List] = {}
    
    def register(self, client_id: str, metadata: Dict):
        """Register a new client."""
        self.clients[client_id] = {
            **metadata,
            "registered_at": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat()
        }
    
    def update(self, client_id: str, updates: Dict):
        """Update client information."""
        if client_id in self.clients:
            self.clients[client_id].update(updates)
            self.clients[client_id]["last_seen"] = datetime.now().isoformat()
    
    def get_active_clients(self) -> List[str]:
        """Get list of active client IDs."""
        return list(self.clients.keys())
    
    def save_artifact(self, client_id: str, artifact_type: str, data: any):
        """Save client artifact."""
        key = f"{client_id}_{artifact_type}"
        if key not in self.artifacts:
            self.artifacts[key] = []
        self.artifacts[key].append({
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
    
    def save_state(self, path: Path):
        """Save registry state to disk."""
        state = {
            "clients": self.clients,
            "artifacts": self.artifacts
        }
        with path.open("wb") as f:
            pickle.dump(state, f)
    
    def load_state(self, path: Path):
        """Load registry state from disk."""
        if path.exists():
            with path.open("rb") as f:
                state = pickle.load(f)
                self.clients = state.get("clients", {})
                self.artifacts = state.get("artifacts", {})