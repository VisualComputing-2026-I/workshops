from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lsc_alphabet.config import EXTERNAL_DATA_DIR, PROCESSED_DATA_DIR
from lsc_alphabet.sequences import build_sequence_features_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convierte secuencias LSC70 en un CSV temporal.")
    parser.add_argument(
        "--input",
        nargs="+",
        type=Path,
        default=[EXTERNAL_DATA_DIR / "lsc70"],
        help="Carpetas donde esta extraido LSC70.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROCESSED_DATA_DIR / "lsc70_words_sequences.csv",
        help="CSV de salida.",
    )
    parser.add_argument(
        "--subset",
        nargs="+",
        default=["LSC70W"],
        choices=["LSC70AN", "LSC70ANH", "LSC70W"],
        help="Subconjuntos a procesar.",
    )
    parser.add_argument("--sequence-length", type=int, default=6, help="Frames por secuencia.")
    parser.add_argument(
        "--min-detected-frames",
        type=int,
        default=None,
        help="Minimo de frames con mano detectada. Por defecto exige sequence-length.",
    )
    parser.add_argument("--max-per-label", type=int, default=None, help="Limite opcional por clase.")
    parser.add_argument("--min-confidence", type=float, default=0.6, help="Confianza minima de MediaPipe.")
    parser.add_argument("--no-mirror-left", action="store_true", help="No reflejar manos izquierdas.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = build_sequence_features_csv(
        args.input,
        args.output,
        subsets=args.subset,
        sequence_length=args.sequence_length,
        min_detected_frames=args.min_detected_frames,
        max_sequences_per_label=args.max_per_label,
        min_detection_confidence=args.min_confidence,
        mirror_left=not args.no_mirror_left,
    )
    print(json.dumps(report.__dict__ | {"output_csv": str(report.output_csv)}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        raise SystemExit(f"Error: {exc}") from None
