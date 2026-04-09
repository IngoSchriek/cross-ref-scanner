"""Kotlin language adapter."""

import os
from fnmatch import fnmatch
from pathlib import Path

from cross_ref_scanner.languages.base import LanguageAdapter, Symbol


class KotlinAdapter(LanguageAdapter):
    """Extracts Kotlin class names from .kt files."""

    @property
    def name(self) -> str:
        return "Kotlin"

    def extract_symbols(self, source_dir: Path, include: str | None = None) -> list[Symbol]:
        symbols = []
        for root, _dirs, files in os.walk(source_dir):
            for f in files:
                if not f.endswith(".kt") and not f.endswith(".kts"):
                    continue
                file_path = Path(root) / f
                rel = file_path.relative_to(source_dir)

                if include and not fnmatch(str(rel), include):
                    continue

                if not include and "/src/test/" in str(file_path):
                    continue

                class_name = file_path.stem
                symbols.append(Symbol(
                    name=class_name,
                    file_path=file_path,
                    kind="class",
                ))
        return sorted(symbols, key=lambda s: s.name)

    def search_extensions(self) -> list[str]:
        return [
            ".kt", ".kts", ".java", ".xml", ".properties",
            ".yml", ".yaml", ".json", ".gradle",
        ]
