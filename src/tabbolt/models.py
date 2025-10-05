"""Data models for TabBolt."""
from __future__ import annotations

from typing import Any, ClassVar, Iterable, List, Sequence

from pydantic import BaseModel, Field, computed_field

try:  # pragma: no cover - optional dependency
    import orjson
except Exception:  # pragma: no cover - fallback when optional dep missing
    orjson = None  # type: ignore[assignment]

BBox = tuple[float, float, float, float]


class Cell(BaseModel):
    """A single table cell."""

    text: str
    bbox: BBox
    row: int
    col: int
    rowspan: int = 1
    colspan: int = 1
    conf: float = 1.0

    model_config = {
        "arbitrary_types_allowed": True,
        "frozen": True,
    }


class Table(BaseModel):
    """Structured table representation."""

    page: list[int] = Field(default_factory=list)
    cells: list[Cell]
    n_rows: int
    n_cols: int
    title: str | None = None
    conf: float = 1.0
    meta: dict[str, Any] = Field(default_factory=dict)
    units: str = "pt"
    page_size: tuple[float, float] | None = None
    schema_version: ClassVar[str] = "1.0"

    @computed_field
    @property
    def schema(self) -> str:
        return self.schema_version

    def to_json(self, *, indent: int | None = None) -> str:
        """Serialize the table to JSON using orjson when available."""

        data = self.model_dump(mode="json")
        if orjson is not None:
            option = orjson.OPT_INDENT_2 if indent else 0
            return orjson.dumps(data, option=option).decode()
        import json

        return json.dumps(data, indent=indent)

    def as_matrix(self, *, fill: str | Any = "") -> list[list[Any]]:
        """Return the table as a 2D matrix.

        Parameters
        ----------
        fill:
            How to fill empty cells. ``"repeat"`` repeats source text across
            spans, ``"sentinel"`` fills with ``None``.
        """

        matrix: list[list[Any]] = [["" for _ in range(self.n_cols)] for _ in range(self.n_rows)]
        for cell in self.cells:
            value: Any
            if fill == "sentinel":
                value = None
            elif fill == "repeat":
                value = cell.text
            else:
                value = fill
            for r in range(cell.row, cell.row + cell.rowspan):
                for c in range(cell.col, cell.col + cell.colspan):
                    if fill == "repeat" and (r, c) == (cell.row, cell.col):
                        matrix[r][c] = cell.text
                    elif fill == "repeat":
                        matrix[r][c] = cell.text
                    elif fill == "empty":
                        matrix[r][c] = ""
                    else:
                        matrix[r][c] = value
            # ensure top-left always text
            matrix[cell.row][cell.col] = cell.text
        return matrix

    def sort_cells(self) -> None:
        self.cells.sort(key=lambda c: (c.row, c.col))


class DocResult(BaseModel):
    """Extraction result for a document."""

    tables: list[Table]
    stats: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)

    def to_json(self, *, indent: int | None = None) -> str:
        data = self.model_dump(mode="json")
        if orjson is not None:
            option = orjson.OPT_INDENT_2 if indent else 0
            return orjson.dumps(data, option=option).decode()
        import json

        return json.dumps(data, indent=indent)

    def as_matrices(self, *, fill: str | Any = "") -> list[list[list[Any]]]:
        return [table.as_matrix(fill=fill) for table in self.tables]


__all__ = ["Cell", "Table", "DocResult", "BBox"]
