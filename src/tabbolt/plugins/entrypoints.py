"""Plugin discovery utilities."""
from __future__ import annotations

from importlib import metadata
from typing import Dict

from ..detect import Detector, PlumberDetector

_CACHE: Dict[str, Detector] = {}


def available_detectors() -> dict[str, Detector]:
    registry: dict[str, Detector] = {"plumber": PlumberDetector()}
    try:
        entries = metadata.entry_points(group="tabbolt.detectors")
    except Exception:  # pragma: no cover - Python <3.10 fallback
        entries = []
    for entry in entries:
        name = entry.name
        if name in registry:
            continue
        detector = entry.load()
        if callable(detector):
            detector = detector()
        registry[name] = detector
    return registry


def get_detector(name: str) -> Detector:
    if name in _CACHE:
        return _CACHE[name]
    registry = available_detectors()
    if name not in registry:
        raise KeyError(f"Unknown detector: {name}")
    _CACHE[name] = registry[name]
    return registry[name]


__all__ = ["available_detectors", "get_detector"]
