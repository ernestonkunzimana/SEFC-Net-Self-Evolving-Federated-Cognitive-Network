from nodes.client_template import BaseClient
from rl.self_evolving_agent import SelfEvolvingAgent
import numpy as np
import flwr as fl
from typing import Dict, List, Tuple
from ..core.evolution_manager import ModelEvolutionManager, EvolutionConfig


class EvolvingClient(BaseClient, fl.client.NumPyClient):
    def __init__(self, client_id, data_path, model, x_train, y_train, x_val, y_val):
        BaseClient.__init__(self, client_id=client_id, data_path=data_path)
        fl.client.NumPyClient.__init__(self)
        self.agent = SelfEvolvingAgent()
        self.learning_rate = 0.01

        self.model = model
        self.x_train = x_train
        self.y_train = y_train
        self.x_val = x_val
        self.y_val = y_val
        self.evolution_manager = ModelEvolutionManager(EvolutionConfig())

    def fit(self, parameters, config):
        self.model.coef_, self.model.intercept_ = parameters
        acc_before = self.model.score(self.X_test, self.y_test)

        # RL agent observes system state (accuracy, latency, dataset size)
        state = np.array([acc_before, len(self.X_train) / 100.0, np.random.rand()])
        action = self.agent.select_action(state)

        # Map RL action to dynamic learning rate changes
        lr_map = {0: 0.001, 1: 0.01, 2: 0.05}
        self.learning_rate = lr_map[action]

        print(f"[{self.client_id}] Adjusted learning rate: {self.learning_rate}")

        self.model.fit(self.X_train, self.y_train)
        acc_after = self.model.score(self.X_test, self.y_test)

        # Reward = improvement in accuracy
        reward = acc_after - acc_before
        next_state = np.array([acc_after, len(self.X_train) / 100.0, np.random.rand()])

        loss = self.agent.train(state, reward, next_state)
        print(f"[{self.client_id}] RL update done, reward={reward:.4f}, loss={loss:.4f}")

        return self.model.coef_, self.model.intercept_, len(self.X_train)

    def get_parameters(self, config: Dict) -> List[np.ndarray]:
        """Get model parameters"""
        return [val.numpy() for val in self.model.get_weights()]

    def fit(self, parameters: List[np.ndarray], config: Dict) -> Tuple[List[np.ndarray], int, Dict]:
        """Train model with evolution"""
        # Set model parameters
        self.model.set_weights(parameters)

        # Train model
        history = self.model.fit(
            self.x_train, self.y_train,
            epochs=config.get('epochs', 1),
            batch_size=config.get('batch_size', 32),
            validation_data=(self.x_val, self.y_val)
        )

        # Evolve model parameters
        evolved_params = self.evolution_manager.evolve_model(
            dict(zip(self.model.weights, parameters)),
            history.history['val_accuracy'][-1]
        )

        return list(evolved_params.values()), len(self.x_train), {
            'accuracy': float(history.history['accuracy'][-1]),
            'loss': float(history.history['loss'][-1])
        }