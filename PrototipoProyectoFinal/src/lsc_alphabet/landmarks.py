from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import time
from typing import Any

import numpy as np
import requests

from .config import MODELS_DIR

WRIST_DISTANCE_INDICES = tuple(range(21))
TIP_PAIR_INDICES = (
    (4, 8),
    (4, 12),
    (4, 16),
    (4, 20),
    (8, 12),
    (8, 16),
    (8, 20),
    (12, 16),
    (12, 20),
    (16, 20),
)
FINGER_CHAINS = (
    (0, 1, 2, 3, 4),
    (0, 5, 6, 7, 8),
    (0, 9, 10, 11, 12),
    (0, 13, 14, 15, 16),
    (0, 17, 18, 19, 20),
)

FEATURE_NAMES = (
    [f"lm_{idx}_{axis}" for idx in range(21) for axis in ("x", "y", "z")]
    + [f"wrist_dist_{idx}" for idx in WRIST_DISTANCE_INDICES]
    + [f"tip_dist_{a}_{b}" for a, b in TIP_PAIR_INDICES]
    + [
        f"angle_{chain_idx}_{joint_idx}"
        for chain_idx, chain in enumerate(FINGER_CHAINS)
        for joint_idx in range(1, len(chain) - 1)
    ]
)

HAND_CONNECTIONS = (
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 4),
    (0, 5),
    (5, 6),
    (6, 7),
    (7, 8),
    (5, 9),
    (9, 10),
    (10, 11),
    (11, 12),
    (9, 13),
    (13, 14),
    (14, 15),
    (15, 16),
    (13, 17),
    (17, 18),
    (18, 19),
    (19, 20),
    (0, 17),
)

HAND_LANDMARKER_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)
DEFAULT_HAND_LANDMARKER_MODEL_PATH = MODELS_DIR / "mediapipe" / "hand_landmarker.task"


@dataclass(frozen=True)
class LandmarkResult:
    feature_vector: np.ndarray
    image_landmarks: np.ndarray
    normalized_landmarks: np.ndarray
    handedness: str
    score: float


@lru_cache(maxsize=1)
def _mp_hands_module() -> Any:
    import mediapipe as mp

    if not hasattr(mp, "solutions"):
        return None
    return mp.solutions.hands


def ensure_hand_landmarker_model(model_path: str | None = None) -> str:
    """Ensure the MediaPipe Tasks hand landmarker model is available locally."""

    path = DEFAULT_HAND_LANDMARKER_MODEL_PATH if model_path is None else MODELS_DIR / model_path
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size > 0:
        return str(path)

    try:
        with requests.get(HAND_LANDMARKER_MODEL_URL, stream=True, timeout=60) as response:
            response.raise_for_status()
            with path.open("wb") as file:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        file.write(chunk)
    except requests.RequestException as exc:
        raise RuntimeError(
            "No se pudo descargar el modelo de MediaPipe Hands. "
            f"Descargalo manualmente desde {HAND_LANDMARKER_MODEL_URL} "
            f"y guardalo como {path}."
        ) from exc

    return str(path)


class TasksHandsAdapter:
    """Small compatibility wrapper for MediaPipe versions without mp.solutions."""

    def __init__(
        self,
        *,
        static_image_mode: bool,
        max_num_hands: int,
        min_detection_confidence: float,
        min_tracking_confidence: float,
    ) -> None:
        import mediapipe as mp
        from mediapipe.tasks.python.core.base_options import BaseOptions
        from mediapipe.tasks.python.vision.core.vision_task_running_mode import VisionTaskRunningMode
        from mediapipe.tasks.python.vision.hand_landmarker import (
            HandLandmarker,
            HandLandmarkerOptions,
        )

        model_path = ensure_hand_landmarker_model()
        running_mode = VisionTaskRunningMode.IMAGE if static_image_mode else VisionTaskRunningMode.VIDEO
        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=running_mode,
            num_hands=max_num_hands,
            min_hand_detection_confidence=min_detection_confidence,
            min_hand_presence_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self._mp = mp
        self._landmarker = HandLandmarker.create_from_options(options)
        self._static_image_mode = static_image_mode
        self._last_timestamp_ms = 0

    def __enter__(self) -> "TasksHandsAdapter":
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        self.close()

    def close(self) -> None:
        self._landmarker.close()

    def process(self, image_rgb: np.ndarray) -> Any:
        image = self._mp.Image(
            image_format=self._mp.ImageFormat.SRGB,
            data=np.ascontiguousarray(image_rgb),
        )
        if self._static_image_mode:
            return self._landmarker.detect(image)

        timestamp_ms = int(time.monotonic() * 1000)
        if timestamp_ms <= self._last_timestamp_ms:
            timestamp_ms = self._last_timestamp_ms + 1
        self._last_timestamp_ms = timestamp_ms
        return self._landmarker.detect_for_video(image, timestamp_ms)


def create_hands(
    *,
    static_image_mode: bool,
    max_num_hands: int = 1,
    min_detection_confidence: float = 0.6,
    min_tracking_confidence: float = 0.6,
) -> Any:
    hands_module = _mp_hands_module()
    if hands_module is None:
        return TasksHandsAdapter(
            static_image_mode=static_image_mode,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

    return hands_module.Hands(
        static_image_mode=static_image_mode,
        max_num_hands=max_num_hands,
        min_detection_confidence=min_detection_confidence,
        min_tracking_confidence=min_tracking_confidence,
    )


def _coords_from_landmarks(hand_landmarks: Any) -> np.ndarray:
    landmarks = hand_landmarks.landmark if hasattr(hand_landmarks, "landmark") else hand_landmarks
    return np.array([[lm.x, lm.y, lm.z] for lm in landmarks], dtype=np.float32)


def _handedness_from_result(result: Any, index: int) -> tuple[str, float]:
    if hasattr(result, "multi_handedness") and result.multi_handedness:
        if index < len(result.multi_handedness):
            classification = result.multi_handedness[index].classification[0]
            return classification.label, float(classification.score)

    if hasattr(result, "handedness") and result.handedness:
        if index < len(result.handedness) and result.handedness[index]:
            category = result.handedness[index][0]
            label = getattr(category, "category_name", None) or getattr(category, "display_name", None)
            return str(label or "Unknown"), float(getattr(category, "score", 0.0))

    return "Unknown", 0.0


def _hand_landmark_sets(result: Any) -> list[Any]:
    if hasattr(result, "multi_hand_landmarks"):
        return list(result.multi_hand_landmarks or [])
    if hasattr(result, "hand_landmarks"):
        return list(result.hand_landmarks or [])
    return []


def _angle_degrees(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    ba = a - b
    bc = c - b
    denom = np.linalg.norm(ba) * np.linalg.norm(bc)
    if denom <= 1e-8:
        return 0.0
    cosine = float(np.clip(np.dot(ba, bc) / denom, -1.0, 1.0))
    return float(np.degrees(np.arccos(cosine)) / 180.0)


def normalize_landmarks(
    landmarks: np.ndarray,
    *,
    handedness: str = "Unknown",
    mirror_left: bool = True,
) -> np.ndarray:
    coords = np.asarray(landmarks, dtype=np.float32).reshape(21, 3).copy()
    coords -= coords[0]

    scale = float(np.percentile(np.linalg.norm(coords[:, :2], axis=1), 95))
    if scale <= 1e-6:
        scale = float(np.max(np.linalg.norm(coords, axis=1)))
    if scale <= 1e-6:
        scale = 1.0

    coords /= scale

    if mirror_left and handedness.lower() == "left":
        coords[:, 0] *= -1.0

    return coords


def build_feature_vector(
    landmarks: np.ndarray,
    *,
    handedness: str = "Unknown",
    mirror_left: bool = True,
) -> tuple[np.ndarray, np.ndarray]:
    normalized = normalize_landmarks(landmarks, handedness=handedness, mirror_left=mirror_left)

    flat = normalized.reshape(-1)
    wrist_distances = np.array(
        [np.linalg.norm(normalized[idx] - normalized[0]) for idx in WRIST_DISTANCE_INDICES],
        dtype=np.float32,
    )
    tip_distances = np.array(
        [np.linalg.norm(normalized[a] - normalized[b]) for a, b in TIP_PAIR_INDICES],
        dtype=np.float32,
    )
    angles = np.array(
        [
            _angle_degrees(normalized[chain[i - 1]], normalized[chain[i]], normalized[chain[i + 1]])
            for chain in FINGER_CHAINS
            for i in range(1, len(chain) - 1)
        ],
        dtype=np.float32,
    )

    features = np.concatenate([flat, wrist_distances, tip_distances, angles]).astype(np.float32)
    return features, normalized


def extract_landmark_result(
    image_rgb: np.ndarray,
    hands: Any,
    *,
    mirror_left: bool = True,
) -> LandmarkResult | None:
    result = hands.process(image_rgb)
    hand_sets = _hand_landmark_sets(result)
    if not hand_sets:
        return None

    best_index = 0
    best_score = -1.0
    for idx, hand_landmarks in enumerate(hand_sets):
        coords = _coords_from_landmarks(hand_landmarks)
        bbox = coords[:, :2]
        area = float(np.prod(np.maximum(bbox.max(axis=0) - bbox.min(axis=0), 1e-6)))
        _, handedness_score = _handedness_from_result(result, idx)
        score = area * max(handedness_score, 0.1)
        if score > best_score:
            best_index = idx
            best_score = score

    hand_landmarks = hand_sets[best_index]
    image_landmarks = _coords_from_landmarks(hand_landmarks)
    handedness, score = _handedness_from_result(result, best_index)

    features, normalized = build_feature_vector(
        image_landmarks,
        handedness=handedness,
        mirror_left=mirror_left,
    )

    return LandmarkResult(
        feature_vector=features,
        image_landmarks=image_landmarks,
        normalized_landmarks=normalized,
        handedness=handedness,
        score=score,
    )
