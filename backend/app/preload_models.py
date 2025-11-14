import mediapipe as mp

mp.solutions.pose.Pose(
    static_image_mode=False,
    model_complexity=2,
)