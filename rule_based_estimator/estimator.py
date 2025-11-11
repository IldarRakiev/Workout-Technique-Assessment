from abc import ABC, abstractmethod
import numpy as np
from scipy.signal import find_peaks
from statistics import mean

class BaseRuleEvaluator(ABC):
    """Base class for all rule-based evaluators."""
    def __init__(self):
        self.score = 100
        self.feedback = []

    @abstractmethod
    def evaluate(self, features):
        """Evaluates one exercise and gives a score and feedback."""
        pass

    def evaluate_sequence(self, feature_sequence, every_n=10):
        """Sequence of exercises evaluation."""
        scores = []
        feedbacks = []
        for i, f in enumerate(feature_sequence[::every_n]):
            self.score = 100
            self.feedback = []
            self.evaluate(f)
            scores.append(self.score)
            feedbacks.extend(self.feedback)
        return {"mean_score": np.mean(scores), "feedback": list(set(feedbacks))}
    
    def phase_analysis(self, feature_sequence, every_n=10):
        """Phase-level analysis hook.

        Default implementation returns a perfect phase score (no penalties).
        Subclasses should override to implement up/down / amplitude checks.

        Returns:
            dict: {"phase_score": float, "phase_feedback": [str,...]}
        """
        return {"phase_score": 100.0, "phase_feedback": []}

    def evaluate_unified(self, feature_sequence, every_n=10, alpha=0.6, beta=0.4):
        """Unified evaluation combining frame-level quality and phase-level analysis.

        Args:
            feature_sequence: list of feature dicts
            every_n: sampling step for frame-level evaluation
            alpha: weight for frame-level score
            beta: weight for phase-level score (alpha+beta should be 1.0 ideally)

        Returns:
            dict: {
               "score": float,
               "frame_score": float,
               "phase_score": float,
               "feedback": [str,...]
            }
        """
        # Frame-level aggregated result
        frame_res = self.evaluate_sequence(feature_sequence, every_n=every_n)
        frame_score = frame_res["mean_score"]
        frame_feedback = frame_res["feedback"]

        # Phase-level result (subclass may override phase_analysis)
        phase_res = self.phase_analysis(feature_sequence, every_n=every_n)
        phase_score = phase_res.get("phase_score", 100.0)
        phase_feedback = phase_res.get("phase_feedback", [])

        # combine
        final_score = float(alpha * frame_score + beta * phase_score)
        combined_feedback = list(dict.fromkeys(frame_feedback + phase_feedback))

        return {
            "score": round(final_score, 1),
            "frame_score": round(frame_score, 1),
            "phase_score": round(phase_score, 1),
            "feedback": combined_feedback
        }

    def _penalize(self, condition, message, penalty):
        """Helper function: decrease the valuse of score and add a feedback when condition."""
        if condition:
            self.score -= penalty
            self.feedback.append(message)

    def result(self):
        return {"score": max(self.score, 0), "feedback": self.feedback}


class PushupEvaluator(BaseRuleEvaluator):
    def evaluate(self, features):
        """Frame-level evaluation for a single pose."""
        elbow_angle = features.get("elbow_angle", 180)
        torso_angle = features.get("torso_angle_from_vertical", 90)
        balance_y = features.get("balance_y", 0)

        self._penalize(elbow_angle > 160, "Do not skip elbow bending — go lower.", 15)
        self._penalize(elbow_angle < 60, "Too deep — control your range.", 5)
        self._penalize(abs(torso_angle - 90) > 15, "Keep your body straight — align shoulders, hips, heels.", 10)
        self._penalize(abs(balance_y) > 0.1, "Maintain body balance — avoid shifting sideways.", 5)

        return self.result()
    
    def phase_analysis(self, feature_sequence, every_n=5):
        """
        Phase-level (up/down) analysis for push-ups.
        Detects amplitude and elbow bend in the terminal phases.
        """
        # --- Build proxy series: prefer hip_y, then nose_y, fallback to elbow_angle ---
        y_series = np.array([f.get("hip_y", np.nan) for f in feature_sequence[::every_n]])
        if np.all(np.isnan(y_series)):
            y_series = np.array([f.get("nose_y", np.nan) for f in feature_sequence[::every_n]])
        if np.all(np.isnan(y_series)):
            elbow_series = np.array([f.get("elbow_angle", np.nan) for f in feature_sequence[::every_n]])
            if elbow_series.size == 0 or np.all(np.isnan(elbow_series)):
                return {"phase_feedback": ["Not enough data for phase detection."], "phase_penalty": 0}
            series = elbow_series
            invert = False
        else:
            series = y_series
            invert = False

        # --- Clean data ---
        valid_idx = ~np.isnan(series)
        series = series[valid_idx]
        if series.size < 6:
            return {"phase_feedback": ["Not enough frames for phase detection."], "phase_penalty": 0}

        # --- Detect peaks (up) and troughs (down) ---
        peaks, _ = find_peaks(series, distance=3)
        troughs, _ = find_peaks(-series, distance=3)

        phase_feedback = []
        penalty = 0

        # --- If no clear cycles ---
        if len(peaks) < 1 or len(troughs) < 1:
            penalty += 15
            phase_feedback.append("No clear up/down cycles detected — complete full push-up reps.")

        # --- Amplitude check ---
        if len(peaks) and len(troughs):
            amp = float(np.mean(series[peaks]) - np.mean(series[troughs]))
            if amp < 0.05:
                penalty += 15
                phase_feedback.append("Range of motion too small — extend arms fully and lower chest closer to the ground.")

        return {"phase_feedback": phase_feedback, "phase_penalty": penalty}


class PullupEvaluator(BaseRuleEvaluator):
    """Rule-based evaluator for Pull-ups (up and down phases)."""
    
    def evaluate(self, f):
        elbow_angle = f.get("elbow_angle", 180)
        torso_angle = f.get("torso_angle_from_vertical", 0)
        balance_y = f.get("balance_y", 0)

        # Frame-level penalties
        self._penalize(elbow_angle > 160, "Not pulling up fully — raise your chin above the bar.", 10)
        self._penalize(elbow_angle < 70, "Pulling too high — control the top phase.", 5)
        self._penalize(abs(torso_angle - 90) > 20, "Keep your body straight — avoid swinging.", 5)
        self._penalize(balance_y > 0.1, "Do not lean sideways — maintain stability.", 5)

        return self.result()

    def phase_analysis(self, feature_sequence, every_n=10):
        # Determine top (up) and bottom (down) phases by min/max elbow angle
        elbows = [f.get("elbow_angle", 180) for f in feature_sequence[::every_n]]
        up_idx = np.argmin(elbows)  # max contraction → elbow smallest
        down_idx = np.argmax(elbows)  # extended arms → elbow largest

        phase_feedback = []
        phase_score = 100

        # Top phase check
        f_up = feature_sequence[up_idx]
        if f_up.get("elbow_angle", 180) > 90:
            phase_score -= 5
            phase_feedback.append("Top phase: Pull higher, chin should be over the bar.")

        # Bottom phase check
        f_down = feature_sequence[down_idx]
        if f_down.get("elbow_angle", 180) < 160:
            phase_score -= 5
            phase_feedback.append("Bottom phase: Arms not fully extended.")

        return {"phase_score": phase_score, "phase_feedback": phase_feedback}


class SitupEvaluator(BaseRuleEvaluator):
    """Rule-based evaluator for Sit-ups."""
    
    def evaluate(self, f):
        torso_angle = f.get("torso_angle_from_vertical", 90)
        hip_angle = f.get("hip_angle", 0)

        self._penalize(torso_angle < 60, "Not lifting torso enough — go higher.", 10)
        self._penalize(torso_angle > 120, "Too high — avoid hyperextension.", 5)
        self._penalize(hip_angle < 40, "Hips are too bent — maintain proper leg angle.", 5)

        return self.result()

    def phase_analysis(self, feature_sequence, every_n=10):
        torsos = [f.get("torso_angle_from_vertical", 90) for f in feature_sequence[::every_n]]
        up_idx = np.argmax(torsos)
        down_idx = np.argmin(torsos)

        phase_feedback = []
        phase_score = 100

        f_up = feature_sequence[up_idx]
        if f_up.get("torso_angle_from_vertical", 90) < 90:
            phase_score -= 5
            phase_feedback.append("Top phase: Lift torso higher.")

        f_down = feature_sequence[down_idx]
        if f_down.get("torso_angle_from_vertical", 90) > 60:
            phase_score -= 5
            phase_feedback.append("Bottom phase: Lower torso fully.")

        return {"phase_score": phase_score, "phase_feedback": phase_feedback}


class JumpingJackEvaluator(BaseRuleEvaluator):
    """Rule-based evaluator for Jumping Jacks."""

    def evaluate(self, f):
        arm_angle = f.get("left_arm_lift_angle", 0)
        leg_spread = f.get("hip_width", 0)

        self._penalize(arm_angle < 70, "Raise arms higher during the jump.", 5)
        self._penalize(leg_spread < 0.5, "Spread legs wider for full range.", 5)

        return self.result()

    def phase_analysis(self, feature_sequence, every_n=10):
        arms = [f.get("left_arm_lift_angle", 0) for f in feature_sequence[::every_n]]
        legs = [f.get("hip_width", 0) for f in feature_sequence[::every_n]]
        up_idx = np.argmax(arms)  # arms fully up
        down_idx = np.argmin(arms)  # arms down

        phase_feedback = []
        phase_score = 100

        f_up = feature_sequence[up_idx]
        if f_up.get("left_arm_lift_angle", 0) < 160:
            phase_score -= 5
            phase_feedback.append("Top phase: Raise arms fully above head.")

        f_down = feature_sequence[down_idx]
        if f_down.get("left_arm_lift_angle", 0) > 20:
            phase_score -= 5
            phase_feedback.append("Bottom phase: Lower arms fully.")

        return {"phase_score": phase_score, "phase_feedback": phase_feedback}


class SquatEvaluator(BaseRuleEvaluator):
    """Rule-based evaluator for Squats."""

    def evaluate(self, f):
        knee_angle = f.get("knee_angle", 180)
        back_tilt = f.get("back_tilt_angle", 0)
        balance_x = f.get("balance_x", 0)
        hip_depth = f.get("squat_depth", 0)

        self._penalize(knee_angle > 140, "Not bending knees enough — go deeper.", 10)
        self._penalize(knee_angle < 60, "Squat too deep — control the depth.", 5)
        self._penalize(abs(back_tilt - 180) > 25, "Keep back straight — avoid leaning forward.", 5)
        self._penalize(balance_x > 0.1, "Maintain balance — hips not aligned.", 5)
        self._penalize(hip_depth > 0.2, "Hips lower than recommended.", 3)

        return self.result()

    def phase_analysis(self, feature_sequence, every_n=10):
        hips = [f.get("squat_depth", 0) for f in feature_sequence[::every_n]]
        knee_angles = [f.get("knee_angle", 180) for f in feature_sequence[::every_n]]

        down_idx = np.argmax(hips)  # bottom of squat
        up_idx = np.argmin(hips)    # standing

        phase_feedback = []
        phase_score = 100

        f_down = feature_sequence[down_idx]
        if f_down.get("knee_angle", 180) > 120:
            phase_score -= 5
            phase_feedback.append("Bottom phase: Bend knees more.")

        f_up = feature_sequence[up_idx]
        if f_up.get("knee_angle", 180) < 160:
            phase_score -= 5
            phase_feedback.append("Top phase: Straighten knees fully.")

        return {"phase_score": phase_score, "phase_feedback": phase_feedback}


# base class
class ExerciseEvaluator:
    def __init__(self):
        self.evaluators = {
            "pushup": PushupEvaluator(),
            "pullup": PullupEvaluator(),
            "situp": SitupEvaluator(),
            "jumping_jack": JumpingJackEvaluator(),
            "squat": SquatEvaluator(),
        }

    def evaluate(self, exercise_type, features, every_n=10, alpha=0.6, beta=0.4):
        """
        Evaluate either a single frame (features is a dict) or a sequence (features is a list of dicts).
        Returns unified result for sequences or frame-level result for single frames.
        """
        if exercise_type not in self.evaluators:
            raise ValueError(f"Unsupported exercise type: {exercise_type}")

        evaluator = self.evaluators[exercise_type]

        if isinstance(features, list):
            return evaluator.evaluate_unified(features, every_n=every_n, alpha=alpha, beta=beta)
        else:
            evaluator.score = 100.0
            evaluator.feedback = []
            evaluator.evaluate(features)
            return evaluator.result()