from __future__ import annotations


def load_tensorflow():
    try:
        import tensorflow.compat.v1 as tf
    except ImportError as exc:
        raise ImportError(
            "TensorFlow is required for the legacy DNC modules under deep-learning/. "
            "As of March 10, 2026, TensorFlow's official pip install guide targets "
            "Python 3.9-3.12, so use a separate Python 3.12 environment for these modules."
        ) from exc

    tf.disable_v2_behavior()
    return tf


def load_tensorflow_and_sonnet():
    tf = load_tensorflow()
    try:
        import sonnet as snt
    except ImportError as exc:
        raise ImportError(
            "DeepMind Sonnet is required for the legacy DNC modules under deep-learning/. "
            "These files are preserved as legacy examples and should be run in a dedicated "
            "TensorFlow-compatible environment."
        ) from exc

    return snt, tf
