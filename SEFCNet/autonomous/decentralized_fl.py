"""
Decentralized Federated Learning
=================================
Fully decentralized FL without central coordinator
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .agent import AutonomousAgent
from .negotiation import NegotiationProtocol
from .topology import SelfOrganizingTopology

logger = logging.getLogger(__name__)


class DecentralizedFederatedLearning:
    """
    Decentralized Federated Learning System.
    
    MANDATORY COMPONENT - Not optional
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize decentralized FL"""
        self.config = config or {}
        self.agents: Dict[str, AutonomousAgent] = {}
        self.negotiation = NegotiationProtocol(self.config.get('negotiation', {}))
        self.topology = SelfOrganizingTopology(self.config.get('topology', {}))
        
        logger.info("Decentralized Federated Learning initialized (MANDATORY)")
    
    def register_agent(self, agent: AutonomousAgent):
        """Register an autonomous agent"""
        self.agents[agent.agent_id] = agent
        logger.debug(f"Registered agent: {agent.agent_id}")
    
    def conduct_federated_round(
        self,
        round_id: int,
        agent_positions: Optional[Dict[str, tuple]] = None
    ) -> Dict[str, Any]:
        """
        Conduct federated learning round in decentralized manner.
        
        This is MANDATORY - all FL must support decentralization.
        """
        logger.info(f"Starting decentralized FL round {round_id}")
        
        # Form self-organizing topology
        agents_list = list(self.agents.values())
        topology = self.topology.form_topology(agents_list, agent_positions)
        
        # Agents make autonomous decisions
        decisions = {}
        for agent in agents_list:
            decision = agent.make_autonomous_decision(
                context={'round_id': round_id, 'topology': topology},
                available_actions=['participate', 'train', 'collaborate']
            )
            decisions[agent.agent_id] = decision
        
        # Agents negotiate collaborations
        collaborations = []
        for agent in agents_list:
            neighbors = self.topology.get_neighbors(agent.agent_id)
            for neighbor_id in neighbors:
                if neighbor_id in self.agents:
                    neighbor = self.agents[neighbor_id]
                    proposal = {
                        'type': 'collaboration',
                        'benefit': 0.5,
                        'cost': 0.3,
                        'proposer_id': agent.agent_id
                    }
                    result = self.negotiation.negotiate(agent, neighbor, proposal)
                    if result['status'] == 'success':
                        collaborations.append((agent.agent_id, neighbor_id))
        
        # Get topology stats
        if hasattr(topology, 'number_of_nodes'):
            topology_stats = {
                'nodes': topology.number_of_nodes(),
                'edges': topology.number_of_edges()
            }
        else:
            topology_stats = {
                'nodes': len(topology.get('nodes', {})),
                'edges': len(topology.get('edges', {}))
            }
        
        return {
            'round_id': round_id,
            'topology': topology_stats,
            'decisions': decisions,
            'collaborations': collaborations,
            'timestamp': datetime.now().isoformat()
        }

