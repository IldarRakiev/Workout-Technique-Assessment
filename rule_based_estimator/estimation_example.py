import os
import sys
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

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'feature_extraction')))

from feature_extractor import FeatureExtractor
extractor = FeatureExtractor()

rows = df.iloc[660:904]
rows = df.iloc[1260:1304]

feat_dicts = []

for _, row in rows.iterrows():
    coords = []
    for name in landmark_names:
        coords.append([row[f"x_{name}"], row[f"y_{name}"], row[f"z_{name}"]])
    coords = np.array(coords)

    _, feat_dict = extractor.build_feature_vector(coords, view='auto')
    feat_dicts.append(feat_dict)

for k, v in feat_dict.items():
    print(f"{k}: {v}")

from estimator import ExerciseEvaluator

estimator = ExerciseEvaluator()
exercise_type = "squat"
result = estimator.evaluate(exercise_type, feat_dict)


print("Pose:", row["pose"])
print("Detected view:", feat_dict.get("detected_view", "unknown"))
print("Score:", result["score"])
print("Feedback:")
for f in result["feedback"]:
    print("-", f)


import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# MediaPipe connections (которые ключевые точки соединять)
connections = [
    (0, 1), (1, 2), (2, 3), (0, 4), (4, 5), (5, 6),  # голова/лицо
    (11, 13), (13, 15), (12, 14), (14, 16),           # руки
    (11, 12), (11, 23), (12, 24),                     # плечи и бедра
    (23, 24), (23, 25), (24, 26),                     # бедра и колени
    (25, 27), (26, 28), (27, 31), (28, 32)            # ноги и стопы
]

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# plot joints
ax.scatter(coords[:,0], coords[:,1], coords[:,2], c='r', s=20)

# plot bones
for a, b in connections:
    x = [coords[a,0], coords[b,0]]
    y = [coords[a,1], coords[b,1]]
    z = [coords[a,2], coords[b,2]]
    ax.plot(x, y, z, c='b')

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('3D Pose Visualization')
plt.show()