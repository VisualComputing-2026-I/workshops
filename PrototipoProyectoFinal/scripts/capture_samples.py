from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

import cv2

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lsc_alphabet.config import RAW_DATA_DIR
from lsc_alphabet.labels import display_label, label_options_for_cli, normalize_label
from lsc_alphabet.landmarks import create_hands, extract_landmark_result
from lsc_alphabet.visualization import draw_landmarks


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Captura imagenes etiquetadas desde webcam.")
    parser.add_argument("--label", required=True, help=f"Letra a capturar: {label_options_for_cli()}")
    parser.add_argument("--samples", type=int, default=250, help="Cantidad objetivo de imagenes.")
    parser.add_argument("--camera", type=int, default=0, help="Indice de camara OpenCV.")
    parser.add_argument("--output-dir", type=Path, default=RAW_DATA_DIR, help="Carpeta base de salida.")
    parser.add_argument("--interval", type=int, default=3, help="Guardar 1 de cada N frames en modo automatico.")
    parser.add_argument("--min-confidence", type=float, default=0.65, help="Confianza minima de MediaPipe.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    label = normalize_label(args.label)
    output_dir = args.output_dir / label
    output_dir.mkdir(parents=True, exist_ok=True)

    capture = cv2.VideoCapture(args.camera)
    if not capture.isOpened():
        raise RuntimeError(f"No se pudo abrir la camara {args.camera}.")

    saved = len(list(output_dir.glob("*.jpg")))
    auto_capture = False
    frame_index = 0
    window_name = f"Captura LSC - {display_label(label)}"

    with create_hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=args.min_confidence,
        min_tracking_confidence=0.65,
    ) as hands:
        while saved < args.samples:
            ok, frame = capture.read()
            if not ok:
                break

            frame = cv2.flip(frame, 1)
            clean_frame = frame.copy()
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = extract_landmark_result(image_rgb, hands)
            has_hand = result is not None
            draw_landmarks(frame, result)

            status = "AUTO" if auto_capture else "PAUSA"
            color = (40, 220, 120) if has_hand else (40, 160, 255)
            cv2.putText(
                frame,
                f"{display_label(label)}  {saved}/{args.samples}  {status}",
                (18, 38),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                color,
                2,
                cv2.LINE_AA,
            )
            cv2.putText(
                frame,
                "Espacio: auto | C: captura | Q: salir",
                (18, frame.shape[0] - 18),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.58,
                (230, 230, 230),
                1,
                cv2.LINE_AA,
            )

            should_save = False
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord(" "):
                auto_capture = not auto_capture
            if key == ord("c"):
                should_save = has_hand
            if auto_capture and has_hand and frame_index % max(args.interval, 1) == 0:
                should_save = True

            if should_save:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                path = output_dir / f"{label}_{timestamp}.jpg"
                cv2.imwrite(str(path), clean_frame)
                saved += 1

            cv2.imshow(window_name, frame)
            frame_index += 1

    capture.release()
    cv2.destroyAllWindows()
    print(f"Capturas guardadas en {output_dir}: {saved}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        raise SystemExit(f"Error: {exc}") from None
