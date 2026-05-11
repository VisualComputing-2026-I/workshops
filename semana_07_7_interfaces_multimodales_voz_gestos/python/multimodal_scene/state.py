from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Tuple


COLOR_PALETTE = {
    "azul": (78, 161, 255),
    "verde": (88, 214, 141),
    "rojo": (255, 99, 132),
    "amarillo": (255, 214, 102),
    "magenta": (214, 88, 214),
}

COLOR_ORDER = tuple(COLOR_PALETTE.keys())


@dataclass(slots=True)
class HandObservation:
    hand_present: bool = False
    hand_open: bool = False
    two_fingers: bool = False
    gesture_name: str = "Sin mano"
    pointer: Tuple[float, float] = (0.5, 0.5)


@dataclass(slots=True)
class VoiceEvent:
    event_type: str
    transcript: str = ""
    keywords: Tuple[str, ...] = ()
    message: str = ""
    created_at: float = field(default_factory=time.time)


@dataclass(slots=True)
class AppState:
    color_name: str = "azul"
    object_visible: bool = True
    rotation_mode: bool = False
    move_mode: bool = False
    object_angle: float = 0.0
    object_position: Tuple[float, float] = (640.0, 360.0)
    gesture_name: str = "Sin mano"
    hand_present: bool = False
    voice_phrase: str = ""
    last_command: str = "Ninguno"
    status_message: str = "Inicializando..."
    status_level: str = "info"
    last_status_at: float = field(default_factory=time.time)

    @property
    def color_rgb(self) -> Tuple[int, int, int]:
        return COLOR_PALETTE[self.color_name]
