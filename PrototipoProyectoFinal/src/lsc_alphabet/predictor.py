from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np

from .labels import display_label
from .landmarks import LandmarkResult, extract_landmark_result


@dataclass(frozen=True)
class Prediction:
    label: str
    display_label: str
    confidence: float
    probabilities: dict[str, float]


class GesturePredictor:
    def __init__(
        self,
        model: Any,
        *,
        labels: list[str],
        display_labels: dict[str, str],
        feature_names: list[str],
        model_name: str = "model",
        model_type: str = "frame",
        sequence_length: int | None = None,
        metrics: dict[str, Any] | None = None,
    ) -> None:
        self.model = model
        self.labels = labels
        self.display_labels = display_labels
        self.feature_names = feature_names
        self.model_name = model_name
        self.model_type = model_type
        self.sequence_length = sequence_length
        self.metrics = metrics or {}

    @classmethod
    def from_file(cls, model_path: str | Path) -> "GesturePredictor":
        package = joblib.load(model_path)
        return cls(
            package["model"],
            labels=list(package.get("labels", [])),
            display_labels=dict(package.get("display_labels", {})),
            feature_names=list(package.get("feature_names", [])),
            model_name=str(package.get("model_name", "model")),
            model_type=str(package.get("model_type", "frame")),
            sequence_length=package.get("sequence_length"),
            metrics=dict(package.get("metrics", {})),
        )

    def predict_features(self, feature_vector: np.ndarray) -> Prediction:
        X = np.asarray(feature_vector, dtype=np.float32).reshape(1, -1)
        if self.feature_names and X.shape[1] != len(self.feature_names):
            raise ValueError(
                f"El modelo espera {len(self.feature_names)} features, pero recibio {X.shape[1]}."
            )

        if hasattr(self.model, "predict_proba"):
            probabilities = self.model.predict_proba(X)[0]
            classes = list(self.model.classes_)
            best_index = int(np.argmax(probabilities))
            label = str(classes[best_index])
            confidence = float(probabilities[best_index])
            probability_map = {
                str(class_label): float(prob)
                for class_label, prob in zip(classes, probabilities)
            }
        else:
            label = str(self.model.predict(X)[0])
            confidence = 1.0
            probability_map = {label: confidence}

        return Prediction(
            label=label,
            display_label=self.display_labels.get(label, display_label(label)),
            confidence=confidence,
            probabilities=probability_map,
        )

    def predict_image(
        self,
        image_rgb: np.ndarray,
        hands: Any,
        *,
        mirror_left: bool = True,
    ) -> tuple[Prediction | None, LandmarkResult | None]:
        landmark_result = extract_landmark_result(image_rgb, hands, mirror_left=mirror_left)
        if landmark_result is None:
            return None, None
        return self.predict_features(landmark_result.feature_vector), landmark_result
