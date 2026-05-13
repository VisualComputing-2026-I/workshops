from __future__ import annotations

import cv2
import numpy as np

from .landmarks import HAND_CONNECTIONS, LandmarkResult
from .predictor import Prediction


def draw_landmarks(image_bgr: np.ndarray, result: LandmarkResult | None) -> np.ndarray:
    if result is None:
        return image_bgr

    height, width = image_bgr.shape[:2]
    points = [
        (int(np.clip(x, 0, 1) * width), int(np.clip(y, 0, 1) * height))
        for x, y, _ in result.image_landmarks
    ]

    for start, end in HAND_CONNECTIONS:
        cv2.line(image_bgr, points[start], points[end], (40, 160, 255), 2, cv2.LINE_AA)
    for point in points:
        cv2.circle(image_bgr, point, 4, (20, 230, 120), -1, cv2.LINE_AA)

    return image_bgr


def draw_overlay(
    image_bgr: np.ndarray,
    prediction: Prediction | None,
    *,
    text: str,
    status: str = "",
) -> np.ndarray:
    height, width = image_bgr.shape[:2]
    overlay = image_bgr.copy()
    cv2.rectangle(overlay, (0, 0), (width, 118), (20, 26, 33), -1)
    cv2.addWeighted(overlay, 0.82, image_bgr, 0.18, 0, image_bgr)

    if prediction is None:
        label = "Sin mano"
        confidence = ""
        color = (180, 190, 200)
    else:
        label = prediction.display_label
        confidence = f"{prediction.confidence:.0%}"
        color = (80, 220, 150) if prediction.confidence >= 0.75 else (60, 190, 255)

    cv2.putText(image_bgr, label, (22, 48), cv2.FONT_HERSHEY_SIMPLEX, 1.25, color, 3, cv2.LINE_AA)
    if confidence:
        cv2.putText(
            image_bgr,
            confidence,
            (105, 48),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.78,
            (225, 232, 240),
            2,
            cv2.LINE_AA,
        )

    visible_text = text[-42:] if text else ""
    cv2.putText(
        image_bgr,
        visible_text,
        (22, 92),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.86,
        (245, 245, 245),
        2,
        cv2.LINE_AA,
    )

    if status:
        cv2.putText(
            image_bgr,
            status,
            (22, height - 24),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.58,
            (220, 225, 230),
            1,
            cv2.LINE_AA,
        )

    return image_bgr
