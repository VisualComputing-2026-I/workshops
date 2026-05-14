from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from .dataset import read_feature_table
from .labels import display_label

NON_FEATURE_COLUMNS = {
    "label",
    "display_label",
    "source_path",
    "source_dir",
    "sequence_id",
    "subset",
    "person",
    "handedness",
    "handedness_score",
    "frames_total",
    "frames_detected",
}


@dataclass(frozen=True)
class TrainResult:
    model_path: Path
    metrics_path: Path
    best_model_name: str
    accuracy: float
    f1_macro: float
    labels: list[str]


def infer_feature_names(dataframe: pd.DataFrame) -> list[str]:
    feature_names: list[str] = []
    for column in dataframe.columns:
        if column in NON_FEATURE_COLUMNS:
            continue
        if pd.api.types.is_numeric_dtype(dataframe[column]):
            feature_names.append(column)
    if not feature_names:
        raise ValueError("No se encontraron columnas numericas de features en el CSV.")
    return feature_names


def _candidate_models(random_state: int) -> dict[str, Any]:
    return {
        "extra_trees": ExtraTreesClassifier(
            n_estimators=600,
            max_features="sqrt",
            class_weight="balanced",
            random_state=random_state,
            n_jobs=-1,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=500,
            max_features="sqrt",
            class_weight="balanced_subsample",
            random_state=random_state,
            n_jobs=-1,
        ),
        "svm_rbf": Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                (
                    "svc",
                    SVC(
                        C=12.0,
                        gamma="scale",
                        probability=True,
                        class_weight="balanced",
                        random_state=random_state,
                    ),
                ),
            ]
        ),
        "mlp": Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                (
                    "mlp",
                    MLPClassifier(
                        hidden_layer_sizes=(256, 128),
                        alpha=1e-4,
                        batch_size="auto",
                        learning_rate="adaptive",
                        max_iter=800,
                        early_stopping=True,
                        random_state=random_state,
                    ),
                ),
            ]
        ),
    }


def _split_data(
    dataframe: pd.DataFrame,
    feature_names: list[str],
    random_state: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    y = dataframe["label"].astype(str).to_numpy()
    X = dataframe[feature_names].astype(np.float32).to_numpy()
    class_counts = pd.Series(y).value_counts()

    if len(class_counts) < 2:
        raise ValueError("Se necesitan al menos dos clases para entrenar.")
    if class_counts.min() < 2:
        raise ValueError(
            "Cada clase necesita al menos 2 muestras para separar entrenamiento y prueba. "
            "Recolecta mas imagenes por letra."
        )

    n_classes = len(class_counts)
    n_samples = len(dataframe)
    test_size = max(n_classes, math.ceil(n_samples * 0.2))
    test_size = min(test_size, n_samples - n_classes)

    return train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )


def train_and_save_model(
    features_csv: str | Path,
    model_path: str | Path,
    metrics_dir: str | Path,
    *,
    random_state: int = 42,
    model_type: str = "frame",
    sequence_length: int | None = None,
) -> TrainResult:
    dataframe = read_feature_table(features_csv)
    feature_names = infer_feature_names(dataframe)
    dataframe = dataframe.dropna(subset=["label", *feature_names]).reset_index(drop=True)
    if dataframe.empty:
        raise ValueError(
            "El CSV de features no contiene muestras validas. "
            "Primero captura imagenes con scripts/capture_samples.py o descarga un dataset, "
            "y luego ejecuta scripts/build_dataset.py."
        )

    X_train, X_test, y_train, y_test = _split_data(dataframe, feature_names, random_state)

    evaluations: dict[str, dict[str, Any]] = {}
    best_name = ""
    best_model: Any | None = None
    best_f1 = -1.0

    for name, model in _candidate_models(random_state).items():
        try:
            model.fit(X_train, y_train)
            predictions = model.predict(X_test)
            accuracy = float(accuracy_score(y_test, predictions))
            f1_macro = float(f1_score(y_test, predictions, average="macro", zero_division=0))
            evaluations[name] = {
                "accuracy": accuracy,
                "f1_macro": f1_macro,
                "status": "ok",
            }
            if f1_macro > best_f1:
                best_name = name
                best_model = model
                best_f1 = f1_macro
        except Exception as exc:  # pragma: no cover - surfaced in metrics file
            evaluations[name] = {
                "status": "failed",
                "error": str(exc),
            }

    if best_model is None:
        raise RuntimeError(f"Ningun modelo pudo entrenarse: {evaluations}")

    predictions = best_model.predict(X_test)
    labels = sorted(pd.Series(dataframe["label"].astype(str)).unique())
    if "display_label" in dataframe.columns:
        display_map = (
            dataframe[["label", "display_label"]]
            .dropna()
            .drop_duplicates("label")
            .set_index("label")["display_label"]
            .astype(str)
            .to_dict()
        )
    else:
        display_map = {}
    display_map = {label: display_map.get(label, display_label(label)) for label in labels}
    report = classification_report(y_test, predictions, labels=labels, zero_division=0, output_dict=True)
    matrix = confusion_matrix(y_test, predictions, labels=labels)

    model_path = Path(model_path)
    metrics_dir = Path(metrics_dir)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_dir.mkdir(parents=True, exist_ok=True)

    metrics = {
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "features_csv": str(Path(features_csv)),
        "model_type": model_type,
        "sequence_length": sequence_length,
        "best_model": best_name,
        "accuracy": float(accuracy_score(y_test, predictions)),
        "f1_macro": float(f1_score(y_test, predictions, average="macro", zero_division=0)),
        "labels": labels,
        "display_labels": display_map,
        "samples_by_label": dataframe["label"].value_counts().sort_index().to_dict(),
        "candidate_models": evaluations,
        "classification_report": report,
    }

    metrics_path = metrics_dir / "metrics.json"
    confusion_path = metrics_dir / "confusion_matrix.csv"

    with metrics_path.open("w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=2, ensure_ascii=False)

    pd.DataFrame(matrix, index=labels, columns=labels).to_csv(confusion_path)

    package = {
        "model": best_model,
        "model_name": best_name,
        "feature_names": feature_names,
        "labels": labels,
        "display_labels": display_map,
        "model_type": model_type,
        "sequence_length": sequence_length,
        "metrics": metrics,
    }
    joblib.dump(package, model_path)

    return TrainResult(
        model_path=model_path,
        metrics_path=metrics_path,
        best_model_name=best_name,
        accuracy=metrics["accuracy"],
        f1_macro=metrics["f1_macro"],
        labels=labels,
    )
