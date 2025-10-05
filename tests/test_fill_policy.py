from __future__ import annotations

from tabbolt import extract
from tabbolt.export import table_to_csv

from .utils_pdf import build_table, write_pdf


def test_fill_policy(tmp_path):
    data = [["Merged", "", "Solo"], ["A1", "B1", "C1"]]
    pdf_path = write_pdf(tmp_path / "fill.pdf", [build_table(data, spans=[(0, 0, 0, 1)])])
    table = extract(pdf_path).tables[0]

    csv_repeat = table_to_csv(table, fill_policy="repeat")
    assert "Merged" in csv_repeat

    csv_empty = table_to_csv(table, fill_policy="empty")
    assert ",," in csv_empty

    csv_sentinel = table_to_csv(table, fill_policy="sentinel", sentinel="X")
    assert "X" in csv_sentinel
