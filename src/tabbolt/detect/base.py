"""Detector interfaces for TabBolt."""
from __future__ import annotations

from typing import Protocol, runtime_checkable

from pydantic import BaseModel, Field

from ..models import BBox


class DetectedRegion(BaseModel):
    """Region returned by a detector representing a candidate table."""

    page: int
    bbox: BBox
    lines: list[BBox] = Field(default_factory=list)
    boxes: list[BBox] = Field(default_factory=list)
    conf: float = 1.0
    detector_version: str

    model_config = {
        "arbitrary_types_allowed": True,
    }


@runtime_checkable
class Detector(Protocol):
    """Protocol for table detectors."""

    name: str
    version: str

    def detect(self, pdf_path: str, pages: list[int] | None = None) -> list[DetectedRegion]:
        """Return detected table regions for the given PDF."""


class DetectorError(RuntimeError):
    """Raised when a detector fails."""


__all__ = ["DetectedRegion", "Detector", "DetectorError"]
