from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lsc_alphabet.config import DEFAULT_FEATURES_PATH, EXTERNAL_DATA_DIR, RAW_DATA_DIR
from lsc_alphabet.dataset import build_features_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convierte imagenes LSC en un CSV de landmarks.")
    parser.add_argument(
        "--input",
        nargs="+",
        type=Path,
        default=[RAW_DATA_DIR, EXTERNAL_DATA_DIR],
        help="Carpetas de imagenes organizadas por etiqueta.",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_FEATURES_PATH, help="CSV de salida.")
    parser.add_argument("--max-per-label", type=int, default=None, help="Limite opcional por clase.")
    parser.add_argument("--min-confidence", type=float, default=0.6, help="Confianza minima de MediaPipe.")
    parser.add_argument("--no-mirror-left", action="store_true", help="No reflejar manos izquierdas.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = build_features_csv(
        args.input,
        args.output,
        max_images_per_label=args.max_per_label,
        min_detection_confidence=args.min_confidence,
        mirror_left=not args.no_mirror_left,
    )
    print(json.dumps(report.__dict__ | {"output_csv": str(report.output_csv)}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        raise SystemExit(f"Error: {exc}") from None
