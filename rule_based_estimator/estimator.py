from abc import ABC, abstractmethod
import numpy as np

class BaseRuleEvaluator(ABC):
    """Базовый класс для всех rule-based оценщиков."""
    def __init__(self):
        self.score = 100
        self.feedback = []

    @abstractmethod
    def evaluate(self, features):
        """Оценивает одно упражнение. Возвращает score и feedback."""
        pass

    def _penalize(self, condition, message, penalty):
        """Помощник: снижает оценку и добавляет комментарий."""
        if condition:
            self.score -= penalty
            self.feedback.append(message)

    def result(self):
        return {"score": max(self.score, 0), "feedback": self.feedback}


class SquatEvaluator(BaseRuleEvaluator):
    def evaluate(self, features):
        knee_angle = features.get("knee_angle", 180)
        back_tilt = features.get("back_tilt_angle", 0)
        balance_x = features.get("balance_x", 0)
        hip_depth = features.get("squat_depth", 0)

        self._penalize(knee_angle > 140, "Недостаточно сгибаешь колени — приседай глубже.", 10)
        self._penalize(knee_angle < 60, "Слишком глубокий присед — поднимись чуть выше.", 5)
        self._penalize(abs(back_tilt - 180) > 25, "Спина должна быть ровной — не заваливай корпус вперёд.", 5)
        self._penalize(balance_x > 0.1, "Держи равновесие — корпус смещён относительно ног.", 5)
        self._penalize(hip_depth > 0.2, "Бёдра опускаются слишком низко.", 3)

        return self.result()
    

class PushupEvaluator(BaseRuleEvaluator):
    def evaluate(self, features):
        elbow_angle = features.get("elbow_angle", 180)
        torso_angle = features.get("torso_angle_from_vertical", 0)
        balance_y = features.get("balance_y", 0)

        self._penalize(elbow_angle > 160, "Ты не выпрямляешь руки в верхней фазе.", 10)
        self._penalize(elbow_angle < 70, "Опускаешься слишком низко — контролируй амплитуду.", 5)
        self._penalize(abs(torso_angle - 90) > 20, "Тело не прямое — держи линию плеч–таз–пятки.", 5)
        self._penalize(balance_y > 0.1, "Смещаешь центр тяжести — держи стабильную стойку.", 5)

        return self.result()
    

    # base class
    class ExerciseEvaluator:
        def __init__(self):
            self.evaluators = {
                "squat": SquatEvaluator(),
                "pushup": PushupEvaluator(),
            }

        def evaluate(self, exercise_type, features):
            if exercise_type not in self.evaluators:
                raise ValueError(f"Unsupported exercise type: {exercise_type}")
            return self.evaluators[exercise_type].evaluate(features)