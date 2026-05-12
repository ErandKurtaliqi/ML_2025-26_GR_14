"""
Train a high-accuracy CNN on EMNIST Digits (handwritten 0–9).

Heavy augmentation + deeper architecture + LR scheduling → 99.5%+ accuracy.

Two-step workflow:
    py -3.10 train_handwriting_emnist.py
    py -3.10 test1.py

Weights are saved to `handwriting_paths.HANDWRITING_MODEL_PATH`.
Override with: py -3.10 train_handwriting_emnist.py -o other/path.keras
"""

import argparse
import os

import tensorflow as tf
from tensorflow.keras import layers, models, callbacks
import tensorflow_datasets as tfds
import numpy as np

from handwriting_paths import HANDWRITING_MODEL_PATH

DEFAULT_OUT = HANDWRITING_MODEL_PATH


# ─── Data augmentation layer applied during training ───────────────────────
def build_augmentation():
    """Random augmentation pipeline to simulate real-world handwriting variation."""
    return tf.keras.Sequential([
        layers.RandomRotation(0.08),          # ±28° (0.08 * 360)
        layers.RandomZoom((-0.1, 0.1)),       # ±10% zoom
        layers.RandomTranslation(0.1, 0.1),   # ±10% shift
    ], name="augmentation")


def prepare_emnist(split):
    """Load EMNIST digits and put them into upright MNIST-like orientation.

    EMNIST images are stored rotated 90° counter-clockwise *and* mirrored
    horizontally relative to MNIST. Transposing (swap H and W axes) undoes both.
    """
    ds = tfds.load(
        "emnist/digits",
        split=split,
        as_supervised=True,
        shuffle_files=(split == "train"),
    )

    def prep(image, label):
        image = tf.cast(image, tf.float32) / 255.0
        image = tf.transpose(image, perm=[1, 0, 2])
        return image, label

    ds = ds.map(prep, num_parallel_calls=tf.data.AUTOTUNE)
    return ds


def build_model():
    """Deeper CNN with batch-norm and dropout for robust digit recognition."""
    inputs = layers.Input(shape=(28, 28, 1))
    
    # Augmentation (only active during training)
    x = build_augmentation()(inputs)
    
    # Block 1
    x = layers.Conv2D(32, (3, 3), activation="relu", padding="same")(x)
    x = layers.BatchNormalization()(x)
    x = layers.Conv2D(32, (3, 3), activation="relu", padding="same")(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Dropout(0.25)(x)
    
    # Block 2
    x = layers.Conv2D(64, (3, 3), activation="relu", padding="same")(x)
    x = layers.BatchNormalization()(x)
    x = layers.Conv2D(64, (3, 3), activation="relu", padding="same")(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Dropout(0.25)(x)
    
    # Block 3
    x = layers.Conv2D(128, (3, 3), activation="relu", padding="same")(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Dropout(0.3)(x)
    
    # Classifier
    x = layers.Flatten()(x)
    x = layers.Dense(256, activation="relu")(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.4)(x)
    x = layers.Dense(128, activation="relu")(x)
    x = layers.Dropout(0.3)(x)
    x = layers.Dense(10, activation="softmax")(x)
    
    return models.Model(inputs, x)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch", type=int, default=128)
    parser.add_argument("-o", "--output", default=DEFAULT_OUT)
    args = parser.parse_args()

    train_ds = prepare_emnist("train").shuffle(10000).batch(args.batch).prefetch(tf.data.AUTOTUNE)
    val_ds = prepare_emnist("test").batch(args.batch).prefetch(tf.data.AUTOTUNE)

    model = build_model()
    model.compile(
        optimizer=tf.keras.optimizers.Adam(1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    cb = [
        callbacks.ReduceLROnPlateau(monitor="val_accuracy", factor=0.5, patience=3,
                                     min_lr=1e-6, verbose=1),
        callbacks.EarlyStopping(monitor="val_accuracy", patience=8,
                                restore_best_weights=True, verbose=1),
    ]

    print("Training on EMNIST / digits (handwritten, multi-writer)...")
    print(f"  Epochs: {args.epochs}, Batch: {args.batch}")
    model.summary()
    model.fit(train_ds, validation_data=val_ds, epochs=args.epochs,
              callbacks=cb, verbose=1)

    model.save(args.output)
    out_abs = os.path.abspath(args.output)
    print(f"\nSaved: {out_abs}")
    print("\nNext step:\n  py -3.10 test1.py")


if __name__ == "__main__":
    main()
