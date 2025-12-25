import flwr as fl
import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression


class BaseClient(fl.client.NumPyClient):
def __init__(self, client_id, data_path):
self.client_id = client_id
self.data_path = data_path
self.model = LogisticRegression(max_iter=200)
self.preprocess_data()


def load_iris_subset(self, seed):
X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=seed)
return X_train, y_train, X_test, y_test


def get_parameters(self, config):
return self.model.coef_, self.model.intercept_


def fit(self, parameters, config):
self.model.coef_, self.model.intercept_ = parameters
self.model.fit(self.X_train, self.y_train)
print(f"[{self.client_id}] Local training complete.")
return self.model.coef_, self.model.intercept_, len(self.X_train)


def evaluate(self, parameters, config):
acc = self.model.score(self.X_test, self.y_test)
print(f"[{self.client_id}] Evaluation accuracy: {acc}")
return float(0), len(self.X_test), {"accuracy": acc}
