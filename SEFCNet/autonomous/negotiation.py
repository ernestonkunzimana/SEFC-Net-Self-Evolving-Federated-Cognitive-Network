"""
Negotiation Protocol for Autonomous Agents
==========================================
Agent-to-agent negotiation without central coordinator
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import random

logger = logging.getLogger(__name__)


class NegotiationProtocol:
    """
    Negotiation protocol for autonomous agents.
    
    MANDATORY COMPONENT - Not optional
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize negotiation protocol"""
        self.config = config or {}
        self.max_rounds = self.config.get('max_negotiation_rounds', 5)
        self.negotiation_history: List[Dict[str, Any]] = []
        
        logger.info("Negotiation Protocol initialized (MANDATORY)")
    
    def negotiate(
        self,
        agent1: Any,
        agent2: Any,
        initial_proposal: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Conduct negotiation between two agents.
        
        This is MANDATORY - all agent interactions must use negotiation.
        """
        logger.info(f"Starting negotiation between {agent1.agent_id} and {agent2.agent_id}")
        
        current_proposal = initial_proposal.copy()
        current_proposal['proposer_id'] = agent1.agent_id
        
        for round_num in range(self.max_rounds):
            # Agent 2 evaluates proposal
            response = agent2.negotiate_with_neighbor(agent1.agent_id, current_proposal)
            
            if response['status'] == 'accepted':
                # Negotiation successful
                result = {
                    'status': 'success',
                    'agreement': current_proposal,
                    'rounds': round_num + 1,
                    'timestamp': datetime.now().isoformat()
                }
                self.negotiation_history.append(result)
                return result
            
            elif response['status'] == 'counter_proposal':
                # Continue negotiation with counter-proposal
                current_proposal = response['proposal']
                current_proposal['proposer_id'] = agent2.agent_id
                
                # Agent 1 evaluates counter-proposal
                response2 = agent1.negotiate_with_neighbor(agent2.agent_id, current_proposal)
                
                if response2['status'] == 'accepted':
                    result = {
                        'status': 'success',
                        'agreement': current_proposal,
                        'rounds': round_num + 1,
                        'timestamp': datetime.now().isoformat()
                    }
                    self.negotiation_history.append(result)
                    return result
                elif response2['status'] == 'counter_proposal':
                    current_proposal = response2['proposal']
        
        # Negotiation failed
        result = {
            'status': 'failed',
            'last_proposal': current_proposal,
            'rounds': self.max_rounds,
            'timestamp': datetime.now().isoformat()
        }
        self.negotiation_history.append(result)
        return result
    
    def multi_agent_negotiation(
        self,
        agents: List[Any],
        proposal: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Conduct multi-agent negotiation"""
        agreements = []
        rejections = []
        
        for agent in agents[1:]:  # Skip proposer
            result = self.negotiate(agents[0], agent, proposal)
            if result['status'] == 'success':
                agreements.append(agent.agent_id)
            else:
                rejections.append(agent.agent_id)
        
        return {
            'status': 'partial' if agreements else 'failed',
            'agreements': agreements,
            'rejections': rejections,
            'consensus_rate': len(agreements) / len(agents[1:]) if agents[1:] else 0.0
        }

