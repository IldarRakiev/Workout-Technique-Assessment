from autoencoder import AutoencoderValidator
import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
import sklearn

validator = AutoencoderValidator()

FEATURE_PATH = "../../../feature_vectors/feature_vectors.pkl"

with open(FEATURE_PATH, "rb") as f:
    exercise_features = pickle.load(f)

all_vectors = np.vstack(list(exercise_features.values()))
print(f"\nCombined feature matrix: {all_vectors.shape}")

print(all_vectors)

ml_validation = validator.validate(all_vectors)

#print(ml_validation["avg_reconstruction_error"])
#print(ml_validation["is_anomaly"])



