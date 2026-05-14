from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data" / "external" / "kaggle_lsc_alphabet"
DATASET = "danielrey96/colombian-sign-language-lsc-alphabet"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Descarga el dataset de alfabeto LSC desde Kaggle.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--keep-zip", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    if shutil.which("kaggle") is None:
        raise RuntimeError(
            "No se encontro el comando 'kaggle'. Instala kaggle y configura kaggle.json "
            "segun la documentacion oficial de Kaggle."
        )

    command = [
        "kaggle",
        "datasets",
        "download",
        "-d",
        DATASET,
        "-p",
        str(args.output_dir),
        "--unzip",
    ]
    subprocess.run(command, check=True)

    if not args.keep_zip:
        for zip_path in args.output_dir.glob("*.zip"):
            zip_path.unlink()

    print(f"Dataset Kaggle descargado en {args.output_dir}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        raise SystemExit(f"Error: {exc}") from None
