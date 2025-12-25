"""
Decision Interpreter for Federated Learning
===========================================
Interpret federated learning decisions
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class DecisionInterpreter:
    """
    Decision Interpreter for federated learning.
    
    MANDATORY COMPONENT - Not optional
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize decision interpreter"""
        self.config = config or {}
        logger.info("Decision Interpreter initialized (MANDATORY)")
    
    def interpret_federated_decision(
        self,
        decision: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Interpret a federated learning decision"""
        return {
            'decision': decision,
            'interpretation': self._generate_interpretation(decision, context),
            'factors': self._identify_factors(decision, context),
            'confidence': self._assess_confidence(decision)
        }
    
    def _generate_interpretation(self, decision: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate interpretation"""
        return f"Decision made based on {context.get('reason', 'optimization criteria')}"
    
    def _identify_factors(self, decision: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Identify factors influencing decision"""
        return ['performance', 'resource_constraints', 'privacy_requirements']
    
    def _assess_confidence(self, decision: Dict[str, Any]) -> float:
        """Assess confidence in decision"""
        return 0.8

