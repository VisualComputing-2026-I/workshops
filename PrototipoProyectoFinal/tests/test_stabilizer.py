from lsc_alphabet.stabilizer import PredictionStabilizer


def test_stabilizer_commits_after_stable_frames() -> None:
    stabilizer = PredictionStabilizer(stable_frames=3, confidence_threshold=0.7)

    assert stabilizer.update("A", confidence=0.8) is None
    assert stabilizer.update("A", confidence=0.8) is None
    event = stabilizer.update("A", confidence=0.8)

    assert event is not None
    assert event.committed_label == "A"
    assert stabilizer.text == "A"


def test_stabilizer_requires_release_for_same_letter() -> None:
    stabilizer = PredictionStabilizer(stable_frames=2, confidence_threshold=0.7)

    stabilizer.update("A", confidence=0.8)
    stabilizer.update("A", confidence=0.8)
    stabilizer.update("A", confidence=0.8)
    stabilizer.update("A", confidence=0.8)
    assert stabilizer.text == "A"

    stabilizer.update(None)
    stabilizer.update("A", confidence=0.8)
    stabilizer.update("A", confidence=0.8)
    assert stabilizer.text == "AA"


def test_space_delete_clear() -> None:
    stabilizer = PredictionStabilizer(stable_frames=1, confidence_threshold=0.7)
    stabilizer.update("A", confidence=0.8)
    stabilizer.space()
    stabilizer.update("B", confidence=0.8)
    assert stabilizer.text == "A B"

    stabilizer.delete()
    assert stabilizer.text == "A "

    stabilizer.clear()
    assert stabilizer.text == ""
