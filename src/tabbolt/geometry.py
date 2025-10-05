"""Geometry helpers for table inference."""
from __future__ import annotations

from dataclasses import dataclass
from math import atan2, cos, pi, sin
from typing import Iterable, Sequence

import numpy as np
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

from .models import BBox


@dataclass(frozen=True)
class RotatedPage:
    angle: float
    width: float
    height: float

    def unrotate_point(self, x: float, y: float) -> tuple[float, float]:
        """Rotate a point into the canonical orientation."""

        if abs(self.angle) < 1e-3:
            return x, y
        # rotate around center
        cx, cy = self.width / 2.0, self.height / 2.0
        x0, y0 = x - cx, y - cy
        xr = x0 * cos(-self.angle) - y0 * sin(-self.angle)
        yr = x0 * sin(-self.angle) + y0 * cos(-self.angle)
        return xr + cx, yr + cy

    def unrotate_bbox(self, bbox: BBox) -> BBox:
        x0, y0, x1, y1 = bbox
        points = [
            self.unrotate_point(x0, y0),
            self.unrotate_point(x0, y1),
            self.unrotate_point(x1, y0),
            self.unrotate_point(x1, y1),
        ]
        xs, ys = zip(*points)
        return min(xs), min(ys), max(xs), max(ys)


def infer_rotation(char_angles: Sequence[float]) -> float:
    """Infer the dominant page rotation from character angles."""

    if not char_angles:
        return 0.0
    angles = np.array([a % 360 for a in char_angles], dtype=float)
    buckets = {0: 0, 90: 0, 180: 0, 270: 0}
    for angle in angles:
        nearest = min(buckets, key=lambda b: min(abs(angle - b), abs(angle - b + 360)))
        buckets[nearest] += 1
    dominant = max(buckets, key=buckets.get)
    return dominant * pi / 180


def rotation_from_chars(chars: Sequence[dict[str, float]], page_width: float, page_height: float) -> RotatedPage:
    angles = [float(char.get("angle", 0.0)) for char in chars if "angle" in char]
    angle = infer_rotation(angles)
    return RotatedPage(angle=angle, width=page_width, height=page_height)


def snap_epsilon(char_heights: Sequence[float]) -> float:
    """Compute an adaptive snapping epsilon based on character heights."""

    if not char_heights:
        return 1.0
    arr = np.array(char_heights, dtype=float)
    median = float(np.median(arr))
    mad = float(np.median(np.abs(arr - median))) or median * 0.1
    return max(0.5, mad * 0.8)


def snap_values(values: Sequence[float], epsilon: float) -> list[float]:
    """Snap a sequence of values into a sorted unique list."""

    if not values:
        return []
    sorted_vals = sorted(values)
    snapped: list[float] = [sorted_vals[0]]
    for value in sorted_vals[1:]:
        if abs(value - snapped[-1]) <= epsilon:
            snapped[-1] = (snapped[-1] + value) / 2.0
        else:
            snapped.append(value)
    return snapped


def expand_bbox(bbox: BBox, padding: float) -> BBox:
    x0, y0, x1, y1 = bbox
    return x0 - padding, y0 - padding, x1 + padding, y1 + padding


def merge_boxes(boxes: Iterable[BBox]) -> BBox:
    shapely_boxes = [box(*b) for b in boxes]
    merged = unary_union(shapely_boxes)
    if merged.geom_type == "Polygon":
        minx, miny, maxx, maxy = merged.bounds
    else:
        minx, miny, maxx, maxy = merged.envelope.bounds
    return float(minx), float(miny), float(maxx), float(maxy)


def bbox_area(bbox: BBox) -> float:
    x0, y0, x1, y1 = bbox
    return max(0.0, (x1 - x0)) * max(0.0, (y1 - y0))


def intersection_over_union(a: BBox, b: BBox) -> float:
    poly_a = box(*a)
    poly_b = box(*b)
    inter = poly_a.intersection(poly_b).area
    union = poly_a.union(poly_b).area
    if union == 0:
        return 0.0
    return float(inter / union)


__all__ = [
    "RotatedPage",
    "rotation_from_chars",
    "snap_epsilon",
    "snap_values",
    "expand_bbox",
    "merge_boxes",
    "bbox_area",
    "intersection_over_union",
]
