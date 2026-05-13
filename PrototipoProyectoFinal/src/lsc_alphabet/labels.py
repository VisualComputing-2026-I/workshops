from __future__ import annotations

import re
import unicodedata
from pathlib import Path

ALPHABET_LABELS: tuple[str, ...] = (
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "N_TILDE",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
)

DISPLAY_LABELS: dict[str, str] = {
    "N_TILDE": "Ñ",
}

DIRECT_ALIASES = {
    "Ñ": "N_TILDE",
    "Ñ": "N_TILDE",
    "N~": "N_TILDE",
    "NN": "N_TILDE",
    "N_TILDE": "N_TILDE",
    "N-TILDE": "N_TILDE",
    "NTILDE": "N_TILDE",
    "ENIE": "N_TILDE",
    "ENE": "N_TILDE",
    "LETRA_Ñ": "N_TILDE",
    "LETRA_N_TILDE": "N_TILDE",
    "LETRA_ENIE": "N_TILDE",
}


def display_label(label: str) -> str:
    """Return the human-readable label shown in the UI."""

    return DISPLAY_LABELS.get(label, label)


def _ascii_fold(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(char for char in normalized if not unicodedata.combining(char))


def _canonical_token(value: str) -> str:
    token = value.strip().upper()
    token = token.replace(" ", "_").replace("-", "_")
    token = re.sub(r"[^A-ZÑ0-9_~]", "_", token)
    token = re.sub(r"_+", "_", token).strip("_")
    return token


def normalize_label(value: str) -> str:
    """Map folder names or user input to the internal label set.

    The project stores the letter Ñ as ``N_TILDE`` to keep folder and model
    filenames portable across operating systems.
    """

    if not value or not str(value).strip():
        raise ValueError("La etiqueta no puede estar vacia.")

    token = _canonical_token(str(value))
    if token in ALPHABET_LABELS:
        return token
    if token in DIRECT_ALIASES:
        return DIRECT_ALIASES[token]

    folded = _canonical_token(_ascii_fold(token))
    if folded in DIRECT_ALIASES:
        return DIRECT_ALIASES[folded]
    if folded in ALPHABET_LABELS:
        return folded

    for prefix in ("LETRA_", "LETTER_", "SIGN_", "SENA_", "SEÑA_"):
        if folded.startswith(prefix):
            candidate = folded.removeprefix(prefix)
            if candidate in DIRECT_ALIASES:
                return DIRECT_ALIASES[candidate]
            if candidate in ALPHABET_LABELS:
                return candidate

    raise ValueError(f"Etiqueta no reconocida: {value!r}")


def label_from_path(path: str | Path) -> str | None:
    """Infer a label from any path segment or filename prefix."""

    path = Path(path)
    candidates = list(reversed(path.parent.parts))
    if path.stem:
        candidates.append(path.stem)
        candidates.append(path.stem.split("_")[0])
        candidates.append(path.stem.split("-")[0])

    for part in candidates:
        try:
            return normalize_label(part)
        except ValueError:
            pass

        for token in re.split(r"[\s_\-./\\]+", part):
            if not token:
                continue
            try:
                return normalize_label(token)
            except ValueError:
                continue

    return None


def label_options_for_cli() -> str:
    return ", ".join(display_label(label) for label in ALPHABET_LABELS)
