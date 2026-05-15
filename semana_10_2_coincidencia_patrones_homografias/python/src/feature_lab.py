from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import cv2
import numpy as np


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


@dataclass
class MatchStats:
    detector: str
    matcher: str
    keypoints_a: int
    keypoints_b: int
    total_matches: int
    good_matches: int
    inliers: int
    inlier_percentage: float
    elapsed_ms: float
    homography: list[list[float]] | None


def list_images(folder: Path) -> list[Path]:
    if not folder.exists():
        return []
    return sorted(path for path in folder.iterdir() if path.suffix.lower() in IMAGE_EXTENSIONS)


def read_image(path: Path, color: bool = True) -> np.ndarray:
    flag = cv2.IMREAD_COLOR if color else cv2.IMREAD_GRAYSCALE
    image = cv2.imread(str(path), flag)
    if image is None:
        raise FileNotFoundError(f"No se pudo cargar la imagen: {path}")
    return image


def create_detector(name: str):
    name = name.lower()
    if name == "sift":
        return cv2.SIFT_create(nfeatures=2500)
    if name == "orb":
        return cv2.ORB_create(nfeatures=3000)
    raise ValueError("Detector no soportado. Usa 'sift' u 'orb'.")


def detect_features(image: np.ndarray, detector_name: str):
    detector = create_detector(detector_name)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    keypoints, descriptors = detector.detectAndCompute(gray, None)
    if descriptors is None:
        size = 128 if detector_name == "sift" else 32
        dtype = np.float32 if detector_name == "sift" else np.uint8
        descriptors = np.empty((0, size), dtype=dtype)
    return keypoints, descriptors


def bf_match(descriptors_a: np.ndarray, descriptors_b: np.ndarray, detector_name: str, ratio: float):
    norm = cv2.NORM_L2 if detector_name == "sift" else cv2.NORM_HAMMING
    bf = cv2.BFMatcher(norm, crossCheck=False)
    if len(descriptors_a) < 2 or len(descriptors_b) < 2:
        return [], 0
    raw_matches = bf.knnMatch(descriptors_a, descriptors_b, k=2)
    good_matches = []
    for pair in raw_matches:
        if len(pair) == 2:
            m, n = pair
            if m.distance < ratio * n.distance:
                good_matches.append(m)
    return sorted(good_matches, key=lambda match: match.distance), len(raw_matches)


def flann_match(descriptors_a: np.ndarray, descriptors_b: np.ndarray, detector_name: str, ratio: float):
    if len(descriptors_a) < 2 or len(descriptors_b) < 2:
        return [], 0

    if detector_name == "sift":
        index_params = dict(algorithm=1, trees=5)  # FLANN_INDEX_KDTREE
        search_params = dict(checks=64)
        descriptors_a = np.float32(descriptors_a)
        descriptors_b = np.float32(descriptors_b)
    else:
        index_params = dict(
            algorithm=6,  # FLANN_INDEX_LSH
            table_number=12,
            key_size=20,
            multi_probe_level=2,
        )
        search_params = dict(checks=64)
        descriptors_a = np.uint8(descriptors_a)
        descriptors_b = np.uint8(descriptors_b)

    flann = cv2.FlannBasedMatcher(index_params, search_params)
    raw_matches = flann.knnMatch(descriptors_a, descriptors_b, k=2)
    good_matches = []
    for pair in raw_matches:
        if len(pair) == 2:
            m, n = pair
            if m.distance < ratio * n.distance:
                good_matches.append(m)
    return sorted(good_matches, key=lambda match: match.distance), len(raw_matches)


def calculate_homography(keypoints_a, keypoints_b, matches, ransac_threshold: float):
    if len(matches) < 4:
        return None, np.zeros((len(matches),), dtype=np.uint8)

    src_points = np.float32([keypoints_a[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    dst_points = np.float32([keypoints_b[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
    homography, mask = cv2.findHomography(src_points, dst_points, cv2.RANSAC, ransac_threshold)
    if mask is None:
        mask = np.zeros((len(matches), 1), dtype=np.uint8)
    return homography, mask.ravel().astype(np.uint8)


def draw_matches(
    image_a: np.ndarray,
    keypoints_a,
    image_b: np.ndarray,
    keypoints_b,
    matches,
    output_path: Path,
    mask: np.ndarray | None = None,
    limit: int = 80,
    match_color: tuple[int, int, int] = (0, 220, 0),
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    selected = list(matches[:limit])
    selected_mask = None
    if mask is not None:
        selected_mask = mask[: len(selected)].astype(int).tolist()

    drawn = cv2.drawMatches(
        image_a,
        keypoints_a,
        image_b,
        keypoints_b,
        selected,
        None,
        matchColor=match_color,
        singlePointColor=(40, 40, 255),
        matchesMask=selected_mask,
        flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
    )
    cv2.imwrite(str(output_path), drawn)


def run_matching_pair(
    image_a_path: Path,
    image_b_path: Path,
    output_dir: Path,
    detector_name: str = "sift",
    matcher_name: str = "bf",
    ratio: float = 0.75,
    ransac_threshold: float = 5.0,
    output_prefix: str | None = None,
) -> MatchStats:
    image_a = read_image(image_a_path)
    image_b = read_image(image_b_path)
    start = time.perf_counter()
    keypoints_a, descriptors_a = detect_features(image_a, detector_name)
    keypoints_b, descriptors_b = detect_features(image_b, detector_name)

    if matcher_name == "bf":
        good_matches, total_matches = bf_match(descriptors_a, descriptors_b, detector_name, ratio)
    elif matcher_name == "flann":
        good_matches, total_matches = flann_match(descriptors_a, descriptors_b, detector_name, ratio)
    else:
        raise ValueError("Matcher no soportado. Usa 'bf' o 'flann'.")

    homography, mask = calculate_homography(keypoints_a, keypoints_b, good_matches, ransac_threshold)
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    inliers = int(mask.sum())
    inlier_percentage = (100.0 * inliers / len(good_matches)) if good_matches else 0.0

    prefix = output_prefix or f"{detector_name}_{matcher_name}"
    draw_matches(
        image_a,
        keypoints_a,
        image_b,
        keypoints_b,
        good_matches,
        output_dir / f"{prefix}_matches.jpg",
    )
    draw_matches(
        image_a,
        keypoints_a,
        image_b,
        keypoints_b,
        good_matches,
        output_dir / f"{prefix}_inliers.jpg",
        mask=mask,
    )
    draw_matches(
        image_a,
        keypoints_a,
        image_b,
        keypoints_b,
        good_matches,
        output_dir / f"{prefix}_outliers.jpg",
        mask=1 - mask,
        match_color=(0, 0, 255),
    )

    return MatchStats(
        detector=detector_name,
        matcher=matcher_name,
        keypoints_a=len(keypoints_a),
        keypoints_b=len(keypoints_b),
        total_matches=total_matches,
        good_matches=len(good_matches),
        inliers=inliers,
        inlier_percentage=inlier_percentage,
        elapsed_ms=elapsed_ms,
        homography=homography.tolist() if homography is not None else None,
    )


def detect_object(
    template_path: Path,
    scene_path: Path,
    output_dir: Path,
    detector_name: str = "sift",
    matcher_name: str = "flann",
    ratio: float = 0.75,
    ransac_threshold: float = 5.0,
) -> MatchStats:
    template = read_image(template_path)
    scene = read_image(scene_path)
    stats = run_matching_pair(
        template_path,
        scene_path,
        output_dir,
        detector_name=detector_name,
        matcher_name=matcher_name,
        ratio=ratio,
        ransac_threshold=ransac_threshold,
        output_prefix=f"{detector_name}_{matcher_name}_object",
    )

    if stats.homography is not None:
        homography = np.array(stats.homography, dtype=np.float64)
        h, w = template.shape[:2]
        corners = np.float32([[0, 0], [w, 0], [w, h], [0, h]]).reshape(-1, 1, 2)
        projected = cv2.perspectiveTransform(corners, homography)
        scene_with_box = scene.copy()
        cv2.polylines(scene_with_box, [np.int32(projected)], True, (0, 255, 0), 4, cv2.LINE_AA)
        output_dir.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output_dir / "object_detection_box.jpg"), scene_with_box)

    return stats


def find_homography_between_images(image_a: np.ndarray, image_b: np.ndarray, detector_name: str, ratio: float):
    keypoints_a, descriptors_a = detect_features(image_a, detector_name)
    keypoints_b, descriptors_b = detect_features(image_b, detector_name)
    matches, _ = flann_match(descriptors_b, descriptors_a, detector_name, ratio)
    homography, mask = calculate_homography(keypoints_b, keypoints_a, matches, 5.0)
    return homography, matches, mask


def image_corners(image: np.ndarray) -> np.ndarray:
    h, w = image.shape[:2]
    return np.float32([[0, 0], [w, 0], [w, h], [0, h]]).reshape(-1, 1, 2)


def blend_warped_images(images: list[np.ndarray], transforms: list[np.ndarray]) -> np.ndarray:
    all_corners = []
    for image, transform in zip(images, transforms):
        all_corners.append(cv2.perspectiveTransform(image_corners(image), transform))

    stacked = np.concatenate(all_corners, axis=0)
    min_xy = np.floor(stacked.min(axis=0).ravel()).astype(int)
    max_xy = np.ceil(stacked.max(axis=0).ravel()).astype(int)
    tx, ty = -min_xy[0], -min_xy[1]
    width, height = max_xy[0] - min_xy[0], max_xy[1] - min_xy[1]

    translation = np.array([[1, 0, tx], [0, 1, ty], [0, 0, 1]], dtype=np.float64)
    accumulator = np.zeros((height, width, 3), dtype=np.float32)
    weights = np.zeros((height, width, 1), dtype=np.float32)

    for image, transform in zip(images, transforms):
        mask = np.ones(image.shape[:2], dtype=np.uint8) * 255
        feather = cv2.distanceTransform(mask, cv2.DIST_L2, 3)
        if feather.max() > 0:
            feather = feather / feather.max()
        feather = np.clip(feather, 0.08, 1.0).astype(np.float32)

        full_transform = translation @ transform
        warped_image = cv2.warpPerspective(image, full_transform, (width, height)).astype(np.float32)
        warped_weight = cv2.warpPerspective(feather, full_transform, (width, height))[:, :, None]
        accumulator += warped_image * warped_weight
        weights += warped_weight

    panorama = accumulator / np.maximum(weights, 1e-6)
    panorama[weights[:, :, 0] <= 0] = 0
    panorama = np.clip(panorama, 0, 255).astype(np.uint8)

    non_empty = np.where(weights[:, :, 0] > 0.02)
    if len(non_empty[0]) > 0:
        y0, y1 = non_empty[0].min(), non_empty[0].max()
        x0, x1 = non_empty[1].min(), non_empty[1].max()
        panorama = panorama[y0 : y1 + 1, x0 : x1 + 1]
    return panorama


def stitch_panorama(
    image_paths: Iterable[Path],
    output_dir: Path,
    detector_name: str = "sift",
    ratio: float = 0.75,
) -> dict:
    paths = list(image_paths)
    if len(paths) < 2:
        raise ValueError("Se necesitan al menos dos imagenes para crear un panorama.")

    start = time.perf_counter()
    images = [read_image(path) for path in paths]
    transforms = [np.eye(3, dtype=np.float64)]
    pair_metrics = []

    for index in range(1, len(images)):
        homography, matches, mask = find_homography_between_images(
            images[index - 1],
            images[index],
            detector_name,
            ratio,
        )
        if homography is None:
            raise RuntimeError(f"No se pudo calcular homografia entre imagen {index} e imagen {index + 1}.")

        transforms.append(transforms[index - 1] @ homography)
        inliers = int(mask.sum())
        pair_metrics.append(
            {
                "pair": [str(paths[index - 1]), str(paths[index])],
                "matches": len(matches),
                "inliers": inliers,
                "inlier_percentage": (100.0 * inliers / len(matches)) if matches else 0.0,
            }
        )

    panorama = blend_warped_images(images, transforms)
    output_dir.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_dir / "panorama.jpg"), panorama)

    return {
        "image_count": len(images),
        "elapsed_ms": (time.perf_counter() - start) * 1000.0,
        "pairs": pair_metrics,
        "output": str(output_dir / "panorama.jpg"),
    }


def write_metrics(output_dir: Path, metrics: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "metrics.json").open("w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=2, ensure_ascii=False)


def stats_to_dict(stats: MatchStats) -> dict:
    return asdict(stats)
