from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lsc_alphabet.config import DEFAULT_FEATURES_PATH, DEFAULT_METRICS_DIR, DEFAULT_MODEL_PATH
from lsc_alphabet.training import train_and_save_model


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Entrena el clasificador del alfabeto LSC.")
    parser.add_argument("--features", type=Path, default=DEFAULT_FEATURES_PATH, help="CSV de landmarks.")
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL_PATH, help="Archivo .joblib de salida.")
    parser.add_argument("--metrics-dir", type=Path, default=DEFAULT_METRICS_DIR, help="Carpeta de metricas.")
    parser.add_argument("--seed", type=int, default=42, help="Semilla aleatoria.")
    parser.add_argument("--model-type", default="frame", choices=["frame", "sequence"], help="Tipo de modelo.")
    parser.add_argument("--sequence-length", type=int, default=None, help="Frames por secuencia si model-type=sequence.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = train_and_save_model(
        args.features,
        args.model,
        args.metrics_dir,
        random_state=args.seed,
        model_type=args.model_type,
        sequence_length=args.sequence_length,
    )
    print(json.dumps(result.__dict__ | {"model_path": str(result.model_path), "metrics_path": str(result.metrics_path)}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        raise SystemExit(f"Error: {exc}") from None
