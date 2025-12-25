"""Unit tests for server components."""
import unittest
from SEFCNet.central_controller.aggregator import FedAvgAggregator
import numpy as np


class TestServer(unittest.TestCase):
    
    def test_fedavg_aggregation(self):
        aggregator = FedAvgAggregator()
        params = [[np.array([1.0]), np.array([2.0])], [np.array([3.0]), np.array([4.0])]]
        weights = [1, 1]
        result = aggregator.aggregate(params, weights)
        self.assertEqual(len(result), 2)