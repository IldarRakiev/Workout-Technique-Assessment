import mediapipe as mp
import cv2
import numpy as np
import os


# === Initialization ===
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Names of 33 landmarks
KEYPOINT_NAMES = [
    "nose", "left_eye_inner", "left_eye", "left_eye_outer", "right_eye_inner", "right_eye", "right_eye_outer",
    "left_ear", "right_ear", "mouth_left", "mouth_right",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow", "left_wrist", "right_wrist",
    "left_pinky", "right_pinky", "left_index", "right_index", "left_thumb", "right_thumb",
    "left_hip", "right_hip", "left_knee", "right_knee", "left_ankle", "right_ankle",
    "left_heel", "right_heel", "left_foot_index", "right_foot_index"
]


def extract_landmarks_from_video(video_path, draw=False, sample_rate=1):
    """
    Extract 3D pose landmarks from a video using MediaPipe Pose.

    Args:
        video_path (str): Path to the input video file.
        draw (bool): Whether to visualize landmarks on frames.
        sample_rate (int): Process every Nth frame (to speed up processing).

    Returns:
        list[np.ndarray]: A list of numpy arrays, each shape = (33, 3)
                          representing (x, y, z) coordinates per frame.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")

    # Initialize MediaPipe pose detector
    pose = mp_pose.Pose(
        model_complexity=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        static_image_mode=False
    )

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"Video loaded: {total_frames} frames @ {fps:.2f} FPS")

    landmarks_sequence = []
    frame_count = 0
    detected_frames = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame_count += 1

        # Skip frames according to sample_rate
        if frame_count % sample_rate != 0:
            continue

        # Convert to RGB
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image_rgb.flags.writeable = False
        results = pose.process(image_rgb)
        image_rgb.flags.writeable = True

        if results.pose_landmarks:
            detected_frames += 1
            landmarks = np.array(
                [[lm.x, lm.y, lm.z] for lm in results.pose_landmarks.landmark],
                dtype=np.float32
            )
            landmarks_sequence.append(landmarks)

            if draw:
                mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=1)
                )
                cv2.imshow("Pose Detection", frame)
                if cv2.waitKey(1) & 0xFF == 27:  # ESC to stop
                    break
        else:
            # Add zero frame if no pose detected
            landmarks_sequence.append(np.zeros((33, 3), dtype=np.float32))

        if frame_count % 50 == 0:
            print(f"Processed {frame_count}/{total_frames} frames "
                  f"({frame_count/total_frames*100:.1f}%)")

    cap.release()
    pose.close()
    if draw:
        cv2.destroyAllWindows()

    print(f"\nDone: {len(landmarks_sequence)} frames processed, "
          f"{detected_frames} with detected pose landmarks.")
    return landmarks_sequence
