"""Table stitching utilities."""
from __future__ import annotations

from typing import Sequence

from ..models import Cell, Table


def stitch_tables(tables: Sequence[Table], aggressiveness: str = "med") -> list[Table]:
    """Stitch tables that continue across pages."""

    if not tables:
        return []
    tolerance = {
        "low": 0.01,
        "med": 0.015,
        "high": 0.025,
    }.get(aggressiveness, 0.015)

    ordered = sorted(tables, key=lambda t: (min(t.page) if t.page else 0, t.page))
    stitched: list[Table] = []
    for table in ordered:
        table.sort_cells()
        if not stitched:
            stitched.append(table)
            continue
        prev = stitched[-1]
        if _should_join(prev, table, tolerance):
            stitched[-1] = _merge_tables(prev, table)
        else:
            stitched.append(table)
    return stitched


def _should_join(first: Table, second: Table, tolerance: float) -> bool:
    if first.n_cols != second.n_cols:
        return False
    width_a = _table_width(first)
    width_b = _table_width(second)
    if not width_a or not width_b:
        return False
    width_diff = abs(width_a - width_b) / max(width_a, width_b)
    if width_diff > tolerance:
        return False
    if _row_signature(first, 0) != _row_signature(second, 0):
        return False
    return True


def _table_width(table: Table) -> float:
    if not table.cells:
        return 0.0
    x0 = min(cell.bbox[0] for cell in table.cells)
    x1 = max(cell.bbox[2] for cell in table.cells)
    return x1 - x0


def _row_signature(table: Table, row: int) -> tuple[str, ...]:
    row_cells = [cell for cell in table.cells if cell.row == row]
    if not row_cells:
        return ()
    row_cells.sort(key=lambda cell: cell.col)
    return tuple(cell.text.strip() for cell in row_cells)


def _merge_tables(first: Table, second: Table) -> Table:
    drop_rows = 0
    if _row_signature(first, 0) == _row_signature(second, 0):
        drop_rows = 1
    offset = first.n_rows
    new_cells: list[Cell] = [cell for cell in first.cells]
    for cell in second.cells:
        if cell.row < drop_rows:
            continue
        updated = cell.model_copy(
            update={
                "row": cell.row - drop_rows + offset,
            },
        )
        new_cells.append(updated)
    pages = sorted(set(first.page + second.page))
    n_rows = first.n_rows + second.n_rows - drop_rows
    stitched = Table(
        page=pages,
        cells=new_cells,
        n_rows=n_rows,
        n_cols=first.n_cols,
        title=first.title or second.title,
        conf=min(first.conf, second.conf),
        meta={**second.meta, **first.meta},
        units=first.units,
        page_size=first.page_size or second.page_size,
    )
    stitched.sort_cells()
    return stitched


__all__ = ["stitch_tables"]
