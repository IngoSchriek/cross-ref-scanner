"""Java language adapter."""

import os
from fnmatch import fnmatch
from pathlib import Path

from cross_ref_scanner.languages.base import LanguageAdapter, Symbol


class JavaAdapter(LanguageAdapter):
    """Extracts Java class names and searches in Java/XML/properties files."""

    @property
    def name(self) -> str:
        return "Java"

    def extract_symbols(self, source_dir: Path, include: str | None = None) -> list[Symbol]:
        symbols = []
        for root, _dirs, files in os.walk(source_dir):
            for f in files:
                if not f.endswith(".java"):
                    continue
                file_path = Path(root) / f
                rel = file_path.relative_to(source_dir)

                if include and not fnmatch(str(rel), include):
                    continue

                # Skip test directories by default if no include pattern
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
            ".java", ".kt", ".xml", ".properties",
            ".yml", ".yaml", ".json", ".gradle", ".kts",
        ]
