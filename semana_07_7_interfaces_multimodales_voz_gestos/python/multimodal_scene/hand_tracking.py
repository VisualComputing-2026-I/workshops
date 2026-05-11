from __future__ import annotations

import time
from pathlib import Path
from typing import Sequence

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.core.base_options import BaseOptions

from .state import HandObservation


class HandTracker:
    def __init__(self, model_path: str | Path) -> None:
        self._model_path = Path(model_path)
        if not self._model_path.is_file():
            raise RuntimeError(
                f"No se encontro el modelo de manos en '{self._model_path}'. "
                "Descarga hand_landmarker.task y colocalo en esa ruta."
            )

        options = vision.HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=str(self._model_path)),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=0.35,
            min_hand_presence_confidence=0.35,
            min_tracking_confidence=0.35,
        )
        self._landmarker = vision.HandLandmarker.create_from_options(options)
        self._drawer = vision.drawing_utils
        self._styles = vision.drawing_styles
        self._connections = vision.HandLandmarksConnections.HAND_CONNECTIONS

    def close(self) -> None:
        self._landmarker.close()

    def process(self, frame: np.ndarray) -> tuple[HandObservation, np.ndarray]:
        annotated = frame.copy()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        timestamp_ms = int(time.monotonic() * 1000)
        result = self._landmarker.detect_for_video(mp_image, timestamp_ms)

        if not result.hand_landmarks:
            cv2.putText(
                annotated,
                "Sin mano detectada",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 190, 255),
                2,
                cv2.LINE_AA,
            )
            return HandObservation(), annotated

        hand_landmarks = result.hand_landmarks[0]
        self._drawer.draw_landmarks(
            annotated,
            hand_landmarks,
            self._connections,
            self._styles.get_default_hand_landmarks_style(),
            self._styles.get_default_hand_connections_style(),
        )

        coords = [(lm.x, lm.y) for lm in hand_landmarks]
        finger_states = self._finger_states(coords)
        extended_count = sum(
            (
                finger_states["index"],
                finger_states["middle"],
                finger_states["ring"],
                finger_states["pinky"],
            )
        )
        hand_open = extended_count >= 3
        two_fingers = (
            finger_states["index"]
            and finger_states["middle"]
            and not finger_states["ring"]
            and not finger_states["pinky"]
        )

        if hand_open:
            gesture_name = "Mano abierta"
            pointer = self._average_point(coords)
        elif two_fingers:
            gesture_name = "Dos dedos"
            pointer = coords[8]
        elif not any(finger_states.values()):
            gesture_name = "Mano cerrada"
            pointer = self._average_point(coords)
        else:
            gesture_name = "Gesto mixto"
            pointer = self._average_point(coords)

        cv2.putText(
            annotated,
            f"{gesture_name} | dedos {extended_count}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (30, 240, 180),
            2,
            cv2.LINE_AA,
        )

        return (
            HandObservation(
                hand_present=True,
                hand_open=hand_open,
                two_fingers=two_fingers,
                gesture_name=gesture_name,
                pointer=pointer,
            ),
            annotated,
        )

    def _finger_states(self, coords: Sequence[tuple[float, float]]) -> dict[str, bool]:
        return {
            "thumb": abs(coords[4][0] - coords[2][0]) > 0.04,
            "index": coords[8][1] < coords[6][1],
            "middle": coords[12][1] < coords[10][1],
            "ring": coords[16][1] < coords[14][1],
            "pinky": coords[20][1] < coords[18][1],
        }

    def _average_point(self, coords: Sequence[tuple[float, float]]) -> tuple[float, float]:
        points = np.array(coords, dtype=np.float32)
        avg = points.mean(axis=0)
        return float(avg[0]), float(avg[1])
