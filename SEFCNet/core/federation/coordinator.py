from typing import Dict, List, Optional
import flwr as fl
import tensorflow as tf
import logging
from dataclasses import dataclass

@dataclass
class RoundMetrics:
    round_number: int
    num_clients: int
    global_accuracy: float
    training_time: float
    communication_cost: float

class FederatedCoordinator:
    """Coordinates federated learning process with advanced features"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.current_round = 0
        self.metrics: List[RoundMetrics] = []
        self.logger = logging.getLogger(__name__)
        
    def initialize_server(self) -> fl.server.Server:
        """Initialize federated server with custom strategy"""
        strategy = self._create_advanced_strategy()
        
        server = fl.server.Server(
            strategy=strategy,
            client_manager=self._create_client_manager()
        )
        
        return server
        
    def _create_advanced_strategy(self) -> fl.server.strategy.Strategy:
        """Create advanced federated strategy with custom aggregation"""
        return fl.server.strategy.FedAvg(
            fraction_fit=self.config['federation']['fit_fraction'],
            fraction_evaluate=self.config['federation']['eval_fraction'],
            min_fit_clients=self.config['federation']['min_fit_clients'],
            min_evaluate_clients=self.config['federation']['min_evaluate_clients'],
            min_available_clients=self.config['federation']['min_available_clients'],
            on_fit_config_fn=self._fit_config,
            on_evaluate_config_fn=self._evaluate_config,
            evaluate_metrics_aggregation_fn=self._aggregate_metrics
        )