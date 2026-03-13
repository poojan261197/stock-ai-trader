import time

import numpy as np


def _sigmoid(values: np.ndarray) -> np.ndarray:
    clipped = np.clip(values, -50, 50)
    return 1.0 / (1.0 + np.exp(-clipped))


def reducedimension(input_, dimension=2, learning_rate=0.01, hidden_layer=256, epoch=20):
    data = np.asarray(input_, dtype=np.float64)
    if data.ndim != 2:
        raise ValueError("input_ must be a 2D array")
    if dimension <= 0 or hidden_layer <= 0 or epoch <= 0:
        raise ValueError("dimension, hidden_layer, and epoch must be positive")

    rng = np.random.default_rng(42)
    input_size = data.shape[1]

    weights = {
        "encoder_h1": rng.normal(0.0, np.sqrt(2.0 / (input_size + hidden_layer)), size=(input_size, hidden_layer)),
        "encoder_h2": rng.normal(0.0, np.sqrt(2.0 / (hidden_layer + dimension)), size=(hidden_layer, dimension)),
        "decoder_h1": rng.normal(0.0, np.sqrt(2.0 / (dimension + hidden_layer)), size=(dimension, hidden_layer)),
        "decoder_h2": rng.normal(0.0, np.sqrt(2.0 / (hidden_layer + input_size)), size=(hidden_layer, input_size)),
    }
    biases = {
        "encoder_b1": np.zeros((1, hidden_layer)),
        "encoder_b2": np.zeros((1, dimension)),
        "decoder_b1": np.zeros((1, hidden_layer)),
        "decoder_b2": np.zeros((1, input_size)),
    }

    sample_count = max(1, data.shape[0])

    for i in range(epoch):
        last_time = time.time()

        first_layer_encoder = _sigmoid(data @ weights["encoder_h1"] + biases["encoder_b1"])
        second_layer_encoder = _sigmoid(first_layer_encoder @ weights["encoder_h2"] + biases["encoder_b2"])
        first_layer_decoder = _sigmoid(second_layer_encoder @ weights["decoder_h1"] + biases["decoder_b1"])
        reconstruction = _sigmoid(first_layer_decoder @ weights["decoder_h2"] + biases["decoder_b2"])

        error = reconstruction - data
        loss = float(np.mean(np.square(error)))

        delta_reconstruction = (2.0 / sample_count) * error * reconstruction * (1.0 - reconstruction)
        delta_decoder_hidden = (delta_reconstruction @ weights["decoder_h2"].T) * first_layer_decoder * (1.0 - first_layer_decoder)
        delta_bottleneck = (delta_decoder_hidden @ weights["decoder_h1"].T) * second_layer_encoder * (1.0 - second_layer_encoder)
        delta_encoder_hidden = (delta_bottleneck @ weights["encoder_h2"].T) * first_layer_encoder * (1.0 - first_layer_encoder)

        weights["decoder_h2"] -= learning_rate * first_layer_decoder.T @ delta_reconstruction
        biases["decoder_b2"] -= learning_rate * np.sum(delta_reconstruction, axis=0, keepdims=True)
        weights["decoder_h1"] -= learning_rate * second_layer_encoder.T @ delta_decoder_hidden
        biases["decoder_b1"] -= learning_rate * np.sum(delta_decoder_hidden, axis=0, keepdims=True)
        weights["encoder_h2"] -= learning_rate * first_layer_encoder.T @ delta_bottleneck
        biases["encoder_b2"] -= learning_rate * np.sum(delta_bottleneck, axis=0, keepdims=True)
        weights["encoder_h1"] -= learning_rate * data.T @ delta_encoder_hidden
        biases["encoder_b1"] -= learning_rate * np.sum(delta_encoder_hidden, axis=0, keepdims=True)

        if (i + 1) % 10 == 0 or i == 0 or i == epoch - 1:
            print("epoch:", i + 1, "loss:", loss, "time:", time.time() - last_time)

    return second_layer_encoder
