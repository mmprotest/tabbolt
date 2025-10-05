"""TabBolt package initialization."""
from __future__ import annotations

from importlib import metadata

from .api import extract
from .models import Cell, DocResult, Table

try:
    __version__ = metadata.version("tabbolt")
except metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = "0.1.0"

__all__ = ["extract", "Cell", "Table", "DocResult", "__version__"]
