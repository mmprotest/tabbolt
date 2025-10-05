from __future__ import annotations

from tabbolt import extract
from tabbolt.export import table_to_html

from .utils_pdf import build_table, write_pdf


def test_basic_table(tmp_path):
    data = [
        ["Header 1", "Header 2", "Header 3"],
        ["R1C1", "R1C2", "R1C3"],
        ["R2C1", "R2C2", "R2C3"],
    ]
    pdf_path = write_pdf(tmp_path / "basic.pdf", [build_table(data)])
    result = extract(pdf_path)
    assert len(result.tables) == 1
    table = result.tables[0]
    assert table.n_rows == 3
    assert table.n_cols == 3
    assert table.as_matrix(fill="repeat") == data
    html = table_to_html(table)
    assert "Header 1" in html
