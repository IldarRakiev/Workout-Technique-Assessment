import os
import numpy as np
from fastapi import UploadFile
import tempfile
from services.mediapipe_extractor import extract_landmarks_from_video
from models.feature_extractor import FeatureExtractor
from models.estimator import ExerciseEvaluator

try:
    from models.autoencoder import AutoencoderValidator
except ImportError as e:
    print(f"Import Error: {e}")

class AssessmentService:
    """Main service for handling video technique assessment pipeline."""

    def __init__(self):
        print("Начало __init__")
        self.extractor = FeatureExtractor()
        print("Extractor создан")
        self.estimator = ExerciseEvaluator()
        print("Estimator создан")
        
        print("Try to create a validator...")
        try:
            self.validator = AutoencoderValidator()
            print("Validator успешно создан")
        except Exception as e:
            print(f"Error when creating validator: {e}")
            import traceback
            traceback.print_exc()
            self.validator = None

    def assess_uploaded_video(self, file: UploadFile, exercise_type: str):
        """Process uploaded video in memory (temporary file)."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(file.file.read())
            tmp_path = tmp.name
        try:
            result = self.assess_video(tmp_path, exercise_type)
        finally:
            os.remove(tmp_path)  # cleanup!

        return result    

    def assess_video(self, video_path: str, exercise_type: str) -> dict:
        """
        Run the full analysis pipeline:
        1. Extract keypoints with MediaPipe
        2. Build feature sequence
        3. Evaluate with rule-based evaluator
        4. Validate with autoencoder (optional)
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video not found: {video_path}")

        # === STEP 1: Extract pose landmarks ===
        print("Extracting landmarks from video...")
        landmarks_array = extract_landmarks_from_video(video_path)
        print(type(landmarks_array))
        print("ss")
        print(f"landmarks_array shape: {None if landmarks_array is None else len(landmarks_array)}")
        if landmarks_array is None or len(landmarks_array) == 0:
            return {"error": "No pose detected in video."}

        # === STEP 2: Extract features from landmarks ===
        print("Building feature sequence...")
        feature_sequence = []
        feat_vector_sequence = []
        for frame_data in landmarks_array:
            print(type(frame_data))
            print(frame_data.shape)
            feat_vector, feat_dict = self.extractor.build_feature_vector(frame_data, view="auto")
            feature_sequence.append(feat_dict)
            feat_vector_sequence.append(feat_vector)

        # === STEP 3: Rule-based evaluation ===
        print("Running rule-based assessment...")
        result = self.estimator.evaluate(exercise_type, feature_sequence)

        # === STEP 4: Autoencoder validation ===
        print("Validating with autoencoder...")
        ml_validation = self.validator.validate(feat_vector_sequence)

        result["ml_score"] = ml_validation["avg_reconstruction_error"]
        result["is_anomaly"] = ml_validation["is_anomaly"]

        if result["is_anomaly"]:
            result["feedback"].append("Movement pattern deviates from normal examples.")
            result["score"] -= 10
        
        print(result["ml_score"])
        print(result["is_anomaly"])

        if len(result["feedback"]) >= 4:
            result["score"] -= 20
            result["frame_score"] -= 20
            result["phase_score"] -= 10
        if len(result["feedback"]) >= 5:
            result["score"] -= 20
            result["frame_score"] -= 20
            result["phase_score"] -= 10
            result["feedback"] = ["⚠️ Wrong exercise or anomaly wrong technique!"]

        # === STEP 5: Final combined result ===
        print("Assessment complete")
        return {
            "exercise": exercise_type,
            "score": round(result["score"]),
            "feedback": result["feedback"],
            "frame_score": round(result.get("frame_score")),
            "phase_score": round(result.get("phase_score")),
            "is_anomaly": result.get("is_anomaly"),
        }
