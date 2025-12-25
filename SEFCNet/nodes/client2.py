from nodes.client_template import BaseClient


class Client2(BaseClient):
def __init__(self, data_path):
super().__init__(client_id="Client2", data_path=data_path)


def preprocess_data(self):
print(f"[{self.client_id}] Loading local dataset...")
self.X_train, self.y_train, self.X_test, self.y_test = self.load_iris_subset(seed=2)
