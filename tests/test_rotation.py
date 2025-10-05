from __future__ import annotations

from tabbolt import extract

from .utils_pdf import build_table, write_rotated


def test_rotation(tmp_path):
    data = [
        ["H1", "H2"],
        ["R1", "R2"],
    ]
    table = build_table(data)
    pdf_path = write_rotated(tmp_path / "rotated.pdf", table)
    result = extract(pdf_path)
    assert result.tables
    matrix = result.tables[0].as_matrix(fill="repeat")
    assert matrix[1][0] == "R1"
