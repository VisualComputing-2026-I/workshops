from __future__ import annotations

import argparse
from collections import deque
import sys
from pathlib import Path

import cv2

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lsc_alphabet.config import DEFAULT_MODEL_PATH
from lsc_alphabet.landmarks import create_hands, extract_landmark_result
from lsc_alphabet.predictor import GesturePredictor
from lsc_alphabet.sequences import build_sequence_feature_vector
from lsc_alphabet.stabilizer import PredictionStabilizer
from lsc_alphabet.visualization import draw_landmarks, draw_overlay


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Demo de reconocimiento LSC con OpenCV.")
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL_PATH, help="Modelo .joblib entrenado.")
    parser.add_argument("--camera", type=int, default=0, help="Indice de camara OpenCV.")
    parser.add_argument("--confidence", type=float, default=0.75, help="Confianza minima para escribir.")
    parser.add_argument("--stable-frames", type=int, default=8, help="Frames consecutivos para confirmar.")
    parser.add_argument("--no-mirror", action="store_true", help="No espejar la camara.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.model.exists():
        raise FileNotFoundError(f"No existe el modelo: {args.model}")

    predictor = GesturePredictor.from_file(args.model)
    stabilizer = PredictionStabilizer(
        stable_frames=args.stable_frames,
        confidence_threshold=args.confidence,
    )
    sequence_length = int(predictor.sequence_length or 6)
    sequence_buffer: deque = deque(maxlen=sequence_length)

    capture = cv2.VideoCapture(args.camera)
    if not capture.isOpened():
        raise RuntimeError(f"No se pudo abrir la camara {args.camera}.")

    with create_hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.65,
        min_tracking_confidence=0.65,
    ) as hands:
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            if not args.no_mirror:
                frame = cv2.flip(frame, 1)

            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            landmark_result = extract_landmark_result(image_rgb, hands)
            prediction = None
            if landmark_result is not None:
                if predictor.model_type == "sequence":
                    sequence_buffer.append(landmark_result.feature_vector)
                    if len(sequence_buffer) == sequence_length:
                        sequence_features = build_sequence_feature_vector(list(sequence_buffer))
                        prediction = predictor.predict_features(sequence_features)
                else:
                    prediction = predictor.predict_features(landmark_result.feature_vector)
            stabilizer.update_from_prediction(prediction)

            draw_landmarks(frame, landmark_result)
            draw_overlay(
                frame,
                prediction,
                text=stabilizer.text,
                status="Q salir | Espacio espacio | B borrar | C limpiar",
            )
            cv2.imshow("Traductor LSC", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord(" "):
                stabilizer.space()
            if key == ord("b") or key == 8:
                stabilizer.delete()
            if key == ord("c"):
                stabilizer.clear()
                sequence_buffer.clear()

    capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        raise SystemExit(f"Error: {exc}") from None
