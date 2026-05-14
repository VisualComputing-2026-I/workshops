from __future__ import annotations

from dataclasses import dataclass

from .predictor import Prediction


@dataclass(frozen=True)
class StabilizerEvent:
    committed_label: str
    text: str


class PredictionStabilizer:
    """Convert noisy frame-level predictions into deliberate text commits."""

    def __init__(
        self,
        *,
        stable_frames: int = 8,
        confidence_threshold: float = 0.75,
    ) -> None:
        self.stable_frames = max(1, stable_frames)
        self.confidence_threshold = confidence_threshold
        self.pending_label: str | None = None
        self.pending_display_label: str | None = None
        self.pending_count = 0
        self.last_committed_label: str | None = None
        self.characters: list[str] = []

    @property
    def text(self) -> str:
        return "".join(self.characters)

    def clear(self) -> None:
        self.pending_label = None
        self.pending_display_label = None
        self.pending_count = 0
        self.last_committed_label = None
        self.characters.clear()

    def reset_pending(self, *, release_last: bool = False) -> None:
        self.pending_label = None
        self.pending_display_label = None
        self.pending_count = 0
        if release_last:
            self.last_committed_label = None

    def space(self) -> None:
        if self.characters and self.characters[-1] != " ":
            self.characters.append(" ")
        self.reset_pending(release_last=True)

    def delete(self) -> None:
        if self.characters:
            self.characters.pop()
        self.reset_pending(release_last=True)

    def update(
        self,
        label: str | None,
        *,
        confidence: float = 1.0,
        display_label: str | None = None,
    ) -> StabilizerEvent | None:
        if label is None or confidence < self.confidence_threshold:
            self.reset_pending(release_last=True)
            return None

        if label != self.pending_label:
            self.pending_label = label
            self.pending_display_label = display_label or label
            self.pending_count = 1
            if self.pending_count < self.stable_frames:
                return None
        else:
            self.pending_count += 1
            if self.pending_count < self.stable_frames:
                return None

        if label == self.last_committed_label:
            return None

        committed = self.pending_display_label or label
        self.characters.append(committed)
        self.last_committed_label = label
        self.pending_count = 0
        return StabilizerEvent(committed_label=committed, text=self.text)

    def update_from_prediction(self, prediction: Prediction | None) -> StabilizerEvent | None:
        if prediction is None:
            return self.update(None)
        return self.update(
            prediction.label,
            confidence=prediction.confidence,
            display_label=prediction.display_label,
        )
