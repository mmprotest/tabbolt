"""Resolve merged cells."""
from __future__ import annotations

from typing import Dict, Iterable

from ..models import Cell
from .grid import CandidateCell, GridStructure


def _has_candidates(
    candidates: Dict[tuple[int, int], CandidateCell],
    row_range: range,
    col_range: range,
    exclude: tuple[int, int],
) -> bool:
    for r in row_range:
        for c in col_range:
            if (r, c) == exclude:
                continue
            if (r, c) in candidates and candidates[(r, c)].text.strip():
                return True
    return False


def apply_merges(
    grid: GridStructure,
    candidates: Iterable[CandidateCell],
) -> list[Cell]:
    """Apply merge inference to produce final cells."""

    candidate_map: Dict[tuple[int, int], CandidateCell] = {
        (cell.row, cell.col): cell for cell in candidates
    }
    has_vertical_lines = any(any(row) for row in grid.vertical_boundaries)
    has_horizontal_lines = any(any(row) for row in grid.horizontal_boundaries)

    n_rows, n_cols = grid.n_rows, grid.n_cols
    consumed = [[False for _ in range(n_cols)] for _ in range(n_rows)]
    resolved: list[Cell] = []

    for row in range(n_rows):
        for col in range(n_cols):
            if consumed[row][col]:
                continue
            candidate = candidate_map.get((row, col))
            text = candidate.text if candidate else ""
            bbox = candidate.bbox if candidate else grid.cell_bbox(row, col)

            row_start = row
            row_end = row
            col_start = col
            col_end = col

            if candidate:
                col_start, col_end = _expand_columns(
                    grid,
                    candidate_map,
                    candidate,
                    has_vertical_lines,
                )
                row_start, row_end = _expand_rows(
                    grid,
                    candidate_map,
                    candidate,
                    col_start,
                    col_end,
                    has_horizontal_lines,
                )
                bbox = (
                    min(grid.col_edges[col_start], candidate.bbox[0]),
                    min(grid.row_edges[row_start], candidate.bbox[1]),
                    max(grid.col_edges[col_end + 1], candidate.bbox[2]),
                    max(grid.row_edges[row_end + 1], candidate.bbox[3]),
                )
            else:
                bbox = grid.cell_bbox(row, col)

            rowspan = row_end - row_start + 1
            colspan = col_end - col_start + 1

            for r in range(row_start, row_end + 1):
                for c in range(col_start, col_end + 1):
                    consumed[r][c] = True

            resolved.append(
                Cell(
                    text=text,
                    bbox=bbox,
                    row=row_start,
                    col=col_start,
                    rowspan=rowspan,
                    colspan=colspan,
                )
            )
    return resolved


def _expand_columns(
    grid: GridStructure,
    candidate_map: Dict[tuple[int, int], CandidateCell],
    candidate: CandidateCell,
    has_vertical_lines: bool,
) -> tuple[int, int]:
    col_start = candidate.col
    col_end = candidate.col

    while col_start > 0:
        boundary_index = col_start - 1
        boundary_present = any(
            grid.vertical_boundaries[r][boundary_index]
            for r in range(candidate.row, candidate.row + 1)
            if boundary_index < len(grid.vertical_boundaries[r])
        )
        reaches = candidate.bbox[0] <= grid.col_edges[col_start] + grid.epsilon
        if boundary_present and not reaches:
            break
        if not has_vertical_lines and not reaches:
            break
        if _has_candidates(
            candidate_map,
            range(candidate.row, candidate.row + 1),
            range(col_start - 1, col_start),
            (candidate.row, candidate.col),
        ):
            break
        col_start -= 1

    while col_end + 1 < grid.n_cols:
        boundary_index = col_end
        boundary_present = any(
            grid.vertical_boundaries[r][boundary_index]
            for r in range(candidate.row, candidate.row + 1)
            if boundary_index < len(grid.vertical_boundaries[r])
        )
        reaches = candidate.bbox[2] >= grid.col_edges[col_end + 1] - grid.epsilon
        if boundary_present and not reaches:
            break
        if not has_vertical_lines and not reaches:
            break
        if _has_candidates(
            candidate_map,
            range(candidate.row, candidate.row + 1),
            range(col_end + 1, col_end + 2),
            (candidate.row, candidate.col),
        ):
            break
        col_end += 1

    return col_start, col_end


def _expand_rows(
    grid: GridStructure,
    candidate_map: Dict[tuple[int, int], CandidateCell],
    candidate: CandidateCell,
    col_start: int,
    col_end: int,
    has_horizontal_lines: bool,
) -> tuple[int, int]:
    row_start = candidate.row
    row_end = candidate.row

    while row_start > 0:
        boundary_index = row_start - 1
        boundary_present = any(
            grid.horizontal_boundaries[boundary_index][c]
            for c in range(col_start, col_end + 1)
            if boundary_index < len(grid.horizontal_boundaries)
        )
        reaches = candidate.bbox[1] <= grid.row_edges[row_start] + grid.epsilon
        if boundary_present and not reaches:
            break
        if not has_horizontal_lines and not reaches:
            break
        if _has_candidates(
            candidate_map,
            range(row_start - 1, row_start),
            range(col_start, col_end + 1),
            (candidate.row, candidate.col),
        ):
            break
        row_start -= 1

    while row_end + 1 < grid.n_rows:
        boundary_index = row_end
        boundary_present = any(
            grid.horizontal_boundaries[boundary_index][c]
            for c in range(col_start, col_end + 1)
            if boundary_index < len(grid.horizontal_boundaries)
        )
        reaches = candidate.bbox[3] >= grid.row_edges[row_end + 1] - grid.epsilon
        if boundary_present and not reaches:
            break
        if not has_horizontal_lines and not reaches:
            break
        if _has_candidates(
            candidate_map,
            range(row_end + 1, row_end + 2),
            range(col_start, col_end + 1),
            (candidate.row, candidate.col),
        ):
            break
        row_end += 1

    return row_start, row_end


__all__ = ["apply_merges"]
