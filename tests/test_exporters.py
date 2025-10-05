from __future__ import annotations

import pandas as pd

from tabbolt import extract
from tabbolt.export import table_to_csv, table_to_dataframe, table_to_html, table_to_markdown

from .utils_pdf import build_table, write_pdf


def test_exporters(tmp_path):
    data = [["Merged", "", "Solo"], ["A1", "B1", "C1"]]
    pdf_path = write_pdf(tmp_path / "export.pdf", [build_table(data, spans=[(0, 0, 0, 1)])])
    table = extract(pdf_path).tables[0]

    html = table_to_html(table)
    assert 'colspan="2"' in html

    csv_data = table_to_csv(table, fill_policy="sentinel", sentinel="<S>")
    assert "<S>" in csv_data

    md = table_to_markdown(table)
    assert md.splitlines()[0].startswith("|")

    df = table_to_dataframe(table)
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (table.n_rows, table.n_cols)

    tidy = table_to_dataframe(table, tidy=True)
    assert set(tidy.columns) == {"row", "col", "value"}
