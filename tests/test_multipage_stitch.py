from __future__ import annotations

from tabbolt import extract

from .utils_pdf import build_table, write_multipage


def test_multipage_stitch(tmp_path):
    header = ["Item", "Qty", "Price"]
    rows_first = [["Item 1", "1", "$10"], ["Item 2", "2", "$20"]]
    rows_second = [["Item 3", "3", "$30"], ["Item 4", "4", "$40"]]
    table1 = build_table([header] + rows_first)
    table2 = build_table([header] + rows_second)
    pdf_path = write_multipage(tmp_path / "multi.pdf", table1, table2)
    result = extract(pdf_path, stitch_aggressiveness="high")
    assert len(result.tables) == 1
    stitched = result.tables[0]
    assert stitched.n_rows == 1 + len(rows_first) + len(rows_second)
    matrix = stitched.as_matrix(fill="repeat")
    assert matrix[1][0] == "Item 1"
    assert matrix[-1][-1] == "$40"
