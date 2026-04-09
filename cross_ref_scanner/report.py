"""Report generation: console, JSON, CSV."""

import csv
import io
import json
from pathlib import Path

from cross_ref_scanner.languages.base import Symbol
from cross_ref_scanner.scanner import ScanResult


def format_console(result: ScanResult, source_dir: Path) -> str:
    """Format scan result for terminal output."""
    lines = []
    lines.append("=" * 70)
    lines.append(f"RESULT: {len(result.used)} used, {len(result.unused)} unused "
                 f"(out of {result.total})")
    lines.append("=" * 70)

    if result.unused:
        lines.append("")
        lines.append("Unused symbols:")
        lines.append("")
        for s in result.unused:
            try:
                rel = s.file_path.relative_to(source_dir)
            except ValueError:
                rel = s.file_path
            lines.append(f"  - {s.name:50s} {rel}")

    if result.errors:
        lines.append("")
        lines.append("Errors:")
        for e in result.errors:
            lines.append(f"  ! {e}")

    return "\n".join(lines)


def format_json(result: ScanResult, source_dir: Path) -> str:
    """Format scan result as JSON."""
    def _symbol_dict(s: Symbol) -> dict:
        try:
            rel = str(s.file_path.relative_to(source_dir))
        except ValueError:
            rel = str(s.file_path)
        return {"name": s.name, "kind": s.kind, "path": rel}

    data = {
        "summary": {
            "total": result.total,
            "used": len(result.used),
            "unused": len(result.unused),
        },
        "unused": [_symbol_dict(s) for s in result.unused],
        "used": [_symbol_dict(s) for s in result.used],
        "errors": result.errors,
    }
    return json.dumps(data, indent=2, ensure_ascii=False)


def format_csv(result: ScanResult, source_dir: Path) -> str:
    """Format scan result as CSV."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["name", "kind", "status", "path"])

    for s in result.unused:
        try:
            rel = str(s.file_path.relative_to(source_dir))
        except ValueError:
            rel = str(s.file_path)
        writer.writerow([s.name, s.kind, "unused", rel])

    for s in result.used:
        try:
            rel = str(s.file_path.relative_to(source_dir))
        except ValueError:
            rel = str(s.file_path)
        writer.writerow([s.name, s.kind, "used", rel])

    return output.getvalue()


FORMATTERS = {
    "console": format_console,
    "json": format_json,
    "csv": format_csv,
}


def generate_report(result: ScanResult, source_dir: Path,
                    fmt: str = "console", output_file: str | None = None) -> str:
    """Generate a report in the specified format.

    Args:
        result: The scan result.
        source_dir: Source directory for relative paths.
        fmt: Format name ("console", "json", "csv").
        output_file: If set, write report to this file path.

    Returns:
        The formatted report string.
    """
    if fmt not in FORMATTERS:
        available = ", ".join(sorted(FORMATTERS))
        raise ValueError(f"Unknown format '{fmt}'. Available: {available}")

    content = FORMATTERS[fmt](result, source_dir)

    if output_file:
        Path(output_file).write_text(content, encoding="utf-8")

    return content
