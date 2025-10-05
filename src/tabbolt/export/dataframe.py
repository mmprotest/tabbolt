"""DataFrame exporters."""
from __future__ import annotations

import pandas as pd

from ..models import Table


def table_to_dataframe(table: Table, *, tidy: bool = False, fill: str = "repeat") -> pd.DataFrame:
    matrix = table.as_matrix(fill=fill)
    df = pd.DataFrame(matrix)
    if not tidy:
        return df
    tidy_rows = []
    for r, row in enumerate(matrix):
        for c, value in enumerate(row):
            tidy_rows.append({"row": r, "col": c, "value": value})
    return pd.DataFrame(tidy_rows)


__all__ = ["table_to_dataframe"]
