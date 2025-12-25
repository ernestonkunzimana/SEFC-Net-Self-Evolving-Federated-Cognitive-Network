"""
Self-Organizing Topology for Autonomous Agents
==============================================
Dynamic network topology formation without central control
"""

try:
    import networkx as nx
except ImportError:
    nx = None  # Will use fallback
import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
import random

logger = logging.getLogger(__name__)


class SelfOrganizingTopology:
    """
    Self-organizing network topology for autonomous agents.
    
    MANDATORY COMPONENT - Not optional
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize self-organizing topology"""
        self.config = config or {}
        self.formation_strategy = self.config.get('formation_strategy', 'proximity')
        
        if nx is None:
            # Fallback: use simple dict-based graph
            self.graph = None
            self._nodes = {}
            self._edges = {}
        else:
            self.graph = nx.Graph()
        
        logger.info("Self-Organizing Topology initialized (MANDATORY)")
    
    def form_topology(
        self,
        agents: List[Any],
        agent_positions: Optional[Dict[str, tuple]] = None,
        trust_network: Optional[Dict[str, Dict[str, float]]] = None
    ) -> Any:
        """
        Form self-organizing topology.
        
        This is MANDATORY - network must self-organize.
        """
        if nx is not None:
            self.graph.clear()
            # Add all agents as nodes
            for agent in agents:
                self.graph.add_node(agent.agent_id, agent=agent)
        else:
            # Fallback implementation
            self._nodes = {agent.agent_id: agent for agent in agents}
            self._edges = {}
        
        # Form edges based on strategy
        if self.formation_strategy == 'proximity' and agent_positions:
            self._form_by_proximity(agent_positions)
        elif self.formation_strategy == 'trust' and trust_network:
            self._form_by_trust(trust_network)
        else:
            self._form_by_random()
        
        if nx is not None:
            logger.info(f"Topology formed: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")
            return self.graph
        else:
            num_edges = len(self._edges)
            logger.info(f"Topology formed: {len(self._nodes)} nodes, {num_edges} edges")
            return {'nodes': self._nodes, 'edges': self._edges}
    
    def _form_by_proximity(self, positions: Dict[str, tuple]):
        """Form topology based on spatial proximity"""
        agent_ids = list(positions.keys())
        
        for i, agent1 in enumerate(agent_ids):
            for agent2 in agent_ids[i+1:]:
                # Calculate distance
                pos1 = positions[agent1]
                pos2 = positions[agent2]
                distance = sum((a - b) ** 2 for a, b in zip(pos1, pos2)) ** 0.5
                
                # Connect if within threshold
                threshold = self.config.get('proximity_threshold', 10.0)
                if distance < threshold:
                    if nx is not None:
                        self.graph.add_edge(agent1, agent2, weight=1.0 / (distance + 0.1))
                    else:
                        self._edges[(agent1, agent2)] = {'weight': 1.0 / (distance + 0.1)}
    
    def _form_by_trust(self, trust_network: Dict[str, Dict[str, float]]):
        """Form topology based on trust scores"""
        for agent1, trusts in trust_network.items():
            for agent2, trust_score in trusts.items():
                if trust_score > self.config.get('trust_threshold', 0.6):
                    if nx is not None:
                        self.graph.add_edge(agent1, agent2, weight=trust_score)
                    else:
                        self._edges[(agent1, agent2)] = {'weight': trust_score}
    
    def _form_by_random(self):
        """Form random topology"""
        if nx is not None:
            nodes = list(self.graph.nodes())
        else:
            nodes = list(self._nodes.keys())
        
        num_edges = int(len(nodes) * self.config.get('edge_probability', 0.3))
        
        for _ in range(num_edges):
            if len(nodes) >= 2:
                agent1, agent2 = random.sample(nodes, 2)
                if nx is not None:
                    self.graph.add_edge(agent1, agent2)
                else:
                    self._edges[(agent1, agent2)] = {}
    
    def adapt_topology(
        self,
        performance_metrics: Dict[str, float],
        trust_updates: Dict[str, Dict[str, float]]
    ):
        """Adapt topology based on performance and trust"""
        if nx is not None:
            # Remove low-performing edges
            edges_to_remove = []
            for u, v in self.graph.edges():
                perf_u = performance_metrics.get(u, 0.0)
                perf_v = performance_metrics.get(v, 0.0)
                if perf_u < 0.3 or perf_v < 0.3:
                    edges_to_remove.append((u, v))
            
            self.graph.remove_edges_from(edges_to_remove)
            
            # Add high-trust edges
            for agent1, trusts in trust_updates.items():
                for agent2, trust in trusts.items():
                    if trust > 0.7 and not self.graph.has_edge(agent1, agent2):
                        self.graph.add_edge(agent1, agent2, weight=trust)
            
            logger.info(f"Topology adapted: {self.graph.number_of_edges()} edges")
        else:
            # Fallback implementation
            edges_to_remove = []
            for (u, v) in list(self._edges.keys()):
                perf_u = performance_metrics.get(u, 0.0)
                perf_v = performance_metrics.get(v, 0.0)
                if perf_u < 0.3 or perf_v < 0.3:
                    edges_to_remove.append((u, v))
            
            for edge in edges_to_remove:
                self._edges.pop(edge, None)
            
            # Add high-trust edges
            for agent1, trusts in trust_updates.items():
                for agent2, trust in trusts.items():
                    if trust > 0.7 and (agent1, agent2) not in self._edges:
                        self._edges[(agent1, agent2)] = {'weight': trust}
            
            logger.info(f"Topology adapted: {len(self._edges)} edges")
    
    def get_neighbors(self, agent_id: str) -> List[str]:
        """Get neighbors of an agent"""
        if nx is not None:
            return list(self.graph.neighbors(agent_id))
        else:
            neighbors = []
            for (u, v) in self._edges.keys():
                if u == agent_id:
                    neighbors.append(v)
                elif v == agent_id:
                    neighbors.append(u)
            return neighbors
    
    def get_shortest_path(self, agent1: str, agent2: str) -> Optional[List[str]]:
        """Get shortest path between two agents"""
        if nx is not None:
            try:
                return nx.shortest_path(self.graph, agent1, agent2)
            except nx.NetworkXNoPath:
                return None
        else:
            # Simple BFS fallback
            from collections import deque
            queue = deque([(agent1, [agent1])])
            visited = {agent1}
            
            while queue:
                current, path = queue.popleft()
                if current == agent2:
                    return path
                
                for neighbor in self.get_neighbors(current):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, path + [neighbor]))
            
            return None

