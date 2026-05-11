from __future__ import annotations

import math

import cv2
import numpy as np
import pygame

from .state import AppState, HandObservation


class SceneRenderer:
    def __init__(self, width: int, height: int) -> None:
        pygame.init()
        pygame.display.set_caption("Escena Multimodal: voz + gestos")
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.width = width
        self.height = height
        self.elapsed = 0.0
        self.title_font = pygame.font.SysFont("Bahnschrift", 30, bold=True)
        self.panel_font = pygame.font.SysFont("Consolas", 20)
        self.small_font = pygame.font.SysFont("Consolas", 16)

    def tick(self) -> float:
        dt = self.clock.tick(30) / 1000.0
        self.elapsed += dt
        return dt

    def draw(self, state: AppState, hand: HandObservation, video_frame: np.ndarray | None) -> None:
        self._draw_background()
        self._draw_scene_core(state)
        self._draw_feedback_rings(state, hand)
        if video_frame is not None:
            self._draw_video_preview(video_frame)
        self._draw_panels(state, hand)
        pygame.display.flip()

    def shutdown(self) -> None:
        pygame.quit()

    def _draw_background(self) -> None:
        top = np.array((10, 22, 34), dtype=np.float32)
        bottom = np.array((24, 68, 92), dtype=np.float32)

        for y in range(self.height):
            ratio = y / max(self.height - 1, 1)
            color = top * (1.0 - ratio) + bottom * ratio
            pygame.draw.line(self.screen, color.astype(int), (0, y), (self.width, y))

        for i in range(10):
            offset = (self.elapsed * 35 + i * 110) % (self.width + 220) - 110
            rect = pygame.Rect(int(offset), 70 + i * 55, 160, 24)
            pygame.draw.ellipse(self.screen, (180, 220, 230), rect, 1)

    def _draw_scene_core(self, state: AppState) -> None:
        center = np.array(state.object_position, dtype=np.float32)
        pulse = 1.0 + 0.05 * math.sin(self.elapsed * 3.5)

        shadow_center = (int(center[0] + 16), int(center[1] + 20))
        pygame.draw.circle(self.screen, (6, 10, 18), shadow_center, int(108 * pulse))

        if not state.object_visible:
            hidden = self.title_font.render("OBJETO OCULTO", True, (245, 245, 245))
            self.screen.blit(hidden, (self.width // 2 - hidden.get_width() // 2, self.height // 2 - 20))
            return

        sides = 6
        radius = 92 * pulse
        base_points = []
        for index in range(sides):
            angle = math.radians(state.object_angle + index * (360 / sides))
            base_points.append((math.cos(angle), math.sin(angle)))

        points = np.array(base_points, dtype=np.float32) * radius + center
        polygon_points = [(int(point[0]), int(point[1])) for point in points]

        pygame.draw.polygon(self.screen, state.color_rgb, polygon_points)
        pygame.draw.aalines(self.screen, (245, 245, 245), True, polygon_points)
        pygame.draw.circle(self.screen, (245, 245, 245), tuple(center.astype(int)), 10)

    def _draw_feedback_rings(self, state: AppState, hand: HandObservation) -> None:
        center = (int(state.object_position[0]), int(state.object_position[1]))
        primary = state.color_rgb
        ring_color = tuple(min(channel + 35, 255) for channel in primary)
        base_radius = 124 + int(8 * math.sin(self.elapsed * 4.0))

        if state.rotation_mode:
            pygame.draw.circle(self.screen, ring_color, center, base_radius, 3)

        if state.move_mode:
            pygame.draw.circle(self.screen, (255, 255, 255), center, base_radius + 18, 2)

        if hand.hand_present:
            hand_radius = base_radius + (30 if hand.hand_open else 15)
            pygame.draw.circle(self.screen, (42, 247, 201), center, hand_radius, 1)

    def _draw_panels(self, state: AppState, hand: HandObservation) -> None:
        header = self.title_font.render("ESCENA MULTIMODAL", True, (248, 250, 252))
        self.screen.blit(header, (34, 26))

        panel = pygame.Rect(24, self.height - 184, 560, 150)
        pygame.draw.rect(self.screen, (8, 18, 28), panel, border_radius=18)
        pygame.draw.rect(self.screen, (70, 202, 255), panel, 2, border_radius=18)

        lines = [
            f"Gesto: {hand.gesture_name}",
            f"Voz: {state.voice_phrase or 'Esperando comando...'}",
            f"Ultimo comando: {state.last_command}",
            f"Modos: mover={'ON' if state.move_mode else 'OFF'} | rotar={'ON' if state.rotation_mode else 'OFF'}",
            f"Estado: {state.status_message}",
        ]

        for index, line in enumerate(lines):
            text = self.panel_font.render(line, True, (235, 241, 245))
            self.screen.blit(text, (44, self.height - 170 + index * 26))

        hint = self.small_font.render("ESC salir | R reiniciar", True, (195, 205, 214))
        self.screen.blit(hint, (self.width - 250, self.height - 34))

    def _draw_video_preview(self, frame: np.ndarray) -> None:
        preview = cv2.resize(frame, (340, 220))
        rgb = cv2.cvtColor(preview, cv2.COLOR_BGR2RGB)
        surface = pygame.surfarray.make_surface(np.transpose(rgb, (1, 0, 2)))
        rect = surface.get_rect(topright=(self.width - 28, 30))
        pygame.draw.rect(self.screen, (8, 18, 28), rect.inflate(12, 12), border_radius=18)
        pygame.draw.rect(self.screen, (255, 214, 102), rect.inflate(12, 12), 2, border_radius=18)
        self.screen.blit(surface, rect)
