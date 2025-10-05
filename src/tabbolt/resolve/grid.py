"""Grid inference utilities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable

from ..geometry import snap_values
from ..models import BBox


@dataclass
class CandidateCell:
    row: int
    col: int
    text: str
    bbox: BBox


@dataclass
class GridStructure:
    row_edges: list[float]
    col_edges: list[float]
    vertical_boundaries: list[list[bool]]  # rows x (cols-1)
    horizontal_boundaries: list[list[bool]]  # (rows-1) x cols
    epsilon: float

    @property
    def n_rows(self) -> int:
        return max(1, len(self.row_edges) - 1)

    @property
    def n_cols(self) -> int:
        return max(1, len(self.col_edges) - 1)

    def cell_bbox(self, row: int, col: int) -> BBox:
        return (
            self.col_edges[col],
            self.row_edges[row],
            self.col_edges[col + 1],
            self.row_edges[row + 1],
        )


def _centers_to_edges(centers: list[float], min_edge: float, max_edge: float) -> list[float]:
    if not centers:
        return [min_edge, max_edge]
    centers = sorted(centers)
    edges = [min_edge]
    for left, right in zip(centers, centers[1:]):
        edges.append((left + right) / 2.0)
    edges.append(max_edge)
    return edges


def _classify_lines(lines: Iterable[BBox]) -> tuple[list[BBox], list[BBox]]:
    vertical: list[BBox] = []
    horizontal: list[BBox] = []
    for line in lines:
        x0, y0, x1, y1 = line
        width = abs(x1 - x0)
        height = abs(y1 - y0)
        normalized = (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))
        if width <= height:
            vertical.append(normalized)
        else:
            horizontal.append(normalized)
    return vertical, horizontal


def _line_covers_vertical(line: BBox, x: float, y0: float, y1: float, epsilon: float) -> bool:
    lx0, ly0, lx1, ly1 = line
    if not (min(lx0, lx1) - epsilon <= x <= max(lx0, lx1) + epsilon):
        return False
    cover_low = min(ly0, ly1) - epsilon
    cover_high = max(ly0, ly1) + epsilon
    return cover_low <= y0 and cover_high >= y1


def _line_covers_horizontal(line: BBox, y: float, x0: float, x1: float, epsilon: float) -> bool:
    lx0, ly0, lx1, ly1 = line
    if not (min(ly0, ly1) - epsilon <= y <= max(ly0, ly1) + epsilon):
        return False
    cover_low = min(lx0, lx1) - epsilon
    cover_high = max(lx0, lx1) + epsilon
    return cover_low <= x0 and cover_high >= x1


def build_grid(
    words: list[dict[str, float]],
    region_bbox: BBox,
    lines: Iterable[BBox],
    epsilon: float,
) -> tuple[GridStructure, list[CandidateCell]]:
    """Infer a grid from words and vector lines."""

    x0, y0, x1, y1 = region_bbox
    centers_y = [
        (float(min(w["top"], w["bottom"])) + float(max(w["top"], w["bottom"]))) / 2.0
        for w in words
    ]
    centers_x = [
        (float(min(w["x0"], w["x1"])) + float(max(w["x0"], w["x1"]))) / 2.0
        for w in words
    ]
    row_centers = snap_values(centers_y, epsilon)
    col_centers = snap_values(centers_x, epsilon)

    row_edges = _centers_to_edges(row_centers, float(y0), float(y1))
    col_edges = _centers_to_edges(col_centers, float(x0), float(x1))

    vertical_lines, horizontal_lines = _classify_lines(lines)

    vertical_boundaries: list[list[bool]] = []
    for row_idx in range(max(1, len(row_edges) - 1)):
        row_low, row_high = row_edges[row_idx], row_edges[row_idx + 1]
        row_marks: list[bool] = []
        for col_idx in range(1, max(1, len(col_edges) - 1)):
            boundary_x = col_edges[col_idx]
            present = any(
                _line_covers_vertical(line, boundary_x, row_low, row_high, epsilon)
                for line in vertical_lines
            )
            row_marks.append(present)
        vertical_boundaries.append(row_marks)

    horizontal_boundaries: list[list[bool]] = []
    for row_idx in range(1, max(1, len(row_edges) - 1)):
        boundary_y = row_edges[row_idx]
        row_marks = []
        for col_idx in range(max(1, len(col_edges) - 1)):
            col_low, col_high = col_edges[col_idx], col_edges[col_idx + 1]
            present = any(
                _line_covers_horizontal(line, boundary_y, col_low, col_high, epsilon)
                for line in horizontal_lines
            )
            row_marks.append(present)
        horizontal_boundaries.append(row_marks)

    grid = GridStructure(
        row_edges=row_edges,
        col_edges=col_edges,
        vertical_boundaries=vertical_boundaries,
        horizontal_boundaries=horizontal_boundaries,
        epsilon=epsilon,
    )

    agg: Dict[tuple[int, int], dict[str, object]] = {}
    for word in words:
        wx0 = float(min(word["x0"], word["x1"]))
        wx1 = float(max(word["x0"], word["x1"]))
        wy0 = float(min(word["top"], word["bottom"]))
        wy1 = float(max(word["top"], word["bottom"]))
        cx = (wx0 + wx1) / 2.0
        cy = (wy0 + wy1) / 2.0
        row = _locate_edge(grid.row_edges, cy, grid.epsilon)
        col = _locate_edge(grid.col_edges, cx, grid.epsilon)
        key = (row, col)
        bucket = agg.setdefault(
            key,
            {
                "texts": [],
                "bbox": [wx0, wy0, wx1, wy1],
            },
        )
        bucket["texts"].append((cx, str(word["text"])) )
        bbox = bucket["bbox"]
        bbox[0] = min(bbox[0], wx0)
        bbox[1] = min(bbox[1], wy0)
        bbox[2] = max(bbox[2], wx1)
        bbox[3] = max(bbox[3], wy1)

    candidate_cells: list[CandidateCell] = []
    for (row, col), bucket in agg.items():
        texts = " ".join(t for _, t in sorted(bucket["texts"], key=lambda item: item[0])).strip()
        bx0, by0, bx1, by1 = bucket["bbox"]
        candidate_cells.append(
            CandidateCell(
                row=row,
                col=col,
                text=texts,
                bbox=(bx0, by0, bx1, by1),
            )
        )

    return grid, candidate_cells


def _locate_edge(edges: list[float], value: float, epsilon: float) -> int:
    if len(edges) < 2:
        return 0
    clamped = min(max(value, edges[0] - epsilon), edges[-1] + epsilon)
    for idx in range(len(edges) - 1):
        if edges[idx] - epsilon <= clamped <= edges[idx + 1] + epsilon:
            return idx
    return max(0, min(len(edges) - 2, len(edges) // 2))


__all__ = ["GridStructure", "CandidateCell", "build_grid"]
