from __future__ import annotations

from tabbolt import extract

from .utils_pdf import build_table, write_pdf


def test_ragged_columns(tmp_path):
    data = [
        ["A", "B", "C", "D"],
        ["1", "2", "", ""],
        ["3", "", "", ""],
    ]
    pdf_path = write_pdf(tmp_path / "ragged.pdf", [build_table(data)])
    table = extract(pdf_path).tables[0]
    matrix = table.as_matrix(fill="repeat")
    assert matrix[2][0] == "3"
    assert matrix[1][2] == ""
