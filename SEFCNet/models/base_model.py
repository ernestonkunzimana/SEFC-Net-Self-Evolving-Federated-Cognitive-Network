import tensorflow as tf

class SimpleMLP(tf.keras.Model):
    """Simple MLP used in tests and examples."""
    def __init__(self, input_dim: int = 4, hidden_dim: int = 16, output_dim: int = 3):
        super().__init__()
        self.layer1 = tf.keras.layers.Dense(hidden_dim, activation="relu", input_shape=(input_dim,))
        self.layer2 = tf.keras.layers.Dense(hidden_dim, activation="relu")
        self.out = tf.keras.layers.Dense(output_dim, activation="softmax")

    def __call__(self, inputs, *args, **kwargs):
        processed = self._ensure_tensorflow_input(inputs)
        return super().__call__(processed, *args, **kwargs)

    def call(self, inputs, training: bool = False):
        x = self.layer1(inputs)
        x = self.layer2(x)
        return self.out(x)

    @staticmethod
    def _ensure_tensorflow_input(inputs):
        try:
            import torch

            if isinstance(inputs, torch.Tensor):
                return inputs.detach().cpu().numpy().astype("float32")
        except Exception:
            pass
        return inputs