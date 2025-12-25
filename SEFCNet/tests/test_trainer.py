"""Unit tests for training components."""
import unittest
from SEFCNet.models.base_model import SimpleMLP


class TestTrainer(unittest.TestCase):
    
    def test_model_initialization(self):
        model = SimpleMLP()
        self.assertIsNotNone(model)
    
    def test_model_forward(self):
        model = SimpleMLP()
        import torch
        x = torch.randn(1, 4)
        out = model(x)
        self.assertEqual(out.shape, (1, 3))