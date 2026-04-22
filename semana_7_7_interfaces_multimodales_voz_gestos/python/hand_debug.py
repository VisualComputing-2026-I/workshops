from __future__ import annotations

import argparse
from pathlib import Path

import cv2

from multimodal_scene.hand_tracking import HandTracker


def open_capture(source_value: str) -> cv2.VideoCapture:
    source = int(source_value) if source_value.strip().isdigit() else source_value.strip()
    if isinstance(source, int):
        capture = cv2.VideoCapture(source, cv2.CAP_DSHOW)
        if not capture.isOpened():
            capture.release()
            capture = cv2.VideoCapture(source)
    else:
        capture = cv2.VideoCapture(source)
    return capture


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnostico minimo de MediaPipe Hands.")
    parser.add_argument("--camera-source", default="0", help="Indice o URL de camara.")
    parser.add_argument(
        "--hand-model-path",
        default=str(Path("models") / "hand_landmarker.task"),
        help="Ruta al modelo hand_landmarker.task.",
    )
    parser.add_argument("--no-mirror-camera", action="store_true")
    args = parser.parse_args()

    capture = open_capture(args.camera_source)
    if not capture.isOpened():
        print("No se pudo abrir la camara.")
        return 1

    tracker = HandTracker(args.hand_model_path)
    frame_count = 0

    print("Vista de diagnostico iniciada. ESC para salir.")
    print("Si siempre ves 'Sin mano detectada', el problema esta en MediaPipe/camara, no en pygame o voz.")

    try:
        while True:
            ok, frame = capture.read()
            if not ok or frame is None:
                print("No se recibieron fotogramas.")
                break

            if not args.no_mirror_camera:
                frame = cv2.flip(frame, 1)

            hand, annotated = tracker.process(frame)
            frame_count += 1

            cv2.putText(
                annotated,
                "ESC salir",
                (10, annotated.shape[0] - 12),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            if hand.hand_present:
                cv2.circle(
                    annotated,
                    (int(hand.pointer[0] * annotated.shape[1]), int(hand.pointer[1] * annotated.shape[0])),
                    10,
                    (255, 255, 0),
                    -1,
                )

            if frame_count % 30 == 0:
                print(
                    f"frame={frame_count} hand_present={hand.hand_present} "
                    f"gesture='{hand.gesture_name}' open={hand.hand_open} two_fingers={hand.two_fingers}"
                )

            cv2.imshow("Hand Debug", annotated)
            if cv2.waitKey(1) & 0xFF == 27:
                break
    finally:
        capture.release()
        tracker.close()
        cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
