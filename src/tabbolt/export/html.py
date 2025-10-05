"""HTML exporter for TabBolt tables."""
from __future__ import annotations

from html import escape
from typing import Iterable

from ..models import Table


def table_to_html(table: Table, *, inline_styles: bool = True) -> str:
    table.sort_cells()
    matrix = _build_cell_matrix(table)
    style_attr = ''
    if inline_styles:
        style_attr = ' style="border-collapse:collapse;border:1px solid #666;font-family:monospace;"'
    lines = [f'<table{style_attr}>']
    for row in matrix:
        lines.append('  <tr>')
        for cell in row:
            if cell is None:
                continue
            attrs = []
            if cell.rowspan > 1:
                attrs.append(f'rowspan="{cell.rowspan}"')
            if cell.colspan > 1:
                attrs.append(f'colspan="{cell.colspan}"')
            cell_style = 'padding:4px;border:1px solid #999;' if inline_styles else ''
            if cell_style:
                attrs.append(f'style="{cell_style}"')
            attrs_str = (' ' + ' '.join(attrs)) if attrs else ''
            lines.append(f'    <td{attrs_str}>{escape(cell.text)}</td>')
        lines.append('  </tr>')
    lines.append('</table>')
    return '
'.join(lines)


def tables_to_html(tables: Iterable[Table], *, inline_styles: bool = True) -> str:
    return '

'.join(table_to_html(table, inline_styles=inline_styles) for table in tables)


def _build_cell_matrix(table: Table) -> list[list[object | None]]:
    matrix: list[list[object | None]] = [[None for _ in range(table.n_cols)] for _ in range(table.n_rows)]
    for cell in table.cells:
        for r in range(cell.row, cell.row + cell.rowspan):
            for c in range(cell.col, cell.col + cell.colspan):
                if (r, c) == (cell.row, cell.col):
                    matrix[r][c] = cell
                else:
                    matrix[r][c] = None
    return matrix


__all__ = ["table_to_html", "tables_to_html"]
