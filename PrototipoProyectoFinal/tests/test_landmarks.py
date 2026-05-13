from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from lsc_alphabet.landmarks import FEATURE_NAMES, extract_landmark_result


@dataclass
class FakeLandmark:
    x: float
    y: float
    z: float


@dataclass
class FakeCategory:
    category_name: str
    score: float


class FakeHands:
    def process(self, image_rgb: np.ndarray):
        landmarks = [FakeLandmark(i / 20, (20 - i) / 20, 0.01 * i) for i in range(21)]
        return type(
            "FakeTasksResult",
            (),
            {
                "hand_landmarks": [landmarks],
                "handedness": [[FakeCategory("Right", 0.93)]],
            },
        )()


def test_extract_landmark_result_supports_mediapipe_tasks_shape() -> None:
    image = np.zeros((32, 32, 3), dtype=np.uint8)

    result = extract_landmark_result(image, FakeHands())

    assert result is not None
    assert result.handedness == "Right"
    assert result.score == 0.93
    assert result.image_landmarks.shape == (21, 3)
    assert result.feature_vector.shape == (len(FEATURE_NAMES),)
