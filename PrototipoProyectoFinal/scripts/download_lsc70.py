from __future__ import annotations

import argparse
import json
import os
import zipfile
from pathlib import Path
from urllib.parse import urljoin

import requests
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data" / "external" / "lsc70"
DATASET_ID = "9ssyn8tff5"
VERSION = "2"
API_URL = f"https://api.mendeley.com/datasets/{DATASET_ID}"
PUBLIC_URL = f"https://data.mendeley.com/datasets/{DATASET_ID}/{VERSION}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Descarga LSC70 desde Mendeley Data cuando el API lo permita.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--version", default=VERSION)
    parser.add_argument("--extract", action="store_true", help="Extraer archivos zip descargados.")
    parser.add_argument("--metadata-only", action="store_true", help="Solo guardar metadata del dataset.")
    return parser.parse_args()


def request_dataset_metadata(version: str) -> dict:
    headers = {"Accept": "application/vnd.mendeley-public-dataset.1+json"}
    token = os.getenv("MENDELEY_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    params = {
        "version": version,
        "fields": (
            "id,short_id,version,name,description,doi.id,data_licence.short_name,"
            "data_licence.url,files.id,files.filename,files.file_size,files.mime_type,"
            "files.download_url,files.url"
        ),
    }
    response = requests.get(API_URL, headers=headers, params=params, timeout=60)
    response.raise_for_status()
    return response.json()


def fallback_metadata(version: str, error: str) -> dict:
    return {
        "id": DATASET_ID,
        "version": version,
        "name": "Speak in Colombian Sign Language: A Dynamic LSC70 Database",
        "doi": {"id": "10.17632/9ssyn8tff5.2"},
        "data_licence": {"short_name": "CC BY 4.0"},
        "public_url": f"https://data.mendeley.com/datasets/{DATASET_ID}/{version}",
        "files": [],
        "download_note": (
            "El API de Mendeley puede requerir MENDELEY_TOKEN. "
            "Descargue manualmente desde public_url y extraiga los archivos en esta carpeta."
        ),
        "api_error": error,
    }


def candidate_download_urls(file_info: dict) -> list[str]:
    urls = []
    for key in ("download_url", "downloadUrl", "url"):
        value = file_info.get(key)
        if value:
            urls.append(value)

    file_id = file_info.get("id")
    if file_id:
        urls.append(f"https://data.mendeley.com/public-files/datasets/{DATASET_ID}/files/{file_id}/download")
        urls.append(urljoin("https://api.mendeley.com/", f"file_contents/{file_id}"))

    return urls


def download_file(urls: list[str], output_path: Path) -> bool:
    headers = {}
    token = os.getenv("MENDELEY_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    for url in urls:
        try:
            with requests.get(url, headers=headers, stream=True, timeout=120) as response:
                if response.status_code >= 400:
                    continue
                total = int(response.headers.get("content-length", 0))
                with output_path.open("wb") as file, tqdm(
                    total=total,
                    unit="B",
                    unit_scale=True,
                    desc=output_path.name,
                ) as progress:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            file.write(chunk)
                            progress.update(len(chunk))
                return True
        except requests.RequestException:
            continue
    return False


def extract_zips(output_dir: Path) -> None:
    for zip_path in output_dir.glob("*.zip"):
        target_dir = output_dir / zip_path.stem
        target_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path) as archive:
            archive.extractall(target_dir)


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    try:
        metadata = request_dataset_metadata(args.version)
    except requests.HTTPError as exc:
        status_code = exc.response.status_code if exc.response is not None else "unknown"
        if status_code != 401:
            raise
        metadata = fallback_metadata(args.version, f"HTTP {status_code}: {exc}")
    metadata_path = args.output_dir / "metadata.json"
    with metadata_path.open("w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=2, ensure_ascii=False)

    files = metadata.get("files", [])
    if args.metadata_only:
        print(f"Metadata guardada en {metadata_path}")
        return

    if not files:
        print(
            "No se encontraron archivos descargables en la respuesta del API. "
            f"Descarga manualmente desde {metadata.get('public_url', PUBLIC_URL)} "
            f"y extrae el contenido en {args.output_dir}."
        )
        return

    downloaded = 0
    for file_info in files:
        filename = file_info.get("filename") or file_info.get("name") or f"{file_info.get('id')}.bin"
        output_path = args.output_dir / filename
        if output_path.exists():
            downloaded += 1
            continue
        if download_file(candidate_download_urls(file_info), output_path):
            downloaded += 1
        else:
            print(f"No se pudo descargar automaticamente: {filename}")

    if args.extract:
        extract_zips(args.output_dir)

    print(f"Archivos descargados: {downloaded}/{len(files)} en {args.output_dir}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        raise SystemExit(f"Error: {exc}") from None
