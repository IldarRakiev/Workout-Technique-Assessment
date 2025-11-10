import pickle
import numpy as np

# === 1. Uploading a saved dictionary with features ===
with open("../feature_vectors/feature_vectors.pkl", "rb") as f:
    exercise_features = pickle.load(f)

print(f"{len(exercise_features)} exercises are uploaded:")
for name, feats in exercise_features.items():
    print(f"  • {name:25s} → {feats.shape}")

# === 2. Example: how to extract all the features of exxercise ===
exercise_name = "pushups_down"   # you can substitute any of the exercise names from the dictionary 
if exercise_name in exercise_features:
    X = exercise_features[exercise_name]
    print(f"\nFeatures for '{exercise_name}': {X.shape}")
    print("Example of the first 3 vectors:\n", X[:3])
else:
    print(f"\nExercise '{exercise_name}' is not in feature dictionary!")

# === 3. Example: assemble all the features into one array to train the autoencoder ===
#    (for example, only the 'correct' poses)
all_vectors = np.vstack(list(exercise_features.values()))
print(f"\nA resulting set for training: {all_vectors.shape}")

# === 4. Normalization ===
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(all_vectors)
print(f"Normalized features: {X_scaled.shape}")

# === 5. Saving normalized data, if needed ===
np.save("../feature_vectors/all_features_scaled.npy", X_scaled)
print("\n💾 File 'all_features_scaled.npy' is saved.")
