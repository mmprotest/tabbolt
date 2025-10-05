from __future__ import annotations

from tabbolt import extract

from .utils_pdf import build_table, write_pdf


def test_table_without_lines(tmp_path):
    data = [
        ["A", "B", "C"],
        ["1", "2", "3"],
    ]
    pdf_path = write_pdf(tmp_path / "nolines.pdf", [build_table(data, grid=False)])
    table = extract(pdf_path).tables[0]
    assert table.as_matrix(fill="repeat")[1][2] == "3"
