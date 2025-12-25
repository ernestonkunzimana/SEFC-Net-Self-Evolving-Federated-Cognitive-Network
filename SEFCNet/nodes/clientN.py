from nodes.client_template import BaseClient
import random


class ClientN(BaseClient):
def __init__(self, client_id, data_path):
super().__init__(client_id=client_id, data_path=data_path)


def preprocess_data(self):
seed = random.randint(4, 100)
print(f"[{self.client_id}] Loading dataset with seed {seed}...")
self.X_train, self.y_train, self.X_test, self.y_test = self.load_iris_subset(seed=seed)