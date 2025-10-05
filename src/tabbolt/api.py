"""Public API for TabBolt."""
from __future__ import annotations

from pathlib import Path
from typing import Sequence

import pdfplumber

from .detect.base import Detector
from .geometry import snap_epsilon
from .models import DocResult, Table
from .plugins.entrypoints import get_detector
from .resolve import apply_merges, build_grid, stitch_tables


def extract(
    pdf_path: str | Path,
    *,
    pages: Sequence[int] | None = None,
    detector: str | Detector | None = None,
    stitch_aggressiveness: str = "med",
) -> DocResult:
    """Extract tables from ``pdf_path``."""

    pdf_path = str(Path(pdf_path))
    detector_obj = _resolve_detector(detector)
    page_filter = sorted(set(int(p) for p in pages)) if pages else None
    detections = detector_obj.detect(pdf_path, pages=page_filter)

    tables: list[Table] = []
    warnings: list[str] = []

    with pdfplumber.open(pdf_path) as pdf:
        for region in detections:
            page_index = region.page - 1
            if page_index < 0 or page_index >= len(pdf.pages):
                warnings.append(f"Region {region.page} out of bounds")
                continue
            page = pdf.pages[page_index]
            if getattr(page, "rotation", 0):
                page = page.rotate(-page.rotation)
            words = page.extract_words(extra_attrs=["size"], keep_blank_chars=False)
            region_words = [word for word in words if _overlaps(_word_bbox(word), region.bbox)]
            heights = [float(word["bottom"]) - float(word["top"]) for word in region_words]
            epsilon = snap_epsilon(heights)
            grid, candidate_cells = build_grid(region_words, region.bbox, region.lines, epsilon)
            cells = apply_merges(grid, candidate_cells)
            table = Table(
                page=[region.page],
                cells=cells,
                n_rows=grid.n_rows,
                n_cols=grid.n_cols,
                conf=region.conf,
                meta={"detector_version": region.detector_version, "epsilon": epsilon},
                page_size=(page.width, page.height),
            )
            table.sort_cells()
            tables.append(table)

    stitched = stitch_tables(tables, aggressiveness=stitch_aggressiveness)
    stats = {
        "detector": detector_obj.name,
        "regions": len(detections),
        "tables": len(stitched),
    }
    return DocResult(tables=stitched, stats=stats, warnings=warnings)


def _word_bbox(word: dict[str, float]) -> tuple[float, float, float, float]:
    return (
        float(min(word["x0"], word["x1"])),
        float(min(word["top"], word["bottom"])),
        float(max(word["x0"], word["x1"])),
        float(max(word["top"], word["bottom"])),
    )


def _overlaps(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    return not (ax1 < bx0 or ax0 > bx1 or ay1 < by0 or ay0 > by1)


def _resolve_detector(detector: str | Detector | None) -> Detector:
    if detector is None:
        return get_detector("plumber")
    if isinstance(detector, str):
        return get_detector(detector)
    return detector


__all__ = ["extract"]
