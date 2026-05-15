from __future__ import annotations

import argparse
from pathlib import Path

from src.feature_lab import (
    detect_object,
    list_images,
    run_matching_pair,
    stats_to_dict,
    stitch_panorama,
    write_metrics,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Taller de coincidencia de caracteristicas, homografias y panorama con OpenCV."
    )
    parser.add_argument("--detector", choices=["sift", "orb"], default="sift")
    parser.add_argument("--ratio", type=float, default=0.75, help="Ratio test de Lowe.")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    parser.add_argument("--match-a", type=Path, help="Primera imagen para matching.")
    parser.add_argument("--match-b", type=Path, help="Segunda imagen para matching.")
    parser.add_argument("--object-template", type=Path, help="Imagen template del objeto.")
    parser.add_argument("--object-scene", type=Path, help="Imagen de escena donde buscar el objeto.")
    parser.add_argument(
        "--panorama-dir",
        type=Path,
        help="Carpeta con 2 o mas imagenes solapadas para crear panorama.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    output_dir = args.output_dir
    metrics = {}

    if args.match_a and args.match_b:
        metrics["bf_matcher"] = stats_to_dict(
            run_matching_pair(
                args.match_a,
                args.match_b,
                output_dir,
                detector_name=args.detector,
                matcher_name="bf",
                ratio=args.ratio,
            )
        )
        metrics["flann_matcher"] = stats_to_dict(
            run_matching_pair(
                args.match_a,
                args.match_b,
                output_dir,
                detector_name=args.detector,
                matcher_name="flann",
                ratio=args.ratio,
            )
        )

    if args.object_template and args.object_scene:
        metrics["object_detection"] = stats_to_dict(
            detect_object(
                args.object_template,
                args.object_scene,
                output_dir,
                detector_name=args.detector,
                matcher_name="flann",
                ratio=args.ratio,
            )
        )

    if args.panorama_dir:
        panorama_images = list_images(args.panorama_dir)
        metrics["panorama"] = stitch_panorama(
            panorama_images,
            output_dir,
            detector_name=args.detector,
            ratio=args.ratio,
        )

    if not metrics:
        print("No se recibieron imagenes de entrada.")
        print("Ejemplo:")
        print(
            "python main.py --match-a data/matching_1.jpg --match-b data/matching_2.jpg "
            "--object-template data/template.jpg --object-scene data/scene.jpg "
            "--panorama-dir data/panorama --output-dir outputs"
        )
        return 0

    write_metrics(output_dir, metrics)
    print(f"Resultados guardados en: {output_dir.resolve()}")
    print(f"Metricas guardadas en: {(output_dir / 'metrics.json').resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
