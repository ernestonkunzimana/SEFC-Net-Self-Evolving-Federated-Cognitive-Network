"""
Autonomous Multi-Agent Federation for SEFCNet
==============================================
Mandatory component for fully decentralized federated learning
"""

from .agent import AutonomousAgent
from .negotiation import NegotiationProtocol
from .topology import SelfOrganizingTopology
from .decentralized_fl import DecentralizedFederatedLearning

__all__ = [
    'AutonomousAgent',
    'NegotiationProtocol',
    'SelfOrganizingTopology',
    'DecentralizedFederatedLearning'
]

