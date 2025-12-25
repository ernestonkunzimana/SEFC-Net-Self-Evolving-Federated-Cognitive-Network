"""
Hybrid model combining RL and supervised learning.
"""
import torch
import torch.nn as nn
from models.base_model import SimpleMLP


class HybridModel(nn.Module):
    """Fuses RL policy with supervised classifier."""
    
    def __init__(self, input_dim: int = 4, hidden_dim: int = 64, output_dim: int = 3):
        super().__init__()
        self.shared_encoder = SimpleMLP(input_dim, hidden_dim, hidden_dim)
        self.classifier_head = nn.Linear(hidden_dim, output_dim)
        self.policy_head = nn.Linear(hidden_dim, output_dim)
        self.value_head = nn.Linear(hidden_dim, 1)
    
    def forward(self, x, mode="classification"):
        """Forward pass with mode selection."""
        features = self.shared_encoder(x)
        
        if mode == "classification":
            return self.classifier_head(features)
        elif mode == "policy":
            return torch.softmax(self.policy_head(features), dim=-1)
        elif mode == "value":
            return self.value_head(features)
        else:
            return features
