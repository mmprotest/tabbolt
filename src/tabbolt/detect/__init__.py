"""Detector implementations."""
from .base import Detector, DetectedRegion
from .plumber import PlumberDetector

__all__ = ["Detector", "DetectedRegion", "PlumberDetector"]
