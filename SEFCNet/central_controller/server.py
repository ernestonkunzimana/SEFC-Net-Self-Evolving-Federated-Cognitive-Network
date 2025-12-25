import flwr as fl


def start_server():
strategy = fl.server.strategy.FedAvg(
min_fit_clients=3,
min_eval_clients=3,
min_available_clients=3,
evaluate_metrics_aggregation_fn=lambda metrics: {"accuracy": sum(m["accuracy"] for m in metrics) / len(metrics)}
)


print("[SERVER] Starting Federated Server...")
fl.server.start_server(
server_address="0.0.0.0:8080",
config=fl.server.ServerConfig(num_rounds=5),
strategy=strategy,
)


if __name__ == "__main__":
start_server()