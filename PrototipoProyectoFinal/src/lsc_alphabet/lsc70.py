from __future__ import annotations

import re
from pathlib import Path

from .labels import display_label, normalize_label

LSC70_SUBSETS = ("LSC70AN", "LSC70ANH", "LSC70W")

LSC70_WORD_LABELS = (
    "ANNOS",
    "BUENAS",
    "DIAS",
    "GUSTAR",
    "HOLA",
    "LICOR",
    "NOCHES",
    "NOMBRE",
    "TARDES",
    "YO",
)

LSC70_WORD_DISPLAY_LABELS = {
    "ANNOS": "AÑOS",
}


def normalize_lsc70_label(value: str) -> str:
    token = str(value).strip().upper().replace(" ", "_").replace("-", "_")
    token = re.sub(r"[^A-Z0-9_]", "_", token)
    token = re.sub(r"_+", "_", token).strip("_")

    if token == "NN":
        return "N_TILDE"
    if token in LSC70_WORD_LABELS or token in {"MIL", "MILLON"}:
        return token
    if token.isdigit():
        return token

    try:
        return normalize_label(token)
    except ValueError:
        return token


def display_lsc70_label(label: str) -> str:
    if label in LSC70_WORD_DISPLAY_LABELS:
        return LSC70_WORD_DISPLAY_LABELS[label]
    return display_label(label)


def lsc70_subset_from_path(path: str | Path) -> str | None:
    parts = Path(path).parts
    for part in parts:
        if part in LSC70_SUBSETS:
            return part
    return None
