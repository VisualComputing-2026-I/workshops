from lsc_alphabet.lsc70 import display_lsc70_label, normalize_lsc70_label


def test_lsc70_label_normalization() -> None:
    assert normalize_lsc70_label("NN") == "N_TILDE"
    assert normalize_lsc70_label("HOLA") == "HOLA"
    assert normalize_lsc70_label("10") == "10"


def test_lsc70_display_labels() -> None:
    assert display_lsc70_label("N_TILDE") == "Ñ"
    assert display_lsc70_label("ANNOS") == "AÑOS"
