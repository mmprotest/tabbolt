"""Command line interface for TabBolt."""
from __future__ import annotations

import time
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table as RichTable

from . import __version__
from .api import extract
from .debug import render_overlay
from .export import table_to_csv, table_to_html, table_to_markdown, table_to_dataframe

console = Console()


@click.group()
@click.version_option(__version__)
def main() -> None:
    """TabBolt command line interface."""


@main.command()
@click.argument("file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--pages", type=str, default=None, help="Comma separated page ranges")
@click.option("--detector", type=str, default="plumber", show_default=True)
@click.option("--to", "export_format", type=click.Choice(["html", "csv", "md", "df"]), default="html")
@click.option("--out", type=click.Path(path_type=Path), default=Path.cwd(), show_default=True)
@click.option("--workers", type=str, default="1", show_default=True)
@click.option("--fill-policy", type=click.Choice(["repeat", "empty", "sentinel"]), default="repeat")
@click.option("--stitch-aggressiveness", type=click.Choice(["low", "med", "high"]), default="med")
@click.option("--inline-styles", is_flag=True, default=False)
@click.option("--debug-overlays", is_flag=True, default=False)
def extract_cmd(
    file: Path,
    pages: str | None,
    detector: str,
    export_format: str,
    out: Path,
    workers: str,
    fill_policy: str,
    stitch_aggressiveness: str,
    inline_styles: bool,
    debug_overlays: bool,
) -> None:
    """Extract tables from FILE."""

    if workers not in {"1", "auto"}:
        console.print("[yellow]Parallel workers not implemented; running single-threaded.[/yellow]")
    page_list = _parse_pages(pages) if pages else None
    result = extract(
        file,
        pages=page_list,
        detector=detector,
        stitch_aggressiveness=stitch_aggressiveness,
    )
    out.mkdir(parents=True, exist_ok=True)
    for idx, table in enumerate(result.tables, start=1):
        stem = file.stem + f"_table_{idx}"
        if export_format == "html":
            html = table_to_html(table, inline_styles=inline_styles)
            (out / f"{stem}.html").write_text(html)
        elif export_format == "csv":
            csv_data = table_to_csv(table, fill_policy=fill_policy)
            (out / f"{stem}.csv").write_text(csv_data)
        elif export_format == "md":
            md = table_to_markdown(table)
            (out / f"{stem}.md").write_text(md)
        elif export_format == "df":
            df = table_to_dataframe(table)
            df.to_json(out / f"{stem}.json", orient="records", force_ascii=False, indent=2)
        if debug_overlays:
            overlay = render_overlay(table, epsilon=table.meta.get("epsilon", 0.0), detector=detector)
            (out / f"{stem}_overlay.html").write_text(overlay)
    console.print(f"[green]Extracted {len(result.tables)} tables.[/green]")


@main.command()
@click.argument("file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--repeat", type=int, default=3, show_default=True)
@click.option("--detector", type=str, default="plumber", show_default=True)
def benchmark(file: Path, repeat: int, detector: str) -> None:
    """Run extraction multiple times and report timing statistics."""

    times: list[float] = []
    for _ in range(repeat):
        start = time.perf_counter()
        result = extract(file, detector=detector)
        times.append(time.perf_counter() - start)
    table = RichTable(title="TabBolt Benchmark")
    table.add_column("Run")
    table.add_column("Seconds", justify="right")
    for idx, duration in enumerate(times, start=1):
        table.add_row(str(idx), f"{duration:.3f}")
    table.add_row("avg", f"{sum(times) / len(times):.3f}")
    table.add_row("tables", str(len(result.tables)))
    console.print(table)


def _parse_pages(value: str) -> list[int]:
    pages: set[int] = set()
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = part.split("-", 1)
            pages.update(range(int(start), int(end) + 1))
        else:
            pages.add(int(part))
    return sorted(pages)


if __name__ == "__main__":  # pragma: no cover
    main()
