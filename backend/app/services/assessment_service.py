import os
import numpy as np
from fastapi import UploadFile
import tempfile
from services.mediapipe_extractor import extract_landmarks_from_video
from models.feature_extractor import FeatureExtractor
from models.estimator import ExerciseEvaluator
# from app.ml.autoencoder_validator import AutoencoderValidator  # will be added later

class AssessmentService:
    """Main service for handling video technique assessment pipeline."""

    def __init__(self):
        self.extractor = FeatureExtractor()
        self.estimator = ExerciseEvaluator()
        # self.validator = AutoencoderValidator()  # TODO: add ML validation later

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
        for frame_data in landmarks_array:
            print(type(frame_data))
            print(frame_data.shape)
            _, feat_dict = self.extractor.build_feature_vector(frame_data, view="auto")
            feature_sequence.append(feat_dict)

        # === STEP 3: Rule-based evaluation ===
        print("Running rule-based assessment...")
        result = self.estimator.evaluate(exercise_type, feature_sequence)

        # === STEP 4: Autoencoder validation (optional) ===
        # print("Validating with autoencoder...")
        # ml_validation = self.validator.validate(feature_sequence)
        # result["ml_confidence"] = ml_validation["confidence"]

        # === STEP 5: Final combined result ===
        print("Assessment complete")
        return {
            "exercise": exercise_type,
            "score": result["score"],
            "feedback": result["feedback"],
            "frame_score": result.get("frame_score"),
            "phase_score": result.get("phase_score"),
            # "ml_confidence": result.get("ml_confidence", None),
        }
