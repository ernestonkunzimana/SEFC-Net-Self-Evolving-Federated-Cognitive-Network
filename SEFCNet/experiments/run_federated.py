# A slightly more advanced script using Flower's simulation API
import flwr as fl
from nodes.client_template import create_client
from central_controller.server import get_round_strategy
import logging


logger = logging.getLogger("SEFCNet.experiments")




def start_simulation(num_clients: int = 4, rounds: int = 3):
logger.info(f"Starting simulation with {num_clients} clients for {rounds} rounds")


def client_fn(cid: str):
return create_client(cid)


strategy = get_round_strategy()
fl.simulation.start_simulation(client_fn=client_fn, num_clients=num_clients, config=fl.server.ServerConfig(num_rounds=rounds), strategy=strategy)




if __name__ == "__main__":
start_simulation()


# End of multi-file template