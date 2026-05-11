import argparse
import math
import queue
import shutil
import time
import unicodedata
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import cv2
import mediapipe as mp
import numpy as np
import speech_recognition as sr


HAND_LANDMARKER_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
)


def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text.lower())
    return "".join(char for char in normalized if unicodedata.category(char) != "Mn")


def distance_px(a: tuple[int, int], b: tuple[int, int]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def landmark_to_point(landmark, width: int, height: int) -> tuple[int, int]:
    x = min(max(int(landmark.x * width), 0), width - 1)
    y = min(max(int(landmark.y * height), 0), height - 1)
    return x, y


def finger_up(landmarks, tip_index: int, pip_index: int) -> bool:
    return landmarks[tip_index].y < landmarks[pip_index].y


def detect_gesture(landmarks, width: int, height: int) -> str:
    index_up = finger_up(landmarks, 8, 6)
    middle_up = finger_up(landmarks, 12, 10)
    ring_up = finger_up(landmarks, 16, 14)
    pinky_up = finger_up(landmarks, 20, 18)

    thumb_tip = landmark_to_point(landmarks[4], width, height)
    index_tip = landmark_to_point(landmarks[8], width, height)
    pinch = distance_px(thumb_tip, index_tip) < max(width, height) * 0.04

    raised_fingers = sum([index_up, middle_up, ring_up, pinky_up])

    if raised_fingers >= 4:
        return "palma_abierta"
    if pinch:
        return "pinza"
    if raised_fingers == 0:
        return "punio"
    if index_up and not middle_up and not ring_up and not pinky_up:
        return "indice"
    if index_up and middle_up and not ring_up and not pinky_up:
        return "hover"
    return "neutro"


def ensure_hand_landmarker_model(model_path: Path) -> Path:
    if model_path.exists():
        return model_path

    model_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = model_path.with_suffix(".tmp")

    try:
        with urllib.request.urlopen(HAND_LANDMARKER_MODEL_URL, timeout=30) as response:
            with tmp_path.open("wb") as output_file:
                shutil.copyfileobj(response, output_file)
        tmp_path.replace(model_path)
        return model_path
    except Exception as exc:
        if tmp_path.exists():
            tmp_path.unlink()
        raise RuntimeError(
            "No se pudo descargar el modelo oficial de MediaPipe Hand Landmarker. "
            f"Descargalo manualmente desde {HAND_LANDMARKER_MODEL_URL} y guardalo en {model_path}. "
            f"Detalle: {exc}"
        ) from exc


def create_hand_landmarker(model_path: Path):
    base_options = mp.tasks.BaseOptions(model_asset_path=str(model_path))
    options = mp.tasks.vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=mp.tasks.vision.RunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=0.6,
        min_hand_presence_confidence=0.6,
        min_tracking_confidence=0.6,
    )
    return mp.tasks.vision.HandLandmarker.create_from_options(options)


def draw_hand_landmarks(frame: np.ndarray, hand_landmarks) -> None:
    height, width = frame.shape[:2]
    points = [landmark_to_point(landmark, width, height) for landmark in hand_landmarks]

    for connection in mp.tasks.vision.HandLandmarksConnections.HAND_CONNECTIONS:
        start = points[connection.start]
        end = points[connection.end]
        cv2.line(frame, start, end, (80, 220, 120), 2)

    for index, point in enumerate(points):
        radius = 6 if index in (4, 8, 12, 16, 20) else 4
        cv2.circle(frame, point, radius, (255, 255, 255), -1)
        cv2.circle(frame, point, radius + 1, (30, 30, 30), 1)


@dataclass
class UiMessage:
    text: str = ""
    expires_at: float = 0.0


class VoiceCommandListener:
    def __init__(self, command_queue: "queue.Queue[tuple[str, str]]", language: str) -> None:
        self.command_queue = command_queue
        self.language = language
        self.recognizer = sr.Recognizer()
        self.stop_callback = None
        self.microphone: Optional[sr.Microphone] = None
        self.available = False
        self.startup_error: Optional[str] = None

        try:
            self.microphone = sr.Microphone()
            self.available = True
        except Exception as exc:
            self.startup_error = f"No se pudo iniciar el microfono: {exc}"

    def start(self) -> Optional[str]:
        if not self.available or self.microphone is None:
            return self.startup_error

        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)

            self.stop_callback = self.recognizer.listen_in_background(
                self.microphone,
                self._on_audio,
                phrase_time_limit=2.5,
            )
            return None
        except Exception as exc:
            return f"No se pudo activar el reconocimiento de voz: {exc}"

    def stop(self) -> None:
        if self.stop_callback is not None:
            self.stop_callback(wait_for_stop=False)
            self.stop_callback = None

    def _on_audio(self, recognizer: sr.Recognizer, audio: sr.AudioData) -> None:
        try:
            spoken_text = recognizer.recognize_google(audio, language=self.language)
            self.command_queue.put(("command", spoken_text))
        except sr.UnknownValueError:
            pass
        except sr.RequestError as exc:
            self.command_queue.put(("error", f"Servicio de voz no disponible: {exc}"))
        except Exception as exc:
            self.command_queue.put(("error", f"Error de voz: {exc}"))


class PainterState:
    COLORS = {
        "rojo": (0, 0, 255),
        "verde": (0, 200, 0),
        "azul": (255, 120, 0),
        "amarillo": (0, 215, 255),
        "blanco": (255, 255, 255),
        "negro": (0, 0, 0),
    }
    BRUSHES = ["circulo", "cuadrado", "spray"]

    def __init__(self, save_dir: Path) -> None:
        self.save_dir = save_dir
        self.current_color_name = "rojo"
        self.current_color = self.COLORS[self.current_color_name]
        self.brush_name = "circulo"
        self.brush_size = 10
        self.eraser_size = 36
        self.last_point: Optional[tuple[int, int]] = None
        self.last_gesture: Optional[str] = None
        self.last_voice_text = "Sin comandos de voz todavia"
        self.voice_status = "Inicializando microfono..."
        self.save_requested = False
        self.ui_message = UiMessage()

    def show_message(self, text: str, duration: float = 2.8) -> None:
        self.ui_message = UiMessage(text=text, expires_at=time.time() + duration)

    def active_message(self) -> str:
        if time.time() <= self.ui_message.expires_at:
            return self.ui_message.text
        return ""

    def set_color(self, color_name: str, origin: str) -> None:
        self.current_color_name = color_name
        self.current_color = self.COLORS[color_name]
        self.show_message(f"{origin}: color {color_name}")

    def set_brush(self, brush_name: str, origin: str) -> None:
        self.brush_name = brush_name
        self.show_message(f"{origin}: pincel {brush_name}")

    def cycle_brush(self, origin: str) -> None:
        index = self.BRUSHES.index(self.brush_name)
        next_brush = self.BRUSHES[(index + 1) % len(self.BRUSHES)]
        self.set_brush(next_brush, origin)

    def clear_canvas(self, paint_layer: np.ndarray, paint_mask: np.ndarray, origin: str) -> None:
        paint_layer[:] = 0
        paint_mask[:] = 0
        self.last_point = None
        self.show_message(f"{origin}: lienzo limpiado")

    def request_save(self) -> None:
        self.save_requested = True
        self.show_message("Guardando imagen...", duration=1.5)

    def handle_voice_command(self, spoken_text: str, paint_layer: np.ndarray, paint_mask: np.ndarray) -> None:
        normalized = normalize_text(spoken_text)
        self.last_voice_text = spoken_text

        for color_name in self.COLORS:
            if color_name in normalized:
                self.set_color(color_name, "Voz")
                return

        if "pincel" in normalized:
            self.cycle_brush("Voz")
            return
        if "limpiar" in normalized or "borrar" in normalized:
            self.clear_canvas(paint_layer, paint_mask, "Voz")
            return
        if "guardar" in normalized:
            self.request_save()
            return

        self.show_message(f"Comando no reconocido: {spoken_text}")


def draw_brush_stamp(
    paint_layer: np.ndarray,
    paint_mask: np.ndarray,
    point: tuple[int, int],
    color: tuple[int, int, int],
    brush_name: str,
    size: int,
    erase: bool = False,
) -> None:
    if erase:
        cv2.circle(paint_layer, point, size, (0, 0, 0), thickness=-1)
        cv2.circle(paint_mask, point, size, 0, thickness=-1)
        return

    if brush_name == "circulo":
        cv2.circle(paint_layer, point, size, color, thickness=-1)
        cv2.circle(paint_mask, point, size, 255, thickness=-1)
        return

    if brush_name == "cuadrado":
        x0 = max(point[0] - size, 0)
        y0 = max(point[1] - size, 0)
        x1 = min(point[0] + size, paint_layer.shape[1] - 1)
        y1 = min(point[1] + size, paint_layer.shape[0] - 1)
        cv2.rectangle(paint_layer, (x0, y0), (x1, y1), color, thickness=-1)
        cv2.rectangle(paint_mask, (x0, y0), (x1, y1), 255, thickness=-1)
        return

    spray_points = max(12, size * 3)
    for _ in range(spray_points):
        angle = np.random.uniform(0, 2 * np.pi)
        radius = np.random.uniform(0, size)
        x = int(point[0] + math.cos(angle) * radius)
        y = int(point[1] + math.sin(angle) * radius)
        if 0 <= x < paint_layer.shape[1] and 0 <= y < paint_layer.shape[0]:
            paint_layer[y, x] = color
            paint_mask[y, x] = 255


def paint_segment(
    paint_layer: np.ndarray,
    paint_mask: np.ndarray,
    start: tuple[int, int],
    end: tuple[int, int],
    color: tuple[int, int, int],
    brush_name: str,
    size: int,
    erase: bool = False,
) -> None:
    steps = max(abs(end[0] - start[0]), abs(end[1] - start[1]), 1)
    for step in range(steps + 1):
        ratio = step / steps
        x = int(start[0] + (end[0] - start[0]) * ratio)
        y = int(start[1] + (end[1] - start[1]) * ratio)
        draw_brush_stamp(paint_layer, paint_mask, (x, y), color, brush_name, size, erase=erase)


def compose_frame(frame: np.ndarray, paint_layer: np.ndarray, paint_mask: np.ndarray) -> np.ndarray:
    mixed = cv2.addWeighted(frame, 0.35, paint_layer, 0.85, 0)
    output = frame.copy()
    painted_pixels = paint_mask > 0
    output[painted_pixels] = mixed[painted_pixels]
    return output


def save_artwork(
    state: PainterState,
    display_frame: np.ndarray,
    paint_layer: np.ndarray,
    paint_mask: np.ndarray,
) -> tuple[Path, Path]:
    state.save_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    overlay_path = state.save_dir / f"obra_overlay_{timestamp}.png"
    canvas_path = state.save_dir / f"obra_lienzo_{timestamp}.png"

    white_canvas = np.full_like(paint_layer, 255)
    painted_pixels = paint_mask > 0
    white_canvas[painted_pixels] = paint_layer[painted_pixels]

    cv2.imwrite(str(overlay_path), display_frame)
    cv2.imwrite(str(canvas_path), white_canvas)
    return overlay_path, canvas_path


def draw_cursor(frame: np.ndarray, point: tuple[int, int], state: PainterState, erasing: bool) -> None:
    if erasing:
        cv2.circle(frame, point, state.eraser_size, (200, 200, 200), 2)
        cv2.putText(frame, "Borrador", (point[0] + 15, point[1] - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (220, 220, 220), 2)
        return

    if state.brush_name == "circulo":
        cv2.circle(frame, point, state.brush_size, state.current_color, 2)
    elif state.brush_name == "cuadrado":
        cv2.rectangle(
            frame,
            (point[0] - state.brush_size, point[1] - state.brush_size),
            (point[0] + state.brush_size, point[1] + state.brush_size),
            state.current_color,
            2,
        )
    else:
        cv2.circle(frame, point, state.brush_size, state.current_color, 1)
        cv2.circle(frame, point, max(2, state.brush_size // 3), state.current_color, -1)


def draw_hud(frame: np.ndarray, state: PainterState, gesture: str) -> None:
    cv2.rectangle(frame, (10, 10), (530, 148), (20, 20, 20), thickness=-1)
    cv2.putText(frame, "Pintura interactiva por voz y gestos", (24, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
    cv2.putText(
        frame,
        f"Color: {state.current_color_name} | Pincel: {state.brush_name} | Gesto: {gesture}",
        (24, 68),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.58,
        (240, 240, 240),
        2,
    )
    cv2.putText(
        frame,
        f"Voz: {state.last_voice_text[:56]}",
        (24, 96),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (180, 255, 180),
        1,
    )
    cv2.putText(
        frame,
        f"Microfono: {state.voice_status[:58]}",
        (24, 121),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (190, 220, 255),
        1,
    )

    message = state.active_message()
    if message:
        cv2.rectangle(frame, (10, frame.shape[0] - 56), (620, frame.shape[0] - 16), (0, 0, 0), thickness=-1)
        cv2.putText(frame, message, (22, frame.shape[0] - 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    help_text = "Teclas: Q salir | C limpiar | S guardar | B pincel"
    cv2.putText(frame, help_text, (18, frame.shape[0] - 70), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (240, 240, 240), 1)


def open_camera(camera_source: int) -> cv2.VideoCapture:
    cap = cv2.VideoCapture(camera_source, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap.release()
        cap = cv2.VideoCapture(camera_source)
    return cap


def main() -> None:
    parser = argparse.ArgumentParser(description="Pintura interactiva con mano y voz.")
    parser.add_argument("--camera-source", type=int, default=0, help="Indice de la camara a usar. DroidCam suele funcionar en 0.")
    parser.add_argument("--width", type=int, default=1280, help="Ancho deseado de captura.")
    parser.add_argument("--height", type=int, default=720, help="Alto deseado de captura.")
    parser.add_argument("--voice-language", default="es-CO", help="Idioma para speech_recognition. Ejemplo: es-CO o es-ES.")
    parser.add_argument("--model-path", default="models/hand_landmarker.task", help="Ruta local del modelo .task de MediaPipe.")
    args = parser.parse_args()

    command_queue: "queue.Queue[tuple[str, str]]" = queue.Queue()
    voice_listener = VoiceCommandListener(command_queue, language=args.voice_language)
    state = PainterState(save_dir=Path("outputs"))

    microphone_error = voice_listener.start()
    if microphone_error:
        state.voice_status = "No disponible"
        state.show_message(microphone_error, duration=5.0)
    else:
        state.voice_status = f"Escuchando ({args.voice_language})"
        state.show_message("Microfono listo. Di: rojo, verde, pincel, limpiar o guardar.")

    cap = open_camera(args.camera_source)
    if not cap.isOpened():
        voice_listener.stop()
        raise SystemExit(
            f"No se pudo abrir la camara en source {args.camera_source}. "
            "Verifica DroidCam, permisos de camara y que el indice sea correcto."
        )

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)

    ok, frame = cap.read()
    if not ok:
        cap.release()
        voice_listener.stop()
        raise SystemExit("La camara se abrio, pero no entrega frames.")

    frame = cv2.flip(frame, 1)
    height, width = frame.shape[:2]
    paint_layer = np.zeros((height, width, 3), dtype=np.uint8)
    paint_mask = np.zeros((height, width), dtype=np.uint8)

    model_path = ensure_hand_landmarker_model(Path(args.model_path))
    hand_landmarker = create_hand_landmarker(model_path)

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                state.show_message("No se pudo leer el frame de la camara.", duration=2.0)
                continue

            frame = cv2.flip(frame, 1)

            while not command_queue.empty():
                event_type, payload = command_queue.get()
                if event_type == "command":
                    state.handle_voice_command(payload, paint_layer, paint_mask)
                else:
                    state.voice_status = "Error en servicio"
                    state.show_message(payload, duration=4.0)

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            frame_timestamp_ms = int(time.perf_counter() * 1000)
            results = hand_landmarker.detect_for_video(mp_image, frame_timestamp_ms)

            gesture = "sin mano"
            index_point: Optional[tuple[int, int]] = None
            erasing = False

            if results.hand_landmarks:
                landmarks = results.hand_landmarks[0]
                gesture = detect_gesture(landmarks, width, height)
                index_point = landmark_to_point(landmarks[8], width, height)

                draw_hand_landmarks(frame, landmarks)

                if gesture == "palma_abierta" and state.last_gesture != "palma_abierta":
                    state.cycle_brush("Gesto palma abierta")
                    state.last_point = None
                elif gesture == "pinza" and state.last_gesture != "pinza":
                    state.set_brush("spray", "Gesto pinza")
                    state.last_point = None
                elif gesture == "punio":
                    erasing = True
                    start_point = state.last_point or index_point
                    paint_segment(
                        paint_layer,
                        paint_mask,
                        start_point,
                        index_point,
                        state.current_color,
                        state.brush_name,
                        state.eraser_size,
                        erase=True,
                    )
                    state.last_point = index_point
                elif gesture == "indice":
                    start_point = state.last_point or index_point
                    paint_segment(
                        paint_layer,
                        paint_mask,
                        start_point,
                        index_point,
                        state.current_color,
                        state.brush_name,
                        state.brush_size,
                        erase=False,
                    )
                    state.last_point = index_point
                else:
                    state.last_point = None

                state.last_gesture = gesture
            else:
                state.last_point = None
                state.last_gesture = None

            display_frame = compose_frame(frame, paint_layer, paint_mask)

            if index_point is not None:
                draw_cursor(display_frame, index_point, state, erasing=erasing)

            if state.save_requested:
                overlay_path, canvas_path = save_artwork(state, display_frame, paint_layer, paint_mask)
                state.save_requested = False
                state.show_message(f"Guardado: {overlay_path.name} y {canvas_path.name}", duration=4.0)

            draw_hud(display_frame, state, gesture)
            cv2.imshow("Pintura interactiva", display_frame)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
            if key == ord("c"):
                state.clear_canvas(paint_layer, paint_mask, "Teclado")
            elif key == ord("s"):
                state.request_save()
            elif key == ord("b"):
                state.cycle_brush("Teclado")

    finally:
        voice_listener.stop()
        hand_landmarker.close()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
