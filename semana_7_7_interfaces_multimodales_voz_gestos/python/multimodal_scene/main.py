from __future__ import annotations

import argparse
import os
import queue
import time
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
import pygame

from .hand_tracking import HandTracker
from .osc_client import OscStateClient
from .scene import SceneRenderer
from .state import AppState, COLOR_ORDER, HandObservation, VoiceEvent
from .voice import VoiceListener


@dataclass(slots=True)
class AppConfig:
    camera_source: str
    hand_model_path: str
    window_width: int = 1280
    window_height: int = 720
    speech_language: str = "es-CO"
    enable_osc: bool = False
    osc_host: str = "127.0.0.1"
    osc_port: int = 9000
    mirror_camera: bool = True
    open_hand_grace_seconds: float = 1.6
    two_fingers_grace_seconds: float = 1.2


class MultimodalApp:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.state = AppState(object_position=(config.window_width / 2, config.window_height / 2))
        self.event_queue: "queue.Queue[VoiceEvent]" = queue.Queue()
        self.voice_listener = VoiceListener(self.event_queue, language=config.speech_language)
        self.renderer = SceneRenderer(config.window_width, config.window_height)
        self.osc_client = OscStateClient(config.enable_osc, config.osc_host, config.osc_port)
        self.last_hand = HandObservation()
        self.last_video_frame: np.ndarray | None = None
        self._last_osc_values: dict[str, object] = {}
        self._shutdown_done = False
        self.hand_tracker: HandTracker | None = None
        self._open_hand_seen_at = 0.0
        self._two_fingers_seen_at = 0.0

        try:
            self.hand_tracker = HandTracker(config.hand_model_path)
        except Exception as exc:
            self.state.status_message = f"MediaPipe no disponible: {exc}"
            self.state.status_level = "error"

        self.capture = self._open_capture(config.camera_source)
        if self.hand_tracker is None:
            pass
        elif self.capture is None or not self.capture.isOpened():
            self.state.status_message = "No se pudo abrir la camara. Revisa --camera-source."
            self.state.status_level = "error"
        else:
            self.state.status_message = "Camara lista. Esperando mano y voz."

    def run(self) -> int:
        self.voice_listener.start()
        running = True

        while running:
            dt = self.renderer.tick()
            running = self._handle_events()
            self._update_camera()
            self._consume_voice_events()
            self._apply_continuous_actions(dt)
            self._sync_osc()
            self.renderer.draw(self.state, self.last_hand, self.last_video_frame)

        return 0

    def shutdown(self) -> None:
        if self._shutdown_done:
            return
        self._shutdown_done = True
        self.voice_listener.stop()
        if self.capture is not None:
            self.capture.release()
        if self.hand_tracker is not None:
            self.hand_tracker.close()
        self.renderer.shutdown()

    def _handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_r:
                    self._reset_scene()
        return True

    def _update_camera(self) -> None:
        if self.hand_tracker is None:
            self.last_hand = HandObservation()
            self.last_video_frame = None
            return

        if self.capture is None or not self.capture.isOpened():
            self.last_hand = HandObservation()
            self.last_video_frame = None
            return

        ok, frame = self.capture.read()
        if not ok or frame is None:
            self.state.status_message = "Sin senal de camara."
            self.state.status_level = "warning"
            self.last_hand = HandObservation()
            self.last_video_frame = None
            return

        if self.config.mirror_camera:
            frame = cv2.flip(frame, 1)

        hand, annotated = self.hand_tracker.process(frame)
        self.last_hand = hand
        self.last_video_frame = annotated
        self.state.hand_present = hand.hand_present
        self.state.gesture_name = hand.gesture_name
        now = time.monotonic()
        if hand.hand_open:
            self._open_hand_seen_at = now
        if hand.two_fingers:
            self._two_fingers_seen_at = now

    def _consume_voice_events(self) -> None:
        while True:
            try:
                event = self.event_queue.get_nowait()
            except queue.Empty:
                break

            if event.event_type == "recognized":
                self.state.voice_phrase = event.transcript
                if event.keywords:
                    for keyword in event.keywords:
                        self._apply_command(keyword)
                else:
                    self.state.status_message = "Frase detectada sin comando util."
                    self.state.status_level = "warning"
            elif event.event_type == "status":
                self.state.status_message = event.message
                self.state.status_level = "info"
            elif event.event_type == "error":
                self.state.status_message = event.message
                self.state.status_level = "error"

    def _apply_command(self, keyword: str) -> None:
        self.state.last_command = keyword

        if keyword in COLOR_ORDER:
            if self._open_hand_is_active():
                self.state.color_name = keyword
                self.state.status_message = f"Color actualizado a {keyword}."
            else:
                self.state.status_message = f"Di '{keyword}' con mano abierta."
            return

        if keyword == "cambiar":
            if self._open_hand_is_active():
                index = COLOR_ORDER.index(self.state.color_name)
                self.state.color_name = COLOR_ORDER[(index + 1) % len(COLOR_ORDER)]
                self.state.status_message = f"Color cambiado a {self.state.color_name}."
            else:
                self.state.status_message = "El comando cambiar requiere mano abierta."
            return

        if keyword == "rotar":
            if self._open_hand_is_active():
                self.state.rotation_mode = not self.state.rotation_mode
                mode = "activada" if self.state.rotation_mode else "desactivada"
                self.state.status_message = f"Rotacion {mode}."
            else:
                self.state.status_message = "El comando rotar requiere mano abierta."
            return

        if keyword == "mover":
            if self._two_fingers_are_active():
                self.state.move_mode = not self.state.move_mode
                mode = "activado" if self.state.move_mode else "desactivado"
                self.state.status_message = f"Modo mover {mode}."
            else:
                self.state.status_message = "El comando mover requiere gesto de dos dedos."
            return

        if keyword == "mostrar":
            self.state.object_visible = True
            self.state.status_message = "Objeto visible."
            return

        if keyword == "ocultar":
            self.state.object_visible = False
            self.state.status_message = "Objeto oculto."
            return

        if keyword == "detener":
            self.state.move_mode = False
            self.state.rotation_mode = False
            self.state.status_message = "Movimiento y rotacion detenidos."

    def _apply_continuous_actions(self, dt: float) -> None:
        if self.state.rotation_mode and self.state.object_visible:
            self.state.object_angle = (self.state.object_angle + 95.0 * dt) % 360.0

        if self.state.move_mode and self.last_hand.hand_present and self.last_hand.two_fingers:
            target = self._pointer_to_screen(self.last_hand.pointer)
            current = np.array(self.state.object_position, dtype=np.float32)
            updated = current + (target - current) * min(1.0, dt * 8.0)
            self.state.object_position = (float(updated[0]), float(updated[1]))

    def _open_hand_is_active(self) -> bool:
        if self.last_hand.hand_open:
            return True
        return (time.monotonic() - self._open_hand_seen_at) <= self.config.open_hand_grace_seconds

    def _two_fingers_are_active(self) -> bool:
        if self.last_hand.two_fingers:
            return True
        return (time.monotonic() - self._two_fingers_seen_at) <= self.config.two_fingers_grace_seconds

    def _pointer_to_screen(self, pointer: tuple[float, float]) -> np.ndarray:
        x = np.clip(pointer[0], 0.0, 1.0) * self.config.window_width
        y = np.clip(pointer[1], 0.0, 1.0) * self.config.window_height
        return np.array((x, y), dtype=np.float32)

    def _reset_scene(self) -> None:
        self.state.color_name = "azul"
        self.state.object_visible = True
        self.state.rotation_mode = False
        self.state.move_mode = False
        self.state.object_angle = 0.0
        self.state.object_position = (self.config.window_width / 2, self.config.window_height / 2)
        self.state.status_message = "Escena reiniciada."
        self.state.last_command = "reiniciar"

    def _sync_osc(self) -> None:
        payloads = {
            "/gesture/name": self.state.gesture_name,
            "/gesture/hand_present": int(self.state.hand_present),
            "/object/color": self.state.color_name,
            "/object/visible": int(self.state.object_visible),
            "/object/rotation_mode": int(self.state.rotation_mode),
            "/object/move_mode": int(self.state.move_mode),
            "/object/angle": round(self.state.object_angle, 2),
            "/object/x": round(self.state.object_position[0], 2),
            "/object/y": round(self.state.object_position[1], 2),
            "/voice/last_command": self.state.last_command,
        }

        for address, value in payloads.items():
            if self._last_osc_values.get(address) != value:
                self.osc_client.send(address, value)
                self._last_osc_values[address] = value

    def _open_capture(self, source_value: str) -> cv2.VideoCapture | None:
        source = _parse_camera_source(source_value)
        if isinstance(source, int):
            capture = cv2.VideoCapture(source, cv2.CAP_DSHOW)
            if not capture.isOpened():
                capture = cv2.VideoCapture(source)
        else:
            capture = cv2.VideoCapture(source)

        if capture.isOpened():
            capture.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
            capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
        return capture


def _parse_camera_source(value: str) -> int | str:
    stripped = value.strip()
    return int(stripped) if stripped.isdigit() else stripped


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Escena multimodal con voz y gestos.")
    parser.add_argument(
        "--camera-source",
        default=os.getenv("CAMERA_SOURCE", "0"),
        help="Indice de camara (0, 1, 2) o URL de streaming del celular.",
    )
    parser.add_argument(
        "--hand-model-path",
        default=os.getenv("HAND_MODEL_PATH", str(Path("models") / "hand_landmarker.task")),
        help="Ruta al modelo hand_landmarker.task de MediaPipe Tasks.",
    )
    parser.add_argument(
        "--language",
        default=os.getenv("SPEECH_LANGUAGE", "es-CO"),
        help="Codigo de idioma para el reconocimiento de voz.",
    )
    parser.add_argument("--width", type=int, default=1280, help="Ancho de ventana.")
    parser.add_argument("--height", type=int, default=720, help="Alto de ventana.")
    parser.add_argument("--enable-osc", action="store_true", help="Activa salida OSC.")
    parser.add_argument("--osc-host", default=os.getenv("OSC_HOST", "127.0.0.1"))
    parser.add_argument("--osc-port", type=int, default=int(os.getenv("OSC_PORT", "9000")))
    parser.add_argument(
        "--no-mirror-camera",
        action="store_true",
        help="Desactiva el efecto espejo de la camara.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    config = AppConfig(
        camera_source=args.camera_source,
        hand_model_path=args.hand_model_path,
        window_width=args.width,
        window_height=args.height,
        speech_language=args.language,
        enable_osc=args.enable_osc,
        osc_host=args.osc_host,
        osc_port=args.osc_port,
        mirror_camera=not args.no_mirror_camera,
    )
    app = MultimodalApp(config)
    try:
        return app.run()
    finally:
        app.shutdown()
