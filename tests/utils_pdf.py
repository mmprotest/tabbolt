"""Utilities for generating synthetic PDFs."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import PageBreak, SimpleDocTemplate, Table, TableStyle


def build_table(data: Sequence[Sequence[str]], spans: Iterable[tuple[int, int, int, int]] | None = None, grid: bool = True) -> Table:
    table = Table(data, repeatRows=1)
    style = [
        ("FONT", (0, 0), (-1, -1), "Helvetica", 10),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]
    if grid:
        style.append(("GRID", (0, 0), (-1, -1), 0.5, colors.black))
    if spans:
        for row0, col0, row1, col1 in spans:
            style.append(("SPAN", (col0, row0), (col1, row1)))
    table.setStyle(TableStyle(style))
    return table


def write_pdf(path: Path, tables: Sequence[Table], *, page_size=letter) -> Path:
    doc = SimpleDocTemplate(str(path), pagesize=page_size)
    doc.build(list(tables))
    return path


def write_multipage(path: Path, first: Table, second: Table, *, page_size=letter) -> Path:
    doc = SimpleDocTemplate(str(path), pagesize=page_size)
    doc.build([first, PageBreak(), second])
    return path


def write_rotated(path: Path, table: Table, *, page_size=letter) -> Path:
    width, height = page_size
    c = canvas.Canvas(str(path), pagesize=page_size)
    c.saveState()
    c.translate(0, height)
    c.rotate(-90)
    table.wrapOn(c, height, width)
    table.drawOn(c, 40, 40)
    c.restoreState()
    c.showPage()
    c.save()
    return path


__all__ = ["build_table", "write_pdf", "write_multipage", "write_rotated"]
