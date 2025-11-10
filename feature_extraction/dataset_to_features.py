import pandas as pd
import numpy as np
from tqdm import tqdm

# === 1. Data loading ===
df_labels = pd.read_csv("../dataset/labels.csv")
df_landmarks = pd.read_csv("../dataset/landmarks.csv")

# === 2. Merging by pose_id ===
df = df_landmarks.merge(df_labels, on="pose_id")

# === 3. List of coordinates (33 points × 3 coodrs) ===
landmark_names = [
    "nose", "left_eye_inner", "left_eye", "left_eye_outer", "right_eye_inner", "right_eye",
    "right_eye_outer", "left_ear", "right_ear", "mouth_left", "mouth_right", "left_shoulder",
    "right_shoulder", "left_elbow", "right_elbow", "left_wrist", "right_wrist", "left_pinky_1",
    "right_pinky_1", "left_index_1", "right_index_1", "left_thumb_2", "right_thumb_2", "left_hip",
    "right_hip", "left_knee", "right_knee", "left_ankle", "right_ankle", "left_heel",
    "right_heel", "left_foot_index", "right_foot_index"
]

# === 4. Feature extraction ===
from feature_extractor import FeatureExtractor
extractor = FeatureExtractor()

features_list = []
labels_list = []

for _, row in tqdm(df.iterrows(), total=len(df)):

    coords = []
    for name in landmark_names:
        coords.append([row[f"x_{name}"], row[f"y_{name}"], row[f"z_{name}"]])
    coords = np.array(coords)

    # we extract features here
    _ , features = extractor.build_feature_vector(coords, 'auto')
    features_list.append(features)
    labels_list.append(row["pose"])

# === 5. Format to DataFrame ===
features_df = pd.DataFrame(features_list)
features_df["pose"] = labels_list

print(features_df.head())
print(features_df["pose"].value_counts())

# === 6. Group by pose type ===
mean_features = features_df.groupby("pose").mean().reset_index()
print(mean_features)