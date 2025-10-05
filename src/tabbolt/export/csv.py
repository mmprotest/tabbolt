"""CSV exporter."""
from __future__ import annotations

import csv
from io import StringIO

from ..models import Table


def table_to_csv(
    table: Table,
    *,
    fill_policy: str = "repeat",
    sentinel: str = "<MERGED>",
) -> str:
    if fill_policy not in {"repeat", "empty", "sentinel"}:
        raise ValueError(f"Unknown fill policy: {fill_policy}")
    fill = ""
    if fill_policy == "repeat":
        fill = "repeat"
    elif fill_policy == "empty":
        fill = "empty"
    elif fill_policy == "sentinel":
        fill = sentinel
    matrix = table.as_matrix(fill=fill)
    buffer = StringIO()
    writer = csv.writer(buffer)
    for row in matrix:
        writer.writerow(row)
    return buffer.getvalue()


__all__ = ["table_to_csv"]
