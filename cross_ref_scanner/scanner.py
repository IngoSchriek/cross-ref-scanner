"""Core scanning logic: find symbols not referenced in target projects."""

import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path

from cross_ref_scanner.languages.base import LanguageAdapter, Symbol


@dataclass
class ScanResult:
    """Result of a cross-reference scan."""
    used: list[Symbol] = field(default_factory=list)
    unused: list[Symbol] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.used) + len(self.unused)


def _build_grep_includes(extensions: list[str]) -> list[str]:
    """Build grep --include flags from extension list."""
    flags = []
    for ext in extensions:
        pattern = f"*{ext}" if ext.startswith(".") else f"*.{ext}"
        flags.extend(["--include", pattern])
    return flags


def _is_symbol_referenced(symbol_name: str, target_dirs: list[Path],
                          include_flags: list[str]) -> bool:
    """Check if a symbol name appears in any target directory using grep."""
    for target in target_dirs:
        if not target.exists():
            continue
        try:
            result = subprocess.run(
                ["grep", "-r", "-l", "-F", symbol_name, *include_flags, str(target)],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode == 0 and result.stdout.strip():
                return True
        except subprocess.TimeoutExpired:
            pass
    return False


def scan(
    adapter: LanguageAdapter,
    source_dir: Path,
    target_dirs: list[Path],
    include: str | None = None,
    workers: int = 8,
    on_progress: callable = None,
) -> ScanResult:
    """Scan for unused symbols.

    Args:
        adapter: Language adapter for symbol extraction.
        source_dir: Root directory of the source project.
        target_dirs: List of target project directories to search.
        include: Optional glob pattern to filter source files.
        workers: Number of parallel workers for grep.
        on_progress: Optional callback(done, total, symbol, is_used).

    Returns:
        ScanResult with used and unused symbols.
    """
    result = ScanResult()

    symbols = adapter.extract_symbols(source_dir, include)
    if not symbols:
        return result

    include_flags = _build_grep_includes(adapter.search_extensions())

    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_symbol = {
            executor.submit(_is_symbol_referenced, s.name, target_dirs, include_flags): s
            for s in symbols
        }

        done_count = 0
        for future in as_completed(future_to_symbol):
            symbol = future_to_symbol[future]
            done_count += 1
            try:
                is_used = future.result()
            except Exception as e:
                result.errors.append(f"Error checking {symbol.name}: {e}")
                continue

            if is_used:
                result.used.append(symbol)
            else:
                result.unused.append(symbol)

            if on_progress:
                on_progress(done_count, len(symbols), symbol, is_used)

    result.used.sort(key=lambda s: s.name)
    result.unused.sort(key=lambda s: s.name)
    return result


def delete_unused(symbols: list[Symbol], source_dir: Path, clean_empty_dirs: bool = True) -> int:
    """Delete unused symbol files and optionally clean empty directories.

    Returns:
        Number of files deleted.
    """
    deleted = 0
    for symbol in symbols:
        try:
            symbol.file_path.unlink()
            deleted += 1
        except OSError:
            pass

    if clean_empty_dirs:
        for root, dirs, files in os.walk(source_dir, topdown=False):
            if not files and not dirs:
                try:
                    os.rmdir(root)
                except OSError:
                    pass

    return deleted
