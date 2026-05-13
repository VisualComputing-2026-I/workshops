from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import cv2
import pandas as pd
from pandas.errors import EmptyDataError
from tqdm import tqdm

from .config import IMAGE_EXTENSIONS
from .labels import display_label, label_from_path
from .landmarks import FEATURE_NAMES, create_hands, extract_landmark_result

FEATURE_TABLE_COLUMNS = [
    "label",
    "display_label",
    "source_path",
    "handedness",
    "handedness_score",
    *FEATURE_NAMES,
]


@dataclass(frozen=True)
class BuildReport:
    output_csv: Path
    total_images: int
    accepted_images: int
    skipped_without_label: int
    skipped_without_hand: int
    counts_by_label: dict[str, int]


def iter_image_paths(input_dirs: Iterable[str | Path]) -> list[Path]:
    paths: list[Path] = []
    for input_dir in input_dirs:
        root = Path(input_dir)
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
                paths.append(path)
    return sorted(paths)


def build_features_csv(
    input_dirs: Iterable[str | Path],
    output_csv: str | Path,
    *,
    max_images_per_label: int | None = None,
    min_detection_confidence: float = 0.6,
    mirror_left: bool = True,
) -> BuildReport:
    output_csv = Path(output_csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    image_paths = iter_image_paths(input_dirs)
    rows: list[dict[str, object]] = []
    counts: Counter[str] = Counter()
    skipped_without_label = 0
    skipped_without_hand = 0

    with create_hands(
        static_image_mode=True,
        max_num_hands=1,
        min_detection_confidence=min_detection_confidence,
        min_tracking_confidence=0.5,
    ) as hands:
        for image_path in tqdm(image_paths, desc="Extrayendo landmarks"):
            label = label_from_path(image_path)
            if label is None:
                skipped_without_label += 1
                continue
            if max_images_per_label is not None and counts[label] >= max_images_per_label:
                continue

            image_bgr = cv2.imread(str(image_path))
            if image_bgr is None:
                skipped_without_hand += 1
                continue

            image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
            result = extract_landmark_result(image_rgb, hands, mirror_left=mirror_left)
            if result is None:
                skipped_without_hand += 1
                continue

            row: dict[str, object] = {
                "label": label,
                "display_label": display_label(label),
                "source_path": str(image_path),
                "handedness": result.handedness,
                "handedness_score": result.score,
            }
            row.update(
                {feature_name: float(value) for feature_name, value in zip(FEATURE_NAMES, result.feature_vector)}
            )
            rows.append(row)
            counts[label] += 1

    dataframe = pd.DataFrame(rows, columns=FEATURE_TABLE_COLUMNS)
    dataframe.to_csv(output_csv, index=False)

    return BuildReport(
        output_csv=output_csv,
        total_images=len(image_paths),
        accepted_images=len(rows),
        skipped_without_label=skipped_without_label,
        skipped_without_hand=skipped_without_hand,
        counts_by_label=dict(sorted(counts.items())),
    )


def read_feature_table(features_csv: str | Path) -> pd.DataFrame:
    features_csv = Path(features_csv)
    if not features_csv.exists():
        raise FileNotFoundError(
            f"No existe {features_csv}. Primero captura o descarga imagenes y ejecuta "
            "scripts/build_dataset.py para generar data/processed/features.csv."
        )

    try:
        dataframe = pd.read_csv(features_csv)
    except EmptyDataError as exc:
        raise ValueError(
            f"{features_csv} esta vacio. Primero captura o descarga imagenes y vuelve a construir el dataset."
        ) from exc

    missing_columns = {"label"} - set(dataframe.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"El CSV de features no tiene las columnas requeridas: {missing}")
    return dataframe
