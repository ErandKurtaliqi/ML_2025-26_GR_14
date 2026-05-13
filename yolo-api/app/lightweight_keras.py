import os
import tempfile
import zipfile

import h5py
import numpy as np


class LightweightKerasDigitModel:
    """Inference-only loader for the project's Keras digit CNN.

    It implements the small subset of Keras used by getIdStudent.py:
    `model.predict(batch, verbose=0) -> probabilities`.
    """

    def __init__(self, keras_path: str):
        self.keras_path = keras_path
        self.weights = self._load_weights(keras_path)

    @classmethod
    def can_load(cls, keras_path: str) -> bool:
        if not os.path.isfile(keras_path) or not zipfile.is_zipfile(keras_path):
            return False
        with zipfile.ZipFile(keras_path) as archive:
            return "model.weights.h5" in archive.namelist()

    def predict(self, batch, verbose=0):
        x = np.asarray(batch, dtype=np.float32)
        if x.ndim == 3:
            x = x[..., np.newaxis]

        return self._forward_batch(x)

    @staticmethod
    def _load_weights(keras_path: str):
        tmp_path = None
        try:
            with zipfile.ZipFile(keras_path) as archive:
                with tempfile.NamedTemporaryFile(suffix=".h5", delete=False) as tmp:
                    tmp.write(archive.read("model.weights.h5"))
                    tmp_path = tmp.name

            weights = {}
            with h5py.File(tmp_path, "r") as h5:
                def read_layer(name):
                    group = h5[f"layers/{name}/vars"]
                    return [np.array(group[str(i)], dtype=np.float32) for i in range(len(group))]

                for layer in [
                    "conv2d",
                    "batch_normalization",
                    "conv2d_1",
                    "batch_normalization_1",
                    "conv2d_2",
                    "batch_normalization_2",
                    "conv2d_3",
                    "batch_normalization_3",
                    "conv2d_4",
                    "batch_normalization_4",
                    "dense",
                    "batch_normalization_5",
                    "dense_1",
                    "dense_2",
                ]:
                    weights[layer] = read_layer(layer)
            return weights
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def _forward_batch(self, x):
        x = self._conv_bn_relu(x, "conv2d", "batch_normalization")
        x = self._conv_bn_relu(x, "conv2d_1", "batch_normalization_1")
        x = self._max_pool(x)

        x = self._conv_bn_relu(x, "conv2d_2", "batch_normalization_2")
        x = self._conv_bn_relu(x, "conv2d_3", "batch_normalization_3")
        x = self._max_pool(x)

        x = self._conv_bn_relu(x, "conv2d_4", "batch_normalization_4")
        x = self._max_pool(x)

        x = x.reshape(x.shape[0], -1)
        x = self._dense(x, "dense")
        x = self._relu(x)
        x = self._batch_norm(x, "batch_normalization_5")
        x = self._dense(x, "dense_1")
        x = self._relu(x)
        x = self._dense(x, "dense_2")
        return self._softmax(x)

    def _conv_bn_relu(self, x, conv_name, bn_name):
        x = self._conv2d_same(x, conv_name)
        x = self._relu(x)
        return self._batch_norm(x, bn_name)

    def _conv2d_same(self, x, layer_name):
        kernel, bias = self.weights[layer_name]
        kh, kw, _, _ = kernel.shape
        padded = np.pad(
            x,
            ((0, 0), (kh // 2, kh // 2), (kw // 2, kw // 2), (0, 0)),
            mode="constant",
            constant_values=0,
        )
        windows = np.lib.stride_tricks.sliding_window_view(padded, (kh, kw), axis=(1, 2))
        windows = windows.transpose(0, 1, 2, 4, 5, 3)
        return np.tensordot(windows, kernel, axes=([3, 4, 5], [0, 1, 2])) + bias

    @staticmethod
    def _max_pool(x):
        _, h, w, channels = x.shape
        x = x[:, : h - (h % 2), : w - (w % 2), :]
        x = x.reshape(x.shape[0], x.shape[1] // 2, 2, x.shape[2] // 2, 2, channels)
        return x.max(axis=(2, 4))

    def _batch_norm(self, x, layer_name, epsilon=0.001):
        gamma, beta, moving_mean, moving_var = self.weights[layer_name]
        return gamma * ((x - moving_mean) / np.sqrt(moving_var + epsilon)) + beta

    def _dense(self, x, layer_name):
        kernel, bias = self.weights[layer_name]
        return x @ kernel + bias

    @staticmethod
    def _relu(x):
        return np.maximum(x, 0)

    @staticmethod
    def _softmax(x):
        x = x - np.max(x, axis=-1, keepdims=True)
        exp = np.exp(x)
        return exp / np.sum(exp, axis=-1, keepdims=True)
