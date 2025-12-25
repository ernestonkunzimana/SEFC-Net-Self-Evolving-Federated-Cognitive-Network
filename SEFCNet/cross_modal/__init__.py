"""
Cross-Modal Learning for SEFCNet
=================================
Mandatory component for multi-modal federated learning
"""

from .multi_modal_fl import MultiModalFederatedLearning
from .transfer_learning import CrossTaskTransfer
from .few_shot import FewShotLearning

__all__ = [
    'MultiModalFederatedLearning',
    'CrossTaskTransfer',
    'FewShotLearning'
]

