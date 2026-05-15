from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
PANORAMA = DATA / "panorama"


def add_texture(image: np.ndarray, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    noise = rng.normal(0, 8, image.shape).astype(np.int16)
    textured = np.clip(image.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    return textured


def draw_feature_rich_object(width: int = 520, height: int = 360) -> np.ndarray:
    image = np.full((height, width, 3), (236, 234, 226), dtype=np.uint8)
    cv2.rectangle(image, (18, 18), (width - 18, height - 18), (45, 69, 112), 5)
    cv2.rectangle(image, (48, 56), (220, 170), (218, 82, 74), -1)
    cv2.circle(image, (355, 120), 58, (68, 153, 112), -1)
    cv2.circle(image, (355, 120), 30, (245, 205, 74), 4)
    cv2.line(image, (70, 250), (470, 260), (32, 32, 32), 7)
    cv2.line(image, (98, 312), (430, 208), (42, 101, 176), 5)
    cv2.putText(image, "VC 2026", (62, 230), cv2.FONT_HERSHEY_SIMPLEX, 1.35, (28, 28, 28), 4)
    cv2.putText(image, "H", (274, 142), cv2.FONT_HERSHEY_SIMPLEX, 2.2, (28, 28, 28), 6)

    for x in range(40, width - 40, 52):
        color = (30 + (x * 5) % 180, 60 + (x * 7) % 160, 80 + (x * 11) % 150)
        cv2.drawMarker(image, (x, 304), color, cv2.MARKER_TILTED_CROSS, 22, 3)

    rng = np.random.default_rng(17)
    for _ in range(85):
        center = tuple(rng.integers([35, 35], [width - 35, height - 35]).tolist())
        color = tuple(int(v) for v in rng.integers(20, 230, 3))
        cv2.circle(image, center, int(rng.integers(3, 8)), color, -1)

    return add_texture(image, 23)


def perspective_variant(image: np.ndarray) -> np.ndarray:
    h, w = image.shape[:2]
    src = np.float32([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]])
    dst = np.float32([[42, 30], [w - 58, 5], [w - 18, h - 36], [28, h - 8]])
    matrix = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(image, matrix, (w, h), borderValue=(245, 245, 245))
    return add_texture(warped, 41)


def make_scene(template: np.ndarray) -> np.ndarray:
    scene = np.full((620, 880, 3), (224, 229, 225), dtype=np.uint8)
    scene = add_texture(scene, 97)
    cv2.putText(scene, "escena con objeto", (40, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (60, 60, 60), 3)
    cv2.rectangle(scene, (610, 70), (820, 225), (82, 133, 179), -1)
    cv2.circle(scene, (710, 430), 76, (184, 103, 91), -1)
    cv2.line(scene, (35, 530), (835, 500), (58, 58, 58), 5)

    h, w = template.shape[:2]
    src = np.float32([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]])
    dst = np.float32([[160, 175], [640, 130], [690, 455], [120, 490]])
    matrix = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(template, matrix, (scene.shape[1], scene.shape[0]))
    mask = cv2.warpPerspective(np.ones((h, w), dtype=np.uint8) * 255, matrix, (scene.shape[1], scene.shape[0]))
    scene[mask > 0] = warped[mask > 0]
    return scene


def make_panorama_source() -> np.ndarray:
    canvas = np.full((430, 1180, 3), (232, 231, 222), dtype=np.uint8)
    canvas = add_texture(canvas, 121)
    colors = [(202, 82, 73), (68, 145, 117), (62, 102, 172), (225, 183, 70)]
    for index, x in enumerate(range(40, 1120, 90)):
        color = colors[index % len(colors)]
        cv2.rectangle(canvas, (x, 90 + (index % 3) * 24), (x + 58, 154 + (index % 4) * 18), color, -1)
        cv2.circle(canvas, (x + 44, 290 - (index % 4) * 22), 28, colors[(index + 1) % len(colors)], -1)
        cv2.putText(canvas, str(index + 1), (x + 8, 245), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (32, 32, 32), 3)
    cv2.putText(canvas, "panorama feature strip", (260, 55), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (35, 35, 35), 3)
    cv2.line(canvas, (20, 360), (1160, 320), (35, 35, 35), 6)
    return canvas


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    PANORAMA.mkdir(parents=True, exist_ok=True)

    template = draw_feature_rich_object()
    matching_a = template.copy()
    matching_b = perspective_variant(template)
    scene = make_scene(template)

    cv2.imwrite(str(DATA / "matching_1.jpg"), matching_a)
    cv2.imwrite(str(DATA / "matching_2.jpg"), matching_b)
    cv2.imwrite(str(DATA / "template.jpg"), template)
    cv2.imwrite(str(DATA / "scene.jpg"), scene)

    source = make_panorama_source()
    crops = [(0, 600), (290, 890), (580, 1180)]
    for index, (x0, x1) in enumerate(crops, start=1):
        crop = source[:, x0:x1].copy()
        cv2.imwrite(str(PANORAMA / f"pano_{index}.jpg"), crop)

    print(f"Imagenes de prueba creadas en: {DATA}")


if __name__ == "__main__":
    main()
