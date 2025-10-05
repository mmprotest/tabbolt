# tabbolt

TabBolt is a batteries-included PDF table extractor that handles tricky page layouts, spanning headers, and multi-page tables without any network access. The project combines pdfplumber's robust text extraction with carefully tuned geometric heuristics to infer grid structure, merged cells, and repeating headers. Optional machine learning detectors can be plugged in for even more recall, but the default experience is fully offline and deterministic.

## Features

- ✅ Accurate extraction of tables with merged or spanning cells
- ✅ Automatic header carry-over when tables continue across pages
- ✅ Multi-page table stitching using geometric similarity heuristics
- ✅ Python API returning strongly typed [Pydantic](https://docs.pydantic.dev/) models
- ✅ Command line interface for batch extraction and rich exports
- ✅ Optional ML detector plugins (e.g., LayoutLM, Detectron2) via entry points
- ✅ Debug overlay generator for quick visual inspection

## Quickstart

Install from source:

```bash
pip install tabbolt
```

Extract tables from a PDF using Python:

```python
from tabbolt import extract

result = extract("sample.pdf")
for table in result.tables:
    print(table.title, table.n_rows, table.n_cols)
    print(table.as_matrix(fill="repeat"))
```

Command line usage:

```bash
# Convert all tables to CSV in the output directory
$ tabbolt extract invoice.pdf --to csv --out outdir --fill-policy repeat
```

## Comparison

| Feature | TabBolt | pdfplumber | Camelot | Tabula |
|---------|---------|------------|---------|--------|
| Offline extraction | ✅ | ✅ | ⚠️ (depends on Ghostscript) | ✅ |
| Spanning cells | ✅ | ⚠️ manual | ⚠️ limited | ❌ |
| Multi-page stitching | ✅ | ❌ | ❌ | ❌ |
| Plugin detectors | ✅ | ❌ | ❌ | ❌ |
| Typed Python API | ✅ | ❌ | ❌ | ❌ |

## Why TabBolt?

- **Geometry-first**: heuristics tuned for PDF coordinate systems, not images.
- **Structured outputs**: Pydantic models ensure stable schemas across releases.
- **Deterministic**: tests generate their own PDFs, so CI never downloads assets.
- **Extensible**: add ML detectors by registering an entry point.

## Plugin Detectors

Plugins register via the `tabbolt.detectors` entry point group. A minimal plugin looks like:

```python
from tabbolt.detect.base import Detector, DetectedRegion

class AwesomeNet(Detector):
    name = "awesomenet"
    version = "1.0"

    def detect(self, pdf_path: str, pages: list[int] | None = None) -> list[DetectedRegion]:
        # Load the PDF and run inference...
        return []
```

Then expose it in your `pyproject.toml`:

```toml
[project.entry-points."tabbolt.detectors"]
awesomenet = "awesomenet:AwesomeNet"
```

## Roadmap

- **tabbolt-tt**: Transformer-based detector for low-contrast scans.
- **Benchmark suite**: reproducible accuracy and latency benchmarks.
- **GUI reviewer**: desktop app to quickly audit extracted tables.

## Development

Clone and install in editable mode:

```bash
git clone https://github.com/yourname/tabbolt.git
cd tabbolt
pip install -e .[dev]
pre-commit install
```

Run the test suite:

```bash
pytest
```

## License

MIT © TabBolt Contributors
