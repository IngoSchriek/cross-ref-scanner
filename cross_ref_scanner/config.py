"""YAML configuration loader."""

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class ScanConfig:
    """Scan configuration loaded from YAML or CLI args."""
    source_path: Path
    target_paths: list[Path]
    language: str
    include: str | None = None
    report_format: str = "console"
    output_file: str | None = None
    delete: bool = False
    workers: int = 8


def load_config(config_path: Path) -> ScanConfig:
    """Load scan configuration from a YAML file.

    Expected format:
        source:
          path: ./my-lib
          include: "src/main/java/**/*.java"  # optional
        targets:
          - path: ./app1
          - path: ./app2
        language: java
        report:
          format: console  # console | json | csv
          output: report.json  # optional
        workers: 8  # optional
    """
    with open(config_path) as f:
        data = yaml.safe_load(f)

    base_dir = config_path.parent

    source = data["source"]
    source_path = _resolve_path(base_dir, source["path"])
    include = source.get("include")

    target_paths = [
        _resolve_path(base_dir, t["path"])
        for t in data["targets"]
    ]

    language = data["language"]

    report = data.get("report", {})
    report_format = report.get("format", "console")
    output_file = report.get("output")

    workers = data.get("workers", 8)

    return ScanConfig(
        source_path=source_path,
        target_paths=target_paths,
        language=language,
        include=include,
        report_format=report_format,
        output_file=output_file,
        workers=workers,
    )


def _resolve_path(base: Path, path_str: str) -> Path:
    """Resolve a path relative to a base directory."""
    p = Path(path_str)
    if p.is_absolute():
        return p
    return (base / p).resolve()
