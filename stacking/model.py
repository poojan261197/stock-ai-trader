import numpy as np
from sklearn.neural_network import MLPRegressor


class Model:
    """Modern replacement for the old TensorFlow 1.x graph-based stacking model."""

    def __init__(self, learning_rate, num_layers, size, size_layer, output_size, forget_bias=0.1):
        hidden_layers = tuple(int(size_layer) for _ in range(max(1, int(num_layers))))
        self.sequence_width = int(size)
        self.output_size = int(output_size)
        self.forget_bias = float(forget_bias)
        self.regressor = MLPRegressor(
            hidden_layer_sizes=hidden_layers,
            activation="relu",
            solver="adam",
            learning_rate_init=float(learning_rate),
            max_iter=500,
            random_state=42,
        )

    def _reshape_sequences(self, inputs):
        array = np.asarray(inputs, dtype=np.float64)
        if array.ndim == 2:
            return array
        if array.ndim != 3:
            raise ValueError("inputs must be a 2D or 3D array")
        batch, steps, width = array.shape
        if width != self.sequence_width:
            raise ValueError(f"expected feature width {self.sequence_width}, got {width}")
        return array.reshape(batch, steps * width)

    def fit(self, inputs, targets):
        features = self._reshape_sequences(inputs)
        labels = np.asarray(targets, dtype=np.float64)
        self.regressor.fit(features, labels)
        return self

    def predict(self, inputs):
        features = self._reshape_sequences(inputs)
        prediction = self.regressor.predict(features)
        if prediction.ndim == 1:
            return prediction.reshape(-1, 1)
        return prediction

    def score(self, inputs, targets):
        features = self._reshape_sequences(inputs)
        labels = np.asarray(targets, dtype=np.float64)
        return self.regressor.score(features, labels)
