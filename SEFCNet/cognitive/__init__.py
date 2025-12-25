"""
Cognitive Network Architecture for SEFCNet
==========================================
Mandatory component for self-aware, cognitive federated learning
"""

from .cognitive_network import CognitiveNetwork
from .memory_systems import EpisodicMemory, SemanticMemory, ProceduralMemory
from .meta_cognition import MetaCognition
from .cognitive_fl import CognitiveFederatedLearning

__all__ = [
    'CognitiveNetwork',
    'EpisodicMemory',
    'SemanticMemory',
    'ProceduralMemory',
    'MetaCognition',
    'CognitiveFederatedLearning'
]

