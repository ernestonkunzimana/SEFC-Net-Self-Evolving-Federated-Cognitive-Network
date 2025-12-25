"""
Autonomous Agent for Decentralized Federated Learning
======================================================
Fully autonomous agents that coordinate without central authority
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


@dataclass
class AgentState:
    """Represents an agent's internal state"""
    agent_id: str
    model_parameters: Dict[str, Any]
    local_data_size: int
    performance_metrics: Dict[str, float]
    neighbors: Set[str] = field(default_factory=set)
    trust_scores: Dict[str, float] = field(default_factory=dict)
    last_update: datetime = field(default_factory=datetime.now)


class AutonomousAgent:
    """
    Autonomous Agent for decentralized federated learning.
    
    MANDATORY COMPONENT - Not optional
    """
    
    def __init__(self, agent_id: str, config: Optional[Dict[str, Any]] = None):
        """Initialize autonomous agent"""
        self.agent_id = agent_id
        self.config = config or {}
        self.state = AgentState(
            agent_id=agent_id,
            model_parameters={},
            local_data_size=0,
            performance_metrics={}
        )
        self.message_queue: List[Dict[str, Any]] = []
        self.decision_history: List[Dict[str, Any]] = []
        
        logger.info(f"Autonomous Agent {agent_id} initialized (MANDATORY)")
    
    def make_autonomous_decision(
        self,
        context: Dict[str, Any],
        available_actions: List[str]
    ) -> str:
        """
        Make autonomous decision without central coordinator.
        
        This is MANDATORY - agents must be fully autonomous.
        """
        # Decision based on:
        # - Local performance
        # - Neighbor states
        # - Trust scores
        # - Resource availability
        
        decision_scores = {}
        for action in available_actions:
            score = self._evaluate_action(action, context)
            decision_scores[action] = score
        
        # Select best action
        best_action = max(decision_scores.items(), key=lambda x: x[1])[0]
        
        # Record decision
        self.decision_history.append({
            'action': best_action,
            'context': context,
            'scores': decision_scores,
            'timestamp': datetime.now()
        })
        
        logger.debug(f"Agent {self.agent_id} decided: {best_action}")
        return best_action
    
    def _evaluate_action(self, action: str, context: Dict[str, Any]) -> float:
        """Evaluate an action based on agent's knowledge"""
        score = 0.0
        
        # Performance-based scoring
        if action == 'participate':
            local_perf = self.state.performance_metrics.get('accuracy', 0.5)
            score += local_perf * 0.4
        
        # Resource-based scoring
        if action == 'train':
            resource_availability = context.get('resource_availability', 0.5)
            score += resource_availability * 0.3
        
        # Trust-based scoring
        if action == 'collaborate':
            avg_trust = np.mean(list(self.state.trust_scores.values())) if self.state.trust_scores else 0.5
            score += avg_trust * 0.3
        
        return score
    
    def negotiate_with_neighbor(
        self,
        neighbor_id: str,
        proposal: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Negotiate with a neighbor agent"""
        # Evaluate proposal
        proposal_value = self._evaluate_proposal(proposal)
        
        # Make counter-proposal if needed
        if proposal_value < 0.5:
            counter_proposal = self._create_counter_proposal(proposal)
            return {
                'status': 'counter_proposal',
                'proposal': counter_proposal,
                'value': proposal_value
            }
        else:
            return {
                'status': 'accepted',
                'proposal': proposal,
                'value': proposal_value
            }
    
    def _evaluate_proposal(self, proposal: Dict[str, Any]) -> float:
        """Evaluate a negotiation proposal"""
        # Evaluate based on:
        # - Benefit to agent
        # - Resource cost
        # - Trust in proposer
        
        benefit = proposal.get('benefit', 0.0)
        cost = proposal.get('cost', 1.0)
        proposer_trust = self.state.trust_scores.get(proposal.get('proposer_id', ''), 0.5)
        
        value = (benefit * proposer_trust) / max(cost, 0.1)
        return min(1.0, max(0.0, value))
    
    def _create_counter_proposal(self, original: Dict[str, Any]) -> Dict[str, Any]:
        """Create counter-proposal"""
        return {
            'benefit': original.get('benefit', 0.0) * 1.2,
            'cost': original.get('cost', 1.0) * 0.8,
            'proposer_id': self.agent_id
        }
    
    def update_trust(self, neighbor_id: str, interaction_result: Dict[str, Any]):
        """Update trust score for a neighbor"""
        success = interaction_result.get('success', False)
        quality = interaction_result.get('quality', 0.5)
        
        current_trust = self.state.trust_scores.get(neighbor_id, 0.5)
        
        # Update trust (exponential moving average)
        alpha = 0.2
        new_trust = alpha * (1.0 if success else 0.0) * quality + (1 - alpha) * current_trust
        
        self.state.trust_scores[neighbor_id] = new_trust
        logger.debug(f"Updated trust for {neighbor_id}: {new_trust:.3f}")
    
    def discover_neighbors(self, network_topology: Dict[str, List[str]]):
        """Discover neighbors in the network"""
        self.state.neighbors = set(network_topology.get(self.agent_id, []))
        logger.debug(f"Agent {self.agent_id} discovered {len(self.state.neighbors)} neighbors")
    
    def get_state(self) -> AgentState:
        """Get current agent state"""
        return self.state

