from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
EXTERNAL_DATA_DIR = DATA_DIR / "external"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = PROJECT_ROOT / "models"

DEFAULT_FEATURES_PATH = PROCESSED_DATA_DIR / "features.csv"
DEFAULT_MODEL_PATH = MODELS_DIR / "best_model.joblib"
DEFAULT_METRICS_DIR = MODELS_DIR / "metrics"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
