"""Markdown exporter."""
from __future__ import annotations

from ..models import Table


def table_to_markdown(table: Table, *, fill: str = "repeat") -> str:
    matrix = table.as_matrix(fill=fill)
    if not matrix:
        return ""
    header = matrix[0]
    body = matrix[1:]
    lines = ["| " + " | ".join(_escape(cell) for cell in header) + " |"]
    lines.append("| " + " | ".join(["---"] * len(header)) + " |")
    for row in body:
        lines.append("| " + " | ".join(_escape(cell) for cell in row) + " |")
    return "
".join(lines)


def _escape(value: object) -> str:
    if value is None:
        return ""
    text = str(value)
    return text.replace("|", "\|")


__all__ = ["table_to_markdown"]
