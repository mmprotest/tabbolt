"""Debug overlay rendering."""
from __future__ import annotations

from html import escape

from ..models import Table


def render_overlay(
    table: Table,
    *,
    epsilon: float,
    detector: str,
    scale: float = 1.0,
) -> str:
    """Render an SVG overlay for the table."""

    width = table.page_size[0] if table.page_size else max(cell.bbox[2] for cell in table.cells)
    height = table.page_size[1] if table.page_size else max(cell.bbox[3] for cell in table.cells)
    svg_width = width * scale
    svg_height = height * scale
    elements = []
    for idx, cell in enumerate(table.cells):
        x0, y0, x1, y1 = cell.bbox
        rect = (
            f'<rect x="{x0*scale:.2f}" y="{(height - y1)*scale:.2f}" '
            f'width="{(x1 - x0)*scale:.2f}" height="{(y1 - y0)*scale:.2f}" '
            f'fill="rgba(0, 128, 255, 0.15)" stroke="rgba(0, 128, 255, 0.7)"/>'
        )
        elements.append(rect)
        text = escape(cell.text)
        elements.append(
            f'<text x="{(x0 + 2)*scale:.2f}" y="{(height - y0 - 2)*scale:.2f}" '
            f'font-size="10" fill="#003366">{text}</text>'
        )
    legend = (
        f'<g transform="translate(10,{svg_height - 60:.2f})">'
        f'<rect width="260" height="50" fill="white" stroke="#999"/>'
        f'<text x="10" y="20" font-size="12">Detector: {escape(detector)}</text>'
        f'<text x="10" y="35" font-size="12">Cells: {len(table.cells)}</text>'
        f'<text x="10" y="48" font-size="12">Epsilon: {epsilon:.2f}</text>'
        f'</g>'
    )
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width:.2f}" height="{svg_height:.2f}" '
        f'viewBox="0 0 {width:.2f} {height:.2f}">' + "".join(elements) + legend + '</svg>'
    )
    return (
        '<!DOCTYPE html><html><head><meta charset="utf-8"><title>TabBolt Overlay</title>'
        '<style>body{background:#f9f9f9;font-family:monospace;}</style>'
        '</head><body>'
        f'{svg}'
        '</body></html>'
    )


__all__ = ["render_overlay"]
