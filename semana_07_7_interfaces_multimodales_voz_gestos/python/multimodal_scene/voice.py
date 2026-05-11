from __future__ import annotations

import queue
import threading
import time
from typing import Iterable

import speech_recognition as sr

from .state import VoiceEvent


COMMAND_ALIASES = {
    "cambiar": ("cambiar", "cambio"),
    "azul": ("azul",),
    "verde": ("verde",),
    "rojo": ("rojo",),
    "amarillo": ("amarillo",),
    "magenta": ("magenta", "morado"),
    "rotar": ("rotar", "girar"),
    "mostrar": ("mostrar", "aparecer"),
    "ocultar": ("ocultar", "esconder"),
    "mover": ("mover", "mueve"),
    "detener": ("detener", "parar", "alto"),
}


class VoiceListener:
    def __init__(self, event_queue: "queue.Queue[VoiceEvent]", language: str = "es-CO") -> None:
        self._event_queue = event_queue
        self._language = language
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._recognizer = sr.Recognizer()
        self._recognizer.dynamic_energy_threshold = True
        self._recognizer.pause_threshold = 0.7
        self._recognizer.non_speaking_duration = 0.4

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._run, name="voice-listener", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

    def _run(self) -> None:
        try:
            with sr.Microphone() as source:
                self._event_queue.put(VoiceEvent("status", message="Calibrando microfono..."))
                self._recognizer.adjust_for_ambient_noise(source, duration=1.0)
                self._event_queue.put(VoiceEvent("status", message="Microfono listo."))

                while not self._stop_event.is_set():
                    try:
                        audio = self._recognizer.listen(source, timeout=1.0, phrase_time_limit=3.0)
                    except sr.WaitTimeoutError:
                        continue

                    try:
                        transcript = self._recognizer.recognize_google(audio, language=self._language)
                    except sr.UnknownValueError:
                        self._event_queue.put(VoiceEvent("status", message="No se entendio el comando."))
                        continue
                    except sr.RequestError as exc:
                        self._event_queue.put(VoiceEvent("error", message=f"Error de voz: {exc}"))
                        time.sleep(1.0)
                        continue

                    normalized = transcript.lower().strip()
                    keywords = tuple(self._extract_keywords(normalized))
                    self._event_queue.put(
                        VoiceEvent(
                            "recognized",
                            transcript=normalized,
                            keywords=keywords,
                            message="Comando reconocido." if keywords else "Frase reconocida sin comando util.",
                        )
                    )
        except OSError as exc:
            self._event_queue.put(VoiceEvent("error", message=f"No se pudo abrir el microfono: {exc}"))

    def _extract_keywords(self, transcript: str) -> Iterable[str]:
        for keyword, aliases in COMMAND_ALIASES.items():
            if any(alias in transcript for alias in aliases):
                yield keyword
