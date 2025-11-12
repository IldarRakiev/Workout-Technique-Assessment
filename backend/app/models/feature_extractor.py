import numpy as np

class FeatureExtractor:
    """
    Full biomechanical feature extractor for pose analysis (front & side views).
    Generates comprehensive features for both ML and rule-based analysis.
    """

    def __init__(self, keypoints=None):
        # MediaPipe keypoint indices
        self.KEYPOINTS = keypoints or {
            "nose": 0,
            "left_eye": 2,
            "right_eye": 5,
            "left_ear": 7,
            "right_ear": 8,
            "left_shoulder": 11,
            "right_shoulder": 12,
            "left_elbow": 13,
            "right_elbow": 14,
            "left_wrist": 15,
            "right_wrist": 16,
            "left_hip": 23,
            "right_hip": 24,
            "left_knee": 25,
            "right_knee": 26,
            "left_ankle": 27,
            "right_ankle": 28,
            "left_heel": 29,
            "right_heel": 30,
            "left_foot_index": 31,
            "right_foot_index": 32
        }

    # ===============================
    # Base geometric utilities
    # ===============================
    def angle_between_points(self, a, b, c):
        """Compute an angle (in degrees) between three points: a-b-c"""
        a, b, c = np.array(a), np.array(b), np.array(c)
        ba = a - b
        bc = c - b
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
        return np.degrees(np.arccos(cosine_angle))

    def distance(self, p1, p2):
        return np.linalg.norm(np.array(p1) - np.array(p2))

    def midpoint(self, p1, p2):
        return (np.array(p1) + np.array(p2)) / 2

    # ===============================
    # Pose normalization
    # ===============================
    def normalize_pose(self, points):
        """Centers the pose and scales by hip distance."""
        left_hip = points[self.KEYPOINTS['left_hip']]
        right_hip = points[self.KEYPOINTS['right_hip']]
        center = self.midpoint(left_hip, right_hip)
        scale = self.distance(left_hip, right_hip)
        if scale == 0:
            scale = 1.0
        normalized = [(np.array(p) - center) / scale for p in points]
        return normalized

    # ===============================
    # Universal features
    # ===============================
    def extract_joint_angles(self, points):
        """Knee, elbow, and torso angles."""
        angles = {}
        neck = self.midpoint(points[self.KEYPOINTS['left_shoulder']], points[self.KEYPOINTS['right_shoulder']])

        angles['left_knee'] = self.angle_between_points(points[self.KEYPOINTS['left_hip']],
                                                        points[self.KEYPOINTS['left_knee']],
                                                        points[self.KEYPOINTS['left_ankle']])
        angles['right_knee'] = self.angle_between_points(points[self.KEYPOINTS['right_hip']],
                                                         points[self.KEYPOINTS['right_knee']],
                                                         points[self.KEYPOINTS['right_ankle']])
        angles['left_elbow'] = self.angle_between_points(points[self.KEYPOINTS['left_shoulder']],
                                                         points[self.KEYPOINTS['left_elbow']],
                                                         points[self.KEYPOINTS['left_wrist']])
        angles['right_elbow'] = self.angle_between_points(points[self.KEYPOINTS['right_shoulder']],
                                                          points[self.KEYPOINTS['right_elbow']],
                                                          points[self.KEYPOINTS['right_wrist']])
        angles['torso'] = self.angle_between_points(neck,
                                                    points[self.KEYPOINTS['left_hip']],
                                                    points[self.KEYPOINTS['left_knee']])
        return angles

    def extract_symmetry_features(self, points):
        """Estimates shoulder and hip symmetry."""
        features = {}
        left_shoulder = points[self.KEYPOINTS['left_shoulder']]
        right_shoulder = points[self.KEYPOINTS['right_shoulder']]
        left_hip = points[self.KEYPOINTS['left_hip']]
        right_hip = points[self.KEYPOINTS['right_hip']]

        features['shoulder_width'] = self.distance(left_shoulder, right_shoulder)
        features['hip_width'] = self.distance(left_hip, right_hip)
        features['shoulders_hips_ratio'] = features['shoulder_width'] / features['hip_width'] if features['hip_width'] > 0 else 0
        features['shoulder_tilt'] = abs(left_shoulder[1] - right_shoulder[1])
        features['hip_tilt'] = abs(left_hip[1] - right_hip[1])
        return features

    def extract_posture_features(self, points):
        """Body vertical alignment (spine tilt)."""
        features = {}
        neck = self.midpoint(points[self.KEYPOINTS['left_shoulder']], points[self.KEYPOINTS['right_shoulder']])
        mid_hip = self.midpoint(points[self.KEYPOINTS['left_hip']], points[self.KEYPOINTS['right_hip']])
        torso_vec = np.array(neck) - np.array(mid_hip)
        vertical = np.array([0, -1, 0])
        cosine = np.dot(torso_vec, vertical) / (np.linalg.norm(torso_vec) * np.linalg.norm(vertical))
        features['torso_angle_from_vertical'] = np.degrees(np.arccos(np.clip(cosine, -1, 1)))
        return features

    def extract_balance_features(self, points):
        """Center of mass balance (projected along x and y)."""
        left_ankle = points[self.KEYPOINTS['left_ankle']]
        right_ankle = points[self.KEYPOINTS['right_ankle']]
        left_hip = points[self.KEYPOINTS['left_hip']]
        right_hip = points[self.KEYPOINTS['right_hip']]

        base_center = self.midpoint(left_ankle, right_ankle)
        hip_center = self.midpoint(left_hip, right_hip)
        balance_x = abs(base_center[0] - hip_center[0])
        balance_y = abs(base_center[1] - hip_center[1])
        return {'balance_x': balance_x, 'balance_y': balance_y}

    # ===============================
    # Front-view specific
    # ===============================
    def extract_front_symmetry_features(self, points):
        """Front-view: symmetry around vertical center."""
        features = {}
        left_shoulder = points[self.KEYPOINTS['left_shoulder']]
        right_shoulder = points[self.KEYPOINTS['right_shoulder']]
        left_knee = points[self.KEYPOINTS['left_knee']]
        right_knee = points[self.KEYPOINTS['right_knee']]
        left_hip = points[self.KEYPOINTS['left_hip']]
        right_hip = points[self.KEYPOINTS['right_hip']]
        center_x = (left_hip[0] + right_hip[0]) / 2
        features['shoulder_x_sym'] = abs(left_shoulder[0] - (2 * center_x - right_shoulder[0]))
        features['knee_x_sym'] = abs(left_knee[0] - (2 * center_x - right_knee[0]))
        features['hip_x_sym'] = abs(left_hip[0] - (2 * center_x - right_hip[0]))
        features['shoulder_y_tilt'] = abs(left_shoulder[1] - right_shoulder[1])
        features['hip_y_tilt'] = abs(left_hip[1] - right_hip[1])
        return features

    def extract_front_alignment_features(self, points):
        """Front-view: body tilt and vertical alignment."""
        features = {}
        neck = self.midpoint(points[self.KEYPOINTS['left_shoulder']], points[self.KEYPOINTS['right_shoulder']])
        mid_hip = self.midpoint(points[self.KEYPOINTS['left_hip']], points[self.KEYPOINTS['right_hip']])
        torso_vec = np.array(neck) - np.array(mid_hip)
        vertical = np.array([0, -1, 0])
        cosine = np.dot(torso_vec, vertical) / (np.linalg.norm(torso_vec) * np.linalg.norm(vertical))
        features['body_tilt_angle'] = np.degrees(np.arccos(np.clip(cosine, -1, 1)))
        return features
    
    def left_arm_lift_angle(self, points):
        """
        Compute angle of left arm lift (shoulder-elbow-wrist)
        Useful для Front Raise
        """
        a = points[self.KEYPOINTS['left_shoulder']]
        b = points[self.KEYPOINTS['left_elbow']]
        c = points[self.KEYPOINTS['left_wrist']]

        ba = np.array(a) - np.array(b)
        bc = np.array(c) - np.array(b)
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
        return np.degrees(np.arccos(cosine_angle))

    def right_arm_lift_angle(self, points):
        """
        Compute angle of right arm lift (shoulder-elbow-wrist)
        """
        a = points[self.KEYPOINTS['right_shoulder']]
        b = points[self.KEYPOINTS['right_elbow']]
        c = points[self.KEYPOINTS['right_wrist']]

        ba = np.array(a) - np.array(b)
        bc = np.array(c) - np.array(b)
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
        return np.degrees(np.arccos(cosine_angle))

    def extract_arm_lift_angle(self, points):
        "Extracts arm lift angles for both left and right sides"
        features = {}

        features['left_arm_lift_angle'] = self.left_arm_lift_angle(points)
        features['right_arm_lift_angle'] = self.right_arm_lift_angle(points)

        return features

    # ===============================
    # Side-view specific
    # ===============================
    def extract_side_motion_features(self, points):
        """Side-view: dynamic pose depth and angles."""
        features = {}
        left_hip = points[self.KEYPOINTS['left_hip']]
        left_knee = points[self.KEYPOINTS['left_knee']]
        left_ankle = points[self.KEYPOINTS['left_ankle']]
        left_shoulder = points[self.KEYPOINTS['left_shoulder']]

        features['squat_depth'] = left_hip[1] - left_knee[1]
        features['back_tilt_angle'] = self.angle_between_points(left_shoulder, left_hip, left_knee)
        return features

    def extract_side_arm_leg_angles(self, points):
        """Side-view: elbow, knee, and hip angles."""
        features = {}
        features['knee_angle'] = self.angle_between_points(points[self.KEYPOINTS['left_hip']],
                                                          points[self.KEYPOINTS['left_knee']],
                                                          points[self.KEYPOINTS['left_ankle']])
        features['elbow_angle'] = self.angle_between_points(points[self.KEYPOINTS['left_shoulder']],
                                                           points[self.KEYPOINTS['left_elbow']],
                                                           points[self.KEYPOINTS['left_wrist']])
        features['hip_angle'] = self.angle_between_points(points[self.KEYPOINTS['left_shoulder']],
                                                         points[self.KEYPOINTS['left_hip']],
                                                         points[self.KEYPOINTS['left_knee']])
        return features


    # ===============================
    # Camera view detection
    # ===============================
    def detect_view(self, points):
        """
        Auto-detects if pose is viewed from 'front' or 'side'.
        Uses combination of shoulder/hip symmetry, torso angle, and leg X displacement.
        """
        left_shoulder = points[self.KEYPOINTS['left_shoulder']]
        right_shoulder = points[self.KEYPOINTS['right_shoulder']]
        left_hip = points[self.KEYPOINTS['left_hip']]
        right_hip = points[self.KEYPOINTS['right_hip']]
        left_knee = points[self.KEYPOINTS['left_knee']]
        right_knee = points[self.KEYPOINTS['right_knee']]

        # 1. Shoulder-hip horizontal symmetry
        center_x = (left_hip[0] + right_hip[0]) / 2
        shoulder_sym = abs(left_shoulder[0] - (2 * center_x - right_shoulder[0]))
        hip_sym = abs(left_hip[0] - (2 * center_x - right_hip[0]))
        symmetry_score = (shoulder_sym + hip_sym) / 2

        # 2. Torso orientation in XY plane
        neck = self.midpoint(left_shoulder, right_shoulder)
        mid_hip = self.midpoint(left_hip, right_hip)
        torso_vec = np.array(neck) - np.array(mid_hip)
        torso_angle_xy = np.degrees(np.arctan2(torso_vec[0], -torso_vec[1]))  # approx horizontal tilt

        # 3. Legs X displacement
        leg_dx = abs((left_knee[0] - right_knee[0]) - (left_hip[0] - right_hip[0]))

        # Combine scores
        score = symmetry_score + abs(torso_angle_xy) + leg_dx

        # Threshold empirically (можно подстраивать)
        if score < 0.15:
            return "front"
        else:
            return "side"



    # ===============================
    # Unified feature builder
    # ===============================
    def build_feature_vector(self, points, view="side"):
        """
        Builds a comprehensive feature vector for one frame.
        Args:
            points: list of 33 (x,y,z)
            view: 'front' or 'side'
        """
        points = self.normalize_pose(points)
        features = {}

        if view == "auto":
            view = self.detect_view(points)

        # universal features
        features.update(self.extract_joint_angles(points))
        features.update(self.extract_symmetry_features(points))
        features.update(self.extract_posture_features(points))
        features.update(self.extract_balance_features(points))
        features.update(self.extract_arm_lift_angle(points))

        if view == "front":
            features.update(self.extract_front_symmetry_features(points))
            features.update(self.extract_front_alignment_features(points))
        elif view == "side":
            features.update(self.extract_side_arm_leg_angles(points))
            features.update(self.extract_side_motion_features(points))
        else:
            raise ValueError("Invalid view type. Use 'front' or 'side' or 'auto'.")

        feature_vector = np.array([v for k, v in features.items() if k != 'detected_view'])
        return feature_vector, features
