from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable

import cv2
import numpy as np
import pandas as pd
from tqdm import tqdm

from .config import IMAGE_EXTENSIONS
from .landmarks import FEATURE_NAMES, create_hands, extract_landmark_result
from .lsc70 import display_lsc70_label, lsc70_subset_from_path, normalize_lsc70_label

SEQUENCE_META_COLUMNS = [
    "label",
    "display_label",
    "sequence_id",
    "subset",
    "person",
    "source_dir",
    "frames_total",
    "frames_detected",
]


@dataclass(frozen=True)
class SequenceBuildReport:
    output_csv: Path
    total_sequences: int
    accepted_sequences: int
    skipped_without_label: int
    skipped_without_enough_frames: int
    counts_by_label: dict[str, int]


def sequence_feature_names(sequence_length: int) -> list[str]:
    names: list[str] = []
    for frame_idx in range(sequence_length):
        names.extend([f"seq_{frame_idx:02d}_{name}" for name in FEATURE_NAMES])
    names.extend([f"mean_{name}" for name in FEATURE_NAMES])
    names.extend([f"std_{name}" for name in FEATURE_NAMES])
    names.extend([f"delta_{name}" for name in FEATURE_NAMES])
    return names


def build_sequence_feature_vector(frame_vectors: list[np.ndarray] | np.ndarray) -> np.ndarray:
    matrix = np.asarray(frame_vectors, dtype=np.float32)
    if matrix.ndim != 2:
        raise ValueError("La secuencia debe tener forma (frames, features).")
    if matrix.shape[0] < 2:
        raise ValueError("La secuencia necesita al menos 2 frames.")

    mean = matrix.mean(axis=0)
    std = matrix.std(axis=0)
    delta = matrix[-1] - matrix[0]
    return np.concatenate([matrix.reshape(-1), mean, std, delta]).astype(np.float32)


def _frame_index(path: Path) -> int:
    match = re.search(r"_(\d+)$", path.stem)
    return int(match.group(1)) if match else 0


def _resample_vectors(vectors: list[np.ndarray], sequence_length: int) -> list[np.ndarray]:
    if len(vectors) < sequence_length:
        raise ValueError("No hay suficientes frames detectados.")
    if len(vectors) == sequence_length:
        return vectors
    indices = np.linspace(0, len(vectors) - 1, sequence_length).round().astype(int)
    return [vectors[int(index)] for index in indices]


def iter_sequence_dirs(input_dirs: Iterable[str | Path], subsets: set[str] | None = None) -> list[Path]:
    sequence_dirs: list[Path] = []
    for input_dir in input_dirs:
        root = Path(input_dir)
        if not root.exists():
            continue

        for directory in root.rglob("*"):
            if not directory.is_dir():
                continue
            subset = lsc70_subset_from_path(directory)
            if subset is None:
                continue
            if subsets is not None and subset not in subsets:
                continue

            image_count = sum(
                1
                for path in directory.iterdir()
                if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
            )
            if image_count:
                sequence_dirs.append(directory)

    return sorted(sequence_dirs)


def build_sequence_features_csv(
    input_dirs: Iterable[str | Path],
    output_csv: str | Path,
    *,
    subsets: Iterable[str] | None = None,
    sequence_length: int = 6,
    min_detected_frames: int | None = None,
    max_sequences_per_label: int | None = None,
    min_detection_confidence: float = 0.6,
    mirror_left: bool = True,
) -> SequenceBuildReport:
    output_csv = Path(output_csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    subset_filter = {subset.strip() for subset in subsets} if subsets else None
    min_detected_frames = sequence_length if min_detected_frames is None else min_detected_frames
    sequence_dirs = iter_sequence_dirs(input_dirs, subset_filter)
    feature_names = sequence_feature_names(sequence_length)

    rows: list[dict[str, object]] = []
    counts: Counter[str] = Counter()
    skipped_without_label = 0
    skipped_without_enough_frames = 0

    with create_hands(
        static_image_mode=True,
        max_num_hands=1,
        min_detection_confidence=min_detection_confidence,
        min_tracking_confidence=0.5,
    ) as hands:
        for sequence_dir in tqdm(sequence_dirs, desc="Extrayendo secuencias"):
            subset = lsc70_subset_from_path(sequence_dir) or ""
            person = sequence_dir.parent.name
            raw_label = sequence_dir.name
            label = normalize_lsc70_label(raw_label)
            if not label:
                skipped_without_label += 1
                continue
            if max_sequences_per_label is not None and counts[label] >= max_sequences_per_label:
                continue

            image_paths = sorted(
                [
                    path
                    for path in sequence_dir.iterdir()
                    if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
                ],
                key=_frame_index,
            )

            frame_vectors: list[np.ndarray] = []
            for image_path in image_paths:
                image_bgr = cv2.imread(str(image_path))
                if image_bgr is None:
                    continue
                image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
                result = extract_landmark_result(image_rgb, hands, mirror_left=mirror_left)
                if result is not None:
                    frame_vectors.append(result.feature_vector)

            if len(frame_vectors) < min_detected_frames:
                skipped_without_enough_frames += 1
                continue

            try:
                selected_vectors = _resample_vectors(frame_vectors, sequence_length)
            except ValueError:
                skipped_without_enough_frames += 1
                continue

            feature_vector = build_sequence_feature_vector(selected_vectors)
            sequence_id = f"{subset}/{person}/{label}"
            row: dict[str, object] = {
                "label": label,
                "display_label": display_lsc70_label(label),
                "sequence_id": sequence_id,
                "subset": subset,
                "person": person,
                "source_dir": str(sequence_dir),
                "frames_total": len(image_paths),
                "frames_detected": len(frame_vectors),
            }
            row.update(
                {feature_name: float(value) for feature_name, value in zip(feature_names, feature_vector)}
            )
            rows.append(row)
            counts[label] += 1

    dataframe = pd.DataFrame(rows, columns=[*SEQUENCE_META_COLUMNS, *feature_names])
    dataframe.to_csv(output_csv, index=False)

    return SequenceBuildReport(
        output_csv=output_csv,
        total_sequences=len(sequence_dirs),
        accepted_sequences=len(rows),
        skipped_without_label=skipped_without_label,
        skipped_without_enough_frames=skipped_without_enough_frames,
        counts_by_label=dict(sorted(counts.items())),
    )
