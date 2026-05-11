from __future__ import annotations

import argparse
import time

import cv2


def open_capture(index: int) -> cv2.VideoCapture:
    capture = cv2.VideoCapture(index, cv2.CAP_DSHOW)
    if not capture.isOpened():
        capture.release()
        capture = cv2.VideoCapture(index)
    return capture


def probe_index(index: int, warmup_frames: int) -> tuple[bool, bool, tuple[int, int] | None]:
    capture = open_capture(index)
    if not capture.isOpened():
        capture.release()
        return False, False, None

    ok = False
    frame = None
    for _ in range(warmup_frames):
        ok, frame = capture.read()
        if ok and frame is not None:
            break
        time.sleep(0.05)

    resolution = None
    if ok and frame is not None:
        resolution = (int(frame.shape[1]), int(frame.shape[0]))

    capture.release()
    return True, ok, resolution


def preview_index(index: int) -> int:
    capture = open_capture(index)
    if not capture.isOpened():
        print(f"[{index}] no se pudo abrir")
        return 1

    print(f"[{index}] mostrando vista previa. ESC para salir.")
    while True:
        ok, frame = capture.read()
        if not ok or frame is None:
            print(f"[{index}] sin fotogramas")
            break

        frame = cv2.flip(frame, 1)
        cv2.putText(
            frame,
            f"Camera source {index}",
            (20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2,
            cv2.LINE_AA,
        )
        cv2.imshow("Camera Probe", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    capture.release()
    cv2.destroyAllWindows()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Detecta indices de camara disponibles para OpenCV.")
    parser.add_argument("--max-index", type=int, default=10, help="Indice maximo a probar.")
    parser.add_argument(
        "--preview",
        type=int,
        default=None,
        help="Abre una vista previa del indice indicado.",
    )
    parser.add_argument(
        "--warmup-frames",
        type=int,
        default=15,
        help="Cantidad de intentos de lectura por indice.",
    )
    args = parser.parse_args()

    if args.preview is not None:
        return preview_index(args.preview)

    print("Buscando camaras visibles para OpenCV...\n")
    found_any = False
    for index in range(args.max_index + 1):
        opened, has_frames, resolution = probe_index(index, args.warmup_frames)
        if not opened:
            print(f"[{index}] no abre")
            continue

        found_any = True
        if has_frames and resolution is not None:
            print(f"[{index}] abre y entrega video {resolution[0]}x{resolution[1]}")
        else:
            print(f"[{index}] abre pero no entrega video")

    if not found_any:
        print("\nNo se detecto ninguna camara. Revisa que DroidCam Client este conectado.")
        return 1

    print("\nUsa el indice que diga 'abre y entrega video' con app.py.")
    print("Ejemplo: python app.py --camera-source 1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
