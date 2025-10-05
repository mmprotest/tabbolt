"""Default pdfplumber-based detector."""
from __future__ import annotations

from typing import Iterable

import pdfplumber
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

from ..geometry import RotatedPage, expand_bbox, merge_boxes, rotation_from_chars, snap_epsilon
from ..models import BBox
from .base import DetectedRegion


class PlumberDetector:
    """Detector that relies on pdfplumber text boxes."""

    name = "plumber"
    version = "1.0"

    def detect(self, pdf_path: str, pages: list[int] | None = None) -> list[DetectedRegion]:
        selected = set(pages or [])
        results: list[DetectedRegion] = []
        with pdfplumber.open(pdf_path) as pdf:
            for index, page in enumerate(pdf.pages, start=1):
                if selected and index not in selected:
                    continue
                chars = page.chars
                if not chars:
                    continue
                rot = rotation_from_chars(chars, page.width, page.height)
                padding = snap_epsilon([float(c.get("size", 10.0)) for c in chars]) * 1.5
                char_boxes = [
                    box(
                        float(min(c["x0"], c["x1"])) - padding,
                        float(min(c["top"], c["bottom"])) - padding,
                        float(max(c["x0"], c["x1"])) + padding,
                        float(max(c["top"], c["bottom"])) + padding,
                    )
                    for c in chars
                ]
                clusters = self._clusters(char_boxes)
                raw_lines = list(getattr(page, "lines", [])) + list(getattr(page, "rects", []))
                line_boxes = [
                    self._normalize_line(line, rot)
                    for line in raw_lines
                ]
                for cluster in clusters:
                    x0, y0, x1, y1 = cluster.bounds
                    region_bbox = (float(x0), float(y0), float(x1), float(y1))
                    region_lines = [lb for lb in line_boxes if self._overlaps(lb, region_bbox)]
                    region_chars = [
                        (
                            float(min(c["x0"], c["x1"])),
                            float(min(c["top"], c["bottom"])),
                            float(max(c["x0"], c["x1"])),
                            float(max(c["top"], c["bottom"])),
                        )
                        for c in chars
                        if self._overlaps(
                            (
                                float(min(c["x0"], c["x1"])),
                                float(min(c["top"], c["bottom"])),
                                float(max(c["x0"], c["x1"])),
                                float(max(c["top"], c["bottom"])),
                            ),
                            region_bbox,
                        )
                    ]
                    merged_bbox = merge_boxes(region_chars) if region_chars else region_bbox
                    expanded = expand_bbox(merged_bbox, padding * 0.3)
                    results.append(
                        DetectedRegion(
                            page=index,
                            bbox=expanded,
                            lines=region_lines,
                            boxes=region_chars,
                            conf=0.8,
                            detector_version=self.version,
                        )
                    )
        return results

    def _clusters(self, char_boxes: Iterable[Polygon]) -> list[Polygon]:
        union = unary_union(list(char_boxes))
        if union.is_empty:
            return []
        if union.geom_type == "Polygon":
            return [union]
        return list(union.geoms)

    def _normalize_line(self, line: dict[str, float], rot: RotatedPage) -> BBox:
        x0 = float(line.get("x0", line.get("x1", 0.0)))
        x1 = float(line.get("x1", line.get("x0", 0.0)))
        top = float(line.get("top", line.get("y0", 0.0)))
        bottom = float(line.get("bottom", line.get("y1", 0.0)))
        x0, top = rot.unrotate_point(x0, top)
        x1, bottom = rot.unrotate_point(x1, bottom)
        x_min, x_max = sorted([x0, x1])
        y_min, y_max = sorted([top, bottom])
        return (x_min, y_min, x_max, y_max)

    def _overlaps(self, bbox: BBox, region: BBox) -> bool:
        ax0, ay0, ax1, ay1 = bbox
        bx0, by0, bx1, by1 = region
        return not (ax1 < bx0 or ax0 > bx1 or ay1 < by0 or ay0 > by1)


__all__ = ["PlumberDetector"]
