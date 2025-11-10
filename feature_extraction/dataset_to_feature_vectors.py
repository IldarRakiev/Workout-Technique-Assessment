import pandas as pd
import numpy as np
import pickle
from feature_extractor import FeatureExtractor
import os

# --- exercise view map ---

EXERCISE_VIEW_MAP = {
    "pushup": "front",
    "squat": "front",
    "situp": "front",
    "plank": "front",
    "jumping_jacks": "front",
    "bicep_curls": "front",
    "shoulder_press": "front",
    "lateral_raise": "front"
}

# --- load the data ---
labels = pd.read_csv("../dataset/labels.csv")
landmarks = pd.read_csv("../dataset/landmarks.csv")

# --- merge by pose_id ---
data = landmarks.merge(labels, on="pose_id")

# --- extractor class initialization ---
extractor = FeatureExtractor()

# die: exercise (pose) → list of feature vectors
exercise_features = {}

for pose_name, group in data.groupby("pose"):
    all_vectors = []
    
    for _, row in group.iterrows():
        # extract coords (33 points × 3 coodrs)
        points = []
        for i in range(33):
            x = row[f"x_{i}"] if f"x_{i}" in row else row.filter(like=f"x_").values[i]
            y = row[f"y_{i}"] if f"y_{i}" in row else row.filter(like=f"y_").values[i]
            z = row[f"z_{i}"] if f"z_{i}" in row else row.filter(like=f"z_").values[i]
            points.append([x, y, z])
        
        # define a view of camera
        base_exercise = pose_name.split("_")[0].lower()
        view = EXERCISE_VIEW_MAP.get(base_exercise, "front")

        # extract the features
        feat_vector, _ = extractor.build_feature_vector(points, view=view)
        all_vectors.append(feat_vector)

    # save all the features of the pose
    exercise_features[pose_name] = np.vstack(all_vectors)

print("Number of exercises (poses):", len(exercise_features))
for k, v in exercise_features.items():
    print(f"{k}: {v.shape}")

# --- Save the result ---
output_dir = "../feature_vectors"
os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(output_dir, "feature_vectors.pkl")

with open(output_path, "wb") as f:
    pickle.dump(exercise_features, f)

print("💾 All the feature vectors were saved in exercise_features.pkl")
