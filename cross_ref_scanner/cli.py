"""Command-line interface for cross-ref-scanner."""

import argparse
import sys
from pathlib import Path

from cross_ref_scanner import __version__
from cross_ref_scanner.languages import ADAPTERS, get_adapter
from cross_ref_scanner.config import load_config
from cross_ref_scanner.scanner import scan, delete_unused
from cross_ref_scanner.report import generate_report


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cross-ref-scan",
        description="Find unused symbols in a source project by scanning target projects.",
    )
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")

    # Config file mode
    parser.add_argument(
        "-c", "--config",
        help="YAML configuration file (alternative to CLI flags).",
    )

    # CLI flags mode
    parser.add_argument(
        "-s", "--source",
        help="Path to the source project (where symbols are extracted from).",
    )
    parser.add_argument(
        "-t", "--targets",
        nargs="+",
        help="Paths to target projects (where to search for references).",
    )
    parser.add_argument(
        "-l", "--lang",
        choices=sorted(ADAPTERS.keys()),
        help="Source language.",
    )
    parser.add_argument(
        "-i", "--include",
        help="Glob pattern to filter source files (e.g. 'src/main/java/**/*.java').",
    )
    parser.add_argument(
        "-f", "--format",
        choices=["console", "json", "csv"],
        default="console",
        help="Output format (default: console).",
    )
    parser.add_argument(
        "-o", "--output",
        help="Write report to file instead of stdout.",
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Delete unused files (default: dry-run, only report).",
    )
    parser.add_argument(
        "-w", "--workers",
        type=int,
        default=8,
        help="Number of parallel workers (default: 8).",
    )
    return parser


def _progress_callback(done: int, total: int, symbol, is_used: bool):
    status = "USED" if is_used else "UNUSED"
    print(f"  [{done}/{total}] {status:>7}  {symbol.name}", flush=True)


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    # Load config from YAML or CLI args
    if args.config:
        config = load_config(Path(args.config))
        source_dir = config.source_path
        target_dirs = config.target_paths
        language = config.language
        include = config.include
        fmt = config.report_format
        output_file = config.output_file
        delete = config.delete
        workers = config.workers
    elif args.source and args.targets and args.lang:
        source_dir = Path(args.source).resolve()
        target_dirs = [Path(t).resolve() for t in args.targets]
        language = args.lang
        include = args.include
        fmt = args.format
        output_file = args.output
        delete = args.delete
        workers = args.workers
    else:
        parser.error("Provide either --config or (--source, --targets, --lang).")
        return 1

    # Validate paths
    if not source_dir.exists():
        print(f"Error: source directory not found: {source_dir}", file=sys.stderr)
        return 1
    for t in target_dirs:
        if not t.exists():
            print(f"Error: target directory not found: {t}", file=sys.stderr)
            return 1

    adapter = get_adapter(language)
    target_names = ", ".join(t.name for t in target_dirs)
    print(f"Source:   {source_dir}")
    print(f"Targets:  {target_names}")
    print(f"Language: {adapter.name}")
    if include:
        print(f"Include:  {include}")
    print(f"Mode:     {'DELETE' if delete else 'dry-run (report only)'}")
    print()

    result = scan(
        adapter=adapter,
        source_dir=source_dir,
        target_dirs=target_dirs,
        include=include,
        workers=workers,
        on_progress=_progress_callback if fmt == "console" else None,
    )

    print()
    report = generate_report(result, source_dir, fmt, output_file)
    if fmt == "console" or not output_file:
        print(report)
    if output_file:
        print(f"\nReport saved to: {output_file}")

    if delete and result.unused:
        print(f"\nDeleting {len(result.unused)} unused files...")
        deleted = delete_unused(result.unused, source_dir)
        print(f"{deleted} files deleted.")

    return 0 if not result.errors else 1


if __name__ == "__main__":
    sys.exit(main())
