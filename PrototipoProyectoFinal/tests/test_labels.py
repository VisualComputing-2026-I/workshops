from pathlib import Path

from lsc_alphabet.labels import display_label, label_from_path, normalize_label


def test_normalize_standard_letters() -> None:
    assert normalize_label("a") == "A"
    assert normalize_label("Letra B") == "B"


def test_normalize_enie_aliases() -> None:
    assert normalize_label("Ñ") == "N_TILDE"
    assert normalize_label("N_TILDE") == "N_TILDE"
    assert normalize_label("enie") == "N_TILDE"
    assert display_label("N_TILDE") == "Ñ"


def test_label_from_path_prefers_parent_folder() -> None:
    path = Path("data/raw/N_TILDE/N_TILDE_20260512_000001.jpg")
    assert label_from_path(path) == "N_TILDE"
