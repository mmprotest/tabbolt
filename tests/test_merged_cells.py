from __future__ import annotations

from tabbolt import extract

from .utils_pdf import build_table, write_pdf


def test_merged_cells(tmp_path):
    data = [
        ["Merged", "", "Solo"],
        ["A1", "B1", "C1"],
    ]
    spans = [(0, 0, 0, 1)]
    pdf_path = write_pdf(tmp_path / "merged.pdf", [build_table(data, spans=spans)])
    result = extract(pdf_path)
    table = result.tables[0]
    merged_cell = next(cell for cell in table.cells if cell.text == "Merged")
    assert merged_cell.colspan == 2
    matrix = table.as_matrix(fill="repeat")
    assert matrix[0][0] == "Merged"
    assert matrix[0][1] == "Merged"
